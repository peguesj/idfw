"""Discovery resolver: runs providers concurrently and merges results."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .models import DiscoveredProject
from .provider import ProjectProvider

logger = logging.getLogger(__name__)


def _normalize_path(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    return str(Path(p).resolve())


def _normalize_name(name: str) -> str:
    """Normalize a project name for matching: lowercase, strip whitespace and common suffixes."""
    return name.strip().lower()


def _merge_key(project: DiscoveredProject) -> str:
    """Produce a dedup key from normalized name.

    Both filesystem and remote providers use name-based keys so that a local
    project ``idfw`` matches a Plane project named ``IDFW - IDEA Definition
    Framework``.  For filesystem projects the key is derived from the directory
    name; for all projects we also store secondary keys via ``_merge_keys`` so
    the resolver can attempt multi-key matching.
    """
    return f"name:{_normalize_name(project.name)}"


def _merge_keys(project: DiscoveredProject) -> list[str]:
    """Return all plausible merge keys for *project*.

    Plane names often look like ``IDFW - IDEA Definition Framework`` while
    filesystem names are just the directory name (``idfw``).  We generate keys
    for the full name **and** for the first word / identifier so cross-provider
    matches succeed.
    """
    keys: list[str] = [_merge_key(project)]
    norm = _normalize_name(project.name)

    # First word of the name (covers "idfw - idea definition …" -> "idfw")
    first_word = norm.split()[0] if norm else ""
    if first_word and first_word != norm:
        keys.append(f"name:{first_word}")

    # Identifier (Plane identifier like "IDFW")
    if project.identifier:
        keys.append(f"name:{project.identifier.strip().lower()}")

    # Hyphen-split first segment (covers "idfw-something")
    first_seg = norm.split("-")[0].strip()
    if first_seg and first_seg != norm and first_seg != first_word:
        keys.append(f"name:{first_seg}")

    return keys


def merge_projects(existing: DiscoveredProject, new: DiscoveredProject) -> DiscoveredProject:
    """Merge new into existing: non-None fields from new fill None fields in existing, metadata dicts are merged."""
    for field_name in (
        "path", "identifier", "plane_id", "plane_url",
        "apm_port", "description", "stack", "last_active",
    ):
        new_val = getattr(new, field_name)
        if new_val is not None and getattr(existing, field_name) is None:
            setattr(existing, field_name, new_val)

    # Source tracking: keep the original source but note enrichment
    if new.source != existing.source:
        sources = existing.metadata.get("enriched_by", [])
        if new.source not in sources:
            sources.append(new.source)
            existing.metadata["enriched_by"] = sources

    # Merge metadata dicts
    for k, v in new.metadata.items():
        if k not in existing.metadata:
            existing.metadata[k] = v

    return existing


class DiscoveryResolver:
    """Orchestrates multiple providers and merges their results."""

    def __init__(self, providers: Optional[List[ProjectProvider]] = None):
        self._providers: List[ProjectProvider] = providers or []

    def add_provider(self, provider: ProjectProvider) -> None:
        self._providers.append(provider)

    @property
    def providers(self) -> List[ProjectProvider]:
        return list(self._providers)

    async def resolve(self, providers: Optional[List[str]] = None) -> List[DiscoveredProject]:
        """Run discovery across all (or specified) providers and return merged list."""
        active = self._providers
        if providers:
            active = [p for p in self._providers if p.name in providers]

        # Run all providers concurrently, tolerating individual failures
        tasks = [self._safe_discover(p) for p in active]
        all_results = await asyncio.gather(*tasks)

        # Merge in provider order.  Each project may have multiple merge keys
        # (full name, first word, identifier).  We check all keys to find an
        # existing entry before inserting a new one.
        merged: Dict[str, DiscoveredProject] = {}
        # secondary_keys maps every alternate key back to the canonical key
        alias: Dict[str, str] = {}

        for result_list in all_results:
            for project in result_list:
                keys = _merge_keys(project)
                canonical = keys[0]

                # Find existing entry via any of our keys
                existing_key: Optional[str] = None
                for k in keys:
                    if k in merged:
                        existing_key = k
                        break
                    if k in alias:
                        existing_key = alias[k]
                        break

                if existing_key is not None:
                    merge_projects(merged[existing_key], project)
                else:
                    merged[canonical] = project
                    # Register all alternate keys as aliases
                    for k in keys[1:]:
                        if k not in merged:
                            alias[k] = canonical

        return list(merged.values())

    async def provider_status(self) -> List[dict]:
        """Return availability status for each provider."""
        async def _check(p: ProjectProvider) -> dict:
            try:
                available = await p.is_available()
            except Exception:
                available = False
            return {"name": p.name, "available": available}

        tasks = [_check(p) for p in self._providers]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def _safe_discover(provider: ProjectProvider) -> List[DiscoveredProject]:
        try:
            return await provider.discover()
        except Exception as exc:
            logger.warning("Provider %s failed: %s", provider.name, exc)
            return []

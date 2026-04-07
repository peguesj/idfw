"""Plane project management discovery provider."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List, Optional

import aiohttp

from ..models import DiscoveredProject
from ..provider import ProjectProvider

_API_BASE = "https://plane.lgtm.build/api/v1/workspaces/lgtm/projects/"

_API_KEY_PATHS = (
    Path.home() / ".config" / "plane" / "api_key",
    Path.home() / ".claude" / "skills" / "upm" / "plane-api-key",
)


def _read_api_key() -> Optional[str]:
    for p in _API_KEY_PATHS:
        try:
            key = p.read_text().strip()
            if key:
                return key
        except OSError:
            continue
    return None


class PlaneProvider(ProjectProvider):
    """Discovers projects from Plane workspace API."""

    def __init__(self, api_base: Optional[str] = None):
        self._api_base = api_base or _API_BASE

    @property
    def name(self) -> str:
        return "plane"

    async def is_available(self) -> bool:
        key = _read_api_key()
        if not key:
            return False
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._api_base,
                    headers={"X-API-Key": key},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def discover(self) -> List[DiscoveredProject]:
        key = _read_api_key()
        if not key:
            return []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._api_base,
                    headers={"X-API-Key": key},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
        except Exception:
            return []

        results = data if isinstance(data, list) else data.get("results", [])
        projects: List[DiscoveredProject] = []

        for item in results:
            pid = item.get("id", "")
            identifier = item.get("identifier", "")
            name = item.get("name", identifier)
            desc = item.get("description", "")

            stable_id = hashlib.sha256(f"plane:{pid}".encode()).hexdigest()[:12]

            projects.append(DiscoveredProject(
                id=stable_id,
                name=name,
                source="plane",
                identifier=identifier,
                plane_id=pid,
                plane_url=f"https://plane.lgtm.build/lgtm/projects/{pid}/issues/",
                description=desc or None,
                metadata={"plane_raw": {
                    k: item[k] for k in ("id", "identifier", "name", "emoji", "created_at", "updated_at")
                    if k in item
                }},
            ))

        return projects

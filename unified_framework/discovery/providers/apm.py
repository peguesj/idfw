"""CCEM APM discovery provider."""

from __future__ import annotations

import hashlib
from typing import List, Optional

import aiohttp

from ..models import DiscoveredProject
from ..provider import ProjectProvider

_DEFAULT_BASE = "http://localhost:3032"


class APMProvider(ProjectProvider):
    """Discovers projects registered with CCEM APM."""

    def __init__(self, base_url: Optional[str] = None):
        self._base_url = (base_url or _DEFAULT_BASE).rstrip("/")

    @property
    def name(self) -> str:
        return "apm"

    async def is_available(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}/api/status",
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def discover(self) -> List[DiscoveredProject]:
        sessions = await self._fetch("/api/sessions")
        status = await self._fetch("/api/status")

        # Merge both endpoints for maximum coverage
        raw_projects: dict[str, dict] = {}

        if isinstance(sessions, list):
            for s in sessions:
                name = s.get("project_name") or s.get("project", "")
                if name:
                    raw_projects.setdefault(name, {}).update(s)

        if isinstance(status, dict):
            for key in ("projects", "sessions"):
                items = status.get(key, [])
                if isinstance(items, list):
                    for s in items:
                        name = s.get("project_name") or s.get("project", "") or s.get("name", "")
                        if name:
                            raw_projects.setdefault(name, {}).update(s)

        results: List[DiscoveredProject] = []
        for name, data in raw_projects.items():
            stable_id = hashlib.sha256(f"apm:{name}".encode()).hexdigest()[:12]
            port = data.get("port") or data.get("apm_port")
            path = data.get("project_root") or data.get("path")

            results.append(DiscoveredProject(
                id=stable_id,
                name=name,
                path=path,
                source="apm",
                apm_port=int(port) if port else None,
                last_active=data.get("last_active") or data.get("updated_at"),
                metadata={"apm_session": {
                    k: data[k] for k in ("session_id", "agent_count", "status")
                    if k in data
                }},
            ))

        return results

    async def _fetch(self, endpoint: str) -> object:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception:
            pass
        return {}

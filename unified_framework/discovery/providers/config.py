"""Static configuration-based discovery provider."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import List, Optional

from ..models import DiscoveredProject
from ..provider import ProjectProvider

_REGISTRY_PATH = Path.home() / ".claude" / "config" / "project-registry.json"
_PROJECTS_DIR = Path.home() / ".claude" / "projects"


class ConfigProvider(ProjectProvider):
    """Discovers projects from static JSON configuration files."""

    def __init__(
        self,
        registry_path: Optional[str] = None,
        projects_dir: Optional[str] = None,
    ):
        self._registry_path = Path(registry_path) if registry_path else _REGISTRY_PATH
        self._projects_dir = Path(projects_dir) if projects_dir else _PROJECTS_DIR

    @property
    def name(self) -> str:
        return "config"

    async def is_available(self) -> bool:
        return self._registry_path.exists() or self._projects_dir.is_dir()

    async def discover(self) -> List[DiscoveredProject]:
        projects: List[DiscoveredProject] = []
        projects.extend(self._from_registry())
        projects.extend(self._from_project_files())
        return projects

    def _from_registry(self) -> List[DiscoveredProject]:
        if not self._registry_path.exists():
            return []
        try:
            data = json.loads(self._registry_path.read_text())
        except (json.JSONDecodeError, OSError):
            return []

        items = data if isinstance(data, list) else data.get("projects", [])
        results: List[DiscoveredProject] = []

        for item in items:
            name = item.get("name", "")
            if not name:
                continue
            path = item.get("path")
            stable_id = hashlib.sha256(f"config:{name}".encode()).hexdigest()[:12]

            results.append(DiscoveredProject(
                id=stable_id,
                name=name,
                path=path,
                source="config",
                identifier=item.get("identifier"),
                plane_id=item.get("plane_id"),
                description=item.get("description"),
                stack=item.get("stack"),
                metadata=item.get("metadata", {}),
            ))

        return results

    def _from_project_files(self) -> List[DiscoveredProject]:
        if not self._projects_dir.is_dir():
            return []

        results: List[DiscoveredProject] = []
        for f in sorted(self._projects_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            name = data.get("name") or data.get("project_name") or f.stem
            path = data.get("path") or data.get("repository_path")
            stable_id = hashlib.sha256(f"config:{name}".encode()).hexdigest()[:12]

            stack_raw = data.get("stack")
            stack = None
            if isinstance(stack_raw, list):
                stack = stack_raw
            elif isinstance(stack_raw, str):
                stack = [s.strip() for s in stack_raw.split(",")]

            results.append(DiscoveredProject(
                id=stable_id,
                name=name,
                path=path,
                source="config",
                identifier=data.get("identifier"),
                plane_id=data.get("linear_project_id") or data.get("plane_id"),
                description=data.get("description"),
                stack=stack,
                metadata={k: v for k, v in data.items() if k not in (
                    "name", "project_name", "path", "repository_path",
                    "identifier", "linear_project_id", "plane_id",
                    "description", "stack",
                )},
            ))

        return results

"""Filesystem-based project discovery provider."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import List, Optional

from ..models import DiscoveredProject
from ..provider import ProjectProvider

_PROJECT_MARKERS = (
    ".claude/CLAUDE.md",
    "pyproject.toml",
    "Package.swift",
    "package.json",
    "mix.exs",
    "Cargo.toml",
)

_SKIP_DIRS = {"node_modules", ".git", "__pycache__", "build", "dist"}


def _stable_id(path: str) -> str:
    return hashlib.sha256(path.encode()).hexdigest()[:12]


def _parse_claude_md(path: Path) -> dict:
    """Extract metadata from a .claude/CLAUDE.md file."""
    metadata: dict = {}
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return metadata

    # Linear project ID
    m = re.search(r"\*\*Linear Project ID\*\*:\s*`([^`]+)`", text)
    if m:
        metadata["linear_project_id"] = m.group(1)

    # Stack info (look for **Stack**: ...)
    m = re.search(r"\*\*Stack\*\*:\s*(.+)", text)
    if m:
        raw = m.group(1).strip()
        metadata["stack"] = [s.strip() for s in raw.split(",")]

    # Description
    m = re.search(r"\*\*Description\*\*:\s*(.+)", text)
    if m:
        metadata["description"] = m.group(1).strip()

    return metadata


class FilesystemProvider(ProjectProvider):
    """Discovers projects by scanning local directories for marker files."""

    def __init__(self, base_dirs: Optional[List[str]] = None, max_depth: int = 2):
        self._base_dirs = base_dirs or [str(Path.home() / "Developer")]
        self._max_depth = max_depth

    @property
    def name(self) -> str:
        return "filesystem"

    async def is_available(self) -> bool:
        return True

    async def discover(self) -> List[DiscoveredProject]:
        projects: dict[str, DiscoveredProject] = {}

        for base in self._base_dirs:
            base_path = Path(base).expanduser()
            if not base_path.is_dir():
                continue
            self._scan(base_path, 0, projects)

        return list(projects.values())

    def _scan(self, directory: Path, depth: int, out: dict[str, DiscoveredProject]) -> None:
        if depth > self._max_depth:
            return

        resolved = str(directory.resolve())
        if resolved in out:
            return

        # Check for project markers
        has_marker = any((directory / marker).exists() for marker in _PROJECT_MARKERS)
        if has_marker and depth > 0:
            proj = self._build_project(directory)
            out[resolved] = proj
            return  # don't recurse into discovered projects

        # Recurse into subdirectories
        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.is_dir() and entry.name not in _SKIP_DIRS and not entry.name.startswith("."):
                self._scan(entry, depth + 1, out)

    def _build_project(self, directory: Path) -> DiscoveredProject:
        resolved = str(directory.resolve())
        pid = _stable_id(resolved)
        name = directory.name

        description: Optional[str] = None
        stack: Optional[list[str]] = None
        metadata: dict = {}

        claude_md = directory / ".claude" / "CLAUDE.md"
        if claude_md.exists():
            parsed = _parse_claude_md(claude_md)
            description = parsed.get("description")
            stack = parsed.get("stack")
            if "linear_project_id" in parsed:
                metadata["linear_project_id"] = parsed["linear_project_id"]

        return DiscoveredProject(
            id=pid,
            name=name,
            path=resolved,
            source="filesystem",
            description=description,
            stack=stack,
            metadata=metadata,
        )

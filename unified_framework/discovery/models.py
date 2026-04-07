"""Data models for project discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DiscoveredProject:
    """A project discovered by one or more providers."""

    id: str
    name: str
    path: Optional[str] = None
    source: str = "unknown"
    identifier: Optional[str] = None
    plane_id: Optional[str] = None
    plane_url: Optional[str] = None
    apm_port: Optional[int] = None
    description: Optional[str] = None
    stack: Optional[list[str]] = None
    last_active: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict, omitting None values."""
        result = {}
        for k in (
            "id", "name", "path", "source", "identifier",
            "plane_id", "plane_url", "apm_port", "description",
            "stack", "last_active", "metadata",
        ):
            v = getattr(self, k)
            if v is not None:
                result[k] = v
        return result

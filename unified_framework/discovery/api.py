"""FastAPI router for project discovery."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .providers.filesystem import FilesystemProvider
from .providers.plane import PlaneProvider
from .providers.apm import APMProvider
from .providers.config import ConfigProvider
from .resolver import DiscoveryResolver

router = APIRouter(prefix="/api/v3/projects", tags=["discovery"])


def _build_resolver() -> DiscoveryResolver:
    """Create resolver with default provider order: filesystem -> config -> apm -> plane."""
    return DiscoveryResolver([
        FilesystemProvider(),
        ConfigProvider(),
        APMProvider(),
        PlaneProvider(),
    ])


@router.get("/providers")
async def list_providers():
    """List available providers and their status."""
    resolver = _build_resolver()
    return await resolver.provider_status()


@router.get("")
@router.get("/")
async def list_projects(provider: Optional[str] = Query(None, description="Filter by provider name")):
    """Return full merged project list, optionally filtered by provider."""
    resolver = _build_resolver()
    filter_list = [provider] if provider else None
    projects = await resolver.resolve(providers=filter_list)
    return [p.to_dict() for p in projects]


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Return a single project by ID."""
    resolver = _build_resolver()
    projects = await resolver.resolve()
    for p in projects:
        if p.id == project_id:
            return p.to_dict()
    raise HTTPException(status_code=404, detail="Project not found")

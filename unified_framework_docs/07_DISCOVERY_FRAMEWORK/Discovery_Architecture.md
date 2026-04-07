# Discovery Framework Architecture

## Overview

The Discovery Framework (`unified_framework/discovery/`) provides a pluggable, multi-source project discovery system. It resolves project metadata from multiple providers concurrently and merges results into a unified view.

**Added in**: v4.0.0 (Phase 8, CP-49)
**API Endpoint**: `GET /api/v3/projects`
**Location**: `unified_framework/discovery/`

## Architecture

```
DiscoveryResolver
├── FilesystemProvider   — scans local directories for project markers
├── PlaneProvider        — enriches from Plane PM API (issues, status)
├── APMProvider          — pulls active sessions from CCEM APM
└── ConfigProvider       — reads static config files (contexts/*.json)
```

## Components

### Models (`models.py`)

```python
@dataclass
class DiscoveredProject:
    project_id: str
    name: str
    slug: str
    source: str              # which provider found it
    path: Optional[str]      # local filesystem path
    project_type: Optional[str]
    status: Optional[str]
    metadata: Dict[str, Any] # provider-specific extras
```

### Provider Interface (`provider.py`)

All providers implement the `DiscoveryProvider` abstract base class:

```python
class DiscoveryProvider(ABC):
    @abstractmethod
    async def discover(self) -> List[DiscoveredProject]:
        """Return all projects this provider can find."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'filesystem', 'plane')."""
```

### Providers

| Provider | Source | What it finds |
|----------|--------|---------------|
| **FilesystemProvider** | Local disk | Directories containing `pyproject.toml`, `Package.swift`, `mix.exs`, `package.json`, `.claude/CLAUDE.md` |
| **PlaneProvider** | Plane PM API | Project issues, status, assignees. Merges with filesystem results by slug matching. |
| **APMProvider** | CCEM APM (port 3031/3032) | Active agent sessions and their associated projects |
| **ConfigProvider** | `~/.claude/skills/idea/contexts/*.json` | IDEA lifecycle context files from `/idea new` |

### Resolver (`resolver.py`)

The `DiscoveryResolver` orchestrates providers:

1. Runs all providers concurrently via `asyncio.gather`
2. Deduplicates by `project_id` (first provider wins)
3. Merges Plane metadata into matching projects (enrichment pass)
4. Returns sorted list

```python
resolver = DiscoveryResolver(providers=[
    FilesystemProvider(scan_paths=[Path.home() / "Developer"]),
    PlaneProvider(api_url="http://localhost:8080"),
    APMProvider(apm_url="http://localhost:3032"),
    ConfigProvider(contexts_dir=Path.home() / ".claude/skills/idea/contexts"),
])
projects = await resolver.resolve()
```

### FastAPI Router (`api.py`)

Mounted at `/api/v3/projects` in the /idea daemon:

```
GET /api/v3/projects          — list all discovered projects
GET /api/v3/projects?source=filesystem  — filter by provider
```

Response: JSON array of `DiscoveredProject` dictionaries.

## Integration

The discovery router is mounted in the /idea daemon (`~/.claude/skills/idea/server/app.py`):

```python
from unified_framework.discovery.api import router as discovery_router
app.include_router(discovery_router)
```

The IDFWU Swift macOS app consumes this API to populate its sidebar with dynamic project listings.

## Configuration

Providers are configured via environment or constructor args:

| Provider | Config | Default |
|----------|--------|---------|
| FilesystemProvider | `scan_paths` | `[~/Developer]` |
| PlaneProvider | `api_url` | `http://localhost:8080` |
| APMProvider | `apm_url` | `http://localhost:3032` |
| ConfigProvider | `contexts_dir` | `~/.claude/skills/idea/contexts` |

Providers that fail (e.g., Plane not running) are silently skipped — the resolver returns whatever it can find.

## Test Coverage

Integration tests in `tests/test_idea_lifecycle.py`:
- `TestDiscoveryAPI::test_discovery_endpoint_exists` — verifies the endpoint returns 200 with a list

---

*Version: 4.0.0 | Last Updated: 2026-04-07*

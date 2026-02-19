# Changelog

## [1.0.0] - 2026-02-19

### Added
- **Package Foundation** (B01): Unified `pyproject.toml`, `setup.py`, `requirements.txt`, `requirements-dev.txt`, `pytest.ini` from idfwu + dev_sentinel
- **FORCE Framework** (B02): `.force/` governance configs (94 JSON files) and `force/` Python package from dev_sentinel
- **Unified Framework Core** (B03): `unified_framework/core/` (schema_bridge, state_manager, converters, force_parser, message_protocols) and `unified_framework/schemas/` from idfwu
- **Agents & Orchestration** (B04): `unified_framework/agents/` (base_agent with Pydantic v2, orchestrator_agent) from idfwu + `agents/` (5 dev_sentinel agents: cdia, rdia, saa, vcla, vcma) + `core/` (message_bus, task_manager) + `utils/`
- **Services & Monitoring** (B05): `unified_framework/services/` (apm_client, checkpoint_manager, orchestrator_service) + `unified_framework/monitoring/` + `unified_framework/hooks/` + `unified_framework/commands/` from idfwu
- **CLI, MCP & Integration** (B06): `unified_framework/cli/` + `unified_framework/mcp/` + `dev_sentinel/` package + `integration/` (fast_agent, FORCE integration) from dev_sentinel
- **Tests & Planning** (B07): 14 test files + fixtures from idfwu, force system test from dev_sentinel, 3 planning artifacts from idfwu2
- **Integration Verification** (B08): Updated exports, CHANGELOG, project documentation

### Changed
- Replaced `dev_sentinel` symlink with actual package contents
- Fixed hardcoded `/Users/jeremiah/` paths in checkpoint_manager.py and orchestrator_service.py to use relative path resolution
- Upgraded Python requirement from >=3.9 to >=3.10
- Renamed package from `idfwu` to `idfw`
- CLI entry point changed from `idfwu` to `idfw`

### Sources
- **idfwu** (`/Users/jeremiah/Developer/idfwu`): unified_framework core, agents, services, CLI, MCP, tests
- **dev_sentinel** (`/Users/jeremiah/Developer/dev_sentinel`): .force/ configs, force/ package, agents/, core/, utils/, dev_sentinel/ package, integration/
- **idfwu2** (`/Users/jeremiah/Developer/idfwu2`): planning/ artifacts (skills mapping, catalog, implementation report)

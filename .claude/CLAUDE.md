# IDFW - IDEA Definition Framework Workspace

## Project Overview
- **Type**: Framework unification across IDFW, IDFWU, IDFWU2, and Dev Sentinel
- **Scope**: Schema validation, agent orchestration, FORCE integration, CLI unification, MCP protocol, documentation
- **Branch**: main (v1.0 consolidated from 4 repos)
- **APM**: http://localhost:3031 (project: idfw, 228 agents registered)

## Repositories
| Repo | Path | Purpose | Status |
|------|------|---------|--------|
| IDFW | /Users/jeremiah/Developer/idfw | Unified framework (v1.0) | **ACTIVE** |
| IDFWU | /Users/jeremiah/Developer/idfwu | Original unified framework | ARCHIVE (idfwu_mfs excluded by design) |
| IDFWU2 | /Users/jeremiah/Developer/idfwu2 | Planning & research (247-skill catalog) | ARCHIVED |
| Dev Sentinel | /Users/jeremiah/Developer/dev_sentinel | FORCE framework (42+ tools, 5 agents) | ARCHIVED |

### STFU Analysis (2026-02-19)
| Pair | Score | Verdict | Absorption |
|------|-------|---------|------------|
| idfw ↔ idfwu | 0.52 | REVIEW | 96.5% core absorbed; idfwu_mfs intentionally excluded |
| idfw ↔ idfwu2 | 0.30 | ARCHIVE | 100% absorbed (all 7 files) |
| idfw ↔ dev_sentinel | 0.26 | ARCHIVE | 97% absorbed (249/263 files) |

**Note**: `.force/` = project-scope runtime config; `force/` = importable Python package. Both coexist by design.

## Implementation Checkpoints

### Phase 1: Schema & Data Integrity (Complete)
- [x] **CP-01**: Fix IDDA.schemas.json structural errors (SQ-01)
- [x] **CP-02**: Add IDDV.schemas.json header compliance (SQ-01)
- [x] **CP-03**: Rewrite DDD.schema.jsonc as valid JSONC (SQ-01)
- [x] **CP-04**: Upgrade resume.schema.json to draft-2020-12 (SQ-01)
- [x] **CP-05**: Remove JS comments from seed JSON files (SQ-01)
- [x] **CP-06**: Reconstruct corrupted idfpj.seed.expanded.json (SQ-01)
- After CP-06: All 8 schema/data files validate with python3 json.load()

### Phase 2: FORCE Schema Compliance (Complete)
- [x] **CP-07**: Fix tool category enum violations - 7 files (SQ-03)
- [x] **CP-08**: Fix sequential strategy stub tools - 31 files (SQ-03)
- [x] **CP-09**: Fix constraint ID format + type enum - 5 files (SQ-03)
- [x] **CP-10**: Fix pattern ID format violations - 2 files (SQ-03)
- [x] **CP-11**: Fix governance enforcement levels - 1 file, 8 policies (SQ-03)
- [x] **CP-12**: Remove placeholder stubs from collection files (SQ-03)
- After CP-12: FORCE validation 68/68 PASS (100%)

### Phase 3: Critical Gap Resolution (Next)
- [x] **CP-13**: Resolve E-layer skill ID duplication (12 conflicts between FORCE E1 and IDEA E1)
- [x] **CP-14**: Create runtime bindings for orphaned agents (66/74 agents, 89% orphaned)
- [x] **CP-15**: Implement CLI command stubs (44/52 commands, 85% unimplemented)
- [x] **CP-16**: Wire APM integration into codebases (0% current integration)
- [x] **CP-17**: Build checkpoint/rollback for orchestration (20% current maturity)
- After CP-17: Run /upm verify

### Phase 4: Consolidation (Complete)
- [x] **B01**: Package foundation (pyproject.toml, setup.py, requirements)
- [x] **B02**: FORCE framework (.force/ + force/ from dev_sentinel)
- [x] **B03**: Unified framework core (core/, schemas/ from idfwu)
- [x] **B04**: Agents and orchestration (agents from idfwu + dev_sentinel)
- [x] **B05**: Services and monitoring (services/, hooks/, monitoring/ from idfwu)
- [x] **B06**: CLI, MCP, and integration (CLI, MCP, dev_sentinel package, integration)
- [x] **B07**: Tests and planning docs (14 test files, planning artifacts)
- [x] **B08**: Integration verification (exports, CHANGELOG, docs)
- After B08: `pip install -e ".[dev]"` && `idfw --help` && `pytest`

### Phase 5: Wiki & Test Hardening (Complete)
- [x] **CP-18**: Phoenix LiveView wiki app with 9 content pages (port 4001)
- [x] **CP-19**: Fix all 51 failing tests (569 pass, 12 skipped, 0 fail)
- [x] **CP-20**: Gitignore cleanup (__pycache__, .pyc, build artifacts)
- [x] **CP-21**: Formation architecture slash command
- After CP-21: All tests green, wiki live, ready for v1.0 merge

### Phase 6: Quality & Documentation (Planned)
- [ ] **CP-22**: Add test coverage to dev_sentinel (currently 0 tests)
- [ ] **CP-23**: Fix 2 broken documentation links (SQ-07)
- [ ] **CP-24**: Bring IDFW documentation from 45% to 70%
- [ ] **CP-25**: Map Claude Code product skills to IDEA framework
- After CP-25: Full squadron re-scan to verify improvements

### Phase 7: STFU Archive Sequence (In Progress)
- [x] **CP-26**: Migrate 4 planning docs from idfwu2 (US-001)
- [x] **CP-27**: Fix mcp version floor >=0.5.0 to >=1.6.0 (US-002)
- [x] **CP-28**: Port Linear integration modules from idfwu (US-003)
- [x] **CP-29**: Add [agents] optional dependency group (US-004)
- [x] **CP-30**: Confirm test_converters.py coverage (US-005)
- [x] **CP-31**: Port orchestrator launchers from idfwu (US-006)
- [x] **CP-32**: Update CLAUDE.md with STFU results (US-007)
- [ ] **CP-33**: Archive idfwu2 + dev_sentinel on GitHub (US-008)
- [ ] **CP-34**: Final verification + idfwu archive + PR (US-009)
- After CP-34: All source repos archived, IDFW is sole active repo

## Test Status
- **511 tests passing** (511 pass + 26 skipped)
- Hooks tests skipped: intentionally removed bloat (7,098 LOC hooks system)
- Schema validation: 8/8 schemas validate
- FORCE validation: 68/68 PASS (100%)
- State manager: checkpoint/rollback fully operational
- Wiki: 9 content pages with evolution tracing

# IDEA Lifecycle Architecture

## Overview

The `/idea` skill provides a guided end-to-end lifecycle for taking a project from concept to execution. It implements the Inception Layer (v4.0) of the IDEA Definition Framework.

**Added in**: v4.0.0 (Phase 8, CP-35 to CP-50)
**Skill Path**: `~/.claude/skills/idea/`
**Daemon Port**: 4040 (dynamic range 4040-4099)

## Lifecycle Phases

```
/idea new → /idea discover → /idea define → /idea plan → /idea execute
                                                              │
                                                    /idea status (anytime)
```

| Phase | Input | Output | Skills Invoked |
|-------|-------|--------|----------------|
| **new** | Interactive wizard (5-8 questions) | `contexts/{slug}.json` | — |
| **discover** | Context file | Problem statement, JTBD, constraints, assumptions, RACI | /problem-statement, /jobs-to-be-done |
| **define** | Discovery artifacts | PRD (markdown + JSON), story count, wave count | /prd, /ralph |
| **plan** | prd.json | Plane issues, checkpoint range, risk matrix | /upm plan, Plane PM API |
| **execute** | Plan artifacts + sizing | Formation deployment, started/completed timestamps | /upm build, /formation |
| **status** | Any phase | Unified view of all phase states | — |

## Context Files

Each project creates a JSON context file at `~/.claude/skills/idea/contexts/{slug}.json`:

```json
{
  "project_id": "myapp-20260407",
  "project_name": "My App",
  "project_slug": "myapp",
  "project_type": "Internal Tool",
  "target_users": "Developers",
  "problem_statement": "...",
  "tech_stack": { "language": "Python", "framework": "FastAPI" },
  "constraints": {},
  "integrations": [],
  "sizing": "new",
  "version": "4.0.0",
  "phases": {
    "discover": { "completed_at": "...", "problem_statement": "...", "jtbd": {} },
    "define": { "completed_at": "...", "prd_path": "...", "story_count": 12 },
    "plan": { "completed_at": "...", "plane_issue_ids": [] },
    "execute": { "started_at": "...", "formation_id": "..." }
  },
  "created_at": "2026-04-07T00:00:00Z"
}
```

## Daemon Architecture

The /idea daemon is a FastAPI server providing real-time AG-UI protocol events.

### Server (`server/app.py`)

Created via `create_app(bus, storage, project_slug)`.

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v3/health` | Daemon health + thread list |
| GET | `/api/v3/events` | SSE stream (AG-UI protocol) |
| POST | `/api/v3/state/{thread_id}` | Push state or emit CUSTOM events |
| GET | `/api/v3/state/{thread_id}` | Read current thread state |
| POST | `/api/v3/decisions/{gate_id}` | Resolve a decision gate |
| GET | `/api/v3/decisions` | List open/resolved gates |
| GET | `/api/v3/projects` | Discovery API (mounted from unified_framework) |
| GET | `/ui` | Web-based dashboard |

### EventBus (`server/events.py`)

Async pub/sub bus implementing the AG-UI protocol (33 event types across 7 categories):

- **Lifecycle**: RUN_STARTED, RUN_FINISHED, RUN_ERROR, STEP_STARTED, STEP_FINISHED
- **State**: STATE_SNAPSHOT, STATE_DELTA, MESSAGES_SNAPSHOT
- **Text**: TEXT_MESSAGE_START/CONTENT/END
- **Tools**: TOOL_CALL_START/END/RESULT
- **Custom**: CUSTOM, RAW (used for decision gates, diagrams, docs)

Features:
- Bounded replay buffer (1000 events) for SSE reconnection via `?since=N`
- Subscriber fan-out with backpressure (slow consumers dropped)
- Typed sync and async event handlers

### Storage (`server/storage.py`)

SQLite-backed persistence with four tables:

| Table | Purpose |
|-------|---------|
| `schema_versions` | Schema version tracking |
| `schema_changes` | Schema change audit log |
| `variable_audits` | Variable change audit trail |
| `gate_decisions` | Decision gate lifecycle (pending → resolved) |
| `event_log` | Full event audit trail |

### Decision Gates

Decision gates are interactive approval points in the lifecycle:

1. Phase handler opens a gate via CUSTOM event → persisted to SQLite
2. Gate appears in UI and SSE stream as `decision_gate_open`
3. User resolves via `POST /api/v3/decisions/{gate_id}` with `approve|reject|defer`
4. Resolution emitted as `decision_gate_resolved` event

### Supporting Modules

| Module | Purpose |
|--------|---------|
| `server/registry.py` | Schema version registry |
| `server/schema_tracker.py` | Schema change detection and tracking |
| `server/variable_monitor.py` | Variable change monitoring |

## Inception Tools

Phase 8 added specialized tools for the inception layer:

| Tool | Location | Purpose |
|------|----------|---------|
| `project_type_classifier` | idea skill | Maps projects to IDFPJ types |
| `risk_assessment_generator` | idea skill | Generates risk matrices |
| `kickoff_package_generator` | idea skill | Produces project kickoff bundles |
| `constraint_registry` | idea skill | Tracks project constraints |
| `assumption_registry` | idea skill | Tracks project assumptions |
| `raci_matrix` | idea skill | RACI responsibility assignment |
| `stakeholder_impact` | idea skill | Stakeholder analysis |

## Test Coverage

24 integration tests in `tests/test_idea_lifecycle.py`:

| Test Class | Tests | Covers |
|------------|-------|--------|
| TestEventBus | 5 | Emit, sequence, replay, subscribe, handlers |
| TestStorage | 4 | Gate open/resolve, list by status, event log |
| TestServerEndpoints | 5 | Health, state push/get/merge, decisions |
| TestDecisionGateCycle | 3 | Full open→resolve cycle, validation, 404 |
| TestSSEStream | 2 | Content-type, buffer replay |
| TestContextLifecycle | 2 | Context creation, phase progression |
| TestAgUiEventSerialization | 2 | camelCase payload, SSE format |
| TestDiscoveryAPI | 1 | Endpoint mount verification |

## Client Integration

The IDFWU Swift macOS app (`/Users/jeremiah/Developer/idfw-idfwu/IDFWU/`) consumes the daemon:

- **DaemonProjectProvider**: Fetches `/api/v3/projects` for sidebar
- **EventStreamViewModel**: Connects to `/api/v3/events` SSE stream
- **Rev-Eng Client**: Posts `idea_rev_eng` events to daemon

---

*Version: 4.0.0 | Last Updated: 2026-04-07*

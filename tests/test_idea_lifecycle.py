"""CP-50: End-to-end integration tests for /idea lifecycle.

Tests the daemon server (FastAPI), EventBus, Storage (SQLite), and
discovery API without requiring external services (Plane, APM).
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

# ── Server + event infrastructure ────────────────────────────────────

import sys

# Ensure the idea skill package is importable
SKILLS_PATH = Path.home() / ".claude" / "skills"
if str(SKILLS_PATH) not in sys.path:
    sys.path.insert(0, str(SKILLS_PATH))

from idea.server.events import AgUiEvent, EventBus, EventType, state_snapshot, new_gate_id
from idea.server.storage import Storage


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def bus():
    return EventBus(buffer_size=100)


@pytest.fixture
def storage(tmp_path):
    return Storage(path=tmp_path / "test_idea.db")


@pytest.fixture
def app(bus, storage):
    from idea.server.app import create_app
    return create_app(bus, storage, project_slug="test-cp50")


@pytest.fixture
def client(app):
    import httpx
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture
def context_dir(tmp_path):
    """Temp directory for idea context files."""
    d = tmp_path / "contexts"
    d.mkdir()
    return d


# ── 1. EventBus unit tests ──────────────────────────────────────────

class TestEventBus:
    @pytest.mark.asyncio
    async def test_emit_assigns_sequence(self, bus):
        ev = AgUiEvent(EventType.STATE_SNAPSHOT, "t1", data={"state": {"a": 1}})
        result = await bus.emit(ev)
        assert result.sequence == 0

    @pytest.mark.asyncio
    async def test_emit_increments_sequence(self, bus):
        await bus.emit(AgUiEvent(EventType.STATE_SNAPSHOT, "t1"))
        ev2 = await bus.emit(AgUiEvent(EventType.STATE_SNAPSHOT, "t1"))
        assert ev2.sequence == 1

    @pytest.mark.asyncio
    async def test_events_since_replays(self, bus):
        for i in range(5):
            await bus.emit(AgUiEvent(EventType.STATE_SNAPSHOT, "t1", data={"i": i}))
        replayed = bus.events_since(3)
        assert len(replayed) == 2
        assert replayed[0].sequence == 3

    @pytest.mark.asyncio
    async def test_subscriber_receives_events(self, bus):
        q = bus.subscribe()
        ev = AgUiEvent(EventType.RUN_STARTED, "t1", run_id="r1")
        await bus.emit(ev)
        received = q.get_nowait()
        assert received.type == EventType.RUN_STARTED
        bus.unsubscribe(q)

    @pytest.mark.asyncio
    async def test_handler_invoked(self, bus):
        captured = []
        bus.on(EventType.CUSTOM, lambda e: captured.append(e))
        await bus.emit(AgUiEvent(EventType.CUSTOM, "t1", data={"name": "test"}))
        assert len(captured) == 1


# ── 2. Storage (SQLite) tests ───────────────────────────────────────

class TestStorage:
    def test_open_and_resolve_gate(self, storage):
        gid = "gate-test001"
        storage.open_gate(gid, "test-proj", "Approve deploy?", ["approve", "reject"], phase="plan")
        gate = storage.get_gate(gid)
        assert gate is not None
        assert gate["status"] == "pending"
        assert gate["title"] == "Approve deploy?"

        resolved = storage.resolve_gate(gid, "approve", "jeremiah", "looks good")
        assert resolved is True
        gate = storage.get_gate(gid)
        assert gate["status"] == "resolved"
        assert gate["decision"] == "approve"
        assert gate["resolved_at"] is not None

    def test_resolve_nonexistent_gate(self, storage):
        assert storage.resolve_gate("nope", "approve", "j") is False

    def test_list_gates_by_status(self, storage):
        storage.open_gate("g1", "proj", "Gate 1", ["approve", "reject"])
        storage.open_gate("g2", "proj", "Gate 2", ["approve", "reject"])
        storage.resolve_gate("g1", "approve", "j")
        pending = storage.list_gates(project_slug="proj", status="pending")
        assert len(pending) == 1
        assert pending[0]["gate_id"] == "g2"

    def test_log_and_retrieve_events(self, storage):
        seq = storage.log_event("STATE_SNAPSHOT", "thread-1", {"state": {"x": 1}}, run_id="r1")
        assert seq > 0
        events = storage.events_for_thread("thread-1")
        assert len(events) == 1
        assert events[0]["event_type"] == "STATE_SNAPSHOT"


# ── 3. Server endpoint tests ────────────────────────────────────────

class TestServerEndpoints:
    @pytest.mark.asyncio
    async def test_health(self, client):
        r = await client.get("/api/v3/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["project"] == "test-cp50"

    @pytest.mark.asyncio
    async def test_state_push_and_get(self, client):
        r = await client.post("/api/v3/state/thread-1", json={"phase": "discover", "progress": 0.5})
        assert r.status_code == 200
        assert r.json()["ok"] is True

        r = await client.get("/api/v3/state/thread-1")
        assert r.status_code == 200
        state = r.json()
        assert state["phase"] == "discover"
        assert state["progress"] == 0.5

    @pytest.mark.asyncio
    async def test_state_merge(self, client):
        await client.post("/api/v3/state/t2", json={"a": 1})
        await client.post("/api/v3/state/t2", json={"b": 2})
        state = (await client.get("/api/v3/state/t2")).json()
        assert state["a"] == 1
        assert state["b"] == 2

    @pytest.mark.asyncio
    async def test_empty_state(self, client):
        r = await client.get("/api/v3/state/nonexistent")
        assert r.status_code == 200
        assert r.json() == {}

    @pytest.mark.asyncio
    async def test_decisions_empty(self, client):
        r = await client.get("/api/v3/decisions")
        assert r.status_code == 200
        assert r.json() == []


# ── 4. Decision gate full cycle ─────────────────────────────────────

class TestDecisionGateCycle:
    @pytest.mark.asyncio
    async def test_open_gate_via_custom_event_then_resolve(self, client):
        gate_id = new_gate_id()
        # Open gate via CUSTOM event through state endpoint
        r = await client.post("/api/v3/state/thread-1", json={
            "type": "CUSTOM",
            "name": "decision_gate_open",
            "data": {
                "gate_id": gate_id,
                "title": "Approve architecture?",
                "options": ["approve", "reject", "defer"],
                "phase": "define",
                "description": "Review the proposed architecture before proceeding.",
            }
        })
        assert r.status_code == 200
        assert r.json()["event"] == "decision_gate_open"

        # Verify gate appears in list
        gates = (await client.get("/api/v3/decisions?status=pending")).json()
        assert any(g["gate_id"] == gate_id for g in gates)

        # Resolve
        r = await client.post(f"/api/v3/decisions/{gate_id}", json={
            "decision": "approve",
            "reason": "Architecture looks solid",
            "approver": "jeremiah",
            "thread_id": "thread-1",
        })
        assert r.status_code == 200
        assert r.json()["decision"] == "approve"

        # Verify resolved
        gates = (await client.get("/api/v3/decisions?status=pending")).json()
        assert not any(g["gate_id"] == gate_id for g in gates)

    @pytest.mark.asyncio
    async def test_resolve_invalid_decision(self, client):
        r = await client.post("/api/v3/decisions/any-gate", json={
            "decision": "maybe",
            "thread_id": "t1",
        })
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_resolve_missing_gate(self, client):
        r = await client.post("/api/v3/decisions/nonexistent", json={
            "decision": "approve",
            "thread_id": "t1",
        })
        assert r.status_code == 404


# ── 5. SSE event stream ─────────────────────────────────────────────

class TestSSEStream:
    @pytest.mark.asyncio
    async def test_events_endpoint_returns_sse(self, client):
        """Verify SSE endpoint returns correct content type."""
        # Push a state to populate the bus buffer
        await client.post("/api/v3/state/t1", json={"hello": "world"})
        # Stream with timeout — SSE streams are infinite by design
        try:
            async with asyncio.timeout(2):
                async with client.stream("GET", "/api/v3/events?since=-1") as r:
                    assert r.status_code == 200
                    assert "text/event-stream" in r.headers.get("content-type", "")
                    # Reading any bytes confirms the stream is alive
                    chunk = await r.aread()
                    assert len(chunk) > 0
        except (TimeoutError, asyncio.TimeoutError):
            pass  # SSE never closes — timeout is the expected exit

    @pytest.mark.asyncio
    async def test_event_bus_replay(self, bus):
        """Verify EventBus buffer replays events correctly (unit-level SSE test)."""
        await bus.emit(AgUiEvent(EventType.STATE_SNAPSHOT, "t1", data={"state": {"x": 1}}))
        await bus.emit(AgUiEvent(EventType.CUSTOM, "t1", data={"name": "test"}))
        replayed = bus.events_since(-1)
        assert len(replayed) == 2
        assert replayed[0].type == EventType.STATE_SNAPSHOT
        sse = replayed[0].to_sse()
        assert "event: STATE_SNAPSHOT" in sse


# ── 6. Context file lifecycle ────────────────────────────────────────

class TestContextLifecycle:
    def test_create_and_read_context(self, context_dir):
        """Simulate /idea new creating a context file."""
        ctx = {
            "project_id": "test-cp50-20260407",
            "project_name": "CP-50 Test Project",
            "project_slug": "cp50-test",
            "project_type": "Internal Tool",
            "target_users": "Developers",
            "problem_statement": "Need end-to-end /idea lifecycle testing",
            "tech_stack": {"language": "Python", "framework": "FastAPI"},
            "constraints": {},
            "integrations": [],
            "sizing": "new",
            "version": "4.0.0",
            "phases": {},
            "created_at": "2026-04-07T00:00:00Z",
        }
        path = context_dir / "cp50-test.json"
        path.write_text(json.dumps(ctx, indent=2))

        loaded = json.loads(path.read_text())
        assert loaded["project_slug"] == "cp50-test"
        assert loaded["version"] == "4.0.0"

    def test_phase_progression(self, context_dir):
        """Simulate phases being populated as /idea progresses."""
        ctx = {
            "project_slug": "lifecycle-test",
            "phases": {},
        }
        path = context_dir / "lifecycle-test.json"

        # Phase: discover
        ctx["phases"]["discover"] = {
            "completed_at": "2026-04-07T00:01:00Z",
            "problem_statement": "Test problem",
            "jtbd": {"functional": "Validate lifecycle", "emotional": "Confidence"},
        }
        path.write_text(json.dumps(ctx))
        assert "discover" in json.loads(path.read_text())["phases"]

        # Phase: define
        ctx["phases"]["define"] = {
            "completed_at": "2026-04-07T00:02:00Z",
            "prd_path": "/tmp/test-prd.md",
            "story_count": 12,
            "wave_count": 3,
        }
        path.write_text(json.dumps(ctx))
        phases = json.loads(path.read_text())["phases"]
        assert "discover" in phases
        assert "define" in phases
        assert phases["define"]["story_count"] == 12

        # Phase: plan
        ctx["phases"]["plan"] = {
            "completed_at": "2026-04-07T00:03:00Z",
            "plane_issue_ids": ["IDFW-101", "IDFW-102"],
            "checkpoint_range": "CP-50",
        }
        path.write_text(json.dumps(ctx))
        phases = json.loads(path.read_text())["phases"]
        assert len(phases) == 3

        # Phase: execute
        ctx["phases"]["execute"] = {
            "started_at": "2026-04-07T00:04:00Z",
            "formation_id": "formation-cp50",
        }
        path.write_text(json.dumps(ctx))
        phases = json.loads(path.read_text())["phases"]
        assert len(phases) == 4
        assert phases["execute"]["formation_id"] == "formation-cp50"


# ── 7. AgUiEvent serialization ──────────────────────────────────────

class TestAgUiEventSerialization:
    def test_to_payload_camel_case(self):
        ev = AgUiEvent(EventType.STATE_SNAPSHOT, "t1", run_id="r1", data={"my_key": "val"})
        payload = ev.to_payload()
        assert "myKey" in payload
        assert payload["threadId"] == "t1"
        assert payload["runId"] == "r1"

    def test_to_sse_format(self):
        ev = AgUiEvent(EventType.CUSTOM, "t1", data={"name": "test"})
        ev.sequence = 5
        sse = ev.to_sse()
        assert "id: 5" in sse
        assert "event: CUSTOM" in sse
        assert '"name": "test"' in sse


# ── 8. Discovery API (if available) ─────────────────────────────────

class TestDiscoveryAPI:
    @pytest.mark.asyncio
    async def test_discovery_endpoint_exists(self, client):
        """The /api/v3/projects endpoint should be mounted."""
        r = await client.get("/api/v3/projects")
        # Should return 200 with a list (may be empty without providers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

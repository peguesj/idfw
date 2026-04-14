#!/bin/bash
# CCEM APM Session Init Hook - dual-APM stateless emitter
# Emits to both:
#   - port 3031 (IDFW project-scoped Phoenix APM)
#   - port 3032 (global CCEM APM v9.0.0)
# Pattern: fire-and-forget, no retries, no local state

set +e

PROJECT_ROOT="${CLAUDE_PROJECT_ROOT:-$(pwd)}"
SESSION_ID="${CLAUDE_SESSION_ID:-$(uuidgen 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "sess-$$-$(date +%s)")}"
PROJECT_NAME=$(basename "$PROJECT_ROOT")
AGENT_ID="session-$SESSION_ID"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FORMATION_ID="${CLAUDE_FORMATION_ID:-solo}"
WAVE="${CLAUDE_WAVE:-0}"
AUTH_SESSION="${IDFW_APM_AUTH_SESSION:-auth_sess_014ddf81a66cf178425843dd}"

REGISTER_PAYLOAD=$(cat <<JSON
{
  "agent_id": "$AGENT_ID",
  "project": "$PROJECT_NAME",
  "role": "session",
  "status": "active",
  "session_id": "$SESSION_ID",
  "formation_id": "$FORMATION_ID",
  "wave_number": $WAVE,
  "started_at": "$TS"
}
JSON
)

UPM_SPAWN_PAYLOAD=$(cat <<JSON
{
  "event_type": "session_start",
  "agent_id": "$AGENT_ID",
  "session_id": "$SESSION_ID",
  "project": "$PROJECT_NAME",
  "formation_id": "$FORMATION_ID",
  "wave": $WAVE,
  "payload": {
    "role": "session",
    "auth_session": "$AUTH_SESSION",
    "project_root": "$PROJECT_ROOT",
    "started_at": "$TS"
  }
}
JSON
)

# Port 3031 - IDFW scoped
(curl -s --max-time 2 -X POST http://localhost:3031/api/register \
  -H "Content-Type: application/json" \
  -d "$REGISTER_PAYLOAD" >/dev/null 2>&1) &

(curl -s --max-time 2 -X POST http://localhost:3031/api/upm/event \
  -H "Content-Type: application/json" \
  -d "$UPM_SPAWN_PAYLOAD" >/dev/null 2>&1) &

# Port 3032 - global CCEM
(curl -s --max-time 2 -X POST http://localhost:3032/api/register \
  -H "Content-Type: application/json" \
  -d "$REGISTER_PAYLOAD" >/dev/null 2>&1) &

(curl -s --max-time 2 -X POST http://localhost:3032/api/upm/event \
  -H "Content-Type: application/json" \
  -d "$UPM_SPAWN_PAYLOAD" >/dev/null 2>&1) &

exit 0

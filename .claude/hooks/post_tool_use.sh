#!/bin/bash
# CCEM APM Post-Tool-Use Hook - dual-APM stateless emitter
# Emits task_complete + heartbeat to both 3031 and 3032
# Stateless: no local writes, no retries, fire-and-forget

set +e

AGENT_ID="${CLAUDE_AGENT_ID:-session-${CLAUDE_SESSION_ID:-unknown}}"
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_USE_ID="${CLAUDE_TOOL_USE_ID:-$(date +%s)-$$}"
TOOL_STATUS="${CLAUDE_TOOL_STATUS:-completed}"
TOOL_DURATION_MS="${CLAUDE_TOOL_DURATION_MS:-0}"
PROJECT_NAME="${CLAUDE_PROJECT_NAME:-$(basename "${CLAUDE_PROJECT_ROOT:-$(pwd)}")}"
FORMATION_ID="${CLAUDE_FORMATION_ID:-solo}"
WAVE="${CLAUDE_WAVE:-0}"
TASK_SUBJECT="${CLAUDE_TASK_SUBJECT:-$TOOL_NAME}"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

HEARTBEAT_PAYLOAD=$(cat <<JSON
{
  "agent_id": "$AGENT_ID",
  "status": "$TOOL_STATUS",
  "message": "Tool done: $TOOL_NAME",
  "tool_name": "$TOOL_NAME",
  "tool_use_id": "$TOOL_USE_ID",
  "duration_ms": $TOOL_DURATION_MS,
  "formation_id": "$FORMATION_ID",
  "wave": $WAVE,
  "timestamp": "$TS"
}
JSON
)

UPM_EVENT_PAYLOAD=$(cat <<JSON
{
  "event_type": "task_complete",
  "agent_id": "$AGENT_ID",
  "session_id": "$SESSION_ID",
  "project": "$PROJECT_NAME",
  "formation_id": "$FORMATION_ID",
  "wave": $WAVE,
  "payload": {
    "tool_name": "$TOOL_NAME",
    "tool_use_id": "$TOOL_USE_ID",
    "task_subject": "$TASK_SUBJECT",
    "status": "$TOOL_STATUS",
    "duration_ms": $TOOL_DURATION_MS,
    "completed_at": "$TS"
  }
}
JSON
)

# Port 3031 - IDFW scoped
(curl -s --max-time 2 -X POST http://localhost:3031/api/heartbeat \
  -H "Content-Type: application/json" \
  -d "$HEARTBEAT_PAYLOAD" >/dev/null 2>&1) &

(curl -s --max-time 2 -X POST http://localhost:3031/api/upm/event \
  -H "Content-Type: application/json" \
  -d "$UPM_EVENT_PAYLOAD" >/dev/null 2>&1) &

# Port 3032 - global CCEM
(curl -s --max-time 2 -X POST http://localhost:3032/api/heartbeat \
  -H "Content-Type: application/json" \
  -d "$HEARTBEAT_PAYLOAD" >/dev/null 2>&1) &

(curl -s --max-time 2 -X POST http://localhost:3032/api/upm/event \
  -H "Content-Type: application/json" \
  -d "$UPM_EVENT_PAYLOAD" >/dev/null 2>&1) &

exit 0

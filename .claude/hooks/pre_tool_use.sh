#!/bin/bash
# CCEM APM Pre-Tool-Use Hook - dual-APM stateless emitter
# Emits task_start + heartbeat to both 3031 and 3032
# Stateless: no local writes, no retries, fire-and-forget

set +e

AGENT_ID="${CLAUDE_AGENT_ID:-session-${CLAUDE_SESSION_ID:-unknown}}"
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_USE_ID="${CLAUDE_TOOL_USE_ID:-$(date +%s)-$$}"
PROJECT_NAME="${CLAUDE_PROJECT_NAME:-$(basename "${CLAUDE_PROJECT_ROOT:-$(pwd)}")}"
FORMATION_ID="${CLAUDE_FORMATION_ID:-solo}"
WAVE="${CLAUDE_WAVE:-0}"
TASK_SUBJECT="${CLAUDE_TASK_SUBJECT:-$TOOL_NAME}"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

HEARTBEAT_PAYLOAD=$(cat <<JSON
{
  "agent_id": "$AGENT_ID",
  "status": "working",
  "message": "Tool: $TOOL_NAME",
  "tool_name": "$TOOL_NAME",
  "tool_use_id": "$TOOL_USE_ID",
  "formation_id": "$FORMATION_ID",
  "wave": $WAVE,
  "timestamp": "$TS"
}
JSON
)

UPM_EVENT_PAYLOAD=$(cat <<JSON
{
  "event_type": "task_start",
  "agent_id": "$AGENT_ID",
  "session_id": "$SESSION_ID",
  "project": "$PROJECT_NAME",
  "formation_id": "$FORMATION_ID",
  "wave": $WAVE,
  "payload": {
    "tool_name": "$TOOL_NAME",
    "tool_use_id": "$TOOL_USE_ID",
    "task_subject": "$TASK_SUBJECT",
    "started_at": "$TS"
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

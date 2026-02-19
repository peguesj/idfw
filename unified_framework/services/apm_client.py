"""
APM Client for CCEM APM v4 Integration
Provides fire-and-forget telemetry to the CCEM APM server on port 3031.
"""

import json
import logging
import threading
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

APM_BASE_URL = "http://localhost:3031"


def _post_async(path: str, data: Dict[str, Any]) -> None:
    """Fire-and-forget POST to APM. Never blocks, never raises."""
    def _do_post():
        try:
            url = f"{APM_BASE_URL}{path}"
            body = json.dumps(data).encode("utf-8")
            req = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            urlopen(req, timeout=3)
        except (URLError, OSError, Exception) as e:
            logger.debug(f"APM post to {path} failed (non-blocking): {e}")

    threading.Thread(target=_do_post, daemon=True).start()


def register_agent(agent_id: str, project: str, role: str, status: str = "active") -> None:
    """Register an agent with APM."""
    _post_async("/api/register", {
        "agent_id": agent_id,
        "project": project,
        "role": role,
        "status": status,
    })


def heartbeat(agent_id: str, status: str = "active", message: str = "") -> None:
    """Send agent heartbeat to APM."""
    _post_async("/api/heartbeat", {
        "agent_id": agent_id,
        "status": status,
        "message": message,
    })


def notify(title: str, message: str, level: str = "info") -> None:
    """Send a notification to APM dashboard."""
    _post_async("/api/notify", {
        "title": title,
        "message": message,
        "level": level,
    })


def track_skill(skill: str, session_id: str, project: str) -> None:
    """Track a skill invocation."""
    _post_async("/api/skills/track", {
        "skill": skill,
        "session_id": session_id,
        "project": project,
    })


def upm_event(upm_session_id: str, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Report a UPM lifecycle event."""
    _post_async("/api/upm/event", {
        "upm_session_id": upm_session_id,
        "event_type": event_type,
        "data": data or {},
    })

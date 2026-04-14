"""
Memory management system for storing and retrieving patterns, learnings, and historical data.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

class PatternStore:
    """Store for identified patterns with persistence."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'patterns'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self._load_patterns()
    
    def add_pattern(self, pattern: Dict[str, Any]) -> str:
        """Add a new pattern to the store."""
        if 'pattern_id' not in pattern:
            pattern['pattern_id'] = str(uuid.uuid4())
        
        if 'created_at' not in pattern:
            pattern['created_at'] = datetime.now().isoformat()
            
        if 'last_updated' not in pattern:
            pattern['last_updated'] = datetime.now().isoformat()
        
        self.patterns[pattern['pattern_id']] = pattern
        self._save_patterns()
        
        return pattern['pattern_id']
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID."""
        return self.patterns.get(pattern_id)
    
    def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing pattern."""
        if pattern_id not in self.patterns:
            return False
        
        pattern = self.patterns[pattern_id]
        pattern.update(updates)
        pattern['last_updated'] = datetime.now().isoformat()
        
        self._save_patterns()
        return True
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Dict[str, Any]]:
        """Get patterns by type."""
        return [
            pattern for pattern in self.patterns.values()
            if pattern.get('type') == pattern_type
        ]
    
    def get_patterns_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get patterns by tags."""
        result = []
        for pattern in self.patterns.values():
            pattern_tags = set(pattern.get('tags', []))
            if pattern_tags.intersection(tags):
                result.append(pattern)
        return result
    
    def _save_patterns(self):
        """Save patterns to disk."""
        patterns_file = self.storage_path / 'patterns.json'
        with open(patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_patterns(self):
        """Load patterns from disk."""
        patterns_file = self.storage_path / 'patterns.json'
        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    self.patterns = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load patterns: {e}")


class LearningStore:
    """Store for learning outcomes and historical insights."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'learning'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.learnings: Dict[str, Dict[str, Any]] = {}
        self._load_learnings()
    
    def add_learning(self, learning: Dict[str, Any]) -> str:
        """Add a new learning insight."""
        if 'learning_id' not in learning:
            learning['learning_id'] = str(uuid.uuid4())
        
        if 'created_at' not in learning:
            learning['created_at'] = datetime.now().isoformat()
        
        self.learnings[learning['learning_id']] = learning
        self._save_learnings()
        
        return learning['learning_id']
    
    def get_recent_learnings(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get learnings from the last N days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        return [
            learning for learning in self.learnings.values()
            if learning.get('created_at', '') >= cutoff
        ]
    
    def get_learnings_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get learnings by category."""
        return [
            learning for learning in self.learnings.values()
            if learning.get('category') == category
        ]
    
    def _save_learnings(self):
        """Save learnings to disk."""
        learnings_file = self.storage_path / 'learnings.json'
        with open(learnings_file, 'w') as f:
            json.dump(self.learnings, f, indent=2)
    
    def _load_learnings(self):
        """Load learnings from disk."""
        learnings_file = self.storage_path / 'learnings.json'
        if learnings_file.exists():
            try:
                with open(learnings_file) as f:
                    self.learnings = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load learnings: {e}")


class SessionStore:
    """Store for session data and context tracking."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'sessions'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.active_session_id = str(uuid.uuid4())
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._load_sessions()
    
    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new session."""
        session_id = str(uuid.uuid4())
        
        session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'metadata': metadata or {},
            'events': [],
            'active': True
        }
        
        self.sessions[session_id] = session
        self.active_session_id = session_id
        self._save_sessions()
        
        return session_id
    
    def end_session(self, session_id: Optional[str] = None) -> bool:
        """End an active session."""
        session_id = session_id or self.active_session_id
        
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        if not session.get('active', False):
            return False
        
        session['end_time'] = datetime.now().isoformat()
        session['active'] = False
        
        self._save_sessions()
        return True
    
    def add_session_event(self, event: Dict[str, Any], session_id: Optional[str] = None) -> bool:
        """Add an event to a session."""
        session_id = session_id or self.active_session_id
        
        if session_id not in self.sessions:
            return False
        
        if 'timestamp' not in event:
            event['timestamp'] = datetime.now().isoformat()
            
        if 'event_id' not in event:
            event['event_id'] = str(uuid.uuid4())
        
        self.sessions[session_id].setdefault('events', []).append(event)
        self._save_sessions()
        
        return True
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions."""
        return [
            session for session in self.sessions.values()
            if session.get('active', False)
        ]
    
    def _save_sessions(self):
        """Save sessions to disk."""
        # Save active sessions to active file
        active_file = self.storage_path / 'active_sessions.json'
        active_sessions = {
            sid: session for sid, session in self.sessions.items()
            if session.get('active', False)
        }
        
        with open(active_file, 'w') as f:
            json.dump(active_sessions, f, indent=2)
        
        # Save completed sessions by date
        today = datetime.now().strftime('%Y-%m-%d')
        completed_file = self.storage_path / f'completed_sessions_{today}.json'
        completed_sessions = {
            sid: session for sid, session in self.sessions.items()
            if not session.get('active', True)
        }
        
        with open(completed_file, 'a') as f:
            for session in completed_sessions.values():
                f.write(json.dumps(session) + '\n')
    
    def _load_sessions(self):
        """Load active sessions from disk."""
        active_file = self.storage_path / 'active_sessions.json'
        if active_file.exists():
            try:
                with open(active_file) as f:
                    self.sessions = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load active sessions: {e}")


class MemoryManager:
    """Central memory manager coordinating all memory stores."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        base_path = storage_path or Path.home() / '.claude' / 'hooks'
        base_path.mkdir(parents=True, exist_ok=True)
        
        self.pattern_store = PatternStore(base_path / 'patterns')
        self.learning_store = LearningStore(base_path / 'learning')
        self.session_store = SessionStore(base_path / 'sessions')
        
        # Create or load runtime cache
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        
        # Start a session for this instance
        self.session_id = self.session_store.start_session({
            'instance_id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'type': 'memory_manager'
        })
    
    def store_patterns(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Store multiple patterns."""
        pattern_ids = []
        for pattern in patterns:
            pattern_id = self.pattern_store.add_pattern(pattern)
            pattern_ids.append(pattern_id)
        return pattern_ids
    
    def store_learning(self, learning: Dict[str, Any]) -> str:
        """Store a learning insight."""
        return self.learning_store.add_learning(learning)
    
    def record_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Record an event in the current session."""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        }
        return self.session_store.add_session_event(event)
    
    def get_recent_patterns(self, days: int = 7, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get patterns from the recent past."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        patterns = []
        for pattern in self.pattern_store.patterns.values():
            created_at = pattern.get('created_at', '')
            last_updated = pattern.get('last_updated', created_at)
            
            # Check if pattern is recent
            if last_updated >= cutoff:
                # Check type if specified
                if pattern_type is None or pattern.get('type') == pattern_type:
                    patterns.append(pattern)
        
        return patterns
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key not in self.cache:
            return None
        
        # Check TTL
        if key in self.cache_ttl:
            if datetime.now() > self.cache_ttl[key]:
                del self.cache[key]
                del self.cache_ttl[key]
                return None
        
        return self.cache[key]
    
    def set_cached(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set a value in the cache with optional TTL."""
        self.cache[key] = value
        
        if ttl_seconds is not None:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self.cache_ttl[key] = expiry
    
    def generate_context(self) -> Dict[str, Any]:
        """Generate a context object with relevant memory data."""
        recent_patterns = self.get_recent_patterns(days=1)
        recent_learnings = self.learning_store.get_recent_learnings(days=1)
        
        return {
            'session_id': self.session_id,
            'recent_patterns_count': len(recent_patterns),
            'recent_learnings_count': len(recent_learnings),
            'patterns_sample': recent_patterns[:3] if recent_patterns else [],
            'learnings_sample': recent_learnings[:3] if recent_learnings else [],
            'timestamp': datetime.now().isoformat()
        }
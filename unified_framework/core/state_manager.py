"""
Unified State Manager for IDFWU Framework
Linear Project: 4d649a6501f7

This module provides unified state management with:
- IDFW variables integration
- Agent state synchronization
- Cache and persistence
- Conflict resolution
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable

from pydantic import BaseModel, Field, ConfigDict


# Configure logging
logger = logging.getLogger(__name__)


class VariableScope(str, Enum):
    """Variable scope levels"""
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"
    AGENT = "agent"
    TASK = "task"


class VariableType(str, Enum):
    """Variable type classification"""
    IMMUTABLE = "immutable"      # IDFW immutable variables -> Agent config
    MUTABLE = "mutable"          # IDFW mutable variables -> Agent runtime state
    PROJECT = "project"          # Project variables -> Task context
    DOCUMENT = "document"        # Document variables -> Tool parameters
    COMPUTED = "computed"        # Computed/derived values


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    MANUAL = "manual"
    REJECT = "reject"


class StateVariable(BaseModel):
    """Individual state variable"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    key: str
    value: Any
    variable_type: VariableType
    scope: VariableScope
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class StateSnapshot(BaseModel):
    """Snapshot of state at a point in time"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    snapshot_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    variables: Dict[str, StateVariable]
    description: Optional[str] = None


class StateObserver:
    """Observer for state changes"""

    def __init__(
        self,
        callback: Callable[[str, StateVariable, Optional[StateVariable]], None],
        filter_keys: Optional[Set[str]] = None,
        filter_scopes: Optional[Set[VariableScope]] = None,
    ) -> None:
        """
        Initialize state observer

        Args:
            callback: Function to call on state changes
            filter_keys: Optional set of keys to observe
            filter_scopes: Optional set of scopes to observe
        """
        self.callback = callback
        self.filter_keys = filter_keys
        self.filter_scopes = filter_scopes

    def should_notify(
        self,
        key: str,
        variable: StateVariable,
    ) -> bool:
        """
        Check if observer should be notified

        Args:
            key: Variable key
            variable: State variable

        Returns:
            True if should notify
        """
        if self.filter_keys and key not in self.filter_keys:
            return False

        if self.filter_scopes and variable.scope not in self.filter_scopes:
            return False

        return True


class StateCache:
    """In-memory cache for state variables"""

    def __init__(self, ttl: int = 300) -> None:
        """
        Initialize state cache

        Args:
            ttl: Time to live in seconds (default 5 minutes)
        """
        self.ttl = ttl
        self.cache: Dict[str, tuple[StateVariable, datetime]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[StateVariable]:
        """Get variable from cache"""
        async with self._lock:
            entry = self.cache.get(key)

            if not entry:
                return None

            variable, expiry = entry

            # Check if expired
            if datetime.utcnow() > expiry:
                del self.cache[key]
                return None

            return variable

    async def set(self, key: str, variable: StateVariable) -> None:
        """Set variable in cache"""
        async with self._lock:
            expiry = datetime.utcnow() + timedelta(seconds=self.ttl)
            self.cache[key] = (variable, expiry)

    async def delete(self, key: str) -> None:
        """Delete variable from cache"""
        async with self._lock:
            self.cache.pop(key, None)

    async def clear(self) -> None:
        """Clear entire cache"""
        async with self._lock:
            self.cache.clear()

    async def cleanup_expired(self) -> int:
        """Remove expired entries"""
        async with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if now > expiry
            ]

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)


class StatePersistence:
    """Persistence layer for state variables"""

    def __init__(self, storage_path: Path) -> None:
        """
        Initialize persistence layer

        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save(self, key: str, variable: StateVariable) -> None:
        """
        Save variable to disk

        Args:
            key: Variable key
            variable: State variable
        """
        async with self._lock:
            file_path = self.storage_path / f"{key}.json"

            try:
                with open(file_path, 'w') as f:
                    json.dump(variable.dict(), f, indent=2, default=str)
                logger.debug(f"Saved state variable: {key}")
            except Exception as e:
                logger.error(f"Failed to save state variable {key}: {e}")

    async def load(self, key: str) -> Optional[StateVariable]:
        """
        Load variable from disk

        Args:
            key: Variable key

        Returns:
            State variable or None if not found
        """
        async with self._lock:
            file_path = self.storage_path / f"{key}.json"

            if not file_path.exists():
                return None

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return StateVariable(**data)
            except Exception as e:
                logger.error(f"Failed to load state variable {key}: {e}")
                return None

    async def delete(self, key: str) -> None:
        """
        Delete variable from disk

        Args:
            key: Variable key
        """
        async with self._lock:
            file_path = self.storage_path / f"{key}.json"

            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted state variable: {key}")

    async def list_keys(self) -> List[str]:
        """
        List all persisted variable keys

        Returns:
            List of variable keys
        """
        async with self._lock:
            return [
                f.stem for f in self.storage_path.glob("*.json")
            ]


class StateManager:
    """
    Main state manager for unified framework
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        enable_cache: bool = True,
        cache_ttl: int = 300,
        conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS,
    ) -> None:
        """
        Initialize state manager

        Args:
            storage_path: Path for state persistence
            enable_cache: Enable in-memory caching
            cache_ttl: Cache TTL in seconds
            conflict_resolution: Default conflict resolution strategy
        """
        self.storage_path = storage_path or Path.home() / ".idfwu" / "state"
        self.conflict_resolution = conflict_resolution

        # Initialize components
        self.cache = StateCache(ttl=cache_ttl) if enable_cache else None
        self.persistence = StatePersistence(self.storage_path)

        # In-memory state
        self.variables: Dict[str, StateVariable] = {}
        self.observers: List[StateObserver] = []
        self.snapshots: Dict[str, StateSnapshot] = {}

        self._lock = asyncio.Lock()

        logger.info(f"Initialized state manager at: {self.storage_path}")

    async def set(
        self,
        key: str,
        value: Any,
        variable_type: VariableType = VariableType.MUTABLE,
        scope: VariableScope = VariableScope.GLOBAL,
        updated_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> StateVariable:
        """
        Set a state variable

        Args:
            key: Variable key
            value: Variable value
            variable_type: Variable type
            scope: Variable scope
            updated_by: ID of updater
            metadata: Optional metadata
            tags: Optional tags

        Returns:
            Updated state variable
        """
        async with self._lock:
            existing = self.variables.get(key)

            # Check for conflicts
            if existing:
                if existing.variable_type == VariableType.IMMUTABLE:
                    raise ValueError(f"Cannot modify immutable variable: {key}")

                # Handle conflict resolution
                if self.conflict_resolution == ConflictResolution.FIRST_WRITE_WINS:
                    logger.warning(f"Variable {key} already exists, keeping first value")
                    return existing

                # Update existing variable
                variable = StateVariable(
                    key=key,
                    value=value,
                    variable_type=existing.variable_type,
                    scope=existing.scope,
                    version=existing.version + 1,
                    created_at=existing.created_at,
                    updated_at=datetime.utcnow(),
                    updated_by=updated_by,
                    metadata=metadata or existing.metadata,
                    tags=tags or existing.tags,
                )
            else:
                # Create new variable
                variable = StateVariable(
                    key=key,
                    value=value,
                    variable_type=variable_type,
                    scope=scope,
                    updated_by=updated_by,
                    metadata=metadata or {},
                    tags=tags or [],
                )

            self.variables[key] = variable

            # Update cache
            if self.cache:
                await self.cache.set(key, variable)

            # Persist to disk
            await self.persistence.save(key, variable)

            # Notify observers
            await self._notify_observers(key, variable, existing)

            logger.debug(f"Set state variable: {key} (v{variable.version})")
            return variable

    async def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a state variable value

        Args:
            key: Variable key
            default: Default value if not found

        Returns:
            Variable value or default
        """
        # Check cache first
        if self.cache:
            cached = await self.cache.get(key)
            if cached:
                return cached.value

        # Check in-memory
        variable = self.variables.get(key)
        if variable:
            return variable.value

        # Load from disk
        variable = await self.persistence.load(key)
        if variable:
            self.variables[key] = variable
            if self.cache:
                await self.cache.set(key, variable)
            return variable.value

        return default

    async def get_variable(self, key: str) -> Optional[StateVariable]:
        """
        Get complete state variable

        Args:
            key: Variable key

        Returns:
            State variable or None
        """
        # Check cache first
        if self.cache:
            cached = await self.cache.get(key)
            if cached:
                return cached

        # Check in-memory
        variable = self.variables.get(key)
        if variable:
            return variable

        # Load from disk
        variable = await self.persistence.load(key)
        if variable:
            self.variables[key] = variable
            if self.cache:
                await self.cache.set(key, variable)

        return variable

    async def delete(self, key: str) -> bool:
        """
        Delete a state variable

        Args:
            key: Variable key

        Returns:
            True if deleted
        """
        async with self._lock:
            variable = self.variables.get(key)

            if variable and variable.variable_type == VariableType.IMMUTABLE:
                raise ValueError(f"Cannot delete immutable variable: {key}")

            # Remove from memory
            self.variables.pop(key, None)

            # Remove from cache
            if self.cache:
                await self.cache.delete(key)

            # Remove from disk
            await self.persistence.delete(key)

            logger.debug(f"Deleted state variable: {key}")
            return True

    async def list_variables(
        self,
        scope: Optional[VariableScope] = None,
        variable_type: Optional[VariableType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[StateVariable]:
        """
        List variables with optional filtering

        Args:
            scope: Optional scope filter
            variable_type: Optional type filter
            tags: Optional tag filter

        Returns:
            List of matching variables
        """
        # Ensure all variables are loaded
        persisted_keys = await self.persistence.list_keys()
        for key in persisted_keys:
            if key not in self.variables:
                variable = await self.persistence.load(key)
                if variable:
                    self.variables[key] = variable

        # Filter variables
        variables = list(self.variables.values())

        if scope:
            variables = [v for v in variables if v.scope == scope]

        if variable_type:
            variables = [v for v in variables if v.variable_type == variable_type]

        if tags:
            tag_set = set(tags)
            variables = [
                v for v in variables
                if tag_set.intersection(v.tags)
            ]

        return variables

    def add_observer(self, observer: StateObserver) -> None:
        """
        Add a state observer

        Args:
            observer: Observer to add
        """
        self.observers.append(observer)
        logger.debug("Added state observer")

    def remove_observer(self, observer: StateObserver) -> None:
        """
        Remove a state observer

        Args:
            observer: Observer to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)
            logger.debug("Removed state observer")

    async def _notify_observers(
        self,
        key: str,
        new_variable: StateVariable,
        old_variable: Optional[StateVariable],
    ) -> None:
        """
        Notify observers of state change

        Args:
            key: Variable key
            new_variable: New variable value
            old_variable: Previous variable value
        """
        for observer in self.observers:
            if observer.should_notify(key, new_variable):
                try:
                    observer.callback(key, new_variable, old_variable)
                except Exception as e:
                    logger.error(f"Observer callback error: {e}")

    async def create_snapshot(
        self,
        snapshot_id: str,
        description: Optional[str] = None,
    ) -> StateSnapshot:
        """
        Create a snapshot of current state

        Args:
            snapshot_id: Snapshot identifier
            description: Optional description

        Returns:
            Created snapshot
        """
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            variables=self.variables.copy(),
            description=description,
        )

        self.snapshots[snapshot_id] = snapshot
        logger.info(f"Created state snapshot: {snapshot_id}")

        return snapshot

    async def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore state from a snapshot

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            True if successful
        """
        snapshot = self.snapshots.get(snapshot_id)

        if not snapshot:
            logger.error(f"Snapshot not found: {snapshot_id}")
            return False

        async with self._lock:
            # Clear persisted keys not in snapshot
            current_keys = set(self.variables.keys())
            snapshot_keys = set(snapshot.variables.keys())
            for key in current_keys - snapshot_keys:
                await self.persistence.delete(key)

            self.variables = snapshot.variables.copy()

            # Clear cache
            if self.cache:
                await self.cache.clear()

            logger.info(f"Restored state snapshot: {snapshot_id}")
            return True
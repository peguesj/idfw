"""
Unit tests for StateManager class
Linear Project: 4d649a6501f7
Task: TEST-004 - State Manager Tests

Tests cover:
- StateManager initialization
- Variable scoping (global, project, session, agent, task)
- Variable types (immutable, mutable, project, document, computed)
- Conflict resolution strategies
- Caching with TTL
- File persistence
- State snapshots and restoration
- Observer pattern for state changes
- Concurrent operations
"""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from unified_framework.core.state_manager import (
    ConflictResolution,
    StateCache,
    StateManager,
    StateObserver,
    StatePersistence,
    StateSnapshot,
    StateVariable,
    VariableScope,
    VariableType,
)


# Fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "state"


@pytest.fixture
def temp_storage_path(tmp_path):
    """Create temporary storage path for testing"""
    storage_path = tmp_path / "state"
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


@pytest.fixture
def sample_variables() -> list[Dict[str, Any]]:
    """Load sample variables"""
    with open(FIXTURES_DIR / "sample_variables.json") as f:
        return json.load(f)


@pytest.fixture
def sample_snapshot() -> Dict[str, Any]:
    """Load sample state snapshot"""
    with open(FIXTURES_DIR / "sample_state_snapshot.json") as f:
        return json.load(f)


class TestStateVariableModel:
    """Tests for StateVariable data model"""

    def test_state_variable_creation_minimal(self):
        """Test creating StateVariable with minimal parameters"""
        variable = StateVariable(
            key="test_key",
            value="test_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        assert variable.key == "test_key"
        assert variable.value == "test_value"
        assert variable.variable_type == VariableType.MUTABLE
        assert variable.scope == VariableScope.GLOBAL
        assert variable.version == 1
        assert variable.created_at is not None
        assert variable.updated_at is not None
        assert variable.updated_by is None
        assert variable.metadata == {}
        assert variable.tags == []

    def test_state_variable_creation_full(self):
        """Test creating StateVariable with all parameters"""
        now = datetime.utcnow()
        metadata = {"source": "test", "priority": "high"}
        tags = ["test", "important"]

        variable = StateVariable(
            key="full_key",
            value={"nested": "data"},
            variable_type=VariableType.IMMUTABLE,
            scope=VariableScope.PROJECT,
            version=5,
            created_at=now,
            updated_at=now,
            updated_by="agent-001",
            metadata=metadata,
            tags=tags,
        )

        assert variable.key == "full_key"
        assert variable.value == {"nested": "data"}
        assert variable.variable_type == VariableType.IMMUTABLE
        assert variable.scope == VariableScope.PROJECT
        assert variable.version == 5
        assert variable.updated_by == "agent-001"
        assert variable.metadata == metadata
        assert variable.tags == tags

    def test_state_variable_with_different_types(self):
        """Test StateVariable with different value types"""
        # String
        var_str = StateVariable(
            key="str", value="text", variable_type=VariableType.MUTABLE, scope=VariableScope.GLOBAL
        )
        assert isinstance(var_str.value, str)

        # Integer
        var_int = StateVariable(
            key="int", value=42, variable_type=VariableType.MUTABLE, scope=VariableScope.GLOBAL
        )
        assert isinstance(var_int.value, int)

        # List
        var_list = StateVariable(
            key="list", value=[1, 2, 3], variable_type=VariableType.MUTABLE, scope=VariableScope.GLOBAL
        )
        assert isinstance(var_list.value, list)

        # Dict
        var_dict = StateVariable(
            key="dict", value={"a": 1}, variable_type=VariableType.MUTABLE, scope=VariableScope.GLOBAL
        )
        assert isinstance(var_dict.value, dict)


class TestStateManagerInitialization:
    """Tests for StateManager initialization"""

    @pytest.mark.asyncio
    async def test_init_default(self):
        """Test StateManager initialization with defaults"""
        manager = StateManager()

        assert manager.storage_path == Path.home() / ".idfwu" / "state"
        assert manager.conflict_resolution == ConflictResolution.LAST_WRITE_WINS
        assert manager.cache is not None
        assert manager.persistence is not None
        assert len(manager.variables) == 0
        assert len(manager.observers) == 0
        assert len(manager.snapshots) == 0

    @pytest.mark.asyncio
    async def test_init_custom_storage_path(self, temp_storage_path):
        """Test StateManager with custom storage path"""
        manager = StateManager(storage_path=temp_storage_path)

        assert manager.storage_path == temp_storage_path
        assert manager.storage_path.exists()

    @pytest.mark.asyncio
    async def test_init_without_cache(self, temp_storage_path):
        """Test StateManager without caching"""
        manager = StateManager(storage_path=temp_storage_path, enable_cache=False)

        assert manager.cache is None
        assert manager.persistence is not None

    @pytest.mark.asyncio
    async def test_init_custom_cache_ttl(self, temp_storage_path):
        """Test StateManager with custom cache TTL"""
        manager = StateManager(storage_path=temp_storage_path, cache_ttl=600)

        assert manager.cache is not None
        assert manager.cache.ttl == 600

    @pytest.mark.asyncio
    async def test_init_custom_conflict_resolution(self, temp_storage_path):
        """Test StateManager with custom conflict resolution"""
        manager = StateManager(
            storage_path=temp_storage_path,
            conflict_resolution=ConflictResolution.FIRST_WRITE_WINS,
        )

        assert manager.conflict_resolution == ConflictResolution.FIRST_WRITE_WINS


class TestVariableScoping:
    """Tests for variable scoping"""

    @pytest.mark.asyncio
    async def test_set_global_scope(self, temp_storage_path):
        """Test setting variable with global scope"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="global_var",
            value="global_value",
            scope=VariableScope.GLOBAL,
        )

        assert variable.scope == VariableScope.GLOBAL
        assert variable.key == "global_var"

    @pytest.mark.asyncio
    async def test_set_project_scope(self, temp_storage_path):
        """Test setting variable with project scope"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="project_var",
            value="project_value",
            scope=VariableScope.PROJECT,
        )

        assert variable.scope == VariableScope.PROJECT

    @pytest.mark.asyncio
    async def test_set_session_scope(self, temp_storage_path):
        """Test setting variable with session scope"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="session_var",
            value="session_value",
            scope=VariableScope.SESSION,
        )

        assert variable.scope == VariableScope.SESSION

    @pytest.mark.asyncio
    async def test_set_agent_scope(self, temp_storage_path):
        """Test setting variable with agent scope"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="agent_var",
            value="agent_value",
            scope=VariableScope.AGENT,
        )

        assert variable.scope == VariableScope.AGENT

    @pytest.mark.asyncio
    async def test_set_task_scope(self, temp_storage_path):
        """Test setting variable with task scope"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="task_var",
            value="task_value",
            scope=VariableScope.TASK,
        )

        assert variable.scope == VariableScope.TASK

    @pytest.mark.asyncio
    async def test_list_variables_by_scope(self, temp_storage_path):
        """Test listing variables filtered by scope"""
        manager = StateManager(storage_path=temp_storage_path)

        # Create variables with different scopes
        await manager.set("global1", "val1", scope=VariableScope.GLOBAL)
        await manager.set("global2", "val2", scope=VariableScope.GLOBAL)
        await manager.set("project1", "val3", scope=VariableScope.PROJECT)
        await manager.set("session1", "val4", scope=VariableScope.SESSION)

        # List by scope
        global_vars = await manager.list_variables(scope=VariableScope.GLOBAL)
        project_vars = await manager.list_variables(scope=VariableScope.PROJECT)

        assert len(global_vars) == 2
        assert len(project_vars) == 1
        assert all(v.scope == VariableScope.GLOBAL for v in global_vars)


class TestVariableTypes:
    """Tests for variable types"""

    @pytest.mark.asyncio
    async def test_immutable_variable(self, temp_storage_path):
        """Test immutable variable behavior"""
        manager = StateManager(storage_path=temp_storage_path)

        # Create immutable variable
        await manager.set(
            key="immutable_var",
            value="original_value",
            variable_type=VariableType.IMMUTABLE,
        )

        # Attempt to modify should raise error
        with pytest.raises(ValueError, match="Cannot modify immutable variable"):
            await manager.set(key="immutable_var", value="new_value")

    @pytest.mark.asyncio
    async def test_mutable_variable(self, temp_storage_path):
        """Test mutable variable behavior"""
        manager = StateManager(storage_path=temp_storage_path)

        # Create and modify mutable variable
        var1 = await manager.set(
            key="mutable_var",
            value="original_value",
            variable_type=VariableType.MUTABLE,
        )

        var2 = await manager.set(key="mutable_var", value="new_value")

        assert var2.version == var1.version + 1
        assert var2.value == "new_value"

    @pytest.mark.asyncio
    async def test_project_variable(self, temp_storage_path):
        """Test project variable type"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="project_config",
            value={"name": "test_project"},
            variable_type=VariableType.PROJECT,
        )

        assert variable.variable_type == VariableType.PROJECT

    @pytest.mark.asyncio
    async def test_document_variable(self, temp_storage_path):
        """Test document variable type"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="doc_params",
            value={"param1": "value1"},
            variable_type=VariableType.DOCUMENT,
        )

        assert variable.variable_type == VariableType.DOCUMENT

    @pytest.mark.asyncio
    async def test_computed_variable(self, temp_storage_path):
        """Test computed variable type"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.set(
            key="computed_sum",
            value=42,
            variable_type=VariableType.COMPUTED,
        )

        assert variable.variable_type == VariableType.COMPUTED

    @pytest.mark.asyncio
    async def test_list_variables_by_type(self, temp_storage_path):
        """Test listing variables filtered by type"""
        manager = StateManager(storage_path=temp_storage_path)

        # Create variables with different types
        await manager.set("immut1", "val1", variable_type=VariableType.IMMUTABLE)
        await manager.set("immut2", "val2", variable_type=VariableType.IMMUTABLE)
        await manager.set("mut1", "val3", variable_type=VariableType.MUTABLE)
        await manager.set("comp1", "val4", variable_type=VariableType.COMPUTED)

        # List by type
        immutable_vars = await manager.list_variables(variable_type=VariableType.IMMUTABLE)
        mutable_vars = await manager.list_variables(variable_type=VariableType.MUTABLE)

        assert len(immutable_vars) == 2
        assert len(mutable_vars) == 1


class TestConflictResolution:
    """Tests for conflict resolution strategies"""

    @pytest.mark.asyncio
    async def test_last_write_wins(self, temp_storage_path):
        """Test LAST_WRITE_WINS conflict resolution"""
        manager = StateManager(
            storage_path=temp_storage_path,
            conflict_resolution=ConflictResolution.LAST_WRITE_WINS,
        )

        var1 = await manager.set("conflict_key", "first_value", variable_type=VariableType.MUTABLE)
        var2 = await manager.set("conflict_key", "second_value")

        assert var2.value == "second_value"
        assert var2.version == var1.version + 1

    @pytest.mark.asyncio
    async def test_first_write_wins(self, temp_storage_path):
        """Test FIRST_WRITE_WINS conflict resolution"""
        manager = StateManager(
            storage_path=temp_storage_path,
            conflict_resolution=ConflictResolution.FIRST_WRITE_WINS,
        )

        var1 = await manager.set("conflict_key", "first_value", variable_type=VariableType.MUTABLE)
        var2 = await manager.set("conflict_key", "second_value")

        # First value should be kept
        assert var2.value == "first_value"
        assert var2.version == var1.version

    @pytest.mark.asyncio
    async def test_immutable_cannot_be_deleted(self, temp_storage_path):
        """Test that immutable variables cannot be deleted"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("immutable_key", "value", variable_type=VariableType.IMMUTABLE)

        with pytest.raises(ValueError, match="Cannot delete immutable variable"):
            await manager.delete("immutable_key")


class TestCaching:
    """Tests for state caching"""

    @pytest.mark.asyncio
    async def test_cache_get_miss(self, temp_storage_path):
        """Test cache miss"""
        cache = StateCache(ttl=300)

        result = await cache.get("non_existent_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, temp_storage_path):
        """Test cache set and get"""
        cache = StateCache(ttl=300)

        variable = StateVariable(
            key="cached_key",
            value="cached_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        await cache.set("cached_key", variable)
        result = await cache.get("cached_key")

        assert result is not None
        assert result.key == "cached_key"
        assert result.value == "cached_value"

    @pytest.mark.asyncio
    async def test_cache_expiration(self, temp_storage_path):
        """Test cache TTL expiration"""
        cache = StateCache(ttl=1)  # 1 second TTL

        variable = StateVariable(
            key="expiring_key",
            value="expiring_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        await cache.set("expiring_key", variable)

        # Should be cached immediately
        result1 = await cache.get("expiring_key")
        assert result1 is not None

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired
        result2 = await cache.get("expiring_key")
        assert result2 is None

    @pytest.mark.asyncio
    async def test_cache_delete(self, temp_storage_path):
        """Test cache deletion"""
        cache = StateCache(ttl=300)

        variable = StateVariable(
            key="delete_key",
            value="delete_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        await cache.set("delete_key", variable)
        await cache.delete("delete_key")

        result = await cache.get("delete_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_clear(self, temp_storage_path):
        """Test cache clear"""
        cache = StateCache(ttl=300)

        # Add multiple items
        for i in range(5):
            variable = StateVariable(
                key=f"key_{i}",
                value=f"value_{i}",
                variable_type=VariableType.MUTABLE,
                scope=VariableScope.GLOBAL,
            )
            await cache.set(f"key_{i}", variable)

        # Clear cache
        await cache.clear()

        # All items should be gone
        for i in range(5):
            result = await cache.get(f"key_{i}")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_cleanup_expired(self, temp_storage_path):
        """Test cleanup of expired entries"""
        cache = StateCache(ttl=1)

        # Add items
        for i in range(3):
            variable = StateVariable(
                key=f"exp_key_{i}",
                value=f"exp_value_{i}",
                variable_type=VariableType.MUTABLE,
                scope=VariableScope.GLOBAL,
            )
            await cache.set(f"exp_key_{i}", variable)

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Cleanup
        count = await cache.cleanup_expired()

        assert count == 3

    @pytest.mark.asyncio
    async def test_manager_uses_cache(self, temp_storage_path):
        """Test that StateManager uses cache for reads"""
        manager = StateManager(storage_path=temp_storage_path, enable_cache=True)

        # Set value
        await manager.set("cached_key", "cached_value")

        # Get value (should hit cache)
        value = await manager.get("cached_key")

        assert value == "cached_value"


class TestPersistence:
    """Tests for state persistence"""

    @pytest.mark.asyncio
    async def test_persistence_save(self, temp_storage_path):
        """Test saving variable to disk"""
        persistence = StatePersistence(temp_storage_path)

        variable = StateVariable(
            key="persist_key",
            value="persist_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        await persistence.save("persist_key", variable)

        # Check file exists
        file_path = temp_storage_path / "persist_key.json"
        assert file_path.exists()

    @pytest.mark.asyncio
    async def test_persistence_load(self, temp_storage_path):
        """Test loading variable from disk"""
        persistence = StatePersistence(temp_storage_path)

        variable = StateVariable(
            key="load_key",
            value="load_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        await persistence.save("load_key", variable)
        loaded = await persistence.load("load_key")

        assert loaded is not None
        assert loaded.key == "load_key"
        assert loaded.value == "load_value"

    @pytest.mark.asyncio
    async def test_persistence_load_missing(self, temp_storage_path):
        """Test loading non-existent variable"""
        persistence = StatePersistence(temp_storage_path)

        loaded = await persistence.load("missing_key")

        assert loaded is None

    @pytest.mark.asyncio
    async def test_persistence_delete(self, temp_storage_path):
        """Test deleting persisted variable"""
        persistence = StatePersistence(temp_storage_path)

        variable = StateVariable(
            key="delete_key",
            value="delete_value",
            variable_type=VariableType.MUTABLE,
            scope=VariableScope.GLOBAL,
        )

        await persistence.save("delete_key", variable)
        await persistence.delete("delete_key")

        file_path = temp_storage_path / "delete_key.json"
        assert not file_path.exists()

    @pytest.mark.asyncio
    async def test_persistence_list_keys(self, temp_storage_path):
        """Test listing persisted keys"""
        persistence = StatePersistence(temp_storage_path)

        # Save multiple variables
        for i in range(3):
            variable = StateVariable(
                key=f"key_{i}",
                value=f"value_{i}",
                variable_type=VariableType.MUTABLE,
                scope=VariableScope.GLOBAL,
            )
            await persistence.save(f"key_{i}", variable)

        keys = await persistence.list_keys()

        assert len(keys) == 3
        assert "key_0" in keys
        assert "key_1" in keys
        assert "key_2" in keys

    @pytest.mark.asyncio
    async def test_manager_persists_variables(self, temp_storage_path):
        """Test that StateManager persists variables"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("persist_test", "persist_value")

        # Create new manager instance
        manager2 = StateManager(storage_path=temp_storage_path)

        # Should load from disk
        value = await manager2.get("persist_test")

        assert value == "persist_value"


class TestStateSnapshots:
    """Tests for state snapshots"""

    @pytest.mark.asyncio
    async def test_create_snapshot(self, temp_storage_path):
        """Test creating state snapshot"""
        manager = StateManager(storage_path=temp_storage_path)

        # Set some variables
        await manager.set("var1", "value1")
        await manager.set("var2", "value2")

        # Create snapshot
        snapshot = await manager.create_snapshot("snapshot_1", "Test snapshot")

        assert snapshot.snapshot_id == "snapshot_1"
        assert snapshot.description == "Test snapshot"
        assert len(snapshot.variables) == 2
        assert "snapshot_1" in manager.snapshots

    @pytest.mark.asyncio
    async def test_restore_snapshot(self, temp_storage_path):
        """Test restoring state from snapshot"""
        manager = StateManager(storage_path=temp_storage_path)

        # Set initial state
        await manager.set("var1", "original1")
        await manager.set("var2", "original2")

        # Create snapshot
        await manager.create_snapshot("snapshot_1")

        # Modify state
        await manager.set("var1", "modified1")
        await manager.set("var3", "new_value")

        # Restore snapshot
        success = await manager.restore_snapshot("snapshot_1")

        assert success is True

        # Check restored state
        value1 = await manager.get("var1")
        value2 = await manager.get("var2")
        value3 = await manager.get("var3")

        assert value1 == "original1"
        assert value2 == "original2"
        assert value3 is None  # Should not exist after restore

    @pytest.mark.asyncio
    async def test_restore_nonexistent_snapshot(self, temp_storage_path):
        """Test restoring non-existent snapshot"""
        manager = StateManager(storage_path=temp_storage_path)

        success = await manager.restore_snapshot("nonexistent")

        assert success is False

    @pytest.mark.asyncio
    async def test_multiple_snapshots(self, temp_storage_path):
        """Test creating multiple snapshots"""
        manager = StateManager(storage_path=temp_storage_path)

        # State 1
        await manager.set("var1", "state1")
        await manager.create_snapshot("snap1")

        # State 2
        await manager.set("var1", "state2")
        await manager.create_snapshot("snap2")

        # State 3
        await manager.set("var1", "state3")
        await manager.create_snapshot("snap3")

        assert len(manager.snapshots) == 3

        # Restore middle snapshot
        await manager.restore_snapshot("snap2")
        value = await manager.get("var1")

        assert value == "state2"


class TestObserverPattern:
    """Tests for observer pattern"""

    @pytest.mark.asyncio
    async def test_add_observer(self, temp_storage_path):
        """Test adding state observer"""
        manager = StateManager(storage_path=temp_storage_path)

        def callback(key, new_var, old_var):
            pass

        observer = StateObserver(callback)
        manager.add_observer(observer)

        assert observer in manager.observers

    @pytest.mark.asyncio
    async def test_remove_observer(self, temp_storage_path):
        """Test removing state observer"""
        manager = StateManager(storage_path=temp_storage_path)

        def callback(key, new_var, old_var):
            pass

        observer = StateObserver(callback)
        manager.add_observer(observer)
        manager.remove_observer(observer)

        assert observer not in manager.observers

    @pytest.mark.asyncio
    async def test_observer_notified_on_set(self, temp_storage_path):
        """Test observer is notified when variable is set"""
        manager = StateManager(storage_path=temp_storage_path)

        notifications = []

        def callback(key, new_var, old_var):
            notifications.append((key, new_var.value, old_var))

        observer = StateObserver(callback)
        manager.add_observer(observer)

        await manager.set("test_key", "test_value")

        assert len(notifications) == 1
        assert notifications[0][0] == "test_key"
        assert notifications[0][1] == "test_value"
        assert notifications[0][2] is None  # No old value

    @pytest.mark.asyncio
    async def test_observer_notified_on_update(self, temp_storage_path):
        """Test observer is notified when variable is updated"""
        manager = StateManager(storage_path=temp_storage_path)

        notifications = []

        def callback(key, new_var, old_var):
            notifications.append((key, new_var.value, old_var.value if old_var else None))

        observer = StateObserver(callback)
        manager.add_observer(observer)

        await manager.set("test_key", "original_value", variable_type=VariableType.MUTABLE)
        await manager.set("test_key", "updated_value")

        assert len(notifications) == 2
        assert notifications[1][1] == "updated_value"
        assert notifications[1][2] == "original_value"

    @pytest.mark.asyncio
    async def test_observer_filter_keys(self, temp_storage_path):
        """Test observer key filtering"""
        manager = StateManager(storage_path=temp_storage_path)

        notifications = []

        def callback(key, new_var, old_var):
            notifications.append(key)

        observer = StateObserver(callback, filter_keys={"watched_key"})
        manager.add_observer(observer)

        await manager.set("watched_key", "value1")
        await manager.set("unwatched_key", "value2")

        assert len(notifications) == 1
        assert notifications[0] == "watched_key"

    @pytest.mark.asyncio
    async def test_observer_filter_scopes(self, temp_storage_path):
        """Test observer scope filtering"""
        manager = StateManager(storage_path=temp_storage_path)

        notifications = []

        def callback(key, new_var, old_var):
            notifications.append(key)

        observer = StateObserver(
            callback, filter_scopes={VariableScope.GLOBAL, VariableScope.PROJECT}
        )
        manager.add_observer(observer)

        await manager.set("global_var", "val1", scope=VariableScope.GLOBAL)
        await manager.set("project_var", "val2", scope=VariableScope.PROJECT)
        await manager.set("session_var", "val3", scope=VariableScope.SESSION)

        assert len(notifications) == 2

    @pytest.mark.asyncio
    async def test_observer_error_handling(self, temp_storage_path):
        """Test error handling in observer callback"""
        manager = StateManager(storage_path=temp_storage_path)

        def failing_callback(key, new_var, old_var):
            raise ValueError("Observer error")

        observer = StateObserver(failing_callback)
        manager.add_observer(observer)

        # Should not raise error
        await manager.set("test_key", "test_value")


class TestGetOperations:
    """Tests for get operations"""

    @pytest.mark.asyncio
    async def test_get_existing_value(self, temp_storage_path):
        """Test getting existing variable value"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("existing_key", "existing_value")
        value = await manager.get("existing_key")

        assert value == "existing_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_value(self, temp_storage_path):
        """Test getting non-existent variable"""
        manager = StateManager(storage_path=temp_storage_path)

        value = await manager.get("nonexistent_key")

        assert value is None

    @pytest.mark.asyncio
    async def test_get_with_default(self, temp_storage_path):
        """Test getting variable with default value"""
        manager = StateManager(storage_path=temp_storage_path)

        value = await manager.get("nonexistent_key", default="default_value")

        assert value == "default_value"

    @pytest.mark.asyncio
    async def test_get_variable_full(self, temp_storage_path):
        """Test getting complete StateVariable object"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("test_key", "test_value", updated_by="agent-001")
        variable = await manager.get_variable("test_key")

        assert variable is not None
        assert variable.key == "test_key"
        assert variable.value == "test_value"
        assert variable.updated_by == "agent-001"
        assert variable.version == 1

    @pytest.mark.asyncio
    async def test_get_variable_nonexistent(self, temp_storage_path):
        """Test getting non-existent StateVariable"""
        manager = StateManager(storage_path=temp_storage_path)

        variable = await manager.get_variable("nonexistent_key")

        assert variable is None


class TestDeleteOperations:
    """Tests for delete operations"""

    @pytest.mark.asyncio
    async def test_delete_existing_variable(self, temp_storage_path):
        """Test deleting existing variable"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("delete_me", "value", variable_type=VariableType.MUTABLE)
        success = await manager.delete("delete_me")

        assert success is True

        value = await manager.get("delete_me")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_variable(self, temp_storage_path):
        """Test deleting non-existent variable"""
        manager = StateManager(storage_path=temp_storage_path)

        success = await manager.delete("nonexistent")

        assert success is True  # No error, just returns True


class TestListOperations:
    """Tests for list operations"""

    @pytest.mark.asyncio
    async def test_list_all_variables(self, temp_storage_path):
        """Test listing all variables"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("var1", "value1")
        await manager.set("var2", "value2")
        await manager.set("var3", "value3")

        variables = await manager.list_variables()

        assert len(variables) == 3

    @pytest.mark.asyncio
    async def test_list_variables_with_tags(self, temp_storage_path):
        """Test listing variables filtered by tags"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("var1", "val1", tags=["tag1", "tag2"])
        await manager.set("var2", "val2", tags=["tag2", "tag3"])
        await manager.set("var3", "val3", tags=["tag3"])

        # Filter by tag1
        vars_tag1 = await manager.list_variables(tags=["tag1"])
        assert len(vars_tag1) == 1

        # Filter by tag2
        vars_tag2 = await manager.list_variables(tags=["tag2"])
        assert len(vars_tag2) == 2

    @pytest.mark.asyncio
    async def test_list_variables_combined_filters(self, temp_storage_path):
        """Test listing variables with multiple filters"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set(
            "var1",
            "val1",
            scope=VariableScope.GLOBAL,
            variable_type=VariableType.MUTABLE,
            tags=["production"],
        )
        await manager.set(
            "var2",
            "val2",
            scope=VariableScope.GLOBAL,
            variable_type=VariableType.IMMUTABLE,
            tags=["production"],
        )
        await manager.set(
            "var3",
            "val3",
            scope=VariableScope.PROJECT,
            variable_type=VariableType.MUTABLE,
            tags=["production"],
        )

        # Filter by scope, type, and tags
        filtered_vars = await manager.list_variables(
            scope=VariableScope.GLOBAL,
            variable_type=VariableType.MUTABLE,
            tags=["production"],
        )

        assert len(filtered_vars) == 1
        assert filtered_vars[0].key == "var1"


class TestConcurrency:
    """Tests for concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_set_operations(self, temp_storage_path):
        """Test concurrent set operations"""
        manager = StateManager(storage_path=temp_storage_path)

        # Set multiple variables concurrently
        tasks = [
            manager.set(f"key_{i}", f"value_{i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert len(manager.variables) == 10

    @pytest.mark.asyncio
    async def test_concurrent_get_operations(self, temp_storage_path):
        """Test concurrent get operations"""
        manager = StateManager(storage_path=temp_storage_path)

        # Set up variables
        for i in range(10):
            await manager.set(f"key_{i}", f"value_{i}")

        # Get concurrently
        tasks = [manager.get(f"key_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(results[i] == f"value_{i}" for i in range(10))

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self, temp_storage_path):
        """Test concurrent mixed operations"""
        manager = StateManager(storage_path=temp_storage_path)

        # Mix of set, get, and list operations
        tasks = []
        for i in range(5):
            tasks.append(manager.set(f"key_{i}", f"value_{i}"))
            tasks.append(manager.get(f"key_{i}", default="default"))

        results = await asyncio.gather(*tasks)

        assert len(results) == 10


class TestMetadataAndTags:
    """Tests for metadata and tag handling"""

    @pytest.mark.asyncio
    async def test_set_with_metadata(self, temp_storage_path):
        """Test setting variable with metadata"""
        manager = StateManager(storage_path=temp_storage_path)

        metadata = {
            "source": "test_agent",
            "priority": "high",
            "category": "config",
        }

        variable = await manager.set("meta_key", "meta_value", metadata=metadata)

        assert variable.metadata == metadata

    @pytest.mark.asyncio
    async def test_set_with_tags(self, temp_storage_path):
        """Test setting variable with tags"""
        manager = StateManager(storage_path=temp_storage_path)

        tags = ["production", "critical", "monitored"]

        variable = await manager.set("tag_key", "tag_value", tags=tags)

        assert variable.tags == tags

    @pytest.mark.asyncio
    async def test_update_preserves_metadata(self, temp_storage_path):
        """Test that updates preserve metadata"""
        manager = StateManager(storage_path=temp_storage_path)

        metadata = {"source": "original"}
        await manager.set("key", "val1", variable_type=VariableType.MUTABLE, metadata=metadata)
        await manager.set("key", "val2")  # Update without metadata

        variable = await manager.get_variable("key")

        assert variable.metadata == metadata


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_empty_string_value(self, temp_storage_path):
        """Test variable with empty string value"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("empty_key", "")
        value = await manager.get("empty_key")

        assert value == ""

    @pytest.mark.asyncio
    async def test_none_value(self, temp_storage_path):
        """Test variable with None value"""
        manager = StateManager(storage_path=temp_storage_path)

        await manager.set("none_key", None)
        value = await manager.get("none_key")

        assert value is None

    @pytest.mark.asyncio
    async def test_complex_nested_value(self, temp_storage_path):
        """Test variable with complex nested structure"""
        manager = StateManager(storage_path=temp_storage_path)

        complex_value = {
            "level1": {
                "level2": {
                    "level3": ["a", "b", "c"],
                    "numbers": [1, 2, 3],
                },
                "list": [{"item": 1}, {"item": 2}],
            }
        }

        await manager.set("complex_key", complex_value)
        value = await manager.get("complex_key")

        assert value == complex_value

    @pytest.mark.asyncio
    async def test_large_value(self, temp_storage_path):
        """Test variable with large value"""
        manager = StateManager(storage_path=temp_storage_path)

        large_value = "x" * 10000  # 10KB string

        await manager.set("large_key", large_value)
        value = await manager.get("large_key")

        assert len(value) == 10000

    @pytest.mark.asyncio
    async def test_special_characters_in_key(self, temp_storage_path):
        """Test variable key with special characters"""
        manager = StateManager(storage_path=temp_storage_path)

        special_key = "test_key-with.special:chars"

        await manager.set(special_key, "value")
        value = await manager.get(special_key)

        assert value == "value"
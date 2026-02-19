"""
Unit tests for BaseAgent class
Linear Project: 4d649a6501f7
Task: TEST-003 - Unit Tests for Base Agent

Tests cover:
- Agent initialization and configuration
- Agent lifecycle (startup, shutdown)
- Task creation and execution
- Message handling and routing
- Linear API integration
- Performance metrics tracking
- Error handling and retry logic
- Observer pattern
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from gql import Client

from unified_framework.agents.base_agent import (
    AgentStatus,
    BaseAgent,
    LinearConfig,
    Message,
    MessageBusConfig,
    MessagePriority,
    PerformanceMetrics,
    Task,
    TaskStatus,
)


# Fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "agents"


@pytest.fixture
def agent_config() -> Dict[str, Any]:
    """Load sample agent configuration"""
    with open(FIXTURES_DIR / "sample_agent_config.json") as f:
        return json.load(f)


@pytest.fixture
def sample_tasks() -> list[Dict[str, Any]]:
    """Load sample tasks"""
    with open(FIXTURES_DIR / "sample_tasks.json") as f:
        return json.load(f)


@pytest.fixture
def sample_messages() -> list[Dict[str, Any]]:
    """Load sample messages"""
    with open(FIXTURES_DIR / "sample_messages.json") as f:
        return json.load(f)


@pytest.fixture
def linear_config() -> LinearConfig:
    """Create Linear configuration for testing"""
    return LinearConfig(
        api_key="test_api_key_12345",
        api_url="https://api.linear.app/graphql",
        team_id="test_team_id",
        project_id="4d649a6501f7",
    )


@pytest.fixture
def message_bus_config() -> MessageBusConfig:
    """Create message bus configuration for testing"""
    return MessageBusConfig(
        redis_url="redis://localhost:6379",
        channel_prefix="test:agent",
        enable_persistence=True,
        max_retries=3,
    )


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing"""

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Simple task processor for testing"""
        # Simulate some work
        await asyncio.sleep(0.01)
        return {
            "status": "completed",
            "task_id": task.id,
            "description": task.description,
        }


class FailingAgent(BaseAgent):
    """Agent that always fails tasks for testing error handling"""

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Always raises an exception"""
        raise ValueError(f"Simulated failure for task {task.id}")


class SlowAgent(BaseAgent):
    """Agent with slow task processing for timeout testing"""

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Slow task processor"""
        await asyncio.sleep(2)
        return {"status": "completed"}


class TestAgentInitialization:
    """Tests for agent initialization"""

    def test_init_minimal_config(self):
        """Test agent initialization with minimal configuration"""
        agent = ConcreteAgent(
            agent_id="test-001",
            agent_type="TestAgent",
        )

        assert agent.agent_id == "test-001"
        assert agent.agent_type == "TestAgent"
        assert agent.status == AgentStatus.IDLE
        assert agent.linear_config is None
        assert agent.message_bus_config is not None
        assert len(agent.tasks) == 0
        assert len(agent.active_tasks) == 0
        assert agent.metrics.tasks_completed == 0

    def test_init_with_linear_config(self, linear_config: LinearConfig):
        """Test agent initialization with Linear configuration"""
        with patch("unified_framework.agents.base_agent.Client") as mock_client:
            agent = ConcreteAgent(
                agent_id="test-002",
                agent_type="TestAgent",
                linear_config=linear_config,
            )

            assert agent.linear_config == linear_config
            assert agent.linear_client is not None
            mock_client.assert_called_once()

    def test_init_with_message_bus_config(self, message_bus_config: MessageBusConfig):
        """Test agent initialization with message bus configuration"""
        agent = ConcreteAgent(
            agent_id="test-003",
            agent_type="TestAgent",
            message_bus_config=message_bus_config,
        )

        assert agent.message_bus_config == message_bus_config
        assert agent.message_bus_config.redis_url == "redis://localhost:6379"
        assert agent.message_bus_config.channel_prefix == "test:agent"

    def test_init_with_full_config(
        self, linear_config: LinearConfig, message_bus_config: MessageBusConfig
    ):
        """Test agent initialization with full configuration"""
        with patch("unified_framework.agents.base_agent.Client"):
            agent = ConcreteAgent(
                agent_id="test-004",
                agent_type="TestAgent",
                linear_config=linear_config,
                message_bus_config=message_bus_config,
            )

            assert agent.agent_id == "test-004"
            assert agent.linear_config is not None
            assert agent.message_bus_config is not None
            assert agent.status == AgentStatus.IDLE


class TestAgentLifecycle:
    """Tests for agent lifecycle management"""

    @pytest.mark.asyncio
    async def test_start_agent(self):
        """Test starting an agent"""
        agent = ConcreteAgent(agent_id="test-005", agent_type="TestAgent")

        await agent.start()

        assert agent.status == AgentStatus.ACTIVE
        assert agent._running is True

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_stop_agent(self):
        """Test stopping an agent"""
        agent = ConcreteAgent(agent_id="test-006", agent_type="TestAgent")

        await agent.start()
        assert agent._running is True

        await agent.stop()

        assert agent.status == AgentStatus.OFFLINE
        assert agent._running is False

    @pytest.mark.asyncio
    async def test_on_start_hook(self):
        """Test on_start hook is called during startup"""

        class HookedAgent(ConcreteAgent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.start_called = False

            async def on_start(self):
                self.start_called = True

        agent = HookedAgent(agent_id="test-007", agent_type="HookedAgent")

        await agent.start()

        assert agent.start_called is True

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_on_stop_hook(self):
        """Test on_stop hook is called during shutdown"""

        class HookedAgent(ConcreteAgent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.stop_called = False

            async def on_stop(self):
                self.stop_called = True

        agent = HookedAgent(agent_id="test-008", agent_type="HookedAgent")

        await agent.start()
        await agent.stop()

        assert agent.stop_called is True


class TestTaskManagement:
    """Tests for task creation and management"""

    @pytest.mark.asyncio
    async def test_create_task_minimal(self):
        """Test creating a task with minimal parameters"""
        agent = ConcreteAgent(agent_id="test-009", agent_type="TestAgent")

        task = await agent.create_task(description="Test task")

        assert task.id is not None
        assert task.agent_id == "test-009"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == MessagePriority.NORMAL
        assert task.id in agent.tasks

    @pytest.mark.asyncio
    async def test_create_task_with_priority(self):
        """Test creating a task with specific priority"""
        agent = ConcreteAgent(agent_id="test-010", agent_type="TestAgent")

        task = await agent.create_task(
            description="Urgent task", priority=MessagePriority.URGENT
        )

        assert task.priority == MessagePriority.URGENT

    @pytest.mark.asyncio
    async def test_create_task_with_metadata(self):
        """Test creating a task with metadata"""
        agent = ConcreteAgent(agent_id="test-011", agent_type="TestAgent")

        metadata = {"component": "auth", "estimated_hours": 4}
        task = await agent.create_task(description="Test task", metadata=metadata)

        assert task.metadata == metadata

    @pytest.mark.asyncio
    async def test_create_task_with_linear_issue(self):
        """Test creating a task linked to Linear issue"""
        agent = ConcreteAgent(agent_id="test-012", agent_type="TestAgent")

        task = await agent.create_task(
            description="Test task", linear_issue_id="PEG-123"
        )

        assert task.linear_issue_id == "PEG-123"

    @pytest.mark.asyncio
    async def test_create_multiple_tasks(self):
        """Test creating multiple tasks"""
        agent = ConcreteAgent(agent_id="test-013", agent_type="TestAgent")

        task1 = await agent.create_task(description="Task 1")
        task2 = await agent.create_task(description="Task 2")
        task3 = await agent.create_task(description="Task 3")

        assert len(agent.tasks) == 3
        assert task1.id != task2.id != task3.id


class TestTaskExecution:
    """Tests for task execution"""

    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test successful task execution"""
        agent = ConcreteAgent(agent_id="test-014", agent_type="TestAgent")

        task = await agent.create_task(description="Test task")
        completed_task = await agent.execute_task(task.id)

        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.result is not None
        assert completed_task.error is None
        assert completed_task.started_at is not None
        assert completed_task.completed_at is not None
        assert agent.metrics.tasks_completed == 1
        assert agent.metrics.tasks_failed == 0

    @pytest.mark.asyncio
    async def test_execute_task_failure(self):
        """Test task execution with failure"""
        agent = FailingAgent(agent_id="test-015", agent_type="FailingAgent")

        task = await agent.create_task(description="Failing task")
        failed_task = await agent.execute_task(task.id)

        assert failed_task.status == TaskStatus.FAILED
        assert failed_task.error is not None
        assert "Simulated failure" in failed_task.error
        assert agent.metrics.tasks_completed == 0
        assert agent.metrics.tasks_failed == 1

    @pytest.mark.asyncio
    async def test_execute_task_not_found(self):
        """Test executing non-existent task raises error"""
        agent = ConcreteAgent(agent_id="test-016", agent_type="TestAgent")

        with pytest.raises(ValueError, match="Task .* not found"):
            await agent.execute_task("non-existent-task-id")

    @pytest.mark.asyncio
    async def test_execute_task_status_transitions(self):
        """Test task status transitions during execution"""
        agent = ConcreteAgent(agent_id="test-017", agent_type="TestAgent")

        task = await agent.create_task(description="Test task")

        # Initial state
        assert task.status == TaskStatus.PENDING
        assert task.id not in agent.active_tasks

        # Execute task
        completed_task = await agent.execute_task(task.id)

        # Final state
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.id not in agent.active_tasks

    @pytest.mark.asyncio
    async def test_execute_task_agent_status(self):
        """Test agent status changes during task execution"""
        agent = ConcreteAgent(agent_id="test-018", agent_type="TestAgent")

        await agent.start()
        initial_status = agent.status

        task = await agent.create_task(description="Test task")
        await agent.execute_task(task.id)

        # After task completion, status should return to ACTIVE or IDLE
        assert agent.status in [AgentStatus.ACTIVE, AgentStatus.IDLE]

        # Cleanup
        await agent.stop()


class TestPerformanceMetrics:
    """Tests for performance metrics tracking"""

    @pytest.mark.asyncio
    async def test_metrics_initialization(self):
        """Test metrics are initialized correctly"""
        agent = ConcreteAgent(agent_id="test-019", agent_type="TestAgent")

        metrics = agent.get_metrics()

        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.total_execution_time == 0.0
        assert metrics.average_execution_time == 0.0
        assert metrics.messages_sent == 0
        assert metrics.messages_received == 0
        assert metrics.errors_encountered == 0

    @pytest.mark.asyncio
    async def test_metrics_task_completion(self):
        """Test metrics update on task completion"""
        agent = ConcreteAgent(agent_id="test-020", agent_type="TestAgent")

        task = await agent.create_task(description="Test task")
        await agent.execute_task(task.id)

        metrics = agent.get_metrics()

        assert metrics.tasks_completed == 1
        assert metrics.total_execution_time > 0
        assert metrics.average_execution_time > 0
        assert metrics.last_active is not None

    @pytest.mark.asyncio
    async def test_metrics_task_failure(self):
        """Test metrics update on task failure"""
        agent = FailingAgent(agent_id="test-021", agent_type="FailingAgent")

        task = await agent.create_task(description="Failing task")
        await agent.execute_task(task.id)

        metrics = agent.get_metrics()

        assert metrics.tasks_failed == 1
        assert metrics.errors_encountered == 1

    @pytest.mark.asyncio
    async def test_metrics_average_execution_time(self):
        """Test average execution time calculation"""
        agent = ConcreteAgent(agent_id="test-022", agent_type="TestAgent")

        # Execute multiple tasks
        for i in range(3):
            task = await agent.create_task(description=f"Task {i}")
            await agent.execute_task(task.id)

        metrics = agent.get_metrics()

        assert metrics.tasks_completed == 3
        assert metrics.average_execution_time > 0
        assert metrics.average_execution_time == (
            metrics.total_execution_time / metrics.tasks_completed
        )

    @pytest.mark.asyncio
    async def test_metrics_message_tracking(self):
        """Test message count tracking"""
        agent = ConcreteAgent(agent_id="test-023", agent_type="TestAgent")

        await agent.start()

        # Send messages
        await agent.send_message("agent-002", "test_message", {"data": "test"})
        await agent.send_message(None, "broadcast", {"data": "broadcast"})

        metrics = agent.get_metrics()

        assert metrics.messages_sent == 2

        # Cleanup
        await agent.stop()


class TestMessageHandling:
    """Tests for message handling and routing"""

    @pytest.mark.asyncio
    async def test_send_message_direct(self):
        """Test sending direct message to another agent"""
        agent = ConcreteAgent(agent_id="test-024", agent_type="TestAgent")

        message_id = await agent.send_message(
            receiver_id="agent-002",
            message_type="task_assignment",
            payload={"task_id": "123"},
        )

        assert message_id is not None
        assert agent.metrics.messages_sent == 1

    @pytest.mark.asyncio
    async def test_send_message_broadcast(self):
        """Test sending broadcast message"""
        agent = ConcreteAgent(agent_id="test-025", agent_type="TestAgent")

        message_id = await agent.send_message(
            receiver_id=None, message_type="status_update", payload={"status": "active"}
        )

        assert message_id is not None
        assert agent.metrics.messages_sent == 1

    @pytest.mark.asyncio
    async def test_send_message_with_priority(self):
        """Test sending message with specific priority"""
        agent = ConcreteAgent(agent_id="test-026", agent_type="TestAgent")

        message_id = await agent.send_message(
            receiver_id="agent-002",
            message_type="urgent_task",
            payload={"task_id": "456"},
            priority=MessagePriority.URGENT,
        )

        assert message_id is not None

    @pytest.mark.asyncio
    async def test_register_message_handler(self):
        """Test registering message handler"""
        agent = ConcreteAgent(agent_id="test-027", agent_type="TestAgent")

        handler_called = False

        async def test_handler(message: Message):
            nonlocal handler_called
            handler_called = True

        agent.register_handler("test_message", test_handler)

        assert "test_message" in agent.message_handlers

    @pytest.mark.asyncio
    async def test_message_handler_execution(self):
        """Test message handler is called when message is received"""
        agent = ConcreteAgent(agent_id="test-028", agent_type="TestAgent")

        received_messages = []

        async def test_handler(message: Message):
            received_messages.append(message)

        agent.register_handler("test_message", test_handler)

        await agent.start()

        # Create and queue a message
        message = Message(
            sender_id="agent-002",
            receiver_id=agent.agent_id,
            message_type="test_message",
            payload={"data": "test"},
        )

        await agent.message_queue.put(message)

        # Wait for message processing
        await asyncio.sleep(0.1)

        assert len(received_messages) == 1
        assert received_messages[0].sender_id == "agent-002"

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_message_handler_not_found(self):
        """Test handling message with no registered handler"""
        agent = ConcreteAgent(agent_id="test-029", agent_type="TestAgent")

        await agent.start()

        # Create message with unregistered type
        message = Message(
            sender_id="agent-002",
            receiver_id=agent.agent_id,
            message_type="unknown_message",
            payload={"data": "test"},
        )

        await agent.message_queue.put(message)

        # Wait for message processing
        await asyncio.sleep(0.1)

        # Should not raise error, just log warning
        assert agent.metrics.messages_received == 1

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_message_handler_error(self):
        """Test error handling in message handler"""
        agent = ConcreteAgent(agent_id="test-030", agent_type="TestAgent")

        async def failing_handler(message: Message):
            raise ValueError("Handler error")

        agent.register_handler("failing_message", failing_handler)

        await agent.start()

        message = Message(
            sender_id="agent-002",
            receiver_id=agent.agent_id,
            message_type="failing_message",
            payload={"data": "test"},
        )

        await agent.message_queue.put(message)

        # Wait for message processing
        await asyncio.sleep(0.1)

        # Error should be caught and counted
        assert agent.metrics.errors_encountered == 1

        # Cleanup
        await agent.stop()


class TestLinearIntegration:
    """Tests for Linear API integration"""

    @pytest.mark.asyncio
    async def test_create_linear_issue_without_client(self):
        """Test creating Linear issue without configured client"""
        agent = ConcreteAgent(agent_id="test-031", agent_type="TestAgent")

        issue_id = await agent.create_linear_issue(
            title="Test Issue", description="Test description"
        )

        assert issue_id is None

    @pytest.mark.asyncio
    async def test_create_linear_issue_success(self, linear_config: LinearConfig):
        """Test successful Linear issue creation"""
        with patch("unified_framework.agents.base_agent.Client") as mock_client_class:
            # Mock the GraphQL client
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                return_value={
                    "issueCreate": {"issue": {"id": "issue-123", "identifier": "PEG-123"}}
                }
            )

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            agent = ConcreteAgent(
                agent_id="test-032",
                agent_type="TestAgent",
                linear_config=linear_config,
            )
            agent.linear_client = mock_client

            issue_id = await agent.create_linear_issue(
                title="Test Issue", description="Test description", priority=2
            )

            assert issue_id == "PEG-123"
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_linear_issue_with_labels(self, linear_config: LinearConfig):
        """Test creating Linear issue with labels"""
        with patch("unified_framework.agents.base_agent.Client") as mock_client_class:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                return_value={
                    "issueCreate": {"issue": {"id": "issue-124", "identifier": "PEG-124"}}
                }
            )

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            agent = ConcreteAgent(
                agent_id="test-033",
                agent_type="TestAgent",
                linear_config=linear_config,
            )
            agent.linear_client = mock_client

            issue_id = await agent.create_linear_issue(
                title="Test Issue",
                description="Test description",
                labels=["bug", "urgent"],
            )

            assert issue_id == "PEG-124"

    @pytest.mark.asyncio
    async def test_create_linear_issue_error(self, linear_config: LinearConfig):
        """Test error handling in Linear issue creation"""
        with patch("unified_framework.agents.base_agent.Client"):
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=Exception("API Error"))

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            agent = ConcreteAgent(
                agent_id="test-034",
                agent_type="TestAgent",
                linear_config=linear_config,
            )
            agent.linear_client = mock_client

            issue_id = await agent.create_linear_issue(
                title="Test Issue", description="Test description"
            )

            assert issue_id is None

    @pytest.mark.asyncio
    async def test_update_linear_issue_success(self, linear_config: LinearConfig):
        """Test successful Linear issue update"""
        with patch("unified_framework.agents.base_agent.Client"):
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                return_value={"issueUpdate": {"issue": {"id": "issue-123"}}}
            )

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            agent = ConcreteAgent(
                agent_id="test-035",
                agent_type="TestAgent",
                linear_config=linear_config,
            )
            agent.linear_client = mock_client

            success = await agent.update_linear_issue(
                issue_id="PEG-123", state="completed"
            )

            assert success is True

    @pytest.mark.asyncio
    async def test_update_linear_issue_with_comment(self, linear_config: LinearConfig):
        """Test updating Linear issue with comment"""
        with patch("unified_framework.agents.base_agent.Client"):
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                return_value={"commentCreate": {"comment": {"id": "comment-123"}}}
            )

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            agent = ConcreteAgent(
                agent_id="test-036",
                agent_type="TestAgent",
                linear_config=linear_config,
            )
            agent.linear_client = mock_client

            success = await agent.update_linear_issue(
                issue_id="PEG-123", comment="Task completed successfully"
            )

            assert success is True

    @pytest.mark.asyncio
    async def test_update_linear_issue_error(self, linear_config: LinearConfig):
        """Test error handling in Linear issue update"""
        with patch("unified_framework.agents.base_agent.Client"):
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=Exception("API Error"))

            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            agent = ConcreteAgent(
                agent_id="test-037",
                agent_type="TestAgent",
                linear_config=linear_config,
            )
            agent.linear_client = mock_client

            success = await agent.update_linear_issue(
                issue_id="PEG-123", state="completed"
            )

            assert success is False


class TestAgentStatus:
    """Tests for agent status management"""

    @pytest.mark.asyncio
    async def test_get_status_idle(self):
        """Test getting status of idle agent"""
        agent = ConcreteAgent(agent_id="test-038", agent_type="TestAgent")

        status = agent.get_status()

        assert status["agent_id"] == "test-038"
        assert status["agent_type"] == "TestAgent"
        assert status["status"] == AgentStatus.IDLE.value
        assert status["active_tasks"] == 0
        assert status["total_tasks"] == 0

    @pytest.mark.asyncio
    async def test_get_status_active(self):
        """Test getting status of active agent"""
        agent = ConcreteAgent(agent_id="test-039", agent_type="TestAgent")

        await agent.start()

        status = agent.get_status()

        assert status["status"] == AgentStatus.ACTIVE.value

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_get_status_with_tasks(self):
        """Test getting status with tasks"""
        agent = ConcreteAgent(agent_id="test-040", agent_type="TestAgent")

        task1 = await agent.create_task(description="Task 1")
        task2 = await agent.create_task(description="Task 2")

        status = agent.get_status()

        assert status["total_tasks"] == 2
        assert status["active_tasks"] == 0

    @pytest.mark.asyncio
    async def test_get_status_includes_metrics(self):
        """Test status includes performance metrics"""
        agent = ConcreteAgent(agent_id="test-041", agent_type="TestAgent")

        task = await agent.create_task(description="Test task")
        await agent.execute_task(task.id)

        status = agent.get_status()

        assert "metrics" in status
        assert status["metrics"]["tasks_completed"] == 1


class TestErrorHandling:
    """Tests for error handling and recovery"""

    @pytest.mark.asyncio
    async def test_task_execution_error_caught(self):
        """Test errors during task execution are caught"""
        agent = FailingAgent(agent_id="test-042", agent_type="FailingAgent")

        task = await agent.create_task(description="Failing task")
        result = await agent.execute_task(task.id)

        assert result.status == TaskStatus.FAILED
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_message_processing_error_caught(self):
        """Test errors during message processing are caught"""
        agent = ConcreteAgent(agent_id="test-043", agent_type="TestAgent")

        async def error_handler(message: Message):
            raise RuntimeError("Handler error")

        agent.register_handler("error_type", error_handler)

        await agent.start()

        message = Message(
            sender_id="agent-002",
            receiver_id=agent.agent_id,
            message_type="error_type",
            payload={},
        )

        await agent.message_queue.put(message)
        await asyncio.sleep(0.1)

        # Error should be logged but not crash the agent
        assert agent._running is True
        assert agent.metrics.errors_encountered > 0

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_metrics_error_count(self):
        """Test error count in metrics"""
        agent = FailingAgent(agent_id="test-044", agent_type="FailingAgent")

        # Execute multiple failing tasks
        for i in range(3):
            task = await agent.create_task(description=f"Failing task {i}")
            await agent.execute_task(task.id)

        metrics = agent.get_metrics()

        assert metrics.tasks_failed == 3
        assert metrics.errors_encountered == 3


class TestConcurrency:
    """Tests for concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_task_creation(self):
        """Test creating tasks concurrently"""
        agent = ConcreteAgent(agent_id="test-045", agent_type="TestAgent")

        tasks = await asyncio.gather(
            agent.create_task(description="Task 1"),
            agent.create_task(description="Task 2"),
            agent.create_task(description="Task 3"),
            agent.create_task(description="Task 4"),
            agent.create_task(description="Task 5"),
        )

        assert len(tasks) == 5
        assert len(agent.tasks) == 5
        # All tasks should have unique IDs
        task_ids = {task.id for task in tasks}
        assert len(task_ids) == 5

    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test executing tasks concurrently"""
        agent = ConcreteAgent(agent_id="test-046", agent_type="TestAgent")

        # Create tasks
        tasks = []
        for i in range(5):
            task = await agent.create_task(description=f"Task {i}")
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(
            *[agent.execute_task(task.id) for task in tasks]
        )

        assert len(results) == 5
        assert all(r.status == TaskStatus.COMPLETED for r in results)
        assert agent.metrics.tasks_completed == 5

    @pytest.mark.asyncio
    async def test_concurrent_message_processing(self):
        """Test processing multiple messages concurrently"""
        agent = ConcreteAgent(agent_id="test-047", agent_type="TestAgent")

        received_count = 0

        async def counter_handler(message: Message):
            nonlocal received_count
            received_count += 1

        agent.register_handler("count_message", counter_handler)

        await agent.start()

        # Queue multiple messages
        for i in range(10):
            message = Message(
                sender_id=f"agent-{i:03d}",
                receiver_id=agent.agent_id,
                message_type="count_message",
                payload={"index": i},
            )
            await agent.message_queue.put(message)

        # Wait for processing
        await asyncio.sleep(0.2)

        assert received_count == 10
        assert agent.metrics.messages_received == 10

        # Cleanup
        await agent.stop()


class TestDataModels:
    """Tests for data model validation and behavior"""

    def test_message_model_creation(self):
        """Test Message model creation"""
        message = Message(
            sender_id="agent-001",
            receiver_id="agent-002",
            message_type="test",
            payload={"data": "test"},
        )

        assert message.id is not None
        assert message.sender_id == "agent-001"
        assert message.receiver_id == "agent-002"
        assert message.priority == MessagePriority.NORMAL
        assert message.timestamp is not None

    def test_message_model_broadcast(self):
        """Test Message model for broadcast"""
        message = Message(
            sender_id="agent-001",
            receiver_id=None,  # Broadcast
            message_type="broadcast",
            payload={"data": "broadcast"},
        )

        assert message.receiver_id is None

    def test_task_model_creation(self):
        """Test Task model creation"""
        task = Task(agent_id="agent-001", description="Test task")

        assert task.id is not None
        assert task.agent_id == "agent-001"
        assert task.status == TaskStatus.PENDING
        assert task.priority == MessagePriority.NORMAL
        assert task.created_at is not None

    def test_performance_metrics_model(self):
        """Test PerformanceMetrics model"""
        metrics = PerformanceMetrics()

        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.total_execution_time == 0.0

    def test_linear_config_model(self):
        """Test LinearConfig model"""
        config = LinearConfig(api_key="test_key", project_id="4d649a6501f7")

        assert config.api_key == "test_key"
        assert config.api_url == "https://api.linear.app/graphql"
        assert config.project_id == "4d649a6501f7"

    def test_message_bus_config_model(self):
        """Test MessageBusConfig model"""
        config = MessageBusConfig()

        assert config.redis_url == "redis://localhost:6379"
        assert config.channel_prefix == "idfwu:agent"
        assert config.enable_persistence is True
        assert config.max_retries == 3


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_execute_task_immediately_after_creation(self):
        """Test executing task immediately after creation"""
        agent = ConcreteAgent(agent_id="test-048", agent_type="TestAgent")

        task = await agent.create_task(description="Immediate task")
        result = await agent.execute_task(task.id)

        assert result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_stop_agent_with_active_tasks(self):
        """Test stopping agent while tasks are active"""
        agent = SlowAgent(agent_id="test-049", agent_type="SlowAgent")

        await agent.start()

        task = await agent.create_task(description="Slow task")

        # Start task execution (don't await)
        task_coro = agent.execute_task(task.id)

        # Stop agent immediately
        await agent.stop()

        assert agent.status == AgentStatus.OFFLINE
        assert agent._running is False

    @pytest.mark.asyncio
    async def test_empty_message_queue(self):
        """Test agent behavior with empty message queue"""
        agent = ConcreteAgent(agent_id="test-050", agent_type="TestAgent")

        await agent.start()

        # Let it run with no messages
        await asyncio.sleep(0.2)

        assert agent.metrics.messages_received == 0

        # Cleanup
        await agent.stop()

    @pytest.mark.asyncio
    async def test_task_with_empty_metadata(self):
        """Test task creation with empty metadata"""
        agent = ConcreteAgent(agent_id="test-051", agent_type="TestAgent")

        task = await agent.create_task(description="Task", metadata={})

        assert task.metadata == {}

    @pytest.mark.asyncio
    async def test_message_with_empty_payload(self):
        """Test message with empty payload"""
        agent = ConcreteAgent(agent_id="test-052", agent_type="TestAgent")

        message_id = await agent.send_message(
            receiver_id="agent-002", message_type="empty", payload={}
        )

        assert message_id is not None
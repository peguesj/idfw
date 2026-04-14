"""
Base Agent Class for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides the foundational BaseAgent class that all specialized agents inherit from.
Includes message bus integration, Linear API integration, task handling, and performance monitoring.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Awaitable

from pydantic import BaseModel, Field, ConfigDict
import httpx
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

try:
    from services.apm_client import register_agent as apm_register, heartbeat as apm_heartbeat
except ImportError:
    apm_register = None
    apm_heartbeat = None


# Configure logging
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentStatus(str, Enum):
    """Agent operational status"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class Message(BaseModel):
    """Message structure for agent communication"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: Optional[str] = None  # None for broadcast
    message_type: str
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None


class Task(BaseModel):
    """Task structure for agent work items"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: MessagePriority = MessagePriority.NORMAL
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    linear_issue_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PerformanceMetrics(BaseModel):
    """Performance tracking metrics"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    messages_sent: int = 0
    messages_received: int = 0
    errors_encountered: int = 0
    last_active: Optional[datetime] = None


class LinearConfig(BaseModel):
    """Linear API configuration"""
    api_key: str
    api_url: str = "https://api.linear.app/graphql"
    team_id: Optional[str] = None
    project_id: str = "4d649a6501f7"  # IDFWU project ID


class MessageBusConfig(BaseModel):
    """Message bus configuration"""
    redis_url: Optional[str] = "redis://localhost:6379"
    channel_prefix: str = "idfwu:agent"
    enable_persistence: bool = True
    max_retries: int = 3


class BaseAgent(ABC):
    """
    Base class for all IDFWU agents.

    Provides:
    - Message bus integration for inter-agent communication
    - Linear API integration for issue tracking
    - Task lifecycle management
    - Performance monitoring
    - Error handling and retry logic
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        linear_config: Optional[LinearConfig] = None,
        message_bus_config: Optional[MessageBusConfig] = None,
    ) -> None:
        """
        Initialize base agent.

        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type/class of agent (e.g., "BackendDeveloperAgent")
            linear_config: Configuration for Linear API integration
            message_bus_config: Configuration for message bus
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE

        # Configuration
        self.linear_config = linear_config
        self.message_bus_config = message_bus_config or MessageBusConfig()

        # State management
        self.tasks: Dict[str, Task] = {}
        self.active_tasks: Set[str] = set()
        self.message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self.metrics = PerformanceMetrics()

        # Handlers
        self.message_handlers: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self._running = False

        # Linear API client
        self.linear_client: Optional[Client] = None
        if linear_config:
            self._init_linear_client()

        logger.info(f"Initialized {agent_type} with ID: {agent_id}")

        # Register with CCEM APM (fire-and-forget)
        if apm_register:
            apm_register(agent_id, "idfw", agent_type, "idle")

    def _init_linear_client(self) -> None:
        """Initialize Linear GraphQL client"""
        if not self.linear_config:
            return

        transport = AIOHTTPTransport(
            url=self.linear_config.api_url,
            headers={"Authorization": self.linear_config.api_key}
        )
        self.linear_client = Client(transport=transport, fetch_schema_from_transport=True)

    async def start(self) -> None:
        """Start the agent and begin processing messages"""
        self._running = True
        self.status = AgentStatus.ACTIVE
        logger.info(f"Starting agent {self.agent_id}")

        # Start message processing loop
        asyncio.create_task(self._process_messages())

        # Call agent-specific startup
        await self.on_start()

    async def stop(self) -> None:
        """Stop the agent and cleanup resources"""
        self._running = False
        self.status = AgentStatus.OFFLINE
        logger.info(f"Stopping agent {self.agent_id}")

        # Call agent-specific cleanup
        await self.on_stop()

    async def on_start(self) -> None:
        """Hook for agent-specific startup logic"""
        pass

    async def on_stop(self) -> None:
        """Hook for agent-specific cleanup logic"""
        pass

    async def _process_messages(self) -> None:
        """Main message processing loop"""
        while self._running:
            try:
                # Get message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                self.metrics.messages_received += 1
                await self._handle_message(message)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                self.metrics.errors_encountered += 1

    async def _handle_message(self, message: Message) -> None:
        """
        Route message to appropriate handler

        Args:
            message: Message to handle
        """
        handler = self.message_handlers.get(message.message_type)

        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error in message handler {message.message_type}: {e}")
                self.metrics.errors_encountered += 1
        else:
            logger.warning(f"No handler for message type: {message.message_type}")

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[Message], Awaitable[None]]
    ) -> None:
        """
        Register a message handler

        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")

    async def send_message(
        self,
        receiver_id: Optional[str],
        message_type: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Send a message to another agent or broadcast

        Args:
            receiver_id: Target agent ID (None for broadcast)
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            correlation_id: Optional correlation ID for tracking

        Returns:
            Message ID
        """
        message = Message(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id,
        )

        # In production, this would publish to Redis or similar
        # For now, we'll just log it
        logger.debug(f"Sending message {message.id}: {message_type} to {receiver_id or 'broadcast'}")
        self.metrics.messages_sent += 1

        return message.id

    async def create_task(
        self,
        description: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        linear_issue_id: Optional[str] = None,
    ) -> Task:
        """
        Create a new task for this agent

        Args:
            description: Task description
            priority: Task priority
            metadata: Additional metadata
            linear_issue_id: Associated Linear issue ID

        Returns:
            Created task
        """
        task = Task(
            agent_id=self.agent_id,
            description=description,
            priority=priority,
            metadata=metadata or {},
            linear_issue_id=linear_issue_id,
        )

        self.tasks[task.id] = task
        logger.info(f"Created task {task.id}: {description}")

        return task

    async def execute_task(self, task_id: str) -> Task:
        """
        Execute a task

        Args:
            task_id: ID of task to execute

        Returns:
            Completed task

        Raises:
            ValueError: If task not found
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        self.status = AgentStatus.BUSY
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.active_tasks.add(task_id)

        start_time = time.time()

        try:
            # Execute agent-specific task logic
            result = await self.process_task(task)

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()

            self.metrics.tasks_completed += 1

            logger.info(f"Completed task {task_id}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()

            self.metrics.tasks_failed += 1
            self.metrics.errors_encountered += 1

            logger.error(f"Task {task_id} failed: {e}")

        finally:
            execution_time = time.time() - start_time
            self.metrics.total_execution_time += execution_time

            if self.metrics.tasks_completed > 0:
                self.metrics.average_execution_time = (
                    self.metrics.total_execution_time / self.metrics.tasks_completed
                )

            self.active_tasks.remove(task_id)
            self.status = AgentStatus.ACTIVE if self.active_tasks else AgentStatus.IDLE
            self.metrics.last_active = datetime.utcnow()

            # Send heartbeat to CCEM APM on task completion
            if apm_heartbeat:
                apm_heartbeat(self.agent_id, self.status.value, f"Task {task_id}: {task.status.value}")

        return task

    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Process a task - must be implemented by subclasses

        Args:
            task: Task to process

        Returns:
            Task result
        """
        pass

    async def create_linear_issue(
        self,
        title: str,
        description: str,
        priority: int = 2,
        labels: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Create a Linear issue

        Args:
            title: Issue title
            description: Issue description
            priority: Priority (0=No priority, 1=Urgent, 2=High, 3=Normal, 4=Low)
            labels: Optional labels

        Returns:
            Created issue ID or None if failed
        """
        if not self.linear_client or not self.linear_config:
            logger.warning("Linear client not configured")
            return None

        mutation = gql("""
            mutation CreateIssue($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    issue {
                        id
                        identifier
                    }
                }
            }
        """)

        variables = {
            "input": {
                "title": title,
                "description": description,
                "priority": priority,
                "projectId": self.linear_config.project_id,
                "labelIds": labels or [],
            }
        }

        try:
            async with self.linear_client as session:
                result = await session.execute(mutation, variable_values=variables)
                issue_id = result["issueCreate"]["issue"]["identifier"]
                logger.info(f"Created Linear issue: {issue_id}")
                return issue_id
        except Exception as e:
            logger.error(f"Failed to create Linear issue: {e}")
            return None

    async def update_linear_issue(
        self,
        issue_id: str,
        state: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> bool:
        """
        Update a Linear issue

        Args:
            issue_id: Issue ID
            state: Optional new state
            comment: Optional comment to add

        Returns:
            True if successful
        """
        if not self.linear_client:
            logger.warning("Linear client not configured")
            return False

        try:
            if state:
                mutation = gql("""
                    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
                        issueUpdate(id: $id, input: $input) {
                            issue {
                                id
                            }
                        }
                    }
                """)

                variables = {
                    "id": issue_id,
                    "input": {"stateId": state}
                }

                async with self.linear_client as session:
                    await session.execute(mutation, variable_values=variables)

            if comment:
                mutation = gql("""
                    mutation CreateComment($input: CommentCreateInput!) {
                        commentCreate(input: $input) {
                            comment {
                                id
                            }
                        }
                    }
                """)

                variables = {
                    "input": {
                        "issueId": issue_id,
                        "body": comment,
                    }
                }

                async with self.linear_client as session:
                    await session.execute(mutation, variable_values=variables)

            logger.info(f"Updated Linear issue: {issue_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update Linear issue: {e}")
            return False

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status

        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "active_tasks": len(self.active_tasks),
            "total_tasks": len(self.tasks),
            "metrics": self.metrics.dict(),
        }
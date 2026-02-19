"""
IDFWU Base Agent Implementation
Integrated Development Framework for Web Unification

This module provides the base agent class and common functionality for all
IDFWU agents, including message bus integration, Linear integration, task
handling, and performance monitoring.

Project: IDFWU (Linear ID: 4d649a6501f7)
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from urllib.parse import urljoin

import aiohttp
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator


class AgentStatus(Enum):
    """Agent operational status enumeration."""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    BLOCKED = "blocked"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class TaskStatus(Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AgentCapability:
    """Represents an agent capability or skill."""
    name: str
    description: str
    expertise_level: float  # 0.0 to 1.0
    task_types: List[str]
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Task:
    """Represents a task assigned to an agent."""
    id: str
    type: str
    description: str
    priority: Priority
    created_at: datetime
    deadline: Optional[datetime] = None
    assignee: Optional[str] = None
    parent_task: Optional[str] = None
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentMetrics:
    """Agent performance metrics."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_response_time: float = 0.0
    uptime_hours: float = 0.0
    success_rate: float = 0.0
    last_activity: Optional[datetime] = None


class LinearIssue(BaseModel):
    """Linear issue model for API integration."""
    title: str
    description: str
    labels: List[str] = Field(default_factory=list)
    priority: Optional[str] = None
    project_id: str = "4d649a6501f7"  # IDFWU project ID
    parent_id: Optional[str] = None
    assignee_id: Optional[str] = None

    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['urgent', 'high', 'medium', 'low']:
            raise ValueError('Priority must be urgent, high, medium, or low')
        return v


class MessageBusMessage(BaseModel):
    """Message bus message format."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: Optional[str] = None
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all IDFWU agents providing common functionality:
    - Message bus communication
    - Linear API integration
    - Task management
    - Performance monitoring
    - Error handling and recovery
    """

    def __init__(
        self,
        agent_id: str,
        department: str,
        capabilities: List[AgentCapability],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the base agent.

        Args:
            agent_id: Unique identifier for the agent
            department: Department the agent belongs to
            capabilities: List of agent capabilities
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.department = department
        self.capabilities = {cap.name: cap for cap in capabilities}
        self.config = config or {}

        # Agent state
        self.status = AgentStatus.OFFLINE
        self.current_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[str] = []
        self.metrics = AgentMetrics()
        self.start_time = datetime.now(timezone.utc)

        # Communication
        self.message_handlers: Dict[str, Callable] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None

        # Configuration
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 3)
        self.linear_api_key = self.config.get('linear_api_key')
        self.linear_project_id = self.config.get('linear_project_id', '4d649a6501f7')
        self.redis_url = self.config.get('redis_url', 'redis://localhost:6379')

        # Logging
        self.logger = logging.getLogger(f'agent.{self.agent_id}')
        self.logger.setLevel(logging.INFO)

    async def initialize(self) -> None:
        """Initialize agent connections and state."""
        try:
            # Initialize Redis connection for message bus
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()

            # Initialize HTTP session
            self.session = aiohttp.ClientSession()

            # Register message handlers
            await self._register_message_handlers()

            # Update status
            self.status = AgentStatus.IDLE
            await self._publish_status_update()

            self.logger.info(f"Agent {self.agent_id} initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            self.status = AgentStatus.FAILED
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        try:
            # Cancel running tasks
            for task_id in list(self.current_tasks.keys()):
                await self.cancel_task(task_id)

            # Update status
            self.status = AgentStatus.OFFLINE
            await self._publish_status_update()

            # Close connections
            if self.session:
                await self.session.close()
            if self.redis_client:
                await self.redis_client.close()

            self.logger.info(f"Agent {self.agent_id} shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Process a task assigned to this agent.

        Args:
            task: Task to process

        Returns:
            Dictionary containing task results
        """
        pass

    @abstractmethod
    def get_task_types(self) -> List[str]:
        """
        Return list of task types this agent can handle.

        Returns:
            List of supported task types
        """
        pass

    async def assign_task(self, task: Task) -> bool:
        """
        Assign a task to this agent.

        Args:
            task: Task to assign

        Returns:
            True if task was accepted, False otherwise
        """
        try:
            # Check if agent can handle this task type
            if task.type not in self.get_task_types():
                self.logger.warning(f"Cannot handle task type: {task.type}")
                return False

            # Check capacity
            if len(self.current_tasks) >= self.max_concurrent_tasks:
                self.logger.warning("Agent at capacity, cannot accept new task")
                return False

            # Check dependencies
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id not in self.completed_tasks:
                        self.logger.warning(f"Task dependency not met: {dep_id}")
                        task.status = TaskStatus.BLOCKED
                        return False

            # Accept task
            task.assignee = self.agent_id
            task.status = TaskStatus.PENDING
            self.current_tasks[task.id] = task

            # Create Linear issue if configured
            await self._create_linear_issue(task)

            # Start processing
            asyncio.create_task(self._execute_task(task))

            self.logger.info(f"Assigned task {task.id}: {task.description}")
            return True

        except Exception as e:
            self.logger.error(f"Error assigning task {task.id}: {e}")
            return False

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.

        Args:
            task_id: ID of task to cancel

        Returns:
            True if task was cancelled, False otherwise
        """
        try:
            if task_id not in self.current_tasks:
                return False

            task = self.current_tasks[task_id]
            task.status = TaskStatus.CANCELLED

            # Update Linear issue
            await self._update_linear_issue(task, "Task cancelled")

            # Remove from current tasks
            del self.current_tasks[task_id]

            self.logger.info(f"Cancelled task {task_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error cancelling task {task_id}: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and metrics.

        Returns:
            Dictionary containing agent status information
        """
        # Update metrics
        self.metrics.uptime_hours = (
            datetime.now(timezone.utc) - self.start_time
        ).total_seconds() / 3600

        if self.metrics.tasks_completed + self.metrics.tasks_failed > 0:
            self.metrics.success_rate = (
                self.metrics.tasks_completed /
                (self.metrics.tasks_completed + self.metrics.tasks_failed)
            )

        return {
            'agent_id': self.agent_id,
            'department': self.department,
            'status': self.status.value,
            'capabilities': list(self.capabilities.keys()),
            'current_tasks': len(self.current_tasks),
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'metrics': asdict(self.metrics),
            'uptime_hours': self.metrics.uptime_hours
        }

    async def send_message(
        self,
        topic: str,
        payload: Dict[str, Any],
        recipient: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Send a message via the message bus.

        Args:
            topic: Message topic
            payload: Message payload
            recipient: Optional specific recipient
            correlation_id: Optional correlation ID for request tracking
        """
        try:
            message = MessageBusMessage(
                sender=self.agent_id,
                recipient=recipient,
                topic=topic,
                payload=payload,
                correlation_id=correlation_id
            )

            channel = f"agent.{recipient}" if recipient else f"topic.{topic}"
            await self.redis_client.publish(channel, message.json())

            self.logger.debug(f"Sent message to {channel}: {topic}")

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def register_message_handler(
        self,
        topic: str,
        handler: Callable[[MessageBusMessage], None]
    ) -> None:
        """
        Register a handler for a specific message topic.

        Args:
            topic: Message topic to handle
            handler: Async function to handle messages
        """
        self.message_handlers[topic] = handler

    async def create_linear_issue(
        self,
        title: str,
        description: str,
        labels: Optional[List[str]] = None,
        priority: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a Linear issue.

        Args:
            title: Issue title
            description: Issue description
            labels: Optional list of labels
            priority: Optional priority level
            parent_id: Optional parent issue ID

        Returns:
            Issue ID if created successfully, None otherwise
        """
        if not self.linear_api_key:
            self.logger.warning("Linear API key not configured")
            return None

        try:
            issue = LinearIssue(
                title=title,
                description=description,
                labels=labels or [],
                priority=priority,
                parent_id=parent_id
            )

            # GraphQL mutation for creating issue
            mutation = """
            mutation CreateIssue($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    issue {
                        id
                        identifier
                    }
                    success
                }
            }
            """

            variables = {
                "input": {
                    "title": issue.title,
                    "description": issue.description,
                    "projectId": issue.project_id,
                    "labelIds": issue.labels,
                    "priority": issue.priority,
                    "parentId": issue.parent_id
                }
            }

            # Remove None values
            variables["input"] = {k: v for k, v in variables["input"].items() if v is not None}

            headers = {
                "Authorization": f"Bearer {self.linear_api_key}",
                "Content-Type": "application/json"
            }

            async with self.session.post(
                "https://api.linear.app/graphql",
                json={"query": mutation, "variables": variables},
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data", {}).get("issueCreate", {}).get("success"):
                        issue_id = data["data"]["issueCreate"]["issue"]["id"]
                        self.logger.info(f"Created Linear issue: {issue_id}")
                        return issue_id
                    else:
                        self.logger.error(f"Failed to create Linear issue: {data}")
                else:
                    self.logger.error(f"Linear API error: {response.status}")

        except Exception as e:
            self.logger.error(f"Error creating Linear issue: {e}")

        return None

    async def update_linear_issue(
        self,
        issue_id: str,
        comment: Optional[str] = None,
        status: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> bool:
        """
        Update a Linear issue.

        Args:
            issue_id: Linear issue ID
            comment: Optional comment to add
            status: Optional status update
            labels: Optional labels to set

        Returns:
            True if updated successfully, False otherwise
        """
        if not self.linear_api_key:
            return False

        try:
            # Add comment if provided
            if comment:
                comment_mutation = """
                mutation CreateComment($input: CommentCreateInput!) {
                    commentCreate(input: $input) {
                        comment {
                            id
                        }
                        success
                    }
                }
                """

                variables = {
                    "input": {
                        "issueId": issue_id,
                        "body": comment
                    }
                }

                headers = {
                    "Authorization": f"Bearer {self.linear_api_key}",
                    "Content-Type": "application/json"
                }

                async with self.session.post(
                    "https://api.linear.app/graphql",
                    json={"query": comment_mutation, "variables": variables},
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data", {}).get("commentCreate", {}).get("success"):
                            self.logger.info(f"Added comment to Linear issue {issue_id}")
                        else:
                            self.logger.error(f"Failed to add comment: {data}")

            return True

        except Exception as e:
            self.logger.error(f"Error updating Linear issue {issue_id}: {e}")
            return False

    # Private methods

    async def _execute_task(self, task: Task) -> None:
        """Execute a task and handle completion/failure."""
        start_time = time.time()

        try:
            # Update status
            task.status = TaskStatus.IN_PROGRESS
            self.status = AgentStatus.ACTIVE
            await self._publish_status_update()
            await self._update_linear_issue(task, f"Task started by {self.agent_id}")

            # Process the task
            result = await self.process_task(task)

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            completion_time = time.time() - start_time

            # Update metrics
            self.metrics.tasks_completed += 1
            self._update_response_time(completion_time)
            self.metrics.last_activity = datetime.now(timezone.utc)

            # Update Linear issue
            await self._update_linear_issue(
                task,
                f"Task completed successfully in {completion_time:.2f}s\n\nResults:\n{json.dumps(result, indent=2)}"
            )

            # Publish completion message
            await self.send_message(
                f"task.completed",
                {
                    "task_id": task.id,
                    "agent_id": self.agent_id,
                    "result": result,
                    "duration": completion_time
                }
            )

            self.logger.info(f"Completed task {task.id} in {completion_time:.2f}s")

        except Exception as e:
            # Mark as failed
            task.status = TaskStatus.FAILED
            self.metrics.tasks_failed += 1

            error_msg = f"Task failed: {str(e)}"
            self.logger.error(f"Task {task.id} failed: {e}")

            # Update Linear issue
            await self._update_linear_issue(task, error_msg)

            # Publish failure message
            await self.send_message(
                f"task.failed",
                {
                    "task_id": task.id,
                    "agent_id": self.agent_id,
                    "error": str(e)
                }
            )

        finally:
            # Remove from current tasks
            if task.id in self.current_tasks:
                del self.current_tasks[task.id]

            # Add to completed tasks history
            self.completed_tasks.append(task.id)

            # Update status
            if not self.current_tasks:
                self.status = AgentStatus.IDLE

            await self._publish_status_update()

    async def _register_message_handlers(self) -> None:
        """Register default message handlers and start listening."""
        # Register default handlers
        await self.register_message_handler("agent.ping", self._handle_ping)
        await self.register_message_handler("agent.status", self._handle_status_request)
        await self.register_message_handler("task.assign", self._handle_task_assignment)

        # Start message listener
        asyncio.create_task(self._message_listener())

    async def _message_listener(self) -> None:
        """Listen for messages on the message bus."""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(f"agent.{self.agent_id}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        msg = MessageBusMessage.parse_raw(message["data"])
                        await self._handle_message(msg)
                    except Exception as e:
                        self.logger.error(f"Error handling message: {e}")

        except Exception as e:
            self.logger.error(f"Message listener error: {e}")

    async def _handle_message(self, message: MessageBusMessage) -> None:
        """Handle incoming messages."""
        handler = self.message_handlers.get(message.topic)
        if handler:
            try:
                await handler(message)
            except Exception as e:
                self.logger.error(f"Error in message handler for {message.topic}: {e}")
        else:
            self.logger.debug(f"No handler for topic: {message.topic}")

    async def _handle_ping(self, message: MessageBusMessage) -> None:
        """Handle ping messages."""
        await self.send_message(
            "agent.pong",
            {"agent_id": self.agent_id, "status": self.status.value},
            message.sender,
            message.correlation_id
        )

    async def _handle_status_request(self, message: MessageBusMessage) -> None:
        """Handle status request messages."""
        status = await self.get_status()
        await self.send_message(
            "agent.status.response",
            status,
            message.sender,
            message.correlation_id
        )

    async def _handle_task_assignment(self, message: MessageBusMessage) -> None:
        """Handle task assignment messages."""
        try:
            task_data = message.payload
            task = Task(
                id=task_data["id"],
                type=task_data["type"],
                description=task_data["description"],
                priority=Priority(task_data["priority"]),
                created_at=datetime.fromisoformat(task_data["created_at"]),
                deadline=datetime.fromisoformat(task_data["deadline"]) if task_data.get("deadline") else None,
                dependencies=task_data.get("dependencies", []),
                metadata=task_data.get("metadata", {})
            )

            success = await self.assign_task(task)

            await self.send_message(
                "task.assignment.response",
                {"task_id": task.id, "accepted": success, "agent_id": self.agent_id},
                message.sender,
                message.correlation_id
            )

        except Exception as e:
            self.logger.error(f"Error handling task assignment: {e}")

    async def _publish_status_update(self) -> None:
        """Publish agent status update."""
        await self.send_message(
            "agent.status.updated",
            {
                "agent_id": self.agent_id,
                "status": self.status.value,
                "current_tasks": len(self.current_tasks),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    async def _create_linear_issue(self, task: Task) -> None:
        """Create Linear issue for a task."""
        if not self.linear_api_key:
            return

        title = f"[{task.type.upper()}] {task.description}"
        description = f"""
## Task Details
- **Type**: {task.type}
- **Priority**: {task.priority.value}
- **Assigned to**: {self.agent_id}
- **Created**: {task.created_at.isoformat()}
- **Deadline**: {task.deadline.isoformat() if task.deadline else 'Not specified'}

## Description
{task.description}

## Dependencies
{', '.join(task.dependencies) if task.dependencies else 'None'}

## Metadata
```json
{json.dumps(task.metadata, indent=2)}
```

---
*Auto-generated by IDFWU Agent System*
        """.strip()

        labels = [task.type, self.department, task.priority.value]

        issue_id = await self.create_linear_issue(
            title=title,
            description=description,
            labels=labels,
            priority=task.priority.value,
            parent_id=task.parent_task
        )

        if issue_id:
            task.metadata["linear_issue_id"] = issue_id

    async def _update_linear_issue(self, task: Task, comment: str) -> None:
        """Update Linear issue for a task."""
        issue_id = task.metadata.get("linear_issue_id")
        if issue_id:
            await self.update_linear_issue(issue_id, comment)

    def _update_response_time(self, duration: float) -> None:
        """Update average response time metric."""
        if self.metrics.avg_response_time == 0:
            self.metrics.avg_response_time = duration
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.avg_response_time = (
                alpha * duration + (1 - alpha) * self.metrics.avg_response_time
            )


# Example specialized agent implementation
class ExampleDeveloperAgent(BaseAgent):
    """Example implementation of a developer agent."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        capabilities = [
            AgentCapability(
                name="code_development",
                description="Develop and implement software features",
                expertise_level=0.9,
                task_types=["feature_implementation", "bug_fix", "code_review"]
            ),
            AgentCapability(
                name="testing",
                description="Create and execute tests",
                expertise_level=0.8,
                task_types=["unit_testing", "integration_testing"]
            )
        ]

        super().__init__(
            agent_id="ExampleDeveloperAgent",
            department="development",
            capabilities=capabilities,
            config=config
        )

    def get_task_types(self) -> List[str]:
        """Return supported task types."""
        return [
            "feature_implementation",
            "bug_fix",
            "code_review",
            "unit_testing",
            "integration_testing"
        ]

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a development task."""
        self.logger.info(f"Processing {task.type}: {task.description}")

        # Simulate task processing
        await asyncio.sleep(2)

        if task.type == "feature_implementation":
            return await self._implement_feature(task)
        elif task.type == "bug_fix":
            return await self._fix_bug(task)
        elif task.type == "code_review":
            return await self._review_code(task)
        elif task.type in ["unit_testing", "integration_testing"]:
            return await self._run_tests(task)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")

    async def _implement_feature(self, task: Task) -> Dict[str, Any]:
        """Implement a feature."""
        # Simulate feature implementation
        await asyncio.sleep(5)

        return {
            "status": "completed",
            "files_modified": ["src/feature.py", "tests/test_feature.py"],
            "lines_added": 150,
            "lines_removed": 25,
            "test_coverage": 95.0
        }

    async def _fix_bug(self, task: Task) -> Dict[str, Any]:
        """Fix a bug."""
        # Simulate bug fix
        await asyncio.sleep(3)

        return {
            "status": "completed",
            "files_modified": ["src/buggy_module.py"],
            "lines_added": 10,
            "lines_removed": 5,
            "tests_added": 2
        }

    async def _review_code(self, task: Task) -> Dict[str, Any]:
        """Review code."""
        # Simulate code review
        await asyncio.sleep(4)

        return {
            "status": "completed",
            "files_reviewed": 5,
            "issues_found": 2,
            "suggestions": 8,
            "approval": True
        }

    async def _run_tests(self, task: Task) -> Dict[str, Any]:
        """Run tests."""
        # Simulate test execution
        await asyncio.sleep(3)

        return {
            "status": "completed",
            "tests_run": 125,
            "tests_passed": 123,
            "tests_failed": 2,
            "coverage": 87.5
        }


if __name__ == "__main__":
    """Example usage of the base agent system."""
    import sys

    async def main():
        """Main example function."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create and initialize agent
        config = {
            'max_concurrent_tasks': 3,
            'linear_api_key': 'your_linear_api_key_here',
            'redis_url': 'redis://localhost:6379'
        }

        agent = ExampleDeveloperAgent(config)

        try:
            await agent.initialize()

            # Create and assign a sample task
            task = Task(
                id=str(uuid.uuid4()),
                type="feature_implementation",
                description="Implement user authentication system",
                priority=Priority.HIGH,
                created_at=datetime.now(timezone.utc),
                metadata={"complexity": "medium", "estimated_hours": 8}
            )

            success = await agent.assign_task(task)
            if success:
                print(f"Task assigned successfully: {task.id}")
            else:
                print("Failed to assign task")

            # Wait for task completion
            await asyncio.sleep(10)

            # Get agent status
            status = await agent.get_status()
            print(f"Agent status: {json.dumps(status, indent=2)}")

        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            await agent.shutdown()

    # Run the example
    asyncio.run(main())
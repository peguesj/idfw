"""
Orchestrator Agent for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module implements the master orchestration agent responsible for coordinating all agent activities,
tracking progress, ensuring successful completion of tasks, and maintaining comprehensive system state.
"""

import asyncio
import json
import logging
import redis
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from uuid import uuid4

from .base_agent import BaseAgent, Task, Message, TaskStatus, AgentStatus, MessagePriority, PerformanceMetrics

# Configure logging
logger = logging.getLogger(__name__)


class AgentInfo:
    """Information about a registered agent"""
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.OFFLINE
        self.last_heartbeat = None
        self.current_tasks = set()
        self.load_score = 0.0
        self.performance_metrics = PerformanceMetrics()


class TaskDependency:
    """Represents task dependencies"""
    def __init__(self, task_id: str, depends_on: List[str]):
        self.task_id = task_id
        self.depends_on = depends_on
        self.satisfied = False


class MessageQueue:
    """Persistent message queue with Redis backend"""
    def __init__(self, redis_client: redis.Redis, channel_prefix: str = "idfwu:mq"):
        self.redis = redis_client
        self.channel_prefix = channel_prefix
        
    async def publish(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """Publish message to queue"""
        try:
            queue_key = f"{self.channel_prefix}:{queue_name}"
            message_json = json.dumps(message)
            await self.redis.lpush(queue_key, message_json)
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    async def consume(self, queue_name: str, timeout: int = 1) -> Optional[Dict[str, Any]]:
        """Consume message from queue"""
        try:
            queue_key = f"{self.channel_prefix}:{queue_name}"
            result = await self.redis.brpop(queue_key, timeout=timeout)
            if result:
                _, message_json = result
                return json.loads(message_json)
            return None
        except Exception as e:
            logger.error(f"Failed to consume message: {e}")
            return None


class StateManager:
    """Manages persistent state for stateful agents"""
    def __init__(self, redis_client: redis.Redis, state_prefix: str = "idfwu:state"):
        self.redis = redis_client
        self.state_prefix = state_prefix
        self.state_cache = {}
    
    async def save_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """Save agent state"""
        try:
            state_key = f"{self.state_prefix}:{agent_id}"
            state_json = json.dumps(state)
            await self.redis.set(state_key, state_json)
            self.state_cache[agent_id] = state
            return True
        except Exception as e:
            logger.error(f"Failed to save state for {agent_id}: {e}")
            return False
    
    async def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state"""
        try:
            if agent_id in self.state_cache:
                return self.state_cache[agent_id]
            
            state_key = f"{self.state_prefix}:{agent_id}"
            state_json = await self.redis.get(state_key)
            if state_json:
                state = json.loads(state_json)
                self.state_cache[agent_id] = state
                return state
            return None
        except Exception as e:
            logger.error(f"Failed to load state for {agent_id}: {e}")
            return None


class OrchestratorAgent(BaseAgent):
    """
    Master orchestration agent responsible for:
    - Agent lifecycle management
    - Progress tracking
    - Communication hub
    - State management
    - Task distribution
    - Result aggregation
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", **kwargs):
        super().__init__(
            agent_id="orchestrator",
            agent_type="OrchestratorAgent",
            **kwargs
        )
        
        # Redis connection
        self.redis_url = redis_url
        self.redis_client = None
        
        # Core components
        self.message_queue = None
        self.state_manager = None
        
        # Agent registry and management
        self.agent_registry: Dict[str, AgentInfo] = {}
        self.agent_capabilities: Dict[str, Set[str]] = defaultdict(set)
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 90  # seconds
        
        # Task management
        self.global_tasks: Dict[str, Task] = {}
        self.task_dependencies: Dict[str, TaskDependency] = {}
        self.task_queue = deque()
        self.priority_queues = {
            MessagePriority.URGENT: deque(),
            MessagePriority.HIGH: deque(),
            MessagePriority.NORMAL: deque(),
            MessagePriority.LOW: deque(),
        }
        
        # Result aggregation
        self.execution_results: Dict[str, Dict[str, Any]] = {}
        self.session_metrics: Dict[str, Any] = {}
        
        # Monitoring and health
        self.health_checks: Dict[str, Callable] = {}
        self.error_recovery_handlers: Dict[str, Callable] = {}
        self.resource_monitors: Dict[str, float] = {}
        
        # Configuration
        self.max_parallel_agents = 10
        self.max_api_calls_per_second = 5
        self.rate_limit_window = {}
        
        # Event hooks
        self.hooks = {
            'before_agent_spawn': [],
            'before_command': [],
            'before_parallel_execution': [],
            'on_progress': [],
            'on_warning': [],
            'on_error': [],
            'on_agent_communication': [],
            'after_agent_complete': [],
            'after_command': [],
            'after_all_complete': []
        }
        
        # Initialize message handlers
        self._register_message_handlers()
    
    async def initialize(self) -> bool:
        """Initialize the orchestrator with Redis connection and core components"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Initialize core components
            self.message_queue = MessageQueue(self.redis_client)
            self.state_manager = StateManager(self.redis_client)
            
            # Start background tasks
            asyncio.create_task(self._heartbeat_monitor())
            asyncio.create_task(self._task_distributor())
            asyncio.create_task(self._resource_monitor())
            
            logger.info("Orchestrator agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            return False
    
    def _register_message_handlers(self):
        """Register handlers for different message types"""
        self.register_handler("agent_register", self._handle_agent_register)
        self.register_handler("agent_heartbeat", self._handle_agent_heartbeat)
        self.register_handler("task_request", self._handle_task_request)
        self.register_handler("task_complete", self._handle_task_complete)
        self.register_handler("task_failed", self._handle_task_failed)
        self.register_handler("agent_communication", self._handle_agent_communication)
        self.register_handler("resource_alert", self._handle_resource_alert)
    
    async def _handle_agent_register(self, message: Message):
        """Handle agent registration"""
        payload = message.payload
        agent_id = payload.get("agent_id")
        agent_type = payload.get("agent_type")
        capabilities = payload.get("capabilities", [])
        
        if agent_id and agent_type:
            agent_info = AgentInfo(agent_id, agent_type, capabilities)
            agent_info.status = AgentStatus.ACTIVE
            agent_info.last_heartbeat = datetime.utcnow()
            
            self.agent_registry[agent_id] = agent_info
            
            for capability in capabilities:
                self.agent_capabilities[capability].add(agent_id)
            
            logger.info(f"Registered agent {agent_id} ({agent_type}) with capabilities: {capabilities}")
            
            # Send acknowledgment
            await self.send_message(
                agent_id,
                "registration_ack",
                {"status": "registered", "orchestrator_id": self.agent_id}
            )
    
    async def _handle_agent_heartbeat(self, message: Message):
        """Handle agent heartbeat"""
        agent_id = message.sender_id
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id].last_heartbeat = datetime.utcnow()
            self.agent_registry[agent_id].status = AgentStatus.ACTIVE
    
    async def _handle_task_request(self, message: Message):
        """Handle task distribution request"""
        payload = message.payload
        task_type = payload.get("task_type")
        requirements = payload.get("requirements", {})
        priority = MessagePriority(payload.get("priority", "normal"))
        
        # Find suitable agents
        suitable_agents = self._find_suitable_agents(task_type, requirements)
        
        if suitable_agents:
            # Select best agent based on load and performance
            selected_agent = self._select_best_agent(suitable_agents)
            
            # Create and assign task
            task = await self.create_task(
                description=payload.get("description", ""),
                priority=priority,
                metadata=payload
            )
            
            self.global_tasks[task.id] = task
            self.agent_registry[selected_agent].current_tasks.add(task.id)
            
            # Send task to agent
            await self.send_message(
                selected_agent,
                "task_assignment",
                {
                    "task_id": task.id,
                    "task": task.dict(),
                    "requirements": requirements
                }
            )
            
            logger.info(f"Assigned task {task.id} to agent {selected_agent}")
        else:
            logger.warning(f"No suitable agents found for task type: {task_type}")
    
    async def _handle_task_complete(self, message: Message):
        """Handle task completion"""
        payload = message.payload
        task_id = payload.get("task_id")
        result = payload.get("result", {})
        
        if task_id in self.global_tasks:
            task = self.global_tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            # Update agent status
            agent_id = message.sender_id
            if agent_id in self.agent_registry:
                self.agent_registry[agent_id].current_tasks.discard(task_id)
                self.agent_registry[agent_id].performance_metrics.tasks_completed += 1
            
            # Store result
            self.execution_results[task_id] = result
            
            # Check for dependent tasks
            await self._check_dependency_completion(task_id)
            
            # Call completion hook
            await self._call_hook('after_agent_complete', {'task': task, 'result': result})
            
            logger.info(f"Task {task_id} completed successfully")
    
    async def _handle_task_failed(self, message: Message):
        """Handle task failure"""
        payload = message.payload
        task_id = payload.get("task_id")
        error = payload.get("error", "Unknown error")
        
        if task_id in self.global_tasks:
            task = self.global_tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            task.completed_at = datetime.utcnow()
            
            # Update agent status
            agent_id = message.sender_id
            if agent_id in self.agent_registry:
                self.agent_registry[agent_id].current_tasks.discard(task_id)
                self.agent_registry[agent_id].performance_metrics.tasks_failed += 1
            
            # Determine recovery strategy
            await self._handle_task_failure_recovery(task)
            
            logger.error(f"Task {task_id} failed: {error}")
    
    async def _handle_agent_communication(self, message: Message):
        """Handle inter-agent communication"""
        # Route message to target agent
        target_agent = message.payload.get("target_agent")
        if target_agent and target_agent in self.agent_registry:
            await self.message_queue.publish(f"agent:{target_agent}", message.payload)
            
        # Call communication hook
        await self._call_hook('on_agent_communication', {'message': message})
    
    async def _handle_resource_alert(self, message: Message):
        """Handle resource alerts"""
        alert_type = message.payload.get("alert_type")
        severity = message.payload.get("severity")
        details = message.payload.get("details", {})
        
        logger.warning(f"Resource alert: {alert_type} (severity: {severity})")
        
        # Implement resource management logic
        if alert_type == "high_memory":
            await self._handle_high_memory_alert(details)
        elif alert_type == "high_cpu":
            await self._handle_high_cpu_alert(details)
        elif alert_type == "rate_limit":
            await self._handle_rate_limit_alert(details)
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats and detect failed agents"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                failed_agents = []
                
                for agent_id, agent_info in self.agent_registry.items():
                    if agent_info.last_heartbeat:
                        time_since_heartbeat = (current_time - agent_info.last_heartbeat).total_seconds()
                        if time_since_heartbeat > self.heartbeat_timeout:
                            failed_agents.append(agent_id)
                
                # Handle failed agents
                for agent_id in failed_agents:
                    await self._handle_agent_failure(agent_id)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(5)
    
    async def _task_distributor(self):
        """Distribute tasks from priority queues"""
        while self._running:
            try:
                # Process queues by priority
                for priority in [MessagePriority.URGENT, MessagePriority.HIGH, 
                               MessagePriority.NORMAL, MessagePriority.LOW]:
                    queue = self.priority_queues[priority]
                    if queue:
                        task_request = queue.popleft()
                        await self._process_task_request(task_request)
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in task distributor: {e}")
                await asyncio.sleep(1)
    
    async def _resource_monitor(self):
        """Monitor system resources and trigger alerts"""
        while self._running:
            try:
                # Monitor agent loads
                for agent_id, agent_info in self.agent_registry.items():
                    load_score = len(agent_info.current_tasks) / max(1, len(agent_info.capabilities))
                    agent_info.load_score = load_score
                    
                    if load_score > 0.8:  # 80% load threshold
                        await self.send_message(
                            None,  # Broadcast
                            "resource_alert",
                            {
                                "alert_type": "high_agent_load",
                                "agent_id": agent_id,
                                "load_score": load_score,
                                "severity": "warning"
                            }
                        )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in resource monitor: {e}")
                await asyncio.sleep(10)
    
    def _find_suitable_agents(self, task_type: str, requirements: Dict[str, Any]) -> List[str]:
        """Find agents suitable for a task"""
        suitable_agents = []
        
        for agent_id, agent_info in self.agent_registry.items():
            if (agent_info.status == AgentStatus.ACTIVE and 
                task_type in agent_info.capabilities and
                agent_info.load_score < 1.0):  # Not overloaded
                suitable_agents.append(agent_id)
        
        return suitable_agents
    
    def _select_best_agent(self, suitable_agents: List[str]) -> str:
        """Select the best agent based on load and performance"""
        if not suitable_agents:
            return None
        
        # Score agents by load and performance
        best_agent = None
        best_score = float('inf')
        
        for agent_id in suitable_agents:
            agent_info = self.agent_registry[agent_id]
            
            # Lower is better: load + failure rate
            failure_rate = 0
            if agent_info.performance_metrics.tasks_completed > 0:
                total_tasks = (agent_info.performance_metrics.tasks_completed + 
                             agent_info.performance_metrics.tasks_failed)
                failure_rate = agent_info.performance_metrics.tasks_failed / total_tasks
            
            score = agent_info.load_score + failure_rate
            
            if score < best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    async def _check_dependency_completion(self, completed_task_id: str):
        """Check if task completion enables dependent tasks"""
        for dependency in self.task_dependencies.values():
            if completed_task_id in dependency.depends_on:
                dependency.depends_on.remove(completed_task_id)
                
                if not dependency.depends_on:  # All dependencies satisfied
                    dependency.satisfied = True
                    # Enable the dependent task
                    await self._enable_dependent_task(dependency.task_id)
    
    async def _enable_dependent_task(self, task_id: str):
        """Enable a task whose dependencies are now satisfied"""
        if task_id in self.global_tasks:
            task = self.global_tasks[task_id]
            # Add to appropriate priority queue for execution
            self.priority_queues[task.priority].append(task)
            logger.info(f"Enabled dependent task: {task_id}")
    
    async def _handle_agent_failure(self, agent_id: str):
        """Handle agent failure and recovery"""
        logger.warning(f"Agent {agent_id} appears to have failed")
        
        agent_info = self.agent_registry[agent_id]
        agent_info.status = AgentStatus.ERROR
        
        # Reassign active tasks
        failed_tasks = list(agent_info.current_tasks)
        agent_info.current_tasks.clear()
        
        for task_id in failed_tasks:
            if task_id in self.global_tasks:
                task = self.global_tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = f"Agent {agent_id} failed"
                
                # Attempt to reassign to another agent
                await self._reassign_task(task)
    
    async def _reassign_task(self, task: Task):
        """Reassign a failed task to another agent"""
        # Find suitable agents for reassignment
        suitable_agents = self._find_suitable_agents(
            task.metadata.get("task_type", ""), 
            task.metadata.get("requirements", {})
        )
        
        if suitable_agents:
            selected_agent = self._select_best_agent(suitable_agents)
            
            # Create new task for reassignment
            new_task = await self.create_task(
                description=f"REASSIGNED: {task.description}",
                priority=task.priority,
                metadata=task.metadata
            )
            
            self.global_tasks[new_task.id] = new_task
            self.agent_registry[selected_agent].current_tasks.add(new_task.id)
            
            await self.send_message(
                selected_agent,
                "task_assignment",
                {
                    "task_id": new_task.id,
                    "task": new_task.dict(),
                    "requirements": task.metadata.get("requirements", {})
                }
            )
            
            logger.info(f"Reassigned task {task.id} as {new_task.id} to agent {selected_agent}")
    
    async def _handle_task_failure_recovery(self, task: Task):
        """Handle task failure and determine recovery strategy"""
        retry_count = task.metadata.get("retry_count", 0)
        max_retries = task.metadata.get("max_retries", 3)
        
        if retry_count < max_retries:
            # Retry the task
            task.metadata["retry_count"] = retry_count + 1
            task.status = TaskStatus.PENDING
            task.error = None
            
            # Add back to queue for retry
            self.priority_queues[task.priority].append(task)
            logger.info(f"Retrying task {task.id} (attempt {retry_count + 1})")
        else:
            # Max retries reached, mark as permanently failed
            logger.error(f"Task {task.id} permanently failed after {max_retries} retries")
            
            # Call error hook
            await self._call_hook('on_error', {'task': task, 'permanent_failure': True})
    
    async def _call_hook(self, hook_name: str, context: Dict[str, Any]):
        """Call registered hooks"""
        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                try:
                    await hook_func(context)
                except Exception as e:
                    logger.error(f"Error in hook {hook_name}: {e}")
    
    def register_hook(self, hook_name: str, hook_func: Callable):
        """Register a hook function"""
        if hook_name in self.hooks:
            self.hooks[hook_name].append(hook_func)
        else:
            logger.warning(f"Unknown hook name: {hook_name}")
    
    async def spawn_agent(self, agent_type: str, agent_config: Dict[str, Any]) -> Optional[str]:
        """Spawn a new agent"""
        agent_id = f"{agent_type}_{uuid4().hex[:8]}"
        
        # Call pre-spawn hook
        await self._call_hook('before_agent_spawn', {
            'agent_type': agent_type, 
            'agent_config': agent_config
        })
        
        try:
            # In a real implementation, this would actually spawn the agent process
            # For now, we'll simulate it
            logger.info(f"Spawning agent {agent_id} of type {agent_type}")
            
            # Simulate agent registration
            capabilities = agent_config.get("capabilities", [])
            agent_info = AgentInfo(agent_id, agent_type, capabilities)
            agent_info.status = AgentStatus.ACTIVE
            agent_info.last_heartbeat = datetime.utcnow()
            
            self.agent_registry[agent_id] = agent_info
            
            for capability in capabilities:
                self.agent_capabilities[capability].add(agent_id)
            
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to spawn agent {agent_type}: {e}")
            return None
    
    async def deploy_agent_swarm(self, epic_id: str, strategy: str, agent_count: int = 20) -> Dict[str, Any]:
        """Deploy a swarm of agents for epic execution"""
        logger.info(f"Deploying agent swarm for epic {epic_id} with strategy {strategy}")
        
        spawned_agents = []
        deployment_results = {}
        
        # Define agent types for swarm
        swarm_config = {
            "backend_agents": agent_count // 4,
            "frontend_agents": agent_count // 4,
            "test_agents": agent_count // 4,
            "qa_agents": agent_count // 4,
        }
        
        try:
            for agent_type, count in swarm_config.items():
                for i in range(count):
                    agent_config = {
                        "capabilities": [agent_type.replace("_agents", "")],
                        "epic_id": epic_id,
                        "strategy": strategy
                    }
                    
                    agent_id = await self.spawn_agent(agent_type, agent_config)
                    if agent_id:
                        spawned_agents.append(agent_id)
            
            deployment_results = {
                "epic_id": epic_id,
                "strategy": strategy,
                "spawned_agents": spawned_agents,
                "total_agents": len(spawned_agents),
                "deployment_time": datetime.utcnow().isoformat(),
                "status": "deployed"
            }
            
            logger.info(f"Successfully deployed {len(spawned_agents)} agents for epic {epic_id}")
            
        except Exception as e:
            logger.error(f"Failed to deploy agent swarm: {e}")
            deployment_results["status"] = "failed"
            deployment_results["error"] = str(e)
        
        return deployment_results
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        active_agents = sum(1 for a in self.agent_registry.values() if a.status == AgentStatus.ACTIVE)
        total_tasks = len(self.global_tasks)
        completed_tasks = sum(1 for t in self.global_tasks.values() if t.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for t in self.global_tasks.values() if t.status == TaskStatus.FAILED)
        
        return {
            "orchestrator_status": self.status.value,
            "total_agents": len(self.agent_registry),
            "active_agents": active_agents,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / max(1, total_tasks) * 100,
            "agent_registry": {
                agent_id: {
                    "type": info.agent_type,
                    "status": info.status.value,
                    "current_tasks": len(info.current_tasks),
                    "load_score": info.load_score
                }
                for agent_id, info in self.agent_registry.items()
            },
            "queue_status": {
                "urgent": len(self.priority_queues[MessagePriority.URGENT]),
                "high": len(self.priority_queues[MessagePriority.HIGH]),
                "normal": len(self.priority_queues[MessagePriority.NORMAL]),
                "low": len(self.priority_queues[MessagePriority.LOW])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process orchestrator-specific tasks"""
        task_type = task.metadata.get("task_type", "")
        
        if task_type == "system_status":
            return await self.get_system_status()
        elif task_type == "deploy_swarm":
            epic_id = task.metadata.get("epic_id")
            strategy = task.metadata.get("strategy", "default")
            agent_count = task.metadata.get("agent_count", 20)
            return await self.deploy_agent_swarm(epic_id, strategy, agent_count)
        else:
            return {"status": "completed", "message": f"Processed orchestrator task: {task.description}"}
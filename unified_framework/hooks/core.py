"""
Core hook infrastructure with event dispatcher and hook registry.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, asdict


class HookType(Enum):
    """Hook execution types."""
    PREHOOK = "prehook"
    POSTHOOK = "posthook"
    POST_TOOL_USE = "post_tool_use"
    CONTEXT_HOOK = "context_hook"
    ERROR_HOOK = "error_hook"


class MessageScope(Enum):
    """Message scope detection categories."""
    USER = "user"
    TASK = "task"
    THREAD = "thread"
    PROJECT = "project"
    AGENT = "agent"
    COMMAND = "command"
    SYSTEM = "system"
    ERROR = "error"


@dataclass
class HookContext:
    """Context passed to hooks during execution."""
    hook_id: str
    hook_type: HookType
    timestamp: datetime
    scope: MessageScope
    message: str
    metadata: Dict[str, Any]
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    thread_id: Optional[str] = None
    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        from enum import Enum
        return {
            'hook_id': self.hook_id,
            'hook_type': self.hook_type.value if isinstance(self.hook_type, Enum) else str(self.hook_type),
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
            'scope': self.scope.value if isinstance(self.scope, Enum) else str(self.scope),
            'message': self.message,
            'metadata': self.metadata,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'thread_id': self.thread_id,
            'task_id': self.task_id
        }


@dataclass
class HookResult:
    """Result from hook execution."""
    hook_id: str
    success: bool
    execution_time: float
    result: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class HookRegistry:
    """Registry for managing hooks and their execution order."""
    
    def __init__(self):
        self._hooks: Dict[HookType, List[Callable]] = {
            hook_type: [] for hook_type in HookType
        }
        self._hook_metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register(
        self,
        hook_type: HookType,
        hook_func: Callable,
        priority: int = 100,
        **metadata
    ) -> str:
        """Register a hook function."""
        hook_id = str(uuid.uuid4())
        
        # Store hook with metadata
        self._hook_metadata[hook_id] = {
            'hook_type': hook_type,
            'priority': priority,
            'function': hook_func,
            **metadata
        }
        
        # Add to hooks list and sort by priority
        self._hooks[hook_type].append((hook_id, hook_func, priority))
        self._hooks[hook_type].sort(key=lambda x: x[2])  # Sort by priority
        
        self.logger.info(f"Registered hook {hook_id} for {hook_type.value}")
        return hook_id
    
    def unregister(self, hook_id: str) -> bool:
        """Unregister a hook by ID."""
        if hook_id not in self._hook_metadata:
            return False
        
        hook_type = self._hook_metadata[hook_id]['hook_type']
        self._hooks[hook_type] = [
            (hid, func, prio) for hid, func, prio in self._hooks[hook_type]
            if hid != hook_id
        ]
        
        del self._hook_metadata[hook_id]
        self.logger.info(f"Unregistered hook {hook_id}")
        return True
    
    def get_hooks(self, hook_type: HookType) -> List[tuple]:
        """Get all hooks for a specific type, ordered by priority."""
        return self._hooks[hook_type]
    
    def get_hook_info(self, hook_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific hook."""
        return self._hook_metadata.get(hook_id)


class EventDispatcher:
    """Event dispatcher for hook execution with async support."""
    
    def __init__(self, registry: HookRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
        self._execution_history: List[HookResult] = []
        self._max_history = 1000
    
    async def dispatch(
        self,
        hook_type: HookType,
        context: HookContext,
        parallel: bool = True
    ) -> List[HookResult]:
        """Dispatch hooks for execution."""
        hooks = self.registry.get_hooks(hook_type)
        
        if not hooks:
            self.logger.debug(f"No hooks registered for {hook_type.value}")
            return []
        
        self.logger.info(f"Dispatching {len(hooks)} hooks for {hook_type.value}")
        
        if parallel:
            return await self._execute_parallel(hooks, context)
        else:
            return await self._execute_sequential(hooks, context)
    
    async def _execute_parallel(
        self,
        hooks: List[tuple],
        context: HookContext
    ) -> List[HookResult]:
        """Execute hooks in parallel."""
        tasks = []
        
        for hook_id, hook_func, priority in hooks:
            task = asyncio.create_task(
                self._execute_hook(hook_id, hook_func, context)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                hook_id, _, _ = hooks[i]
                processed_results.append(HookResult(
                    hook_id=hook_id,
                    success=False,
                    execution_time=0.0,
                    result=None,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_sequential(
        self,
        hooks: List[tuple],
        context: HookContext
    ) -> List[HookResult]:
        """Execute hooks sequentially."""
        results = []
        
        for hook_id, hook_func, priority in hooks:
            result = await self._execute_hook(hook_id, hook_func, context)
            results.append(result)
            
            # Stop on critical failure if configured
            if not result.success and self._should_stop_on_failure(hook_id):
                self.logger.warning(f"Stopping execution due to failure in {hook_id}")
                break
        
        return results
    
    async def _execute_hook(
        self,
        hook_id: str,
        hook_func: Callable,
        context: HookContext
    ) -> HookResult:
        """Execute a single hook function."""
        start_time = time.time()
        
        try:
            # Check if hook function is async
            if asyncio.iscoroutinefunction(hook_func):
                result = await hook_func(context)
            else:
                result = hook_func(context)
            
            execution_time = time.time() - start_time
            
            hook_result = HookResult(
                hook_id=hook_id,
                success=True,
                execution_time=execution_time,
                result=result
            )
            
            self.logger.debug(f"Hook {hook_id} executed successfully in {execution_time:.3f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            hook_result = HookResult(
                hook_id=hook_id,
                success=False,
                execution_time=execution_time,
                result=None,
                error=str(e)
            )
            
            self.logger.error(f"Hook {hook_id} failed: {e}")
        
        # Store in history
        self._add_to_history(hook_result)
        return hook_result
    
    def _should_stop_on_failure(self, hook_id: str) -> bool:
        """Check if execution should stop on failure for this hook."""
        hook_info = self.registry.get_hook_info(hook_id)
        return hook_info and hook_info.get('stop_on_failure', False)
    
    def _add_to_history(self, result: HookResult):
        """Add result to execution history."""
        self._execution_history.append(result)
        
        # Trim history if too long
        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]
    
    def get_execution_history(
        self,
        hook_type: Optional[HookType] = None,
        limit: Optional[int] = None
    ) -> List[HookResult]:
        """Get execution history, optionally filtered."""
        history = self._execution_history
        
        if hook_type:
            # Filter by hook type (would need hook_type in result)
            pass
        
        if limit:
            history = history[-limit:]
        
        return history


class HookSystem:
    """Main hook system coordinating all components."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / '.claude' / 'hooks' / 'config.json'
        self.registry = HookRegistry()
        self.dispatcher = EventDispatcher(self.registry)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize storage paths
        self._init_storage()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load hook system configuration."""
        default_config = {
            'storage_root': str(Path.home() / '.claude' / 'hooks'),
            'max_memory_mb': 1000,
            'retention_days': 30,
            'auto_cleanup': True,
            'compression_enabled': True,
            'encryption_enabled': True,
            'backup_enabled': True,
            'vector_db_enabled': True,
            'parallel_execution': True,
            'max_concurrent_hooks': 10,
            'hook_timeout_seconds': 30
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _init_storage(self):
        """Initialize storage directories."""
        storage_root = Path(self.config['storage_root'])
        
        # Create all required directories
        dirs = [
            'messages', 'reports', 'learning', 'patterns', 
            'cache', 'security'
        ]
        
        for dir_name in dirs:
            (storage_root / dir_name).mkdir(parents=True, exist_ok=True)
        
        # Create references directories
        refs_root = Path.home() / '.claude' / 'references'
        ref_dirs = ['threads', 'thought_chains', 'patterns', 'performance']
        
        for dir_name in ref_dirs:
            (refs_root / dir_name).mkdir(parents=True, exist_ok=True)
    
    async def process_message(
        self,
        message: str,
        scope: MessageScope = MessageScope.USER,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message through the hook system."""
        
        # Create context
        context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=scope,
            message=message,
            metadata=metadata or {},
            project_id=self.config.get('project_id'),
            thread_id=self.config.get('thread_id')
        )
        
        # Execute prehooks
        prehook_results = await self.dispatcher.dispatch(
            HookType.PREHOOK,
            context,
            parallel=self.config.get('parallel_execution', True)
        )
        
        # Return processing results
        return {
            'context': context.to_dict(),
            'prehook_results': [r.to_dict() for r in prehook_results],
            'processing_time': sum(r.execution_time for r in prehook_results)
        }
    
    async def process_tool_result(
        self,
        tool_name: str,
        tool_result: Any,
        context: Optional[HookContext] = None
    ) -> Dict[str, Any]:
        """Process tool usage results."""
        
        if context is None:
            context = HookContext(
                hook_id=str(uuid.uuid4()),
                hook_type=HookType.POST_TOOL_USE,
                timestamp=datetime.now(),
                scope=MessageScope.SYSTEM,
                message=f"Tool used: {tool_name}",
                metadata={'tool_name': tool_name, 'tool_result': tool_result}
            )
        
        # Execute post-tool-use hooks
        results = await self.dispatcher.dispatch(
            HookType.POST_TOOL_USE,
            context,
            parallel=self.config.get('parallel_execution', True)
        )
        
        return {
            'context': context.to_dict(),
            'results': [r.to_dict() for r in results]
        }
    
    def save_config(self):
        """Save current configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        history = self.dispatcher.get_execution_history()
        
        total_executions = len(history)
        successful_executions = sum(1 for r in history if r.success)
        failed_executions = total_executions - successful_executions
        
        avg_execution_time = (
            sum(r.execution_time for r in history) / total_executions
            if total_executions > 0 else 0
        )
        
        return {
            'total_hooks_registered': len(self.registry._hook_metadata),
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
            'average_execution_time': avg_execution_time,
            'storage_root': self.config['storage_root']
        }


# Global hook system instance
_hook_system: Optional[HookSystem] = None


def get_hook_system() -> HookSystem:
    """Get the global hook system instance."""
    global _hook_system
    if _hook_system is None:
        _hook_system = HookSystem()
    return _hook_system
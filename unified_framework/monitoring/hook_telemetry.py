"""
Hook Telemetry Collection and Performance Monitoring

This module implements comprehensive hook usage tracking and performance metrics
collection, integrating with the .claude directory hooks system.
"""

import time
import json
import os
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import hashlib
import traceback

# Performance timing
from time import perf_counter_ns


@dataclass
class HookMetrics:
    """Performance metrics for a hook execution"""
    
    hook_id: str
    hook_type: str  # prehook, posthook
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    
    # Resource metrics
    cpu_percent_before: float = 0.0
    cpu_percent_after: Optional[float] = None
    memory_mb_before: float = 0.0
    memory_mb_after: Optional[float] = None
    memory_delta_mb: Optional[float] = None
    
    # Execution context
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    parent_hook_id: Optional[str] = None
    thread_id: int = field(default_factory=lambda: threading.get_ident())
    
    # Status tracking
    status: str = 'running'  # running, completed, failed
    error: Optional[str] = None
    error_trace: Optional[str] = None
    
    # Additional metrics
    input_size_bytes: int = 0
    output_size_bytes: int = 0
    network_calls: int = 0
    db_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def complete(self):
        """Mark hook as completed and calculate final metrics"""
        self.end_time = perf_counter_ns() / 1_000_000  # Convert to ms
        self.duration_ms = self.end_time - self.start_time
        
        # Capture final resource metrics
        self.cpu_percent_after = psutil.cpu_percent(interval=0.1)
        process = psutil.Process()
        self.memory_mb_after = process.memory_info().rss / 1024 / 1024
        self.memory_delta_mb = self.memory_mb_after - self.memory_mb_before
        
        self.status = 'completed'
    
    def fail(self, error: Exception):
        """Mark hook as failed with error details"""
        self.complete()
        self.status = 'failed'
        self.error = str(error)
        self.error_trace = traceback.format_exc()


@dataclass
class HookTrace:
    """Distributed trace for hook execution chain"""
    
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    start_time: float = field(default_factory=lambda: perf_counter_ns() / 1_000_000)
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    child_spans: List['HookTrace'] = field(default_factory=list)
    
    def add_log(self, message: str, level: str = 'info'):
        """Add a log entry to the trace"""
        self.logs.append({
            'timestamp': perf_counter_ns() / 1_000_000,
            'level': level,
            'message': message
        })
    
    def finish(self):
        """Complete the span"""
        self.end_time = perf_counter_ns() / 1_000_000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary format"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_ms': (self.end_time - self.start_time) if self.end_time else None,
            'tags': self.tags,
            'logs': self.logs,
            'child_spans': [child.to_dict() for child in self.child_spans]
        }


class HookTelemetryCollector:
    """Collects and aggregates hook telemetry data"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize telemetry collector
        
        Args:
            base_dir: Base directory for storing telemetry data
        """
        self.base_dir = base_dir or Path.home() / '.claude' / 'hooks' / 'telemetry'
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Active hooks tracking
        self.active_hooks: Dict[str, HookMetrics] = {}
        self.completed_hooks: deque = deque(maxlen=10000)  # Circular buffer
        
        # Traces tracking
        self.active_traces: Dict[str, HookTrace] = {}
        self.completed_traces: deque = deque(maxlen=1000)
        
        # Aggregated metrics
        self.metrics_summary = defaultdict(lambda: {
            'count': 0,
            'total_duration_ms': 0,
            'avg_duration_ms': 0,
            'min_duration_ms': float('inf'),
            'max_duration_ms': 0,
            'error_count': 0,
            'success_rate': 0.0
        })
        
        # Performance baselines
        self.performance_baselines = {}
        self.load_baselines()
        
        # Real-time metrics stream
        self.metrics_stream = deque(maxlen=1000)
        self.stream_listeners = []
    
    def load_baselines(self):
        """Load performance baselines from disk"""
        baseline_file = self.base_dir / 'baselines.json'
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                self.performance_baselines = json.load(f)
    
    def save_baselines(self):
        """Save performance baselines to disk"""
        baseline_file = self.base_dir / 'baselines.json'
        with open(baseline_file, 'w') as f:
            json.dump(self.performance_baselines, f, indent=2)
    
    def start_hook(
        self,
        hook_name: str,
        hook_type: str = 'prehook',
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start tracking a hook execution
        
        Args:
            hook_name: Name of the hook
            hook_type: Type of hook (prehook/posthook)
            context: Optional execution context
        
        Returns:
            Hook ID for tracking
        """
        # Generate hook ID
        hook_id = hashlib.md5(
            f"{hook_name}_{time.time()}_{threading.get_ident()}".encode()
        ).hexdigest()[:12]
        
        # Capture initial metrics
        process = psutil.Process()
        
        metrics = HookMetrics(
            hook_id=hook_id,
            hook_type=hook_type,
            name=hook_name,
            start_time=perf_counter_ns() / 1_000_000,
            cpu_percent_before=psutil.cpu_percent(interval=0.1),
            memory_mb_before=process.memory_info().rss / 1024 / 1024
        )
        
        # Add context if provided
        if context:
            metrics.task_id = context.get('task_id')
            metrics.agent_id = context.get('agent_id')
            metrics.parent_hook_id = context.get('parent_hook_id')
        
        # Store active hook
        self.active_hooks[hook_id] = metrics
        
        # Start trace if this is a root hook
        if not metrics.parent_hook_id:
            self.start_trace(hook_id, hook_name)
        
        # Emit to stream
        self.emit_metric('hook.started', {
            'hook_id': hook_id,
            'name': hook_name,
            'type': hook_type
        })
        
        return hook_id
    
    def end_hook(self, hook_id: str, success: bool = True, error: Optional[Exception] = None):
        """Complete tracking a hook execution
        
        Args:
            hook_id: Hook ID to complete
            success: Whether hook completed successfully
            error: Optional error if hook failed
        """
        if hook_id not in self.active_hooks:
            return
        
        metrics = self.active_hooks[hook_id]
        
        if success:
            metrics.complete()
        else:
            metrics.fail(error or Exception("Unknown error"))
        
        # Move to completed
        del self.active_hooks[hook_id]
        self.completed_hooks.append(metrics)
        
        # Update aggregated metrics
        self.update_summary(metrics)
        
        # Complete trace
        if hook_id in self.active_traces:
            trace = self.active_traces[hook_id]
            trace.finish()
            del self.active_traces[hook_id]
            self.completed_traces.append(trace)
        
        # Check for performance regression
        self.check_performance(metrics)
        
        # Emit to stream
        self.emit_metric('hook.completed', {
            'hook_id': hook_id,
            'name': metrics.name,
            'duration_ms': metrics.duration_ms,
            'status': metrics.status
        })
    
    def update_summary(self, metrics: HookMetrics):
        """Update aggregated metrics summary"""
        summary = self.metrics_summary[metrics.name]
        summary['count'] += 1
        
        if metrics.duration_ms:
            summary['total_duration_ms'] += metrics.duration_ms
            summary['avg_duration_ms'] = summary['total_duration_ms'] / summary['count']
            summary['min_duration_ms'] = min(summary['min_duration_ms'], metrics.duration_ms)
            summary['max_duration_ms'] = max(summary['max_duration_ms'], metrics.duration_ms)
        
        if metrics.status == 'failed':
            summary['error_count'] += 1
        
        summary['success_rate'] = (summary['count'] - summary['error_count']) / summary['count']
    
    def check_performance(self, metrics: HookMetrics):
        """Check for performance regressions against baselines"""
        if metrics.name not in self.performance_baselines:
            # Establish baseline
            self.performance_baselines[metrics.name] = {
                'avg_duration_ms': metrics.duration_ms,
                'memory_delta_mb': metrics.memory_delta_mb or 0
            }
            self.save_baselines()
            return
        
        baseline = self.performance_baselines[metrics.name]
        
        # Check for regression (>20% slower)
        if metrics.duration_ms and metrics.duration_ms > baseline['avg_duration_ms'] * 1.2:
            self.emit_metric('hook.performance.regression', {
                'hook_name': metrics.name,
                'duration_ms': metrics.duration_ms,
                'baseline_ms': baseline['avg_duration_ms'],
                'regression_percent': ((metrics.duration_ms / baseline['avg_duration_ms']) - 1) * 100
            })
    
    def start_trace(self, trace_id: str, operation_name: str) -> HookTrace:
        """Start a new trace"""
        trace = HookTrace(
            trace_id=trace_id,
            span_id=trace_id,
            operation_name=operation_name
        )
        self.active_traces[trace_id] = trace
        return trace
    
    def add_trace_log(self, trace_id: str, message: str, level: str = 'info'):
        """Add log to active trace"""
        if trace_id in self.active_traces:
            self.active_traces[trace_id].add_log(message, level)
    
    def emit_metric(self, metric_name: str, data: Dict[str, Any]):
        """Emit metric to stream and listeners"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'name': metric_name,
            'data': data
        }
        
        self.metrics_stream.append(metric)
        
        # Notify listeners
        for listener in self.stream_listeners:
            try:
                listener(metric)
            except Exception as e:
                print(f"Error notifying listener: {e}")
    
    def add_listener(self, callback):
        """Add a metrics stream listener"""
        self.stream_listeners.append(callback)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        return {
            'active_hooks': len(self.active_hooks),
            'completed_hooks': len(self.completed_hooks),
            'hook_summaries': dict(self.metrics_summary),
            'active_traces': len(self.active_traces),
            'performance_baselines': self.performance_baselines
        }
    
    def get_hook_timeline(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get timeline of recent hook executions"""
        timeline = []
        
        # Include active hooks
        for metrics in self.active_hooks.values():
            timeline.append({
                'hook_id': metrics.hook_id,
                'name': metrics.name,
                'type': metrics.hook_type,
                'start_time': metrics.start_time,
                'status': 'running',
                'agent_id': metrics.agent_id,
                'task_id': metrics.task_id
            })
        
        # Include recent completed hooks
        for metrics in list(self.completed_hooks)[-limit:]:
            timeline.append({
                'hook_id': metrics.hook_id,
                'name': metrics.name,
                'type': metrics.hook_type,
                'start_time': metrics.start_time,
                'end_time': metrics.end_time,
                'duration_ms': metrics.duration_ms,
                'status': metrics.status,
                'agent_id': metrics.agent_id,
                'task_id': metrics.task_id,
                'error': metrics.error
            })
        
        # Sort by start time
        timeline.sort(key=lambda x: x['start_time'], reverse=True)
        
        return timeline[:limit]
    
    def get_performance_report(self, hook_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate performance report for hooks"""
        if hook_name:
            if hook_name in self.metrics_summary:
                return {
                    'hook_name': hook_name,
                    'metrics': self.metrics_summary[hook_name],
                    'baseline': self.performance_baselines.get(hook_name)
                }
            return {}
        
        # Overall report
        total_hooks = sum(s['count'] for s in self.metrics_summary.values())
        total_duration = sum(s['total_duration_ms'] for s in self.metrics_summary.values())
        total_errors = sum(s['error_count'] for s in self.metrics_summary.values())
        
        return {
            'total_hooks_executed': total_hooks,
            'total_duration_ms': total_duration,
            'avg_duration_ms': total_duration / total_hooks if total_hooks > 0 else 0,
            'total_errors': total_errors,
            'overall_success_rate': (total_hooks - total_errors) / total_hooks if total_hooks > 0 else 0,
            'hook_summaries': dict(self.metrics_summary),
            'top_slowest_hooks': sorted(
                [(name, data['avg_duration_ms']) for name, data in self.metrics_summary.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'top_error_hooks': sorted(
                [(name, data['error_count']) for name, data in self.metrics_summary.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def export_traces(self, output_file: Optional[Path] = None) -> Path:
        """Export traces to JSON file"""
        output_file = output_file or self.base_dir / f"traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        traces_data = {
            'export_time': datetime.now().isoformat(),
            'traces': [trace.to_dict() for trace in self.completed_traces]
        }
        
        with open(output_file, 'w') as f:
            json.dump(traces_data, f, indent=2)
        
        return output_file
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        self.active_hooks.clear()
        self.completed_hooks.clear()
        self.active_traces.clear()
        self.completed_traces.clear()
        self.metrics_summary.clear()
        self.metrics_stream.clear()


# Global collector instance
_collector = None


def get_collector() -> HookTelemetryCollector:
    """Get or create global telemetry collector"""
    global _collector
    if _collector is None:
        _collector = HookTelemetryCollector()
    return _collector


# Decorator for automatic hook telemetry
def track_hook(hook_type: str = 'function'):
    """Decorator to automatically track function execution as a hook
    
    Args:
        hook_type: Type of hook to track as
    
    Example:
        @track_hook('api_call')
        def fetch_data():
            # Function implementation
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            collector = get_collector()
            hook_id = collector.start_hook(
                hook_name=func.__name__,
                hook_type=hook_type,
                context={'module': func.__module__}
            )
            
            try:
                result = func(*args, **kwargs)
                collector.end_hook(hook_id, success=True)
                return result
            except Exception as e:
                collector.end_hook(hook_id, success=False, error=e)
                raise
        
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Create collector
    collector = get_collector()
    
    # Simulate hook execution
    hook_id = collector.start_hook("test_hook", "prehook", {
        'task_id': 'task_123',
        'agent_id': 'agent_456'
    })
    
    # Simulate some work
    time.sleep(0.1)
    
    # Complete hook
    collector.end_hook(hook_id, success=True)
    
    # Get metrics
    print("Metrics Summary:")
    print(json.dumps(collector.get_metrics_summary(), indent=2))
    
    print("\nHook Timeline:")
    print(json.dumps(collector.get_hook_timeline(), indent=2))
    
    print("\nPerformance Report:")
    print(json.dumps(collector.get_performance_report(), indent=2))
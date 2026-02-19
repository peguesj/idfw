"""
Posthook reporting system with pattern recognition and reinforcement learning.
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .core import HookContext, MessageScope


class ExecutionStatus(Enum):
    """Execution status categories."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PENDING = "pending"


class PatternType(Enum):
    """Types of patterns that can be identified."""
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    OPTIMIZATION_PATTERN = "optimization_pattern"
    DEPENDENCY_PATTERN = "dependency_pattern"
    WORKFLOW_PATTERN = "workflow_pattern"
    ANTI_PATTERN = "anti_pattern"


@dataclass
class ExecutionMetrics:
    """Metrics from task/command execution."""
    execution_time: float
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    disk_io: Optional[float]
    network_io: Optional[float]
    error_count: int
    warning_count: int
    test_coverage: Optional[float]
    build_success: bool
    deployment_success: bool


@dataclass
class DependencyInfo:
    """Information about detected dependencies."""
    dependency_id: str
    dependency_type: str  # task, agent, command, resource
    dependency_name: str
    required: bool
    satisfied: bool
    satisfaction_time: Optional[datetime]
    blocking_factor: float  # How much this dependency blocks progress


@dataclass
class Pattern:
    """Identified pattern with metadata."""
    pattern_id: str
    pattern_type: PatternType
    pattern_name: str
    description: str
    confidence: float
    frequency: int
    success_rate: float
    context_markers: List[str]
    improvement_potential: float
    created_at: datetime
    last_seen: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value if isinstance(self.pattern_type, Enum) else str(self.pattern_type),
            'pattern_name': self.pattern_name,
            'description': self.description,
            'confidence': self.confidence,
            'frequency': self.frequency,
            'success_rate': self.success_rate,
            'context_markers': self.context_markers,
            'improvement_potential': self.improvement_potential,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            'last_seen': self.last_seen.isoformat() if isinstance(self.last_seen, datetime) else str(self.last_seen)
        }


@dataclass
class NextAction:
    """Recommended next action."""
    action_id: str
    action_type: str
    priority: int
    description: str
    estimated_effort: str
    confidence: float
    dependencies: List[str]
    context: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'action_id': self.action_id,
            'action_type': self.action_type,
            'priority': self.priority,
            'description': self.description,
            'estimated_effort': self.estimated_effort,
            'confidence': self.confidence,
            'dependencies': self.dependencies,
            'context': self.context
        }


@dataclass
class ExecutionReport:
    """Comprehensive execution report."""
    report_id: str
    execution_context: HookContext
    execution_status: ExecutionStatus
    start_time: datetime
    end_time: datetime
    execution_metrics: ExecutionMetrics
    detected_patterns: List[Pattern]
    dependencies: List[DependencyInfo]
    lessons_learned: List[str]
    next_actions: List[NextAction]
    reinforcement_data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'report_id': self.report_id,
            'execution_context': self.execution_context.to_dict(),
            'execution_status': self.execution_status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'execution_metrics': asdict(self.execution_metrics),
            'detected_patterns': [p.to_dict() for p in self.detected_patterns],
            'dependencies': [asdict(d) for d in self.dependencies],
            'lessons_learned': self.lessons_learned,
            'next_actions': [a.to_dict() for a in self.next_actions],
            'reinforcement_data': self.reinforcement_data,
            'metadata': self.metadata
        }


class PatternRecognizer:
    """Pattern recognition and analysis component."""
    
    def __init__(self):
        self.known_patterns: Dict[str, Pattern] = {}
        self.pattern_history: List[Pattern] = []
        
        # Pattern templates for common scenarios
        self.pattern_templates = {
            'build_failure_cycle': {
                'type': PatternType.FAILURE_PATTERN,
                'markers': ['build failed', 'typescript error', 'compilation error'],
                'description': 'Recurring build failures requiring similar fixes'
            },
            'dependency_installation': {
                'type': PatternType.WORKFLOW_PATTERN,
                'markers': ['npm install', 'package.json', 'dependencies'],
                'description': 'Standard dependency installation workflow'
            },
            'test_fix_cycle': {
                'type': PatternType.SUCCESS_PATTERN,
                'markers': ['test failed', 'test fixed', 'coverage improved'],
                'description': 'Successful test fixing and improvement cycle'
            },
            'optimization_opportunity': {
                'type': PatternType.OPTIMIZATION_PATTERN,
                'markers': ['slow', 'performance', 'optimize', 'refactor'],
                'description': 'Opportunities for performance optimization'
            }
        }
    
    def analyze_execution(
        self,
        context: HookContext,
        metrics: ExecutionMetrics,
        execution_log: str
    ) -> List[Pattern]:
        """Analyze execution to identify patterns."""
        
        detected_patterns = []
        
        # Check against known pattern templates
        for template_name, template in self.pattern_templates.items():
            pattern = self._match_pattern_template(
                template_name, template, context, metrics, execution_log
            )
            if pattern:
                detected_patterns.append(pattern)
        
        # Learn new patterns from execution
        new_patterns = self._learn_new_patterns(context, metrics, execution_log)
        detected_patterns.extend(new_patterns)
        
        # Update pattern statistics
        for pattern in detected_patterns:
            self._update_pattern_stats(pattern)
        
        return detected_patterns
    
    def _match_pattern_template(
        self,
        template_name: str,
        template: Dict[str, Any],
        context: HookContext,
        metrics: ExecutionMetrics,
        execution_log: str
    ) -> Optional[Pattern]:
        """Match execution against a pattern template."""
        
        # Check if markers are present
        marker_matches = 0
        for marker in template['markers']:
            if marker.lower() in execution_log.lower() or marker.lower() in context.message.lower():
                marker_matches += 1
        
        if marker_matches == 0:
            return None
        
        # Calculate confidence based on marker matches and execution success
        confidence = (marker_matches / len(template['markers'])) * 0.7
        
        # Adjust confidence based on execution outcome
        if metrics.build_success and template['type'] == PatternType.SUCCESS_PATTERN:
            confidence += 0.2
        elif not metrics.build_success and template['type'] == PatternType.FAILURE_PATTERN:
            confidence += 0.2
        
        # Get or create pattern
        pattern_id = f"{template_name}_{hash(execution_log) % 10000}"
        
        if pattern_id in self.known_patterns:
            pattern = self.known_patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
            pattern.confidence = max(pattern.confidence, confidence)
        else:
            pattern = Pattern(
                pattern_id=pattern_id,
                pattern_type=template['type'],
                pattern_name=template_name,
                description=template['description'],
                confidence=confidence,
                frequency=1,
                success_rate=1.0 if metrics.build_success else 0.0,
                context_markers=template['markers'],
                improvement_potential=self._calculate_improvement_potential(template, metrics),
                created_at=datetime.now(),
                last_seen=datetime.now()
            )
            self.known_patterns[pattern_id] = pattern
        
        return pattern
    
    def _learn_new_patterns(
        self,
        context: HookContext,
        metrics: ExecutionMetrics,
        execution_log: str
    ) -> List[Pattern]:
        """Learn new patterns from execution data."""
        
        # This would implement more sophisticated pattern learning
        # For now, basic heuristics
        
        new_patterns = []
        
        # Error pattern learning
        if metrics.error_count > 0:
            error_pattern = self._create_error_pattern(context, metrics, execution_log)
            if error_pattern:
                new_patterns.append(error_pattern)
        
        # Performance pattern learning
        if metrics.execution_time > 30:  # Long execution
            perf_pattern = self._create_performance_pattern(context, metrics, execution_log)
            if perf_pattern:
                new_patterns.append(perf_pattern)
        
        return new_patterns
    
    def _create_error_pattern(
        self,
        context: HookContext,
        metrics: ExecutionMetrics,
        execution_log: str
    ) -> Optional[Pattern]:
        """Create pattern from error conditions."""
        
        # Extract error keywords
        error_keywords = []
        if 'typescript' in execution_log.lower():
            error_keywords.append('typescript')
        if 'build' in execution_log.lower():
            error_keywords.append('build')
        if 'test' in execution_log.lower():
            error_keywords.append('test')
        
        if not error_keywords:
            return None
        
        pattern_name = f"error_{'_'.join(error_keywords)}"
        pattern_id = f"{pattern_name}_{hash(execution_log) % 10000}"
        
        return Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.FAILURE_PATTERN,
            pattern_name=pattern_name,
            description=f"Error pattern involving {', '.join(error_keywords)}",
            confidence=0.6,
            frequency=1,
            success_rate=0.0,
            context_markers=error_keywords,
            improvement_potential=0.8,
            created_at=datetime.now(),
            last_seen=datetime.now()
        )
    
    def _create_performance_pattern(
        self,
        context: HookContext,
        metrics: ExecutionMetrics,
        execution_log: str
    ) -> Optional[Pattern]:
        """Create pattern from performance issues."""
        
        pattern_id = f"performance_slow_{hash(execution_log) % 10000}"
        
        return Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.OPTIMIZATION_PATTERN,
            pattern_name="slow_execution",
            description=f"Slow execution taking {metrics.execution_time:.1f}s",
            confidence=0.7,
            frequency=1,
            success_rate=0.5,
            context_markers=['slow', 'performance'],
            improvement_potential=0.9,
            created_at=datetime.now(),
            last_seen=datetime.now()
        )
    
    def _calculate_improvement_potential(
        self,
        template: Dict[str, Any],
        metrics: ExecutionMetrics
    ) -> float:
        """Calculate improvement potential for a pattern."""
        
        base_potential = 0.5
        
        # Higher potential for failure patterns
        if template['type'] == PatternType.FAILURE_PATTERN:
            base_potential += 0.3
        
        # Higher potential for optimization patterns
        if template['type'] == PatternType.OPTIMIZATION_PATTERN:
            base_potential += 0.2
        
        # Adjust based on execution metrics
        if metrics.error_count > 0:
            base_potential += 0.2
        
        if metrics.execution_time > 30:
            base_potential += 0.1
        
        return min(1.0, base_potential)
    
    def _update_pattern_stats(self, pattern: Pattern):
        """Update statistics for a pattern."""
        # This would update success rates, frequency, etc.
        # Implementation would track historical data
        pass
    
    def get_pattern_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations based on identified patterns."""
        
        recommendations = []
        
        # Sort patterns by improvement potential
        sorted_patterns = sorted(
            self.known_patterns.values(),
            key=lambda p: p.improvement_potential * p.frequency,
            reverse=True
        )
        
        for pattern in sorted_patterns[:5]:  # Top 5
            if pattern.improvement_potential > 0.6:
                recommendations.append({
                    'pattern_name': pattern.pattern_name,
                    'description': pattern.description,
                    'improvement_potential': pattern.improvement_potential,
                    'frequency': pattern.frequency,
                    'recommendation': self._generate_recommendation(pattern)
                })
        
        return recommendations
    
    def _generate_recommendation(self, pattern: Pattern) -> str:
        """Generate recommendation for a pattern."""
        
        if pattern.pattern_type == PatternType.FAILURE_PATTERN:
            return f"Consider implementing automated checks for {pattern.pattern_name} to prevent recurrence"
        elif pattern.pattern_type == PatternType.OPTIMIZATION_PATTERN:
            return f"Optimize {pattern.pattern_name} to improve performance"
        elif pattern.pattern_type == PatternType.SUCCESS_PATTERN:
            return f"Replicate {pattern.pattern_name} success pattern in similar contexts"
        else:
            return f"Monitor {pattern.pattern_name} for further optimization opportunities"


class DependencyDetector:
    """Automatic dependency detection and tracking."""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.dependency_cache: Dict[str, DependencyInfo] = {}
    
    def detect_dependencies(
        self,
        context: HookContext,
        execution_log: str
    ) -> List[DependencyInfo]:
        """Detect dependencies from execution context and logs."""
        
        dependencies = []
        
        # File dependencies
        file_deps = self._detect_file_dependencies(context, execution_log)
        dependencies.extend(file_deps)
        
        # Package dependencies
        package_deps = self._detect_package_dependencies(context, execution_log)
        dependencies.extend(package_deps)
        
        # Service dependencies
        service_deps = self._detect_service_dependencies(context, execution_log)
        dependencies.extend(service_deps)
        
        # Task dependencies
        task_deps = self._detect_task_dependencies(context, execution_log)
        dependencies.extend(task_deps)
        
        return dependencies
    
    def _detect_file_dependencies(
        self,
        context: HookContext,
        execution_log: str
    ) -> List[DependencyInfo]:
        """Detect file-based dependencies."""
        
        dependencies = []
        
        # Look for file references in logs
        import re
        file_patterns = [
            r'\.\/[a-zA-Z0-9_\/\-\.]+',
            r'[a-zA-Z0-9_\/\-\.]+\.py',
            r'[a-zA-Z0-9_\/\-\.]+\.ts',
            r'[a-zA-Z0-9_\/\-\.]+\.js',
            r'[a-zA-Z0-9_\/\-\.]+\.json'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, execution_log)
            for match in matches:
                if match not in [d.dependency_name for d in dependencies]:
                    dependencies.append(DependencyInfo(
                        dependency_id=str(uuid.uuid4()),
                        dependency_type='file',
                        dependency_name=match,
                        required=True,
                        satisfied=True,  # Assume satisfied if referenced
                        satisfaction_time=datetime.now(),
                        blocking_factor=0.3
                    ))
        
        return dependencies
    
    def _detect_package_dependencies(
        self,
        context: HookContext,
        execution_log: str
    ) -> List[DependencyInfo]:
        """Detect package dependencies."""
        
        dependencies = []
        
        # Look for package references
        if 'npm install' in execution_log or 'package.json' in execution_log:
            dependencies.append(DependencyInfo(
                dependency_id=str(uuid.uuid4()),
                dependency_type='package',
                dependency_name='npm_packages',
                required=True,
                satisfied='successfully installed' in execution_log.lower(),
                satisfaction_time=datetime.now() if 'successfully installed' in execution_log.lower() else None,
                blocking_factor=0.8
            ))
        
        if 'pip install' in execution_log or 'requirements.txt' in execution_log:
            dependencies.append(DependencyInfo(
                dependency_id=str(uuid.uuid4()),
                dependency_type='package',
                dependency_name='python_packages',
                required=True,
                satisfied='successfully installed' in execution_log.lower(),
                satisfaction_time=datetime.now() if 'successfully installed' in execution_log.lower() else None,
                blocking_factor=0.8
            ))
        
        return dependencies
    
    def _detect_service_dependencies(
        self,
        context: HookContext,
        execution_log: str
    ) -> List[DependencyInfo]:
        """Detect service dependencies."""
        
        dependencies = []
        
        services = ['docker', 'database', 'redis', 'api', 'server']
        
        for service in services:
            if service in execution_log.lower():
                dependencies.append(DependencyInfo(
                    dependency_id=str(uuid.uuid4()),
                    dependency_type='service',
                    dependency_name=service,
                    required=True,
                    satisfied='running' in execution_log.lower() or 'started' in execution_log.lower(),
                    satisfaction_time=datetime.now() if 'running' in execution_log.lower() else None,
                    blocking_factor=0.9
                ))
        
        return dependencies
    
    def _detect_task_dependencies(
        self,
        context: HookContext,
        execution_log: str
    ) -> List[DependencyInfo]:
        """Detect task dependencies."""
        
        dependencies = []
        
        # Look for task references
        task_keywords = ['after', 'before', 'requires', 'depends on', 'needs']
        
        for keyword in task_keywords:
            if keyword in context.message.lower():
                dependencies.append(DependencyInfo(
                    dependency_id=str(uuid.uuid4()),
                    dependency_type='task',
                    dependency_name=f'task_dependency_{keyword}',
                    required=True,
                    satisfied=False,  # Would need to check actual task status
                    satisfaction_time=None,
                    blocking_factor=0.7
                ))
        
        return dependencies


class NextActionGenerator:
    """Generate intelligent next action recommendations."""
    
    def __init__(self):
        self.action_templates = {
            'fix_build_errors': {
                'priority': 1,
                'effort': 'medium',
                'description': 'Fix build errors to enable continued development'
            },
            'run_tests': {
                'priority': 2,
                'effort': 'low',
                'description': 'Run tests to verify functionality'
            },
            'update_dependencies': {
                'priority': 3,
                'effort': 'low',
                'description': 'Update package dependencies'
            },
            'optimize_performance': {
                'priority': 4,
                'effort': 'high',
                'description': 'Optimize performance bottlenecks'
            },
            'improve_documentation': {
                'priority': 5,
                'effort': 'medium',
                'description': 'Improve code documentation'
            }
        }
    
    def generate_next_actions(
        self,
        context: HookContext,
        patterns: List[Pattern],
        dependencies: List[DependencyInfo],
        execution_status: ExecutionStatus
    ) -> List[NextAction]:
        """Generate next action recommendations."""
        
        actions = []
        
        # Actions based on execution status
        if execution_status == ExecutionStatus.FAILURE:
            actions.extend(self._generate_failure_actions(context, patterns))
        elif execution_status == ExecutionStatus.PARTIAL_SUCCESS:
            actions.extend(self._generate_partial_success_actions(context, patterns))
        elif execution_status == ExecutionStatus.SUCCESS:
            actions.extend(self._generate_success_actions(context, patterns))
        
        # Actions based on dependencies
        actions.extend(self._generate_dependency_actions(dependencies))
        
        # Actions based on patterns
        actions.extend(self._generate_pattern_actions(patterns))
        
        # Sort by priority and return top actions
        actions.sort(key=lambda a: a.priority)
        return actions[:10]  # Top 10 actions
    
    def _generate_failure_actions(
        self,
        context: HookContext,
        patterns: List[Pattern]
    ) -> List[NextAction]:
        """Generate actions for failure scenarios."""
        
        actions = []
        
        # Always recommend investigating errors
        actions.append(NextAction(
            action_id=str(uuid.uuid4()),
            action_type='investigation',
            priority=1,
            description='Investigate and fix execution errors',
            estimated_effort='medium',
            confidence=0.9,
            dependencies=[],
            context={'scope': context.scope.value}
        ))
        
        # Check for build errors
        if 'build' in context.message.lower():
            actions.append(NextAction(
                action_id=str(uuid.uuid4()),
                action_type='fix',
                priority=1,
                description='Fix build errors',
                estimated_effort='medium',
                confidence=0.8,
                dependencies=[],
                context={'type': 'build_fix'}
            ))
        
        return actions
    
    def _generate_partial_success_actions(
        self,
        context: HookContext,
        patterns: List[Pattern]
    ) -> List[NextAction]:
        """Generate actions for partial success scenarios."""
        
        actions = []
        
        actions.append(NextAction(
            action_id=str(uuid.uuid4()),
            action_type='completion',
            priority=2,
            description='Complete remaining tasks',
            estimated_effort='medium',
            confidence=0.7,
            dependencies=[],
            context={'scope': context.scope.value}
        ))
        
        return actions
    
    def _generate_success_actions(
        self,
        context: HookContext,
        patterns: List[Pattern]
    ) -> List[NextAction]:
        """Generate actions for success scenarios."""
        
        actions = []
        
        # Suggest optimization or next features
        actions.append(NextAction(
            action_id=str(uuid.uuid4()),
            action_type='optimization',
            priority=4,
            description='Consider optimizations or next features',
            estimated_effort='variable',
            confidence=0.6,
            dependencies=[],
            context={'scope': context.scope.value}
        ))
        
        return actions
    
    def _generate_dependency_actions(
        self,
        dependencies: List[DependencyInfo]
    ) -> List[NextAction]:
        """Generate actions based on dependencies."""
        
        actions = []
        
        unsatisfied_deps = [d for d in dependencies if not d.satisfied]
        
        for dep in unsatisfied_deps:
            actions.append(NextAction(
                action_id=str(uuid.uuid4()),
                action_type='dependency_resolution',
                priority=int(dep.blocking_factor * 10),
                description=f'Resolve {dep.dependency_type} dependency: {dep.dependency_name}',
                estimated_effort='low' if dep.dependency_type == 'package' else 'medium',
                confidence=0.8,
                dependencies=[dep.dependency_id],
                context={'dependency_type': dep.dependency_type}
            ))
        
        return actions
    
    def _generate_pattern_actions(
        self,
        patterns: List[Pattern]
    ) -> List[NextAction]:
        """Generate actions based on identified patterns."""
        
        actions = []
        
        for pattern in patterns:
            if pattern.improvement_potential > 0.7:
                actions.append(NextAction(
                    action_id=str(uuid.uuid4()),
                    action_type='pattern_optimization',
                    priority=5,
                    description=f'Address pattern: {pattern.pattern_name}',
                    estimated_effort='medium',
                    confidence=pattern.confidence,
                    dependencies=[],
                    context={'pattern_id': pattern.pattern_id}
                ))
        
        return actions


class PosthookProcessor:
    """Main posthook processor coordinating all components."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.claude' / 'hooks' / 'reports'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.pattern_recognizer = PatternRecognizer()
        self.dependency_detector = DependencyDetector()
        self.action_generator = NextActionGenerator()
        
        # Execution tracking
        self.active_executions: Dict[str, datetime] = {}
        self.execution_history: List[ExecutionReport] = []
    
    def start_execution_tracking(self, context: HookContext) -> str:
        """Start tracking an execution."""
        execution_id = str(uuid.uuid4())
        self.active_executions[execution_id] = datetime.now()
        return execution_id

    def process_tool_result(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_result: Dict[str, Any],
        execution_time: float,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simplified synchronous interface for processing tool results.

        This is a convenience method for hook scripts that don't need
        full async execution reporting.
        """
        import asyncio

        # Create a basic HookContext
        from .core import HookContext, HookType, MessageScope
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.POST_TOOL_USE,
            timestamp=datetime.now(),
            scope=MessageScope.SYSTEM,
            message=f"Tool {tool_name} executed",
            metadata={'tool_name': tool_name, 'tool_args': tool_args, 'tool_result': tool_result}
        )

        # Start tracking
        execution_id = self.start_execution_tracking(hook_context)

        # Determine execution status
        success = tool_result.get('success', True)
        execution_status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILURE

        # Create execution log
        execution_log = f"Tool: {tool_name}\nExecution time: {execution_time}s\nResult: {tool_result}"

        # Create metrics
        metrics = ExecutionMetrics(
            execution_time=execution_time,
            cpu_usage=None,
            memory_usage=None,
            disk_io=None,
            network_io=None,
            error_count=1 if not success else 0,
            warning_count=0,
            test_coverage=None,
            build_success=success,
            deployment_success=success
        )

        # Process execution completion (run async function in sync context)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            report = loop.run_until_complete(
                self.process_execution_completion(
                    execution_id,
                    hook_context,
                    execution_status,
                    execution_log,
                    metrics
                )
            )

            return {
                'success': True,
                'execution_id': execution_id,
                'patterns': [p.to_dict() for p in report.detected_patterns],
                'lessons_learned': report.lessons_learned,
                'next_actions': [a.to_dict() for a in report.next_actions],
                'reinforcement_data': report.reinforcement_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_id': execution_id
            }
    
    async def process_execution_completion(
        self,
        execution_id: str,
        context: HookContext,
        execution_status: ExecutionStatus,
        execution_log: str,
        metrics: Optional[ExecutionMetrics] = None
    ) -> ExecutionReport:
        """Process completion of an execution."""
        
        start_time = self.active_executions.get(execution_id, datetime.now())
        end_time = datetime.now()
        
        # Default metrics if not provided
        if metrics is None:
            metrics = ExecutionMetrics(
                execution_time=(end_time - start_time).total_seconds(),
                cpu_usage=None,
                memory_usage=None,
                disk_io=None,
                network_io=None,
                error_count=execution_log.lower().count('error'),
                warning_count=execution_log.lower().count('warning'),
                test_coverage=None,
                build_success='success' in execution_status.value,
                deployment_success='success' in execution_status.value
            )
        
        # Pattern recognition
        detected_patterns = self.pattern_recognizer.analyze_execution(
            context, metrics, execution_log
        )
        
        # Dependency detection
        dependencies = self.dependency_detector.detect_dependencies(
            context, execution_log
        )
        
        # Generate next actions
        next_actions = self.action_generator.generate_next_actions(
            context, detected_patterns, dependencies, execution_status
        )
        
        # Extract lessons learned
        lessons_learned = self._extract_lessons_learned(
            context, metrics, execution_log, detected_patterns
        )
        
        # Create reinforcement data
        reinforcement_data = self._create_reinforcement_data(
            context, metrics, execution_status, detected_patterns
        )
        
        # Create execution report
        report = ExecutionReport(
            report_id=str(uuid.uuid4()),
            execution_context=context,
            execution_status=execution_status,
            start_time=start_time,
            end_time=end_time,
            execution_metrics=metrics,
            detected_patterns=detected_patterns,
            dependencies=dependencies,
            lessons_learned=lessons_learned,
            next_actions=next_actions,
            reinforcement_data=reinforcement_data,
            metadata={'execution_id': execution_id}
        )
        
        # Store report
        await self._store_execution_report(report)
        
        # Clean up tracking
        if execution_id in self.active_executions:
            del self.active_executions[execution_id]
        
        # Add to history
        self.execution_history.append(report)
        
        return report
    
    def _extract_lessons_learned(
        self,
        context: HookContext,
        metrics: ExecutionMetrics,
        execution_log: str,
        patterns: List[Pattern]
    ) -> List[str]:
        """Extract lessons learned from execution."""
        
        lessons = []
        
        # Performance lessons
        if metrics.execution_time > 30:
            lessons.append(f"Execution took {metrics.execution_time:.1f}s - consider optimization")
        
        # Error lessons
        if metrics.error_count > 0:
            lessons.append(f"Encountered {metrics.error_count} errors - review error handling")
        
        # Pattern lessons
        for pattern in patterns:
            if pattern.pattern_type == PatternType.FAILURE_PATTERN:
                lessons.append(f"Identified failure pattern: {pattern.pattern_name}")
            elif pattern.pattern_type == PatternType.SUCCESS_PATTERN:
                lessons.append(f"Successful pattern: {pattern.pattern_name} - replicate in similar contexts")
        
        # Build lessons
        if not metrics.build_success:
            lessons.append("Build failed - ensure all dependencies are resolved")
        
        return lessons
    
    def _create_reinforcement_data(
        self,
        context: HookContext,
        metrics: ExecutionMetrics,
        status: ExecutionStatus,
        patterns: List[Pattern]
    ) -> Dict[str, Any]:
        """Create reinforcement learning data."""
        
        return {
            'success_score': 1.0 if status == ExecutionStatus.SUCCESS else 0.0,
            'efficiency_score': max(0.0, 1.0 - (metrics.execution_time / 60)),  # Normalize to 1 minute
            'quality_score': 1.0 - (metrics.error_count * 0.1),
            'pattern_confidence': sum(p.confidence for p in patterns) / len(patterns) if patterns else 0.0,
            'context_features': {
                'scope': context.scope.value,
                'message_length': len(context.message),
                'has_metadata': bool(context.metadata)
            },
            'outcome_features': {
                'execution_time': metrics.execution_time,
                'error_count': metrics.error_count,
                'warning_count': metrics.warning_count,
                'build_success': metrics.build_success
            }
        }
    
    async def _store_execution_report(self, report: ExecutionReport):
        """Store execution report to disk."""
        timestamp = report.start_time
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Create daily storage file
        daily_file = self.storage_path / f'reports_{date_str}.jsonl'
        
        # Append to file
        with open(daily_file, 'a') as f:
            f.write(json.dumps(report.to_dict()) + '\n')
    
    def get_performance_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get performance analytics for the last N days."""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_reports = [
            r for r in self.execution_history
            if r.start_time >= cutoff_date
        ]
        
        if not recent_reports:
            return {'total_executions': 0}
        
        total = len(recent_reports)
        successful = sum(1 for r in recent_reports if r.execution_status == ExecutionStatus.SUCCESS)
        
        avg_execution_time = sum(r.execution_metrics.execution_time for r in recent_reports) / total
        avg_error_count = sum(r.execution_metrics.error_count for r in recent_reports) / total
        
        # Pattern analysis
        all_patterns = []
        for report in recent_reports:
            all_patterns.extend(report.detected_patterns)
        
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern.pattern_name] = pattern_counts.get(pattern.pattern_name, 0) + 1
        
        return {
            'total_executions': total,
            'success_rate': successful / total,
            'average_execution_time': avg_execution_time,
            'average_error_count': avg_error_count,
            'top_patterns': sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'improvement_opportunities': self.pattern_recognizer.get_pattern_recommendations()
        }
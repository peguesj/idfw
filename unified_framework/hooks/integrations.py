"""
Hook integration points for existing systems (Todo, Agent, IDE, Linear, MCP).
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from .core import HookContext, HookType, MessageScope, get_hook_system
from .prehook import PrehookProcessor
from .posthook import PosthookProcessor, ExecutionStatus, ExecutionMetrics
from .link_catalog import LinkCatalogHook
from .vector_rag import VectorRAGSystem
from .security import SecurityFramework, SecurityLevel


@dataclass
class IntegrationEvent:
    """Event for system integrations."""
    event_id: str
    event_type: str
    source_system: str
    target_system: str
    timestamp: datetime
    data: Dict[str, Any]
    context: Optional[HookContext] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TodoSystemIntegration:
    """Integration with TodoWrite system."""
    
    def __init__(self, hooks_system):
        self.hooks_system = hooks_system
        self.todo_contexts: Dict[str, Dict[str, Any]] = {}
        self.completion_patterns: Dict[str, float] = {}
    
    async def on_todo_created(self, todo_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle todo creation event."""
        
        # Store todo context for pattern learning
        todo_id = todo_data.get('id', str(uuid.uuid4()))
        self.todo_contexts[todo_id] = {
            'created_at': datetime.now().isoformat(),
            'content': todo_data.get('content', ''),
            'priority': self._assess_priority(todo_data.get('content', '')),
            'complexity': self._assess_complexity(todo_data.get('content', '')),
            'estimated_effort': self._estimate_effort(todo_data.get('content', '')),
            'context': context.to_dict()
        }
        
        # Process through hooks
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.CONTEXT_HOOK,
            timestamp=datetime.now(),
            scope=MessageScope.TASK,
            message=f"Todo created: {todo_data.get('content', '')}",
            metadata={'todo_data': todo_data, 'integration': 'todo_system'},
            task_id=todo_id
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.TASK,
            hook_context.metadata
        )
        
        return {
            'todo_id': todo_id,
            'processing_result': result,
            'priority_assessment': self.todo_contexts[todo_id]['priority'],
            'complexity_assessment': self.todo_contexts[todo_id]['complexity']
        }
    
    async def on_todo_completed(
        self,
        todo_id: str,
        completion_data: Dict[str, Any],
        context: HookContext
    ) -> Dict[str, Any]:
        """Handle todo completion event."""
        
        if todo_id not in self.todo_contexts:
            return {'error': 'Todo context not found'}
        
        todo_context = self.todo_contexts[todo_id]
        
        # Calculate completion metrics
        created_at = datetime.fromisoformat(todo_context['created_at'])
        completion_time = (datetime.now() - created_at).total_seconds()
        
        # Update completion patterns
        content = todo_context['content']
        success_rate = self.completion_patterns.get(content, 0.5)
        
        if completion_data.get('success', True):
            # Successful completion - increase success rate
            self.completion_patterns[content] = min(1.0, success_rate + 0.1)
        else:
            # Failed completion - decrease success rate
            self.completion_patterns[content] = max(0.0, success_rate - 0.1)
        
        # Create execution metrics
        execution_metrics = ExecutionMetrics(
            execution_time=completion_time,
            cpu_usage=None,
            memory_usage=None,
            disk_io=None,
            network_io=None,
            error_count=completion_data.get('error_count', 0),
            warning_count=completion_data.get('warning_count', 0),
            test_coverage=completion_data.get('test_coverage'),
            build_success=completion_data.get('build_success', True),
            deployment_success=completion_data.get('deployment_success', True)
        )
        
        # Process through posthook
        execution_status = ExecutionStatus.SUCCESS if completion_data.get('success', True) else ExecutionStatus.FAILURE
        
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.POSTHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.TASK,
            message=f"Todo completed: {content}",
            metadata={'completion_data': completion_data, 'integration': 'todo_system'},
            task_id=todo_id
        )
        
        # Process through posthook system
        posthook_processor = PosthookProcessor()
        execution_id = posthook_processor.start_execution_tracking(hook_context)
        
        execution_report = await posthook_processor.process_execution_completion(
            execution_id,
            hook_context,
            execution_status,
            json.dumps(completion_data),
            execution_metrics
        )
        
        return {
            'todo_id': todo_id,
            'completion_time': completion_time,
            'success_rate': self.completion_patterns[content],
            'execution_report': execution_report.to_dict(),
            'lessons_learned': execution_report.lessons_learned,
            'next_actions': [action.description for action in execution_report.next_actions]
        }
    
    def _assess_priority(self, content: str) -> float:
        """Assess todo priority based on content."""
        high_priority_keywords = ['urgent', 'critical', 'asap', 'immediately', 'fix', 'bug', 'error']
        medium_priority_keywords = ['important', 'should', 'update', 'improve', 'optimize']
        
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in high_priority_keywords):
            return 0.8
        elif any(keyword in content_lower for keyword in medium_priority_keywords):
            return 0.6
        else:
            return 0.4
    
    def _assess_complexity(self, content: str) -> float:
        """Assess todo complexity based on content."""
        complex_keywords = ['integrate', 'system', 'architecture', 'framework', 'complex', 'multiple']
        simple_keywords = ['add', 'remove', 'update', 'fix', 'simple']
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        complexity = 0.5  # Base complexity
        
        if any(keyword in content_lower for keyword in complex_keywords):
            complexity += 0.3
        if any(keyword in content_lower for keyword in simple_keywords):
            complexity -= 0.2
        
        # Adjust based on length
        if word_count > 20:
            complexity += 0.2
        elif word_count < 5:
            complexity -= 0.1
        
        return max(0.1, min(1.0, complexity))
    
    def _estimate_effort(self, content: str) -> str:
        """Estimate effort required for todo."""
        complexity = self._assess_complexity(content)
        
        if complexity > 0.7:
            return 'high'
        elif complexity > 0.4:
            return 'medium'
        else:
            return 'low'


class AgentSystemIntegration:
    """Integration with agent orchestration system."""
    
    def __init__(self, hooks_system):
        self.hooks_system = hooks_system
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
        self.task_distributions: Dict[str, List[str]] = {}
    
    async def on_agent_deployed(self, agent_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle agent deployment event."""
        
        agent_id = agent_data.get('agent_id', str(uuid.uuid4()))
        
        # Initialize performance tracking
        self.agent_performance[agent_id] = {
            'deployed_at': datetime.now().isoformat(),
            'task_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'average_execution_time': 0.0,
            'specialization': agent_data.get('specialization', 'general')
        }
        
        # Process through hooks
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.CONTEXT_HOOK,
            timestamp=datetime.now(),
            scope=MessageScope.AGENT,
            message=f"Agent deployed: {agent_data.get('name', agent_id)}",
            metadata={'agent_data': agent_data, 'integration': 'agent_system'},
            user_id=context.user_id
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.AGENT,
            hook_context.metadata
        )
        
        return {
            'agent_id': agent_id,
            'deployment_result': result,
            'performance_tracking_initialized': True
        }
    
    async def on_agent_task_completed(
        self,
        agent_id: str,
        task_data: Dict[str, Any],
        context: HookContext
    ) -> Dict[str, Any]:
        """Handle agent task completion."""
        
        if agent_id not in self.agent_performance:
            return {'error': 'Agent performance data not found'}
        
        perf_data = self.agent_performance[agent_id]
        
        # Update performance metrics
        perf_data['task_count'] += 1
        
        if task_data.get('success', True):
            perf_data['success_count'] += 1
        else:
            perf_data['failure_count'] += 1
        
        # Update average execution time
        execution_time = task_data.get('execution_time', 0)
        current_avg = perf_data['average_execution_time']
        task_count = perf_data['task_count']
        
        perf_data['average_execution_time'] = (
            (current_avg * (task_count - 1) + execution_time) / task_count
        )
        
        # Process through hooks for pattern learning
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.POSTHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.AGENT,
            message=f"Agent {agent_id} completed task: {task_data.get('task_name', 'unknown')}",
            metadata={'task_data': task_data, 'agent_id': agent_id, 'integration': 'agent_system'}
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.AGENT,
            hook_context.metadata
        )
        
        # Calculate agent effectiveness
        success_rate = perf_data['success_count'] / perf_data['task_count']
        effectiveness_score = success_rate * (1 / max(1, perf_data['average_execution_time'] / 60))
        
        return {
            'agent_id': agent_id,
            'task_processing_result': result,
            'performance_update': perf_data,
            'success_rate': success_rate,
            'effectiveness_score': effectiveness_score
        }
    
    def optimize_task_distribution(self) -> Dict[str, Any]:
        """Optimize task distribution based on agent performance."""
        
        recommendations = {}
        
        for agent_id, perf_data in self.agent_performance.items():
            if perf_data['task_count'] > 5:  # Enough data for analysis
                success_rate = perf_data['success_count'] / perf_data['task_count']
                avg_time = perf_data['average_execution_time']
                specialization = perf_data['specialization']
                
                if success_rate > 0.8 and avg_time < 120:  # High performer
                    recommendations[agent_id] = {
                        'recommendation': 'increase_task_allocation',
                        'confidence': 0.9,
                        'reason': 'High success rate and fast execution'
                    }
                elif success_rate < 0.5:  # Poor performer
                    recommendations[agent_id] = {
                        'recommendation': 'reduce_task_allocation',
                        'confidence': 0.8,
                        'reason': 'Low success rate'
                    }
                elif avg_time > 300:  # Slow performer
                    recommendations[agent_id] = {
                        'recommendation': 'optimize_or_retrain',
                        'confidence': 0.7,
                        'reason': 'Slow execution time'
                    }
        
        return {
            'optimization_recommendations': recommendations,
            'total_agents_analyzed': len(self.agent_performance)
        }


class IDEIntegration:
    """Integration with IDE context and diagnostics."""
    
    def __init__(self, hooks_system):
        self.hooks_system = hooks_system
        self.diagnostic_history: List[Dict[str, Any]] = []
        self.code_quality_trends: Dict[str, List[float]] = {}
    
    async def on_diagnostic_update(self, diagnostic_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle IDE diagnostic updates."""
        
        # Store diagnostic history
        diagnostic_entry = {
            'timestamp': datetime.now().isoformat(),
            'file_uri': diagnostic_data.get('uri', ''),
            'diagnostics': diagnostic_data.get('diagnostics', []),
            'error_count': len([d for d in diagnostic_data.get('diagnostics', []) if d.get('severity') == 1]),
            'warning_count': len([d for d in diagnostic_data.get('diagnostics', []) if d.get('severity') == 2])
        }
        
        self.diagnostic_history.append(diagnostic_entry)
        
        # Keep only recent history
        if len(self.diagnostic_history) > 1000:
            self.diagnostic_history = self.diagnostic_history[-1000:]
        
        # Update quality trends
        file_uri = diagnostic_entry['file_uri']
        if file_uri not in self.code_quality_trends:
            self.code_quality_trends[file_uri] = []
        
        # Calculate quality score (0-100, higher is better)
        error_count = diagnostic_entry['error_count']
        warning_count = diagnostic_entry['warning_count']
        quality_score = max(0, 100 - (error_count * 10) - (warning_count * 2))
        
        self.code_quality_trends[file_uri].append(quality_score)
        
        # Keep only recent trends
        if len(self.code_quality_trends[file_uri]) > 50:
            self.code_quality_trends[file_uri] = self.code_quality_trends[file_uri][-50:]
        
        # Process through hooks
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.CONTEXT_HOOK,
            timestamp=datetime.now(),
            scope=MessageScope.SYSTEM,
            message=f"IDE diagnostics updated for {file_uri}: {error_count} errors, {warning_count} warnings",
            metadata={'diagnostic_data': diagnostic_data, 'integration': 'ide_system'}
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.SYSTEM,
            hook_context.metadata
        )
        
        return {
            'diagnostic_processed': True,
            'quality_score': quality_score,
            'quality_trend': self._calculate_trend(self.code_quality_trends[file_uri]),
            'hook_processing_result': result
        }
    
    async def on_code_execution(self, execution_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle code execution events."""
        
        # Process through hooks
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.POST_TOOL_USE,
            timestamp=datetime.now(),
            scope=MessageScope.SYSTEM,
            message=f"Code executed: {execution_data.get('code', '')[:100]}...",
            metadata={'execution_data': execution_data, 'integration': 'ide_system'}
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.SYSTEM,
            hook_context.metadata
        )
        
        return {
            'execution_processed': True,
            'hook_processing_result': result
        }
    
    def _calculate_trend(self, quality_scores: List[float]) -> str:
        """Calculate quality trend direction."""
        if len(quality_scores) < 3:
            return 'insufficient_data'
        
        recent_avg = sum(quality_scores[-3:]) / 3
        older_avg = sum(quality_scores[-6:-3]) / 3 if len(quality_scores) >= 6 else sum(quality_scores[:-3]) / len(quality_scores[:-3])
        
        if recent_avg > older_avg + 5:
            return 'improving'
        elif recent_avg < older_avg - 5:
            return 'declining'
        else:
            return 'stable'
    
    def get_quality_insights(self) -> Dict[str, Any]:
        """Get code quality insights."""
        
        if not self.diagnostic_history:
            return {'total_files': 0}
        
        # Overall statistics
        total_errors = sum(entry['error_count'] for entry in self.diagnostic_history)
        total_warnings = sum(entry['warning_count'] for entry in self.diagnostic_history)
        
        # File-specific insights
        file_insights = {}
        for file_uri, scores in self.code_quality_trends.items():
            if scores:
                file_insights[file_uri] = {
                    'current_quality': scores[-1],
                    'average_quality': sum(scores) / len(scores),
                    'trend': self._calculate_trend(scores),
                    'sample_count': len(scores)
                }
        
        return {
            'total_files': len(self.code_quality_trends),
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'file_insights': file_insights,
            'overall_trend': self._calculate_overall_trend()
        }
    
    def _calculate_overall_trend(self) -> str:
        """Calculate overall code quality trend."""
        trends = [self._calculate_trend(scores) for scores in self.code_quality_trends.values()]
        
        improving_count = trends.count('improving')
        declining_count = trends.count('declining')
        
        if improving_count > declining_count:
            return 'improving'
        elif declining_count > improving_count:
            return 'declining'
        else:
            return 'stable'


class LinearIntegration:
    """Integration with Linear issue tracking."""
    
    def __init__(self, hooks_system):
        self.hooks_system = hooks_system
        self.issue_contexts: Dict[str, Dict[str, Any]] = {}
        self.project_metrics: Dict[str, Dict[str, Any]] = {}
    
    async def on_issue_created(self, issue_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle Linear issue creation."""
        
        issue_id = issue_data.get('id', str(uuid.uuid4()))
        
        # Store issue context
        self.issue_contexts[issue_id] = {
            'created_at': datetime.now().isoformat(),
            'title': issue_data.get('title', ''),
            'description': issue_data.get('description', ''),
            'priority': issue_data.get('priority', 'medium'),
            'project_id': issue_data.get('projectId'),
            'team_id': issue_data.get('teamId')
        }
        
        # Process through hooks for priority analysis
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.PREHOOK,
            timestamp=datetime.now(),
            scope=MessageScope.PROJECT,
            message=f"Linear issue created: {issue_data.get('title', '')}",
            metadata={'issue_data': issue_data, 'integration': 'linear_system'},
            project_id=issue_data.get('projectId')
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.PROJECT,
            hook_context.metadata
        )
        
        return {
            'issue_id': issue_id,
            'processing_result': result,
            'context_stored': True
        }
    
    async def on_issue_updated(self, issue_id: str, update_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle Linear issue updates."""
        
        if issue_id in self.issue_contexts:
            # Update stored context
            self.issue_contexts[issue_id]['last_updated'] = datetime.now().isoformat()
            self.issue_contexts[issue_id].update(update_data)
        
        # Process through hooks
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.CONTEXT_HOOK,
            timestamp=datetime.now(),
            scope=MessageScope.PROJECT,
            message=f"Linear issue updated: {issue_id}",
            metadata={'update_data': update_data, 'integration': 'linear_system'},
            project_id=update_data.get('projectId')
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.PROJECT,
            hook_context.metadata
        )
        
        return {
            'issue_id': issue_id,
            'update_processed': True,
            'hook_processing_result': result
        }
    
    def generate_project_insights(self, project_id: str) -> Dict[str, Any]:
        """Generate insights for a specific project."""
        
        project_issues = [
            issue for issue in self.issue_contexts.values()
            if issue.get('project_id') == project_id
        ]
        
        if not project_issues:
            return {'project_id': project_id, 'total_issues': 0}
        
        # Calculate metrics
        total_issues = len(project_issues)
        priority_distribution = {}
        
        for issue in project_issues:
            priority = issue.get('priority', 'medium')
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        # Calculate completion trends (would need issue state data)
        # For now, basic analysis
        
        return {
            'project_id': project_id,
            'total_issues': total_issues,
            'priority_distribution': priority_distribution,
            'insights': self._generate_insights(project_issues)
        }
    
    def _generate_insights(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate insights based on issue data."""
        
        insights = []
        
        high_priority_count = len([i for i in issues if i.get('priority') == 'high'])
        total_issues = len(issues)
        
        if high_priority_count / total_issues > 0.3:
            insights.append("High concentration of high-priority issues - consider resource reallocation")
        
        # Analyze titles for common patterns
        titles = [issue.get('title', '').lower() for issue in issues]
        common_words = {}
        
        for title in titles:
            words = title.split()
            for word in words:
                if len(word) > 3:  # Ignore short words
                    common_words[word] = common_words.get(word, 0) + 1
        
        frequent_words = [word for word, count in common_words.items() if count > len(issues) * 0.2]
        
        if frequent_words:
            insights.append(f"Common issue themes: {', '.join(frequent_words[:3])}")
        
        return insights


class MCPIntegration:
    """Integration with MCP (Model Context Protocol) system."""
    
    def __init__(self, hooks_system):
        self.hooks_system = hooks_system
        self.protocol_events: List[Dict[str, Any]] = []
        self.tool_usage_stats: Dict[str, Dict[str, Any]] = {}
    
    async def on_tool_call(self, tool_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle MCP tool calls."""
        
        tool_name = tool_data.get('name', 'unknown')
        
        # Update tool usage statistics
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {
                'call_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'average_execution_time': 0.0
            }
        
        stats = self.tool_usage_stats[tool_name]
        stats['call_count'] += 1
        
        # Process through hooks
        hook_context = HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.POST_TOOL_USE,
            timestamp=datetime.now(),
            scope=MessageScope.SYSTEM,
            message=f"MCP tool called: {tool_name}",
            metadata={'tool_data': tool_data, 'integration': 'mcp_system'}
        )
        
        result = await self.hooks_system.process_message(
            hook_context.message,
            MessageScope.SYSTEM,
            hook_context.metadata
        )
        
        return {
            'tool_name': tool_name,
            'call_processed': True,
            'hook_processing_result': result
        }
    
    async def on_tool_result(self, tool_name: str, result_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """Handle MCP tool results."""
        
        if tool_name in self.tool_usage_stats:
            stats = self.tool_usage_stats[tool_name]
            
            if result_data.get('success', True):
                stats['success_count'] += 1
            else:
                stats['failure_count'] += 1
            
            # Update average execution time
            execution_time = result_data.get('execution_time', 0)
            if execution_time > 0:
                current_avg = stats['average_execution_time']
                call_count = stats['call_count']
                stats['average_execution_time'] = (
                    (current_avg * (call_count - 1) + execution_time) / call_count
                )
        
        # Process through link cataloging hook if URLs are found
        link_catalog = LinkCatalogHook()
        link_result = await link_catalog.process_tool_use(HookContext(
            hook_id=str(uuid.uuid4()),
            hook_type=HookType.POST_TOOL_USE,
            timestamp=datetime.now(),
            scope=MessageScope.SYSTEM,
            message=f"MCP tool result: {tool_name}",
            metadata={'tool_name': tool_name, 'tool_result': result_data}
        ))
        
        return {
            'tool_name': tool_name,
            'result_processed': True,
            'link_cataloging_result': link_result
        }
    
    def get_tool_analytics(self) -> Dict[str, Any]:
        """Get MCP tool usage analytics."""
        
        if not self.tool_usage_stats:
            return {'total_tools': 0}
        
        total_calls = sum(stats['call_count'] for stats in self.tool_usage_stats.values())
        total_successes = sum(stats['success_count'] for stats in self.tool_usage_stats.values())
        
        # Most used tools
        most_used = sorted(
            self.tool_usage_stats.items(),
            key=lambda x: x[1]['call_count'],
            reverse=True
        )[:5]
        
        # Most reliable tools
        most_reliable = []
        for tool_name, stats in self.tool_usage_stats.items():
            if stats['call_count'] > 5:  # Enough data
                success_rate = stats['success_count'] / stats['call_count']
                most_reliable.append((tool_name, success_rate))
        
        most_reliable.sort(key=lambda x: x[1], reverse=True)
        most_reliable = most_reliable[:5]
        
        return {
            'total_tools': len(self.tool_usage_stats),
            'total_calls': total_calls,
            'overall_success_rate': total_successes / total_calls if total_calls > 0 else 0,
            'most_used_tools': [{'name': name, 'calls': stats['call_count']} for name, stats in most_used],
            'most_reliable_tools': [{'name': name, 'success_rate': rate} for name, rate in most_reliable]
        }


class HookIntegrationManager:
    """Main integration manager coordinating all system integrations."""
    
    def __init__(self, hooks_system=None):
        self.hooks_system = hooks_system or get_hook_system()
        
        # Initialize integrations
        self.todo_integration = TodoSystemIntegration(self.hooks_system)
        self.agent_integration = AgentSystemIntegration(self.hooks_system)
        self.ide_integration = IDEIntegration(self.hooks_system)
        self.linear_integration = LinearIntegration(self.hooks_system)
        self.mcp_integration = MCPIntegration(self.hooks_system)
        
        # Integration event history
        self.integration_events: List[IntegrationEvent] = []
        
        # Setup hooks
        self._setup_integration_hooks()
    
    def _setup_integration_hooks(self):
        """Setup hooks for integration events."""
        
        # Register integration hooks with the hook system
        self.hooks_system.registry.register(
            HookType.PREHOOK,
            self._handle_prehook_integration,
            priority=50,
            name='integration_prehook'
        )
        
        self.hooks_system.registry.register(
            HookType.POSTHOOK,
            self._handle_posthook_integration,
            priority=50,
            name='integration_posthook'
        )
        
        self.hooks_system.registry.register(
            HookType.POST_TOOL_USE,
            self._handle_tool_use_integration,
            priority=50,
            name='integration_tool_use'
        )
    
    async def _handle_prehook_integration(self, context: HookContext) -> Dict[str, Any]:
        """Handle integration for prehook events."""
        
        integration_type = context.metadata.get('integration')
        
        if integration_type == 'todo_system':
            # Additional todo system processing if needed
            pass
        elif integration_type == 'linear_system':
            # Additional Linear processing if needed
            pass
        
        # Log integration event
        event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type='prehook_integration',
            source_system=integration_type or 'unknown',
            target_system='hooks_system',
            timestamp=datetime.now(),
            data={'scope': context.scope.value, 'message_length': len(context.message)},
            context=context
        )
        
        self.integration_events.append(event)
        
        return {'integration_processed': True, 'event_id': event.event_id}
    
    async def _handle_posthook_integration(self, context: HookContext) -> Dict[str, Any]:
        """Handle integration for posthook events."""
        
        integration_type = context.metadata.get('integration')
        
        # Log integration event
        event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type='posthook_integration',
            source_system=integration_type or 'unknown',
            target_system='hooks_system',
            timestamp=datetime.now(),
            data={'scope': context.scope.value},
            context=context
        )
        
        self.integration_events.append(event)
        
        return {'integration_processed': True, 'event_id': event.event_id}
    
    async def _handle_tool_use_integration(self, context: HookContext) -> Dict[str, Any]:
        """Handle integration for tool use events."""
        
        tool_name = context.metadata.get('tool_name', 'unknown')
        
        # Log integration event
        event = IntegrationEvent(
            event_id=str(uuid.uuid4()),
            event_type='tool_use_integration',
            source_system='mcp_system',
            target_system='hooks_system',
            timestamp=datetime.now(),
            data={'tool_name': tool_name},
            context=context
        )
        
        self.integration_events.append(event)
        
        return {'integration_processed': True, 'event_id': event.event_id}
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get comprehensive integration statistics."""
        
        return {
            'total_integration_events': len(self.integration_events),
            'todo_integration': {
                'tracked_todos': len(self.todo_integration.todo_contexts),
                'completion_patterns': len(self.todo_integration.completion_patterns)
            },
            'agent_integration': {
                'tracked_agents': len(self.agent_integration.agent_performance),
                'optimization_recommendations': self.agent_integration.optimize_task_distribution()
            },
            'ide_integration': self.ide_integration.get_quality_insights(),
            'linear_integration': {
                'tracked_issues': len(self.linear_integration.issue_contexts),
                'tracked_projects': len(self.linear_integration.project_metrics)
            },
            'mcp_integration': self.mcp_integration.get_tool_analytics()
        }
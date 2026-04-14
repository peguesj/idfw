"""
Result Aggregation and Reporting Pipeline for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides comprehensive result aggregation and reporting capabilities including:
- Real-time result collection from agents
- Data transformation and analysis
- Report generation and distribution
- Performance metrics calculation
- Status reporting for Linear integration
"""

import asyncio
import json
import logging
import statistics
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

import redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ResultEntry(BaseModel):
    """Individual result entry from an agent"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    task_id: str
    result_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AggregatedResult(BaseModel):
    """Aggregated results from multiple agents/tasks"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    success_rate: float = 0.0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    results_by_agent: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    results_by_type: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


class ReportTemplate(BaseModel):
    """Report template configuration"""
    name: str
    description: str
    sections: List[str]
    format: str = "markdown"  # markdown, json, html
    filters: Dict[str, Any] = Field(default_factory=dict)
    aggregations: List[str] = Field(default_factory=list)


class ResultAggregator:
    """Aggregates and analyzes results from multiple agents"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.result_buffer: deque = deque(maxlen=10000)
        self.active_sessions: Dict[str, AggregatedResult] = {}
        self.completed_sessions: deque = deque(maxlen=1000)
        self.performance_cache: Dict[str, Any] = {}
        
        # Report templates
        self.report_templates = self._load_default_templates()
        
        # Metrics
        self.metrics = {
            "total_results_processed": 0,
            "total_sessions": 0,
            "average_session_duration": 0.0,
            "peak_throughput": 0.0,
            "last_updated": datetime.utcnow()
        }
    
    def _load_default_templates(self) -> Dict[str, ReportTemplate]:
        """Load default report templates"""
        templates = {}
        
        # Executive Summary Template
        templates["executive_summary"] = ReportTemplate(
            name="Executive Summary",
            description="High-level overview for stakeholders",
            sections=[
                "overview",
                "key_metrics",
                "achievements",
                "issues",
                "next_steps"
            ],
            format="markdown",
            aggregations=["success_rate", "total_tasks", "execution_time"]
        )
        
        # Technical Report Template
        templates["technical_report"] = ReportTemplate(
            name="Technical Report",
            description="Detailed technical analysis",
            sections=[
                "system_performance",
                "agent_performance",
                "error_analysis",
                "resource_utilization",
                "recommendations"
            ],
            format="markdown",
            aggregations=["performance_metrics", "error_rates", "resource_usage"]
        )
        
        # Linear Status Template
        templates["linear_status"] = ReportTemplate(
            name="Linear Status Update",
            description="Status update for Linear issues",
            sections=[
                "progress_summary",
                "completed_tasks",
                "blockers",
                "next_actions"
            ],
            format="markdown",
            filters={"success": True},
            aggregations=["task_completion"]
        )
        
        return templates
    
    async def add_result(self, result: ResultEntry) -> bool:
        """Add a result to the aggregation pipeline"""
        try:
            # Add to buffer
            self.result_buffer.append(result)
            
            # Update session if active
            session_id = result.metadata.get("session_id")
            if session_id and session_id in self.active_sessions:
                await self._update_session(session_id, result)
            
            # Store in Redis for persistence
            result_key = f"idfwu:results:{result.id}"
            await self.redis.setex(
                result_key, 
                3600,  # 1 hour TTL
                result.json()
            )
            
            # Update metrics
            self.metrics["total_results_processed"] += 1
            self.metrics["last_updated"] = datetime.utcnow()
            
            logger.debug(f"Added result {result.id} from agent {result.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add result {result.id}: {e}")
            return False
    
    async def start_session(self, session_id: str, metadata: Dict[str, Any] = None) -> AggregatedResult:
        """Start a new aggregation session"""
        session = AggregatedResult(
            session_id=session_id,
            start_time=datetime.utcnow()
        )
        
        if metadata:
            session.metadata = metadata
        
        self.active_sessions[session_id] = session
        self.metrics["total_sessions"] += 1
        
        logger.info(f"Started aggregation session: {session_id}")
        return session
    
    async def end_session(self, session_id: str) -> Optional[AggregatedResult]:
        """End an aggregation session and finalize results"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session = self.active_sessions.pop(session_id)
        session.end_time = datetime.utcnow()
        
        # Calculate final metrics
        await self._finalize_session_metrics(session)
        
        # Store completed session
        self.completed_sessions.append(session)
        
        # Store in Redis
        session_key = f"idfwu:sessions:{session_id}"
        await self.redis.setex(
            session_key,
            86400,  # 24 hours TTL
            session.json()
        )
        
        logger.info(f"Ended aggregation session: {session_id}")
        return session
    
    async def _update_session(self, session_id: str, result: ResultEntry):
        """Update session with new result"""
        session = self.active_sessions[session_id]
        
        # Update counters
        session.total_tasks += 1
        if result.success:
            session.completed_tasks += 1
        else:
            session.failed_tasks += 1
        
        # Update execution time
        if result.execution_time:
            session.total_execution_time += result.execution_time
            session.average_execution_time = session.total_execution_time / session.total_tasks
        
        # Update success rate
        session.success_rate = (session.completed_tasks / session.total_tasks) * 100
        
        # Group by agent
        if result.agent_id not in session.results_by_agent:
            session.results_by_agent[result.agent_id] = []
        session.results_by_agent[result.agent_id].append(result.dict())
        
        # Group by type
        if result.result_type not in session.results_by_type:
            session.results_by_type[result.result_type] = []
        session.results_by_type[result.result_type].append(result.dict())
    
    async def _finalize_session_metrics(self, session: AggregatedResult):
        """Calculate final performance metrics for session"""
        if not session.results_by_agent:
            return
        
        # Agent performance metrics
        agent_metrics = {}
        for agent_id, results in session.results_by_agent.items():
            agent_results = [r for r in results if r.get("success")]
            agent_failures = [r for r in results if not r.get("success")]
            
            execution_times = [r.get("execution_time", 0) for r in agent_results if r.get("execution_time")]
            
            agent_metrics[agent_id] = {
                "total_tasks": len(results),
                "successful_tasks": len(agent_results),
                "failed_tasks": len(agent_failures),
                "success_rate": (len(agent_results) / len(results)) * 100 if results else 0,
                "avg_execution_time": statistics.mean(execution_times) if execution_times else 0,
                "min_execution_time": min(execution_times) if execution_times else 0,
                "max_execution_time": max(execution_times) if execution_times else 0
            }
        
        session.performance_metrics["agents"] = agent_metrics
        
        # Overall performance
        all_execution_times = []
        for results in session.results_by_agent.values():
            all_execution_times.extend([
                r.get("execution_time", 0) for r in results 
                if r.get("execution_time") and r.get("success")
            ])
        
        if all_execution_times:
            session.performance_metrics["overall"] = {
                "median_execution_time": statistics.median(all_execution_times),
                "std_dev_execution_time": statistics.stdev(all_execution_times) if len(all_execution_times) > 1 else 0,
                "throughput": len(all_execution_times) / ((session.end_time - session.start_time).total_seconds() / 3600)  # tasks per hour
            }
        
        # Generate summary
        session.summary = self._generate_session_summary(session)
    
    def _generate_session_summary(self, session: AggregatedResult) -> str:
        """Generate a summary of the session"""
        duration = session.end_time - session.start_time if session.end_time else timedelta(0)
        duration_str = f"{duration.total_seconds():.1f}s"
        
        summary_parts = [
            f"Session completed in {duration_str}",
            f"Processed {session.total_tasks} tasks",
            f"Success rate: {session.success_rate:.1f}%",
            f"Average execution time: {session.average_execution_time:.2f}s"
        ]
        
        if session.failed_tasks > 0:
            summary_parts.append(f"Failed tasks: {session.failed_tasks}")
        
        return " | ".join(summary_parts)
    
    async def get_session_results(self, session_id: str) -> Optional[AggregatedResult]:
        """Get results for a specific session"""
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Check completed sessions
        for session in self.completed_sessions:
            if session.session_id == session_id:
                return session
        
        # Check Redis
        session_key = f"idfwu:sessions:{session_id}"
        session_data = await self.redis.get(session_key)
        if session_data:
            return AggregatedResult.parse_raw(session_data)
        
        return None
    
    async def query_results(
        self,
        filters: Dict[str, Any] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100
    ) -> List[ResultEntry]:
        """Query results with filters"""
        results = []
        
        # Apply filters to buffer
        for result in list(self.result_buffer):
            if self._matches_filters(result, filters, time_range):
                results.append(result)
                if len(results) >= limit:
                    break
        
        return results
    
    def _matches_filters(
        self,
        result: ResultEntry,
        filters: Dict[str, Any] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> bool:
        """Check if result matches filters"""
        if time_range:
            start_time, end_time = time_range
            if not (start_time <= result.timestamp <= end_time):
                return False
        
        if filters:
            for key, value in filters.items():
                if key == "agent_id" and result.agent_id != value:
                    return False
                elif key == "success" and result.success != value:
                    return False
                elif key == "result_type" and result.result_type != value:
                    return False
                elif key in result.metadata and result.metadata[key] != value:
                    return False
        
        return True
    
    async def generate_report(
        self,
        template_name: str,
        session_id: Optional[str] = None,
        custom_data: Dict[str, Any] = None
    ) -> str:
        """Generate a report using a template"""
        if template_name not in self.report_templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.report_templates[template_name]
        
        # Get data
        if session_id:
            session_data = await self.get_session_results(session_id)
            data = session_data.dict() if session_data else {}
        else:
            data = await self._get_global_data()
        
        if custom_data:
            data.update(custom_data)
        
        # Generate report based on template
        if template.format == "markdown":
            return await self._generate_markdown_report(template, data)
        elif template.format == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {template.format}")
    
    async def _get_global_data(self) -> Dict[str, Any]:
        """Get global aggregated data"""
        now = datetime.utcnow()
        recent_results = await self.query_results(
            time_range=(now - timedelta(hours=24), now),
            limit=1000
        )
        
        total_tasks = len(recent_results)
        successful_tasks = sum(1 for r in recent_results if r.success)
        failed_tasks = total_tasks - successful_tasks
        
        return {
            "timestamp": now,
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (successful_tasks / max(1, total_tasks)) * 100,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "metrics": self.metrics
        }
    
    async def _generate_markdown_report(self, template: ReportTemplate, data: Dict[str, Any]) -> str:
        """Generate markdown report"""
        report_lines = [
            f"# {template.name}",
            f"*Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            template.description,
            ""
        ]
        
        for section in template.sections:
            section_content = await self._generate_section_content(section, data, template)
            if section_content:
                report_lines.extend(section_content)
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    async def _generate_section_content(self, section: str, data: Dict[str, Any], template: ReportTemplate) -> List[str]:
        """Generate content for a report section"""
        if section == "overview":
            return [
                "## Overview",
                f"- Total Tasks: {data.get('total_tasks', 0)}",
                f"- Success Rate: {data.get('success_rate', 0):.1f}%",
                f"- Active Sessions: {data.get('active_sessions', 0)}"
            ]
        
        elif section == "key_metrics":
            return [
                "## Key Metrics",
                f"- Completed Tasks: {data.get('successful_tasks', 0)}",
                f"- Failed Tasks: {data.get('failed_tasks', 0)}",
                f"- Average Execution Time: {data.get('average_execution_time', 0):.2f}s"
            ]
        
        elif section == "achievements":
            achievements = []
            if data.get('success_rate', 0) > 90:
                achievements.append("- ✅ High success rate maintained")
            if data.get('total_tasks', 0) > 100:
                achievements.append("- 📈 High task throughput achieved")
            
            return ["## Achievements"] + (achievements or ["- No major achievements to report"])
        
        elif section == "issues":
            issues = []
            if data.get('success_rate', 100) < 80:
                issues.append("- ⚠️ Success rate below acceptable threshold")
            if data.get('failed_tasks', 0) > 10:
                issues.append("- 🔴 High number of failed tasks")
            
            return ["## Issues"] + (issues or ["- No significant issues detected"])
        
        elif section == "next_steps":
            return [
                "## Next Steps",
                "- Continue monitoring system performance",
                "- Address any identified issues",
                "- Optimize agent performance based on metrics"
            ]
        
        return []


class ReportScheduler:
    """Schedules and distributes reports"""
    
    def __init__(self, aggregator: ResultAggregator):
        self.aggregator = aggregator
        self.scheduled_reports: List[Dict[str, Any]] = []
        self.running = False
    
    def schedule_report(
        self,
        template_name: str,
        schedule: str,  # cron-like: "0 9 * * *" for daily at 9 AM
        recipients: List[str],
        session_filter: Optional[str] = None
    ):
        """Schedule a recurring report"""
        self.scheduled_reports.append({
            "template": template_name,
            "schedule": schedule,
            "recipients": recipients,
            "session_filter": session_filter,
            "last_run": None
        })
    
    async def start_scheduler(self):
        """Start the report scheduler"""
        self.running = True
        while self.running:
            await self._check_scheduled_reports()
            await asyncio.sleep(60)  # Check every minute
    
    async def _check_scheduled_reports(self):
        """Check and run scheduled reports"""
        # Implementation would check schedule and generate reports
        # For now, just a placeholder
        pass
    
    def stop_scheduler(self):
        """Stop the report scheduler"""
        self.running = False
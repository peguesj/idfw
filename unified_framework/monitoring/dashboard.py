"""
Monitoring Dashboard for IDFWU Unified Framework
Linear Project: 4d649a6501f7

Real-time monitoring dashboard for the orchestrator agent providing:
- Agent status monitoring
- Task queue visualization
- Performance metrics
- System health indicators
- Alert management
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

import redis
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text


class MetricsCollector:
    """Collects and aggregates system metrics"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.metrics_history = []
        self.max_history = 1000
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            # Get orchestrator status
            status_key = "idfwu:orchestrator:status"
            status_data = await self.redis.get(status_key)
            orchestrator_status = json.loads(status_data) if status_data else {}
            
            # Get agent registry
            registry_key = "idfwu:orchestrator:agents"
            registry_data = await self.redis.get(registry_key)
            agent_registry = json.loads(registry_data) if registry_data else {}
            
            # Calculate derived metrics
            total_agents = len(agent_registry)
            active_agents = sum(1 for agent in agent_registry.values() 
                              if agent.get("status") == "active")
            
            # Get task statistics
            task_stats = orchestrator_status.get("orchestrator", {})
            completed_tasks = task_stats.get("completed_tasks", 0)
            failed_tasks = task_stats.get("failed_tasks", 0)
            total_tasks = task_stats.get("total_tasks", 0)
            
            success_rate = (completed_tasks / max(1, total_tasks)) * 100
            
            # Get queue status
            queue_status = task_stats.get("queue_status", {})
            queue_total = sum(queue_status.values())
            
            # Calculate load metrics
            avg_load = sum(agent.get("load_score", 0) for agent in agent_registry.values()) / max(1, total_agents)
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "orchestrator_status": orchestrator_status.get("status", "unknown"),
                    "uptime": orchestrator_status.get("uptime", 0),
                    "restart_count": orchestrator_status.get("restart_count", 0),
                    "health_check": orchestrator_status.get("health_check_passed", False)
                },
                "agents": {
                    "total": total_agents,
                    "active": active_agents,
                    "idle": sum(1 for agent in agent_registry.values() 
                               if agent.get("status") == "idle"),
                    "busy": sum(1 for agent in agent_registry.values() 
                               if agent.get("status") == "busy"),
                    "error": sum(1 for agent in agent_registry.values() 
                                if agent.get("status") == "error"),
                    "average_load": avg_load
                },
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks,
                    "success_rate": success_rate,
                    "queue_depth": queue_total
                },
                "queues": queue_status,
                "performance": {
                    "avg_execution_time": task_stats.get("avg_execution_time", 0),
                    "throughput": completed_tasks / max(1, orchestrator_status.get("uptime", 1) / 3600),  # tasks per hour
                    "error_rate": (failed_tasks / max(1, total_tasks)) * 100
                }
            }
            
            # Add to history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "system": {"orchestrator_status": "error"}
            }
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for the specified number of hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics["timestamp"]) > cutoff_time
        ]


class MonitoringDashboard:
    """Real-time monitoring dashboard"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.console = Console()
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.metrics_collector = MetricsCollector(self.redis_client)
        self.running = False
        self.refresh_interval = 2.0  # seconds
        
        # Alert thresholds
        self.alert_thresholds = {
            "high_error_rate": 10.0,  # %
            "high_queue_depth": 100,
            "low_success_rate": 80.0,  # %
            "high_load": 0.8
        }
        
        self.alerts: List[Dict[str, Any]] = []
    
    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="system_status"),
            Layout(name="agent_status")
        )
        
        layout["right"].split_column(
            Layout(name="task_metrics"),
            Layout(name="alerts")
        )
        
        return layout
    
    def create_header_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create header panel with system overview"""
        system = metrics.get("system", {})
        status = system.get("orchestrator_status", "unknown")
        uptime = system.get("uptime", 0)
        
        # Status indicator
        status_color = {
            "running": "green",
            "error": "red",
            "stopped": "red",
            "unknown": "yellow"
        }.get(status, "yellow")
        
        uptime_hours = uptime / 3600
        
        header_text = Text()
        header_text.append("🎛️  IDFWU Orchestrator Dashboard", style="bold blue")
        header_text.append("  |  ")
        header_text.append(f"Status: {status.upper()}", style=f"bold {status_color}")
        header_text.append("  |  ")
        header_text.append(f"Uptime: {uptime_hours:.1f}h", style="cyan")
        header_text.append("  |  ")
        header_text.append(f"Updated: {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        return Panel(header_text, border_style="blue")
    
    def create_system_status_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create system status panel"""
        system = metrics.get("system", {})
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        # System metrics
        health_icon = "✅" if system.get("health_check") else "❌"
        table.add_row("Health Check", health_icon)
        table.add_row("Restart Count", str(system.get("restart_count", 0)))
        
        # Performance metrics
        perf = metrics.get("performance", {})
        table.add_row("Avg Execution", f"{perf.get('avg_execution_time', 0):.2f}s")
        table.add_row("Throughput", f"{perf.get('throughput', 0):.1f} tasks/h")
        table.add_row("Error Rate", f"{perf.get('error_rate', 0):.1f}%")
        
        return Panel(table, title="🔧 System Status", border_style="green")
    
    def create_agent_status_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create agent status panel"""
        agents = metrics.get("agents", {})
        
        table = Table(show_header=True, box=None)
        table.add_column("Status", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Percentage", justify="right")
        
        total = agents.get("total", 0)
        
        statuses = [
            ("Active", agents.get("active", 0), "green"),
            ("Idle", agents.get("idle", 0), "yellow"),
            ("Busy", agents.get("busy", 0), "blue"),
            ("Error", agents.get("error", 0), "red")
        ]
        
        for status, count, color in statuses:
            percentage = (count / max(1, total)) * 100
            table.add_row(
                Text(status, style=color),
                str(count),
                f"{percentage:.1f}%"
            )
        
        # Add total and average load
        table.add_row("", "", "")
        table.add_row(
            Text("Total", style="bold"),
            str(total),
            ""
        )
        table.add_row(
            Text("Avg Load", style="bold"),
            f"{agents.get('average_load', 0):.2f}",
            ""
        )
        
        return Panel(table, title="🤖 Agent Status", border_style="blue")
    
    def create_task_metrics_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create task metrics panel"""
        tasks = metrics.get("tasks", {})
        queues = metrics.get("queues", {})
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        # Task statistics
        table.add_row("Total Tasks", str(tasks.get("total", 0)))
        table.add_row("Completed", str(tasks.get("completed", 0)))
        table.add_row("Failed", str(tasks.get("failed", 0)))
        table.add_row("Success Rate", f"{tasks.get('success_rate', 0):.1f}%")
        table.add_row("", "")
        
        # Queue depths
        table.add_row("Queue Depth", str(tasks.get("queue_depth", 0)))
        for priority, count in queues.items():
            if count > 0:
                table.add_row(f"  {priority.title()}", str(count))
        
        return Panel(table, title="📊 Task Metrics", border_style="yellow")
    
    def create_alerts_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create alerts panel"""
        # Check for new alerts
        self._check_alerts(metrics)
        
        if not self.alerts:
            content = Text("No active alerts", style="green")
        else:
            content = ""
            for alert in self.alerts[-5:]:  # Show last 5 alerts
                severity_color = {
                    "critical": "red",
                    "warning": "yellow",
                    "info": "blue"
                }.get(alert.get("severity", "info"), "white")
                
                timestamp = alert.get("timestamp", "")
                time_str = timestamp.split("T")[1][:8] if "T" in timestamp else "Unknown"
                
                content += f"[{severity_color}]● {time_str} - {alert.get('message', 'Unknown alert')}[/]\n"
        
        return Panel(content, title="🚨 Alerts", border_style="red")
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        current_time = datetime.utcnow().isoformat()
        
        # Clear old alerts (older than 1 hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]
        
        # Check error rate
        error_rate = metrics.get("performance", {}).get("error_rate", 0)
        if error_rate > self.alert_thresholds["high_error_rate"]:
            self.alerts.append({
                "timestamp": current_time,
                "severity": "warning",
                "message": f"High error rate: {error_rate:.1f}%"
            })
        
        # Check queue depth
        queue_depth = metrics.get("tasks", {}).get("queue_depth", 0)
        if queue_depth > self.alert_thresholds["high_queue_depth"]:
            self.alerts.append({
                "timestamp": current_time,
                "severity": "warning",
                "message": f"High queue depth: {queue_depth}"
            })
        
        # Check success rate
        success_rate = metrics.get("tasks", {}).get("success_rate", 100)
        if success_rate < self.alert_thresholds["low_success_rate"]:
            self.alerts.append({
                "timestamp": current_time,
                "severity": "critical",
                "message": f"Low success rate: {success_rate:.1f}%"
            })
        
        # Check agent load
        avg_load = metrics.get("agents", {}).get("average_load", 0)
        if avg_load > self.alert_thresholds["high_load"]:
            self.alerts.append({
                "timestamp": current_time,
                "severity": "warning",
                "message": f"High agent load: {avg_load:.2f}"
            })
        
        # Check orchestrator health
        health = metrics.get("system", {}).get("health_check", True)
        if not health:
            self.alerts.append({
                "timestamp": current_time,
                "severity": "critical",
                "message": "Orchestrator health check failed"
            })
    
    def create_footer_panel(self) -> Panel:
        """Create footer panel with controls"""
        footer_text = Text()
        footer_text.append("Controls: ", style="bold")
        footer_text.append("Q - Quit", style="cyan")
        footer_text.append("  |  ")
        footer_text.append("R - Refresh", style="cyan")
        footer_text.append("  |  ")
        footer_text.append("A - View All Agents", style="cyan")
        footer_text.append("  |  ")
        footer_text.append("T - Task Details", style="cyan")
        
        return Panel(footer_text, border_style="dim")
    
    async def update_display(self, layout: Layout):
        """Update the dashboard display"""
        try:
            # Collect metrics
            metrics = await self.metrics_collector.collect_metrics()
            
            # Update layout panels
            layout["header"].update(self.create_header_panel(metrics))
            layout["system_status"].update(self.create_system_status_panel(metrics))
            layout["agent_status"].update(self.create_agent_status_panel(metrics))
            layout["task_metrics"].update(self.create_task_metrics_panel(metrics))
            layout["alerts"].update(self.create_alerts_panel(metrics))
            layout["footer"].update(self.create_footer_panel())
            
        except Exception as e:
            error_panel = Panel(f"Error updating display: {e}", border_style="red")
            layout["header"].update(error_panel)
    
    async def run(self):
        """Run the monitoring dashboard"""
        try:
            # Test Redis connection
            await self.redis_client.ping()
        except Exception as e:
            self.console.print(f"[red]Failed to connect to Redis: {e}[/]")
            return
        
        layout = self.create_layout()
        self.running = True
        
        with Live(layout, console=self.console, refresh_per_second=1) as live:
            while self.running:
                try:
                    await self.update_display(layout)
                    await asyncio.sleep(self.refresh_interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.console.print(f"[red]Dashboard error: {e}[/]")
                    await asyncio.sleep(5)
        
        self.console.print("\n[yellow]Dashboard stopped[/]")


async def main():
    """Main entry point for the dashboard"""
    dashboard = MonitoringDashboard()
    
    try:
        await dashboard.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Dashboard failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
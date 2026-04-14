"""
Orchestrator CLI for IDFWU Unified Framework
Linear Project: 4d649a6501f7

Command-line interface for managing the orchestrator agent service including:
- Service lifecycle management
- Agent deployment and monitoring
- Task queue management
- System status and diagnostics
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import click
import redis

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.orchestrator_service import OrchestratorService
try:
    from agents.cdia.orchestrator_agent import OrchestratorAgent
except ImportError:
    OrchestratorAgent = None
try:
    from agents.base_agent import MessagePriority
except ImportError:
    MessagePriority = None


class OrchestratorCLI:
    """CLI interface for orchestrator management"""
    
    def __init__(self):
        self.redis_client = None
        self.service = None
        
    async def connect_redis(self, redis_url: str = "redis://localhost:6379"):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            return True
        except Exception as e:
            click.echo(f"Failed to connect to Redis: {e}", err=True)
            return False
    
    async def start_service(self, background: bool = False):
        """Start the orchestrator service"""
        click.echo("Starting Orchestrator Service...")
        
        self.service = OrchestratorService()
        
        if background:
            # Start as background daemon
            import daemon
            with daemon.DaemonContext():
                await self.service.run_forever()
        else:
            # Start in foreground
            success = await self.service.start()
            if success:
                click.echo("✅ Orchestrator Service started successfully")
                click.echo("Press Ctrl+C to stop...")
                try:
                    await self.service.run_forever()
                except KeyboardInterrupt:
                    click.echo("\nShutting down...")
                    await self.service.stop()
            else:
                click.echo("❌ Failed to start Orchestrator Service", err=True)
                return False
        
        return True
    
    async def stop_service(self):
        """Stop the orchestrator service"""
        if self.service:
            success = await self.service.stop()
            if success:
                click.echo("✅ Orchestrator Service stopped")
            else:
                click.echo("❌ Failed to stop service", err=True)
            return success
        else:
            click.echo("No service instance found")
            return False
    
    async def get_status(self):
        """Get service status"""
        if not await self.connect_redis():
            return
        
        try:
            # Try to get status from running service
            status_key = "idfwu:orchestrator:status"
            status_data = await self.redis_client.get(status_key)
            
            if status_data:
                status = json.loads(status_data)
                self._display_status(status)
            else:
                click.echo("No orchestrator service found running")
                
        except Exception as e:
            click.echo(f"Error getting status: {e}", err=True)
    
    def _display_status(self, status: Dict[str, Any]):
        """Display formatted status information"""
        click.echo("\n🎛️  Orchestrator Service Status")
        click.echo("=" * 50)
        
        # Service status
        service_status = status.get("status", "unknown")
        status_icon = "🟢" if service_status == "running" else "🔴"
        click.echo(f"{status_icon} Status: {service_status}")
        
        if status.get("start_time"):
            click.echo(f"⏰ Started: {status['start_time']}")
        
        if status.get("uptime"):
            uptime_hours = status["uptime"] / 3600
            click.echo(f"🕐 Uptime: {uptime_hours:.2f} hours")
        
        click.echo(f"🔄 Restarts: {status.get('restart_count', 0)}")
        
        health_icon = "✅" if status.get("health_check_passed") else "❌"
        click.echo(f"{health_icon} Health Check: {'Passed' if status.get('health_check_passed') else 'Failed'}")
        
        # Orchestrator details
        if "orchestrator" in status:
            orch_status = status["orchestrator"]
            click.echo(f"\n📊 Orchestrator Details")
            click.echo(f"   Total Agents: {orch_status.get('total_agents', 0)}")
            click.echo(f"   Active Agents: {orch_status.get('active_agents', 0)}")
            click.echo(f"   Total Tasks: {orch_status.get('total_tasks', 0)}")
            click.echo(f"   Completed: {orch_status.get('completed_tasks', 0)}")
            click.echo(f"   Failed: {orch_status.get('failed_tasks', 0)}")
            click.echo(f"   Success Rate: {orch_status.get('success_rate', 0):.1f}%")
            
            # Queue status
            if "queue_status" in orch_status:
                queue_status = orch_status["queue_status"]
                click.echo(f"\n📋 Task Queues")
                for priority, count in queue_status.items():
                    click.echo(f"   {priority.title()}: {count}")
    
    async def list_agents(self):
        """List registered agents"""
        if not await self.connect_redis():
            return
        
        try:
            # Get agent registry from Redis
            registry_key = "idfwu:orchestrator:agents"
            registry_data = await self.redis_client.get(registry_key)
            
            if registry_data:
                agents = json.loads(registry_data)
                self._display_agents(agents)
            else:
                click.echo("No agents registered")
                
        except Exception as e:
            click.echo(f"Error listing agents: {e}", err=True)
    
    def _display_agents(self, agents: Dict[str, Any]):
        """Display formatted agent information"""
        click.echo("\n🤖 Registered Agents")
        click.echo("=" * 60)
        
        for agent_id, agent_info in agents.items():
            status = agent_info.get("status", "unknown")
            status_icon = {"active": "🟢", "idle": "🟡", "busy": "🔵", "error": "🔴", "offline": "⚫"}.get(status, "❓")
            
            click.echo(f"{status_icon} {agent_id}")
            click.echo(f"   Type: {agent_info.get('type', 'Unknown')}")
            click.echo(f"   Status: {status}")
            click.echo(f"   Tasks: {agent_info.get('current_tasks', 0)}")
            click.echo(f"   Load: {agent_info.get('load_score', 0):.2f}")
            click.echo("")
    
    async def spawn_agent(self, agent_type: str, capabilities: List[str], agent_config: Dict[str, Any]):
        """Spawn a new agent"""
        if not await self.connect_redis():
            return
        
        try:
            # Send spawn request to orchestrator
            spawn_message = {
                "message_type": "spawn_agent",
                "payload": {
                    "agent_type": agent_type,
                    "capabilities": capabilities,
                    "config": agent_config
                }
            }
            
            await self.redis_client.lpush("idfwu:mq:orchestrator", json.dumps(spawn_message))
            click.echo(f"✅ Spawn request sent for {agent_type}")
            
        except Exception as e:
            click.echo(f"Error spawning agent: {e}", err=True)
    
    async def deploy_swarm(self, epic_id: str, strategy: str = "default", agent_count: int = 20):
        """Deploy an agent swarm"""
        if not await self.connect_redis():
            return
        
        try:
            deploy_message = {
                "message_type": "deploy_swarm",
                "payload": {
                    "epic_id": epic_id,
                    "strategy": strategy,
                    "agent_count": agent_count
                }
            }
            
            await self.redis_client.lpush("idfwu:mq:orchestrator", json.dumps(deploy_message))
            click.echo(f"✅ Swarm deployment request sent for epic {epic_id}")
            click.echo(f"   Strategy: {strategy}")
            click.echo(f"   Agent Count: {agent_count}")
            
        except Exception as e:
            click.echo(f"Error deploying swarm: {e}", err=True)
    
    async def send_task(self, task_type: str, description: str, priority: str = "normal", requirements: Dict[str, Any] = None):
        """Send a task to the orchestrator"""
        if not await self.connect_redis():
            return
        
        try:
            task_message = {
                "message_type": "task_request",
                "payload": {
                    "task_type": task_type,
                    "description": description,
                    "priority": priority,
                    "requirements": requirements or {}
                }
            }
            
            await self.redis_client.lpush("idfwu:mq:orchestrator", json.dumps(task_message))
            click.echo(f"✅ Task sent: {description}")
            click.echo(f"   Type: {task_type}")
            click.echo(f"   Priority: {priority}")
            
        except Exception as e:
            click.echo(f"Error sending task: {e}", err=True)
    
    async def monitor_logs(self, follow: bool = False):
        """Monitor orchestrator logs"""
        log_file = Path(__file__).parent.parent.parent / "logs" / "orchestrator.log"
        
        if not log_file.exists():
            click.echo("Log file not found")
            return
        
        click.echo(f"📋 Monitoring logs: {log_file}")
        click.echo("=" * 50)
        
        if follow:
            # Follow mode - tail -f equivalent
            import subprocess
            try:
                subprocess.run(["tail", "-f", str(log_file)])
            except KeyboardInterrupt:
                click.echo("\nStopped monitoring logs")
        else:
            # Show last 50 lines
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        click.echo(line.rstrip())
            except Exception as e:
                click.echo(f"Error reading logs: {e}", err=True)


# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """IDFWU Orchestrator CLI - Manage the unified framework orchestrator"""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = OrchestratorCLI()


@cli.command()
@click.option('--background', '-b', is_flag=True, help='Run in background as daemon')
@click.pass_context
def start(ctx, background):
    """Start the orchestrator service"""
    asyncio.run(ctx.obj['cli'].start_service(background))


@cli.command()
@click.pass_context
def stop(ctx):
    """Stop the orchestrator service"""
    asyncio.run(ctx.obj['cli'].stop_service())


@cli.command()
@click.pass_context
def status(ctx):
    """Get orchestrator service status"""
    asyncio.run(ctx.obj['cli'].get_status())


@cli.command()
@click.pass_context
def agents(ctx):
    """List registered agents"""
    asyncio.run(ctx.obj['cli'].list_agents())


@cli.command()
@click.argument('agent_type')
@click.option('--capabilities', '-c', multiple=True, help='Agent capabilities')
@click.option('--config', '-cfg', default='{}', help='Agent configuration as JSON')
@click.pass_context
def spawn(ctx, agent_type, capabilities, config):
    """Spawn a new agent"""
    try:
        agent_config = json.loads(config)
    except json.JSONDecodeError:
        click.echo("Invalid JSON in config parameter", err=True)
        return
    
    asyncio.run(ctx.obj['cli'].spawn_agent(agent_type, list(capabilities), agent_config))


@cli.command()
@click.argument('epic_id')
@click.option('--strategy', '-s', default='default', help='Deployment strategy')
@click.option('--count', '-n', default=20, help='Number of agents to deploy')
@click.pass_context
def swarm(ctx, epic_id, strategy, count):
    """Deploy an agent swarm for an epic"""
    asyncio.run(ctx.obj['cli'].deploy_swarm(epic_id, strategy, count))


@cli.command()
@click.argument('task_type')
@click.argument('description')
@click.option('--priority', '-p', default='normal', 
              type=click.Choice(['low', 'normal', 'high', 'urgent']),
              help='Task priority')
@click.option('--requirements', '-r', default='{}', help='Task requirements as JSON')
@click.pass_context
def task(ctx, task_type, description, priority, requirements):
    """Send a task to the orchestrator"""
    try:
        req_dict = json.loads(requirements)
    except json.JSONDecodeError:
        click.echo("Invalid JSON in requirements parameter", err=True)
        return
    
    asyncio.run(ctx.obj['cli'].send_task(task_type, description, priority, req_dict))


@cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.pass_context
def logs(ctx, follow):
    """Monitor orchestrator logs"""
    asyncio.run(ctx.obj['cli'].monitor_logs(follow))


if __name__ == '__main__':
    cli()
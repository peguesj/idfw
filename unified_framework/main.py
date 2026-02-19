"""
IDFWU - IDEA Framework Unified
Main entry point for the unified framework
Linear Project: 4d649a6501f7
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click

# Ensure local imports work - add both unified_framework dir and project root
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.orchestrator_cli import OrchestratorCLI
from services.checkpoint_manager import CheckpointManager


@click.group()
@click.pass_context
def cli(ctx):
    """IDFW Unified Framework CLI

    Manage agents, orchestration, tasks, and the IDFW unified framework.
    """
    ctx.ensure_object(dict)
    ctx.obj['cli'] = OrchestratorCLI()


# --- Orchestrator service commands ---

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


# --- Agent management commands ---

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


# --- Task management commands ---

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


# --- Registry commands ---

@cli.command()
@click.option('--department', '-d', default=None, help='Filter by department')
@click.option('--implemented', is_flag=True, help='Show only implemented agents')
@click.option('--json-output', '--json', 'json_out', is_flag=True, help='Output as JSON')
def registry(department, implemented, json_out):
    """Show the agent registry with implementation status"""
    registry_path = Path(__file__).parent / "config" / "agent_registry.json"
    if not registry_path.exists():
        click.echo("Agent registry not found. Run 'init' first.", err=True)
        return

    data = json.loads(registry_path.read_text())

    agents_list = data["agents"]
    if department:
        agents_list = [a for a in agents_list if a["department"] == department]
    if implemented:
        agents_list = [a for a in agents_list if a["implementation_status"] == "implemented"]

    if json_out:
        click.echo(json.dumps(agents_list, indent=2))
        return

    click.echo(f"\nAgent Registry ({len(agents_list)} agents)")
    click.echo("=" * 70)
    for a in sorted(agents_list, key=lambda x: x["priority_rank"]):
        icon = "+" if a["implementation_status"] == "implemented" else "-"
        click.echo(f"  [{icon}] {a['id']:16s} {a['name']:30s} {a['department']:12s} {a['repo']}")

    summary = data["summary"]
    click.echo(f"\nImplemented: {summary['implemented']}/{summary['total_agents']}")


@cli.command()
@click.option('--schema', '-s', default=None, help='Schema file to validate against')
def validate(schema):
    """Validate FORCE schemas and agent registry"""
    registry_path = Path(__file__).parent / "config" / "agent_registry.json"
    errors = []

    # Validate registry
    if registry_path.exists():
        try:
            data = json.loads(registry_path.read_text())
            agent_ids = [a["id"] for a in data["agents"]]
            if len(agent_ids) != len(set(agent_ids)):
                errors.append("Duplicate agent IDs in registry")
            click.echo(f"Registry: {len(data['agents'])} agents, {data['summary']['implemented']} implemented")
        except (json.JSONDecodeError, KeyError) as e:
            errors.append(f"Registry parse error: {e}")
    else:
        errors.append("Agent registry not found")

    # Validate FORCE schemas if dev_sentinel is accessible
    force_dir = Path("/Users/jeremiah/Developer/dev_sentinel/.force")
    if force_dir.exists():
        tool_count = len(list((force_dir / "tools").glob("*.json")))
        constraint_count = len(list((force_dir / "constraints").glob("*.json")))
        pattern_count = len(list((force_dir / "patterns").glob("*.json")))
        click.echo(f"FORCE: {tool_count} tools, {constraint_count} constraints, {pattern_count} patterns")
    else:
        click.echo("FORCE directory not accessible")

    if errors:
        click.echo(f"\nErrors ({len(errors)}):")
        for e in errors:
            click.echo(f"  - {e}")
    else:
        click.echo("\nAll validations passed")


@cli.command()
@click.argument('wave', type=int)
@click.option('--stories', '-s', default='', help='Comma-separated story IDs')
@click.option('--files', '-f', default='', help='Comma-separated file paths to snapshot')
def checkpoint(wave, stories, files):
    """Create a state checkpoint before wave execution"""
    mgr = CheckpointManager()
    story_list = [s.strip() for s in stories.split(',') if s.strip()]
    file_list = [f.strip() for f in files.split(',') if f.strip()]
    cp = mgr.create_checkpoint(wave, story_list, file_list)
    click.echo(f"Checkpoint created: {cp.checkpoint_id}")
    click.echo(f"  Wave: {cp.wave}, Stories: {cp.stories}")
    click.echo(f"  Files snapshotted: {len(cp.files)}")


@cli.command()
@click.argument('checkpoint_id')
def rollback(checkpoint_id):
    """Rollback to a previous checkpoint"""
    mgr = CheckpointManager()
    success = mgr.rollback(checkpoint_id)
    if success:
        click.echo(f"Rollback to {checkpoint_id} succeeded")
    else:
        click.echo(f"Rollback to {checkpoint_id} failed", err=True)


@cli.command()
def checkpoints():
    """List all checkpoints"""
    mgr = CheckpointManager()
    cps = mgr.list_checkpoints()
    if not cps:
        click.echo("No checkpoints found")
        return
    click.echo(f"\nCheckpoints ({len(cps)}):")
    for cp in cps:
        click.echo(f"  {cp['checkpoint_id']}  wave={cp['wave']}  status={cp['status']}  files={len(cp['files'])}  {cp['created_at']}")


@cli.command()
def init():
    """Initialize the unified framework"""
    click.echo("Initializing IDFW Unified Framework...")
    click.echo("Linear Project: IDFWU (4d649a6501f7)")

    # Verify agent registry
    registry_path = Path(__file__).parent / "config" / "agent_registry.json"
    if registry_path.exists():
        data = json.loads(registry_path.read_text())
        click.echo(f"Agent Registry: {data['summary']['total_agents']} agents loaded")
    else:
        click.echo("Warning: Agent registry not found at config/agent_registry.json")

    # Verify orchestrator config
    config_path = Path(__file__).parent / "config" / "orchestrator.yaml"
    if config_path.exists():
        click.echo("Orchestrator config: loaded")
    else:
        click.echo("Warning: Orchestrator config not found")

    click.echo("Framework initialized.")


if __name__ == "__main__":
    cli()

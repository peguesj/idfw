#!/usr/bin/env python3
"""
Orchestrator Initialization Script for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This script initializes the orchestrator agent system with all necessary components:
- Validates environment and dependencies
- Sets up Redis and message queues
- Initializes the orchestrator service
- Provides management interface
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

import click
import redis
import yaml

# Ensure proper imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from unified_framework.services.orchestrator_service import OrchestratorService
from unified_framework.monitoring.dashboard import MonitoringDashboard
from unified_framework.cli.orchestrator_cli import OrchestratorCLI


class OrchestratorInitializer:
    """Handles initialization and setup of the orchestrator system"""
    
    def __init__(self):
        self.project_root = project_root
        self.config_path = project_root / "unified_framework" / "config" / "orchestrator.yaml"
        self.config = None
        self.redis_client = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        if not self.config_path.exists():
            click.echo(f"❌ Config file not found: {self.config_path}", err=True)
            return {}
        
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            click.echo(f"✅ Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            click.echo(f"❌ Failed to load config: {e}", err=True)
            return {}
    
    async def validate_dependencies(self) -> bool:
        """Validate all required dependencies"""
        click.echo("🔍 Validating dependencies...")
        
        checks = [
            ("Python version", self._check_python_version),
            ("Required packages", self._check_packages),
            ("Redis connectivity", self._check_redis),
            ("File permissions", self._check_permissions),
            ("Environment variables", self._check_environment),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = await check_func()
                if result:
                    click.echo(f"  ✅ {check_name}")
                else:
                    click.echo(f"  ❌ {check_name}")
                    all_passed = False
            except Exception as e:
                click.echo(f"  ❌ {check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    async def _check_python_version(self) -> bool:
        """Check Python version compatibility"""
        return sys.version_info >= (3, 8)
    
    async def _check_packages(self) -> bool:
        """Check required packages are installed"""
        required_packages = [
            'redis', 'pydantic', 'asyncio', 'gql', 'httpx', 'rich', 'click', 'yaml'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                click.echo(f"    Missing package: {package}")
                return False
        
        return True
    
    async def _check_redis(self) -> bool:
        """Check Redis connectivity"""
        try:
            redis_url = self.config.get("redis", {}).get("url", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            await client.ping()
            client.close()
            return True
        except Exception:
            return False
    
    async def _check_permissions(self) -> bool:
        """Check file system permissions"""
        required_dirs = [
            self.project_root / "logs",
            self.project_root / "data" / "cache",
            self.project_root / "unified_framework"
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                except Exception:
                    return False
            
            if not os.access(directory, os.W_OK):
                return False
        
        return True
    
    async def _check_environment(self) -> bool:
        """Check environment variables"""
        # Optional environment variables
        linear_api_key = os.getenv("LINEAR_API_KEY")
        if not linear_api_key:
            click.echo("    Warning: LINEAR_API_KEY not set (Linear integration disabled)")
        
        return True
    
    async def setup_redis_queues(self) -> bool:
        """Setup Redis message queues and data structures"""
        click.echo("🔧 Setting up Redis queues...")
        
        try:
            redis_url = self.config.get("redis", {}).get("url", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Initialize queue structures
            queue_setup = {
                "idfwu:orchestrator:status": json.dumps({
                    "status": "initializing",
                    "timestamp": time.time()
                }),
                "idfwu:orchestrator:agents": json.dumps({}),
                "idfwu:system:config": json.dumps(self.config)
            }
            
            for key, value in queue_setup.items():
                await self.redis_client.set(key, value)
            
            click.echo("  ✅ Redis queues initialized")
            return True
            
        except Exception as e:
            click.echo(f"  ❌ Redis setup failed: {e}")
            return False
    
    async def initialize_orchestrator(self) -> bool:
        """Initialize the orchestrator service"""
        click.echo("🚀 Initializing orchestrator...")
        
        try:
            service = OrchestratorService()
            
            # Initialize but don't start yet
            if await service.service.initialize() if hasattr(service, 'service') else True:
                click.echo("  ✅ Orchestrator initialized")
                return True
            else:
                click.echo("  ❌ Orchestrator initialization failed")
                return False
                
        except Exception as e:
            click.echo(f"  ❌ Orchestrator initialization error: {e}")
            return False
    
    async def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        status = {
            "timestamp": time.time(),
            "system": {
                "python_version": sys.version,
                "working_directory": str(self.project_root),
                "config_loaded": self.config is not None
            },
            "redis": {
                "connected": False,
                "url": self.config.get("redis", {}).get("url", "redis://localhost:6379")
            },
            "orchestrator": {
                "initialized": False,
                "service_available": False
            },
            "dependencies": {
                "validation_passed": await self.validate_dependencies()
            }
        }
        
        # Test Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                status["redis"]["connected"] = True
        except Exception:
            pass
        
        return status
    
    def display_status_report(self, status: Dict[str, Any]):
        """Display formatted status report"""
        click.echo("\n" + "="*60)
        click.echo("🎛️  IDFWU Orchestrator Status Report")
        click.echo("="*60)
        
        # System status
        click.echo("\n📋 System Information:")
        system = status["system"]
        click.echo(f"  Python Version: {system['python_version'].split()[0]}")
        click.echo(f"  Working Directory: {system['working_directory']}")
        click.echo(f"  Config Loaded: {'✅' if system['config_loaded'] else '❌'}")
        
        # Redis status
        click.echo("\n🔴 Redis Status:")
        redis_status = status["redis"]
        click.echo(f"  Connection: {'✅ Connected' if redis_status['connected'] else '❌ Disconnected'}")
        click.echo(f"  URL: {redis_status['url']}")
        
        # Dependencies
        click.echo("\n📦 Dependencies:")
        deps = status["dependencies"]
        click.echo(f"  Validation: {'✅ Passed' if deps['validation_passed'] else '❌ Failed'}")
        
        # Overall status
        all_good = (system['config_loaded'] and 
                   redis_status['connected'] and 
                   deps['validation_passed'])
        
        status_icon = "✅" if all_good else "❌"
        status_text = "READY" if all_good else "NOT READY"
        
        click.echo(f"\n🎯 Overall Status: {status_icon} {status_text}")
        
        if all_good:
            click.echo("\n🚀 Ready to start orchestrator service!")
            click.echo("   Use: python orchestrator_launcher.py")
        else:
            click.echo("\n⚠️  Please resolve issues before starting the service.")
        
        click.echo("="*60)


@click.group()
def cli():
    """IDFWU Orchestrator Initialization and Management"""
    pass


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
async def init(verbose):
    """Initialize the orchestrator system"""
    initializer = OrchestratorInitializer()
    
    # Load configuration
    initializer.config = initializer.load_config()
    if not initializer.config:
        click.echo("❌ Failed to load configuration", err=True)
        return
    
    click.echo("🎯 Initializing IDFWU Orchestrator System...")
    
    # Validate dependencies
    if not await initializer.validate_dependencies():
        click.echo("❌ Dependency validation failed", err=True)
        return
    
    # Setup Redis
    if not await initializer.setup_redis_queues():
        click.echo("❌ Redis setup failed", err=True)
        return
    
    # Initialize orchestrator
    if not await initializer.initialize_orchestrator():
        click.echo("❌ Orchestrator initialization failed", err=True)
        return
    
    click.echo("✅ Orchestrator system initialized successfully!")


@cli.command()
async def status():
    """Show orchestrator system status"""
    initializer = OrchestratorInitializer()
    initializer.config = initializer.load_config()
    
    status = await initializer.generate_status_report()
    initializer.display_status_report(status)


@cli.command()
@click.option('--background', '-b', is_flag=True, help='Run in background')
async def start(background):
    """Start the orchestrator service"""
    click.echo("🚀 Starting orchestrator service...")
    
    if background:
        # Start as background process
        import subprocess
        subprocess.Popen([
            sys.executable, 
            str(project_root / "orchestrator_launcher.py")
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("✅ Orchestrator started in background")
    else:
        # Start in foreground
        from orchestrator_launcher import main as launcher_main
        await launcher_main()


@cli.command()
async def stop():
    """Stop the orchestrator service"""
    click.echo("🛑 Stopping orchestrator service...")
    
    registration_file = project_root / "data" / "service_registration.json"
    if registration_file.exists():
        try:
            with open(registration_file) as f:
                registration = json.load(f)
            
            pid = registration.get("pid")
            if pid:
                import signal
                os.kill(pid, signal.SIGTERM)
                click.echo(f"✅ Stop signal sent to PID {pid}")
            else:
                click.echo("❌ No PID found in registration")
        except Exception as e:
            click.echo(f"❌ Failed to stop service: {e}")
    else:
        click.echo("❌ Service not found or not running")


@cli.command()
async def dashboard():
    """Launch the monitoring dashboard"""
    click.echo("🎛️ Launching monitoring dashboard...")
    
    try:
        dashboard = MonitoringDashboard()
        await dashboard.run()
    except KeyboardInterrupt:
        click.echo("\n✅ Dashboard stopped")
    except Exception as e:
        click.echo(f"❌ Dashboard failed: {e}")


@cli.command()
@click.argument('command', required=False)
async def manage(command):
    """Interactive management interface"""
    if not command:
        click.echo("🎛️ IDFWU Orchestrator Management Interface")
        click.echo("\nAvailable commands:")
        click.echo("  status  - Show system status")
        click.echo("  init    - Initialize system")
        click.echo("  start   - Start orchestrator")
        click.echo("  stop    - Stop orchestrator")
        click.echo("  dash    - Launch dashboard")
        click.echo("  cli     - Launch CLI interface")
        return
    
    if command == "status":
        await status.callback()
    elif command == "init":
        await init.callback(verbose=False)
    elif command == "start":
        await start.callback(background=False)
    elif command == "stop":
        await stop.callback()
    elif command == "dash":
        await dashboard.callback()
    elif command == "cli":
        cli_interface = OrchestratorCLI()
        await cli_interface.get_status()
    else:
        click.echo(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    # Convert async commands to sync for Click
    import asyncio
    
    def async_command(f):
        def wrapper(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return wrapper
    
    # Apply async wrapper to commands
    for command in [init, status, start, stop, dashboard, manage]:
        command.callback = async_command(command.callback)
    
    cli()
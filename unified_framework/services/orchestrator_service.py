"""
Orchestrator Service Runner for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides the service runner that initializes and maintains the orchestrator agent
as a persistent background service with monitoring, health checks, and automatic recovery.
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.orchestrator_agent import OrchestratorAgent
from agents.base_agent import LinearConfig, MessageBusConfig
from services.apm_client import register_agent, heartbeat, notify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(Path(__file__).resolve().parent.parent.parent / 'logs' / 'orchestrator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Service wrapper for the orchestrator agent that provides:
    - Persistent background operation
    - Health monitoring and recovery
    - Service lifecycle management
    - Configuration management
    - Signal handling for graceful shutdown
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path(__file__).resolve().parent.parent / "config.yaml")
        self.orchestrator: Optional[OrchestratorAgent] = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 5
        self.last_restart_time = None
        self.restart_cooldown = 60  # seconds
        
        # Service status
        self.service_status = {
            "status": "stopped",
            "start_time": None,
            "uptime": 0,
            "restart_count": 0,
            "last_error": None,
            "health_check_passed": False
        }
        
        # Configuration
        self.config = self._load_config()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load service configuration"""
        default_config = {
            "orchestrator": {
                "redis_url": "redis://localhost:6379",
                "heartbeat_interval": 30,
                "heartbeat_timeout": 90,
                "max_parallel_agents": 10,
                "max_api_calls_per_second": 5
            },
            "linear": {
                "api_key": os.getenv("LINEAR_API_KEY", ""),
                "project_id": "4d649a6501f7"
            },
            "logging": {
                "level": "INFO",
                "file": str(Path(__file__).resolve().parent.parent.parent / "logs" / "orchestrator.log")
            },
            "health_check": {
                "interval": 60,
                "timeout": 10,
                "failure_threshold": 3
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                import yaml
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config from {self.config_path}: {e}")
        
        return default_config
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self.stop())
    
    async def start(self) -> bool:
        """Start the orchestrator service"""
        try:
            logger.info("Starting Orchestrator Service...")

            # Register with CCEM APM
            register_agent("orchestrator-service", "idfw", "orchestrator", "active")
            notify("Orchestrator Starting", "IDFWU orchestrator service initializing", "info")
            
            # Initialize orchestrator agent
            linear_config = LinearConfig(
                api_key=self.config["linear"]["api_key"],
                project_id=self.config["linear"]["project_id"]
            ) if self.config["linear"]["api_key"] else None
            
            message_bus_config = MessageBusConfig(
                redis_url=self.config["orchestrator"]["redis_url"]
            )
            
            self.orchestrator = OrchestratorAgent(
                redis_url=self.config["orchestrator"]["redis_url"],
                linear_config=linear_config,
                message_bus_config=message_bus_config
            )
            
            # Initialize orchestrator
            if not await self.orchestrator.initialize():
                raise Exception("Failed to initialize orchestrator agent")
            
            # Start orchestrator
            await self.orchestrator.start()
            
            # Update service status
            self.running = True
            self.service_status.update({
                "status": "running",
                "start_time": datetime.utcnow().isoformat(),
                "last_error": None
            })
            
            logger.info("Orchestrator Service started successfully")
            
            # Start background monitoring tasks
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._status_updater())
            asyncio.create_task(self._restart_manager())
            
            # Register built-in hooks
            self._register_builtin_hooks()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start orchestrator service: {e}")
            self.service_status["last_error"] = str(e)
            return False
    
    async def stop(self) -> bool:
        """Stop the orchestrator service"""
        try:
            logger.info("Stopping Orchestrator Service...")
            
            self.running = False
            
            if self.orchestrator:
                await self.orchestrator.stop()
            
            # Update service status
            self.service_status.update({
                "status": "stopped",
                "uptime": 0
            })
            
            logger.info("Orchestrator Service stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping orchestrator service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the orchestrator service"""
        logger.info("Restarting Orchestrator Service...")
        
        # Check restart limits
        current_time = time.time()
        if (self.last_restart_time and 
            current_time - self.last_restart_time < self.restart_cooldown):
            logger.warning("Restart cooldown in effect, delaying restart...")
            await asyncio.sleep(self.restart_cooldown)
        
        if self.restart_count >= self.max_restarts:
            logger.error(f"Maximum restart attempts ({self.max_restarts}) reached")
            return False
        
        # Stop current instance
        await self.stop()
        
        # Wait a moment before restarting
        await asyncio.sleep(5)
        
        # Start new instance
        success = await self.start()
        
        if success:
            self.restart_count += 1
            self.last_restart_time = current_time
            logger.info(f"Service restarted successfully (restart #{self.restart_count})")
        else:
            logger.error("Service restart failed")
        
        return success
    
    async def _health_monitor(self):
        """Monitor orchestrator health and trigger recovery if needed"""
        consecutive_failures = 0
        failure_threshold = self.config["health_check"]["failure_threshold"]
        check_interval = self.config["health_check"]["interval"]
        
        while self.running:
            try:
                # Perform health check
                if await self._perform_health_check():
                    consecutive_failures = 0
                    self.service_status["health_check_passed"] = True
                else:
                    consecutive_failures += 1
                    self.service_status["health_check_passed"] = False
                    
                    if consecutive_failures >= failure_threshold:
                        logger.error(f"Health check failed {consecutive_failures} times, triggering restart")
                        asyncio.create_task(self.restart())
                        break
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(10)
    
    async def _perform_health_check(self) -> bool:
        """Perform health check on orchestrator"""
        try:
            if not self.orchestrator or not self.orchestrator._running:
                return False
            
            # Check if orchestrator is responsive
            status = await self.orchestrator.get_system_status()
            
            # Verify orchestrator status
            if status.get("orchestrator_status") != "active":
                return False
            
            # Check Redis connection
            if self.orchestrator.redis_client:
                await self.orchestrator.redis_client.ping()
            
            # Check agent registry responsiveness
            if not hasattr(self.orchestrator, 'agent_registry'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def _status_updater(self):
        """Update service status metrics"""
        start_time = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                self.service_status.update({
                    "uptime": current_time - start_time,
                    "restart_count": self.restart_count,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Log status periodically
                if int(current_time) % 300 == 0:  # Every 5 minutes
                    logger.info(f"Service Status: {self.service_status}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in status updater: {e}")
                await asyncio.sleep(5)
    
    async def _restart_manager(self):
        """Manage restart logic and recovery"""
        while self.running:
            try:
                # Reset restart count after successful uptime
                if (self.service_status["uptime"] > 3600 and  # 1 hour
                    self.restart_count > 0):
                    logger.info("Resetting restart count after successful uptime")
                    self.restart_count = 0
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in restart manager: {e}")
                await asyncio.sleep(10)
    
    def _register_builtin_hooks(self):
        """Register built-in hooks for monitoring and logging"""
        if not self.orchestrator:
            return
        
        async def log_agent_spawn(context):
            agent_type = context.get("agent_type")
            logger.info(f"Agent spawn hook triggered for: {agent_type}")
        
        async def log_task_completion(context):
            task = context.get("task")
            result = context.get("result")
            logger.info(f"Task completed: {task.id} with result keys: {list(result.keys()) if result else []}")
        
        async def log_error(context):
            task = context.get("task")
            permanent_failure = context.get("permanent_failure", False)
            if permanent_failure:
                logger.error(f"Permanent task failure: {task.id} - {task.error}")
        
        self.orchestrator.register_hook('before_agent_spawn', log_agent_spawn)
        self.orchestrator.register_hook('after_agent_complete', log_task_completion)
        self.orchestrator.register_hook('on_error', log_error)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        status = self.service_status.copy()
        
        if self.orchestrator and self.running:
            orchestrator_status = await self.orchestrator.get_system_status()
            status["orchestrator"] = orchestrator_status
        
        return status
    
    async def run_forever(self):
        """Run the service indefinitely"""
        try:
            if not await self.start():
                logger.error("Failed to start service")
                return
            
            logger.info("Orchestrator Service running in background mode...")
            
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in service loop: {e}")
        finally:
            await self.stop()


async def main():
    """Main entry point for the service"""
    service = OrchestratorService()
    
    try:
        await service.run_forever()
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs(Path(__file__).resolve().parent.parent.parent / "logs", exist_ok=True)
    
    # Run the service
    asyncio.run(main())
#!/usr/bin/env python3
"""
Orchestrator Launcher for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This script launches the orchestrator agent as a persistent background service
with comprehensive monitoring, health checks, and automatic recovery capabilities.
"""

import asyncio
import os
import sys
import signal
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure proper imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from unified_framework.services.orchestrator_service import OrchestratorService
from unified_framework.core.message_protocols import CommunicationProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'orchestrator_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OrchestratorLauncher:
    """
    Launcher for the orchestrator service with enhanced features:
    - Process management and monitoring
    - Configuration validation
    - Health monitoring
    - Automatic recovery
    - Status reporting
    """
    
    def __init__(self):
        self.service: OrchestratorService = None
        self.running = False
        self.launch_time = None
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Configuration
        self.config = self._load_launcher_config()
        
        # Status tracking
        self.status = {
            "launcher_version": "1.0.0",
            "status": "initializing",
            "launch_time": None,
            "uptime": 0,
            "restarts": 0,
            "last_health_check": None,
            "errors": [],
            "service_status": None
        }
        
        # Setup signal handlers
        self._setup_signals()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            project_root / 'logs',
            project_root / 'data' / 'cache',
            project_root / 'unified_framework' / 'services'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_launcher_config(self) -> Dict[str, Any]:
        """Load launcher configuration"""
        config_file = project_root / 'unified_framework' / 'launcher_config.json'
        
        default_config = {
            "health_check_interval": 30,
            "max_restart_attempts": 5,
            "restart_delay": 10,
            "status_report_interval": 300,
            "log_retention_days": 7,
            "redis_connection_timeout": 10,
            "service_startup_timeout": 60
        }
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
                logger.info(f"Loaded launcher config from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load launcher config: {e}, using defaults")
        
        return default_config
    
    def _setup_signals(self):
        """Setup signal handlers"""
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        if hasattr(signal, 'SIGUSR1'):
            signal.signal(signal.SIGUSR1, self._handle_status_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())
    
    def _handle_status_signal(self, signum, frame):
        """Handle status query signals"""
        logger.info("Status query requested via signal")
        asyncio.create_task(self._log_status())
    
    async def launch(self) -> bool:
        """Launch the orchestrator service"""
        try:
            logger.info("🚀 Launching IDFWU Orchestrator Service...")
            
            self.launch_time = datetime.utcnow()
            self.status.update({
                "status": "launching",
                "launch_time": self.launch_time.isoformat()
            })
            
            # Pre-launch checks
            if not await self._pre_launch_checks():
                logger.error("Pre-launch checks failed")
                return False
            
            # Initialize service
            self.service = OrchestratorService()
            
            # Start service
            if not await self.service.start():
                logger.error("Failed to start orchestrator service")
                return False
            
            # Update status
            self.running = True
            self.status["status"] = "running"
            
            # Start monitoring tasks
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._status_reporter())
            asyncio.create_task(self._log_rotator())
            
            logger.info("✅ Orchestrator Service launched successfully")
            
            # Register with system
            await self._register_service()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch orchestrator: {e}")
            self.status["errors"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "type": "launch_failure"
            })
            return False
    
    async def _pre_launch_checks(self) -> bool:
        """Perform pre-launch validation checks"""
        logger.info("Performing pre-launch checks...")
        
        checks = [
            ("Redis connectivity", self._check_redis),
            ("Directory permissions", self._check_directories),
            ("Configuration validation", self._check_configuration),
            ("Port availability", self._check_ports),
        ]
        
        for check_name, check_func in checks:
            try:
                result = await check_func()
                if result:
                    logger.info(f"✅ {check_name}: PASSED")
                else:
                    logger.error(f"❌ {check_name}: FAILED")
                    return False
            except Exception as e:
                logger.error(f"❌ {check_name}: ERROR - {e}")
                return False
        
        logger.info("All pre-launch checks passed")
        return True
    
    async def _check_redis(self) -> bool:
        """Check Redis connectivity"""
        try:
            import redis
            client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await client.ping()
            client.close()
            return True
        except Exception:
            return False
    
    async def _check_directories(self) -> bool:
        """Check directory permissions"""
        test_dirs = [
            project_root / 'logs',
            project_root / 'data' / 'cache'
        ]
        
        for directory in test_dirs:
            if not directory.exists() or not os.access(directory, os.W_OK):
                return False
        
        return True
    
    async def _check_configuration(self) -> bool:
        """Validate configuration"""
        required_config = ['health_check_interval', 'max_restart_attempts']
        
        for key in required_config:
            if key not in self.config:
                return False
        
        return True
    
    async def _check_ports(self) -> bool:
        """Check if required ports are available"""
        # This would check if any required ports are free
        # For now, just return True as we're using Redis
        return True
    
    async def _health_monitor(self):
        """Monitor service health and trigger recovery if needed"""
        consecutive_failures = 0
        max_failures = 3
        
        while self.running:
            try:
                # Perform health check
                is_healthy = await self._perform_health_check()
                
                if is_healthy:
                    consecutive_failures = 0
                    self.status["last_health_check"] = datetime.utcnow().isoformat()
                else:
                    consecutive_failures += 1
                    logger.warning(f"Health check failed ({consecutive_failures}/{max_failures})")
                    
                    if consecutive_failures >= max_failures:
                        logger.error("Service unhealthy, attempting restart...")
                        await self._attempt_recovery()
                        consecutive_failures = 0
                
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(10)
    
    async def _perform_health_check(self) -> bool:
        """Perform comprehensive health check"""
        try:
            if not self.service or not self.service.running:
                return False
            
            # Get service status
            service_status = await self.service.get_status()
            self.status["service_status"] = service_status
            
            # Check critical components
            if service_status.get("status") != "running":
                return False
            
            # Check for recent errors
            if len(self.status["errors"]) > 10:  # Too many recent errors
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    async def _attempt_recovery(self):
        """Attempt to recover the service"""
        logger.info("Attempting service recovery...")
        
        try:
            # Stop current service
            if self.service:
                await self.service.stop()
            
            # Wait before restart
            await asyncio.sleep(self.config["restart_delay"])
            
            # Restart service
            self.service = OrchestratorService()
            if await self.service.start():
                self.status["restarts"] += 1
                logger.info("✅ Service recovery successful")
            else:
                logger.error("❌ Service recovery failed")
                
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
    
    async def _status_reporter(self):
        """Periodically report status"""
        while self.running:
            try:
                await self._log_status()
                await self._save_status()
                await asyncio.sleep(self.config["status_report_interval"])
            except Exception as e:
                logger.error(f"Error in status reporter: {e}")
                await asyncio.sleep(60)
    
    async def _log_status(self):
        """Log current status"""
        if self.launch_time:
            uptime = (datetime.utcnow() - self.launch_time).total_seconds()
            self.status["uptime"] = uptime
        
        logger.info(f"📊 Status Report: {self.status['status']} | "
                   f"Uptime: {self.status['uptime']:.0f}s | "
                   f"Restarts: {self.status['restarts']}")
    
    async def _save_status(self):
        """Save status to file"""
        status_file = project_root / 'data' / 'orchestrator_status.json'
        try:
            with open(status_file, 'w') as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")
    
    async def _log_rotator(self):
        """Rotate and clean up old logs"""
        while self.running:
            try:
                log_dir = project_root / 'logs'
                retention_days = self.config["log_retention_days"]
                
                # Clean up old log files
                for log_file in log_dir.glob("*.log*"):
                    file_age = (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days
                    if file_age > retention_days:
                        log_file.unlink()
                        logger.info(f"Removed old log file: {log_file}")
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Error in log rotator: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _register_service(self):
        """Register service with system"""
        registration_data = {
            "service_name": "idfwu-orchestrator",
            "pid": os.getpid(),
            "launch_time": self.launch_time.isoformat(),
            "version": self.status["launcher_version"],
            "working_directory": str(project_root)
        }
        
        registration_file = project_root / 'data' / 'service_registration.json'
        try:
            with open(registration_file, 'w') as f:
                json.dump(registration_data, f, indent=2)
            logger.info(f"Service registered with PID {os.getpid()}")
        except Exception as e:
            logger.warning(f"Failed to register service: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Initiating graceful shutdown...")
        
        self.running = False
        self.status["status"] = "shutting_down"
        
        try:
            if self.service:
                await self.service.stop()
            
            # Clean up registration
            registration_file = project_root / 'data' / 'service_registration.json'
            if registration_file.exists():
                registration_file.unlink()
            
            self.status["status"] = "stopped"
            await self._save_status()
            
            logger.info("✅ Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def run_forever(self):
        """Run the launcher indefinitely"""
        try:
            if not await self.launch():
                logger.error("Failed to launch service")
                return False
            
            logger.info("🔄 Orchestrator running in persistent mode...")
            logger.info("Use Ctrl+C to stop, or send SIGUSR1 for status")
            
            # Main loop
            while self.running:
                await asyncio.sleep(1)
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            await self.shutdown()
            return True
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await self.shutdown()
            return False


async def main():
    """Main entry point"""
    launcher = OrchestratorLauncher()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            # Show status and exit
            status_file = project_root / 'data' / 'orchestrator_status.json'
            if status_file.exists():
                with open(status_file) as f:
                    status = json.load(f)
                print(json.dumps(status, indent=2))
            else:
                print("No status file found - service may not be running")
            return
        
        elif command == "stop":
            # Send stop signal to running service
            registration_file = project_root / 'data' / 'service_registration.json'
            if registration_file.exists():
                with open(registration_file) as f:
                    registration = json.load(f)
                pid = registration.get("pid")
                if pid:
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"Stop signal sent to PID {pid}")
                    except ProcessLookupError:
                        print("Service is not running")
                        registration_file.unlink()
                else:
                    print("No PID found in registration")
            else:
                print("Service registration not found")
            return
    
    # Default: start the service
    success = await launcher.run_forever()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
"""
Services module for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides service infrastructure including:
- Orchestrator service management
- Background task processing
- Health monitoring
- Service discovery
"""

from .orchestrator_service import OrchestratorService

__all__ = ['OrchestratorService']
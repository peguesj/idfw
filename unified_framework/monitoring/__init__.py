"""
Monitoring module for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides monitoring and observability tools including:
- Real-time dashboard
- Metrics collection
- Alert management
- Performance tracking
"""

from .dashboard import MonitoringDashboard, MetricsCollector

__all__ = ['MonitoringDashboard', 'MetricsCollector']
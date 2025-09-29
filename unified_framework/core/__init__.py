"""
Core Module for IDFWU Unified Framework
Linear Project: 4d649a6501f7
"""

from unified_framework.core.schema_bridge import (
    SchemaUnifier,
    SchemaRegistry,
    SchemaDefinition,
    SchemaMetadata,
    SchemaFormat,
    SchemaNamespace,
    ConversionRule,
    initialize_schema_bridge,
    create_default_conversion_rules,
)

from unified_framework.core.state_manager import (
    StateManager,
    StateVariable,
    VariableScope,
    VariableType,
    ConflictResolution,
    StateSnapshot,
    StateObserver,
)

__all__ = [
    # Schema Bridge
    "SchemaUnifier",
    "SchemaRegistry",
    "SchemaDefinition",
    "SchemaMetadata",
    "SchemaFormat",
    "SchemaNamespace",
    "ConversionRule",
    "initialize_schema_bridge",
    "create_default_conversion_rules",
    # State Manager
    "StateManager",
    "StateVariable",
    "VariableScope",
    "VariableType",
    "ConflictResolution",
    "StateSnapshot",
    "StateObserver",
]
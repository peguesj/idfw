"""
IDFWU - IDEA Framework Unified
Linear Project: 4d649a6501f7

Unified framework for IDFW (IDEA Definition Framework) and Dev Sentinel integration.
"""

__version__ = "1.0.0"
__project_id__ = "4d649a6501f7"

# Import main components
from unified_framework.agents import (
    BaseAgent,
    Task,
    TaskStatus,
    Message,
    MessagePriority,
    AgentStatus,
    PerformanceMetrics,
    LinearConfig,
    MessageBusConfig,
)

from unified_framework.core import (
    SchemaUnifier,
    SchemaRegistry,
    SchemaDefinition,
    SchemaFormat,
    SchemaNamespace,
    StateManager,
    StateVariable,
    VariableScope,
    VariableType,
    initialize_schema_bridge,
)

from unified_framework.commands import (
    CommandProcessor,
    Command,
    CommandPrefix,
    CommandContext,
    CommandResult,
    create_default_processor,
)

from unified_framework.mcp import (
    MCPServer,
    Tool,
    ToolRegistry,
    ToolCategory,
    create_mcp_server,
)

__all__ = [
    # Version info
    "__version__",
    "__project_id__",

    # Agents
    "BaseAgent",
    "Task",
    "TaskStatus",
    "Message",
    "MessagePriority",
    "AgentStatus",
    "PerformanceMetrics",
    "LinearConfig",
    "MessageBusConfig",

    # Core
    "SchemaUnifier",
    "SchemaRegistry",
    "SchemaDefinition",
    "SchemaFormat",
    "SchemaNamespace",
    "StateManager",
    "StateVariable",
    "VariableScope",
    "VariableType",
    "initialize_schema_bridge",

    # Commands
    "CommandProcessor",
    "Command",
    "CommandPrefix",
    "CommandContext",
    "CommandResult",
    "create_default_processor",

    # MCP
    "MCPServer",
    "Tool",
    "ToolRegistry",
    "ToolCategory",
    "create_mcp_server",
]
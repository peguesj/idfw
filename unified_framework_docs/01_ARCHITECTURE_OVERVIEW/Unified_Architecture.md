# Unified Framework Architecture Design

## Vision

Create a comprehensive development framework that seamlessly combines IDFW's structured project definitions with Dev Sentinel's autonomous execution capabilities, providing a complete solution from project conception to implementation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                    (CLI, VS Code, Web API)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    MCP Protocol Layer                        │
│              (Model Context Protocol Server)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Unified Command Processor                   │
│           (YUNG Commands + IDFW Actions + Extensions)        │
└──────┬──────────────────────────────────────┬───────────────┘
       │                                      │
┌──────▼────────────┐              ┌─────────▼────────────────┐
│   IDFW Engine     │              │   Dev Sentinel Engine    │
│                   │              │                          │
│ • Schemas         │              │ • FORCE Framework        │
│ • Generators      │              │ • Agent System           │
│ • Variables       │              │ • Message Bus            │
│ • Validators      │              │ • Task Manager           │
└──────┬────────────┘              └─────────┬────────────────┘
       │                                      │
       └──────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Unified State Manager                     │
│            (Variables, Context, Configuration)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Storage & Persistence                     │
│              (File System, Database, Cache)                  │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Unified Command Processor (UCP)

The central command routing and processing system that understands both YUNG commands and IDFW actions.

```python
class UnifiedCommandProcessor:
    """Central command processing for unified framework"""

    def __init__(self):
        self.yung_processor = YUNGProcessor()
        self.idfw_processor = IDFWProcessor()
        self.extension_processor = ExtensionProcessor()
        self.context_manager = UnifiedContextManager()

    async def process(self, command: str, context: Dict[str, Any]):
        # Determine command type and route appropriately
        if command.startswith('$'):
            return await self.process_yung(command, context)
        elif command.startswith('@'):
            return await self.process_idfw(command, context)
        elif command.startswith('#'):
            return await self.process_extension(command, context)
        else:
            return await self.process_natural(command, context)
```

### 2. Unified Schema System (USS)

A comprehensive schema management system that bridges IDFW and Force schemas.

```python
class UnifiedSchemaSystem:
    """Manages all schemas across the unified framework"""

    schemas = {
        'idfw': IDFWSchemaRegistry(),
        'force': ForceSchemaRegistry(),
        'unified': UnifiedSchemaRegistry()
    }

    def validate(self, data: Any, schema_ref: str):
        # Intelligent validation across schema types
        namespace, schema_id = self.parse_ref(schema_ref)
        return self.schemas[namespace].validate(data, schema_id)

    def convert(self, data: Any, from_schema: str, to_schema: str):
        # Convert between schema formats
        converter = self.get_converter(from_schema, to_schema)
        return converter.transform(data)
```

### 3. Intelligent Agent Orchestrator (IAO)

Manages all agents including native Dev Sentinel agents and wrapped IDFW generators.

```python
class IntelligentAgentOrchestrator:
    """Orchestrates all agents in the unified system"""

    def __init__(self):
        self.native_agents = self.load_dev_sentinel_agents()
        self.idfw_agents = self.wrap_idfw_generators()
        self.message_bus = UnifiedMessageBus()
        self.task_manager = UnifiedTaskManager()

    async def execute_workflow(self, workflow: WorkflowDefinition):
        # Execute complex multi-agent workflows
        tasks = self.decompose_workflow(workflow)

        for task in tasks:
            agent = self.select_agent(task)
            result = await agent.execute(task)

            # Publish results for other agents
            await self.message_bus.publish(
                f"workflow.{workflow.id}.task.{task.id}",
                result
            )
```

### 4. Unified State Manager (USM)

Maintains consistent state across IDFW variables and Dev Sentinel agent states.

```python
class UnifiedStateManager:
    """Manages state across the entire framework"""

    def __init__(self):
        self.idfw_variables = IDFWVariableManager()
        self.agent_states = AgentStateManager()
        self.global_context = GlobalContextManager()
        self.cache = UnifiedCache()

    def get_state(self, key: str, scope: str = 'global'):
        # Hierarchical state resolution
        search_order = [
            ('cache', self.cache),
            ('agent', self.agent_states),
            ('idfw', self.idfw_variables),
            ('global', self.global_context)
        ]

        for source_name, source in search_order:
            if value := source.get(key, scope):
                return value, source_name

        return None, None

    def set_state(self, key: str, value: Any, scope: str = 'global'):
        # Intelligent state distribution
        if self.is_idfw_variable(key):
            self.idfw_variables.set(key, value, scope)
        elif self.is_agent_state(key):
            self.agent_states.set(key, value, scope)
        else:
            self.global_context.set(key, value, scope)

        # Notify observers
        self.notify_state_change(key, value, scope)
```

### 5. Unified Tool Registry (UTR)

Combines Force tools with IDFW actions exposed as tools.

```python
class UnifiedToolRegistry:
    """Central registry for all tools in the framework"""

    def __init__(self):
        self.tools = {}
        self.categories = defaultdict(list)
        self.load_force_tools()
        self.load_idfw_tools()
        self.load_extensions()

    def register_tool(self, tool: ToolDefinition):
        # Register with validation and conflict resolution
        if tool.id in self.tools:
            tool = self.resolve_conflict(tool, self.tools[tool.id])

        self.tools[tool.id] = tool
        self.categories[tool.category].append(tool.id)

        # Update MCP server
        self.update_mcp_registration(tool)
```

## Key Design Patterns

### 1. Adapter Pattern
Convert between IDFW and Dev Sentinel components seamlessly.

```python
class IDFWToAgentAdapter:
    """Adapts IDFW generators to Dev Sentinel agent interface"""

    def __init__(self, idfw_component):
        self.component = idfw_component

    async def execute(self, task: AgentTask) -> AgentResult:
        # Convert agent task to IDFW format
        idfw_input = self.convert_task(task)

        # Execute IDFW component
        idfw_output = await self.component.generate(idfw_input)

        # Convert result to agent format
        return self.convert_result(idfw_output)
```

### 2. Bridge Pattern
Bridge between different schema systems.

```python
class SchemaBridge:
    """Bridges between IDFW and Force schema systems"""

    def __init__(self):
        self.idfw_impl = IDFWSchemaImplementation()
        self.force_impl = ForceSchemaImplementation()

    def validate(self, data: Any, schema_type: str):
        if schema_type.startswith('idfw:'):
            return self.idfw_impl.validate(data, schema_type)
        elif schema_type.startswith('force:'):
            return self.force_impl.validate(data, schema_type)
        else:
            return self.unified_validate(data, schema_type)
```

### 3. Observer Pattern
State changes propagate across systems.

```python
class StateObserver:
    """Observes state changes and synchronizes systems"""

    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, state_change: StateChange):
        for observer in self.observers:
            observer.update(state_change)
```

### 4. Strategy Pattern
Different execution strategies for different command types.

```python
class ExecutionStrategy(ABC):
    @abstractmethod
    async def execute(self, command: Command) -> Result:
        pass

class IDFWExecutionStrategy(ExecutionStrategy):
    async def execute(self, command: Command) -> Result:
        # IDFW-specific execution logic
        pass

class ForceExecutionStrategy(ExecutionStrategy):
    async def execute(self, command: Command) -> Result:
        # Force-specific execution logic
        pass
```

## Integration Layers

### 1. MCP Integration Layer

```python
class UnifiedMCPServer:
    """Unified MCP server for the framework"""

    def __init__(self):
        self.server = MCPServer("unified-framework")
        self.tool_registry = UnifiedToolRegistry()
        self.command_processor = UnifiedCommandProcessor()

    @server.list_tools()
    async def list_tools(self):
        # List all available tools from both systems
        return self.tool_registry.get_all_tools()

    @server.call_tool()
    async def call_tool(self, name: str, arguments: dict):
        # Execute tool with unified context
        tool = self.tool_registry.get_tool(name)
        context = self.build_context(arguments)
        return await tool.execute(context)
```

### 2. CLI Integration Layer

```python
@click.group()
def cli():
    """Unified Framework CLI"""
    pass

@cli.command()
@click.argument('command')
def execute(command):
    """Execute a unified command"""
    processor = UnifiedCommandProcessor()
    result = processor.process(command)
    click.echo(result)

@cli.command()
def interactive():
    """Start interactive mode"""
    shell = UnifiedInteractiveShell()
    shell.run()
```

### 3. Web API Integration Layer

```python
app = FastAPI(title="Unified Framework API")

@app.post("/execute")
async def execute_command(request: CommandRequest):
    """Execute a command through the API"""
    processor = UnifiedCommandProcessor()
    result = await processor.process(
        request.command,
        request.context
    )
    return CommandResponse(result=result)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time communication"""
    await websocket.accept()
    handler = WebSocketHandler(websocket)
    await handler.handle()
```

## Data Flow

### 1. Command Execution Flow

```
User Input → MCP/CLI/API → Unified Command Processor
    ↓
Command Analysis & Routing
    ↓
[IDFW Engine / Dev Sentinel Engine]
    ↓
Agent Selection & Task Creation
    ↓
Agent Execution with State Management
    ↓
Result Aggregation & Formatting
    ↓
Response to User
```

### 2. State Synchronization Flow

```
State Change Event → State Manager
    ↓
Validation & Conflict Resolution
    ↓
Update IDFW Variables ←→ Update Agent States
    ↓
Cache Update & Persistence
    ↓
Observer Notifications
```

## Configuration

### Unified Configuration Structure

```yaml
unified_framework:
  version: "1.0.0"

  idfw:
    enabled: true
    schema_version: "2020-12"
    generators:
      - IDDG
      - IDPG
      - IDAA

  dev_sentinel:
    enabled: true
    agents:
      - SAA
      - VCMA
      - VCLA
      - CDIA
      - RDIA

  integration:
    command_prefix:
      yung: "$"
      idfw: "@"
      extension: "#"

    mcp:
      stdio: true
      http: true
      port: 8888

    state:
      sync_interval: 1000  # ms
      cache_ttl: 3600      # seconds
```

## Benefits of Unified Architecture

### 1. Seamless Integration
- Single command interface for all operations
- Unified state management across systems
- Consistent validation and error handling

### 2. Enhanced Capabilities
- IDFW project definitions with autonomous execution
- Force tools aware of IDFW project context
- Multi-agent workflows with IDFW generators

### 3. Developer Experience
- One CLI for everything
- VS Code integration through MCP
- Comprehensive documentation and tooling

### 4. Scalability
- Modular architecture for easy extension
- Distributed agent execution
- Efficient state management and caching

### 5. Maintainability
- Clear separation of concerns
- Well-defined interfaces
- Comprehensive testing framework

## Future Extensions

### 1. Plugin System
```python
class UnifiedPlugin(ABC):
    @abstractmethod
    def register(self, framework: UnifiedFramework):
        pass

    @abstractmethod
    def execute(self, command: str) -> Result:
        pass
```

### 2. Machine Learning Integration
- Learn from execution patterns
- Optimize agent selection
- Predictive command suggestions

### 3. Distributed Execution
- Agent distribution across machines
- Cloud-based execution
- Collaborative development support

---

*Design Version: 1.0.0*
*Date: 2025-09-29*
*Status: Architecture Design Complete*
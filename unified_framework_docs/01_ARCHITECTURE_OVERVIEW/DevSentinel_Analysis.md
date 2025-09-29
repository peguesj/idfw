# Dev Sentinel - Complete Architecture Analysis

## Overview

Dev Sentinel (v0.4.3) is a sophisticated AI-powered development assistant framework that combines autonomous agents with the FORCE (Federated Orchestration & Reporting for Copilot Execution) development system. It provides comprehensive development workflow automation through intelligent agents and MCP integration.

## Core Architecture

### 1. Multi-Agent System

#### 1.1 Base Agent Framework
```python
class BaseAgent:
    """Foundation for all Dev Sentinel agents"""
    - Lifecycle management (init, startup, shutdown)
    - Status tracking and state transitions
    - Message bus integration
    - Task processing pipeline
    - Activity logging and metrics
```

#### 1.2 Specialized Agents

**SAA (Static Analysis Agent)**
- Multi-language support (Python, JS/TS, Ruby, Elixir, PHP, Swift, Go, Shell)
- Code quality metrics and scoring
- Security vulnerability detection
- Performance analysis

**VCMA (Version Control Master Agent)**
- Repository state management
- Intelligent commit grouping
- Branch strategy enforcement
- Semantic versioning automation

**VCLA (Version Control Listener Agent)**
- File system monitoring
- Change detection and tracking
- Event publication to message bus
- Real-time repository updates

**CDIA (Code Documentation Inspector Agent)**
- Documentation coverage analysis
- Docstring validation
- API documentation generation
- Cross-reference checking

**RDIA (README Inspector Agent)**
- README structure validation
- Section completeness checking
- Example code verification
- Link validation

### 2. FORCE Framework

#### 2.1 Architecture Components
```
force/
├── tools/           # 40+ executable development actions
├── patterns/        # Reusable workflow templates
├── constraints/     # Quality rules and validation
├── governance/      # Policy enforcement
├── learning/        # System improvement
└── schemas/         # JSON schema definitions
```

#### 2.2 Tool System

**Tool Categories:**
- **Git Tools**: Status, commit, branch, merge operations
- **Project Tools**: Migration, scaffolding, structure analysis
- **Documentation Tools**: Sync, generation, validation
- **System Tools**: File operations, process management
- **Testing Tools**: Test execution, coverage analysis
- **Infrastructure Tools**: Deployment, monitoring, scaling

**Tool Definition Structure:**
```json
{
  "id": "tool_name",
  "category": "git|project|docs|system",
  "description": "Tool purpose",
  "parameters": {
    "param1": {"type": "string", "required": true},
    "param2": {"type": "number", "default": 0}
  },
  "execution": {
    "strategy": "sequential|parallel|conditional",
    "commands": ["cmd1", "cmd2"],
    "validation": {"success_criteria": "..."}
  }
}
```

#### 2.3 Pattern System
- **Workflow Templates**: Predefined task sequences
- **Composition**: Patterns can include other patterns
- **Conditional Logic**: Branch based on results
- **Iteration Support**: Loop constructs for repetitive tasks

### 3. YUNG Command System

#### 3.1 Command Structure
```
$COMMAND [SCOPE] [ACTION] [OPTIONS]

Examples:
$VIC ALL                    # Validation check all files
$CODE TIER=backend FIX     # Fix backend code issues
$VCS COMMIT MESSAGE="fix"  # Commit with message
$DIAGRAM ARCH FORMAT=svg   # Generate architecture diagram
```

#### 3.2 Command Categories
- **$VIC**: Validation and integrity checking
- **$CODE**: Code generation and modification
- **$VCS**: Version control operations
- **$TEST**: Test execution and coverage
- **$INFRA**: Infrastructure management
- **$FAST**: Fast-agent integration
- **$DIAGRAM**: Diagram generation
- **$MAN**: Manual and help system

#### 3.3 Command Processing Pipeline
1. **Parse**: Regex-based command extraction
2. **Validate**: Parameter and syntax checking
3. **Route**: Map to appropriate agent/tool
4. **Execute**: Async execution with context
5. **Aggregate**: Combine results from multiple operations
6. **Report**: Format and return results

### 4. Message Bus Architecture

#### 4.1 Core Features
```python
class MessageBus:
    """Event-driven communication system"""
    - Pub/sub pattern implementation
    - Priority-based message queuing
    - TTL-based expiration
    - Message correlation tracking
    - Comprehensive history logging
```

#### 4.2 Message Types
- **Direct Messages**: Point-to-point communication
- **Broadcast Messages**: All subscribers receive
- **Request/Reply**: Synchronous-style communication
- **Event Notifications**: State change alerts

#### 4.3 Topics Organization
```
vc.*            # Version control events
doc.*           # Documentation events
code.*          # Code analysis events
task.*          # Task management events
system.*        # System-level events
```

### 5. Task Management System

#### 5.1 Task Lifecycle
```
CREATED → QUEUED → RUNNING → [COMPLETED|FAILED|CANCELLED]
```

#### 5.2 Task Manager Features
- **Priority Scheduling**: 1-10 scale priority system
- **Concurrent Execution**: Configurable parallelism
- **Type-Based Routing**: Handler registration by task type
- **Cancellation Support**: Graceful task termination
- **Audit Trail**: Complete task history

### 6. MCP (Model Context Protocol) Integration

#### 6.1 Server Configurations

**Stdio Servers:**
- `force-mcp-stdio`: Force framework over stdio
- `dev-sentinel-stdio`: Full Dev Sentinel over stdio

**HTTP Servers:**
- `force-mcp-http`: Force framework HTTP API (port 8080)
- `dev-sentinel-http`: Dev Sentinel HTTP API (port 8000)

#### 6.2 MCP Tool Registration
```python
@server.list_tools()
async def handle_list_tools():
    """Register available tools with MCP"""
    tools = []
    for tool in force_engine.get_tool_list():
        tools.append({
            "name": tool.id,
            "description": tool.description,
            "inputSchema": convert_to_mcp_schema(tool.parameters)
        })
    return tools
```

#### 6.3 Protocol Features
- **Tool Discovery**: Automatic tool registration
- **Schema Validation**: JSON Schema-based parameter validation
- **Error Handling**: Structured error responses
- **Async Execution**: Non-blocking tool execution
- **Result Streaming**: Progressive result delivery

### 7. Integration Architecture

#### 7.1 Fast-Agent Integration
```python
class FastAgentAdapter:
    """Bridge between Dev Sentinel and fast-agent framework"""
    - Command translation
    - Workflow orchestration
    - Result aggregation
    - Context management
```

#### 7.2 Terminal Management
```python
SUBAGENT_TERMINALS = {
    "vcs": "TERMINAL-VCS",
    "documentation": "TERMINAL-DOC",
    "code": "TERMINAL-CODE",
    "infrastructure": "TERMINAL-INFRA",
    "testing": "TERMINAL-TEST",
    "fast_agent": "TERMINAL-FAST"
}
```

Each agent maintains dedicated terminal state for:
- Working directory persistence
- Environment variable management
- Command history tracking
- Output buffering

### 8. Configuration Management

#### 8.1 Project Configuration
```toml
[project]
name = "dev_sentinel"
version = "0.4.3"
requires-python = ">=3.10"

[project.scripts]
dev-sentinel = "dev_sentinel.cli:main"
force-mcp-stdio = "dev_sentinel.servers.force_mcp_stdio:main"
```

#### 8.2 Agent Configuration
```yaml
agents:
  saa:
    enabled: true
    languages: ["python", "javascript", "typescript"]
    rules: ["complexity", "security", "performance"]

  vcma:
    enabled: true
    auto_commit: false
    branch_strategy: "feature-branch"
```

#### 8.3 MCP Configuration
```json
{
  "mcpServers": {
    "dev-sentinel-stdio": {
      "command": "dev-sentinel-stdio",
      "args": [],
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 9. Technology Stack

#### 9.1 Core Dependencies
- **Python 3.10+**: Modern async/await patterns
- **FastAPI**: HTTP server framework
- **Uvicorn**: ASGI server
- **Pydantic v2**: Data validation
- **Click**: CLI interface
- **AIOHTTP**: Async HTTP client

#### 9.2 Development Tools
- **Pytest**: Testing with async support
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **MyPy**: Static type checking
- **Sphinx**: Documentation generation

### 10. Execution Flow

#### 10.1 Command Execution Path
1. **Client Request**: MCP client sends tool invocation
2. **Server Reception**: MCP server receives and validates
3. **Command Parsing**: YUNG processor extracts command
4. **Agent Routing**: Route to appropriate agent
5. **Task Creation**: Create task with parameters
6. **Agent Processing**: Agent executes task
7. **Result Aggregation**: Combine outputs
8. **Response Formation**: Format MCP response
9. **Client Response**: Return to MCP client

#### 10.2 Agent Communication Flow
```
Agent A → Message Bus → Agent B
   ↓                        ↓
Task Manager          Event Handler
   ↓                        ↓
Execution              Processing
   ↓                        ↓
Result   ←  Message Bus  ← Response
```

## Performance Characteristics

### Async Architecture Benefits
- **Non-blocking Operations**: All I/O operations are async
- **Concurrent Processing**: Multiple agents run simultaneously
- **Resource Efficiency**: Proper cleanup and resource management
- **Scalability**: Horizontal scaling through agent distribution

### Optimization Strategies
- **Lazy Loading**: Components loaded on demand
- **Caching**: Results cached with TTL
- **Batch Processing**: Group similar operations
- **Connection Pooling**: Reuse connections for efficiency

## Security Features

### Authentication & Authorization
- **API Key Management**: Secure storage and rotation
- **Role-Based Access**: Fine-grained permissions
- **Audit Logging**: Complete activity tracking
- **Encryption**: TLS for transport, encryption at rest

### Code Security
- **Static Analysis**: Security vulnerability scanning
- **Dependency Checking**: Known vulnerability detection
- **Secret Detection**: Prevent credential leaks
- **Sandboxing**: Isolated execution environments

## Integration Points with IDFW

### Complementary Capabilities
1. **Schema Systems**: Both use JSON Schema validation
2. **Document Generation**: Shared documentation goals
3. **Project Management**: Compatible project structures
4. **Command Systems**: Extensible command frameworks

### Potential Synergies
1. **IDFW Schemas → Force Tools**: Generate tools from IDFW definitions
2. **IDFW Generators → Dev Sentinel Agents**: Wrap generators as agents
3. **IDFW Variables → Agent State**: Unified state management
4. **IDFW Actions → YUNG Commands**: Map actions to commands

---

*Analysis Version: 1.0.0*
*Date: 2025-09-29*
*Dev Sentinel Version: 0.4.3*
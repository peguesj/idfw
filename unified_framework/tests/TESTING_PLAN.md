# IDFWU Testing Plan - Phase 1

**Linear Project**: [IDFWU - IDEA Framework Unified](https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7)
**Project ID**: `4d649a6501f7`
**Repository**: https://github.com/peguesj/idfwu
**Test Framework**: pytest 7.4+
**Coverage Target**: 80% minimum
**Version**: 1.0.0

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Unit Testing Strategy](#unit-testing-strategy)
3. [Integration Testing Strategy](#integration-testing-strategy)
4. [End-to-End Testing Strategy](#end-to-end-testing-strategy)
5. [Performance Testing Strategy](#performance-testing-strategy)
6. [Coverage Targets](#coverage-targets)
7. [Test Execution Order](#test-execution-order)
8. [Test Infrastructure](#test-infrastructure)
9. [Continuous Integration](#continuous-integration)

---

## Testing Overview

### Testing Pyramid

```
                 E2E Tests (10%)
              ┌──────────────────┐
              │  User Workflows  │
              │  10 test cases   │
              └──────────────────┘
                      ▲
         Integration Tests (20%)
    ┌────────────────────────────────┐
    │   Component Integration        │
    │   50 test cases                │
    └────────────────────────────────┘
                ▲
          Unit Tests (70%)
┌──────────────────────────────────────────┐
│   Individual Functions & Classes         │
│   200+ test cases                        │
└──────────────────────────────────────────┘
```

### Test Distribution

| Test Type | Test Count | Coverage Target | Execution Time | Frequency |
|-----------|------------|-----------------|----------------|-----------|
| Unit | 200+ | 80% | < 30s | Every commit |
| Integration | 50+ | 70% | < 2min | Every PR |
| E2E | 10+ | 60% | < 5min | Pre-release |
| Performance | 20+ | N/A | < 3min | Daily |

---

## Unit Testing Strategy

### Objectives
- Validate individual functions and classes in isolation
- Achieve 80%+ code coverage
- Fast execution (< 30 seconds total)
- Run on every commit

### Framework Configuration

**pytest.ini**:
```ini
[pytest]
testpaths = unified_framework/tests/unit
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=unified_framework
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    performance: marks tests as performance tests
```

### Module Coverage Targets

#### Core Modules (90% target)

**unified_framework/core/schema_bridge.py** - 90%
```python
# Test coverage breakdown
- SchemaUnifier class: 95%
- SchemaRegistry class: 90%
- ConversionRule class: 85%
- SchemaDefinition validation: 100%
- Edge cases: 85%
```

**Test File**: `tests/unit/core/test_schema_bridge.py`
**Test Count**: 50+
**Key Test Cases**:
- Schema parsing (IDFW, FORCE, Unified)
- Schema validation (success and failure cases)
- Schema conversion (all format combinations)
- Conflict detection and resolution
- Registry operations (register, discover, retrieve)
- Edge cases (malformed schemas, circular references)

**unified_framework/core/state_manager.py** - 85%
```python
# Test coverage breakdown
- StateManager class: 90%
- Variable scoping: 85%
- Conflict resolution: 85%
- State persistence: 80%
- Cache operations: 85%
```

**Test File**: `tests/unit/core/test_state_manager.py`
**Test Count**: 40+
**Key Test Cases**:
- State initialization and cleanup
- Variable get/set operations
- Scope hierarchy (global, project, session, agent, task)
- Conflict resolution strategies
- State snapshots and restoration
- Cache hit/miss scenarios
- Persistence to file system

**unified_framework/commands/processor.py** - 90%
```python
# Test coverage breakdown
- CommandProcessor class: 95%
- CommandHandler implementations: 90%
- Middleware pipeline: 90%
- Command parsing: 95%
- Error handling: 85%
```

**Test File**: `tests/unit/commands/test_processor.py`
**Test Count**: 45+
**Key Test Cases**:
- Prefix detection ($, @, #, /)
- Command parsing (with/without args)
- Parameter parsing (flags, values, quoted strings)
- Command routing to handlers
- Middleware execution order
- Error handling and recovery
- Context propagation

#### Agent System (85% target)

**unified_framework/agents/base_agent.py** - 85%
```python
# Test coverage breakdown
- BaseAgent class: 90%
- Task execution: 85%
- Message handling: 85%
- Linear integration: 80%
- Performance tracking: 85%
```

**Test File**: `tests/unit/agents/test_base_agent.py`
**Test Count**: 35+
**Key Test Cases**:
- Agent initialization and lifecycle
- Task assignment and execution
- Message sending and receiving
- Linear API integration (create issue, update status)
- Performance metrics collection
- Observer pattern notifications
- Error handling and retry logic

**unified_framework/agents/implementations/*.py** - 85%
```python
# Test coverage per agent implementation
- SchemaEngineerAgent: 90%
- ArchitectAgent: 85%
- BackendDeveloperAgent: 85%
- QualityAssuranceAgent: 90%
- DocumentationAgent: 80%
```

**Test Files**: `tests/unit/agents/test_implementations.py`
**Test Count**: 50+ (10 per agent)
**Key Test Cases**:
- Agent-specific task execution
- Specialized logic validation
- Integration with core modules
- Error scenarios
- Performance benchmarks

#### MCP Server (85% target)

**unified_framework/mcp/server.py** - 85%
```python
# Test coverage breakdown
- MCPServer class: 90%
- ToolRegistry class: 85%
- Protocol handlers: 85%
- Transport layers: 80%
```

**Test File**: `tests/unit/mcp/test_server.py`
**Test Count**: 40+
**Key Test Cases**:
- Server initialization and lifecycle
- Tool registration and discovery
- Tool invocation (success and failure)
- Protocol compliance (stdio, HTTP)
- Error responses
- Resource access
- Concurrent tool calls

### Test Fixtures and Utilities

**conftest.py** - Shared fixtures:
```python
@pytest.fixture
def sample_idfw_schema():
    """Sample IDFW document schema for testing"""
    return {
        "name": "test-document",
        "version": "1.0.0",
        "sections": [...]
    }

@pytest.fixture
def sample_force_tool():
    """Sample FORCE tool definition"""
    return {
        "name": "validate_tool",
        "parameters": [...]
    }

@pytest.fixture
def mock_redis():
    """Mock Redis connection for message bus tests"""
    return fakeredis.FakeStrictRedis()

@pytest.fixture
def mock_linear_client():
    """Mock Linear API client"""
    return Mock(spec=LinearClient)

@pytest.fixture
def temp_state_dir(tmp_path):
    """Temporary directory for state persistence tests"""
    return tmp_path / "state"
```

### Mocking Strategy

**External Dependencies to Mock**:
- Redis (use fakeredis)
- Linear API (use unittest.mock)
- File system (use pytest tmp_path)
- HTTP requests (use responses or httpx.mock)
- Time functions (use freezegun)

**Example Mock Usage**:
```python
@pytest.mark.asyncio
async def test_agent_creates_linear_issue(mock_linear_client):
    agent = SchemaEngineerAgent(agent_id="SEA", linear_client=mock_linear_client)

    task = Task(
        id="task-123",
        agent_id="SEA",
        description="Convert IDFW schema to FORCE"
    )

    await agent.execute_task(task)

    mock_linear_client.create_issue.assert_called_once()
    assert mock_linear_client.create_issue.call_args[0][0] == "PEG-XXX"
```

### Parametrized Testing

**Use pytest.mark.parametrize for variations**:
```python
@pytest.mark.parametrize("schema_format,expected_type", [
    (SchemaFormat.IDFW_DOCUMENT, IDFWSchema),
    (SchemaFormat.FORCE_TOOL, FORCESchema),
    (SchemaFormat.UNIFIED_COMMAND, UnifiedSchema),
])
def test_schema_parsing(schema_format, expected_type):
    parser = SchemaParser()
    result = parser.parse(schema_format, sample_data)
    assert isinstance(result, expected_type)
```

---

## Integration Testing Strategy

### Objectives
- Validate component interactions
- Test data flow across boundaries
- Verify API contracts
- Run on every PR

### Test Environment Setup

**Docker Compose for Integration Tests**:
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: idfwu_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 3s
      retries: 5
```

### Integration Test Suites

#### Suite 1: Schema Conversion Workflows

**Test File**: `tests/integration/test_schema_workflows.py`
**Test Count**: 10+
**Estimated Time**: 30s

**Test Scenarios**:

**IT-SCHEMA-001**: IDFW Document to FORCE Tool Conversion
```python
@pytest.mark.integration
async def test_idfw_document_to_force_tool():
    """
    End-to-end test of IDFW → FORCE conversion

    Steps:
    1. Load IDFW document schema
    2. Parse with IDFWDocumentParser
    3. Convert to FORCE tool with SchemaUnifier
    4. Validate FORCE tool definition
    5. Verify metadata preservation
    """
    # Load schema
    idfw_schema = load_test_schema("sample_document.idfw")

    # Parse
    parser = IDFWDocumentParser()
    parsed = parser.parse(idfw_schema)

    # Convert
    unifier = SchemaUnifier()
    force_tool = await unifier.idfw_to_force(parsed)

    # Validate
    assert force_tool.metadata.format == SchemaFormat.FORCE_TOOL
    assert force_tool.metadata.name == parsed.metadata.name
    assert len(force_tool.parameters) == len(parsed.properties)
```

**IT-SCHEMA-002**: FORCE Pattern to IDFW Diagram Conversion
```python
@pytest.mark.integration
async def test_force_pattern_to_idfw_diagram():
    """Test FORCE → IDFW conversion with diagram generation"""
    # Similar structure to IT-SCHEMA-001
```

**IT-SCHEMA-003**: Roundtrip Conversion Fidelity
```python
@pytest.mark.integration
async def test_roundtrip_conversion_fidelity():
    """
    Test IDFW → FORCE → IDFW maintains data fidelity

    Success criteria: > 95% fidelity score
    """
    original_schema = load_test_schema("complex_document.idfw")

    # Convert to FORCE
    force_schema = await unifier.idfw_to_force(original_schema)

    # Convert back to IDFW
    roundtrip_schema = await unifier.force_to_idfw(force_schema)

    # Measure fidelity
    validator = RoundtripValidator()
    fidelity = validator.measure_fidelity(original_schema, roundtrip_schema)

    assert fidelity > 0.95  # 95% fidelity
```

**IT-SCHEMA-004**: Conflict Detection and Resolution
```python
@pytest.mark.integration
async def test_conflict_detection_and_resolution():
    """Test automatic conflict resolution during conversion"""
    # Schema with known conflicts
    conflicting_schema = load_test_schema("conflict_schema.idfw")

    unifier = SchemaUnifier()
    result = await unifier.convert_with_conflicts(conflicting_schema)

    assert len(result.conflicts) > 0
    assert result.resolution_rate > 0.8  # 80% auto-resolved
```

#### Suite 2: Command Execution Workflows

**Test File**: `tests/integration/test_command_workflows.py`
**Test Count**: 15+
**Estimated Time**: 45s

**Test Scenarios**:

**IT-CMD-001**: YUNG Command End-to-End Execution
```python
@pytest.mark.integration
async def test_yung_command_execution(dev_sentinel_mock):
    """
    Test complete YUNG command workflow

    Steps:
    1. Parse YUNG command
    2. Route to Dev Sentinel handler
    3. Execute command
    4. Transform result
    5. Validate output
    """
    processor = UnifiedCommandProcessor()
    context = CommandContext(working_directory="/test")

    result = await processor.process("$validate --schema test.json", context)

    assert result.status == CommandStatus.SUCCESS
    assert result.output is not None
```

**IT-CMD-002**: IDFW Action Execution
```python
@pytest.mark.integration
async def test_idfw_action_execution(idfw_generator_mock):
    """Test complete IDFW action workflow"""
    processor = UnifiedCommandProcessor()

    result = await processor.process("@create-document --name test", context)

    assert result.status == CommandStatus.SUCCESS
    assert "document_id" in result.data
```

**IT-CMD-003**: Command Pipeline Execution
```python
@pytest.mark.integration
async def test_command_pipeline():
    """Test chained command execution"""
    pipeline = CommandPipeline()

    # Chain: create document → validate → convert
    pipeline.add("@create-document --name test")
    pipeline.add("$validate --schema {output.path}")
    pipeline.add("@convert-to-force --input {output.schema}")

    results = await pipeline.execute(context)

    assert all(r.status == CommandStatus.SUCCESS for r in results)
```

**IT-CMD-004**: Middleware Pipeline Integration
```python
@pytest.mark.integration
async def test_middleware_pipeline():
    """Test middleware execution order and data flow"""
    processor = UnifiedCommandProcessor()
    processor.add_middleware(LoggingMiddleware())
    processor.add_middleware(ValidationMiddleware())
    processor.add_middleware(PermissionMiddleware())

    result = await processor.process("$test-command", context)

    # Verify all middleware was executed
    assert context.metadata["logging_executed"]
    assert context.metadata["validation_executed"]
    assert context.metadata["permission_checked"]
```

#### Suite 3: Agent Orchestration Workflows

**Test File**: `tests/integration/test_agent_workflows.py`
**Test Count**: 10+
**Estimated Time**: 1min

**Test Scenarios**:

**IT-AGENT-001**: Task Assignment and Execution
```python
@pytest.mark.integration
async def test_agent_task_assignment(redis_instance):
    """
    Test complete agent task workflow

    Steps:
    1. Create agents
    2. Initialize message bus
    3. Assign task
    4. Execute task
    5. Verify result
    """
    # Create agents
    sea = SchemaEngineerAgent(agent_id="SEA")

    # Initialize message bus
    bus = MessageBus(redis_url="redis://localhost:6379")
    await sea.connect_to_bus(bus)

    # Assign task
    task = Task(
        agent_id="SEA",
        description="Convert IDFW schema to FORCE",
        metadata={"schema_path": "/test/schema.idfw"}
    )

    await sea.assign_task(task)

    # Wait for execution
    result = await sea.wait_for_completion(task.id, timeout=30)

    assert result.status == TaskStatus.COMPLETED
    assert result.result is not None
```

**IT-AGENT-002**: Multi-Agent Collaboration
```python
@pytest.mark.integration
async def test_multi_agent_collaboration(redis_instance):
    """Test multiple agents working together on a workflow"""
    # Create agents
    sea = SchemaEngineerAgent(agent_id="SEA")
    qaa = QualityAssuranceAgent(agent_id="QAA")

    # Initialize orchestrator
    orchestrator = AgentOrchestrator(agents={"SEA": sea, "QAA": qaa})

    # Create workflow
    workflow = Workflow(
        name="schema-conversion-with-validation",
        tasks=[
            Task(agent_id="SEA", description="Convert schema"),
            Task(agent_id="QAA", description="Validate conversion",
                 depends_on=["SEA"])
        ]
    )

    # Execute workflow
    result = await orchestrator.execute_workflow(workflow)

    assert result.status == WorkflowStatus.COMPLETED
    assert all(t.status == TaskStatus.COMPLETED for t in result.tasks)
```

**IT-AGENT-003**: Message Bus Communication
```python
@pytest.mark.integration
async def test_message_bus_communication(redis_instance):
    """Test agent-to-agent communication via message bus"""
    # Create agents
    agent1 = SchemaEngineerAgent(agent_id="SEA-1")
    agent2 = SchemaEngineerAgent(agent_id="SEA-2")

    # Connect to bus
    bus = MessageBus(redis_url="redis://localhost:6379")
    await agent1.connect_to_bus(bus)
    await agent2.connect_to_bus(bus)

    # Agent 1 sends message
    message = Message(
        sender_id="SEA-1",
        receiver_id="SEA-2",
        message_type="REQUEST_SCHEMA",
        payload={"schema_id": "test-123"}
    )

    await agent1.send_message(message)

    # Agent 2 receives and responds
    received = await agent2.receive_message(timeout=5)
    assert received.sender_id == "SEA-1"

    response = Message(
        sender_id="SEA-2",
        receiver_id="SEA-1",
        message_type="SCHEMA_RESPONSE",
        payload={"schema": {...}},
        reply_to=received.id
    )

    await agent2.send_message(response)
```

**IT-AGENT-004**: Task Dependency Resolution
```python
@pytest.mark.integration
async def test_task_dependency_resolution():
    """Test automatic task ordering based on dependencies"""
    orchestrator = AgentOrchestrator()

    # Create tasks with dependencies (DAG)
    tasks = [
        Task(id="A", agent_id="SEA", description="Task A"),
        Task(id="B", agent_id="BDA", description="Task B", depends_on=["A"]),
        Task(id="C", agent_id="QAA", description="Task C", depends_on=["A"]),
        Task(id="D", agent_id="DOC", description="Task D", depends_on=["B", "C"]),
    ]

    # Resolve dependencies
    resolver = DependencyResolver()
    execution_order = resolver.resolve_dependencies(tasks)

    # Verify execution order
    assert execution_order[0].id == "A"
    assert execution_order[-1].id == "D"
    assert set([t.id for t in execution_order[1:3]]) == {"B", "C"}
```

#### Suite 4: MCP Protocol Integration

**Test File**: `tests/integration/test_mcp_workflows.py`
**Test Count**: 15+
**Estimated Time**: 45s

**Test Scenarios**:

**IT-MCP-001**: MCP Server Lifecycle
```python
@pytest.mark.integration
async def test_mcp_server_lifecycle():
    """Test MCP server startup, operation, and shutdown"""
    server = MCPServer(host="localhost", port=8080)

    # Start server
    await server.start()
    assert server.is_running()

    # Register tools
    server.register_tool(IDFWTools.create_document)
    server.register_tool(FORCETools.validate_tool)

    # Verify tool list
    tools = await server.list_tools()
    assert len(tools) >= 2

    # Shutdown
    await server.shutdown()
    assert not server.is_running()
```

**IT-MCP-002**: Tool Invocation via HTTP
```python
@pytest.mark.integration
async def test_mcp_tool_invocation_http():
    """Test tool invocation via HTTP transport"""
    server = MCPServer(host="localhost", port=8080)
    await server.start()

    # Make HTTP request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/tools/idfw.create_document",
            json={"name": "test-doc", "sections": []}
        )

    assert response.status_code == 200
    result = response.json()
    assert "document_id" in result
```

**IT-MCP-003**: WebSocket Bidirectional Communication
```python
@pytest.mark.integration
async def test_mcp_websocket_communication():
    """Test bidirectional WebSocket communication"""
    server = MCPServer(host="localhost", port=8080)
    await server.start()

    # Connect WebSocket client
    async with websockets.connect("ws://localhost:8080/ws") as ws:
        # Send tool call request
        await ws.send(json.dumps({
            "method": "tools/call",
            "params": {
                "name": "idfw.create_document",
                "arguments": {"name": "test"}
            }
        }))

        # Receive response
        response = await ws.recv()
        result = json.loads(response)

        assert result["status"] == "success"
```

**IT-MCP-004**: VS Code Extension Integration
```python
@pytest.mark.integration
async def test_vscode_extension_integration():
    """Test VS Code extension connecting to MCP server"""
    server = MCPServer(host="localhost", port=8080)
    await server.start()

    # Simulate VS Code extension connection
    client = MCPClient("http://localhost:8080")

    # List available tools
    tools = await client.list_tools()
    assert len(tools) > 0

    # Execute command
    result = await client.execute_command("unified.convert_schema", {
        "source_format": "idfw",
        "target_format": "force",
        "schema_path": "/test/schema.idfw"
    })

    assert result.success
```

---

## End-to-End Testing Strategy

### Objectives
- Validate complete user workflows
- Test system behavior under realistic conditions
- Verify critical paths
- Run before releases

### E2E Test Scenarios

#### E2E-001: Complete Schema Conversion Workflow
```python
@pytest.mark.e2e
async def test_complete_schema_conversion_workflow():
    """
    Complete user workflow for schema conversion

    Steps:
    1. User creates IDFW document
    2. User executes convert command
    3. System parses IDFW
    4. System converts to FORCE
    5. System validates conversion
    6. User receives FORCE tool definition
    """
    # User creates IDFW document
    idfw_content = create_idfw_document(
        name="payment-service",
        sections=["api", "models", "database"]
    )

    # Save to file
    idfw_path = write_to_file(idfw_content, "/tmp/payment-service.idfw")

    # User executes convert command
    cli = UnifiedCLI()
    result = await cli.execute(
        f"@convert-to-force --input {idfw_path} --output /tmp/payment.force"
    )

    # Verify conversion successful
    assert result.exit_code == 0
    assert os.path.exists("/tmp/payment.force")

    # Validate FORCE tool
    force_tool = load_force_tool("/tmp/payment.force")
    assert force_tool.name == "payment-service"
    assert len(force_tool.parameters) > 0
```

#### E2E-002: Multi-Agent Development Workflow
```python
@pytest.mark.e2e
async def test_multi_agent_development_workflow():
    """
    Complete development workflow with multiple agents

    Steps:
    1. User requests feature implementation
    2. PMA creates task breakdown
    3. SEA designs schemas
    4. BDA implements backend
    5. QAA validates implementation
    6. DOC generates documentation
    """
    # User creates feature request
    feature_request = """
    Implement user authentication system with:
    - JWT tokens
    - Role-based access control
    - Password hashing
    - Session management
    """

    # Deploy agent team
    orchestrator = AgentOrchestrator()
    await orchestrator.deploy_team([
        "PMA", "SEA", "BDA", "QAA", "DOC"
    ])

    # Submit feature request
    workflow = await orchestrator.create_workflow_from_request(feature_request)

    # Execute workflow
    result = await orchestrator.execute_workflow(workflow)

    # Verify completion
    assert result.status == WorkflowStatus.COMPLETED
    assert all(task.status == TaskStatus.COMPLETED for task in result.tasks)

    # Verify artifacts
    assert os.path.exists("/output/schemas/auth.idfw")
    assert os.path.exists("/output/backend/auth_service.py")
    assert os.path.exists("/output/tests/test_auth.py")
    assert os.path.exists("/output/docs/auth_api.md")
```

#### E2E-003: CLI to MCP Server to VS Code Integration
```python
@pytest.mark.e2e
async def test_cli_mcp_vscode_integration():
    """
    Complete integration across all interfaces

    Steps:
    1. Start MCP server
    2. Register tools
    3. Connect VS Code extension
    4. Execute command from VS Code
    5. Verify result in CLI
    """
    # Start MCP server
    server = MCPServer(host="localhost", port=8080)
    await server.start()

    # Register tools
    register_all_tools(server)

    # Connect VS Code extension (simulated)
    vscode_client = VSCodeMCPClient("http://localhost:8080")
    await vscode_client.connect()

    # Execute command from VS Code
    result = await vscode_client.execute_command(
        "idfwu.convertSchema",
        {"input": "/test/schema.idfw"}
    )

    # Verify result
    assert result.success
    assert os.path.exists(result.output_path)

    # Verify in CLI
    cli = UnifiedCLI()
    status = await cli.execute("$status --last-command")
    assert status.exit_code == 0
```

#### E2E-004: Linear Integration Workflow
```python
@pytest.mark.e2e
async def test_linear_integration_workflow():
    """
    Complete Linear integration workflow

    Steps:
    1. Agent executes task
    2. Agent creates Linear issue
    3. Agent updates issue status
    4. Agent adds comments
    5. Agent closes issue on completion
    """
    # Create agent with Linear integration
    agent = SchemaEngineerAgent(
        agent_id="SEA",
        linear_api_key=os.getenv("LINEAR_API_KEY")
    )

    # Assign task
    task = Task(
        agent_id="SEA",
        description="Convert payment schema to FORCE",
        metadata={"create_linear_issue": True}
    )

    # Execute task
    result = await agent.execute_task(task)

    # Verify Linear issue created
    assert result.linear_issue_id is not None

    # Verify issue on Linear
    linear_client = LinearClient(api_key=os.getenv("LINEAR_API_KEY"))
    issue = await linear_client.get_issue(result.linear_issue_id)

    assert issue.title == task.description
    assert issue.status == "Done"
    assert len(issue.comments) > 0
```

---

## Performance Testing Strategy

### Objectives
- Establish performance baselines
- Identify bottlenecks
- Validate performance targets
- Run daily

### Performance Test Categories

#### Category 1: Schema Operations

**PERF-SCHEMA-001**: Schema Parsing Performance
```python
@pytest.mark.performance
def test_schema_parsing_performance(benchmark):
    """
    Target: < 50ms for typical schema

    Benchmark schema parsing across different sizes
    """
    parser = IDFWDocumentParser()
    schema = load_test_schema("medium_complexity.idfw")

    result = benchmark(parser.parse, schema)

    # Assertions
    assert benchmark.stats.mean < 0.05  # 50ms
    assert benchmark.stats.stddev < 0.01  # Low variance
```

**PERF-SCHEMA-002**: Schema Conversion Performance
```python
@pytest.mark.performance
def test_schema_conversion_performance(benchmark):
    """
    Target: < 100ms for typical conversion
    """
    unifier = SchemaUnifier()
    idfw_schema = load_test_schema("medium_complexity.idfw")

    result = benchmark(unifier.idfw_to_force, idfw_schema)

    assert benchmark.stats.mean < 0.1  # 100ms
```

**PERF-SCHEMA-003**: Roundtrip Conversion Performance
```python
@pytest.mark.performance
def test_roundtrip_conversion_performance(benchmark):
    """
    Target: < 200ms for roundtrip
    """
    def roundtrip():
        unifier = SchemaUnifier()
        force = unifier.idfw_to_force(idfw_schema)
        return unifier.force_to_idfw(force)

    result = benchmark(roundtrip)

    assert benchmark.stats.mean < 0.2  # 200ms
```

#### Category 2: Command Processing

**PERF-CMD-001**: Command Parsing Performance
```python
@pytest.mark.performance
def test_command_parsing_performance(benchmark):
    """
    Target: < 10ms for command parsing
    """
    processor = UnifiedCommandProcessor()
    command = "$validate --schema /test/schema.json --verbose --output /tmp/result"

    result = benchmark(processor.parse_command, command)

    assert benchmark.stats.mean < 0.01  # 10ms
```

**PERF-CMD-002**: Middleware Overhead
```python
@pytest.mark.performance
def test_middleware_overhead(benchmark):
    """
    Target: < 5ms overhead per middleware
    """
    processor = UnifiedCommandProcessor()
    processor.add_middleware(LoggingMiddleware())
    processor.add_middleware(ValidationMiddleware())
    processor.add_middleware(PermissionMiddleware())

    command = Command(prefix=CommandPrefix.YUNG, name="test")

    result = benchmark(processor.apply_middleware, command)

    # 3 middleware * 5ms = 15ms max
    assert benchmark.stats.mean < 0.015
```

#### Category 3: Agent System

**PERF-AGENT-001**: Task Execution Overhead
```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_task_execution_overhead(benchmark):
    """
    Target: < 50ms overhead for task execution
    """
    agent = SchemaEngineerAgent(agent_id="SEA")
    task = Task(
        agent_id="SEA",
        description="Simple task"
    )

    result = benchmark(agent.execute_task, task)

    assert benchmark.stats.mean < 0.05
```

**PERF-AGENT-002**: Message Bus Throughput
```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_message_bus_throughput(benchmark, redis_instance):
    """
    Target: > 1000 messages/second
    """
    bus = MessageBus(redis_url="redis://localhost:6379")

    async def send_messages(count=1000):
        for i in range(count):
            await bus.publish("test.topic", Message(
                sender_id="test",
                message_type="TEST",
                payload={"index": i}
            ))

    result = benchmark(send_messages)

    # 1000 messages in < 1 second
    assert benchmark.stats.mean < 1.0
```

#### Category 4: MCP Server

**PERF-MCP-001**: Tool Discovery Performance
```python
@pytest.mark.performance
def test_tool_discovery_performance(benchmark):
    """
    Target: < 10ms for tool discovery
    """
    server = MCPServer()
    register_all_tools(server)  # 200+ tools

    result = benchmark(server.discover_tools, category=ToolCategory.IDFW)

    assert benchmark.stats.mean < 0.01
```

**PERF-MCP-002**: HTTP Request Latency
```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_http_request_latency(benchmark):
    """
    Target: < 50ms for HTTP tool call
    """
    server = MCPServer(host="localhost", port=8080)
    await server.start()

    async def make_request():
        async with httpx.AsyncClient() as client:
            return await client.post(
                "http://localhost:8080/tools/idfw.create_document",
                json={"name": "test"}
            )

    result = benchmark(make_request)

    assert benchmark.stats.mean < 0.05
```

### Load Testing

**Load Test Configuration**:
```python
# tests/performance/load_test_config.py
LOAD_TEST_SCENARIOS = [
    {
        "name": "message_bus_load",
        "duration": "1m",
        "users": 100,
        "spawn_rate": 10,
        "target_rps": 1000
    },
    {
        "name": "mcp_server_load",
        "duration": "2m",
        "users": 50,
        "spawn_rate": 5,
        "target_rps": 500
    },
    {
        "name": "command_processor_load",
        "duration": "1m",
        "users": 200,
        "spawn_rate": 20,
        "target_rps": 2000
    }
]
```

---

## Coverage Targets

### Overall Coverage: 80% minimum

### Module-Specific Targets

| Module | Target | Priority | Notes |
|--------|--------|----------|-------|
| core/schema_bridge.py | 90% | Urgent | Critical path |
| core/state_manager.py | 85% | High | State integrity |
| commands/processor.py | 90% | Urgent | Core functionality |
| agents/base_agent.py | 85% | High | Agent foundation |
| mcp/server.py | 85% | High | MCP protocol |
| cli/*.py | 70% | Medium | CLI interface |
| tests/*.py | 100% | N/A | Test code itself |

### Critical Path Coverage: 95% minimum

**Critical Paths**:
- Schema conversion (IDFW ↔ FORCE)
- Command parsing and routing
- Agent task execution
- MCP tool invocation
- Error handling and recovery

### Coverage Exclusions

**Exclude from coverage**:
```python
# .coveragerc
[run]
omit =
    */tests/*
    */conftest.py
    */venv/*
    */node_modules/*
    */migrations/*
    */__pycache__/*
    */setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

## Test Execution Order

### 1. Pre-commit (< 30s)
```bash
# Fast unit tests only
pytest tests/unit -m "not slow" --maxfail=3 -q
```

### 2. Pull Request (< 3min)
```bash
# All unit tests + integration tests
pytest tests/unit tests/integration -v --cov
```

### 3. Daily Build (< 10min)
```bash
# All tests including performance
pytest tests/ --cov --cov-report=html
pytest tests/performance/ --benchmark-only
```

### 4. Pre-release (< 15min)
```bash
# Complete test suite including E2E
pytest tests/ --cov --cov-report=xml
pytest tests/e2e/ -v --durations=10
pytest tests/performance/ --benchmark-compare
```

### Test Selection

**Run specific test suites**:
```bash
# Schema tests only
pytest tests/unit/core/test_schema*.py -v

# Command tests only
pytest tests/unit/commands/ -v

# Agent tests only
pytest tests/unit/agents/ tests/integration/test_agent*.py -v

# MCP tests only
pytest tests/unit/mcp/ tests/integration/test_mcp*.py -v

# Performance tests only
pytest tests/performance/ --benchmark-only
```

**Run by marker**:
```bash
# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

---

## Test Infrastructure

### Directory Structure

```
unified_framework/tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── fixtures/
│   ├── __init__.py
│   ├── schema_fixtures.py      # Schema test data
│   ├── command_fixtures.py     # Command test data
│   ├── agent_fixtures.py       # Agent test data
│   └── mcp_fixtures.py         # MCP test data
├── unit/
│   ├── __init__.py
│   ├── conftest.py
│   ├── core/
│   │   ├── test_schema_bridge.py (50+ tests)
│   │   ├── test_state_manager.py (40+ tests)
│   │   └── test_converters.py (30+ tests)
│   ├── commands/
│   │   ├── test_processor.py (45+ tests)
│   │   ├── test_handlers.py (30+ tests)
│   │   └── test_middleware.py (25+ tests)
│   ├── agents/
│   │   ├── test_base_agent.py (35+ tests)
│   │   ├── test_implementations.py (50+ tests)
│   │   └── test_orchestration.py (25+ tests)
│   └── mcp/
│       ├── test_server.py (40+ tests)
│       ├── test_registry.py (30+ tests)
│       └── test_protocol.py (20+ tests)
├── integration/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_schema_workflows.py (10+ tests)
│   ├── test_command_workflows.py (15+ tests)
│   ├── test_agent_workflows.py (10+ tests)
│   └── test_mcp_workflows.py (15+ tests)
├── e2e/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_schema_conversion.py (3+ tests)
│   ├── test_agent_development.py (3+ tests)
│   ├── test_cli_integration.py (2+ tests)
│   └── test_linear_integration.py (2+ tests)
├── performance/
│   ├── __init__.py
│   ├── conftest.py
│   ├── benchmarks.py
│   ├── test_schema_perf.py (5+ tests)
│   ├── test_command_perf.py (4+ tests)
│   ├── test_agent_perf.py (5+ tests)
│   ├── test_mcp_perf.py (4+ tests)
│   └── load_tests.py (3+ scenarios)
└── mocks/
    ├── __init__.py
    ├── mock_redis.py
    ├── mock_linear.py
    ├── mock_dev_sentinel.py
    └── mock_idfw.py
```

### Test Data Management

**Test Schema Repository**:
```
tests/fixtures/schemas/
├── idfw/
│   ├── simple_document.idfw
│   ├── medium_complexity.idfw
│   ├── complex_document.idfw
│   ├── diagram_flowchart.idfw
│   └── variables_all_types.idfw
├── force/
│   ├── simple_tool.force
│   ├── complex_tool.force
│   ├── pattern_example.force
│   └── constraint_rules.force
└── unified/
    ├── command_schema.json
    └── workflow_schema.json
```

---

## Continuous Integration

### GitHub Actions Workflows

#### Workflow 1: Pull Request Tests
```yaml
# .github/workflows/pr-tests.yml
name: PR Tests

on:
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run unit tests
        run: pytest tests/unit -v --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run integration tests
        run: pytest tests/integration -v
```

#### Workflow 2: Daily Performance Tests
```yaml
# .github/workflows/daily-performance.yml
name: Daily Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt pytest-benchmark
      - name: Run benchmarks
        run: pytest tests/performance --benchmark-only --benchmark-json=output.json
      - name: Compare with baseline
        run: python scripts/compare_benchmarks.py
```

---

## Summary

### Test Coverage Summary

| Category | Tests | Coverage | Time |
|----------|-------|----------|------|
| Unit | 200+ | 80%+ | < 30s |
| Integration | 50+ | 70%+ | < 2min |
| E2E | 10+ | 60%+ | < 5min |
| Performance | 20+ | N/A | < 3min |
| **Total** | **280+** | **80%+** | **< 10min** |

### Success Criteria

**Phase 1 Complete When**:
- ✅ 80%+ overall code coverage
- ✅ 200+ unit tests passing
- ✅ 50+ integration tests passing
- ✅ All critical paths tested
- ✅ Performance benchmarks meet targets
- ✅ CI/CD pipeline operational
- ✅ All tests run in < 10 minutes

---

**Document Version**: 1.0.0
**Created**: 2025-09-29
**Linear Project**: IDFWU (4d649a6501f7)
**Test Framework**: pytest 7.4+
**Python Version**: 3.11+

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
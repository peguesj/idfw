"""
Unit tests for MCP Server
Linear Project: 4d649a6501f7
Task: TEST-005 - MCP Server Tests

Tests cover:
- MCPServer initialization
- Tool registration and management
- Stdio transport operations
- HTTP transport operations (if implemented)
- Tool invocation and execution
- Request/response handling
- Error handling
- Protocol methods (tools/list, tools/call, tools/schema)
"""

import asyncio
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from unified_framework.mcp.server import (
    HTTPTransport,
    MCPRequest,
    MCPResponse,
    MCPServer,
    ParameterType,
    StdioTransport,
    Tool,
    ToolCategory,
    ToolParameter,
    ToolRegistry,
    TransportType,
    create_mcp_server,
)


# Fixtures directory
from pathlib import Path
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "mcp"


@pytest.fixture
def sample_tools() -> list[Dict[str, Any]]:
    """Load sample tools"""
    with open(FIXTURES_DIR / "sample_tools.json") as f:
        return json.load(f)


@pytest.fixture
def sample_requests() -> list[Dict[str, Any]]:
    """Load sample requests"""
    with open(FIXTURES_DIR / "sample_requests.json") as f:
        return json.load(f)


@pytest.fixture
def sample_responses() -> list[Dict[str, Any]]:
    """Load sample responses"""
    with open(FIXTURES_DIR / "sample_responses.json") as f:
        return json.load(f)


class TestToolParameterModel:
    """Tests for ToolParameter data model"""

    def test_tool_parameter_minimal(self):
        """Test ToolParameter with minimal configuration"""
        param = ToolParameter(
            name="test_param",
            type=ParameterType.STRING,
            description="Test parameter",
        )

        assert param.name == "test_param"
        assert param.type == ParameterType.STRING
        assert param.description == "Test parameter"
        assert param.required is False
        assert param.default is None
        assert param.enum is None

    def test_tool_parameter_full(self):
        """Test ToolParameter with all options"""
        param = ToolParameter(
            name="priority",
            type=ParameterType.STRING,
            description="Priority level",
            required=True,
            default="normal",
            enum=["low", "normal", "high", "urgent"],
        )

        assert param.name == "priority"
        assert param.required is True
        assert param.default == "normal"
        assert len(param.enum) == 4

    def test_tool_parameter_types(self):
        """Test different parameter types"""
        types = [
            ParameterType.STRING,
            ParameterType.INTEGER,
            ParameterType.BOOLEAN,
            ParameterType.NUMBER,
            ParameterType.ARRAY,
            ParameterType.OBJECT,
        ]

        for param_type in types:
            param = ToolParameter(
                name=f"param_{param_type.value}",
                type=param_type,
                description=f"Test {param_type.value}",
            )
            assert param.type == param_type


class TestToolModel:
    """Tests for Tool data model"""

    def test_tool_minimal(self):
        """Test Tool with minimal configuration"""
        tool = Tool(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.UNIFIED,
        )

        assert tool.name == "test_tool"
        assert tool.description == "Test tool"
        assert tool.category == ToolCategory.UNIFIED
        assert len(tool.parameters) == 0
        assert tool.return_type == "object"
        assert len(tool.examples) == 0
        assert tool.handler is None

    def test_tool_with_parameters(self):
        """Test Tool with parameters"""
        params = [
            ToolParameter(name="input", type=ParameterType.STRING, description="Input text"),
            ToolParameter(name="count", type=ParameterType.INTEGER, description="Count"),
        ]

        tool = Tool(
            name="parameterized_tool",
            description="Tool with parameters",
            category=ToolCategory.COMMAND,
            parameters=params,
        )

        assert len(tool.parameters) == 2
        assert tool.parameters[0].name == "input"
        assert tool.parameters[1].name == "count"

    def test_tool_with_handler(self):
        """Test Tool with handler function"""
        async def test_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "success"}

        tool = Tool(
            name="handler_tool",
            description="Tool with handler",
            category=ToolCategory.AGENT,
            handler=test_handler,
        )

        assert tool.handler is not None
        assert asyncio.iscoroutinefunction(tool.handler)

    def test_tool_categories(self):
        """Test different tool categories"""
        categories = [
            ToolCategory.IDFW,
            ToolCategory.FORCE,
            ToolCategory.UNIFIED,
            ToolCategory.AGENT,
            ToolCategory.SCHEMA,
            ToolCategory.COMMAND,
        ]

        for category in categories:
            tool = Tool(
                name=f"tool_{category.value}",
                description=f"Test {category.value}",
                category=category,
            )
            assert tool.category == category


class TestToolRegistry:
    """Tests for ToolRegistry"""

    def test_registry_initialization(self):
        """Test ToolRegistry initialization"""
        registry = ToolRegistry()

        assert len(registry.tools) == 0
        assert len(registry.categories) == len(ToolCategory)

    def test_register_tool(self):
        """Test registering a tool"""
        registry = ToolRegistry()

        tool = Tool(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.UNIFIED,
        )

        registry.register(tool)

        assert "test_tool" in registry.tools
        assert "test_tool" in registry.categories[ToolCategory.UNIFIED]

    def test_register_duplicate_tool(self):
        """Test registering duplicate tool (should log warning)"""
        registry = ToolRegistry()

        tool = Tool(
            name="duplicate_tool",
            description="Test tool",
            category=ToolCategory.UNIFIED,
        )

        registry.register(tool)
        registry.register(tool)  # Should not raise error

        assert len(registry.tools) == 1

    def test_unregister_tool(self):
        """Test unregistering a tool"""
        registry = ToolRegistry()

        tool = Tool(
            name="remove_me",
            description="Test tool",
            category=ToolCategory.COMMAND,
        )

        registry.register(tool)
        success = registry.unregister("remove_me")

        assert success is True
        assert "remove_me" not in registry.tools
        assert "remove_me" not in registry.categories[ToolCategory.COMMAND]

    def test_unregister_nonexistent_tool(self):
        """Test unregistering non-existent tool"""
        registry = ToolRegistry()

        success = registry.unregister("nonexistent")

        assert success is False

    def test_get_tool(self):
        """Test getting a tool by name"""
        registry = ToolRegistry()

        tool = Tool(
            name="get_me",
            description="Test tool",
            category=ToolCategory.AGENT,
        )

        registry.register(tool)
        retrieved = registry.get("get_me")

        assert retrieved is not None
        assert retrieved.name == "get_me"

    def test_get_nonexistent_tool(self):
        """Test getting non-existent tool"""
        registry = ToolRegistry()

        retrieved = registry.get("nonexistent")

        assert retrieved is None

    def test_list_all_tools(self):
        """Test listing all tools"""
        registry = ToolRegistry()

        for i in range(5):
            tool = Tool(
                name=f"tool_{i}",
                description=f"Tool {i}",
                category=ToolCategory.UNIFIED,
            )
            registry.register(tool)

        tools = registry.list_tools()

        assert len(tools) == 5

    def test_list_tools_by_category(self):
        """Test listing tools filtered by category"""
        registry = ToolRegistry()

        # Register tools in different categories
        for category in [ToolCategory.IDFW, ToolCategory.FORCE, ToolCategory.UNIFIED]:
            for i in range(2):
                tool = Tool(
                    name=f"{category.value}_tool_{i}",
                    description=f"Tool {i}",
                    category=category,
                )
                registry.register(tool)

        idfw_tools = registry.list_tools(category=ToolCategory.IDFW)
        force_tools = registry.list_tools(category=ToolCategory.FORCE)

        assert len(idfw_tools) == 2
        assert len(force_tools) == 2

    def test_get_tool_schema(self):
        """Test getting tool schema"""
        registry = ToolRegistry()

        params = [
            ToolParameter(
                name="input",
                type=ParameterType.STRING,
                description="Input text",
                required=True,
            ),
            ToolParameter(
                name="count",
                type=ParameterType.INTEGER,
                description="Count",
                default=1,
            ),
        ]

        tool = Tool(
            name="schema_tool",
            description="Tool with schema",
            category=ToolCategory.COMMAND,
            parameters=params,
        )

        registry.register(tool)
        schema = registry.get_tool_schema("schema_tool")

        assert schema is not None
        assert schema["name"] == "schema_tool"
        assert "parameters" in schema
        assert "input" in schema["parameters"]["properties"]
        assert "count" in schema["parameters"]["properties"]
        assert "input" in schema["parameters"]["required"]
        assert "count" not in schema["parameters"]["required"]

    def test_get_schema_nonexistent_tool(self):
        """Test getting schema for non-existent tool"""
        registry = ToolRegistry()

        schema = registry.get_tool_schema("nonexistent")

        assert schema is None


class TestStdioTransport:
    """Tests for StdioTransport"""

    @pytest.mark.asyncio
    async def test_stdio_initialization(self):
        """Test StdioTransport initialization"""
        transport = StdioTransport()

        assert transport._running is False

    @pytest.mark.asyncio
    async def test_stdio_start(self):
        """Test starting stdio transport"""
        transport = StdioTransport()

        await transport.start()

        assert transport._running is True

        await transport.stop()

    @pytest.mark.asyncio
    async def test_stdio_stop(self):
        """Test stopping stdio transport"""
        transport = StdioTransport()

        await transport.start()
        await transport.stop()

        assert transport._running is False

    @pytest.mark.asyncio
    async def test_stdio_send_response(self):
        """Test sending response via stdio"""
        transport = StdioTransport()

        response = MCPResponse(
            id="req-123",
            result={"status": "success"},
        )

        # Mock stdout
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.write = Mock()
            mock_stdout.flush = Mock()

            await transport.send_response(response)

            mock_stdout.write.assert_called_once()
            mock_stdout.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_stdio_receive_request(self):
        """Test receiving request via stdio"""
        transport = StdioTransport()

        await transport.start()

        request_json = json.dumps({
            "id": "req-456",
            "method": "tools/list",
            "params": {},
        }) + "\n"

        # Mock stdin
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = Mock(return_value=request_json)

            request = await transport.receive_request()

            assert request is not None
            assert request.id == "req-456"
            assert request.method == "tools/list"

        await transport.stop()

    @pytest.mark.asyncio
    async def test_stdio_receive_invalid_json(self):
        """Test receiving invalid JSON"""
        transport = StdioTransport()

        await transport.start()

        # Mock stdin with invalid JSON
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.readline = Mock(return_value="invalid json\n")

            request = await transport.receive_request()

            assert request is None

        await transport.stop()


class TestHTTPTransport:
    """Tests for HTTPTransport"""

    @pytest.mark.asyncio
    async def test_http_initialization(self):
        """Test HTTPTransport initialization"""
        transport = HTTPTransport(host="localhost", port=8080)

        assert transport.host == "localhost"
        assert transport.port == 8080
        assert transport._running is False

    @pytest.mark.asyncio
    async def test_http_start(self):
        """Test starting HTTP transport"""
        transport = HTTPTransport()

        await transport.start()

        assert transport._running is True

        await transport.stop()

    @pytest.mark.asyncio
    async def test_http_stop(self):
        """Test stopping HTTP transport"""
        transport = HTTPTransport()

        await transport.start()
        await transport.stop()

        assert transport._running is False

    @pytest.mark.asyncio
    async def test_http_send_response(self):
        """Test sending response via HTTP"""
        transport = HTTPTransport()

        response = MCPResponse(
            id="req-789",
            result={"status": "success"},
        )

        # Register callback
        callback_called = False

        def callback(resp):
            nonlocal callback_called
            callback_called = True
            assert resp.id == "req-789"

        transport.response_callbacks["req-789"] = callback

        await transport.send_response(response)

        assert callback_called
        assert "req-789" not in transport.response_callbacks

    @pytest.mark.asyncio
    async def test_http_receive_request(self):
        """Test receiving request via HTTP"""
        transport = HTTPTransport()

        await transport.start()

        # Queue a request
        request = MCPRequest(
            id="req-999",
            method="tools/call",
            params={"tool_name": "test_tool"},
        )

        await transport.request_queue.put(request)

        # Receive it
        received = await transport.receive_request()

        assert received is not None
        assert received.id == "req-999"
        assert received.method == "tools/call"

        await transport.stop()

    @pytest.mark.asyncio
    async def test_http_receive_timeout(self):
        """Test receive timeout when no requests"""
        transport = HTTPTransport()

        await transport.start()

        # Try to receive with no requests queued
        received = await transport.receive_request()

        assert received is None

        await transport.stop()


class TestMCPServer:
    """Tests for MCPServer"""

    @pytest.mark.asyncio
    async def test_server_initialization_default(self):
        """Test MCPServer initialization with defaults"""
        server = MCPServer()

        assert server.registry is not None
        assert server.transport is not None
        assert isinstance(server.transport, StdioTransport)
        assert server._running is False

    @pytest.mark.asyncio
    async def test_server_initialization_custom(self):
        """Test MCPServer initialization with custom components"""
        registry = ToolRegistry()
        transport = HTTPTransport()

        server = MCPServer(registry=registry, transport=transport)

        assert server.registry is registry
        assert server.transport is transport

    @pytest.mark.asyncio
    async def test_server_start(self):
        """Test starting MCP server"""
        server = MCPServer()

        await server.start()

        assert server._running is True

        await server.stop()

    @pytest.mark.asyncio
    async def test_server_stop(self):
        """Test stopping MCP server"""
        server = MCPServer()

        await server.start()
        await server.stop()

        assert server._running is False

    @pytest.mark.asyncio
    async def test_handle_list_tools_request(self):
        """Test handling tools/list request"""
        registry = ToolRegistry()

        # Register some tools
        for i in range(3):
            tool = Tool(
                name=f"tool_{i}",
                description=f"Tool {i}",
                category=ToolCategory.UNIFIED,
            )
            registry.register(tool)

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-001",
            method="tools/list",
            params={},
        )

        response = await server._handle_request(request)

        assert response.id == "req-001"
        assert response.error is None
        assert response.result is not None
        assert "tools" in response.result
        assert len(response.result["tools"]) == 3

    @pytest.mark.asyncio
    async def test_handle_list_tools_by_category(self):
        """Test handling tools/list with category filter"""
        registry = ToolRegistry()

        # Register tools in different categories
        registry.register(Tool(name="idfw_tool", description="IDFW", category=ToolCategory.IDFW))
        registry.register(Tool(name="force_tool", description="Force", category=ToolCategory.FORCE))

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-002",
            method="tools/list",
            params={"category": "idfw"},
        )

        response = await server._handle_request(request)

        assert len(response.result["tools"]) == 1
        assert response.result["tools"][0]["name"] == "idfw_tool"

    @pytest.mark.asyncio
    async def test_handle_list_tools_invalid_category(self):
        """Test handling tools/list with invalid category"""
        server = MCPServer()

        request = MCPRequest(
            id="req-003",
            method="tools/list",
            params={"category": "invalid_category"},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32602

    @pytest.mark.asyncio
    async def test_handle_get_schema_request(self):
        """Test handling tools/schema request"""
        registry = ToolRegistry()

        params = [
            ToolParameter(
                name="input",
                type=ParameterType.STRING,
                description="Input",
                required=True,
            )
        ]

        tool = Tool(
            name="test_tool",
            description="Test",
            category=ToolCategory.COMMAND,
            parameters=params,
        )

        registry.register(tool)

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-004",
            method="tools/schema",
            params={"tool_name": "test_tool"},
        )

        response = await server._handle_request(request)

        assert response.error is None
        assert response.result is not None
        assert response.result["name"] == "test_tool"
        assert "parameters" in response.result

    @pytest.mark.asyncio
    async def test_handle_get_schema_missing_tool_name(self):
        """Test handling tools/schema without tool_name"""
        server = MCPServer()

        request = MCPRequest(
            id="req-005",
            method="tools/schema",
            params={},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32602
        assert "Missing parameter" in response.error["message"]

    @pytest.mark.asyncio
    async def test_handle_get_schema_nonexistent_tool(self):
        """Test handling tools/schema for non-existent tool"""
        server = MCPServer()

        request = MCPRequest(
            id="req-006",
            method="tools/schema",
            params={"tool_name": "nonexistent"},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32602
        assert "Tool not found" in response.error["message"]

    @pytest.mark.asyncio
    async def test_handle_call_tool_request(self):
        """Test handling tools/call request"""
        async def test_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": f"processed {args.get('input', '')}"}

        registry = ToolRegistry()
        tool = Tool(
            name="callable_tool",
            description="Callable",
            category=ToolCategory.COMMAND,
            handler=test_handler,
        )
        registry.register(tool)

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-007",
            method="tools/call",
            params={
                "tool_name": "callable_tool",
                "arguments": {"input": "test_data"},
            },
        )

        response = await server._handle_request(request)

        assert response.error is None
        assert response.result is not None
        assert response.result["result"] == "processed test_data"

    @pytest.mark.asyncio
    async def test_handle_call_tool_missing_tool_name(self):
        """Test handling tools/call without tool_name"""
        server = MCPServer()

        request = MCPRequest(
            id="req-008",
            method="tools/call",
            params={"arguments": {}},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32602

    @pytest.mark.asyncio
    async def test_handle_call_tool_nonexistent(self):
        """Test handling tools/call for non-existent tool"""
        server = MCPServer()

        request = MCPRequest(
            id="req-009",
            method="tools/call",
            params={"tool_name": "nonexistent", "arguments": {}},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32602
        assert "Tool not found" in response.error["message"]

    @pytest.mark.asyncio
    async def test_handle_call_tool_no_handler(self):
        """Test handling tools/call for tool without handler"""
        registry = ToolRegistry()
        tool = Tool(
            name="no_handler",
            description="No handler",
            category=ToolCategory.COMMAND,
            handler=None,
        )
        registry.register(tool)

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-010",
            method="tools/call",
            params={"tool_name": "no_handler", "arguments": {}},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32603
        assert "no handler" in response.error["message"]

    @pytest.mark.asyncio
    async def test_handle_call_tool_handler_error(self):
        """Test handling tools/call when handler raises error"""
        async def failing_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            raise ValueError("Handler failed")

        registry = ToolRegistry()
        tool = Tool(
            name="failing_tool",
            description="Failing",
            category=ToolCategory.COMMAND,
            handler=failing_handler,
        )
        registry.register(tool)

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-011",
            method="tools/call",
            params={"tool_name": "failing_tool", "arguments": {}},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32603
        assert "Handler failed" in response.error["message"]

    @pytest.mark.asyncio
    async def test_handle_unknown_method(self):
        """Test handling unknown method"""
        server = MCPServer()

        request = MCPRequest(
            id="req-012",
            method="unknown/method",
            params={},
        )

        response = await server._handle_request(request)

        assert response.error is not None
        assert response.error["code"] == -32601
        assert "Method not found" in response.error["message"]


class TestCreateMCPServer:
    """Tests for create_mcp_server factory function"""

    def test_create_server_stdio(self):
        """Test creating server with stdio transport"""
        server = create_mcp_server(transport_type=TransportType.STDIO)

        assert isinstance(server, MCPServer)
        assert isinstance(server.transport, StdioTransport)
        assert isinstance(server.registry, ToolRegistry)

    def test_create_server_http(self):
        """Test creating server with HTTP transport"""
        server = create_mcp_server(
            transport_type=TransportType.HTTP,
            host="localhost",
            port=9000,
        )

        assert isinstance(server, MCPServer)
        assert isinstance(server.transport, HTTPTransport)
        assert server.transport.host == "localhost"
        assert server.transport.port == 9000

    def test_create_server_unsupported_transport(self):
        """Test creating server with unsupported transport"""
        with pytest.raises(ValueError, match="Unsupported transport type"):
            create_mcp_server(transport_type=TransportType.WEBSOCKET)


class TestRequestResponseModels:
    """Tests for request/response data models"""

    def test_mcp_request_creation(self):
        """Test MCPRequest creation"""
        request = MCPRequest(
            id="req-123",
            method="tools/list",
            params={"category": "idfw"},
        )

        assert request.id == "req-123"
        assert request.method == "tools/list"
        assert request.params == {"category": "idfw"}

    def test_mcp_response_with_result(self):
        """Test MCPResponse with result"""
        response = MCPResponse(
            id="req-456",
            result={"status": "success"},
        )

        assert response.id == "req-456"
        assert response.result == {"status": "success"}
        assert response.error is None

    def test_mcp_response_with_error(self):
        """Test MCPResponse with error"""
        response = MCPResponse(
            id="req-789",
            error={"code": -32600, "message": "Invalid request"},
        )

        assert response.id == "req-789"
        assert response.result is None
        assert response.error["code"] == -32600


class TestConcurrentOperations:
    """Tests for concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_tool_registration(self):
        """Test registering tools concurrently"""
        registry = ToolRegistry()

        async def register_tool(i):
            tool = Tool(
                name=f"concurrent_tool_{i}",
                description=f"Tool {i}",
                category=ToolCategory.UNIFIED,
            )
            registry.register(tool)

        # Register concurrently
        await asyncio.gather(*[register_tool(i) for i in range(10)])

        assert len(registry.tools) == 10

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test calling tools concurrently"""
        call_count = 0

        async def counting_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate work
            return {"count": call_count}

        registry = ToolRegistry()
        tool = Tool(
            name="counter_tool",
            description="Counter",
            category=ToolCategory.COMMAND,
            handler=counting_handler,
        )
        registry.register(tool)

        server = MCPServer(registry=registry)

        # Make concurrent calls
        requests = [
            MCPRequest(
                id=f"req-{i}",
                method="tools/call",
                params={"tool_name": "counter_tool", "arguments": {}},
            )
            for i in range(5)
        ]

        responses = await asyncio.gather(
            *[server._handle_request(req) for req in requests]
        )

        assert len(responses) == 5
        assert all(r.error is None for r in responses)
        assert call_count == 5


class TestEdgeCases:
    """Tests for edge cases"""

    @pytest.mark.asyncio
    async def test_empty_tool_name(self):
        """Test handling empty tool name"""
        server = MCPServer()

        request = MCPRequest(
            id="req-empty",
            method="tools/schema",
            params={"tool_name": ""},
        )

        response = await server._handle_request(request)

        assert response.error is not None

    @pytest.mark.asyncio
    async def test_null_arguments(self):
        """Test tool call with null arguments"""
        async def handler(args: Dict[str, Any]) -> Dict[str, Any]:
            return {"received": args}

        registry = ToolRegistry()
        tool = Tool(
            name="null_args_tool",
            description="Test",
            category=ToolCategory.COMMAND,
            handler=handler,
        )
        registry.register(tool)

        server = MCPServer(registry=registry)

        request = MCPRequest(
            id="req-null",
            method="tools/call",
            params={"tool_name": "null_args_tool"},  # No arguments key
        )

        response = await server._handle_request(request)

        assert response.error is None
        assert response.result["received"] == {}

    @pytest.mark.asyncio
    async def test_large_payload(self):
        """Test handling large payload"""
        async def handler(args: Dict[str, Any]) -> Dict[str, Any]:
            return {"size": len(args.get("data", ""))}

        registry = ToolRegistry()
        tool = Tool(
            name="large_payload_tool",
            description="Test",
            category=ToolCategory.COMMAND,
            handler=handler,
        )
        registry.register(tool)

        server = MCPServer(registry=registry)

        large_data = "x" * 100000  # 100KB

        request = MCPRequest(
            id="req-large",
            method="tools/call",
            params={
                "tool_name": "large_payload_tool",
                "arguments": {"data": large_data},
            },
        )

        response = await server._handle_request(request)

        assert response.error is None
        assert response.result["size"] == 100000
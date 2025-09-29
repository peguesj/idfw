"""
Unified MCP Server for IDFWU Framework
Linear Project: 4d649a6501f7

This module provides the unified MCP (Model Context Protocol) server implementation
with tool registry integration and protocol handlers for stdio and HTTP transports.
"""

import asyncio
import json
import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

from pydantic import BaseModel, Field, ConfigDict


# Configure logging
logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Tool categories for organization"""
    IDFW = "idfw"
    FORCE = "force"
    UNIFIED = "unified"
    AGENT = "agent"
    SCHEMA = "schema"
    COMMAND = "command"


class ParameterType(str, Enum):
    """Parameter types"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    NUMBER = "number"
    ARRAY = "array"
    OBJECT = "object"


class TransportType(str, Enum):
    """Transport layer types"""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    type: ParameterType
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    properties: Optional[Dict[str, 'ToolParameter']] = None


class Tool(BaseModel):
    """MCP Tool definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter] = Field(default_factory=list)
    return_type: str = "object"
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    handler: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None


@dataclass
class MCPRequest:
    """MCP protocol request"""
    id: str
    method: str
    params: Dict[str, Any]


@dataclass
class MCPResponse:
    """MCP protocol response"""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ToolRegistry:
    """
    Registry for MCP tools
    """

    def __init__(self) -> None:
        """Initialize tool registry"""
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {
            cat: [] for cat in ToolCategory
        }

        logger.info("Initialized tool registry")

    def register(self, tool: Tool) -> None:
        """
        Register a tool

        Args:
            tool: Tool to register
        """
        if tool.name in self.tools:
            logger.warning(f"Tool already registered: {tool.name}")
            return

        self.tools[tool.name] = tool
        self.categories[tool.category].append(tool.name)

        logger.info(f"Registered tool: {tool.name} ({tool.category.value})")

    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool

        Args:
            tool_name: Name of tool to unregister

        Returns:
            True if successful
        """
        tool = self.tools.get(tool_name)

        if not tool:
            return False

        del self.tools[tool_name]
        self.categories[tool.category].remove(tool_name)

        logger.info(f"Unregistered tool: {tool_name}")
        return True

    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name

        Args:
            tool_name: Tool name

        Returns:
            Tool or None if not found
        """
        return self.tools.get(tool_name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[Tool]:
        """
        List registered tools

        Args:
            category: Optional category filter

        Returns:
            List of tools
        """
        if category:
            tool_names = self.categories.get(category, [])
            return [self.tools[name] for name in tool_names]

        return list(self.tools.values())

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool schema in JSON Schema format

        Args:
            tool_name: Tool name

        Returns:
            Tool schema or None
        """
        tool = self.get(tool_name)

        if not tool:
            return None

        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type.value,
                "description": param.description,
            }

            if param.default is not None:
                properties[param.name]["default"] = param.default

            if param.enum:
                properties[param.name]["enum"] = param.enum

            if param.required:
                required.append(param.name)

        schema = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

        return schema


class MCPTransport(ABC):
    """Base class for MCP transports"""

    @abstractmethod
    async def start(self) -> None:
        """Start the transport"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport"""
        pass

    @abstractmethod
    async def send_response(self, response: MCPResponse) -> None:
        """Send a response"""
        pass

    @abstractmethod
    async def receive_request(self) -> Optional[MCPRequest]:
        """Receive a request"""
        pass


class StdioTransport(MCPTransport):
    """Standard I/O transport for MCP"""

    def __init__(self) -> None:
        """Initialize stdio transport"""
        self._running = False
        logger.info("Initialized stdio transport")

    async def start(self) -> None:
        """Start stdio transport"""
        self._running = True
        logger.info("Started stdio transport")

    async def stop(self) -> None:
        """Stop stdio transport"""
        self._running = False
        logger.info("Stopped stdio transport")

    async def send_response(self, response: MCPResponse) -> None:
        """
        Send response to stdout

        Args:
            response: MCP response
        """
        data = {
            "id": response.id,
            "result": response.result,
            "error": response.error,
        }

        sys.stdout.write(json.dumps(data) + "\n")
        sys.stdout.flush()

    async def receive_request(self) -> Optional[MCPRequest]:
        """
        Receive request from stdin

        Returns:
            MCP request or None
        """
        if not self._running:
            return None

        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )

            if not line:
                return None

            data = json.loads(line)

            return MCPRequest(
                id=data.get("id", ""),
                method=data.get("method", ""),
                params=data.get("params", {}),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse request: {e}")
            return None


class HTTPTransport(MCPTransport):
    """HTTP transport for MCP"""

    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        """
        Initialize HTTP transport

        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self._running = False
        self.request_queue: asyncio.Queue[MCPRequest] = asyncio.Queue()
        self.response_callbacks: Dict[str, Callable[[MCPResponse], None]] = {}

        logger.info(f"Initialized HTTP transport at {host}:{port}")

    async def start(self) -> None:
        """Start HTTP server"""
        self._running = True
        # In production, this would start an actual HTTP server
        logger.info(f"Started HTTP transport at {self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop HTTP server"""
        self._running = False
        logger.info("Stopped HTTP transport")

    async def send_response(self, response: MCPResponse) -> None:
        """
        Send HTTP response

        Args:
            response: MCP response
        """
        callback = self.response_callbacks.get(response.id)
        if callback:
            callback(response)
            del self.response_callbacks[response.id]

    async def receive_request(self) -> Optional[MCPRequest]:
        """
        Receive HTTP request

        Returns:
            MCP request or None
        """
        if not self._running:
            return None

        try:
            request = await asyncio.wait_for(
                self.request_queue.get(),
                timeout=1.0,
            )
            return request
        except asyncio.TimeoutError:
            return None


class MCPServer:
    """
    Unified MCP Server for IDFWU Framework
    """

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        transport: Optional[MCPTransport] = None,
    ) -> None:
        """
        Initialize MCP server

        Args:
            registry: Tool registry
            transport: Transport layer
        """
        self.registry = registry or ToolRegistry()
        self.transport = transport or StdioTransport()
        self._running = False

        logger.info("Initialized MCP server")

    async def start(self) -> None:
        """Start the MCP server"""
        self._running = True
        await self.transport.start()

        logger.info("MCP server started")

        # Start request processing loop
        asyncio.create_task(self._process_requests())

    async def stop(self) -> None:
        """Stop the MCP server"""
        self._running = False
        await self.transport.stop()

        logger.info("MCP server stopped")

    async def _process_requests(self) -> None:
        """Main request processing loop"""
        while self._running:
            try:
                request = await self.transport.receive_request()

                if not request:
                    continue

                # Handle request
                response = await self._handle_request(request)

                # Send response
                await self.transport.send_response(response)

            except Exception as e:
                logger.error(f"Error processing request: {e}")

    async def _handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle an MCP request

        Args:
            request: MCP request

        Returns:
            MCP response
        """
        method = request.method

        # Handle protocol methods
        if method == "tools/list":
            return await self._handle_list_tools(request)
        elif method == "tools/call":
            return await self._handle_call_tool(request)
        elif method == "tools/schema":
            return await self._handle_get_schema(request)
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            )

    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """
        Handle tools/list request

        Args:
            request: MCP request

        Returns:
            MCP response
        """
        category = request.params.get("category")

        if category:
            try:
                category = ToolCategory(category)
            except ValueError:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": f"Invalid category: {category}",
                    },
                )

        tools = self.registry.list_tools(category)

        result = {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category.value,
                }
                for tool in tools
            ]
        }

        return MCPResponse(id=request.id, result=result)

    async def _handle_get_schema(self, request: MCPRequest) -> MCPResponse:
        """
        Handle tools/schema request

        Args:
            request: MCP request

        Returns:
            MCP response
        """
        tool_name = request.params.get("tool_name")

        if not tool_name:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,
                    "message": "Missing parameter: tool_name",
                },
            )

        schema = self.registry.get_tool_schema(tool_name)

        if not schema:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,
                    "message": f"Tool not found: {tool_name}",
                },
            )

        return MCPResponse(id=request.id, result=schema)

    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """
        Handle tools/call request

        Args:
            request: MCP request

        Returns:
            MCP response
        """
        tool_name = request.params.get("tool_name")
        arguments = request.params.get("arguments", {})

        if not tool_name:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,
                    "message": "Missing parameter: tool_name",
                },
            )

        tool = self.registry.get(tool_name)

        if not tool:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,
                    "message": f"Tool not found: {tool_name}",
                },
            )

        if not tool.handler:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool has no handler: {tool_name}",
                },
            )

        try:
            result = await tool.handler(arguments)
            return MCPResponse(id=request.id, result=result)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}",
                },
            )


def create_mcp_server(
    transport_type: TransportType = TransportType.STDIO,
    host: str = "localhost",
    port: int = 8080,
) -> MCPServer:
    """
    Create MCP server with specified transport

    Args:
        transport_type: Type of transport to use
        host: Host for HTTP transport
        port: Port for HTTP transport

    Returns:
        Configured MCP server
    """
    registry = ToolRegistry()

    if transport_type == TransportType.STDIO:
        transport = StdioTransport()
    elif transport_type == TransportType.HTTP:
        transport = HTTPTransport(host, port)
    else:
        raise ValueError(f"Unsupported transport type: {transport_type}")

    server = MCPServer(registry, transport)

    logger.info(f"Created MCP server with {transport_type.value} transport")
    return server
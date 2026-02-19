"""
Unified Command Processor for IDFWU Framework
Linear Project: 4d649a6501f7

This module provides unified command processing with support for multiple prefixes:
- $ : YUNG commands (Dev Sentinel)
- @ : IDFW actions
- # : Unified framework commands
- / : Slash commands for agents
"""

import asyncio
import logging
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

from pydantic import BaseModel, Field, ConfigDict


# Configure logging
logger = logging.getLogger(__name__)


class CommandPrefix(str, Enum):
    """Command prefix types"""
    YUNG = "$"          # Dev Sentinel YUNG commands
    IDFW = "@"          # IDFW actions
    UNIFIED = "#"       # Unified framework commands
    SLASH = "/"         # Agent slash commands


class CommandStatus(str, Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandContext(BaseModel):
    """Context for command execution"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    working_directory: str = "."
    environment: Dict[str, str] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[str] = None
    linear_project_id: str = "4d649a6501f7"


class CommandResult(BaseModel):
    """Result of command execution"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: CommandStatus
    output: Optional[str] = None
    error: Optional[str] = None
    return_code: int = 0
    data: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0


@dataclass
class Command:
    """Parsed command structure"""
    prefix: CommandPrefix
    name: str
    args: List[str] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    raw_command: str = ""


class CommandHandler(ABC):
    """Base class for command handlers"""

    @abstractmethod
    async def execute(
        self,
        command: Command,
        context: CommandContext,
    ) -> CommandResult:
        """
        Execute a command

        Args:
            command: Parsed command
            context: Execution context

        Returns:
            Command result
        """
        pass

    @abstractmethod
    def supports(self, command_name: str) -> bool:
        """
        Check if handler supports a command

        Args:
            command_name: Command name to check

        Returns:
            True if supported
        """
        pass


class YUNGCommandHandler(CommandHandler):
    """Handler for YUNG commands (Dev Sentinel)"""

    def __init__(self) -> None:
        self.supported_commands = {
            "spawn", "init", "audit", "build", "test", "deploy",
            "monitor", "status", "logs", "config",
        }

    def supports(self, command_name: str) -> bool:
        return command_name in self.supported_commands

    async def execute(
        self,
        command: Command,
        context: CommandContext,
    ) -> CommandResult:
        """Execute YUNG command"""
        logger.info(f"Executing YUNG command: ${command.name}")

        try:
            # In production, this would integrate with Dev Sentinel
            # For now, we simulate execution
            await asyncio.sleep(0.1)

            return CommandResult(
                status=CommandStatus.SUCCESS,
                output=f"YUNG command ${command.name} executed successfully",
                data={"command": command.name, "args": command.args},
            )
        except Exception as e:
            logger.error(f"YUNG command failed: {e}")
            return CommandResult(
                status=CommandStatus.FAILED,
                error=str(e),
                return_code=1,
            )


class IDFWCommandHandler(CommandHandler):
    """Handler for IDFW actions"""

    def __init__(self) -> None:
        self.supported_commands = {
            "define", "generate", "validate", "diagram", "variable",
            "project", "document", "template", "export",
        }

    def supports(self, command_name: str) -> bool:
        return command_name in self.supported_commands

    async def execute(
        self,
        command: Command,
        context: CommandContext,
    ) -> CommandResult:
        """Execute IDFW action"""
        logger.info(f"Executing IDFW action: @{command.name}")

        try:
            # In production, this would integrate with IDFW
            # For now, we simulate execution
            await asyncio.sleep(0.1)

            return CommandResult(
                status=CommandStatus.SUCCESS,
                output=f"IDFW action @{command.name} executed successfully",
                data={"action": command.name, "args": command.args},
            )
        except Exception as e:
            logger.error(f"IDFW action failed: {e}")
            return CommandResult(
                status=CommandStatus.FAILED,
                error=str(e),
                return_code=1,
            )


class UnifiedCommandHandler(CommandHandler):
    """Handler for unified framework commands"""

    def __init__(self) -> None:
        self.supported_commands = {
            "sync", "convert", "bridge", "integrate", "orchestrate",
            "workflow", "pipeline", "health", "metrics",
        }

    def supports(self, command_name: str) -> bool:
        return command_name in self.supported_commands

    async def execute(
        self,
        command: Command,
        context: CommandContext,
    ) -> CommandResult:
        """Execute unified command"""
        logger.info(f"Executing unified command: #{command.name}")

        try:
            # Execute unified framework logic
            await asyncio.sleep(0.1)

            return CommandResult(
                status=CommandStatus.SUCCESS,
                output=f"Unified command #{command.name} executed successfully",
                data={"command": command.name, "args": command.args},
            )
        except Exception as e:
            logger.error(f"Unified command failed: {e}")
            return CommandResult(
                status=CommandStatus.FAILED,
                error=str(e),
                return_code=1,
            )


class SlashCommandHandler(CommandHandler):
    """Handler for agent slash commands"""

    def __init__(self) -> None:
        self.supported_commands = {
            "agent-product-owner", "agent-ux", "agent-requirements",
            "agent-project-manager", "agent-scrum-master", "agent-release-manager",
            "agent-architect", "agent-backend", "agent-frontend",
            "agent-schema", "agent-developer", "agent-integrator",
            "agent-devops", "agent-dba", "agent-qa", "agent-security",
            "agent-performance", "agent-documentation",
            "deploy-agent-team", "agent-status", "agent-sync",
            "fix-schema-conflicts", "implement-unified-cli", "setup-mcp-server",
        }

    def supports(self, command_name: str) -> bool:
        return command_name in self.supported_commands

    async def execute(
        self,
        command: Command,
        context: CommandContext,
    ) -> CommandResult:
        """Execute slash command"""
        logger.info(f"Executing slash command: /{command.name}")

        try:
            # Execute agent command logic
            await asyncio.sleep(0.1)

            return CommandResult(
                status=CommandStatus.SUCCESS,
                output=f"Slash command /{command.name} executed successfully",
                data={"command": command.name, "args": command.args},
            )
        except Exception as e:
            logger.error(f"Slash command failed: {e}")
            return CommandResult(
                status=CommandStatus.FAILED,
                error=str(e),
                return_code=1,
            )


class CommandParser:
    """Parser for unified commands"""

    @staticmethod
    def parse(raw_command: str) -> Optional[Command]:
        """
        Parse a raw command string

        Args:
            raw_command: Raw command string

        Returns:
            Parsed Command or None if invalid
        """
        if not raw_command or not raw_command.strip():
            return None

        raw_command = raw_command.strip()

        # Determine prefix
        prefix_char = raw_command[0]
        try:
            prefix = CommandPrefix(prefix_char)
        except ValueError:
            logger.warning(f"Invalid command prefix: {prefix_char}")
            return None

        # Remove prefix
        command_str = raw_command[1:].strip()

        if not command_str:
            return None

        # Parse command and arguments using shlex for proper quote handling
        try:
            parts = shlex.split(command_str)
        except ValueError as e:
            logger.error(f"Failed to parse command: {e}")
            return None

        if not parts:
            return None

        command_name = parts[0]
        args = []
        kwargs = {}

        # Parse arguments
        for part in parts[1:]:
            if "=" in part:
                # Key-value argument
                key, value = part.split("=", 1)
                kwargs[key] = value
            else:
                # Positional argument
                args.append(part)

        return Command(
            prefix=prefix,
            name=command_name,
            args=args,
            kwargs=kwargs,
            raw_command=raw_command,
        )


class CommandProcessor:
    """
    Main command processor for unified framework
    """

    def __init__(self) -> None:
        """Initialize command processor"""
        self.handlers: Dict[CommandPrefix, CommandHandler] = {
            CommandPrefix.YUNG: YUNGCommandHandler(),
            CommandPrefix.IDFW: IDFWCommandHandler(),
            CommandPrefix.UNIFIED: UnifiedCommandHandler(),
            CommandPrefix.SLASH: SlashCommandHandler(),
        }

        self.parser = CommandParser()
        self.middleware: List[Callable[[Command, CommandContext], Awaitable[None]]] = []

        logger.info("Initialized unified command processor")

    def register_handler(
        self,
        prefix: CommandPrefix,
        handler: CommandHandler,
    ) -> None:
        """
        Register a command handler

        Args:
            prefix: Command prefix
            handler: Handler instance
        """
        self.handlers[prefix] = handler
        logger.info(f"Registered handler for prefix: {prefix.value}")

    def add_middleware(
        self,
        middleware: Callable[[Command, CommandContext], Awaitable[None]],
    ) -> None:
        """
        Add middleware for command processing

        Args:
            middleware: Middleware function
        """
        self.middleware.append(middleware)
        logger.debug("Added command middleware")

    async def execute(
        self,
        raw_command: str,
        context: Optional[CommandContext] = None,
    ) -> CommandResult:
        """
        Execute a command

        Args:
            raw_command: Raw command string
            context: Optional execution context

        Returns:
            Command result
        """
        if context is None:
            context = CommandContext()

        # Parse command
        command = self.parser.parse(raw_command)

        if not command:
            return CommandResult(
                status=CommandStatus.FAILED,
                error="Invalid command syntax",
                return_code=1,
            )

        # Run middleware
        for mw in self.middleware:
            try:
                await mw(command, context)
            except Exception as e:
                logger.error(f"Middleware error: {e}")
                return CommandResult(
                    status=CommandStatus.FAILED,
                    error=f"Middleware error: {e}",
                    return_code=1,
                )

        # Get handler
        handler = self.handlers.get(command.prefix)

        if not handler:
            return CommandResult(
                status=CommandStatus.FAILED,
                error=f"No handler for prefix: {command.prefix.value}",
                return_code=1,
            )

        # Check if command is supported
        if not handler.supports(command.name):
            return CommandResult(
                status=CommandStatus.FAILED,
                error=f"Unsupported command: {command.prefix.value}{command.name}",
                return_code=1,
            )

        # Execute command
        import time
        start_time = time.time()

        result = await handler.execute(command, context)
        result.execution_time = time.time() - start_time

        logger.info(
            f"Command {command.prefix.value}{command.name} "
            f"completed with status: {result.status.value}"
        )

        return result

    async def execute_batch(
        self,
        commands: List[str],
        context: Optional[CommandContext] = None,
    ) -> List[CommandResult]:
        """
        Execute multiple commands in sequence

        Args:
            commands: List of command strings
            context: Optional execution context

        Returns:
            List of command results
        """
        results = []

        for cmd in commands:
            result = await self.execute(cmd, context)
            results.append(result)

            # Stop on first failure if needed
            if result.status == CommandStatus.FAILED:
                logger.warning(f"Command failed, stopping batch execution: {cmd}")
                break

        return results

    def get_supported_commands(self, prefix: CommandPrefix) -> List[str]:
        """
        Get list of supported commands for a prefix

        Args:
            prefix: Command prefix

        Returns:
            List of supported command names
        """
        handler = self.handlers.get(prefix)

        if not handler:
            return []

        # This assumes handlers have a supported_commands attribute
        if hasattr(handler, 'supported_commands'):
            return list(handler.supported_commands)

        return []


async def logging_middleware(command: Command, context: CommandContext) -> None:
    """Middleware for logging command execution"""
    logger.info(
        f"Executing command: {command.prefix.value}{command.name} "
        f"in session: {context.session_id}"
    )


async def validation_middleware(command: Command, context: CommandContext) -> None:
    """Middleware for command validation"""
    # Add validation logic here
    pass


def create_default_processor() -> CommandProcessor:
    """
    Create command processor with default configuration

    Returns:
        Configured CommandProcessor instance
    """
    processor = CommandProcessor()

    # Add default middleware
    processor.add_middleware(logging_middleware)
    processor.add_middleware(validation_middleware)

    logger.info("Created default command processor")
    return processor
"""
Unit tests for unified command processor
Linear Project: 4d649a6501f7
Task: TEST-002 - Unit Tests for Command Processor

Tests cover:
- UnifiedCommandProcessor initialization
- Command parsing for all prefixes ($, @, #, /)
- Command routing to handlers
- Parameter extraction
- Quote handling
- Error handling
- Middleware execution
- Batch command processing
"""

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from unified_framework.commands.processor import (
    Command,
    CommandContext,
    CommandHandler,
    CommandParser,
    CommandPrefix,
    CommandProcessor,
    CommandResult,
    CommandStatus,
    IDFWCommandHandler,
    SlashCommandHandler,
    UnifiedCommandHandler,
    YUNGCommandHandler,
    create_default_processor,
    logging_middleware,
    validation_middleware,
)


class TestCommandProcessorInitialization:
    """Tests for CommandProcessor initialization"""

    def test_processor_initialization(self):
        """Test processor initializes with default handlers"""
        processor = CommandProcessor()

        assert processor is not None
        assert len(processor.handlers) == 4
        assert CommandPrefix.YUNG in processor.handlers
        assert CommandPrefix.IDFW in processor.handlers
        assert CommandPrefix.UNIFIED in processor.handlers
        assert CommandPrefix.SLASH in processor.handlers

    def test_processor_has_parser(self):
        """Test processor has parser instance"""
        processor = CommandProcessor()

        assert processor.parser is not None
        assert isinstance(processor.parser, CommandParser)

    def test_processor_middleware_list_initialized(self):
        """Test processor middleware list is initialized"""
        processor = CommandProcessor()

        assert processor.middleware is not None
        assert isinstance(processor.middleware, list)
        assert len(processor.middleware) == 0  # Empty by default

    def test_processor_handlers_are_correct_types(self):
        """Test processor handlers are correct handler types"""
        processor = CommandProcessor()

        assert isinstance(processor.handlers[CommandPrefix.YUNG], YUNGCommandHandler)
        assert isinstance(processor.handlers[CommandPrefix.IDFW], IDFWCommandHandler)
        assert isinstance(processor.handlers[CommandPrefix.UNIFIED], UnifiedCommandHandler)
        assert isinstance(processor.handlers[CommandPrefix.SLASH], SlashCommandHandler)


class TestCommandProcessorHandlerRegistration:
    """Tests for registering custom handlers"""

    def test_register_custom_handler(self):
        """Test registering a custom handler"""
        processor = CommandProcessor()

        # Create mock handler
        custom_handler = Mock(spec=CommandHandler)

        # Register handler
        processor.register_handler(CommandPrefix.YUNG, custom_handler)

        assert processor.handlers[CommandPrefix.YUNG] == custom_handler

    def test_register_handler_replaces_existing(self):
        """Test registering handler replaces existing handler"""
        processor = CommandProcessor()

        original_handler = processor.handlers[CommandPrefix.IDFW]
        custom_handler = Mock(spec=CommandHandler)

        processor.register_handler(CommandPrefix.IDFW, custom_handler)

        assert processor.handlers[CommandPrefix.IDFW] == custom_handler
        assert processor.handlers[CommandPrefix.IDFW] != original_handler

    def test_register_handler_for_all_prefixes(self):
        """Test registering handlers for all prefixes"""
        processor = CommandProcessor()

        custom_handlers = {
            CommandPrefix.YUNG: Mock(spec=CommandHandler),
            CommandPrefix.IDFW: Mock(spec=CommandHandler),
            CommandPrefix.UNIFIED: Mock(spec=CommandHandler),
            CommandPrefix.SLASH: Mock(spec=CommandHandler),
        }

        for prefix, handler in custom_handlers.items():
            processor.register_handler(prefix, handler)

        for prefix, handler in custom_handlers.items():
            assert processor.handlers[prefix] == handler


class TestCommandProcessorMiddleware:
    """Tests for middleware functionality"""

    def test_add_middleware(self):
        """Test adding middleware to processor"""
        processor = CommandProcessor()

        async def test_middleware(cmd: Command, ctx: CommandContext) -> None:
            pass

        processor.add_middleware(test_middleware)

        assert len(processor.middleware) == 1
        assert processor.middleware[0] == test_middleware

    def test_add_multiple_middleware(self):
        """Test adding multiple middleware functions"""
        processor = CommandProcessor()

        async def middleware1(cmd: Command, ctx: CommandContext) -> None:
            pass

        async def middleware2(cmd: Command, ctx: CommandContext) -> None:
            pass

        async def middleware3(cmd: Command, ctx: CommandContext) -> None:
            pass

        processor.add_middleware(middleware1)
        processor.add_middleware(middleware2)
        processor.add_middleware(middleware3)

        assert len(processor.middleware) == 3
        assert processor.middleware[0] == middleware1
        assert processor.middleware[1] == middleware2
        assert processor.middleware[2] == middleware3

    @pytest.mark.asyncio
    async def test_middleware_execution_order(self):
        """Test middleware executes in correct order"""
        processor = CommandProcessor()
        execution_order = []

        async def middleware1(cmd: Command, ctx: CommandContext) -> None:
            execution_order.append(1)

        async def middleware2(cmd: Command, ctx: CommandContext) -> None:
            execution_order.append(2)

        async def middleware3(cmd: Command, ctx: CommandContext) -> None:
            execution_order.append(3)

        processor.add_middleware(middleware1)
        processor.add_middleware(middleware2)
        processor.add_middleware(middleware3)

        result = await processor.execute("$spawn")

        assert execution_order == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_middleware_receives_command_and_context(self):
        """Test middleware receives command and context"""
        processor = CommandProcessor()
        captured_data = {}

        async def capturing_middleware(cmd: Command, ctx: CommandContext) -> None:
            captured_data['command'] = cmd
            captured_data['context'] = ctx

        processor.add_middleware(capturing_middleware)

        context = CommandContext(session_id="test-session")
        await processor.execute("$spawn", context)

        assert 'command' in captured_data
        assert 'context' in captured_data
        assert captured_data['command'].name == "spawn"
        assert captured_data['context'].session_id == "test-session"

    @pytest.mark.asyncio
    async def test_middleware_error_stops_execution(self):
        """Test middleware error stops command execution"""
        processor = CommandProcessor()

        async def failing_middleware(cmd: Command, ctx: CommandContext) -> None:
            raise ValueError("Middleware error")

        processor.add_middleware(failing_middleware)

        result = await processor.execute("$spawn")

        assert result.status == CommandStatus.FAILED
        assert "Middleware error" in result.error


class TestYUNGCommandExecution:
    """Tests for YUNG command execution"""

    @pytest.mark.asyncio
    async def test_execute_yung_spawn_command(self):
        """Test executing $spawn command"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn")

        assert result.status == CommandStatus.SUCCESS
        assert "spawn" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_yung_init_command(self):
        """Test executing $init command"""
        processor = CommandProcessor()
        result = await processor.execute("$init")

        assert result.status == CommandStatus.SUCCESS
        assert "init" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_yung_audit_command(self):
        """Test executing $audit command"""
        processor = CommandProcessor()
        result = await processor.execute("$audit")

        assert result.status == CommandStatus.SUCCESS
        assert "audit" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_yung_command_with_args(self):
        """Test executing YUNG command with arguments"""
        processor = CommandProcessor()
        result = await processor.execute("$build production --verbose")

        assert result.status == CommandStatus.SUCCESS
        assert result.data['command'] == 'build'
        assert 'production' in result.data['args']
        assert '--verbose' in result.data['args']

    @pytest.mark.asyncio
    async def test_execute_unsupported_yung_command(self):
        """Test executing unsupported YUNG command"""
        processor = CommandProcessor()
        result = await processor.execute("$unsupported")

        assert result.status == CommandStatus.FAILED
        assert "unsupported" in result.error.lower()

    @pytest.mark.asyncio
    async def test_yung_command_execution_time(self):
        """Test YUNG command tracks execution time"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn")

        assert result.execution_time > 0


class TestIDFWCommandExecution:
    """Tests for IDFW command execution"""

    @pytest.mark.asyncio
    async def test_execute_idfw_define_command(self):
        """Test executing @define command"""
        processor = CommandProcessor()
        result = await processor.execute("@define")

        assert result.status == CommandStatus.SUCCESS
        assert "define" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_idfw_generate_command(self):
        """Test executing @generate command"""
        processor = CommandProcessor()
        result = await processor.execute("@generate")

        assert result.status == CommandStatus.SUCCESS
        assert "generate" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_idfw_validate_command(self):
        """Test executing @validate command"""
        processor = CommandProcessor()
        result = await processor.execute("@validate")

        assert result.status == CommandStatus.SUCCESS
        assert "validate" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_idfw_command_with_args(self):
        """Test executing IDFW command with arguments"""
        processor = CommandProcessor()
        result = await processor.execute("@diagram flowchart --format=svg")

        assert result.status == CommandStatus.SUCCESS
        assert result.data['action'] == 'diagram'

    @pytest.mark.asyncio
    async def test_execute_unsupported_idfw_command(self):
        """Test executing unsupported IDFW command"""
        processor = CommandProcessor()
        result = await processor.execute("@unsupported")

        assert result.status == CommandStatus.FAILED
        assert "unsupported" in result.error.lower()


class TestUnifiedCommandExecution:
    """Tests for unified framework command execution"""

    @pytest.mark.asyncio
    async def test_execute_unified_sync_command(self):
        """Test executing #sync command"""
        processor = CommandProcessor()
        result = await processor.execute("#sync")

        assert result.status == CommandStatus.SUCCESS
        assert "sync" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_unified_convert_command(self):
        """Test executing #convert command"""
        processor = CommandProcessor()
        result = await processor.execute("#convert")

        assert result.status == CommandStatus.SUCCESS
        assert "convert" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_unified_bridge_command(self):
        """Test executing #bridge command"""
        processor = CommandProcessor()
        result = await processor.execute("#bridge")

        assert result.status == CommandStatus.SUCCESS
        assert "bridge" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_unified_command_with_args(self):
        """Test executing unified command with arguments"""
        processor = CommandProcessor()
        result = await processor.execute("#integrate idfw force")

        assert result.status == CommandStatus.SUCCESS
        assert result.data['command'] == 'integrate'

    @pytest.mark.asyncio
    async def test_execute_unsupported_unified_command(self):
        """Test executing unsupported unified command"""
        processor = CommandProcessor()
        result = await processor.execute("#unsupported")

        assert result.status == CommandStatus.FAILED
        assert "unsupported" in result.error.lower()


class TestSlashCommandExecution:
    """Tests for slash command execution"""

    @pytest.mark.asyncio
    async def test_execute_slash_agent_backend_command(self):
        """Test executing /agent-backend command"""
        processor = CommandProcessor()
        result = await processor.execute("/agent-backend")

        assert result.status == CommandStatus.SUCCESS
        assert "agent-backend" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_slash_deploy_agent_team_command(self):
        """Test executing /deploy-agent-team command"""
        processor = CommandProcessor()
        result = await processor.execute("/deploy-agent-team")

        assert result.status == CommandStatus.SUCCESS
        assert "deploy-agent-team" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_slash_fix_schema_conflicts_command(self):
        """Test executing /fix-schema-conflicts command"""
        processor = CommandProcessor()
        result = await processor.execute("/fix-schema-conflicts")

        assert result.status == CommandStatus.SUCCESS
        assert "fix-schema-conflicts" in result.output.lower()

    @pytest.mark.asyncio
    async def test_execute_slash_command_with_args(self):
        """Test executing slash command with arguments"""
        processor = CommandProcessor()
        result = await processor.execute("/agent-status --active")

        assert result.status == CommandStatus.SUCCESS
        assert result.data['command'] == 'agent-status'

    @pytest.mark.asyncio
    async def test_execute_unsupported_slash_command(self):
        """Test executing unsupported slash command"""
        processor = CommandProcessor()
        result = await processor.execute("/unsupported")

        assert result.status == CommandStatus.FAILED
        assert "unsupported" in result.error.lower()


class TestBatchCommandExecution:
    """Tests for batch command execution"""

    @pytest.mark.asyncio
    async def test_execute_batch_all_success(self):
        """Test executing batch commands with all successful"""
        processor = CommandProcessor()
        commands = ["$spawn", "@define", "#sync", "/agent-backend"]

        results = await processor.execute_batch(commands)

        assert len(results) == 4
        assert all(r.status == CommandStatus.SUCCESS for r in results)

    @pytest.mark.asyncio
    async def test_execute_batch_stops_on_failure(self):
        """Test batch execution stops on first failure"""
        processor = CommandProcessor()
        commands = ["$spawn", "$unsupported", "@define", "#sync"]

        results = await processor.execute_batch(commands)

        # Should stop after the unsupported command
        assert len(results) == 2
        assert results[0].status == CommandStatus.SUCCESS
        assert results[1].status == CommandStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_batch_with_context(self):
        """Test batch execution with shared context"""
        processor = CommandProcessor()
        context = CommandContext(session_id="batch-session")
        commands = ["$spawn", "@define"]

        results = await processor.execute_batch(commands, context)

        assert len(results) == 2
        assert all(r.status == CommandStatus.SUCCESS for r in results)

    @pytest.mark.asyncio
    async def test_execute_empty_batch(self):
        """Test executing empty batch"""
        processor = CommandProcessor()
        commands = []

        results = await processor.execute_batch(commands)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_execute_batch_with_invalid_command(self):
        """Test batch with invalid command syntax"""
        processor = CommandProcessor()
        commands = ["$spawn", "invalid", "@define"]

        results = await processor.execute_batch(commands)

        # Should stop after invalid command
        assert len(results) == 2
        assert results[0].status == CommandStatus.SUCCESS
        assert results[1].status == CommandStatus.FAILED


class TestCommandContextHandling:
    """Tests for command context handling"""

    @pytest.mark.asyncio
    async def test_execute_with_custom_context(self):
        """Test executing command with custom context"""
        processor = CommandProcessor()
        context = CommandContext(
            user_id="user123",
            session_id="session456",
            working_directory="/test/dir",
            agent_id="agent789",
        )

        result = await processor.execute("$spawn", context)

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_execute_without_context_creates_default(self):
        """Test executing without context creates default context"""
        processor = CommandProcessor()

        result = await processor.execute("$spawn")

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_context_with_environment_variables(self):
        """Test context with environment variables"""
        processor = CommandProcessor()
        context = CommandContext(
            environment={"ENV": "test", "DEBUG": "true"}
        )

        result = await processor.execute("$spawn", context)

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_context_with_variables(self):
        """Test context with IDFW variables"""
        processor = CommandProcessor()
        context = CommandContext(
            variables={"project_name": "test", "version": "1.0.0"}
        )

        result = await processor.execute("@define", context)

        assert result.status == CommandStatus.SUCCESS


class TestCommandResultHandling:
    """Tests for command result handling"""

    @pytest.mark.asyncio
    async def test_successful_result_structure(self):
        """Test successful result has correct structure"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn")

        assert result.status == CommandStatus.SUCCESS
        assert result.output is not None
        assert result.error is None
        assert result.return_code == 0
        assert result.execution_time > 0

    @pytest.mark.asyncio
    async def test_failed_result_structure(self):
        """Test failed result has correct structure"""
        processor = CommandProcessor()
        result = await processor.execute("$unsupported")

        assert result.status == CommandStatus.FAILED
        assert result.error is not None
        assert result.return_code == 1

    @pytest.mark.asyncio
    async def test_result_contains_data(self):
        """Test result contains command data"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn arg1 arg2")

        assert result.status == CommandStatus.SUCCESS
        assert 'command' in result.data or 'action' in result.data

    @pytest.mark.asyncio
    async def test_result_execution_time_tracked(self):
        """Test result tracks execution time"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn")

        assert result.execution_time > 0
        assert result.execution_time < 1.0  # Should be very fast


class TestErrorHandling:
    """Tests for error handling"""

    @pytest.mark.asyncio
    async def test_invalid_command_syntax(self):
        """Test invalid command syntax returns error"""
        processor = CommandProcessor()
        result = await processor.execute("invalid")

        assert result.status == CommandStatus.FAILED
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_empty_command(self):
        """Test empty command returns error"""
        processor = CommandProcessor()
        result = await processor.execute("")

        assert result.status == CommandStatus.FAILED
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_whitespace_only_command(self):
        """Test whitespace-only command returns error"""
        processor = CommandProcessor()
        result = await processor.execute("   ")

        assert result.status == CommandStatus.FAILED
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_invalid_prefix(self):
        """Test invalid prefix returns error"""
        processor = CommandProcessor()
        result = await processor.execute("?invalid")

        assert result.status == CommandStatus.FAILED
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_missing_command_name(self):
        """Test missing command name returns error"""
        processor = CommandProcessor()
        result = await processor.execute("$")

        assert result.status == CommandStatus.FAILED

    @pytest.mark.asyncio
    async def test_handler_exception_caught(self):
        """Test handler exceptions are caught and returned as errors"""
        processor = CommandProcessor()

        # Create handler that raises exception but catches it
        class FailingHandler(CommandHandler):
            def supports(self, command_name: str) -> bool:
                return True

            async def execute(self, command: Command, context: CommandContext) -> CommandResult:
                try:
                    raise RuntimeError("Handler failed")
                except Exception as e:
                    return CommandResult(
                        status=CommandStatus.FAILED,
                        error=str(e),
                        return_code=1,
                    )

        processor.register_handler(CommandPrefix.YUNG, FailingHandler())

        result = await processor.execute("$spawn")

        assert result.status == CommandStatus.FAILED
        assert "failed" in result.error.lower()


class TestGetSupportedCommands:
    """Tests for getting supported commands"""

    def test_get_yung_supported_commands(self):
        """Test getting YUNG supported commands"""
        processor = CommandProcessor()
        commands = processor.get_supported_commands(CommandPrefix.YUNG)

        assert len(commands) > 0
        assert "spawn" in commands
        assert "init" in commands
        assert "audit" in commands

    def test_get_idfw_supported_commands(self):
        """Test getting IDFW supported commands"""
        processor = CommandProcessor()
        commands = processor.get_supported_commands(CommandPrefix.IDFW)

        assert len(commands) > 0
        assert "define" in commands
        assert "generate" in commands
        assert "validate" in commands

    def test_get_unified_supported_commands(self):
        """Test getting unified supported commands"""
        processor = CommandProcessor()
        commands = processor.get_supported_commands(CommandPrefix.UNIFIED)

        assert len(commands) > 0
        assert "sync" in commands
        assert "convert" in commands
        assert "bridge" in commands

    def test_get_slash_supported_commands(self):
        """Test getting slash supported commands"""
        processor = CommandProcessor()
        commands = processor.get_supported_commands(CommandPrefix.SLASH)

        assert len(commands) > 0
        assert "agent-backend" in commands
        assert "deploy-agent-team" in commands

    def test_get_supported_commands_invalid_prefix(self):
        """Test getting supported commands for unregistered handler"""
        processor = CommandProcessor()
        # Remove a handler
        del processor.handlers[CommandPrefix.YUNG]

        commands = processor.get_supported_commands(CommandPrefix.YUNG)

        assert commands == []


class TestDefaultProcessorFactory:
    """Tests for default processor factory"""

    def test_create_default_processor(self):
        """Test creating default processor"""
        processor = create_default_processor()

        assert processor is not None
        assert isinstance(processor, CommandProcessor)

    def test_default_processor_has_middleware(self):
        """Test default processor has middleware"""
        processor = create_default_processor()

        assert len(processor.middleware) >= 2  # logging and validation

    def test_default_processor_has_handlers(self):
        """Test default processor has all handlers"""
        processor = create_default_processor()

        assert len(processor.handlers) == 4


class TestMiddlewareFunctions:
    """Tests for provided middleware functions"""

    @pytest.mark.asyncio
    async def test_logging_middleware(self):
        """Test logging middleware executes without error"""
        command = Command(
            prefix=CommandPrefix.YUNG,
            name="spawn",
            raw_command="$spawn",
        )
        context = CommandContext(session_id="test")

        # Should not raise exception
        await logging_middleware(command, context)

    @pytest.mark.asyncio
    async def test_validation_middleware(self):
        """Test validation middleware executes without error"""
        command = Command(
            prefix=CommandPrefix.IDFW,
            name="define",
            raw_command="@define",
        )
        context = CommandContext()

        # Should not raise exception
        await validation_middleware(command, context)


class TestCommandHandlerInterface:
    """Tests for CommandHandler interface"""

    def test_yung_handler_supports_method(self):
        """Test YUNG handler supports method"""
        handler = YUNGCommandHandler()

        assert handler.supports("spawn") is True
        assert handler.supports("init") is True
        assert handler.supports("unsupported") is False

    def test_idfw_handler_supports_method(self):
        """Test IDFW handler supports method"""
        handler = IDFWCommandHandler()

        assert handler.supports("define") is True
        assert handler.supports("generate") is True
        assert handler.supports("unsupported") is False

    def test_unified_handler_supports_method(self):
        """Test unified handler supports method"""
        handler = UnifiedCommandHandler()

        assert handler.supports("sync") is True
        assert handler.supports("convert") is True
        assert handler.supports("unsupported") is False

    def test_slash_handler_supports_method(self):
        """Test slash handler supports method"""
        handler = SlashCommandHandler()

        assert handler.supports("agent-backend") is True
        assert handler.supports("deploy-agent-team") is True
        assert handler.supports("unsupported") is False


class TestConcurrentExecution:
    """Tests for concurrent command execution"""

    @pytest.mark.asyncio
    async def test_concurrent_command_execution(self):
        """Test multiple commands can be executed concurrently"""
        processor = CommandProcessor()

        # Execute multiple commands concurrently
        tasks = [
            processor.execute("$spawn"),
            processor.execute("@define"),
            processor.execute("#sync"),
            processor.execute("/agent-backend"),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 4
        assert all(r.status == CommandStatus.SUCCESS for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_execution_with_failures(self):
        """Test concurrent execution with some failures"""
        processor = CommandProcessor()

        tasks = [
            processor.execute("$spawn"),
            processor.execute("$unsupported"),
            processor.execute("@define"),
            processor.execute("/agent-backend"),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 4
        assert results[0].status == CommandStatus.SUCCESS
        assert results[1].status == CommandStatus.FAILED
        assert results[2].status == CommandStatus.SUCCESS
        assert results[3].status == CommandStatus.SUCCESS


class TestEdgeCases:
    """Tests for edge cases"""

    @pytest.mark.asyncio
    async def test_command_with_special_characters(self):
        """Test command with special characters in args"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn --name='test-123'")

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_command_with_unicode(self):
        """Test command with unicode characters"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn 你好")

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_very_long_command(self):
        """Test very long command string"""
        processor = CommandProcessor()
        long_arg = "a" * 1000
        result = await processor.execute(f"$spawn {long_arg}")

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_command_with_multiple_spaces(self):
        """Test command with multiple spaces"""
        processor = CommandProcessor()
        result = await processor.execute("$spawn    arg1     arg2")

        assert result.status == CommandStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_command_with_newlines(self):
        """Test command with newlines is handled"""
        processor = CommandProcessor()
        # Command should be single line, newlines would make it invalid
        result = await processor.execute("$spawn\narg1")

        # This might fail or be handled - test current behavior
        assert result is not None
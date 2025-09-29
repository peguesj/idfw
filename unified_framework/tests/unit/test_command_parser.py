"""
Unit tests for command parser
Linear Project: 4d649a6501f7
Task: TEST-002 - Unit Tests for Command Processor

Tests cover:
- CommandParser for all command types
- YUNG command parsing ($)
- IDFW action parsing (@)
- Unified command parsing (#)
- Slash command parsing (/)
- Edge cases and malformed commands
- Quote handling
- Parameter extraction
"""

import pytest

from unified_framework.commands.processor import (
    Command,
    CommandParser,
    CommandPrefix,
)


class TestBasicCommandParsing:
    """Tests for basic command parsing"""

    def test_parse_yung_command(self):
        """Test parsing YUNG command"""
        parser = CommandParser()
        command = parser.parse("$spawn")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"
        assert command.raw_command == "$spawn"

    def test_parse_idfw_command(self):
        """Test parsing IDFW command"""
        parser = CommandParser()
        command = parser.parse("@define")

        assert command is not None
        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "define"
        assert command.raw_command == "@define"

    def test_parse_unified_command(self):
        """Test parsing unified command"""
        parser = CommandParser()
        command = parser.parse("#sync")

        assert command is not None
        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "sync"
        assert command.raw_command == "#sync"

    def test_parse_slash_command(self):
        """Test parsing slash command"""
        parser = CommandParser()
        command = parser.parse("/agent-backend")

        assert command is not None
        assert command.prefix == CommandPrefix.SLASH
        assert command.name == "agent-backend"
        assert command.raw_command == "/agent-backend"


class TestYUNGCommandParsing:
    """Tests for YUNG command parsing"""

    def test_parse_yung_spawn_command(self):
        """Test parsing $spawn command"""
        parser = CommandParser()
        command = parser.parse("$spawn")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"
        assert len(command.args) == 0
        assert len(command.kwargs) == 0

    def test_parse_yung_init_command(self):
        """Test parsing $init command"""
        parser = CommandParser()
        command = parser.parse("$init")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "init"

    def test_parse_yung_command_with_args(self):
        """Test parsing YUNG command with positional arguments"""
        parser = CommandParser()
        command = parser.parse("$build production staging")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "build"
        assert len(command.args) == 2
        assert "production" in command.args
        assert "staging" in command.args

    def test_parse_yung_command_with_kwargs(self):
        """Test parsing YUNG command with key-value arguments"""
        parser = CommandParser()
        command = parser.parse("$deploy env=production verbose=true")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "deploy"
        assert len(command.kwargs) == 2
        assert command.kwargs["env"] == "production"
        assert command.kwargs["verbose"] == "true"

    def test_parse_yung_command_mixed_args(self):
        """Test parsing YUNG command with mixed args and kwargs"""
        parser = CommandParser()
        command = parser.parse("$test unit env=test --verbose")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "test"
        assert "unit" in command.args
        assert "--verbose" in command.args
        assert command.kwargs["env"] == "test"

    def test_parse_yung_command_with_flags(self):
        """Test parsing YUNG command with flags"""
        parser = CommandParser()
        command = parser.parse("$audit --strict --verbose --quiet")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "audit"
        assert "--strict" in command.args
        assert "--verbose" in command.args
        assert "--quiet" in command.args


class TestIDFWCommandParsing:
    """Tests for IDFW command parsing"""

    def test_parse_idfw_define_command(self):
        """Test parsing @define command"""
        parser = CommandParser()
        command = parser.parse("@define")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "define"
        assert len(command.args) == 0

    def test_parse_idfw_generate_command(self):
        """Test parsing @generate command"""
        parser = CommandParser()
        command = parser.parse("@generate")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "generate"

    def test_parse_idfw_command_with_args(self):
        """Test parsing IDFW command with arguments"""
        parser = CommandParser()
        command = parser.parse("@diagram flowchart sequence")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "diagram"
        assert "flowchart" in command.args
        assert "sequence" in command.args

    def test_parse_idfw_command_with_kwargs(self):
        """Test parsing IDFW command with key-value arguments"""
        parser = CommandParser()
        command = parser.parse("@export format=json output=file.json")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "export"
        assert command.kwargs["format"] == "json"
        assert command.kwargs["output"] == "file.json"

    def test_parse_idfw_command_with_path(self):
        """Test parsing IDFW command with file path"""
        parser = CommandParser()
        command = parser.parse("@validate /path/to/document.idfw")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "validate"
        assert "/path/to/document.idfw" in command.args


class TestUnifiedCommandParsing:
    """Tests for unified command parsing"""

    def test_parse_unified_sync_command(self):
        """Test parsing #sync command"""
        parser = CommandParser()
        command = parser.parse("#sync")

        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "sync"

    def test_parse_unified_convert_command(self):
        """Test parsing #convert command"""
        parser = CommandParser()
        command = parser.parse("#convert")

        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "convert"

    def test_parse_unified_command_with_args(self):
        """Test parsing unified command with arguments"""
        parser = CommandParser()
        command = parser.parse("#integrate idfw force")

        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "integrate"
        assert "idfw" in command.args
        assert "force" in command.args

    def test_parse_unified_command_with_kwargs(self):
        """Test parsing unified command with key-value arguments"""
        parser = CommandParser()
        command = parser.parse("#workflow run=pipeline stage=test")

        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "workflow"
        assert command.kwargs["run"] == "pipeline"
        assert command.kwargs["stage"] == "test"

    def test_parse_unified_bridge_command(self):
        """Test parsing #bridge command"""
        parser = CommandParser()
        command = parser.parse("#bridge idfw force --bidirectional")

        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "bridge"
        assert "idfw" in command.args
        assert "force" in command.args
        assert "--bidirectional" in command.args


class TestSlashCommandParsing:
    """Tests for slash command parsing"""

    def test_parse_slash_agent_backend_command(self):
        """Test parsing /agent-backend command"""
        parser = CommandParser()
        command = parser.parse("/agent-backend")

        assert command.prefix == CommandPrefix.SLASH
        assert command.name == "agent-backend"

    def test_parse_slash_deploy_agent_team_command(self):
        """Test parsing /deploy-agent-team command"""
        parser = CommandParser()
        command = parser.parse("/deploy-agent-team")

        assert command.prefix == CommandPrefix.SLASH
        assert command.name == "deploy-agent-team"

    def test_parse_slash_command_with_args(self):
        """Test parsing slash command with arguments"""
        parser = CommandParser()
        command = parser.parse("/agent-status active idle")

        assert command.prefix == CommandPrefix.SLASH
        assert command.name == "agent-status"
        assert "active" in command.args
        assert "idle" in command.args

    def test_parse_slash_command_with_options(self):
        """Test parsing slash command with options"""
        parser = CommandParser()
        command = parser.parse("/deploy-agent-team department=development --force")

        assert command.prefix == CommandPrefix.SLASH
        assert command.name == "deploy-agent-team"
        assert command.kwargs["department"] == "development"
        assert "--force" in command.args

    def test_parse_slash_fix_schema_conflicts(self):
        """Test parsing /fix-schema-conflicts command"""
        parser = CommandParser()
        command = parser.parse("/fix-schema-conflicts")

        assert command.prefix == CommandPrefix.SLASH
        assert command.name == "fix-schema-conflicts"


class TestQuoteHandling:
    """Tests for quote handling in commands"""

    def test_parse_command_with_single_quotes(self):
        """Test parsing command with single quotes"""
        parser = CommandParser()
        command = parser.parse("$spawn --name='my project'")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"
        # shlex should handle quotes properly
        assert any("my project" in arg for arg in command.args or command.kwargs.values())

    def test_parse_command_with_double_quotes(self):
        """Test parsing command with double quotes"""
        parser = CommandParser()
        command = parser.parse('$build --message="Build complete"')

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "build"
        # Check if quotes are handled
        assert any("Build complete" in str(v) for v in command.kwargs.values())

    def test_parse_command_with_quotes_in_value(self):
        """Test parsing command with quotes in key-value pair"""
        parser = CommandParser()
        command = parser.parse('@export output="test file.json"')

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "export"
        assert "output" in command.kwargs
        assert "test file.json" in command.kwargs["output"]

    def test_parse_command_with_escaped_quotes(self):
        """Test parsing command with escaped quotes"""
        parser = CommandParser()
        command = parser.parse(r'$test --pattern="test\"case"')

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "test"

    def test_parse_command_with_nested_quotes(self):
        """Test parsing command with nested quotes"""
        parser = CommandParser()
        command = parser.parse("""$spawn --config='{"key": "value"}'""")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"


class TestParameterExtraction:
    """Tests for parameter extraction"""

    def test_parse_positional_parameters(self):
        """Test parsing positional parameters"""
        parser = CommandParser()
        command = parser.parse("$deploy prod us-east-1 v1.2.3")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "deploy"
        assert len(command.args) == 3
        assert command.args[0] == "prod"
        assert command.args[1] == "us-east-1"
        assert command.args[2] == "v1.2.3"

    def test_parse_keyword_parameters(self):
        """Test parsing keyword parameters"""
        parser = CommandParser()
        command = parser.parse("@generate type=document format=markdown version=2.0")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "generate"
        assert len(command.kwargs) == 3
        assert command.kwargs["type"] == "document"
        assert command.kwargs["format"] == "markdown"
        assert command.kwargs["version"] == "2.0"

    def test_parse_mixed_parameters(self):
        """Test parsing mixed positional and keyword parameters"""
        parser = CommandParser()
        command = parser.parse("#integrate idfw force mode=bidirectional --verbose")

        assert command.prefix == CommandPrefix.UNIFIED
        assert command.name == "integrate"
        assert "idfw" in command.args
        assert "force" in command.args
        assert "--verbose" in command.args
        assert command.kwargs["mode"] == "bidirectional"

    def test_parse_parameter_with_equals_in_value(self):
        """Test parsing parameter with equals sign in value"""
        parser = CommandParser()
        command = parser.parse("$config key=value=with=equals")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "config"
        # Should split on first = only
        assert command.kwargs["key"] == "value=with=equals"

    def test_parse_parameter_with_special_characters(self):
        """Test parsing parameter with special characters"""
        parser = CommandParser()
        command = parser.parse("@validate pattern=^[a-zA-Z0-9_-]+$")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "validate"
        assert "pattern" in command.kwargs

    def test_parse_boolean_parameters(self):
        """Test parsing boolean-like parameters"""
        parser = CommandParser()
        command = parser.parse("$test verbose=true debug=false")

        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "test"
        assert command.kwargs["verbose"] == "true"
        assert command.kwargs["debug"] == "false"

    def test_parse_numeric_parameters(self):
        """Test parsing numeric parameters"""
        parser = CommandParser()
        command = parser.parse("@generate count=100 timeout=30.5")

        assert command.prefix == CommandPrefix.IDFW
        assert command.name == "generate"
        assert command.kwargs["count"] == "100"
        assert command.kwargs["timeout"] == "30.5"


class TestEdgeCases:
    """Tests for edge cases and malformed commands"""

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        parser = CommandParser()
        command = parser.parse("")

        assert command is None

    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only string"""
        parser = CommandParser()
        command = parser.parse("   ")

        assert command is None

    def test_parse_prefix_only(self):
        """Test parsing prefix without command"""
        parser = CommandParser()
        command = parser.parse("$")

        assert command is None

    def test_parse_prefix_with_whitespace(self):
        """Test parsing prefix with only whitespace after"""
        parser = CommandParser()
        command = parser.parse("$   ")

        assert command is None

    def test_parse_invalid_prefix(self):
        """Test parsing command with invalid prefix"""
        parser = CommandParser()
        command = parser.parse("?invalid")

        assert command is None

    def test_parse_no_prefix(self):
        """Test parsing command without prefix"""
        parser = CommandParser()
        command = parser.parse("command")

        assert command is None

    def test_parse_multiple_prefixes(self):
        """Test parsing command with multiple prefixes"""
        parser = CommandParser()
        command = parser.parse("$$spawn")

        # First $ is the prefix, second $ becomes part of command name
        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "$spawn"

    def test_parse_command_with_leading_whitespace(self):
        """Test parsing command with leading whitespace"""
        parser = CommandParser()
        command = parser.parse("   $spawn")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"

    def test_parse_command_with_trailing_whitespace(self):
        """Test parsing command with trailing whitespace"""
        parser = CommandParser()
        command = parser.parse("$spawn   ")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"

    def test_parse_command_with_tabs(self):
        """Test parsing command with tabs"""
        parser = CommandParser()
        command = parser.parse("$spawn\targ1\targ2")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"

    def test_parse_unclosed_quotes(self):
        """Test parsing command with unclosed quotes"""
        parser = CommandParser()
        command = parser.parse('$spawn --name="unclosed')

        # shlex should fail to parse unclosed quotes
        assert command is None

    def test_parse_empty_quotes(self):
        """Test parsing command with empty quotes"""
        parser = CommandParser()
        command = parser.parse('$spawn --name=""')

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"

    def test_parse_command_with_unicode(self):
        """Test parsing command with unicode characters"""
        parser = CommandParser()
        command = parser.parse("$spawn 你好 мир")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"
        assert "你好" in command.args
        assert "мир" in command.args

    def test_parse_very_long_command(self):
        """Test parsing very long command"""
        parser = CommandParser()
        long_arg = "a" * 10000
        command = parser.parse(f"$spawn {long_arg}")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "spawn"
        assert long_arg in command.args


class TestCommandNameValidation:
    """Tests for command name validation"""

    def test_parse_command_with_hyphen(self):
        """Test parsing command with hyphen in name"""
        parser = CommandParser()
        command = parser.parse("/agent-backend")

        assert command is not None
        assert command.name == "agent-backend"

    def test_parse_command_with_underscore(self):
        """Test parsing command with underscore in name"""
        parser = CommandParser()
        command = parser.parse("$init_project")

        assert command is not None
        assert command.name == "init_project"

    def test_parse_command_with_numbers(self):
        """Test parsing command with numbers in name"""
        parser = CommandParser()
        command = parser.parse("@validate2")

        assert command is not None
        assert command.name == "validate2"

    def test_parse_command_with_dots(self):
        """Test parsing command with dots in name"""
        parser = CommandParser()
        command = parser.parse("#sync.state")

        assert command is not None
        assert command.name == "sync.state"


class TestRawCommandPreservation:
    """Tests for raw command preservation"""

    def test_raw_command_preserved(self):
        """Test raw command string is preserved"""
        parser = CommandParser()
        raw = "$spawn arg1 arg2"
        command = parser.parse(raw)

        assert command is not None
        assert command.raw_command == raw

    def test_raw_command_with_quotes_preserved(self):
        """Test raw command with quotes is preserved"""
        parser = CommandParser()
        raw = '$deploy --message="Test message"'
        command = parser.parse(raw)

        assert command is not None
        assert command.raw_command == raw

    def test_raw_command_with_whitespace_preserved(self):
        """Test raw command with whitespace is preserved"""
        parser = CommandParser()
        raw = "$build    production    --verbose"
        command = parser.parse(raw)

        assert command is not None
        # Raw command should be trimmed but original spacing may not be preserved
        assert command.raw_command.strip() == raw.strip()


class TestComplexCommandScenarios:
    """Tests for complex command scenarios"""

    def test_parse_command_with_url(self):
        """Test parsing command with URL argument"""
        parser = CommandParser()
        command = parser.parse("@export url=https://example.com/api")

        assert command is not None
        assert command.kwargs["url"] == "https://example.com/api"

    def test_parse_command_with_file_path(self):
        """Test parsing command with file path"""
        parser = CommandParser()
        command = parser.parse("@validate /home/user/documents/test.idfw")

        assert command is not None
        assert "/home/user/documents/test.idfw" in command.args

    def test_parse_command_with_json_string(self):
        """Test parsing command with JSON string"""
        parser = CommandParser()
        command = parser.parse("""$config data='{"key": "value", "number": 42}'""")

        assert command is not None
        assert command.prefix == CommandPrefix.YUNG
        assert command.name == "config"

    def test_parse_command_with_multiple_flags(self):
        """Test parsing command with multiple flags"""
        parser = CommandParser()
        command = parser.parse("$test --verbose --debug --quiet --strict")

        assert command is not None
        assert "--verbose" in command.args
        assert "--debug" in command.args
        assert "--quiet" in command.args
        assert "--strict" in command.args

    def test_parse_command_with_environment_variable_syntax(self):
        """Test parsing command with environment variable syntax"""
        parser = CommandParser()
        command = parser.parse("$deploy env=$ENVIRONMENT region=$AWS_REGION")

        assert command is not None
        assert command.kwargs["env"] == "$ENVIRONMENT"
        assert command.kwargs["region"] == "$AWS_REGION"
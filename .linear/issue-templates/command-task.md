# Command Task Template

**Template ID**: `command-task`
**Category**: Development - Command System
**Default Assignee**: BackendDeveloperAgent (BDA)
**Default Project**: IDFWU - IDEA Framework Unified (`4d649a6501f7`)
**Default Priority**: High

---

## Title Format
```
[Command] {Task Description}
```

**Examples**:
- `[Command] Implement YUNG Command Handler`
- `[Command] Add Command History Storage`
- `[Command] Fix Command Parsing for Quoted Strings`

---

## Description Template

### Overview
<!-- Brief description of the command functionality -->

**Command Type**: [ ] Handler | [ ] Middleware | [ ] Integration | [ ] Other: _______

**Command Prefix**: [ ] $ (YUNG) | [ ] @ (IDFW) | [ ] # (Unified) | [ ] / (Slash)

**Complexity**: [ ] Simple | [ ] Medium | [ ] Complex

**Estimated Hours**: ___ h

---

### Requirements

#### Command Specification

**Command Name**: `[prefix][command-name]`

**Syntax**:
```bash
[prefix][command-name] [--flag] [--option value] [positional-args]
```

**Example Usage**:
```bash
$ validate --schema /path/to/schema.json --verbose
@ create-document --name "My Document" --sections api,models
# convert-schema --from idfw --to force --input schema.idfw
/ deploy-agent-team --department development
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--flag` | boolean | No | false | Flag description |
| `--option` | string | Yes | N/A | Option description |
| `arg1` | string | Yes | N/A | Positional arg description |

---

### Implementation Details

#### Files to Create/Modify
```
unified_framework/
├── commands/
│   ├── handlers/
│   │   └── [handler_name].py
│   ├── middleware/
│   │   └── [middleware_name].py
│   └── processor.py (modify)
└── tests/
    └── unit/
        └── commands/
            └── test_[handler_name].py
```

#### Handler Implementation
```python
class [HandlerName]CommandHandler(CommandHandler):
    """Handler for [command-type] commands"""

    async def execute(
        self,
        command: Command,
        context: CommandContext,
    ) -> CommandResult:
        """
        Execute the command

        Args:
            command: Parsed command
            context: Execution context

        Returns:
            Command execution result
        """
        pass

    def supports(self, command: Command) -> bool:
        """Check if this handler supports the command"""
        return command.prefix == CommandPrefix.[PREFIX]
```

---

### Integration Points

#### External Systems
- [ ] Dev Sentinel integration
- [ ] IDFW generator integration
- [ ] Linear API integration
- [ ] Message bus integration
- [ ] State manager integration

#### Internal Components
- [ ] Schema bridge
- [ ] Agent orchestrator
- [ ] MCP server
- [ ] File system

---

### Test Cases

#### Unit Tests Required
1. **Test command parsing**
   - Valid command syntax
   - Invalid command syntax
   - Missing required parameters
   - Default values

2. **Test command execution**
   - Success path
   - Error handling
   - Timeout handling
   - Cancellation

3. **Test middleware integration**
   - Logging middleware
   - Validation middleware
   - Permission middleware

4. **Test result transformation**
   - Success result
   - Error result
   - Partial result

**Test Coverage Target**: 90%

#### Integration Tests Required
- [ ] End-to-end command execution
- [ ] Command pipeline/chaining
- [ ] Error recovery
- [ ] Performance under load

---

### Acceptance Criteria

**Definition of Done**:
- [ ] Handler implementation complete
- [ ] Command parsing working correctly
- [ ] All parameters validated
- [ ] Error messages are helpful
- [ ] Unit tests passing (coverage > 90%)
- [ ] Integration tests added
- [ ] Command documented in CLI help
- [ ] Examples added to documentation
- [ ] Performance meets targets
- [ ] PR created and linked

**Success Metrics**:
- Command parsing success rate: > 99%
- Execution time: < 50ms overhead
- Error rate: < 1%
- Help text completeness: 100%

---

### Dependencies

**Blocked By**:
- PEG-XXX: [Related Issue Title]

**Blocks**:
- PEG-XXX: [Related Issue Title]

**Related Issues**:
- PEG-XXX: [Related Issue Title]

---

### Command Documentation

#### Help Text
```
[command-name] - Brief description

Usage:
  [prefix][command-name] [options] [args]

Options:
  --flag              Flag description
  --option <value>    Option description
  --help, -h          Show this help message

Arguments:
  arg1                Positional argument description

Examples:
  # Example 1: Basic usage
  [prefix][command-name] arg1

  # Example 2: With options
  [prefix][command-name] --option value arg1

  # Example 3: Complex usage
  [prefix][command-name] --flag --option value arg1 arg2
```

---

### Error Handling

#### Error Scenarios

| Error Type | Exit Code | Message | Recovery |
|------------|-----------|---------|----------|
| Invalid syntax | 1 | "Invalid command syntax" | Show usage |
| Missing parameter | 2 | "Missing required parameter: [name]" | Show help |
| Execution failed | 3 | "[Specific error message]" | Log and report |
| Timeout | 4 | "Command execution timed out" | Allow retry |

#### Error Messages
<!-- Example error messages that should be displayed -->
```
Error: Invalid command syntax
Usage: [prefix][command-name] [options] [args]
Run '[prefix][command-name] --help' for more information

Error: Missing required parameter: --schema
The --schema parameter is required for validation

Error: Command execution failed: [detailed error]
See log file for details: /var/log/idfwu/commands.log
```

---

### Performance Considerations

**Target Performance**:
- Command parsing: < 10ms
- Command execution overhead: < 50ms
- Memory usage: < 100MB
- Concurrent executions: > 100

**Optimization Notes**:
-
-

---

### GitHub References

**Branch**: `jeremiah/peg-XXX-command-[description]`
**PR**: #XXX (link when created)
**Commits**: (link to commits)

---

### Testing Instructions

#### Manual Testing
```bash
# Test command execution
[prefix][command-name] [args]

# Test with verbose output
[prefix][command-name] --verbose [args]

# Test error handling
[prefix][command-name]  # Missing required args

# Test help
[prefix][command-name] --help
```

#### Automated Testing
```bash
# Run unit tests
pytest unified_framework/tests/unit/commands/test_[handler_name].py -v

# Run integration tests
pytest unified_framework/tests/integration/test_command*.py -v

# Test command from CLI
python -m unified_framework.cli [prefix][command-name] [args]
```

---

### Documentation Updates

**Files to Update**:
- [ ] Command reference documentation
- [ ] CLI help text
- [ ] Examples directory
- [ ] Quick start guide

---

### Security Considerations

- [ ] Input validation and sanitization
- [ ] Permission checks
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Sensitive data handling

---

### Labels
`command`, `handler`, `yung|idfw|unified|slash`, `development`, `priority:high`

---

**Template Version**: 1.0.0
**Linear Project**: 4d649a6501f7
**Created**: 2025-09-29
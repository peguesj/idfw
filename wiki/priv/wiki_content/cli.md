<!-- section: Usage -->
# CLI Reference

The unified `idfw` CLI provides access to all framework capabilities.

## Installation

```bash
pip install -e ".[dev]"
idfw --help
```

## Command Groups

### Schema Commands
```bash
idfw schema validate <file>    # Validate against JSON Schema
idfw schema list               # List available schemas
idfw schema inspect <name>     # Show schema details
```

### Agent Commands
```bash
idfw agent list                # List registered agents
idfw agent status <id>         # Show agent status
idfw agent deploy <config>     # Deploy agent from config
idfw agent stop <id>           # Stop running agent
```

### FORCE Commands
```bash
idfw force validate            # Run FORCE validation suite
idfw force tools               # List available tools
idfw force constraints         # Show active constraints
idfw force governance          # Show governance policies
```

### Formation Commands
```bash
idfw formation deploy <name>   # Deploy a formation
idfw formation show            # Show current formation
idfw formation status          # Formation health status
idfw formation refactor        # Refactor formation structure
```

### MCP Commands
```bash
idfw mcp serve                 # Start MCP protocol server
idfw mcp status                # Show MCP server status
```

### Monitor Commands
```bash
idfw monitor start             # Start monitoring
idfw monitor dashboard         # Open APM dashboard
idfw monitor agents            # Show agent metrics
```

## Configuration

CLI configuration lives in `~/.idfw/config.json` or project-level `.idfw.json`.

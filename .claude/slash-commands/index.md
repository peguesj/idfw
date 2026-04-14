# Slash Commands Index - IDFWU Project

## Overview
This directory contains all slash command definitions for the IDFW Unified Framework project. Each command is designed to automate specific aspects of the unification process.

## Available Commands

### Core Integration Commands
- **[/fix-schema-conflicts](./fix-schema-conflicts.md)** - Resolve schema conflicts between IDFW and Dev Sentinel
- **[/implement-unified-cli](./implement-unified-cli.md)** - Build unified command-line interface
- **[/setup-mcp-server](./setup-mcp-server.md)** - Configure unified MCP server
- **[/implement-schema-bridge](./implement-schema-bridge.md)** - Create schema bridging system

### Agent Integration Commands
- **[/wrap-idfw-generators](./wrap-idfw-generators.md)** - Convert IDFW generators to agents
- **[/create-state-manager](./create-state-manager.md)** - Build unified state management

### Development & Testing Commands
- **[/setup-testing-framework](./setup-testing-framework.md)** - Establish comprehensive testing
- **[/document-api](./document-api.md)** - Generate API documentation
- **[/deploy-monitoring](./deploy-monitoring.md)** - Set up monitoring infrastructure

### Project Management Commands
- **[/create-linear-epic](./create-linear-epic.md)** - Create Linear epic for major features
- **[/update-project-status](./update-project-status.md)** - Generate project status updates

### Automation Commands
- **[/autofix](./autofix.md)** - Automatically launch fix agents concurrently
- **[/watch-deployment](./watch-deployment.md)** - Monitor deployment status

## Command Execution Guidelines

### Parallel Execution
Commands are designed to run concurrently when possible:
```bash
# Run multiple commands in parallel
/autofix
/setup-testing-framework
/document-api
```

### Dependencies
Some commands have dependencies:
1. Run `/fix-schema-conflicts` before `/implement-schema-bridge`
2. Run `/setup-mcp-server` before `/wrap-idfw-generators`
3. Run `/create-state-manager` after agent wrappers are ready

### Linear Integration
All commands automatically:
- Create Linear issues for tracking
- Update issue status during execution
- Add completion comments with results
- Link related issues and PRs

## Success Metrics
- **Command Success Rate**: Target >95%
- **Execution Time**: Average <2 minutes per command
- **Parallel Execution**: Support 3-5 concurrent commands
- **Linear Updates**: 100% issue tracking coverage

## Troubleshooting
- If rate limited: Commands auto-adjust concurrency
- If Linear fails: Commands cache updates for retry
- If tests fail: Commands create bug issues automatically

---

*Linear Project: IDFWU - IDEA Framework Unified (ID: 4d649a6501f7)*
*Last Updated: 2025-09-29*
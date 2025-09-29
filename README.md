# IDFWU - IDEA Framework Unified

> Unification of IDFW (IDEA Definition Framework) and Dev Sentinel into a comprehensive development framework with autonomous agent execution.

## Project Links

- **Linear Project**: [IDFWU - IDEA Framework Unified](https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7)
- **Linear Project ID**: `4d649a6501f7`
- **Team**: Pegues Innovations
- **Repository**: https://github.com/[to-be-created]/idfw-unified

## Overview

IDFWU combines two powerful frameworks into a unified system:

1. **IDFW (IDEA Definition Framework)**: Document-centric development framework with immutable/mutable variables, schema definitions, and project management
2. **Dev Sentinel (YUNG)**: Autonomous agent execution framework with MCP integration and tool orchestration

The unified framework provides:
- Seamless schema translation between IDFW and Force (Dev Sentinel)
- Unified command-line interface with multiple command prefixes
- Autonomous agent team with 16+ specialized roles
- Comprehensive MCP server integration
- State synchronization between frameworks
- Linear issue tracking integration

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/[to-be-created]/idfw-unified.git
cd idfw-unified

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Run tests
pytest
npm test
```

### Basic Usage

```bash
# YUNG commands (Dev Sentinel)
$ agent-deploy --squadron TDD

# IDFW actions
@ generate-document --type architecture

# Unified framework commands
# deploy-agent-team --all

# Slash commands for agents
/agent-architect
/fix-schema-conflicts
/update-project-status
```

## Directory Structure

```
idfwu/
├── unified_framework/          # Core unified framework code
│   ├── core/                   # Core integration components
│   ├── schemas/                # Unified schema definitions
│   ├── commands/               # Command processors
│   ├── agents/                 # Agent implementations
│   ├── mcp/                    # MCP server implementations
│   └── tests/                  # Test suites
├── unified_framework_docs/     # Documentation
│   ├── architecture/           # Architecture diagrams
│   ├── api/                    # API documentation
│   ├── guides/                 # User guides
│   └── agents/                 # Agent documentation
├── dev_sentinel/               # Dev Sentinel (symlink)
├── idfw_original/              # IDFW original (symlink)
├── .claude/                    # Claude Code configuration
├── .github/                    # GitHub Actions workflows
├── CLAUDE.md                   # Claude Code project instructions
├── CONTRIBUTING.md             # Contribution guidelines
├── README.md                   # This file
├── package.json                # Node package configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Python project configuration
└── setup.py                    # Python package setup
```

## Schema Organization

### IDFW Schemas
```
idfw/
├── documents/      # IDFW document schemas
├── diagrams/       # IDFW diagram schemas
├── variables/      # IDFW variable schemas
└── projects/       # IDFW project schemas
```

### Force Schemas (Dev Sentinel)
```
force/
├── tools/          # Force tool schemas
├── patterns/       # Force pattern schemas
├── constraints/    # Force constraint schemas
└── governance/     # Force governance schemas
```

### Unified Schemas
```
unified/
├── commands/       # Unified command schemas
├── workflows/      # Unified workflow schemas
└── integrations/   # Integration schemas
```

## Agent Team

IDFWU includes 16+ specialized agents organized into five departments:

### Product Agents
- **ProductOwnerAgent** (`/agent-product-owner`): Product vision and strategy
- **UserExperienceAgent** (`/agent-ux`): User experience design
- **RequirementsAnalystAgent** (`/agent-requirements`): Requirements analysis

### Project Agents
- **ProjectManagerAgent** (`/agent-project-manager`): Project coordination
- **ScrumMasterAgent** (`/agent-scrum-master`): Agile facilitation
- **ReleaseManagerAgent** (`/agent-release-manager`): Release coordination

### Development Agents
- **ArchitectAgent** (`/agent-architect`): System architecture
- **BackendDeveloperAgent** (`/agent-backend`): Backend implementation
- **FrontendDeveloperAgent** (`/agent-frontend`): Frontend implementation
- **SchemaEngineerAgent** (`/agent-schema`): Schema design
- **AgentDeveloperAgent** (`/agent-developer`): Agent system implementation

### Integration Agents
- **SystemIntegratorAgent** (`/agent-integrator`): System integration
- **DevOpsAgent** (`/agent-devops`): Infrastructure and automation
- **DatabaseAdminAgent** (`/agent-dba`): Database management

### Quality Agents
- **QualityAssuranceAgent** (`/agent-qa`): Testing and quality
- **SecurityAuditorAgent** (`/agent-security`): Security analysis
- **PerformanceEngineerAgent** (`/agent-performance`): Performance optimization
- **DocumentationAgent** (`/agent-documentation`): Documentation management

## Slash Commands Reference

### Agent Orchestration
- `/deploy-agent-team [department]` - Deploy agents concurrently
- `/agent-status [agent-id]` - Show agent status
- `/agent-sync` - Synchronize agents and tasks

### Integration & Setup
- `/fix-schema-conflicts` - Resolve schema conflicts
- `/implement-unified-cli` - Build unified CLI
- `/setup-mcp-server` - Configure MCP server
- `/wrap-idfw-generators` - Convert generators to agents
- `/create-state-manager` - Build state management
- `/implement-schema-bridge` - Create schema bridging

### Development & Testing
- `/setup-testing-framework` - Establish testing
- `/document-api` - Generate API docs
- `/deploy-monitoring` - Setup monitoring

### Project Management
- `/create-linear-epic` - Create Linear epic
- `/update-project-status [options]` - Update project status
- `/watch-deployment [options]` - Monitor deployments

### Quick Fix
- `/autofix` - Auto-fix critical issues

## Command Prefix Configuration

- `$` - YUNG commands (existing Dev Sentinel)
- `@` - IDFW actions (new)
- `#` - Unified framework commands (new)
- `/` - Slash commands for agents

## Linear Integration

All work is tracked in Linear with the project ID `4d649a6501f7`.

### Creating Issues
```bash
# Use MCP Linear server
mcp__linear-server__create_issue

# Or use slash command
/create-linear-epic
```

### Issue References
- Always use `PEG-XXX` format in commits
- Link GitHub PRs to Linear issues
- Update issue status as work progresses

### Workflow
1. Check Linear for existing issues
2. Create/update issues as needed
3. Commit with `PEG-XXX: Description`
4. Create PR with Linear references
5. Update Linear with completion status

## Development Standards

### Testing Requirements
- Unit test coverage minimum: 80%
- Integration tests for all major workflows
- E2E tests for critical user journeys
- Performance benchmarks for key operations

### Code Quality
- Type checking with mypy (Python) and TypeScript
- Linting with flake8 (Python) and ESLint (Node)
- Formatting with black (Python) and Prettier (Node)
- Pre-commit hooks for quality checks

### Documentation
- API documentation using OpenAPI 3.0
- Architecture diagrams using Mermaid
- User guides with examples
- Inline code documentation

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

### Commit Standards
```
type(scope): description

PEG-XXX: Implement unified schema system

feat: New feature
fix: Bug fix
docs: Documentation
test: Testing
refactor: Code refactoring
chore: Maintenance
```

## Monitoring and Metrics

### Key Metrics
- Command execution time
- Agent task completion rate
- Schema validation success rate
- State synchronization latency
- Error rates by component

### Alert Thresholds
- Command execution > 5 seconds
- Agent failure rate > 5%
- Schema validation failure > 10%
- State sync delay > 1 second

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- Linear Project: https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7
- Team: Pegues Innovations
- Project Lead: Jeremiah Pegues

---

*Project Version: 1.0.0*
*Last Updated: 2025-09-29*
*Linear Project: IDFWU - IDEA Framework Unified*
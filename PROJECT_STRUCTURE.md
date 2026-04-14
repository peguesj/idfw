# IDFWU Project Structure

## Overview

This document describes the complete structure of the **IDFWU (IDEA Framework Unified)** project located at `/Users/jeremiah/Developer/idfwu`.

## Directory Structure

```
idfwu/
├── .claude/                          # Claude Code configuration
│   ├── agents/                       # Agent definitions (18 agents)
│   │   ├── product/                  # POA, UXA, RAA
│   │   ├── project/                  # PMA, SMA, RMA
│   │   ├── development/              # ARA, BDA, FDA, SEA, ADA
│   │   ├── integration/              # SIA, DOA, DBA
│   │   ├── quality/                  # QAA, SAA, PEA, DOC
│   │   └── orchestration.yaml        # Agent orchestration config
│   ├── slash-commands/               # 17 slash command definitions
│   │   ├── index.md
│   │   ├── agent-*.md
│   │   ├── deploy-*.md
│   │   ├── fix-*.md
│   │   ├── implement-*.md
│   │   ├── setup-*.md
│   │   └── *.md
│   └── scripts/
│       └── init-project.sh           # Project initialization script
│
├── .github/                          # GitHub configuration
│   ├── workflows/
│   │   └── ci.yml                    # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
│
├── .vscode/                          # VS Code configuration
│   └── settings.json                 # Complete IDE settings
│
├── unified_framework/                # Framework implementation (planned)
│   ├── core/                         # Core integration components
│   ├── schemas/                      # Unified schema definitions
│   ├── commands/                     # Command processors
│   ├── agents/                       # Agent implementations
│   ├── mcp/                          # MCP server implementations
│   ├── cli/                          # CLI interface
│   └── tests/                        # Test suites
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── unified_framework_docs/           # Comprehensive documentation
│   ├── 00_EXECUTIVE_SUMMARY.md
│   ├── 01_ARCHITECTURE_OVERVIEW/
│   │   ├── IDFW_Analysis.md
│   │   ├── DevSentinel_Analysis.md
│   │   ├── Integration_Points.md
│   │   └── Unified_Architecture.md
│   ├── 02_SCHEMA_MAPPINGS/
│   │   └── Unified_Schema_Design.md
│   ├── 03_COMMAND_SYSTEMS/
│   │   ├── YUNG_Commands.md
│   │   ├── IDFW_Actions.md
│   │   └── Unified_Commands.md
│   ├── 04_AGENT_INTEGRATION/
│   │   ├── Agent_Wrappers.md
│   │   └── Message_Bus_Integration.md
│   ├── 05_MCP_PROTOCOL/
│   │   └── MCP_Extensions.md
│   ├── 06_IMPLEMENTATION_PLAN/
│   │   └── Phase_Roadmap.md
│   ├── INTEGRATION_COMPLETE.md
│   ├── LINEAR_INTEGRATION.md
│   ├── README.md
│   └── mermaid-plantuml-architecture-reference.md
│
├── idfw_original -> ../idfw          # Symlink to original IDFW repo
├── dev_sentinel -> ../yj-dev_sentinel # Symlink to Dev Sentinel repo
│
├── .gitignore                        # Git ignore rules
├── CLAUDE.md                         # Claude Code project instructions
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # MIT License
├── README.md                         # Project README
├── package.json                      # Node.js configuration
├── pyproject.toml                    # Python project configuration
├── requirements.txt                  # Python dependencies
└── setup.py                          # Python package setup

```

## Key Components

### 1. Agent System
- **18 specialized agents** across 5 departments
- **Product**: POA, UXA, RAA
- **Project**: PMA, SMA, RMA
- **Development**: ARA, BDA, FDA, SEA, ADA
- **Integration**: SIA, DOA, DBA
- **Quality**: QAA, SAA, PEA, DOC

### 2. Slash Commands (17 total)
- **Agent Commands**: `/deploy-agent-team`, `/agent-status`, `/agent-sync`
- **Implementation**: `/fix-schema-conflicts`, `/implement-unified-cli`, `/setup-mcp-server`
- **Development**: `/wrap-idfw-generators`, `/create-state-manager`, `/implement-schema-bridge`
- **Quality**: `/setup-testing-framework`, `/document-api`, `/deploy-monitoring`
- **Project**: `/create-linear-epic`, `/update-project-status`
- **Automation**: `/autofix`, `/watch-deployment`

### 3. Documentation (15+ files)
- **Executive Summary**: High-level overview
- **Architecture**: IDFW, Dev Sentinel, Integration, Unified
- **Schema Mappings**: Unified schema design
- **Command Systems**: YUNG, IDFW, Unified commands
- **Agent Integration**: Wrappers, message bus
- **MCP Protocol**: Extensions and implementations
- **Implementation Plan**: 10-week roadmap

### 4. Configuration Files
- **VS Code**: Complete IDE settings with Linear integration
- **GitHub**: CI/CD, issue templates, PR templates
- **Python**: pyproject.toml, requirements.txt, setup.py
- **Node**: package.json with test/lint/build scripts
- **Git**: Comprehensive .gitignore

## Linear Integration

**Project ID**: `4d649a6501f7`
**Project URL**: https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7
**Team**: Pegues Innovations

All components reference the Linear project for:
- Automated issue creation
- Progress tracking
- Sprint planning
- Cross-platform traceability

## Symlinks

### idfw_original
Links to `/Users/jeremiah/Developer/idfw` - the original IDFW framework repository.
- Contains: IDFW schemas, generators, documentation

### dev_sentinel
Links to `/Users/jeremiah/Developer/yj-dev_sentinel` - the Dev Sentinel repository.
- Contains: FORCE framework (171 components), agents, MCP servers

## Git Repository

- **Initialized**: ✅ Yes
- **Initial Commit**: ✅ Complete (69 files, 19,099 insertions)
- **Branch**: main
- **Remote**: Not yet configured

## Quick Start

### 1. Initialize Project
```bash
cd /Users/jeremiah/Developer/idfwu
./.claude/scripts/init-project.sh
```

### 2. Activate Environment
```bash
source venv/bin/activate
```

### 3. Run Tests
```bash
pytest unified_framework/tests/ -v
```

### 4. Deploy Agent Team
```bash
python unified_framework/agents/deploy_team.py
# Or use slash command: /deploy-agent-team --all
```

## Development Workflow

1. **Check Linear** for existing issues
2. **Create branch** using Linear naming: `jeremiah/peg-XXX-feature`
3. **Make changes** following standards in CONTRIBUTING.md
4. **Run tests** and ensure they pass
5. **Commit** with Linear reference: `PEG-XXX: Description`
6. **Create PR** using GitHub template
7. **Update Linear** issue with PR link

## Next Steps

1. Run initialization script
2. Install dependencies
3. Set up virtual environment
4. Begin Phase 1 implementation (Schema Bridge)
5. Deploy development agents
6. Create Linear epics for implementation phases

---

*Document Version: 1.0.0*
*Created: 2025-09-29*
*Linear Project: IDFWU (4d649a6501f7)*
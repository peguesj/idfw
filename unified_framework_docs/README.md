# Unified Framework Documentation

## Overview

This directory contains comprehensive documentation for the unification of **IDFW (IDEA Definition Framework)** and **Dev Sentinel** into a cohesive, powerful development framework.

## Project Status

- **Phase**: v4.0 Shipped (Phase 8 Complete, Inception Layer)
- **Version**: Documentation v4.0.0
- **Date**: 2026-04-11
- **Test Suite**: 597 pass, 26 skipped, 0 fail
- **Schemas**: 8/8 validate, FORCE 68/68 PASS
- **Runtime**: /idea daemon live on port 4040, IDFWU macOS app live

## Documentation Structure

```
unified_framework_docs/
│
├── 00_EXECUTIVE_SUMMARY.md              # High-level overview and vision
│
├── 01_ARCHITECTURE_OVERVIEW/            # System architecture documentation
│   ├── IDFW_Analysis.md                 # Complete IDFW framework analysis
│   ├── DevSentinel_Analysis.md          # Complete Dev Sentinel analysis
│   ├── Integration_Points.md            # Identified integration opportunities
│   └── Unified_Architecture.md          # Proposed unified system design
│
├── 02_SCHEMA_MAPPINGS/                  # Schema integration documentation
│   └── Unified_Schema_Design.md         # Merged schema approach and mappings
│
├── 03_COMMAND_SYSTEMS/                  # Command system integration
│   ├── YUNG_Commands.md
│   ├── IDFW_Actions.md
│   └── Unified_Commands.md
│
├── 04_AGENT_INTEGRATION/                # Agent architecture
│   ├── Agent_Wrappers.md
│   └── Message_Bus_Integration.md
│
├── 05_MCP_PROTOCOL/                     # MCP integration
│   └── MCP_Extensions.md
│
├── 06_IMPLEMENTATION_PLAN/              # Implementation roadmap
│   └── Phase_Roadmap.md
│
├── 07_DISCOVERY_FRAMEWORK/              # v4.0 Project discovery system
│   └── Discovery_Architecture.md        # Multi-source provider system
│
└── 08_IDEA_LIFECYCLE/                   # v4.0 /idea skill lifecycle
    └── Lifecycle_Architecture.md        # new → discover → define → plan → execute
```

## Quick Reference

### Key Findings

#### IDFW (IDEA Definition Framework)
- **Version**: 2.1.1
- **Purpose**: JSON Schema-based project structure and documentation framework
- **Strengths**:
  - Comprehensive schema definitions
  - LLM-optimized token management
  - Project templates and journeys
  - Strong validation framework

#### Dev Sentinel
- **Version**: 0.4.3
- **Purpose**: AI-powered development assistant with autonomous agents
- **Strengths**:
  - Multi-agent architecture
  - FORCE framework with 40+ tools
  - YUNG command system
  - MCP protocol integration

### Integration Synergies

| Aspect | IDFW Provides | Dev Sentinel Provides | Unified Benefit |
|--------|---------------|----------------------|-----------------|
| **Definition** | Project structure & schemas | Execution framework | Complete lifecycle management |
| **Documentation** | Templates & standards | Generation agents | Automated documentation |
| **Commands** | Project actions | YUNG commands | Unified command interface |
| **Validation** | Schema validation | Tool validation | Comprehensive validation |
| **State** | Variable system | Agent states | Unified state management |

## Key Documents

### Essential Reading

1. **[Executive Summary](00_EXECUTIVE_SUMMARY.md)** - Start here for overview
2. **[Integration Points](01_ARCHITECTURE_OVERVIEW/Integration_Points.md)** - Key synergies identified
3. **[Unified Architecture](01_ARCHITECTURE_OVERVIEW/Unified_Architecture.md)** - Proposed system design
4. **[Schema Design](02_SCHEMA_MAPPINGS/Unified_Schema_Design.md)** - Schema unification strategy

### v4.0 Documentation (New)

5. **[Discovery Framework](07_DISCOVERY_FRAMEWORK/Discovery_Architecture.md)** - Multi-source project discovery
6. **[IDEA Lifecycle](08_IDEA_LIFECYCLE/Lifecycle_Architecture.md)** - End-to-end idea-to-execution flow

### Deep Dives

- **[IDFW Analysis](01_ARCHITECTURE_OVERVIEW/IDFW_Analysis.md)** - Complete IDFW framework analysis
- **[Dev Sentinel Analysis](01_ARCHITECTURE_OVERVIEW/DevSentinel_Analysis.md)** - Complete Dev Sentinel analysis

## Unified Framework Benefits

### 1. Seamless Integration
- Single command interface combining YUNG and IDFW commands
- Unified state management across both systems
- Consistent validation and error handling

### 2. Enhanced Capabilities
- IDFW project definitions with autonomous execution
- Force tools aware of IDFW project context
- Multi-agent workflows with IDFW generators

### 3. Developer Experience
- One CLI for all operations
- VS Code integration through MCP
- Comprehensive documentation and tooling

## Implementation Plan Summary

### Phase 1: Foundation (Weeks 1-2)
- Create unified directory structure
- Establish schema mapping framework
- Build basic command routing

### Phase 2: Schema Integration (Weeks 3-4)
- Merge JSON schemas
- Implement validation layer
- Create conversion utilities

### Phase 3: Command Unification (Weeks 5-6)
- Extend YUNG with IDFW commands
- Build unified CLI
- Implement command mapping

### Phase 4: Agent Integration (Weeks 7-8)
- Wrap IDFW generators as agents
- Integrate message bus
- Implement state synchronization

### Phase 5: Protocol & Deployment (Weeks 9-10)
- Complete MCP integration
- VS Code extension updates
- Testing and documentation

## Next Steps

1. **Review Documentation**: Ensure all stakeholders review the analysis
2. **Approve Architecture**: Get sign-off on unified architecture design
3. **Begin Implementation**: Start Phase 1 implementation
4. **Set Up Development Environment**: Configure unified development setup
5. **Create Test Framework**: Establish testing infrastructure

## Technical Details

### Unified Command Examples

```bash
# IDFW commands (proposed @ prefix)
@init enterprise multi-tenant    # Initialize IDFW project
@generate BRD                    # Generate business requirements
@validate project                # Validate project structure

# YUNG commands (existing $ prefix)
$VIC ALL                         # Validate all files
$CODE TIER=backend FIX          # Fix backend issues
$VCS COMMIT MESSAGE="update"    # Commit changes

# Unified commands (proposed # prefix)
#workflow complete-setup         # Run unified workflow
#analyze project                # Combined analysis
#deploy staging                 # Unified deployment
```

### Unified Schema Example

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "unified:command",
  "type": "object",
  "properties": {
    "type": {"enum": ["yung", "idfw", "unified"]},
    "command": {"type": "string"},
    "parameters": {"type": "object"},
    "context": {"$ref": "#/$defs/ExecutionContext"}
  }
}
```

### MCP Integration

```json
{
  "mcpServers": {
    "unified-framework": {
      "command": "unified-mcp-server",
      "args": ["--idfw", "--force"],
      "env": {
        "UNIFIED_MODE": "true",
        "ENABLE_IDFW": "true",
        "ENABLE_FORCE": "true"
      }
    }
  }
}
```

## Contributing

### Documentation Updates
1. Follow the existing structure
2. Update version numbers and dates
3. Cross-reference related documents
4. Maintain consistency in terminology

### Implementation Contributions
1. Review the architecture documents
2. Follow the implementation phases
3. Write tests for new features
4. Update documentation as you code

## Contact & Support

For questions about this unification project:
- Review the documentation in this directory
- Check the integration points document for technical details
- Refer to individual framework documentation for specific features

## License & Attribution

This unified framework documentation combines analysis of:
- **IDFW** (IDEA Definition Framework) v2.1.1
- **Dev Sentinel** v0.4.3

---

*Documentation Version: 4.0.0*
*Last Updated: 2026-04-11*
*Status: v4.0 Shipped — Phase 8 Complete, branch idfw/idea-v4-inception pending merge*
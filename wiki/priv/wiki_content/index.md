<!-- section: Overview -->
# IDFW - IDEA Definition Framework

Welcome to the IDFW Wiki -- the unified knowledge base for the IDEA Definition Framework ecosystem.

## The Evolution Story

IDFW represents a **fundamental architectural shift**: from four bloated repositories with 12,865 lines of unused code to a unified, skills-based framework that loads only what's needed.

| Before | After |
|--------|-------|
| 40,000 tokens loaded per session | 5,000 token core (8x reduction) |
| 5 heavyweight monolithic agents | 5 lean agents + 247 discrete skills |
| 7,098-line hooks system (unused) | Event-driven, on-demand loading |
| 10 governance policies (unenforced) | 2-3 focused, active policies |
| 68 FORCE validation failures | 68/68 PASS (100%) |

**Deep dives**: [Evolution Trace](/wiki/evolution) | [Bloat Analysis](/wiki/bloat-analysis) | [Skills Architecture](/wiki/skills-architecture)

## What is IDFW?

IDFW (IDEA Definition Framework Workspace) is the consolidated monorepo unifying four previously separate repositories into a single, coherent framework for agent orchestration, schema validation, and development tooling.

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Files | 399+ |
| Schema Files | 8 validated |
| FORCE Validations | 68/68 (100%) |
| Skills Catalog | 247 across 24 modules |
| Agents Registered | 228 |
| CLI Commands | 52 |
| Implementation Coverage | 86.3% (of analyzed skills) |

## Repository Origins

| Repo | Purpose | Key Contribution |
|------|---------|-----------------|
| **IDFW** (Core) | Schema definitions, seed data | 8 validated schema files |
| **IDFWU** (Unified) | Runtime framework, CLI, MCP | Core agents, services (minus bloat) |
| **IDFWU2** (Planning) | Strategic analysis, skills catalog | 247-skill architecture, Vanguart analysis |
| **Dev Sentinel** (FORCE) | Governance, specialized agents | 5 lean agents, FORCE tool system |

Consolidated in B01-B08 (Feb 2026) into the unified IDFW monorepo.

## Architecture

```
idfw/
├── .force/              # FORCE governance (94 JSON configs)
├── force/               # FORCE Python package
├── unified_framework/
│   ├── agents/          # Base agent, orchestrator
│   ├── cli/             # Unified CLI (idfw command)
│   ├── core/            # Schema bridge, state manager
│   ├── mcp/             # MCP protocol server
│   ├── services/        # APM client, checkpoint manager
│   └── schemas/         # JSON Schema definitions
├── agents/              # Dev Sentinel agents (CDIA, RDIA, SAA, VCLA, VCMA)
├── dev_sentinel/        # Dev Sentinel package
├── integration/         # FastAgent, FORCE integration
├── planning/            # Skills mapping, catalog, reports
└── wiki/                # This wiki (Phoenix LiveView)
```

## Wiki Pages

### Architecture
- [Formation Architecture](/wiki/formation) - Hierarchical agent deployment
- [Skills Architecture](/wiki/skills-architecture) - 247-skill catalog and framework
- [Agent Architecture](/wiki/agents) - Agent hierarchy and orchestration

### Framework
- [FORCE Framework](/wiki/force) - Governance, validation, tooling
- [Schema Definitions](/wiki/schemas) - JSON Schema infrastructure

### Analysis
- [Bloat Analysis](/wiki/bloat-analysis) - Before/after metrics from 4-repo analysis
- [Evolution Trace](/wiki/evolution) - Full history with commits and quotes

### Usage
- [CLI Reference](/wiki/cli) - Unified `idfw` command documentation

## Getting Started

```bash
# Install the framework
pip install -e ".[dev]"

# Run CLI
idfw --help

# Run tests
pytest

# Start wiki
cd wiki && mix phx.server
```

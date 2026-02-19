<!-- section: Architecture -->
# Skills-Based Architecture

The defining evolution of IDFW: from monolithic agent roles to 247 discrete, composable skills organized across 24 modules.

## The Pivot

The strategic analysis document "Vanguart" (from IDFWU2) identified the core problem:

> "Overloaded context leads to 'Instruction Watering Down,' where the model ignores critical project rules because it is overwhelmed by irrelevant data."

The solution: **Progressive Disclosure** -- load only relevant information when needed, using discrete skills instead of monolithic instruction files.

## Token Economics

| Approach | Base Tokens | Context Recovery | Session Efficiency |
|----------|-------------|------------------|--------------------|
| Old (Monolithic CLAUDE.md) | 40,000 | 0% | Low - all rules loaded regardless |
| New (Skills-Based) | 5,000 | 70-80% | High - on-demand loading |

**Result**: 8x reduction in base token usage with intelligent context assembly.

### Token Budget by Context

| Context | Base | Add-Ons | Total |
|---------|------|---------|-------|
| Minimal (core only) | 5,000 | -- | 5,000 |
| TDD workflow | 5,000 | TDD (2,500) + Commands (8,000) | 15,500 |
| Fix loop | 5,000 | Fix (3,000) + Commands (8,000) | 16,000 |
| Full project | 5,000 | Project (3K) + Commands (8K) + Methodology (6K) | 22,000 |
| Maximum (all modules) | 5,000 | ~50,000 | 55,000 |

## FORCE Framework: 156 Skills

The FORCE (Framework for Orchestrated Reliable Code Evolution) framework expanded from 5 components to 15 modules containing 156 discrete skills.

| Layer | Full Name | Modules | Skills | Purpose |
|-------|-----------|---------|--------|---------|
| **F** | Foundation | 4 | 42 | Context Management, Progressive Disclosure, Token Optimization, Memory & State |
| **O** | Orchestration | 4 | 48 | Mode System (SPARC), Mission Control, Agent Coordination, Workflow |
| **R** | Runtime | 4 | 36 | Hook Lifecycle, MCP Integration, A2UI, Tool Execution |
| **C** | Compliance | 2 | 18 | Governance Engine, Security Module |
| **E** | Evolution | 1 | 12 | Learning & Analytics |

### Key FORCE Skills

**Progressive Disclosure Engine (F.2)**:
- `F2-001` skill_discovery_scanner - Discover skills via semantic matching
- `F2-002` on_demand_skill_loader - Load full skill content when needed
- `F2-003` metadata_index_builder - Build lightweight metadata index
- `F2-008` disclosure_order_optimizer - Optimize what loads first

**Mode System / SPARC (O.1)**:
- `O1-001` mode_security_auditor - Read-only security analysis
- `O1-002` mode_documentation_writer - Doc-only file access
- `O1-003` mode_tdd_implementer - Test-first enforcement
- `O1-005` mode_architect_planner - Exploration-only planning

**Mission Control (O.2)**:
- `O2-001` agent_instance_spawner - Spawn agent instances
- `O2-009` squadron_team_deployer - Deploy agent squadrons
- `O2-010` dashboard_state_renderer - Visual dashboard (Wave 1 gap)

## IDEA Framework: 91 Skills

The IDEA framework provides 91 skills across 9 modules for project lifecycle management.

| Layer | Full Name | Modules | Skills | Purpose |
|-------|-----------|---------|--------|---------|
| **I** | Inception | 2 | 18 | Project Definition, Stakeholder Management |
| **D** | Documentation | 3 | 32 | Requirements Docs, Technical Docs, Operational Docs |
| **E** | Evolution | 1 | 22 | Schema Management (IDPC, IDPG, IDDG, IDDC, IDDA, IDFV) |
| **G** | Generation | 2 | 30 | Diagram Generation, Schema Management |
| **A** | Assurance | 2 | 19 | Traceability, Quality Assurance |

## Implementation Status

Of 243 total cataloged skills, 51 have been deeply analyzed with cross-referencing against implementation files:

| Status | Count | Percentage |
|--------|-------|------------|
| **IMPLEMENTED** | 33 | 64.7% |
| **PARTIAL** | 11 | 21.6% |
| **NOT_STARTED** | 7 | 13.7% |
| Unmapped (phased) | 192 | Wave 2-3 work |

### Layer Coverage

| Layer | Coverage | Status |
|-------|----------|--------|
| F (Foundation) | 70% | Strong |
| O (Orchestration) | 81.8% | Excellent |
| R (Runtime) | 66.7% | Good |
| C (Compliance) | 100% | Complete |
| E (Evolution) | 100% | Complete |
| I (Inception) | 0% | Needs work |
| D (Documentation) | 66.7% | Good |
| A (Assurance) | 100% | Complete |

### Implementation Resources

The 33 implemented skills map to 75 artifacts:
- **15 agent files** (security, documentation, architecture, orchestration, learning)
- **9 configuration files** (memory-system, slash-commands, agent-execution)
- **51 FORCE tool definitions** (git, documentation, analysis, testing, deployment)

## Three Pillars

### 1. Progressive Disclosure
Load information on-demand based on semantic intent matching. Instead of 40K tokens upfront, start with 5K core and fetch what's needed.

### 2. Mode Specialization
20 specialized modes with least-privilege permissions replace one generalist agent. A security auditor gets read-only access. A TDD implementer enforces test-first.

### 3. Mission Control
Multi-agent async orchestration. Dispatch 5 agents for 5 tasks simultaneously. Monitor via APM dashboard. Inject feedback during execution.

## Cross-Framework Integration

10 defined integration points bridge FORCE and IDEA skills:

| FORCE Skill | IDEA Skill | Purpose |
|-------------|-----------|---------|
| hook_post_commit | change_history_tracker | Auto-track changes on commit |
| mode_documentation_writer | brd_generator_full | Generate BRD in doc mode |
| context_provider_docs | All D1/D2 skills | Index IDEA docs as context |
| squadron_team_deployer | project_initializer_wizard | Deploy agents for new project |
| audit_trail_logger | audit_trail_generator | Unified audit trail |
| mcp_ecosystem_integrator | rtm_matrix_generator | Link RTM with GitHub/Jira |

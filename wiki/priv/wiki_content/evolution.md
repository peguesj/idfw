<!-- section: History -->
# Evolution Trace

The IDFW ecosystem evolved through four distinct phases -- from monolithic bloat to a lean, skills-based architecture. This page documents that journey with specific commits, metrics, and strategic quotes.

## The Core Narrative

> "The software development lifecycle is currently undergoing its most significant structural transformation since the advent of high-level programming languages."
> -- Vanguart Strategic Analysis (IDFWU2)

**From**: 5 heavyweight agents + 40,000-token monolithic config + 7,098-line hooks system + unused governance
**To**: 247 discrete skills + 5,000-token core + progressive disclosure + mode-based execution

## Phase 1: IDFW (Core Schemas)

The original IDFW repository established the foundational schema definitions:

- **IDDA.schemas.json** - IDEA Data Architecture schemas
- **IDDV.schemas.json** - IDEA Data Validation schemas
- **DDD.schema.jsonc** - Domain-Driven Design schema
- **resume.schema.json** - Resume/capability schema (draft-2020-12)
- Seed data files for framework initialization
- JSON Schema validation infrastructure

**Key milestone**: CP-01 through CP-06 fixed all structural errors, achieving 100% JSON validation.

## Phase 2: IDFWU (The Bloat Phase)

IDFWU introduced the runtime framework -- but also introduced massive scope creep.

**Original Plan** (Sept 29, 2025):
- 6 components, 26 sub-tasks, 104 hours
- Schema conversion + command routing + agent activation

**What Actually Happened** (Oct 8, 2025):
- +12,000 LOC added in a single day (50%+ of the codebase)
- PEG-996 commit: 6,390-line hooks system with sentiment analysis, reinforcement learning, PII detection, vector RAG
- PEG-992 commit: 3,270-line monitoring dashboard with GridStack, Chart.js, D3.js
- Multiple "unified server" implementations created simultaneously

**The Hooks System** (7,098 LOC -- never in the original plan):
- Sentiment analysis across 8 categories with 12 accuracy dimensions
- Pattern recognition with reinforcement learning
- PII detection with encryption and audit trails
- Semantic search via vectorization (vector RAG)
- 4 system integrations (Linear, Agent, IDE, Todo)
- Processing overhead: 2-5ms per message

> "Feature expansion without scope approval -- the hooks system was an undeclared enhancement that added 27% of total complexity."

**Total IDFWU**: 58 Python files, 26,986 LOC. **12,865 LOC identified as bloat (50%).**

## Phase 3: IDFWU2 (The Skills Pivot)

IDFWU2 represented the strategic turning point. Instead of building more framework, it analyzed what worked and what didn't.

**Key Documents**:
- `vanguart.md` (30 KB) - Strategic analysis of 6 agentic tools (Claude Code, Roo Code, Continue.dev, Antigravity, Codex Max, Copilot)
- `comprehensive_skills_catalog.md` (35 KB) - Full 247-skill expansion
- `SQ-08-SKILLS-IMPLEMENTATION-REPORT.md` (16 KB) - Implementation status with cross-referencing

**The Insight: Context Bloat Was the Enemy**

> "Context hygiene is the practice of maintaining the 'purity' and relevance of the information currently stored in the agent's memory. Overloaded context leads to 'Instruction Watering Down,' where the model ignores critical project rules because it is overwhelmed by irrelevant data."

**The Solution: Progressive Disclosure**

> "Claude Code solves this by loading only the most relevant metadata initially and fetching detailed instructions or scripts only when the agent determines they are necessary for the task at hand."

**Token Impact**:
- Old: 40,000 tokens loaded every session regardless of task
- New: 5,000 core tokens + context-aware module loading
- Result: **8x reduction** in base token usage

## Phase 4: Dev Sentinel (FORCE Framework)

Dev Sentinel brought governance and specialized agents -- but also demonstrated over-engineering at the governance layer.

**What Was Valuable** (90%):
- 5 lean agents (CDIA, RDIA, SAA, VCLA, VCMA) -- none exceeding 540 lines
- Message-bus integration, async task handling
- FORCE tool executor for git and documentation workflows

**What Was Bloat**:
- 10 governance policies with no enforcement engine (80% bloat)
- Learning system with only 5 example records, all with identical timestamps (90% bloat)
- 51 tool definitions where 30+ were unused (60% bloat)
- Generator tools to make tools that were never used (meta-over-engineering)

**Key milestone**: CP-07 through CP-12 achieved 68/68 FORCE validation (100%).

## Phase 5: Consolidation (B01-B08)

The B-series batches merged everything into IDFW, stripping bloat and keeping value:

| Batch | Contents | What Was Kept |
|-------|----------|---------------|
| B01 | Package foundation | Unified pyproject.toml, renamed to `idfw` |
| B02 | FORCE framework | .force/ configs (94 files) + force/ package |
| B03 | Unified core | schema_bridge, state_manager, converters |
| B04 | Agents & orchestration | 5 lean agents + base_agent + orchestrator |
| B05 | Services & monitoring | APM client, checkpoint manager (no dashboard bloat) |
| B06 | CLI, MCP, integration | Unified CLI + MCP server + legacy adapter |
| B07 | Tests & planning | 14 tests + 3 planning artifacts (skills catalog) |
| B08 | Verification | Exports, CHANGELOG, documentation |

**Result**: 399 files, 77K insertions, unified `idfw` CLI entry point.

## Phase 6: Skills-Based Architecture (Current)

The current architecture replaces heavyweight agents with 247 discrete skills:

| Metric | Old (4 repos) | New (IDFW) |
|--------|---------------|------------|
| Token Load | 40,000/session | 5,000/session |
| Agent Model | 5 heavyweight | 5 lean + 247 skills |
| Context Strategy | All-or-nothing | Progressive disclosure |
| Governance | 10 unenforced policies | 2-3 focused policies |
| Validation | 68 failures | 68/68 PASS (100%) |
| Orphaned Code | 89% agents unmapped | Runtime-bound |

**Three Pillars**:
1. **Progressive Disclosure** - Load information on-demand
2. **Mode Specialization** - Least-privilege, focused agents
3. **Mission Control** - Multi-agent async orchestration

See [Skills Architecture](/wiki/skills-architecture) for the full 247-skill breakdown.
See [Bloat Analysis](/wiki/bloat-analysis) for detailed before/after metrics.

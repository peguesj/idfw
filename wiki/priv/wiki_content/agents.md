<!-- section: Framework -->
# Agent Architecture

IDFW supports 228 registered agents across multiple orchestration layers.

## Agent Hierarchy

### Formation Architecture

Agents are organized into formations - hierarchical structures for coordinated execution:

```
Formation
├── Squadron (5-8 agents, mission-focused)
│   ├── Swarm (2-3 agents, task-focused)
│   │   ├── Agent (individual executor)
│   │   └── Agent
│   └── Swarm
│       ├── Agent
│       └── Agent
├── Squadron
│   └── ...
└── Cluster (cross-cutting concerns)
    ├── Monitor Agent
    └── Coordinator Agent
```

### Department Structure (from IDFWU)

| Department | Agents | Focus |
|-----------|--------|-------|
| Engineering | 5 | Code, build, deploy |
| Quality | 4 | Test, lint, validate |
| Operations | 3 | Monitor, health, scale |
| Security | 3 | Audit, scan, enforce |
| Intelligence | 3 | Analyze, learn, predict |

### Dev Sentinel Agents

| Agent | Role |
|-------|------|
| CDIA | Continuous development intelligence |
| RDIA | Runtime development intelligence |
| SAA | Static analysis |
| VCLA | Version control lifecycle |
| VCMA | Version control management |

## Orchestration

The orchestrator service manages agent lifecycle:

1. **Registration** - Agent registers with APM
2. **Assignment** - Orchestrator assigns tasks based on capability
3. **Execution** - Agent executes with checkpoint support
4. **Reporting** - Results reported to APM dashboard
5. **Cleanup** - Resources released, state persisted

## Runtime Bindings

CP-14 resolved 89% orphaned agents (66/74) by creating runtime bindings connecting agent definitions to executable handlers.

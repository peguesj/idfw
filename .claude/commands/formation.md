---
description: "Formation-based agentic architecture for deploying hierarchical agent structures. Manages squadrons, swarms, clusters, and individual agents with APM integration."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, WebFetch
---

# Formation Architecture Command

You are managing IDFW's formation-based agentic architecture. Formations are hierarchical agent structures deployed for coordinated task execution.

## Subcommands

The user said: $ARGUMENTS

Parse the arguments to determine the subcommand:

### `deploy <formation-name>`
Deploy a named formation. Steps:
1. Read formation config from `.force/formations/<name>.json` or use built-in templates
2. Validate agent availability against APM at http://localhost:3031
3. Register formation with APM: `curl -X POST http://localhost:3031/api/register -H 'Content-Type: application/json' -d '{"agent_name":"formation:<name>","agent_type":"formation","status":"deploying"}'`
4. Spawn agents concurrently using Task tool
5. Report hierarchical tree to APM and user

Built-in formations:
- **tdd-squadron**: 6 agents (2 test-writers, 2 implementers, 1 reviewer, 1 integrator)
- **fix-swarm**: 3 agents (1 analyzer, 2 fixers)
- **ops-cluster**: 3 agents (1 monitor, 1 coordinator, 1 reporter)
- **full-stack**: Combines tdd-squadron + ops-cluster

### `show`
Display the current formation tree structure:
```
Formation: tdd-squadron (active)
├── Swarm: test-writers (2 agents)
│   ├── Agent: test-writer-1 [running]
│   └── Agent: test-writer-2 [running]
├── Swarm: implementers (2 agents)
│   ├── Agent: impl-1 [running]
│   └── Agent: impl-2 [idle]
├── Agent: reviewer-1 [running]
└── Agent: integrator-1 [waiting]
```
Query APM for active agents and reconstruct the tree.

### `status`
Health check all active formations:
1. Query APM: `curl http://localhost:3031/api/agents`
2. Filter formation-registered agents
3. Report health metrics per formation
4. Flag any degraded or failed agents

### `refactor`
Restructure an active formation:
1. Analyze current formation topology
2. Identify bottlenecks or idle agents
3. Propose restructuring (merge swarms, add agents, remove idle)
4. Apply changes with user confirmation

### `apm`
Open APM dashboard with formation view:
```bash
open http://localhost:3031
```

## APM Integration

All formation operations report to CCEM APM:
- Register formation agents with type "formation"
- Send heartbeats during execution
- Report completion/failure events
- Update hierarchical tree visualization

## Tree Depiction Format

When reporting to APM or displaying to user, use this format:
```
[Formation] name (status)
├── [Squadron] name
│   ├── [Swarm] name
│   │   ├── [Agent] name [status]
│   │   └── [Agent] name [status]
│   └── [Swarm] name
│       └── [Agent] name [status]
└── [Cluster] name
    └── [Agent] name [status]
```

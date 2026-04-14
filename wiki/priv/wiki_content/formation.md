<!-- section: Architecture -->
# Formation Architecture

Formations are the deployment unit for hierarchical agent structures in IDFW.

## Concept

A Formation is a named, versioned configuration that defines:
- Which agents to deploy
- How they're organized (squadrons, swarms, clusters)
- Communication patterns between them
- Resource allocation and constraints
- Lifecycle policies (scaling, failover, cleanup)

## Formation Types

### Squadron Formation
Mission-focused group of 5-8 agents working toward a single objective.

```json
{
  "name": "tdd-squadron",
  "type": "squadron",
  "agents": [
    {"role": "test-writer", "count": 2},
    {"role": "implementer", "count": 2},
    {"role": "reviewer", "count": 1},
    {"role": "integrator", "count": 1}
  ],
  "strategy": "red-green-refactor"
}
```

### Swarm Formation
Task-focused group of 2-3 agents for rapid parallel execution.

```json
{
  "name": "fix-swarm",
  "type": "swarm",
  "agents": [
    {"role": "analyzer", "count": 1},
    {"role": "fixer", "count": 2}
  ],
  "strategy": "divide-and-conquer"
}
```

### Cluster Formation
Cross-cutting formation for monitoring and coordination.

```json
{
  "name": "ops-cluster",
  "type": "cluster",
  "agents": [
    {"role": "monitor", "count": 1},
    {"role": "coordinator", "count": 1},
    {"role": "reporter", "count": 1}
  ],
  "strategy": "always-on"
}
```

## Deployment Flow

```
/formation deploy tdd-squadron
    │
    ▼
┌─────────────┐
│ Validate     │ Check agent availability, resource limits
│ Config       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Provision    │ Allocate resources, register with APM
│ Agents       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Wire         │ Establish communication channels
│ Connections  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Activate     │ Start agents, begin execution
│ Formation    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Monitor &    │ Track health, report to APM
│ Report       │
└─────────────┘
```

## APM Integration

Formations report to CCEM APM at `http://localhost:3031`:
- Formation topology visible on dashboard
- Agent health metrics per formation
- Hierarchical tree visualization
- Real-time status updates via WebSocket

## Commands

| Command | Description |
|---------|-------------|
| `/formation deploy <name>` | Deploy a named formation |
| `/formation show` | Display current formation tree |
| `/formation status` | Health check all formations |
| `/formation refactor` | Restructure formation |
| `/formation apm` | Open APM with formation view |
| `/upm formation deploy` | Deploy via UPM orchestrator |
| `/upm formation show` | Show via UPM |
| `/upm formation status` | Status via UPM |

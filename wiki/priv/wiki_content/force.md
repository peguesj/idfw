<!-- section: Framework -->
# FORCE Framework

FORCE (Framework for Orchestrated Reliable Code Evolution) provides governance, validation, and tooling for development workflows.

## Structure

```
.force/
├── tools/          # 42+ tool definitions
├── constraints/    # Constraint configurations
├── patterns/       # Pattern definitions
├── governance/     # Policy enforcement
└── collections/    # Tool collections
```

## Tool Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Analysis | 12 | Code analysis, metrics, complexity |
| Generation | 8 | Code generation, scaffolding |
| Validation | 10 | Schema validation, lint, type check |
| Monitoring | 6 | Performance, health, telemetry |
| Deployment | 6 | Build, deploy, release |

## Validation Results

All 68 FORCE validations pass:
- Tool category enum compliance
- Sequential strategy stubs resolved
- Constraint ID format (`CONST-XXX`)
- Pattern ID format compliance
- Governance enforcement levels valid
- No placeholder stubs remaining

## Agents

Five specialized agents from Dev Sentinel:

- **CDIA** - Continuous Development Intelligence Agent
- **RDIA** - Runtime Development Intelligence Agent
- **SAA** - Static Analysis Agent
- **VCLA** - Version Control Lifecycle Agent
- **VCMA** - Version Control Management Agent

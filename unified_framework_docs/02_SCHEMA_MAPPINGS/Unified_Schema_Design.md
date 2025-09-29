# Unified Schema Design

## Overview

This document outlines the unified schema system that bridges IDFW and Dev Sentinel schemas, providing a cohesive validation and type system for the integrated framework.

## Schema Architecture

### 1. Namespace Organization

```
unified-framework/
├── idfw/              # IDFW schemas
│   ├── documents/
│   ├── diagrams/
│   ├── variables/
│   └── projects/
├── force/             # Force tool schemas
│   ├── tools/
│   ├── patterns/
│   ├── constraints/
│   └── governance/
├── agents/            # Agent schemas
│   ├── tasks/
│   ├── messages/
│   └── states/
└── unified/           # Unified extensions
    ├── commands/
    ├── workflows/
    └── integrations/
```

### 2. Schema Version Alignment

Standardizing on JSON Schema draft/2020-12:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://unified-framework.dev/schemas/base",
  "title": "Unified Base Schema",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "namespace": {
      "enum": ["idfw", "force", "agents", "unified"]
    }
  }
}
```

## Core Schema Definitions

### 1. Unified Command Schema

Combines YUNG commands with IDFW actions:

```json
{
  "$id": "unified:command",
  "type": "object",
  "required": ["type", "command"],
  "properties": {
    "type": {
      "enum": ["yung", "idfw", "unified"]
    },
    "command": {
      "type": "string"
    },
    "parameters": {
      "type": "object"
    },
    "context": {
      "$ref": "#/$defs/ExecutionContext"
    }
  },
  "$defs": {
    "ExecutionContext": {
      "type": "object",
      "properties": {
        "project_id": {"type": "string"},
        "agent_id": {"type": "string"},
        "variables": {"type": "object"},
        "state": {"type": "object"}
      }
    }
  }
}
```

### 2. Unified Tool Schema

Merges Force tools with IDFW actions:

```json
{
  "$id": "unified:tool",
  "type": "object",
  "required": ["id", "name", "category", "execution"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*$"
    },
    "name": {
      "type": "string"
    },
    "category": {
      "enum": [
        "git", "project", "documentation", "system",
        "testing", "infrastructure", "idfw", "unified"
      ]
    },
    "source": {
      "enum": ["force", "idfw", "extension"]
    },
    "parameters": {
      "$ref": "#/$defs/ParameterSchema"
    },
    "execution": {
      "$ref": "#/$defs/ExecutionSchema"
    }
  },
  "$defs": {
    "ParameterSchema": {
      "type": "object",
      "patternProperties": {
        "^[a-zA-Z][a-zA-Z0-9_]*$": {
          "type": "object",
          "properties": {
            "type": {
              "enum": [
                "string", "number", "boolean", "array",
                "object", "file_path", "directory_path"
              ]
            },
            "required": {"type": "boolean"},
            "default": {},
            "validation": {"type": "object"}
          }
        }
      }
    },
    "ExecutionSchema": {
      "type": "object",
      "properties": {
        "strategy": {
          "enum": ["sequential", "parallel", "conditional"]
        },
        "handler": {"type": "string"},
        "timeout": {"type": "number"},
        "retries": {"type": "integer"}
      }
    }
  }
}
```

### 3. Unified State Schema

Combines IDFW variables with agent states:

```json
{
  "$id": "unified:state",
  "type": "object",
  "properties": {
    "immutable": {
      "type": "object",
      "description": "IDFW immutable variables",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "value": {},
          "type": {"type": "string"},
          "source": {"enum": ["idfw", "config", "default"]},
          "timestamp": {"type": "string", "format": "date-time"}
        }
      }
    },
    "mutable": {
      "type": "object",
      "description": "Runtime state variables",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "value": {},
          "type": {"type": "string"},
          "modified": {"type": "string", "format": "date-time"},
          "modified_by": {"type": "string"}
        }
      }
    },
    "agent_states": {
      "type": "object",
      "description": "Agent-specific states",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "status": {
            "enum": ["idle", "running", "completed", "failed"]
          },
          "context": {"type": "object"},
          "history": {"type": "array"}
        }
      }
    }
  }
}
```

## Schema Mapping Tables

### IDFW to Force Mappings

| IDFW Schema | Force Equivalent | Mapping Strategy |
|-------------|------------------|------------------|
| Document | Tool Output | Convert doc to tool result |
| Diagram | Tool Output | Diagram as tool artifact |
| Variable | Parameter | Variable as tool parameter |
| Project | Workflow | Project as workflow definition |
| Action | Tool | Action wrapped as tool |

### Force to IDFW Mappings

| Force Schema | IDFW Equivalent | Mapping Strategy |
|--------------|-----------------|------------------|
| Tool | Action | Tool exposed as action |
| Pattern | Project Template | Pattern as project type |
| Constraint | Validation Rule | Constraint as validator |
| Governance | Document | Governance as doc type |

## Schema Conversion Functions

### 1. IDFW Document to Force Tool Output

```python
def convert_idfw_doc_to_tool_output(doc: IDFWDocument) -> ForceToolOutput:
    return ForceToolOutput(
        success=True,
        result={
            "type": "document",
            "format": doc.format,
            "content": doc.content,
            "metadata": {
                "id": doc.id,
                "version": doc.version,
                "created": doc.created,
                "schema": f"idfw:{doc.schema_type}"
            }
        },
        execution_time=0,
        tool_id=f"idfw_doc_{doc.type}"
    )
```

### 2. Force Tool to IDFW Action

```python
def convert_force_tool_to_idfw_action(tool: ForceTool) -> IDFWAction:
    return IDFWAction(
        id=tool.id,
        name=tool.name,
        type="external_tool",
        parameters=[
            IDFWParameter(
                name=name,
                type=param.type,
                required=param.required,
                default=param.default
            )
            for name, param in tool.parameters.items()
        ],
        execution={
            "handler": f"force.tools.{tool.category}.{tool.id}",
            "async": True
        }
    )
```

## Validation Strategy

### 1. Multi-Level Validation

```python
class UnifiedValidator:
    def validate(self, data: Any, schema_ref: str) -> ValidationResult:
        # Level 1: Schema validation
        schema_result = self.validate_schema(data, schema_ref)
        if not schema_result.valid:
            return schema_result

        # Level 2: Business rules
        rules_result = self.validate_business_rules(data, schema_ref)
        if not rules_result.valid:
            return rules_result

        # Level 3: Cross-reference validation
        xref_result = self.validate_cross_references(data, schema_ref)
        return xref_result
```

### 2. Schema Evolution Support

```python
class SchemaEvolution:
    def migrate(self, data: Any, from_version: str, to_version: str):
        migrations = self.get_migration_path(from_version, to_version)

        for migration in migrations:
            data = migration.apply(data)

        return data
```

## Type System Integration

### 1. Unified Type Definitions

```python
from typing import Union, TypeVar, Generic
from pydantic import BaseModel

# Base types
IDFWType = TypeVar('IDFWType')
ForceType = TypeVar('ForceType')
UnifiedType = Union[IDFWType, ForceType]

class UnifiedModel(BaseModel, Generic[UnifiedType]):
    """Base model for unified types"""
    value: UnifiedType
    source: str  # 'idfw' or 'force'
    schema_ref: str

    def to_idfw(self) -> IDFWType:
        """Convert to IDFW type"""
        if self.source == 'idfw':
            return self.value
        return self.convert_to_idfw()

    def to_force(self) -> ForceType:
        """Convert to Force type"""
        if self.source == 'force':
            return self.value
        return self.convert_to_force()
```

### 2. Type Mappings

| IDFW Type | Force Type | Unified Type | Conversion |
|-----------|------------|--------------|------------|
| Document | ToolOutput | UnifiedArtifact | Bidirectional |
| Variable | Parameter | UnifiedValue | Bidirectional |
| Diagram | Artifact | UnifiedDiagram | Bidirectional |
| Project | Workflow | UnifiedProject | Bidirectional |

## Schema Registry

### 1. Registry Structure

```python
class UnifiedSchemaRegistry:
    def __init__(self):
        self.schemas = {
            'idfw': {},
            'force': {},
            'unified': {}
        }
        self.converters = {}
        self.validators = {}

    def register_schema(self, schema: Dict, namespace: str):
        schema_id = schema.get('$id')
        self.schemas[namespace][schema_id] = schema

        # Register associated converter and validator
        self.register_converter(schema_id)
        self.register_validator(schema_id)
```

### 2. Schema Discovery

```python
class SchemaDiscovery:
    def discover_schemas(self, path: str):
        """Discover and register all schemas in a directory"""
        for schema_file in Path(path).glob('**/*.json'):
            schema = json.load(schema_file.open())
            namespace = self.determine_namespace(schema)
            self.registry.register_schema(schema, namespace)
```

## Benefits

1. **Unified Validation**: Single validation framework for both systems
2. **Type Safety**: Strong typing with conversion support
3. **Extensibility**: Easy to add new schemas and types
4. **Backward Compatibility**: Migration support for schema evolution
5. **Performance**: Caching and optimized validation

---

*Document Version: 1.0.0*
*Date: 2025-09-29*
*Status: Design Complete*
# IDCMD: IDEA Command Definitions

## Introduction
The **IDCMD** object encapsulates a structured reference for all commands used within an IDEA Framework project. Derived from the METRICS implementation, this object defines the commands, arguments, and usage patterns for interacting with an IDEA-based interpreter. It ensures consistency, extensibility, and ease of use across all projects leveraging IDEA.

---

## 1. Purpose
The IDCMD object provides:
1. **Standardization** of all commands within a framework project.
2. **Documentation** for developers and contributors.
3. **Schema Validation** to ensure commands are syntactically and semantically correct.
4. **Object References** for integration into related IDEA Framework components.

---

## 2. Command Object Structure

### High-Level Schema
The IDCMD schema defines the structure for each command, including its arguments, accepted values, and documentation.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IDCMD Schema",
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "The name of the command."
    },
    "shortname": {
      "type": "string",
      "description": "A short alias for the command."
    },
    "arguments": {
      "type": "array",
      "description": "List of arguments for the command.",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "The name of the argument."
          },
          "required": {
            "type": "boolean",
            "description": "Whether the argument is required."
          },
          "type": {
            "type": "string",
            "description": "The data type of the argument (e.g., string, boolean, integer)."
          },
          "description": {
            "type": "string",
            "description": "Description of the argument."
          },
          "default": {
            "type": "string",
            "description": "Default value if not provided."
          }
        },
        "required": ["name", "type"]
      }
    },
    "description": {
      "type": "string",
      "description": "A detailed description of what the command does."
    }
  },
  "required": ["command", "arguments", "description"]
}
```

---

## 3. Example Commands
Below are examples of how the IDCMD object is applied within the METRICS Framework:

### Command: `init`
```json
{
  "command": "init",
  "shortname": "initialize",
  "arguments": [
    {
      "name": "project",
      "type": "string",
      "required": true,
      "description": "The name of the project to initialize."
    },
    {
      "name": "discovery-rounds",
      "type": "integer",
      "required": false,
      "default": 1,
      "description": "Number of discovery rounds for initial setup."
    },
    {
      "name": "default-format",
      "type": "string",
      "required": false,
      "default": "md",
      "description": "Default file format for generated files."
    }
  ],
  "description": "Initializes an IDCMD object within the existing IDFW object, or provides it as additional context if the command is used to pipe into an IDEA prompt"
}
```

### Command: `set-versioning`
```json
{
  "command": "set-versioning",
  "shortname": "set-v",
  "arguments": [
    {
      "name": "scheme",
      "type": "string",
      "required": true,
      "description": "The versioning scheme to use (e.g., i++mm/i++mj)."
    },
    {
      "name": "enforce-semver",
      "type": "boolean",
      "required": false,
      "default": true,
      "description": "Whether to enforce semantic versioning rules."
    },
    {
      "name": "project-name",
      "type": "string",
      "required": true,
      "description": "The name of the project for which versioning is set."
    }
  ],
  "description": "Defines the versioning scheme and rules for a project."
}
```

---

## 4. Documentation for Developers

### Command Structure
1. **Command Name:** The primary identifier for the command.
2. **Shortname:** A concise alias for shorthand usage.
3. **Arguments:**
   - `name`: The argument’s name.
   - `required`: Whether the argument is mandatory.
   - `type`: The expected data type.
   - `description`: Explains the purpose of the argument.
   - `default`: Optional default value.
4. **Description:** Detailed explanation of the command’s functionality.

### Command Listing
The full list of commands should be maintained in the project root under `IDCMD.json`.

---

## 5. Object Reference
The IDCMD object integrates with:
1. **IDPG (Project Generator):** Ensures commands are valid during project creation.
2. **IDFPJ (Framework Project JSON):** Maps commands to framework modules and workflows.
3. **IDFW (Framework Workflows):** Uses IDCMD as a reference for workflow definitions.

---

## 6. Example Usage
**Workflow Integration:**
```plaintext
init --project "METRICS" --discovery-rounds 3 --default-format "md"
set-versioning --scheme "i++mm/i++mj" --enforce-semver true --project-name "METRICS"
```
**Validation:**
Each command is validated against the IDCMD schema to ensure compliance.


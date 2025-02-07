# IDPG - Idea Framework Project Generator

Doc ID: IDPG  
Version: 0.2.0  
Revision: _a1  

## Version History

| Version | Revision | Date       | Change Description                                                  |
| ------- | -------- | ---------- | ------------------------------------------------------------------- |
| 0.1.0   | _a1      | 2025-01-01 | Initial addition of IDPG version control based on HISTORY.md context |
| 0.2.0   | _a1      | 2025-02-01 | Incremented version to reflect updates based on HISTORY.md context   |
| 2.0.0   | _b1      | 2025-06-15 | Major update with schema integration and documentation enhancements |
| 2.1.0   | _c1      | 2025-07-10 | Added dynamic update dependencies and enhanced project actions      |

Manages prompt-based generation steps.

## 1. Purpose
Automates artifact generation using prompt engineering and references from IDFW.

## 2. Schema & Structure
- `promptId`: Unique identifier for the prompt.
- `promptText`: The actual prompt to be processed.
- `desiredOutputType`: Specifies the type of output, e.g., "diagram", "document".
- `contextRefs`: References to existing documents or schemas.
- `generationActions`: Steps for building or updating artifacts

## 3. Example Input/Output
### 3.1 Input Prompt
```json
{
  "generatedArtifacts": [
    {
      "artifactId": "erd01",
      "status": "generated",
      "content": "ERD Diagram JSON or UML snippet..."
    },
    {
      "artifactId": "hplot",
      "status": "updated",
      "content": "HyperPlot representation with the new data from erd01"
    }
  ]
}

## 4. Recursive & Asynchronous Updates
If updateDependencies.autoRegenOnChange is true, IDPG automatically regenerates documents or diagrams whenever their linked data changes. This ensures referential integrity across all project actions.



**Update Log:** Updated for schema compatibility and workflow alignment.
# Diagrams for Liightbulb Package

This document contains all the diagrams for the `liightbulb` package, created using the IDEA Framework logic.

## Table of Contents
1. [System Context Diagram](#system-context-diagram)
2. [Component Diagram](#component-diagram)
3. [Entity-Relationship Diagram](#entity-relationship-diagram)
4. [User Flow Diagram](#user-flow-diagram)
5. [Security & Threat Model](#security--threat-model)
6. [Incident Response Flow](#incident-response-flow)
7. [Business Continuity Process](#business-continuity-process)
8. [UX Flow & Wireframe](#ux-flow--wireframe)
9. [HyperPlot Multi-Axis Diagram](#hyperplot-multi-axis-diagram)
10. [OpenAI Integration Flow](#openai-integration-flow)
11. [OpenAI API Interaction Sequence](#openai-api-interaction-sequence)
12. [OpenAI Component Hierarchy](#openai-component-hierarchy)
13. [OpenAI Architecture Overview](#openai-architecture-overview)

---

## 1. System Context Diagram
```plantuml
@startuml
title System Context Diagram for Liightbulb Package
actor User
package "Liightbulb Package" {
  [IDEA Framework] --> [OpenAI API]
  [IDEA Framework] --> [Documents]
  [IDEA Framework] --> [Diagrams]
  [IDEA Framework] --> [Variables]
  [IDEA Framework] --> [Project Actions]
}
User --> [IDEA Framework]
@enduml
```

## 2. Component Diagram
```plantuml
@startuml
title Component Diagram for Liightbulb Package
package "Liightbulb Package" {
  [Core Functions] --> [IDEA Framework Integration]
  [IDEA Framework Integration] --> [OpenAI API Integration]
  [Core Functions] --> [Validation Functions]
  [IDEA Framework Integration] --> [Document Management]
  [IDEA Framework Integration] --> [Diagram Management]
  [IDEA Framework Integration] --> [Variable Management]
  [IDEA Framework Integration] --> [Project Action Management]
}
@enduml
```

## 3. Entity-Relationship Diagram
```mermaid
erDiagram
    Project {
        string projectId
        string projectName
        string description
        datetime dateCreated
        datetime dateUpdated
    }
    Document {
        string docId
        string title
        string purpose
        string ownerTeam
        string version
        string revision
        datetime dateCreated
        datetime dateUpdated
    }
    Diagram {
        string diagId
        string diagramName
        string purpose
        string typeTool
        string diagramType
        string generatorLibId
        string version
        string revision
        datetime dateCreated
        datetime dateUpdated
    }
    Variable {
        string varId
        string varName
        string varType
        string varValue
        datetime dateCreated
        datetime dateUpdated
    }
    ProjectAction {
        string actionId
        string actionType
        string artifactId
        string inputRefs
        string actionParams
        datetime dateCreated
        datetime dateUpdated
    }
    Project ||--|| Document : "Contains"
    Project ||--|| Diagram : "Contains"
    Project ||--|| Variable : "Contains"
    Project ||--|| ProjectAction : "Contains"
    Document ||--|| Variable : "References"
    Diagram ||--|| Variable : "References"
    ProjectAction ||--|| Variable : "References"
```

## 4. User Flow Diagram
```mermaid
flowchart TD
    Start --> DefineIDFW
    DefineIDFW --> InitializeVariables
    InitializeVariables --> GenerateDocs
    InitializeVariables --> GenerateDiagrams
    GenerateDocs --> ValidateDocs
    GenerateDiagrams --> ValidateDiagrams
    ValidateDocs -->|Valid| StoreDocs
    ValidateDocs -->|Invalid| FeedbackLoopDocs
    ValidateDiagrams -->|Valid| StoreDiagrams
    ValidateDiagrams -->|Invalid| FeedbackLoopDiagrams
    StoreDocs --> Finalize
    StoreDiagrams --> Finalize
    FeedbackLoopDocs --> DefineIDFW
    FeedbackLoopDiagrams --> DefineIDFW
    Finalize --> End
```

## 5. Security & Threat Model
```plantuml
@startuml
title Security & Threat Model for Liightbulb Package
actor User
package "Liightbulb Package" {
  [IDEA Framework] --> [OpenAI API]
  [IDEA Framework] --> [Documents]
  [IDEA Framework] --> [Diagrams]
  [IDEA Framework] --> [Variables]
  [IDEA Framework] --> [Project Actions]
}
User --> [IDEA Framework]
@enduml
```

## 6. Incident Response Flow
```mermaid
flowchart TD
    Incident --> Identify
    Identify --> Contain
    Contain --> Eradicate
    Eradicate --> Recover
    Recover --> LessonsLearned
    LessonsLearned --> Incident
```

## 7. Business Continuity Process
```mermaid
flowchart TD
    Start --> AssessImpact
    AssessImpact --> DevelopPlan
    DevelopPlan --> ImplementPlan
    ImplementPlan --> TestPlan
    TestPlan --> ReviewPlan
    ReviewPlan --> UpdatePlan
```

## 8. UX Flow & Wireframe
```mermaid
flowchart TD
    Start --> DefineUX
    DefineUX --> CreateWireframe
    CreateWireframe --> ValidateWireframe
    ValidateWireframe -->|Valid| StoreWireframe
    ValidateWireframe -->|Invalid| FeedbackLoopWireframe
    StoreWireframe --> Finalize
    FeedbackLoopWireframe --> DefineUX
    Finalize --> End
```

## 9. HyperPlot Multi-Axis Diagram
```mermaid
flowchart TD
    Start --> DefineAxes
    DefineAxes --> PlotData
    PlotData --> ValidatePlot
    ValidatePlot -->|Valid| StorePlot
    ValidatePlot -->|Invalid| FeedbackLoopPlot
    StorePlot --> Finalize
    FeedbackLoopPlot --> DefineAxes
    Finalize --> End
```

## 10. OpenAI Integration Flow
```mermaid
flowchart TD
    User -->|Provides Prompt| IDPG
    IDPG -->|Retrieves Config| IDPC
    IDPC -->|Checks API Keys| OpenAI
    OpenAI -->|Generates Idea| IDPG
    IDPG -->|Updates Project| IDFW
    IDFW -->|Stores Artifacts| Logger
    Logger -->|Logs Actions| IDFW
    IDFW -->|Final Output| User
```

## 11. OpenAI API Interaction Sequence
```plantuml
@startuml
title OpenAI API Interaction Sequence
actor User
participant IDPG as "IDPG (Prompt & Generation)"
participant IDPC as "IDPC (Project Config)"
participant OpenAI as "OpenAI API"
participant IDFW as "IDFW (Master Spec & Actions)"
participant Logger as "Logger (Activity Logging)"

User -> IDPG: Provide Prompt
IDPG -> IDPC: Retrieve Config
IDPC -> OpenAI: Check API Keys
OpenAI -> IDPG: Valid API Key
IDPG -> OpenAI: Generate Idea
OpenAI -> IDPG: Return Idea
IDPG -> IDFW: Update Project
IDFW -> Logger: Log Action
Logger -> IDFW: Confirm Log
IDFW -> User: Provide Final Output
@enduml
```

## 12. OpenAI Component Hierarchy
```plantuml
@startuml
title OpenAI Component Hierarchy
package "OpenAI Integration" {
  [OpenAI Client] --> [Chat Completion]
  [OpenAI Client] --> [Embeddings]
  [OpenAI Client] --> [Files]
  [OpenAI Client] --> [Images]
  [OpenAI Client] --> [Audio]
  [OpenAI Client] --> [Moderations]
  [OpenAI Client] --> [Models]
  [OpenAI Client] --> [FineTuning]
  [OpenAI Client] --> [Beta Features]
}
@enduml
```

## 13. OpenAI Architecture Overview
```plantuml
@startuml
title OpenAI Architecture Overview
actor User
package "Liightbulb Package" {
  [IDEA Framework] --> [OpenAI API]
  [IDEA Framework] --> [Documents]
  [IDEA Framework] --> [Diagrams]
  [IDEA Framework] --> [Variables]
  [IDEA Framework] --> [Project Actions]
}
package "OpenAI API" {
  [Chat Completion]
  [Embeddings]
  [Files]
  [Images]
  [Audio]
  [Moderations]
  [Models]
  [FineTuning]
  [Beta Features]
}
User --> [IDEA Framework]
[IDEA Framework] --> [OpenAI API]
@enduml
```

---

**Document Version**: 1.0.0  
**Publication Date**: 2025-01-01  
**IDEA Framework Version**: 2.0.0  
**Components Used**: IDFW, SDREF, DDD

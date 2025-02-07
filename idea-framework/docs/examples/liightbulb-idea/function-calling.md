# Function Calling with OpenAI for Liightbulb Package

## Version: 1.3.0  
## Revision: _a1  
## Date: 2025-02-07  

---

## 1. Introduction
This document provides a detailed guide on using function calling with OpenAI for the `liightbulb` package. Function calling can increase efficiency and preserve memory by allowing the model to call predefined functions and return structured outputs.

## 2. Setup Instructions
### 2.1 Prerequisites
- Python 3.7 or higher
- OpenAI Python SDK
- IDEA Framework components

### 2.2 Installation
1. **Install OpenAI Python SDK**:
    ```bash
    pip install openai
    ```

2. **Set up Environment Variables**:
    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    ```

## 3. Example Code
### 3.1 Initializing OpenAI Client
```python
import openai
import os

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
```

### 3.2 Defining Functions
```python
def get_weather(location):
    # Example function to get weather information
    return {
        "location": location,
        "temperature": "22°C",
        "condition": "Sunny"
    }

functions = [{
    "name": "get_weather",
    "description": "Get current temperature for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and country e.g. Bogotá, Colombia"
            }
        },
        "required": ["location"]
    }
}]
```

### 3.3 Using Function Calling
```python
def call_function(prompt, function_name, function_params):
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=150,
        functions=functions,
        function_call={
            "name": function_name,
            "parameters": function_params
        }
    )
    return response.choices[0].text.strip()

# Example usage
prompt = "What is the weather like in Paris today?"
function_name = "get_weather"
function_params = {"location": "Paris, France"}
result = call_function(prompt, function_name, function_params)
print(f"Function Call Result: {result}")
```

## 4. Best Practices
### 4.1 Managing API Keys
- Store API keys securely using environment variables or a secrets manager.
- Avoid hardcoding API keys in your source code.

### 4.2 Handling API Rate Limits
- Implement retry logic to handle rate limits.
- Monitor your usage and adjust your plan as needed.

### 4.3 Optimizing Token Usage
- Use concise prompts to minimize token usage.
- Set appropriate `max_tokens` to control the length of responses.

## 5. Integration with IDEA Framework
### 5.1 Creating a New Project
```python
from idea_framework import Project

# Initialize a new project
project = Project(project_id="proj-001", project_name="Liightbulb Project", description="A project to integrate OpenAI with IDEA Framework")

# Add documents, diagrams, and variables as needed
project.add_document(Document(doc_id="doc-001", title="Project Plan", purpose="Outline the project plan"))
project.add_diagram(Diagram(diag_id="diag-001", diagram_name="System Architecture", purpose="Illustrate the system architecture"))
project.add_variable(Variable(var_id="var-001", var_name="API_KEY", var_type="string", var_value=os.getenv('OPENAI_API_KEY')))
```

### 5.2 Using Function Calling within the Project
```python
# Define functions and add them to the project
functions = [{
    "name": "get_weather",
    "description": "Get current temperature for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and country e.g. Bogotá, Colombia"
            }
        },
        "required": ["location"]
    }
}]
project.add_document(Document(doc_id="doc-002", title="Function Definitions", purpose="Store function definitions", content=functions))

# Call a function and add the result to the project
prompt = "What is the weather like in Paris today?"
function_name = "get_weather"
function_params = {"location": "Paris, France"}
result = call_function(prompt, function_name, function_params)
project.add_document(Document(doc_id="doc-003", title="Function Call Result", purpose="Store the result of the function call", content=result))
```

## 6. Technical Diagrams
### 6.1 Component Diagram
```plantuml
@startuml
title Component Diagram for Liightbulb Package with Function Calling
package "Liightbulb Package" {
  [Core Functions] --> [IDEA Framework Integration]
  [IDEA Framework Integration] --> [OpenAI API Integration]
  [Core Functions] --> [Validation Functions]
  [IDEA Framework Integration] --> [Document Management]
  [IDEA Framework Integration] --> [Diagram Management]
  [IDEA Framework Integration] --> [Variable Management]
  [IDEA Framework Integration] --> [Project Action Management]
  [IDEA Framework Integration] --> [Function Calling]
}
@enduml
```

### 6.2 Entity-Relationship Diagram
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
    Function {
        string functionName
        string description
        object parameters
    }
    Project ||--|| Document : "Contains"
    Project ||--|| Diagram : "Contains"
    Project ||--|| Variable : "Contains"
    Project ||--|| ProjectAction : "Contains"
    Project ||--|| Function : "Contains"
    Document ||--|| Variable : "References"
    Diagram ||--|| Variable : "References"
    ProjectAction ||--|| Variable : "References"
    Function ||--|| Variable : "References"
```

### 6.3 OpenAI Integration Flow with Function Calling
```mermaid
flowchart TD
    User -->|Provides Prompt| IDPG
    IDPG -->|Retrieves Config| IDPC
    IDPC -->|Checks API Keys| OpenAI
    OpenAI -->|Generates Idea| IDPG
    IDPG -->|Calls Function| Function
    Function -->|Returns Result| IDPG
    IDPG -->|Updates Project| IDFW
    IDFW -->|Stores Artifacts| Logger
    Logger -->|Logs Actions| IDFW
    IDFW -->|Final Output| User
```

### 6.4 OpenAI API Interaction Sequence with Function Calling
```plantuml
@startuml
title OpenAI API Interaction Sequence with Function Calling
actor User
participant IDPG as "IDPG (Prompt & Generation)"
participant IDPC as "IDPC (Project Config)"
participant OpenAI as "OpenAI API"
participant Function as "Function"
participant IDFW as "IDFW (Master Spec & Actions)"
participant Logger as "Logger (Activity Logging)"

User -> IDPG: Provide Prompt
IDPG -> IDPC: Retrieve Config
IDPC -> OpenAI: Check API Keys
OpenAI -> IDPG: Valid API Key
IDPG -> OpenAI: Generate Idea
OpenAI -> IDPG: Return Idea
IDPG -> Function: Call Function
Function -> IDPG: Return Result
IDPG -> IDFW: Update Project
IDFW -> Logger: Log Action
Logger -> IDFW: Confirm Log
IDFW -> User: Provide Final Output
@enduml
```

### 6.5 OpenAI Component Hierarchy with Function Calling
```plantuml
@startuml
title OpenAI Component Hierarchy with Function Calling
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
  [OpenAI Client] --> [Function Calling]
}
@enduml
```

### 6.6 OpenAI Architecture Overview with Function Calling
```plantuml
@startuml
title OpenAI Architecture Overview with Function Calling
actor User
package "Liightbulb Package" {
  [IDEA Framework] --> [OpenAI API]
  [IDEA Framework] --> [Documents]
  [IDEA Framework] --> [Diagrams]
  [IDEA Framework] --> [Variables]
  [IDEA Framework] --> [Project Actions]
  [IDEA Framework] --> [Function Calling]
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
  [Function Calling]
}
User --> [IDEA Framework]
[IDEA Framework] --> [OpenAI API]
@enduml
```

---

**Document Version**: 1.3.0  
**Publication Date**: 2025-02-07  
**IDEA Framework Version**: 2.3.0  
**Components Used**: IDFW, SDREF, DDD

# OpenAI Integration with Python for Liightbulb Package

## Version: 1.3.0  
## Revision: _a1  
## Date: 2025-02-07  

---

## 1. Introduction
This document provides a detailed guide on integrating OpenAI with Python for the `liightbulb` package. It includes setup instructions, example code, and best practices for using OpenAI's API within the IDEA framework.

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

### 3.2 Generating an Idea
```python
def generate_idea(prompt):
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Example usage
prompt = "Generate an innovative idea for a mobile app."
idea = generate_idea(prompt)
print(f"Generated Idea: {idea}")
```

### 3.3 Evaluating an Idea
```python
def evaluate_idea(idea):
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Evaluate the following idea: {idea}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Example usage
evaluation = evaluate_idea(idea)
print(f"Evaluation: {evaluation}")
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

### 5.2 Generating and Evaluating Ideas within the Project
```python
# Generate an idea and add it to the project
idea = generate_idea("Generate an innovative idea for a mobile app.")
project.add_document(Document(doc_id="doc-002", title="Generated Idea", purpose="Store the generated idea", content=idea))

# Evaluate the idea and add the evaluation to the project
evaluation = evaluate_idea(idea)
project.add_document(Document(doc_id="doc-003", title="Idea Evaluation", purpose="Store the evaluation of the idea", content=evaluation))
```

---

**Document Version**: 1.3.0  
**Publication Date**: 2025-02-07  
**IDEA Framework Version**: 2.3.0  
**Components Used**: IDFW, SDREF, DDD
# Liightbulb IDEA Framework Planning

This folder contains the planning documents for the `liightbulb` package, created using the IDEA Framework logic. The documents include high-level overviews, core concepts, project actions, and iterative updates for the development of the `liightbulb` package.

## Table of Contents
1. [High-Level Overview](#high-level-overview)
2. [Core Concepts](#core-concepts)
3. [Project Actions & Iterative Updates](#project-actions--iterative-updates)
4. [Usage Scenarios](#usage-scenarios)
5. [Technical Details](#technical-details)
6. [Diagrams](#diagrams)
7. [Functions Overview](#functions-overview)
8. [Reasoning Implementation](#reasoning-implementation)
9. [Function Calling](#function-calling)
10. [Integration Details](#integration-details)
11. [IF2IF: Using IDEA Framework to Generate an Implementation of IDEA Framework](#if2if-using-idea-framework-to-generate-an-implementation-of-idea-framework)
12. [References to All Schemas & SDREF](#references-to-all-schemas--sdref)
13. [Version Control & Document Assets](#version-control--document-assets)

---

## 1. High-Level Overview
The **Liightbulb IDEA Framework** is a comprehensive specification designed to define, structure, and maintain the various components of the `liightbulb` package, including documents, diagrams, variables, and references. By encapsulating the project's scope within the IDEA Framework object, the framework ensures efficient memory usage and optimal token management when interacting with Large Language Models (LLMs).

## 2. Core Concepts
- **Documents**: Structured textual artifacts such as BRD (Business Requirements Document) and FRS (Functional Requirements Specification).
- **Diagrams**: Visual representations like UML, BPMN, and Mermaid diagrams that illustrate system architecture and workflows.
- **Variables**: Key-value pairs that hold runtime or build-time data essential for project operations. The variables object is divided into immutable variables and mutable variables:
  - **Immutable Variables**: Variables that are established at the initialization of the IDEA Framework object and remain constant throughout the project lifecycle.
  - **Mutable Variables**: Variables that can change based on use cases and project actions, retrieved by accessing collection arrays.
- **Project Actions**: Iterative processes for creating, updating, or removing artifacts within the project.

## 3. Project Actions & Iterative Updates
The IDEA Framework facilitates iterative processing of project components, ensuring each action maintains referential integrity through validation functions.

## 4. Usage Scenarios
The IDEA Framework supports a range of project complexities, from single MVPs with minimal documentation to extensive enterprise projects requiring compliance and multi-axis strategies.

## 5. Technical Details
The technical details section provides in-depth information on the implementation of the `liightbulb` package. It covers the architecture, design patterns, and integration points with external systems such as the OpenAI API. This section is crucial for developers and engineers who need to understand the inner workings of the package and how to extend or modify it.

Refer to the [Technical Reference](./technical-reference.md) for detailed technical information on the implementation of the `liightbulb` package.

## 6. Diagrams
The diagrams section includes various visual representations that illustrate the system architecture, workflows, and data models of the `liightbulb` package. These diagrams help in understanding the relationships between different components and the flow of data within the system. They are essential for both technical and non-technical stakeholders to grasp the overall structure and functionality of the package.

Refer to the [Diagrams](./diagrams.md) document for all the diagrams related to the `liightbulb` package.

## 7. Functions Overview
The functions overview section provides a detailed description of the core functions within the `liightbulb` package. It includes information on the inputs, outputs, and the role of each function in the overall system. This section is particularly useful for developers who need to understand how to use and integrate these functions into their applications.

### Key Functions:
- `create_project_component`: Creates a new project component.
- `update_project_component`: Updates an existing project component.
- `remove_project_component`: Removes a project component.
- `generate_idea`: Generates an idea using the OpenAI API.
- `evaluate_idea`: Evaluates an idea using the OpenAI API.
- `create_document`: Creates a document using the IDEA Framework.
- `create_diagram`: Creates a diagram using the IDEA Framework.
- `manage_variables`: Manages variables using the IDEA Framework.

Refer to the [Functions Overview](./functions-overview.md) document for an overview of the functions within the `liightbulb` package.

## 8. Reasoning Implementation
The reasoning implementation section explains how reasoning is applied when iterating and improving upon an idea within the `liightbulb` package. It includes steps for contextual analysis, feasibility evaluation, impact assessment, optimization suggestions, and iterative refinement. This section is essential for ensuring that ideas are thoroughly evaluated and optimized before implementation.

### Key Steps:
1. **Contextual Analysis**: Analyze the context and requirements of the idea.
2. **Feasibility Evaluation**: Evaluate the feasibility of the idea using predefined criteria.
3. **Impact Assessment**: Assess the potential impact of the idea on the project.
4. **Optimization Suggestions**: Generate suggestions for optimizing the idea.
5. **Iterative Refinement**: Refine the idea based on the reasoning outcomes.

Refer to the [Reasoning Implementation](./reasoning-implementation.md) document for details on the implementation of reasoning when iterating and improving upon an idea.

## 9. Function Calling
The function calling section provides a detailed guide on using function calling with OpenAI in the `liightbulb` package. It includes setup instructions, example code, and best practices for defining and using functions. This section is crucial for developers who want to leverage the power of OpenAI's function calling capabilities to enhance their applications.

### Key Topics:
- **Setup Instructions**: Prerequisites and installation steps.
- **Example Code**: Initializing OpenAI client, defining functions, and using function calling.
- **Best Practices**: Managing API keys, handling API rate limits, and optimizing token usage.

Refer to the [Function Calling](./function-calling.md) document for a detailed guide on using function calling with OpenAI in the `liightbulb` package.

## 10. Integration Details
The integration details section provides comprehensive information on how the `liightbulb` package integrates with the OpenAI API and other external systems. It includes architectural diagrams, interaction sequences, and component hierarchies. This section is vital for understanding how different parts of the system work together and how to extend the integration with additional services.

### Key Topics:
- **Architectural Diagrams**: Visual representations of the system architecture.
- **Interaction Sequences**: Detailed sequences of interactions between components.
- **Component Hierarchies**: Hierarchical structure of components and their relationships.

Refer to the [Integration Details](./integration-details.md) document for detailed information on the integration of the OpenAI interface with the IDEA framework.

## 11. IF2IF: Using IDEA Framework to Generate an Implementation of IDEA Framework
The IDEA Framework can be used to generate an implementation of itself, demonstrating its recursive and self-referential capabilities. This process involves using the framework's components to create the necessary documents, diagrams, and project actions for the `liightbulb` package.

### Simulation Outline:
1. **Define Project Components**:
   - Create documents such as BRD, FRS, TAD, and SCD.
   - Generate diagrams like system context, component, and entity-relationship diagrams.
   - Define variables and project actions.

2. **Generate Initial Artifacts**:
   - Use the `generate_idea` function to create initial ideas for the project.
   - Create documents and diagrams based on these ideas.

3. **Iterative Refinement**:
   - Apply reasoning steps to evaluate and refine the generated artifacts.
   - Use the `evaluate_idea` function to assess the feasibility and impact of the ideas.
   - Generate optimization suggestions and iteratively refine the artifacts.

4. **Integration and Validation**:
   - Integrate the generated artifacts with the OpenAI API and other external systems.
   - Validate the artifacts using the framework's validation functions.

5. **Finalization**:
   - Store the validated artifacts and finalize the project components.
   - Document the version control and changes made during the process.

Refer to the [Complete Reference](./IDEA_Complete_Reference.md) document for a similar mention and detailed explanation of the IDEA Framework's capabilities.

## 12. References to All Schemas & SDREF
The IDEA Framework defers to separate schemas or documents for specific details:
- **IDFW Schema** for the structural definition
- **SDREF** for standard doc/diagram references
- **DDD** for default templates

## 13. Version Control & Document Assets
### VC Table for All Components

| **Doc/Asset**                 | **Version** | **Revision** | **Date**       | **Change Description**                                                                                                                       |
|-------------------------------|-------------|-------------:|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Liightbulb IDEA (This Document)** | 1.3.0       | _a1          | 2025-02-07    | Initial planning document for the `liightbulb` package using the IDEA Framework.                                                              |

### Versioning Practices
1. **Semantic Versioning**: For major and minor expansions.
2. **Revision Suffix**: For minor editorial or textual updates.
3. **Approval**: Each major or minor change must be documented in the table.

---

**Document Version**: 1.3.0  
**Publication Date**: 2025-02-07  
**IDEA Framework Version**: 2.0.0  
**Components Used**: 
- IDFW (2.3.0) [IDFW.json](./idref/IDFW.json)
- IDPG (1.0.0) [IDPG.json](./idref/IDPG.json)
- IDPC (1.0.0) [IDPC.json](./idref/IDPC.json)
- IDPJ (1.0.0) [IDPJ.json](./idref/IDPJ.json)
- IDDC (1.0.0) [IDDC.json](./idref/IDDC.json)
- IDDG (1.0.0) [IDDG.json](./idref/IDDG.json)
- IDDV (1.0.0) [IDDV.json](./idref/IDDV.json)

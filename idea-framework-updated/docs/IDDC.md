# IDDC - Idea Diagram Configuration

Follows IDDC.schema.json. This object defines how diagrams are generated and tracked.

// No changes required for version updates

## Key Fields

### diagId
- **Type**: string
- **Description**: Uniquely identifies the diagram configuration within the framework.

### diagramName
- **Type**: string
- **Description**: The name of the diagram to be generated.

### typeTool
- **Type**: string
- **Description**: The tool used for diagram generation (e.g., "PlantUML", "Mermaid").

### diagramType
- **Type**: string
- **Description**: The specific type of diagram (e.g., "sequence", "flowchart").

### generatorLibId
- **Type**: string
- **Description**: Identifier for the library or tool used to generate the diagram.

### purposeDescription
- **Type**: string
- **Description**: A brief description of the diagram’s purpose.

### relevantSection
- **Type**: string
- **Description**: The section of the documentation that the diagram pertains to.

### lastUpdated
- **Type**: string (date-time)
- **Description**: Timestamp of the last diagram update.

### diagramStatus
- **Type**: string
- **Description**: Current status of the diagram (e.g., "draft", "finalized").

## Usage Examples

### Example 1: Initial Diagram Configuration
```json
{
  "diagId": "SEQ001",
  "diagramName": "UserAuthenticationFlow",
  "typeTool": "PlantUML",
  "diagramType": "sequence",
  "generatorLibId": "gen-plantuml",
  "purposeDescription": "Illustrates the user authentication process.",
  "relevantSection": "3. Functional Requirements",
  "lastUpdated": "2025-02-01T12:00:00Z",
  "diagramStatus": "draft"
}
```

### Example 2: Finalizing a Diagram
```json
{
  "diagId": "SEQ001",
  "diagramStatus": "finalized",
  "lastUpdated": "2025-03-20T15:45:00Z"
}
```

## Integration with IDFW

The IDDC integrates with the IDFW by referencing the master schema and ensuring that all diagram configurations adhere to the defined structure and standards. Changes in the IDFW schemas will automatically affect the diagram configurations, ensuring consistency across the framework.

## Best Practices

- **Consistent Naming**: Ensure `diagId` values are unique and follow a consistent naming convention.
- **Version Tracking**: Regularly update the `lastUpdated` field to maintain version control.
- **Tool Selection**: Choose `typeTool` based on the diagram requirements and team familiarity.
- **Status Management**: Accurately reflect the diagram’s lifecycle stage using the `diagramStatus` field.

## Troubleshooting

- **Unsupported Tools**: Ensure that the `typeTool` specified is supported and properly integrated with the framework.
- **Diagram Errors**: Verify that the diagram definitions conform to the syntax and requirements of the chosen `typeTool`.
- **Reference Issues**: Make sure that the `relevantSection` accurately points to existing sections within the documentation.

## FAQs

**Q1: How do I add a new diagram configuration?**
- **A1**: Create a new entry in the `iddcs` array within the IDFW.schema.json, following the IDDC schema structure.

**Q2: Can I use multiple tools for the same diagram type?**
- **A2**: Yes, by specifying different `generatorLibId` values and ensuring each tool is configured correctly for the diagram type.
- **A2**: Yes, by specifying different `generatorLibId` values and ensuring each tool is configured correctly for the diagram type.



**Update Log:** Updated for schema compatibility and workflow alignment.
# IDDG - Idea Document Generator

Follows IDDG.schema.json. This object represents configuration for generating and maintaining a document’s lifecycle.

## Key Fields

### docId
- **Type**: string
- **Description**: Uniquely identifies the document generator within the framework.

### title
- **Type**: string
- **Description**: The name of the document to be generated.

### purpose
- **Type**: string
- **Description**: A brief description of what the document aims to achieve.

### ownerTeam
- **Type**: string
- **Description**: The team responsible for maintaining the document.

### references
- **Type**: array of strings
- **Description**: List of documents or schemas that this generator references.

### formatType
- **Type**: string
- **Description**: The format of the generated document (e.g., "Markdown", "HTML", "PDF").

### generatorId
- **Type**: string
- **Description**: Identifier for the generator tool or library used.

### contentRef
- **Type**: string
- **Description**: Reference to the content template or source.

### lastUpdated
- **Type**: string (date-time)
- **Description**: Timestamp of the last document update.

### status
- **Type**: string
- **Description**: Current status of the document (e.g., "draft", "published").

## Usage Examples

### Example 1: Initial Document Generation
```json
{
  "docId": "BP001",
  "title": "Business Plan",
  "purpose": "Outline the business strategy and financial projections.",
  "ownerTeam": "Business Development",
  "references": ["MarketAnalysis", "FinancialForecast"],
  "formatType": "Markdown",
  "generatorId": "gen-markdown",
  "contentRef": "templates/business_plan.md",
  "lastUpdated": "2025-02-01T12:00:00Z",
  "status": "draft"
}
```

### Example 2: Updating Document Status
```json
{
  "docId": "BP001",
  "status": "published",
  "lastUpdated": "2025-03-15T09:30:00Z"
}
```

## Integration with IDFW

The IDDG integrates with the IDFW by referencing the master schema and ensuring that all generated documents adhere to the defined structure and standards. Changes in the IDFW schemas will automatically propagate to the document generators, ensuring consistency across the framework.

## Best Practices

- **Consistent Naming**: Ensure `docId` values are unique and follow a consistent naming convention.
- **Version Tracking**: Regularly update the `lastUpdated` field to maintain version control.
- **Reference Management**: Keep the `references` array up-to-date to reflect any dependencies on other documents or schemas.
- **Status Updates**: Accurately reflect the document’s lifecycle stage using the `status` field.

## Troubleshooting

- **Missing References**: Ensure all references listed in the `references` field exist within the framework.
- **Generator Errors**: Verify that the `generatorId` corresponds to a valid generator tool and that `contentRef` points to an accessible template.
- **Format Issues**: Confirm that the `formatType` is supported by the generator and compatible with the intended use case.

## FAQs

**Q1: How do I add a new document generator?**
- **A1**: Create a new entry in the `iddgs` array within the IDFW.schema.json, following the IDDG schema structure.

**Q2: Can I use multiple generator tools for a single document?**
- **A2**: Yes, by specifying different `generatorId` values and ensuring that each generator handles a specific aspect of the document generation process.


**Update Log:** Updated for schema compatibility and workflow alignment.
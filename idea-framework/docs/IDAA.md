
# IDAA Reference Documentation

## Overview

The IDAA (Idea Framework) utilizes three primary objects to manage and structure project components:

- **Document**
- **Diagram**
- **Asset**

This documentation provides detailed information on each object, including their properties, usage instructions, validation rules, and examples. For schema definitions and additional context, refer to the [IDDA.schemas.json](../schemas/IDDA.schemas.json) file.

## Objects

### Document

Represents textual or structured documents essential to the project's requirements and specifications.

**Properties:**

- `docId` (string): Unique identifier for the document.
- `title` (string): Title of the document.
- `purpose` (string): Description of the document's purpose.
- `ownerTeam` (string): Team responsible for the document.
- `version` (string): Version of the document.
- `revision` (string): Revision identifier.
- `dateCreated` (string): Creation date in YYYY-MM-DD format.
- `dateUpdated` (string): Last update date in YYYY-MM-DD format.
- `references` (array): List of related document IDs.
- `formatType` (string): Format of the document (e.g., markdown).
- `tasks` (array): Tasks associated with the document.
- `variables` (object): Variables defined within the document.
- `instructions` (object): Instructions related to the document's structure.

**Usage Instructions:**

- Ensure each document has a unique `docId`.
- Populate the `references` array with relevant `docId`s to establish document relationships.
- Define variables that are pertinent to the document's content within the `variables` object.
- Provide clear instructions in the `instructions` object to guide content creation and formatting.

**Validation Rules:**

- All required properties (`docId`, `title`, `purpose`, `ownerTeam`) must be present.
- `dateCreated` and `dateUpdated` should follow the YYYY-MM-DD format.
- `version` should adhere to semantic versioning (e.g., "1.0.0").
- `formatType` must be a supported format (currently "markdown").

**Example:**


# IDPC - Idea Project Config

## 1. Purpose

Defines environment data, API keys, LLM configs, and optional projectActions for the broader IDEA Framework.

## 2. Config Fields

- `docId`, `version`, `revision`, `date`, `projectName`
- `apiKeys`: Storage for external service credentials
- `llmConfigs`: Model choices, temperature, topP, maxTokens
- `defaultGenerators`: Array of generators to use by default
- `typeTools`: Array of tool objects with optional `config`
- `environment`: Arbitrary environment keys/values
- `security`: Arbitrary security properties or flags
- `projectActions`: Iterative steps referencing relevant documents

## 4. Example Config

See `IDPC.schema.json`.

## 5. Additional Information

### 5.1 Security Policies

- **Data Encryption**: In-transit (HTTPS/TLS), at-rest encryption in DB.
- **Access Control**: Role-based, permission checks at the application and database layers.
- **Logging & Monitoring**: Application logs, intrusion detection, usage analytics.

### 5.2 Incident Response

- **Policy**: Documented procedure for triaging system vulnerabilities, data breaches, service outages.
- **Escalation Path**: Identify roles and responsibilities.

## 6. Detailed Field Specifications

### docId

- Type: string
- Purpose: Uniquely identifies this config document within the framework.

### version

- Type: string
- Purpose: Semantic version of the config (e.g., "0.1.1" or "2.0.0").

### revision

- Type: string
- Purpose: Minor revision suffix (\_<hex 2 digit>) appended to the version when making smaller updates.

### date

- Type: string (date-time)
- Purpose: Timestamp indicating when the config version was created or updated.

### projectName

- Type: string
- Purpose: Human-friendly name of the project.

### apiKeys

- Type: object (key-value)
- Purpose: Stores external service credentials. Each key is the service name; the value is the credential token.

### llmConfigs

- Type: object
  - model (string) : The LLM or model name (e.g., "gpt-4").
  - temperature (number) : Controls randomness of response generation.
  - topP (number) : Probability mass controlling token sampling.
  - maxTokens (integer) : Maximum tokens for each generation.

### defaultGenerators

- Type: array of strings
- Purpose: Contains IDs or names of generators to use by default for doc/diagram creation.

### typeTools

- Type: array of objects
  - tool (string) : Unique tool ID or name (required).
  - subType (string) : An optional subtype or variation for specialized tasks.
  - config (object) : Arbitrary settings for the tool.

### environment

- Type: object
- Purpose: Key-value map for environment variables or deployment context.

### security

- Type: object
- Purpose: Additional security flags or settings (e.g., encryption toggles, allowed IP ranges).

### projectActions

- Type: array of objects
  - artifactId (string) : Identifier for the target artifact (doc, diagram, etc.).
  - actionType (string) : Operation (e.g., "generate", "update", "remove").
  - inputRefs (array of strings) : References to other data or docs needed for the action.
  - actionParams (object) : Arbitrary parameters controlling the action.


**Update Log:** Updated for schema compatibility and workflow alignment.
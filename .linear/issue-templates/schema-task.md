# Schema Task Template

**Template ID**: `schema-task`
**Category**: Development - Schema Engineering
**Default Assignee**: SchemaEngineerAgent (SEA)
**Default Project**: IDFWU - IDEA Framework Unified (`4d649a6501f7`)
**Default Priority**: High

---

## Title Format
```
[Schema] {Task Description}
```

**Examples**:
- `[Schema] Implement IDFW Document Parser`
- `[Schema] Add FORCE Pattern Converter`
- `[Schema] Fix Schema Validation Error in Complex Types`

---

## Description Template

### Overview
<!-- Brief description of what needs to be done -->

**Task Type**: [ ] Parser | [ ] Converter | [ ] Validator | [ ] Other: _______

**Complexity**: [ ] Simple | [ ] Medium | [ ] Complex

**Estimated Hours**: ___ h

---

### Requirements

#### Functional Requirements
<!-- What the schema component must do -->
-
-
-

#### Technical Requirements
<!-- Technical specifications and constraints -->
- **Input Format**:
- **Output Format**:
- **Validation Rules**:
- **Performance Target**:

---

### Implementation Details

#### Files to Create/Modify
```
unified_framework/
├── core/
│   └── schema_parsers/
│       └── [file_name].py
└── tests/
    └── unit/
        └── core/
            └── test_[file_name].py
```

#### Schema Formats Involved
- [ ] IDFW Document
- [ ] IDFW Diagram
- [ ] IDFW Variable
- [ ] IDFW Project
- [ ] FORCE Tool
- [ ] FORCE Pattern
- [ ] FORCE Constraint
- [ ] Unified Command

#### Conversion Direction
- [ ] IDFW → FORCE
- [ ] FORCE → IDFW
- [ ] IDFW → Unified
- [ ] FORCE → Unified
- [ ] Other: _______

---

### Test Cases

#### Unit Tests Required
<!-- List key test scenarios -->
1. Parse valid schema
2. Handle malformed schema
3. Validate all required fields
4. Test edge cases
5. Performance benchmark

**Test Coverage Target**: ___ %

#### Integration Tests Required
- [ ] End-to-end workflow test
- [ ] Schema registry integration
- [ ] File I/O test

---

### Acceptance Criteria

**Definition of Done**:
- [ ] Implementation complete and code reviewed
- [ ] All unit tests passing (coverage > 85%)
- [ ] Integration tests added and passing
- [ ] Documentation updated (docstrings, API docs)
- [ ] Performance benchmark meets target
- [ ] No new linting errors
- [ ] PR created and linked to this issue
- [ ] Code merged to main branch

**Success Metrics**:
- Schema parsing success rate: > 95%
- Conversion fidelity: > 95%
- Performance: < 100ms for typical schema
- Zero regression errors

---

### Dependencies

**Blocked By**:
- PEG-XXX: [Related Issue Title]

**Blocks**:
- PEG-XXX: [Related Issue Title]

**Related Issues**:
- PEG-XXX: [Related Issue Title]

---

### Technical Notes

#### API Signature
```python
class [ComponentName]:
    def parse(self, schema: Dict) -> SchemaDefinition:
        """Parse schema from dictionary format"""
        pass

    def validate(self, schema: Dict) -> ValidationResult:
        """Validate schema structure"""
        pass

    def convert(self, source: Schema, target_format: SchemaFormat) -> Schema:
        """Convert schema to target format"""
        pass
```

#### Error Handling
<!-- How errors should be handled -->
- Invalid schema → ValidationError with details
- Missing fields → Default values or error
- Type mismatches → Type coercion or error

#### Performance Considerations
<!-- Any performance concerns or optimizations -->
-
-

---

### GitHub References

**Branch**: `jeremiah/peg-XXX-schema-[description]`
**PR**: #XXX (link when created)
**Commits**: (link to commits)

---

### Testing Instructions

#### Manual Testing Steps
1.
2.
3.

#### Automated Testing
```bash
# Run unit tests
pytest unified_framework/tests/unit/core/test_[file_name].py -v

# Run with coverage
pytest unified_framework/tests/unit/core/test_[file_name].py --cov -v

# Run integration tests
pytest unified_framework/tests/integration/test_schema*.py -v
```

---

### Documentation Updates

**Files to Update**:
- [ ] README.md
- [ ] API documentation
- [ ] Schema reference guide
- [ ] Examples directory

---

### Labels
`schema`, `parser`, `idfw`, `force`, `development`, `priority:high`

---

**Template Version**: 1.0.0
**Linear Project**: 4d649a6501f7
**Created**: 2025-09-29
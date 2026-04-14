# Linear Issue Templates for IDFWU

**Linear Project**: [IDFWU - IDEA Framework Unified](https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7)
**Project ID**: `4d649a6501f7`
**Team**: Pegues Innovations
**Version**: 1.0.0
**Created**: 2025-09-29

---

## Overview

This directory contains standardized Linear issue templates for the IDFWU project. These templates ensure consistency, completeness, and traceability across all development tasks.

---

## Available Templates

### 1. Schema Task Template
**File**: `schema-task.md`
**Use For**: Schema-related development tasks
**Default Assignee**: SchemaEngineerAgent (SEA)
**Examples**:
- Implementing schema parsers
- Creating schema converters
- Adding schema validation
- Schema migration tools

**When to Use**:
- Creating IDFW or FORCE parsers
- Implementing schema conversion logic
- Building schema validation systems
- Developing schema migration utilities

---

### 2. Command Task Template
**File**: `command-task.md`
**Use For**: Command system development tasks
**Default Assignee**: BackendDeveloperAgent (BDA)
**Examples**:
- Implementing command handlers
- Adding command middleware
- Creating command integrations
- Command history features

**When to Use**:
- Creating new command handlers ($, @, #, /)
- Implementing command middleware
- Integrating with external systems (YUNG, IDFW)
- Building command utilities (history, bookmarks)

---

### 3. Agent Task Template
**File**: `agent-task.md`
**Use For**: Agent system development tasks
**Default Assignee**: AgentDeveloperAgent (ADA)
**Examples**:
- Implementing new agents
- Adding agent capabilities
- Message bus integration
- Agent orchestration features

**When to Use**:
- Creating new specialized agents
- Implementing agent functionality
- Building agent communication systems
- Developing orchestration features

---

### 4. Testing Task Template
**File**: `testing-task.md`
**Use For**: Testing and quality assurance tasks
**Default Assignee**: QualityAssuranceAgent (QAA)
**Examples**:
- Creating unit test suites
- Adding integration tests
- Building E2E tests
- Performance benchmarking

**When to Use**:
- Creating test suites for new features
- Improving test coverage
- Adding performance tests
- Fixing flaky tests

---

### 5. Bug Report Template
**File**: `bug-report.md`
**Use For**: Reporting and tracking bugs
**Default Assignee**: Auto-assigned based on component
**Examples**:
- Schema conversion failures
- Command parsing errors
- Agent execution timeouts
- MCP protocol issues

**When to Use**:
- Reporting any bug or defect
- Documenting unexpected behavior
- Tracking regression issues
- Security vulnerabilities

---

## Template Usage Guide

### Creating a New Issue

1. **Choose the appropriate template**:
   - Schema work → `schema-task.md`
   - Command work → `command-task.md`
   - Agent work → `agent-task.md`
   - Testing → `testing-task.md`
   - Bug → `bug-report.md`

2. **Copy template contents** into Linear issue description

3. **Fill in all required fields**:
   - Replace `[placeholders]` with actual values
   - Check all applicable checkboxes
   - Add specific details for your task
   - Update dependencies section

4. **Set issue metadata**:
   - **Title**: Follow template title format
   - **Project**: IDFWU - IDEA Framework Unified
   - **Assignee**: Use default or assign specific agent
   - **Priority**: Set based on urgency
   - **Labels**: Add relevant labels from template

5. **Link related issues**:
   - Add parent issue if applicable
   - Link blocking/blocked issues
   - Reference related issues

---

## Template Structure

### Common Sections

All templates include these standard sections:

1. **Title Format**: Standardized naming convention
2. **Overview**: Brief description and metadata
3. **Requirements**: Functional and technical requirements
4. **Implementation Details**: Code structure and approach
5. **Test Cases**: Testing requirements
6. **Acceptance Criteria**: Definition of done
7. **Dependencies**: Related issues and blockers
8. **GitHub References**: Branch, PR, commits
9. **Documentation**: Updates needed
10. **Labels**: Appropriate tags

---

## Issue Naming Conventions

### Title Formats

**Schema Tasks**:
```
[Schema] Implement IDFW Document Parser
[Schema] Add FORCE Pattern Converter
[Schema] Fix Roundtrip Conversion Fidelity
```

**Command Tasks**:
```
[Command] Implement YUNG Command Handler
[Command] Add Command History Storage
[Command] Fix Command Parsing for Quoted Strings
```

**Agent Tasks**:
```
[Agent] Implement SchemaEngineerAgent
[Agent] Add Message Bus Integration
[Agent] Fix Agent Task Execution Timeout
```

**Testing Tasks**:
```
[Test] Create Schema Bridge Unit Tests
[Test] Add Integration Tests for Command System
[Test] Fix Flaky E2E Test in Agent Workflow
```

**Bug Reports**:
```
[Bug] Schema Conversion Fails for Complex IDFW Documents
[Bug] Command Parser Doesn't Handle Quoted Strings
[Bug] Agent Task Execution Timeout in Production
```

---

## Label Standards

### Component Labels
- `schema` - Schema-related tasks
- `command` - Command system tasks
- `agent` - Agent system tasks
- `mcp` - MCP server tasks
- `testing` - Testing tasks
- `documentation` - Documentation tasks

### Type Labels
- `bug` - Bug reports
- `feature` - New features
- `enhancement` - Improvements
- `refactor` - Code refactoring
- `performance` - Performance optimization

### Priority Labels
- `priority:urgent` - Critical, blocking issues
- `priority:high` - Important, near-term work
- `priority:medium` - Standard priority
- `priority:low` - Nice to have

### Department Labels
- `product` - Product team
- `project` - Project management
- `development` - Development team
- `integration` - Integration team
- `quality` - QA team

### Status Labels
- `status:todo` - Not started
- `status:in-progress` - Currently working
- `status:blocked` - Blocked by dependency
- `status:review` - In review
- `status:done` - Completed

---

## Issue Lifecycle

### 1. Creation
- Use appropriate template
- Fill in all required fields
- Set initial priority
- Add labels
- Link dependencies

### 2. Assignment
- Assign to appropriate agent/developer
- Verify agent has capacity
- Add to current sprint/milestone

### 3. In Progress
- Update status to "In Progress"
- Create branch: `jeremiah/peg-XXX-[description]`
- Add comments with progress updates
- Link commits as they're made

### 4. Code Review
- Create PR with issue reference
- Link PR to issue
- Address review comments
- Update issue with PR link

### 5. Testing
- Run all tests
- Verify acceptance criteria
- Update test results in issue
- Add test coverage metrics

### 6. Completion
- Merge PR
- Update status to "Done"
- Add completion comment with summary
- Close issue

### 7. Verification
- Verify in staging/production
- Monitor for issues
- Add post-deployment notes
- Link to deployment

---

## Cross-Platform References

### GitHub → Linear

**In Commit Messages**:
```bash
git commit -m "PEG-XXX: Implement IDFW document parser

- Add parser for IDFW document schemas
- Support JSON and YAML formats
- Include comprehensive validation
- Add unit tests with 95% coverage

Refs: PEG-XXX"
```

**In Pull Requests**:
```markdown
## Summary
Implements IDFW document parser as specified in PEG-XXX

## Related Linear Issues
- Closes PEG-XXX
- Blocked PEG-YYY
- Related to PEG-ZZZ

## Testing
- [x] Unit tests (95% coverage)
- [x] Integration tests
- [x] Manual testing

## Linear Reference
https://linear.app/pegues-innovations/issue/PEG-XXX
```

### Linear → GitHub

**In Issue Comments**:
```markdown
**GitHub PR**: #123
**Branch**: jeremiah/peg-XXX-implement-idfw-parser
**Commits**: abc123, def456, ghi789

**Progress Update**:
- ✅ Parser implementation complete
- ✅ Unit tests added
- 🔄 Integration tests in progress
- ⏳ Documentation pending
```

---

## Agent-Specific Guidelines

### SchemaEngineerAgent (SEA)
**Default Template**: `schema-task.md`
**Focus Areas**:
- Schema parsing and conversion
- Validation logic
- Migration tools
- Performance optimization

### BackendDeveloperAgent (BDA)
**Default Template**: `command-task.md`
**Focus Areas**:
- Command handlers
- API implementations
- Business logic
- Integrations

### AgentDeveloperAgent (ADA)
**Default Template**: `agent-task.md`
**Focus Areas**:
- Agent implementations
- Message bus
- Orchestration
- Task management

### QualityAssuranceAgent (QAA)
**Default Template**: `testing-task.md`
**Focus Areas**:
- Test creation
- Coverage improvement
- Quality audits
- Performance testing

---

## Best Practices

### Issue Creation
1. **Use the right template** for your task type
2. **Fill in all sections** - don't skip placeholders
3. **Be specific** in descriptions and requirements
4. **Set realistic estimates** for hours/complexity
5. **Link related issues** for traceability
6. **Add acceptance criteria** that are measurable

### Issue Management
1. **Update regularly** with progress comments
2. **Keep status current** (Todo → In Progress → Done)
3. **Link PRs and commits** as soon as created
4. **Document blockers** immediately when encountered
5. **Close promptly** after verification

### Cross-Platform Linking
1. **Always reference Linear IDs** in commits (PEG-XXX)
2. **Include issue links** in PR descriptions
3. **Add PR links** to Linear issues
4. **Update both platforms** when status changes
5. **Maintain audit trail** across platforms

---

## Template Customization

### Adding Custom Sections

Templates can be extended with project-specific sections:

```markdown
### Custom Section
**[Section Name]**:
- [Custom content]
```

### Modifying Existing Sections

Maintain core structure but adapt content:

```markdown
### Implementation Details
<!-- Modified for specific use case -->
**[Project-specific implementation details]**
```

---

## Quality Gates

### Before Creating Issue
- [ ] Appropriate template selected
- [ ] All required fields filled
- [ ] Dependencies identified
- [ ] Acceptance criteria defined
- [ ] Estimated effort provided

### Before Starting Work
- [ ] Issue reviewed and understood
- [ ] Dependencies resolved
- [ ] Branch created with correct naming
- [ ] Agent has capacity

### Before Marking Done
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] PR merged

---

## Template Maintenance

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-09-29 | Initial templates created |

### Update Process

1. Propose changes in team discussion
2. Update template files
3. Update version number
4. Document changes in this README
5. Notify team of updates

---

## Support

### Questions or Issues

If you have questions about template usage:
1. Check this README first
2. Review example issues in Linear
3. Ask in team chat
4. Create a documentation issue

### Template Improvements

To suggest template improvements:
1. Create a Linear issue with `documentation` label
2. Describe the improvement
3. Provide rationale
4. Submit for team review

---

## Examples

### Example Schema Task
**Issue**: PEG-123: [Schema] Implement IDFW Document Parser
**Template**: `schema-task.md`
**Status**: Completed
**Link**: [Example issue in Linear]

### Example Command Task
**Issue**: PEG-124: [Command] Implement YUNG Command Handler
**Template**: `command-task.md`
**Status**: In Progress
**Link**: [Example issue in Linear]

### Example Agent Task
**Issue**: PEG-125: [Agent] Implement SchemaEngineerAgent
**Template**: `agent-task.md`
**Status**: Completed
**Link**: [Example issue in Linear]

---

## Quick Reference

| Task Type | Template | Agent | Priority | Typical Duration |
|-----------|----------|-------|----------|------------------|
| Schema parsing | schema-task.md | SEA | High | 2-4h |
| Command handler | command-task.md | BDA | High | 2-3h |
| Agent implementation | agent-task.md | ADA | High | 1-2h |
| Unit tests | testing-task.md | QAA | High | 2-3h |
| Integration tests | testing-task.md | QAA | Medium | 3-4h |
| Bug fix | bug-report.md | Various | Varies | Varies |

---

**README Version**: 1.0.0
**Linear Project**: IDFWU (4d649a6501f7)
**Template Count**: 5
**Last Updated**: 2025-09-29

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com)
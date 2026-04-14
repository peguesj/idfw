# Bug Report Template

**Template ID**: `bug-report`
**Category**: Bug
**Default Assignee**: [Auto-assign based on component]
**Default Project**: IDFWU - IDEA Framework Unified (`4d649a6501f7`)
**Default Priority**: Medium

---

## Title Format
```
[Bug] {Brief Description}
```

**Examples**:
- `[Bug] Schema Conversion Fails for Complex IDFW Documents`
- `[Bug] Command Parser Doesn't Handle Quoted Strings`
- `[Bug] Agent Task Execution Timeout in Production`

---

## Bug Report

### Summary
<!-- One-sentence description of the bug -->

---

### Environment

**Platform**: [ ] macOS | [ ] Linux | [ ] Windows | [ ] Docker
**OS Version**: [e.g., macOS 14.5, Ubuntu 22.04]
**Python Version**: [e.g., 3.11.5]
**Node Version**: [e.g., 20.10.0]
**Framework Version**: [e.g., 1.0.0]

**Installation Method**: [ ] pip | [ ] source | [ ] docker

---

### Component Affected

**Primary Component**:
- [ ] Schema Bridge
- [ ] Command System
- [ ] Agent System
- [ ] MCP Server
- [ ] State Manager
- [ ] CLI
- [ ] VS Code Extension
- [ ] Documentation
- [ ] Other: _______

**Specific Module**: `unified_framework/[module]/[file].py`

---

### Bug Details

#### Description
<!-- Detailed description of the bug and its impact -->

**What is happening**:
<!-- Current behavior -->

**What should happen**:
<!-- Expected behavior -->

**Impact**: [ ] Critical | [ ] High | [ ] Medium | [ ] Low

**Frequency**: [ ] Always | [ ] Often | [ ] Sometimes | [ ] Rare

---

### Steps to Reproduce

1. <!-- First step -->
2. <!-- Second step -->
3. <!-- Third step -->
4. <!-- ... -->

**Minimal Reproducible Example**:
```python
# Code that reproduces the bug
from unified_framework.core import SchemaUnifier

schema = {
    "name": "test",
    # ... problematic schema
}

unifier = SchemaUnifier()
result = unifier.convert(schema)  # Fails here
```

---

### Expected Behavior
<!-- What you expected to happen -->

**Expected Output**:
```
[Expected output or behavior]
```

---

### Actual Behavior
<!-- What actually happened -->

**Actual Output**:
```
[Actual output or error]
```

---

### Error Messages

#### Console Output
```
[Copy/paste full error message and stack trace]
```

#### Log Files
```
[Relevant log entries from /var/log/idfwu/ or ~/.idfwu/logs/]
```

#### Stack Trace
```python
Traceback (most recent call last):
  File "...", line X, in <module>
    ...
  File "...", line Y, in function
    ...
Error: [Error message]
```

---

### Screenshots
<!-- If applicable, add screenshots to help explain the problem -->

![Screenshot 1](url-to-screenshot)
![Screenshot 2](url-to-screenshot)

---

### Configuration

#### Environment Variables
```bash
# Relevant environment variables
IDFWU_ENV=production
IDFWU_LOG_LEVEL=debug
LINEAR_API_KEY=[REDACTED]
REDIS_URL=redis://localhost:6379
```

#### Configuration Files
```yaml
# unified_framework/config.yaml
[Relevant configuration]
```

---

### Additional Context

#### Related Issues
- PEG-XXX: [Related issue]
- PEG-XXX: [Another related issue]

#### Recent Changes
<!-- Any recent changes that might be related -->
- Commit: [hash] - [description]
- PR: #XXX - [title]

#### Workarounds
<!-- If you found a temporary workaround, describe it here -->

---

### Impact Assessment

**Users Affected**: [ ] All users | [ ] Some users | [ ] Specific use case

**Business Impact**:
- [ ] Blocks deployment
- [ ] Blocks feature development
- [ ] Degrades performance
- [ ] Causes data loss
- [ ] Security vulnerability
- [ ] Minor inconvenience

**Severity Justification**:
<!-- Why this bug has the assigned severity -->

---

### Root Cause Analysis (To be filled by assignee)

#### Investigation Steps
1.
2.
3.

#### Root Cause
<!-- What is causing the bug -->

#### Affected Code
```python
# unified_framework/[module]/[file].py lines X-Y
[Problematic code snippet]
```

---

### Proposed Fix

#### Solution Approach
<!-- How to fix the bug -->

**Option 1**: [Description]
- Pros:
- Cons:

**Option 2**: [Description]
- Pros:
- Cons:

**Recommended**: Option [1/2]

#### Implementation Details
```python
# Proposed fix
def fixed_function():
    # Fixed implementation
    pass
```

---

### Testing Plan

#### Test Cases to Add
1. **Test Case 1**: Reproduce the original bug
2. **Test Case 2**: Verify the fix works
3. **Test Case 3**: Ensure no regression

#### Regression Tests
<!-- What existing tests need to be updated -->

```python
def test_bug_fix_PEG_XXX():
    """
    Test that bug PEG-XXX is fixed

    Reproduces the original bug scenario and verifies
    it no longer occurs after the fix.
    """
    # Test implementation
    pass
```

---

### Acceptance Criteria

**Definition of Done**:
- [ ] Bug reproduced in test
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Test case added (reproduces bug)
- [ ] Regression tests passing
- [ ] Fix verified in staging
- [ ] Documentation updated (if needed)
- [ ] PR created and reviewed
- [ ] Fix deployed to production
- [ ] Monitoring added (if needed)

**Verification Steps**:
1. Run reproduction steps
2. Verify expected behavior
3. Check for side effects
4. Verify in production

---

### Dependencies

**Blocked By**:
- PEG-XXX: [Related Issue]

**Blocks**:
- PEG-XXX: [Related Issue]

**Related Issues**:
- PEG-XXX: [Related Issue]

---

### GitHub References

**Branch**: `jeremiah/peg-XXX-fix-[description]`
**PR**: #XXX (link when created)
**Commits**: (link to commits)

---

### Debugging Information

#### Debug Mode Output
```
[Output with DEBUG logging enabled]
```

#### Performance Profiling
```
[If performance-related, include profiling data]
```

#### Memory Usage
```
[If memory-related, include memory profiling]
```

---

### Rollback Plan

**If fix causes issues**:
1. Revert commit [hash]
2. Redeploy previous version
3. Verify system stability
4. Re-investigate fix

---

### Labels
`bug`, `[component]`, `[severity]`, `priority:[level]`

**Automatic Labels Based on Component**:
- Schema Bridge → `schema`, `bug`
- Command System → `command`, `bug`
- Agent System → `agent`, `bug`
- MCP Server → `mcp`, `bug`

**Severity Labels**:
- Critical → `severity:critical`, `priority:urgent`
- High → `severity:high`, `priority:high`
- Medium → `severity:medium`, `priority:medium`
- Low → `severity:low`, `priority:low`

---

### Monitoring and Alerts

#### Alerts to Add
- [ ] Error rate alert for this scenario
- [ ] Performance degradation alert
- [ ] Resource usage alert

#### Metrics to Track
- [ ] Bug occurrence frequency
- [ ] Fix success rate
- [ ] Performance impact

---

### Security Considerations

**Is this a security vulnerability?** [ ] Yes | [ ] No

**If Yes**:
- [ ] Report to security team immediately
- [ ] Do not disclose details publicly
- [ ] Follow security incident process
- [ ] Update security documentation

---

### Communication Plan

#### Stakeholders to Notify
- [ ] Development team
- [ ] QA team
- [ ] Product team
- [ ] Users (if user-facing)

#### Release Notes Entry
```markdown
### Bug Fixes
- Fixed [bug description] (PEG-XXX)
  - [Detailed explanation]
  - [Impact on users]
```

---

### Post-Fix Review

**After fix is deployed**:
- [ ] Monitor for 24 hours
- [ ] Verify no new issues
- [ ] Check performance metrics
- [ ] Update documentation
- [ ] Conduct post-mortem (if critical)

---

**Template Version**: 1.0.0
**Linear Project**: 4d649a6501f7
**Created**: 2025-09-29
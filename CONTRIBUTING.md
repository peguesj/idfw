# Contributing to IDFW Unified Framework

Thank you for your interest in contributing to the IDFW Unified Framework! This document provides guidelines and instructions for contributing to the project.

## Linear Project Management

All work is tracked in Linear:
- **Project**: [IDFWU - IDEA Framework Unified](https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7)
- **Project ID**: `4d649a6501f7`
- **Team**: Pegues Innovations

### Before Starting Work

1. **Check Linear** for existing issues
2. **Create or assign** an issue to yourself
3. **Update status** to "In Progress"
4. **Create feature branch** using Linear's naming: `jeremiah/peg-XXX-issue-title`

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/[org]/idfw-unified.git
cd idfw-unified

# Run the initialization script
chmod +x .claude/scripts/init-project.sh
./.claude/scripts/init-project.sh

# Activate Python virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Use Linear's branch naming convention
git checkout -b jeremiah/peg-XXX-feature-name
```

### 2. Make Changes

Follow these conventions:
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use ESLint configuration
- **Commits**: Use conventional commit format

### 3. Test Your Changes

```bash
# Run Python tests
pytest unified_framework/tests/ -v

# Run Node tests
npm test

# Run linters
black unified_framework/
isort unified_framework/
flake8 unified_framework/
npm run lint
```

### 4. Commit Changes

Use conventional commit format:
```bash
git commit -m "feat(scope): add new feature

- Detailed change description
- Related Linear issue: PEG-XXX

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 5. Create Pull Request

Use the PR template and ensure:
- Linear issue is referenced
- Tests pass
- Documentation is updated
- PR description is complete

## Code Standards

### Python Code Style

```python
"""Module docstring describing purpose."""

from typing import Dict, Optional, Any
import asyncio

class UnifiedComponent:
    """Class docstring with description."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize component with config."""
        self.config = config

    async def execute(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Execute a command.

        Args:
            command: The command to execute

        Returns:
            Optional result dictionary
        """
        # Implementation
        pass
```

### TypeScript Code Style

```typescript
/**
 * Module description
 */

interface UnifiedConfig {
  project: string;
  version: string;
  linearId: string;
}

export class UnifiedComponent {
  constructor(private config: UnifiedConfig) {}

  /**
   * Execute a command
   * @param command - The command to execute
   * @returns Promise with result
   */
  async execute(command: string): Promise<any> {
    // Implementation
  }
}
```

## Testing Guidelines

### Unit Tests

```python
# unified_framework/tests/unit/test_component.py
import pytest
from unified_framework.core import Component

@pytest.fixture
def component():
    return Component({"test": True})

def test_component_initialization(component):
    assert component.config["test"] is True

@pytest.mark.asyncio
async def test_component_execution(component):
    result = await component.execute("test")
    assert result is not None
```

### Integration Tests

Test interactions between components:
```python
# unified_framework/tests/integration/test_integration.py
@pytest.mark.integration
async def test_idfw_force_integration():
    # Test IDFW and Force integration
    pass
```

## Documentation

### Code Documentation

- All public functions/methods must have docstrings
- Complex logic should have inline comments
- Update README when adding features

### API Documentation

When adding new endpoints or commands:
1. Update OpenAPI spec
2. Add examples to documentation
3. Update slash command definitions

## Using Slash Commands

Claude Code slash commands are available in `.claude/slash-commands/`:

```bash
# Run automated fixes
/autofix

# Update project status
/update-project-status

# Create Linear epic
/create-linear-epic "Epic Title"
```

## Submitting Changes

### Pull Request Checklist

- [ ] Linear issue referenced (PEG-XXX)
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] PR template completed
- [ ] CI pipeline passes
- [ ] Review requested

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainer
3. **Linear status** updated to "In Review"
4. **Merge** after approval
5. **Linear status** updated to "Done"

## Issue Reporting

### Bug Reports

Use GitHub issue template or create Linear issue:
1. Describe the bug clearly
2. Provide reproduction steps
3. Include error messages
4. Specify environment details

### Feature Requests

1. Check existing Linear epics/issues
2. Create detailed feature request
3. Explain use cases
4. Consider implementation approach

## Communication

### Linear Comments

- Update issues with progress
- Ask questions on related issues
- Link PRs and commits

### GitHub Discussions

- Architecture decisions
- Feature proposals
- General questions

## Release Process

1. **Version Bump**: Update version in all relevant files
2. **Changelog**: Update CHANGELOG.md
3. **Linear Milestone**: Complete milestone tasks
4. **Tag Release**: Create Git tag
5. **Deploy**: Follow deployment guide

## Getting Help

- **Documentation**: Check `unified_framework_docs/`
- **Linear Project**: Search existing issues
- **GitHub Discussions**: Ask questions
- **Slash Commands**: Use `/help` for command info

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to IDFW Unified Framework!

**Linear Project**: [IDFWU - IDEA Framework Unified](https://linear.app/pegues-innovations/project/idfwu-idea-framework-unified-4d649a6501f7)
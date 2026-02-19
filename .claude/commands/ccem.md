---
description: CCEM - Claude Code Environment Manager (IDFW Project)
argument-hint: <action> [options]
---

# CCEM for IDFW Project

Quick access to CCEM functions tailored for the IDFW project.

## Quick Actions

```bash
/ccem inspect project           # View IDFW project configuration
/ccem backup project            # Backup IDFW settings
/ccem migrate ~/idfw-module     # Fork IDFW to new project
/ccem optimize project          # Optimize configuration
```

## Project-Specific Examples

### Fork for Experimentation
```bash
/ccem migrate ~/idfw-experiment --fork --include-history
```

### Review Git Workflow Permissions
```bash
/ccem inspect project --filter git
```
Shows:
- `git checkout:*`
- `git branch:*`
- `git remote:*`
- `gh repo:*` (GitHub CLI)

## IDFW Project Context

**Current Permissions**: 25
- Git: Advanced git workflow permissions
- Python: `python:*`, `python3:*`, `pip install:*`, `pytest:*`
- GitHub: `gh repo create:*`, `gh auth:*`
- Scripts: `./.claude/scripts/init-project.sh:*`

**Language Focus**: Python development with git automation

For full CCEM documentation: `/ccem --help`

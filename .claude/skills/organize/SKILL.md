---
description: "Clean up and organize repository structure"
argument-hint: "[scope: folders|files|branches|code|all] [--ai-patterns] [--depth=quick|full]"
---

# Organize

Repository organization and cleanup with architecture analysis.

## Usage

```bash
/organize all                        # Full cleanup + structure analysis
/organize folders                    # Folder structure
/organize files                      # Unused/backup files
/organize branches                   # Stale git branches
/organize code                       # Code organization
/organize code --ai-patterns         # AI-codebase specific analysis

# Depth
/organize all --depth=quick          # Critical issues only
/organize all --depth=full           # Complete analysis
```

## Scopes

| Scope | What It Checks |
|-------|---------------|
| `folders` | Structure, unnecessary nesting, empty dirs |
| `files` | Unused files, backups, dead code files |
| `branches` | Stale branches, merged not deleted |
| `code` | Code organization, architecture issues |
| `all` | Everything above |

## Agent Delegation

| Scope | Agent(s) | What It Does |
|-------|----------|--------------|
| `folders` | `architect` | Structure analysis, unnecessary nesting, empty dirs |
| `files` | `architect` | Unused files, backups, dead code files |
| `branches` | (direct) | Git branch cleanup (no agent needed) |
| `code` | `architect` + `code-reviewer` | Code organization, architecture issues |
| `all` | `architect` + `code-reviewer` | Everything above (agents run in parallel) |

## Python-Specific Checks

### Module Organization
- Files mixing concerns (models + business logic + I/O)
- `__init__.py` exports are explicit, not `import *`
- Test structure mirrors source structure
- Circular import potential

### Package Structure
```
project/
├── pyproject.toml
├── src/
│   └── package_name/
│       ├── __init__.py        # Public API exports
│       ├── core/              # Core business logic
│       ├── models/            # Pydantic models
│       ├── services/          # Business services
│       └── utils/             # Shared utilities
└── tests/
    └── package_name/          # Mirror src structure
```

### AI-Pattern Detection

Add `--ai-patterns` to detect issues common in AI-generated codebases:

| Pattern | Description |
|---------|-------------|
| Over-abstraction | Unnecessary interfaces, factories, wrappers |
| Redundant code | Same logic implemented multiple ways |
| Over-defensive | Excessive null checks, type guards |
| Dependency bloat | Unused or redundant packages |
| Verbose patterns | Could be simpler |

## Output Format

```markdown
# Organization Report

**Scope:** all
**Date:** 2026-01-15

## Summary

| Category | Issues |
|----------|--------|
| Folders | 3 |
| Files | 5 |
| Branches | 2 |
| Code | 4 |

## Folder Issues

### Empty directories
- src/legacy/ (empty)
- tests/fixtures/old/ (empty)
**Action:** Delete or populate

## Code Structure Issues

### Monolithic modules
- src/api/handlers.py (450 lines)
**Action:** Split by responsibility

## Recommendations

1. Delete empty directories
2. Remove backup files
3. Clean up merged branches
4. Split monolithic modules
```

## After Organizing

```bash
/execute                      # Apply fixes
/review --quick               # Verify no issues introduced
git status                    # Review changes
```

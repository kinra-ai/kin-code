---
description: "Code review for Python projects"
argument-hint: "[scope] [--thorough|--arch|--security|--deps|--quick]"
context: fork
---

# Review

Code review optimized for **Python 3.12+** projects with modern tooling.

Delegates to specialized agents based on flags. Agents run in parallel when independent.

## Usage

```bash
/review                        # Auto-detect from git context → code-reviewer agent
/review git diff main          # Review changes since main
/review src/                   # Specific directory
/review full                   # Full project review → architect + code-reviewer agents

# Focus modes (launch specific agents)
/review --quick                # Critical issues only → code-reviewer (single pass)
/review --arch                 # Architecture focus → architect agent
/review --security             # Security audit → security-auditor agent
/review --deps                 # Dependency health → dependency-manager agent
/review --thorough             # Full deep review → architect + code-reviewer + security-auditor + test-validator
```

## Agent Routing

| Flag | Agent(s) to Launch | What It Does |
|------|-------------------|-------------|
| *(default)* | `code-reviewer` | Python patterns, type safety, linting |
| `--quick` | `code-reviewer` | Fast pass on critical issues only |
| `--arch` | `architect` | File structure, modularity, coupling |
| `--security` | `security-auditor` | Command injection, path traversal, secrets, OWASP Top 10 |
| `--deps` | `dependency-manager` | Security audit (pip-audit), outdated packages |
| `--thorough` | `architect` + `code-reviewer` + `security-auditor` + `test-validator` | Full codebase deep review |

## Python-Specific Checks

### Code Quality (code-reviewer)

| Category | What to Check | Common Issues |
|----------|---------------|---------------|
| **Type hints** | Modern `\|` union, `list`/`dict` generics | Using `Optional`, `Union`, `List`, `Dict` |
| **Pydantic** | `model_validate`, proper validators | Ad-hoc parsing, manual `getattr` |
| **Error handling** | Specific exceptions, proper chaining | Bare `except:`, swallowing errors |
| **Async** | No blocking in async, proper `await` | Blocking I/O in async functions |
| **Style** | match-case, walrus operator, pathlib | Old-style if/elif, os.path |

### Security (security-auditor)

| Category | What to Check | Common Issues |
|----------|---------------|---------------|
| **Command injection** | subprocess with shell=True | User input in shell commands |
| **Path traversal** | Unsanitized file paths | Missing boundary validation |
| **SQL injection** | String formatting in queries | f-strings in SQL |
| **Deserialization** | pickle with untrusted data | pickle.loads() on user input |
| **Secrets** | API keys in code/logs | Hardcoded credentials |

## Linter Integration

```bash
# Run before review
uv run ruff check .            # Linting
uv run pyright                 # Type checking
uv run ruff format --check .   # Format check
```

## Severity Levels

| Level | Meaning | Examples |
|-------|---------|----------|
| **CRITICAL** | Security risk or will break | Command injection, SQL injection, secrets |
| **IMPORTANT** | Should fix soon | Missing types, bare except, magic numbers |
| **SUGGESTION** | Nice to have | Extract constant, add docstring |

## Output Format

```
Code Review

Files reviewed: X
Scope: [git diff / specific files / full project]

## Summary
- Critical: X (must fix before merge)
- Important: Y (should fix)
- Suggestions: Z (optional improvements)

## Linter Results
- ruff: PASSED / X errors
- pyright: PASSED / X errors

## CRITICAL

### [CR-1] Issue title
**File:** path/to/file.py:45
**Issue:** Description
**Fix:** Specific solution

## IMPORTANT
[...]

## SUGGESTIONS
[...]
```

## After Review

```bash
# Fix specific issues
/execute CR-1             # Fix command injection
/execute ARCH-1           # Split large module

# Fix by severity
/execute critical         # All critical issues
/execute important        # All important issues

# Re-review
/review                   # Verify fixes
```

## Tips

- `/review --quick` before every commit
- `/review --security` when handling user input or external data
- `/review --arch` when refactoring modules
- `/review --deps` periodically for security audit
- `/review --thorough` before merging to main

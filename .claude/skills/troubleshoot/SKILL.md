---
description: "Diagnose and troubleshoot issues with optional research and auto-fixes"
argument-hint: "<problem-description> [--research] [--fix]"
---

# Troubleshoot

Delegates to the **troubleshooter agent** to diagnose issues by mapping symptoms to root causes.

## Usage

```bash
# Diagnose
/troubleshoot "ImportError: No module named xyz"

# Diagnose with research
/troubleshoot "Memory usage growing" --research

# Diagnose and fix
/troubleshoot "TypeError: undefined" --fix

# Full automation
/troubleshoot "Tests failing after upgrade" --research --fix
```

## Flags

- `--research` - Search for solutions online
- `--fix` - Automatically apply recommended fix
- `--verbose` - Show detailed analysis

## How It Works

Launches the **troubleshooter agent** (via Task tool) which will:

1. **Understand symptom** - What's broken and when?
2. **Read project context** - CLAUDE.md, code, patterns
3. **Map to root cause** - Which module is involved?
4. **Diagnose** - What's actually wrong?
5. **Recommend fixes** - Specific solutions with file:line
6. **Apply fixes** - If --fix flag used

## Agent Delegation

| Flag | Agent(s) | What It Does |
|------|----------|--------------|
| (default) | `troubleshooter` | Diagnose issue, recommend fixes |
| `--research` | `troubleshooter` + `researcher` | Search for solutions (parallel) |
| `--fix` | `troubleshooter` + `task-executor` | Diagnose then apply fix |
| `--research --fix` | `troubleshooter` + `researcher` + `task-executor` | Full automation |

## Common Python Issues

### ImportError / ModuleNotFoundError
- Check virtual environment (`uv sync`)
- Verify package in pyproject.toml
- Check for circular imports
- Verify `__init__.py` exports

### AttributeError
- Check for None values
- Verify object type at runtime
- Review class inheritance

### TypeError
- Check function signatures
- Verify argument types match hints
- Review Pydantic validation

### Pydantic ValidationError
- Print raw data being validated
- Compare with model field types
- Check for optional vs required fields

### Async issues
- Check for blocking calls in async functions
- Verify all `await` keywords present
- Use `asyncio.to_thread()` for blocking calls

## How to Report Problems

Be specific:
```
TypeError: expected str, got NoneType at line 45 in src/api/users.py
Happens when calling create_user() with empty form
Started after updating pydantic to v2.5
```

Include:
- Exact error message
- When it happens
- Recent changes

## Output

Reports saved to `.claude/notes/`:
- `troubleshoot-analysis-[timestamp].md` - Diagnosis
- `troubleshoot-research-[timestamp].md` - Research (if --research)
- `troubleshoot-fix-[timestamp].md` - Fix details (if --fix)

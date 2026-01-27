---
description: "Documentation management - sync, validate, audit, optimize"
argument-hint: "[action: sync|validate|audit|optimize] [target] [--depth=quick|full]"
---

# Docs

Delegates to the **doc-auditor agent** for comprehensive documentation management.

## Quick Examples

```bash
/docs sync                    # Verify docs match code
/docs validate                # Check links and structure
/docs audit --depth=full      # Comprehensive audit
/docs optimize readme         # Improve README clarity
```

## How It Works

When you run `/docs [action]`, this command launches the **doc-auditor** agent with specific focus areas:

- **sync** - Verify code-docs alignment (functions/APIs, configuration, examples)
- **validate** - Check link validity and documentation structure
- **audit** - Comprehensive check (all sync + validate + style consistency)
- **optimize** - Work with design-partner for clarity and engagement improvements

## Usage Patterns

After code changes:
```bash
/docs sync
```

Before committing:
```bash
/docs validate
```

Pre-release:
```bash
/docs audit --depth=full
```

## Agent Delegation

| Action | Agent(s) | What It Does |
|--------|----------|--------------|
| `sync` | `doc-auditor` | Verify functions/APIs documented, config options, code examples current |
| `validate` | `doc-auditor` | Check broken internal links, missing referenced files, documentation gaps |
| `audit` | `doc-auditor` | All sync + validate checks, style consistency, completeness assessment |
| `optimize` | `doc-auditor` + `design-partner` | Improve CLAUDE.md token efficiency, README clarity |

## Python Documentation Standards

### Docstring Style (Google)
```python
def process_data(data: list[int], multiplier: int = 2) -> list[int]:
    """Process a list of integers.

    Args:
        data: The input integers to process.
        multiplier: Factor to multiply each value by.

    Returns:
        Processed list with each value multiplied.

    Raises:
        ValueError: If data is empty.
    """
```

### What to Check
- All public functions have docstrings
- Type hints present on all signatures
- Examples included for complex functions
- Exceptions documented accurately
- Module-level docstrings present

## Output

Reports saved to `.claude/notes/docs-[action]-[timestamp].md`

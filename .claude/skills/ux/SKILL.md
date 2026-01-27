---
description: "UX review - CLI help text, error messages, user flows"
argument-hint: "[scope] [--help|--errors|--flows|--quick]"
---

# UX Review

Identify usability issues in CLI/TUI applications: help text quality, error messages, user flows.

## Usage

```bash
/ux                            # Auto-detect CLI files
/ux src/cli/                   # Specific directory
/ux src/cli/commands.py        # Specific file
/ux --help                     # Focus on help text
/ux --errors                   # Focus on error messages
/ux --flows                    # User flow analysis
/ux --quick                    # Critical issues only
```

## What It Does

Launches the **ux-reviewer agent** (via Task tool) to analyze CLI/TUI code for:

| Category | What It Checks |
|----------|----------------|
| **Help text** | Command descriptions, argument help, usage examples |
| **Error messages** | Actionable errors, context, recovery guidance |
| **Feedback** | Progress indicators, confirmations, status updates |
| **Consistency** | Command naming, flag conventions, output format |
| **Discoverability** | Shell completions, --help accessibility |
| **Heuristics** | Nielsen's 10 usability principles for CLI |

## Agent Delegation

| Flag | Agent(s) | What It Does |
|------|----------|--------------|
| (default) | `ux-reviewer` | Full UX review (help, errors, feedback) |
| `--help` | `ux-reviewer` | Help text focus (descriptions, examples) |
| `--errors` | `ux-reviewer` | Error message focus (actionable, specific) |
| `--flows` | `ux-reviewer` + `design-partner` | User flow analysis with recommendations |
| `--quick` | `ux-reviewer` | Critical issues only (fast pass) |

## Focus Modes

| Flag | Focus Area |
|------|------------|
| (default) | Full UX review |
| `--help` | Help text quality (argparse, typer, click) |
| `--errors` | Error messages (clarity, actionability) |
| `--flows` | User flows (command sequences, confirmations) |
| `--quick` | Critical issues only |

## CLI UX Patterns

### Good Help Text (typer/click)
```python
@app.command()
def process(
    file: Annotated[str, typer.Argument(help="Input file (e.g., data.json)")]
):
    """Process a data file and output results.

    Example:
        $ myapp process data.json --output results.csv
    """
```

### Good Error Messages
```python
# BAD: Generic error
raise ValueError("Invalid input")

# GOOD: Actionable error with context
raise typer.BadParameter(
    f"File '{path}' not found. Check the path and try again.\n"
    f"Available files: {', '.join(available_files)}"
)
```

### Good Progress Feedback
```python
with Progress() as progress:
    task = progress.add_task("Processing...", total=len(items))
    for item in items:
        process(item)
        progress.advance(task)
```

## Nielsen's Heuristics for CLI

| Heuristic | CLI Application |
|-----------|-----------------|
| Visibility of status | Progress bars, spinners, verbose mode |
| Match system | Standard flags (-h, -v, -q), POSIX conventions |
| User control | Ctrl+C handling, --dry-run, confirmations |
| Consistency | Uniform command/flag naming, output format |
| Error prevention | Input validation, confirmations for destructive ops |

## Severity Levels

| Level | Examples |
|-------|----------|
| **Critical** | Missing help text, generic errors, no progress on long ops |
| **Important** | Inconsistent naming, small issues, no confirmations |
| **Suggestions** | Missing completions, no quiet mode |

## After UX Review

```bash
# Fix specific issues
/execute UX-1,UX-2

# Fix all critical
/execute critical

# Re-review after fixes
/ux --quick
```

## Limitations

Code analysis cannot catch:
- Actual terminal rendering issues
- Color contrast problems
- Real user behavior
- Cross-platform compatibility

Combine with manual testing in target terminals.

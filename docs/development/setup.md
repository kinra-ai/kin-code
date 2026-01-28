# Development Setup

Set up your environment for contributing to Kin Code.

## Prerequisites

- Python 3.12+
- Git
- uv (recommended)

## Clone the Repository

```bash
git clone https://github.com/kinra-ai/kin-code.git
cd kin-code
```

## Install Dependencies

Using uv (recommended):

```bash
uv sync
```

This installs all dependencies including dev dependencies.

## Verify Setup

Run tests:

```bash
uv run pytest tests/
```

Run type checking:

```bash
uv run pyright
```

Run linting:

```bash
uv run ruff check .
```

## Development Tools

### Running Kin Code

```bash
uv run kin
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific file
uv run pytest tests/test_specific.py

# With coverage
uv run pytest --cov=kin_code
```

### Code Quality

```bash
# Lint
uv run ruff check .

# Auto-fix
uv run ruff check . --fix

# Format
uv run ruff format .

# Type check
uv run pyright
```

## Project Structure

```
kin-code/
  kin_code/           # Main package
    cli/              # CLI interface
    core/             # Core logic
      tools/          # Built-in tools
      providers/      # LLM providers
      skills/         # Skills system
    acp/              # ACP server
  tests/              # Test suite
  docs/               # Documentation
```

## Environment Variables

For development, create `.env` in the project root:

```bash
OPENAI_API_KEY=sk-...
# Or other provider keys
```

## Related

- [Contributing](contributing.md)
- [Testing](testing.md)
- [Code Style](code-style.md)

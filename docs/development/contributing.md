# Contributing to Kin Code

Thank you for your interest in contributing to Kin Code! This guide explains how to get started.

## Ways to Contribute

- **Bug reports** - Report issues you encounter
- **Feature requests** - Suggest new functionality
- **Documentation** - Improve or add documentation
- **Code** - Fix bugs or implement features
- **Testing** - Add or improve tests

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- uv (recommended) or pip

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/kinra-ai/kin-code.git
cd kin-code
```

2. Install dependencies with uv:

```bash
uv sync
```

3. Verify the setup:

```bash
uv run pytest tests/
```

See [Development Setup](setup.md) for detailed instructions.

## Development Workflow

### Creating a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/bug-description
```

### Making Changes

1. Write your code
2. Add or update tests
3. Update documentation if needed
4. Run tests locally

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_specific.py

# With coverage
uv run pytest --cov=kin_code
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Type checking
uv run pyright

# Auto-format
uv run ruff format .
```

### Committing

Write clear commit messages:

```
Add support for new feature X

- Implemented X in module Y
- Added tests for X
- Updated documentation
```

### Submitting a Pull Request

1. Push your branch
2. Open a pull request on GitHub
3. Fill in the PR template
4. Wait for review

## Code Style

### Python Style

- Follow PEP 8
- Use type hints (Python 3.12+ style)
- Prefer `match-case` over `if/elif` chains
- Use modern typing (`list`, `dict`, `|` for unions)
- Avoid deep nesting (prefer early returns)

See [Code Style](code-style.md) for details.

### Documentation Style

- Use Markdown
- Keep language clear and concise
- Include code examples
- Link to related documentation

## Testing Guidelines

### Test Organization

```
tests/
  test_module_name.py
  module_name/
    test_specific.py
```

### Writing Tests

- Test one thing per test
- Use descriptive test names
- Include both positive and negative cases
- Mock external dependencies

### Test Coverage

Aim for high coverage, but prioritize meaningful tests over coverage numbers.

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Commit messages are clear

### PR Description

Include:
- What the change does
- Why it's needed
- How to test it
- Any breaking changes

### Review Process

1. Automated checks run
2. Maintainer review
3. Address feedback
4. Merge when approved

## Reporting Issues

### Bug Reports

Include:
- Kin Code version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Description of the feature
- Use case / motivation
- Proposed implementation (optional)

## Code of Conduct

Be respectful and constructive. We're all here to improve the project.

## Questions?

- Check existing issues and discussions
- Open a discussion for general questions
- Open an issue for bugs or feature requests

## Related

- [Development Setup](setup.md)
- [Testing](testing.md)
- [Code Style](code-style.md)

# Testing

Guidelines for testing Kin Code.

## Running Tests

### All Tests

```bash
uv run pytest
```

### Specific Tests

```bash
# Single file
uv run pytest tests/test_file.py

# Single test
uv run pytest tests/test_file.py::test_name

# Pattern match
uv run pytest -k "test_pattern"
```

### With Coverage

```bash
uv run pytest --cov=kin_code
```

## Test Organization

```
tests/
  conftest.py          # Shared fixtures
  test_module.py       # Module tests
  module/
    test_specific.py   # Detailed tests
  acp/                 # ACP tests
  snapshots/           # Snapshot tests
```

## Writing Tests

### Basic Test

```python
def test_something():
    result = function_under_test()
    assert result == expected
```

### Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

## Mocking

Mock external dependencies:

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch("module.external_call") as mock:
        mock.return_value = "mocked"
        result = function_that_calls_external()
        assert result == "mocked"
```

## Snapshot Tests

For UI components:

```python
def test_ui_snapshot(snapshot):
    output = render_component()
    assert output == snapshot
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation.

### Integration Tests

Test component interactions.

### Snapshot Tests

Verify UI output hasn't changed unexpectedly.

## Best Practices

1. **One assertion per test** when practical
2. **Descriptive names** - `test_function_behavior_condition`
3. **Arrange-Act-Assert** pattern
4. **Mock external services**
5. **Test edge cases**

## Related

- [Development Setup](setup.md)
- [Contributing](contributing.md)

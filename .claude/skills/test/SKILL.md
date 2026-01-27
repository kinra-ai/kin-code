---
description: "Testing - automated tests, manual scenarios, coverage analysis"
argument-hint: "[mode: auto|manual|coverage] [target] [--verbose]"
context: fork
---

# Test

Run and validate tests using the **test-validator agent**.

## Usage

```bash
/test                          # Run full test suite
/test auto                     # Automated tests (default)
/test manual                   # Interactive manual testing
/test coverage                 # Coverage analysis

# Target specific tests
/test tests/test_auth.py       # Specific file
/test -k "test_login"          # Pattern match

# Options
/test --verbose                # Detailed output
/test --cov                    # With coverage report
```

## Modes

| Mode | Use Case |
|------|----------|
| `auto` | Run pytest, report pass/fail/skip |
| `manual` | Interactive testing scenarios |
| `coverage` | Analyze test coverage gaps |
| `regression` | Post-fix validation |

## Agent Delegation

| Mode | Agent | What It Does |
|------|-------|--------------|
| `auto` | `test-validator` | Run pytest, capture results |
| `manual` | `test-validator` | Guide through test scenarios |
| `coverage` | `test-validator` | Coverage analysis and gaps |
| `regression` | `test-validator` + `regression-tracker` | Verify fix + check baselines |

## Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific tests
uv run pytest tests/test_auth.py -v

# Run with markers
uv run pytest -m "not slow"

# Run matching pattern
uv run pytest -k "test_login"
```

## Output Format

```
Test Results

Framework: pytest
Command: uv run pytest

Results: X passed, Y failed, Z skipped
Duration: Xs

## Failed Tests (if any)

### test_function_name (tests/test_file.py:45)
Expected: [expected]
Actual: [actual]
Traceback: [relevant lines]

## Coverage (if --cov)

Overall: XX%
Missing: [uncovered files/lines]

## Status: PASS / FAIL
```

## After Tests

```bash
# If failures, troubleshoot
/troubleshoot "test_function fails with error X"

# Review coverage gaps
/test coverage

# Check for regressions
/test regression
```

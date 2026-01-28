# Code Style

Python style guidelines for Kin Code.

## Overview

Kin Code follows modern Python 3.12+ best practices.

## Type Hints

Use modern type hints:

```python
# Good
def process(items: list[str]) -> dict[str, int]:
    ...

def maybe_value() -> str | None:
    ...

# Avoid
from typing import List, Dict, Optional

def process(items: List[str]) -> Dict[str, int]:
    ...

def maybe_value() -> Optional[str]:
    ...
```

## Match-Case

Prefer match-case over if/elif chains:

```python
# Good
match command:
    case "start":
        start()
    case "stop":
        stop()
    case _:
        unknown()

# Avoid
if command == "start":
    start()
elif command == "stop":
    stop()
else:
    unknown()
```

## Walrus Operator

Use when it improves clarity:

```python
# Good
if (match := pattern.search(text)):
    process(match.group())

# When appropriate
while (line := file.readline()):
    process(line)
```

## Never Nester

Avoid deep nesting with early returns:

```python
# Good
def process(item):
    if not item:
        return None
    if not item.valid:
        return None
    return transform(item)

# Avoid
def process(item):
    if item:
        if item.valid:
            return transform(item)
    return None
```

## Pathlib

Use pathlib for file operations:

```python
# Good
from pathlib import Path

path = Path("dir") / "file.txt"
content = path.read_text()

# Avoid
import os

path = os.path.join("dir", "file.txt")
with open(path) as f:
    content = f.read()
```

## Pydantic

Use Pydantic for data validation:

```python
from pydantic import BaseModel

class Config(BaseModel):
    name: str
    count: int = 0
```

## Formatting

Use ruff for formatting:

```bash
uv run ruff format .
```

## Linting

Use ruff for linting:

```bash
uv run ruff check .
```

## Type Checking

Use pyright for type checking:

```bash
uv run pyright
```

## Related

- [Contributing](contributing.md)
- [Development Setup](setup.md)

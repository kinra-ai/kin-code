# search_replace

Make targeted edits to files using search/replace blocks.

## Overview

The `search_replace` tool finds exact text matches in a file and replaces them. It's the preferred way to edit existing files.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to the file to modify |
| `content` | string | Yes | SEARCH/REPLACE blocks defining changes |

## Block Format

```
<<<<<<< SEARCH
[exact text to find]
=======
[replacement text]
>>>>>>> REPLACE
```

## Multiple Changes

Include multiple blocks to make several changes:

```
<<<<<<< SEARCH
def old_function():
    return "old value"
=======
def new_function():
    return "new value"
>>>>>>> REPLACE

<<<<<<< SEARCH
import os
=======
import os
import sys
>>>>>>> REPLACE
```

## Important Rules

1. **Exact match required**: The SEARCH text must match exactly, including whitespace and indentation
2. **Unique match**: The SEARCH text must appear exactly once in the file
3. **Sequential application**: Each block is applied in order; later blocks see results of earlier ones
4. **Use 5+ equals signs**: Between SEARCH and REPLACE sections

## Examples

```python
# Add a new import
search_replace(
    file_path="src/main.py",
    content='''<<<<<<< SEARCH
import os
=======
import os
import logging
>>>>>>> REPLACE'''
)

# Fix a typo
search_replace(
    file_path="README.md",
    content='''<<<<<<< SEARCH
This is an example
=======
This is an example
>>>>>>> REPLACE'''
)
```

## Error Handling

If the search text isn't found or appears multiple times, the tool provides detailed error messages showing context to help identify the issue.

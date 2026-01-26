# Skills Guide

Create and manage skills to give Kin Code domain-specific capabilities.

## Overview

Skills are reusable instruction sets that teach the agent specialized tasks. Unlike tools (which execute code), skills provide context and guidance through structured prompts.

Use skills to:

- **Share expertise** - Package domain knowledge for reuse
- **Standardize workflows** - Define consistent approaches to common tasks
- **Customize behavior** - Teach the agent your preferred coding styles
- **Enable collaboration** - Share skill packs with your team

## Skill Structure

A skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```
my-skill/
    SKILL.md
```

### SKILL.md Format

```markdown
---
name: my-skill
description: Brief description of what this skill does
license: MIT
compatibility: Python 3.10+
metadata:
  author: Jane Doe
  version: "1.0"
allowed-tools: grep read_file write_file
---

# Detailed Instructions

The content below the frontmatter is the actual skill prompt that gets
injected into the conversation when the skill is activated.

## When to Use This Skill

Explain when and why to use this skill...

## Guidelines

1. First guideline
2. Second guideline
...
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens allowed) |
| `description` | Yes | Short description (max 1024 chars) |
| `license` | No | License name or file reference |
| `compatibility` | No | Environment requirements |
| `metadata` | No | Arbitrary key-value pairs |
| `allowed-tools` | No | Space-separated list of pre-approved tools |

### Name Constraints

- Lowercase letters, numbers, and hyphens only
- Must start with a letter or number
- Maximum 64 characters
- Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`

Valid: `code-review`, `django-api`, `test-writer-v2`
Invalid: `Code_Review`, `my skill`, `_private`

## Skill Discovery

Kin Code searches for skills in these locations (in order):

1. **Custom paths** - Directories in `skill_paths` config
2. **Local project** - `.kin-code/skills/` in working directory
3. **Global directory** - `~/.kin-code/skills/`

Earlier paths take precedence for duplicate names.

### Configuring Skill Paths

In `~/.kin-code/config.toml`:

```toml
skill_paths = [
    "~/my-skills",
    "/shared/team-skills",
]
```

## Example Skills

### Code Review Skill

```markdown
---
name: code-review
description: Systematic code review following best practices
license: MIT
metadata:
  author: Team
  version: "1.0"
allowed-tools: grep read_file
---

# Code Review Guidelines

When reviewing code, follow this systematic approach:

## 1. Security Check
- Look for hardcoded secrets or credentials
- Check for SQL injection vulnerabilities
- Verify input validation
- Review authentication/authorization logic

## 2. Code Quality
- Check for code duplication
- Verify proper error handling
- Review naming conventions
- Assess function complexity

## 3. Performance
- Identify potential bottlenecks
- Check for N+1 queries
- Review memory usage patterns
- Look for unnecessary computations

## 4. Testing
- Verify test coverage for changes
- Check edge cases are tested
- Review test quality and assertions

## Output Format

Provide findings in this format:
- **Critical**: Security issues, bugs
- **Major**: Performance problems, missing tests
- **Minor**: Style issues, suggestions
- **Positive**: Good patterns worth noting
```

### API Documentation Skill

```markdown
---
name: api-docs
description: Generate OpenAPI-compliant API documentation
license: Apache-2.0
compatibility: REST APIs
metadata:
  author: Documentation Team
  version: "2.0"
  standard: OpenAPI 3.0
allowed-tools: grep read_file write_file
---

# API Documentation Generator

Generate comprehensive API documentation following OpenAPI 3.0 spec.

## Analysis Steps

1. **Identify Endpoints**
   - Scan for route definitions
   - Note HTTP methods used
   - Extract path parameters

2. **Document Parameters**
   - Query parameters with types
   - Request body schemas
   - Header requirements

3. **Response Schemas**
   - Success response format
   - Error response structures
   - Status codes used

## Output Format

Generate documentation as:

```yaml
openapi: 3.0.0
info:
  title: API Title
  version: "1.0"
paths:
  /endpoint:
    get:
      summary: Brief description
      parameters: [...]
      responses:
        200:
          description: Success
          content:
            application/json:
              schema: {...}
```

## Best Practices

- Use clear, concise descriptions
- Include example values
- Document error responses
- Note deprecation warnings
```

### Test Writer Skill

```markdown
---
name: test-writer
description: Write comprehensive tests following pytest best practices
license: MIT
compatibility: Python with pytest
metadata:
  author: QA Team
  version: "1.5"
  framework: pytest
allowed-tools: grep read_file write_file
---

# Test Writing Guidelines

Generate comprehensive test suites using pytest.

## Test Structure

```python
import pytest
from module import function_under_test

class TestFunctionName:
    """Tests for function_name."""

    def test_basic_case(self):
        """Test the happy path."""
        result = function_under_test(valid_input)
        assert result == expected_output

    def test_edge_case(self):
        """Test boundary conditions."""
        ...

    def test_error_handling(self):
        """Test error cases."""
        with pytest.raises(ExpectedError):
            function_under_test(invalid_input)
```

## Coverage Requirements

- Test all public functions
- Cover success and failure paths
- Test edge cases (empty, null, max values)
- Test error handling and exceptions

## Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<behavior>_<scenario>`

## Fixtures

Use fixtures for common setup:

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert process(sample_data) == expected
```

## Assertions

- Use specific assertions (`assert x == y` not `assert x`)
- Include helpful error messages
- Use `pytest.approx()` for floats
```

## Using Skills

### Activating Skills

Reference skills in your conversation:

```
Use the code-review skill to review the changes in src/api.py
```

Or via the `/skill` command:

```
/skill code-review
```

### Multiple Skills

Skills can be combined:

```
Use the code-review and test-writer skills to review main.py and generate tests
```

### Skill with Parameters

Pass context to skills:

```
Use the api-docs skill to document the REST API in src/routes/
Focus on the authentication endpoints
```

## Creating Skills

### Step 1: Create Directory

```bash
mkdir -p ~/.kin-code/skills/my-skill
```

### Step 2: Write SKILL.md

Create `~/.kin-code/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: What this skill does
---

# Skill Instructions

Your detailed instructions here...
```

### Step 3: Verify Discovery

Check that your skill is found:

```bash
kin-code --list-skills
```

## Skill Validation

Skills are validated on load:

| Validation | Description |
|------------|-------------|
| Name format | Must match pattern `^[a-z0-9]+(-[a-z0-9]+)*$` |
| Name match | Directory name should match `name` field |
| Description | Required, max 1024 characters |
| YAML syntax | Frontmatter must be valid YAML |
| Frontmatter markers | Must have `---` delimiters |

### Validation Errors

Common errors and fixes:

```
Missing or invalid YAML frontmatter
  -> Ensure SKILL.md starts and ends with ---

Skill name doesn't match directory name
  -> Rename directory or update name field

Invalid skill name pattern
  -> Use lowercase letters, numbers, hyphens only
```

## Advanced Features

### Allowed Tools

Pre-approve tools for the skill:

```yaml
allowed-tools: grep read_file write_file bash
```

This suggests which tools the skill typically needs.

### Metadata

Store arbitrary data:

```yaml
metadata:
  author: Jane Doe
  version: "2.1"
  tags: security, review
  min_context: 50000
```

### Compatibility Notes

Document requirements:

```yaml
compatibility: |
  - Python 3.10+
  - Django 4.0+
  - PostgreSQL database
```

## Best Practices

1. **Clear naming** - Use descriptive, searchable names
2. **Detailed descriptions** - Help users understand when to use the skill
3. **Structured content** - Use headers and lists for clarity
4. **Concrete examples** - Show expected inputs and outputs
5. **Version tracking** - Update metadata version on changes
6. **Minimal tool list** - Only list truly needed tools in allowed-tools

## Skill Organization

### Team Skills

Create a shared repository:

```
team-skills/
    code-review/SKILL.md
    security-audit/SKILL.md
    performance-review/SKILL.md
```

Configure in each developer's `config.toml`:

```toml
skill_paths = ["/shared/team-skills"]
```

### Project Skills

Keep project-specific skills with the code:

```
my-project/
    .kin-code/
        skills/
            project-conventions/SKILL.md
            api-patterns/SKILL.md
    src/
    tests/
```

## Related Documentation

- [Custom Prompts](./custom-prompts.md) - System prompt customization
- [Custom Tools](./custom-tools.md) - Build executable tools
- [Configuration Reference](../reference/config-reference.md) - All config options

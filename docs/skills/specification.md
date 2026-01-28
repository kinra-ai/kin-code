# Skill Specification

Kin Code follows the [Agent Skills specification](https://agentskills.io/specification).

## Overview

The Agent Skills format provides a standard way to package agent capabilities. Skills are defined in `SKILL.md` files with YAML frontmatter.

## File Format

```markdown
---
name: skill-name
description: Brief description
version: 1.0.0
license: MIT
author: Author Name
compatibility: Python 3.12+
user-invocable: true
allowed-tools:
  - tool_a
  - tool_b
required-tools:
  - tool_c
---

# Skill Title

Markdown content with instructions for the agent.
```

## Frontmatter Fields

### Identification

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier |
| `description` | Yes | Brief description |
| `version` | No | Semantic version |
| `author` | No | Author name or organization |
| `license` | No | License identifier (e.g., MIT, Apache-2.0) |

### Compatibility

| Field | Required | Description |
|-------|----------|-------------|
| `compatibility` | No | Compatibility notes (e.g., "Python 3.12+") |

### Invocation

| Field | Required | Description |
|-------|----------|-------------|
| `user-invocable` | No | If true, creates a slash command |

### Tool Control

| Field | Required | Description |
|-------|----------|-------------|
| `allowed-tools` | No | Tools the skill may use |
| `required-tools` | No | Tools the skill must have |

## Markdown Content

After the frontmatter, write instructions in Markdown:

- Describe when to use the skill
- Provide step-by-step guidance
- Include examples if helpful
- Note any constraints

## Validation

Kin Code validates skills on load:
- Required fields present
- Valid YAML syntax
- Tool names are valid

Invalid skills are skipped with a warning.

## External Resources

- [Agent Skills Specification](https://agentskills.io/specification)
- [Agent Skills Registry](https://agentskills.io/)

## Related

- [Skills Overview](overview.md)
- [Creating Skills](creating-skills.md)

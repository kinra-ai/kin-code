# Creating Skills

Build custom skills to extend Kin Code.

## Skill Structure

A skill is a directory with a `SKILL.md` file:

```
my-skill/
  SKILL.md           # Required
  prompts/           # Optional
  examples/          # Optional
```

## SKILL.md Format

```markdown
---
name: my-skill
description: Description of the skill
license: MIT
compatibility: Python 3.12+
user-invocable: true
allowed-tools:
  - read_file
  - grep
---

# My Skill

Instructions for the agent when this skill is active.

## When to Use

Explain when this skill applies...

## Instructions

Step-by-step guidance for the agent...
```

## Metadata Fields

### Required

| Field | Description |
|-------|-------------|
| `name` | Unique identifier |
| `description` | Brief description |

### Optional

| Field | Description |
|-------|-------------|
| `license` | License identifier |
| `compatibility` | Compatibility notes |
| `user-invocable` | Enable as slash command |
| `allowed-tools` | Tools the skill can use |
| `required-tools` | Tools the skill needs |

## Making Skills Invocable

Set `user-invocable: true` to create a slash command:

```markdown
---
name: review
user-invocable: true
---
```

Use with:

```
> /review
```

## Skill Instructions

The markdown content after the frontmatter becomes instructions for the agent. Write clear, specific guidance:

```markdown
# Code Review Skill

When performing code reviews:

1. Check for security issues
2. Look for performance problems
3. Verify error handling
4. Review documentation

Be specific and constructive in feedback.
```

## Examples

### Simple Skill

```markdown
---
name: explain
description: Explain code in detail
user-invocable: true
---

# Code Explainer

When asked to explain code:
1. Describe the overall purpose
2. Explain key functions
3. Note any complex logic
4. Identify potential issues
```

### Restricted Skill

```markdown
---
name: safe-review
description: Read-only code review
user-invocable: true
allowed-tools:
  - read_file
  - grep
---

# Safe Code Review

Review code without making changes.
```

## Installation

Place skills in:
- Global: `~/.kin-code/skills/my-skill/SKILL.md`
- Project: `./.kin-code/skills/my-skill/SKILL.md`

## Related

- [Skills Overview](overview.md)
- [Skill Discovery](discovery.md)
- [Skill Specification](specification.md)

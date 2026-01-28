# Skills Overview

Skills are reusable components that extend Kin Code's functionality. They can add specialized behaviors, custom slash commands, and domain-specific knowledge.

## What Are Skills?

Skills are packages of functionality defined in a `SKILL.md` file. They follow the [Agent Skills specification](https://agentskills.io/specification).

A skill can:
- Provide specialized instructions for the agent
- Add custom slash commands
- Restrict or require specific tools
- Inject domain knowledge

## Skill Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
my-skill/
  SKILL.md           # Required: skill definition
  prompts/           # Optional: additional prompts
  examples/          # Optional: usage examples
```

### SKILL.md Format

```markdown
---
name: my-skill
description: A helpful skill for my workflow
license: MIT
compatibility: Python 3.12+
user-invocable: true
allowed-tools:
  - read_file
  - grep
---

# My Skill

Instructions for the agent when this skill is active.

## Usage

Describe how to use this skill...
```

## Skill Discovery

Kin Code discovers skills from:

1. **Global skills**: `~/.kin-code/skills/`
2. **Project skills**: `./.kin-code/skills/`
3. **Custom paths**: Configured in `config.toml`

```toml
skill_paths = ["/path/to/custom/skills"]
```

## Using Skills

### Slash Commands

Skills with `user-invocable: true` become slash commands:

```
> /my-skill
```

The skill's instructions are activated.

### Listing Skills

```
> /skills
```

Shows all available skills.

## Skill Metadata

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Unique skill identifier |
| `description` | Brief description |

### Optional Fields

| Field | Description |
|-------|-------------|
| `license` | License identifier |
| `compatibility` | Compatibility notes |
| `user-invocable` | Enable as slash command |
| `allowed-tools` | Tools the skill can use |
| `required-tools` | Tools the skill requires |

## Managing Skills

### Enable Specific Skills

```toml
enabled_skills = ["code-review", "testing"]
```

### Disable Skills

```toml
disabled_skills = ["experimental-*"]
```

### Pattern Matching

```toml
# Glob patterns
enabled_skills = ["code-*"]

# Regex patterns
enabled_skills = ["re:^(code|test).*$"]
```

## Built-in Skills

Kin Code may include built-in skills for common workflows. Check `/skills` for available options.

## Creating Skills

See [Creating Skills](creating-skills.md) for a detailed guide.

Quick example:

```markdown
---
name: code-review
description: Perform code reviews
user-invocable: true
allowed-tools:
  - read_file
  - grep
---

# Code Review

When reviewing code, focus on:
1. Security vulnerabilities
2. Performance issues
3. Code style
4. Best practices
```

Save as `~/.kin-code/skills/code-review/SKILL.md`.

Use with:

```
> /code-review
```

## Project-Specific Skills

Place skills in `.kin-code/skills/` for project-specific functionality:

```
my-project/
  .kin-code/
    skills/
      my-project-skill/
        SKILL.md
```

These skills are only available in that project.

## Skill Security

Skills can modify agent behavior. Consider:

1. **Review skills before enabling** - Especially third-party
2. **Use allowed-tools** - Restrict what skills can do
3. **Trust folder system** - Project skills require trust

## Related

- [Creating Skills](creating-skills.md)
- [Skill Discovery](discovery.md)
- [Managing Skills](managing.md)
- [Skill Specification](specification.md)

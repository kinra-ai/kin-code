# Skills

Skills are reusable components that extend Kin Code's functionality. This section covers what skills are, how to use them, and how to create your own.

## Quick Links

| Topic | Description |
|-------|-------------|
| [Overview](overview.md) | Skills system introduction and concepts |
| [Creating Skills](creating-skills.md) | Build your own skills |
| [Discovery](discovery.md) | Where skills are loaded from |
| [Managing Skills](managing.md) | Enable and disable skills |
| [Specification](specification.md) | The Agent Skills format |

## What Are Skills?

Skills are packages of specialized functionality that you can add to Kin Code. They follow the [Agent Skills specification](https://agentskills.io/specification) and can:

- **Add domain knowledge** - Instructions for specific tasks
- **Provide slash commands** - New `/command` shortcuts
- **Restrict tools** - Limit what tools are available
- **Inject context** - Add relevant information automatically

Think of skills as plugins that teach Kin Code new capabilities or specialize its behavior for particular workflows.

## Example Skills

### Code Review Skill

A skill that configures Kin Code for code reviews:

```markdown
---
name: code-review
description: Perform thorough code reviews
user-invocable: true
allowed-tools:
  - read_file
  - grep
---

# Code Review

When reviewing code, focus on:
1. Security vulnerabilities
2. Performance issues
3. Code style and consistency
4. Best practices adherence
```

Use with:
```
> /code-review
```

### Testing Skill

A skill for test-driven development:

```markdown
---
name: testing
description: Test-driven development assistance
user-invocable: true
---

# Testing

Help write comprehensive tests following TDD principles:
1. Write failing test first
2. Implement minimum code to pass
3. Refactor while keeping tests green
```

## Skill Discovery

Kin Code discovers skills from three locations:

| Location | Description |
|----------|-------------|
| `~/.kin-code/skills/` | Global skills available everywhere |
| `./.kin-code/skills/` | Project-specific skills |
| Custom paths | Configured via `skill_paths` |

Skills in project directories are only available in that project.

See [Discovery](discovery.md) for details.

## Using Skills

### As Slash Commands

Skills with `user-invocable: true` become slash commands:

```
> /code-review
```

The skill's instructions are activated for the conversation.

### Listing Skills

See all available skills:

```
> /skills
```

### Automatic Activation

Some skills activate automatically based on context. For example, a Python skill might activate when working in a Python project.

## Skill Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
my-skill/
  SKILL.md           # Required: skill definition
  prompts/           # Optional: additional prompts
  examples/          # Optional: usage examples
  resources/         # Optional: data files
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
required-tools:
  - bash
---

# My Skill

Instructions for the agent when this skill is active.

## Usage

Describe how to use this skill...

## Examples

Show example interactions...
```

## Skill Metadata

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Unique skill identifier |
| `description` | Brief description of what the skill does |

### Optional Fields

| Field | Description |
|-------|-------------|
| `license` | License identifier (e.g., MIT, Apache-2.0) |
| `compatibility` | Compatibility notes |
| `user-invocable` | Enable as slash command (true/false) |
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

See [Managing Skills](managing.md) for details.

## Creating Your First Skill

1. Create a skill directory:
   ```bash
   mkdir -p ~/.kin-code/skills/my-skill
   ```

2. Create `SKILL.md`:
   ```markdown
   ---
   name: my-skill
   description: My custom skill
   user-invocable: true
   ---

   # My Skill

   Custom instructions here...
   ```

3. Use your skill:
   ```
   > /my-skill
   ```

See [Creating Skills](creating-skills.md) for a complete guide.

## Project-Specific Skills

Place skills in your project's `.kin-code/skills/` directory:

```
my-project/
  .kin-code/
    skills/
      project-skill/
        SKILL.md
  src/
  tests/
```

These skills are only available when working in that project.

## Skill Security

Skills can modify agent behavior, so consider:

1. **Review skills before enabling** - Especially third-party skills
2. **Use `allowed-tools`** - Restrict what skills can do
3. **Trust folder system** - Project skills require directory trust

## Built-in Skills

Kin Code may include built-in skills. Check `/skills` to see what's available in your installation.

Common built-in skills:
- `test` - Testing assistance
- `review` - Code review
- `docs` - Documentation generation

---

**Related Pages**

- [Agents](../agents/index.md) - Agent profiles and customization
- [Configuration](../configuration/index.md) - Configure skill paths and enablement
- [Tools](../tools/index.md) - Tool permissions and configuration
- [Documentation Home](../index.md) - All documentation sections

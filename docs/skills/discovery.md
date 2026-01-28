# Skill Discovery

How Kin Code finds and loads skills.

## Discovery Locations

Kin Code looks for skills in these locations (in order):

### 1. Global Skills

```
~/.kin-code/skills/
```

Skills here are available in all projects.

### 2. Project Skills

```
./.kin-code/skills/
```

Skills here are only available in the current project.

### 3. Custom Paths

Configured in `config.toml`:

```toml
skill_paths = [
  "/path/to/custom/skills",
  "~/shared-skills"
]
```

## Directory Structure

Each skill is a directory containing `SKILL.md`:

```
skills/
  code-review/
    SKILL.md
  testing/
    SKILL.md
  custom/
    SKILL.md
```

## Discovery Process

1. Kin Code scans each skill location
2. Finds directories containing `SKILL.md`
3. Parses the SKILL.md frontmatter
4. Validates required fields
5. Registers valid skills

## Viewing Available Skills

List discovered skills:

```
> /skills
```

## Priority

When skills have the same name:
1. Project skills override global skills
2. Earlier paths in `skill_paths` have priority

## Troubleshooting

### Skill Not Found

- Check the directory exists
- Verify `SKILL.md` is present
- Check frontmatter is valid YAML
- Ensure required fields are present

### Skill Not Loading

- Check for YAML syntax errors in frontmatter
- Verify the skill isn't disabled in config
- Check file permissions

## Related

- [Skills Overview](overview.md)
- [Managing Skills](managing.md)

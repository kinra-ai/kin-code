# Managing Skills

Enable, disable, and configure skills.

## Listing Skills

View available skills:

```
> /skills
```

## Enabling Skills

### Enable Specific Skills

```toml
enabled_skills = ["code-review", "testing"]
```

When `enabled_skills` is set, only listed skills are active.

### Enable with Patterns

```toml
# Glob patterns
enabled_skills = ["code-*", "test-*"]

# Regex patterns
enabled_skills = ["re:^(code|test).*$"]
```

## Disabling Skills

### Disable Specific Skills

```toml
disabled_skills = ["experimental", "deprecated"]
```

### Disable with Patterns

```toml
disabled_skills = ["experimental-*"]
```

## Priority

If both `enabled_skills` and `disabled_skills` are set:
1. `enabled_skills` whitelist is applied first
2. `disabled_skills` removes from the whitelist

## Per-Project Configuration

Project-level `.kin-code/config.toml` can override skill settings:

```toml
# Enable project-specific skills
enabled_skills = ["my-project-skill"]

# Disable global skills
disabled_skills = ["general-skill"]
```

## Skill Paths

Add custom skill directories:

```toml
skill_paths = [
  "/shared/team-skills",
  "~/my-skills"
]
```

## Troubleshooting

### Skill Not Available

1. Check it's in a discovery location
2. Verify it's not in `disabled_skills`
3. If `enabled_skills` is set, verify it's listed
4. Run `/skills` to see what's loaded

### Skill Conflicts

If two skills have the same name, the one in the higher-priority location wins (project > global > custom paths).

## Related

- [Skills Overview](overview.md)
- [Skill Discovery](discovery.md)

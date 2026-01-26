# Config File

Kin Code is configured via a `config.toml` file.

## File Location

Kin looks for configuration in this order:

1. `./.kin-code/config.toml` (project-local)
2. `~/.kin-code/config.toml` (global)

Project-local configuration takes precedence over global settings.

## Creating a Config File

On first run, Kin creates a default config at `~/.kin-code/config.toml`.

You can also create a project-specific config:

```bash
mkdir -p .kin-code
touch .kin-code/config.toml
```

## Basic Structure

```toml
# Active model alias
active_model = "devstral-2"

# UI settings
textual_theme = "terminal"
vim_keybindings = false

# Feature flags
include_project_context = true
enable_update_checks = true

# Context management
auto_compact_threshold = 200000
```

## Reloading Configuration

After editing `config.toml`, reload without restarting:

```
> /reload
```

## Custom Home Directory

Override the config location with `KIN_HOME`:

```bash
export KIN_HOME="/path/to/custom/kin/home"
```

This affects where Kin looks for:
- `config.toml`
- `.env`
- `agents/`
- `prompts/`
- `tools/`
- `logs/`

## Next Steps

- [API Keys](./api-keys.md) - Configure provider credentials
- [Providers](./providers.md) - Add custom API endpoints
- [Models](./models.md) - Configure available models
- [Config Reference](../reference/config-reference.md) - Full schema

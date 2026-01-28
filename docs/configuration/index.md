# Configuration

Kin Code is highly configurable to match your workflow. This section covers all configuration options, from basic setup to advanced customization.

## Quick Links

| Topic | Description |
|-------|-------------|
| [Overview](overview.md) | Configuration system introduction |
| [Config File](config-file.md) | Complete config.toml reference |
| [API Keys](api-keys.md) | Provider credentials setup |
| [Models](models.md) | Model selection and providers |
| [Themes](themes.md) | Visual customization |
| [Auto Updates](auto-updates.md) | Update settings |

## Configuration Locations

Kin Code uses a layered configuration system:

| Location | Description | Priority |
|----------|-------------|----------|
| Command-line flags | `kin --agent plan` | Highest |
| Environment variables | `KIN_MODEL=gpt-4o` | High |
| Project config | `./.kin-code/config.toml` | Medium |
| User config | `~/.kin-code/config.toml` | Low |
| Defaults | Built-in defaults | Lowest |

Higher priority settings override lower priority ones.

## Configuration Directory

The default configuration directory is `~/.kin-code/`:

```
~/.kin-code/
  config.toml          # Main configuration
  .env                 # API keys and secrets
  trusted_folders.toml # Trusted directory list
  agents/              # Custom agent configurations
  prompts/             # Custom system prompts
  skills/              # Global skills
  tools/               # Custom tools
  logs/                # Session logs
```

### Custom Configuration Directory

Override with the `KIN_HOME` environment variable:

```bash
export KIN_HOME="/path/to/custom/config"
```

## Quick Configuration Tasks

### Set Your API Key

Interactive setup:
```bash
kin --setup
```

Or manually add to `~/.kin-code/.env`:
```bash
OPENAI_API_KEY=sk-...
```

See [API Keys](api-keys.md) for all providers.

### Change the Default Model

In `~/.kin-code/config.toml`:
```toml
active_model = "gpt-4o"
```

Or at runtime:
```bash
kin --model claude-3-5-sonnet
```

See [Models](models.md) for available options.

### Configure Tool Permissions

```toml
[tools.read_file]
permission = "always"  # Never ask for approval

[tools.bash]
permission = "ask"     # Ask before executing

[tools.write_file]
permission = "ask"
```

### Disable Tools

```toml
disabled_tools = ["bash", "write_file"]
```

### Add MCP Servers

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

See [MCP Configuration](../mcp/configuration.md) for details.

### Configure Skills

```toml
# Additional skill directories
skill_paths = ["/path/to/custom/skills"]

# Enable specific skills
enabled_skills = ["code-review", "testing"]

# Disable skills
disabled_skills = ["experimental-*"]
```

See [Managing Skills](../skills/managing.md) for details.

## Configuration File Reference

### General Settings

```toml
# Model selection
active_model = "gpt-4o"

# System prompt
system_prompt_id = "cli"

# Auto-update behavior
enable_auto_update = true

# Session logging
enable_session_logging = true
log_directory = "~/.kin-code/logs"
```

### Tool Settings

```toml
# Global tool controls
enabled_tools = []      # Empty = all enabled
disabled_tools = []     # Tools to disable

# Per-tool permissions
[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"
```

### MCP Servers

```toml
[[mcp_servers]]
name = "server-name"
transport = "stdio"     # or "http", "streamable-http"
command = "command"
args = ["arg1", "arg2"]
env = { KEY = "value" }
```

### Skills

```toml
skill_paths = []
enabled_skills = []
disabled_skills = []
```

## Minimal Configuration

A minimal `config.toml` only needs:

```toml
active_model = "gpt-4o"
```

Everything else uses sensible defaults.

## Full Example

A comprehensive configuration:

```toml
# Model and prompts
active_model = "gpt-4o"
system_prompt_id = "cli"

# Updates
enable_auto_update = true

# Session logging
enable_session_logging = true
log_directory = "~/.kin-code/logs"

# Tools
disabled_tools = []

[tools.bash]
permission = "ask"

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "ask"

[tools.grep]
permission = "always"

# MCP Servers
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]

# Skills
skill_paths = []
enabled_skills = []
disabled_skills = []
```

## Project Configuration

Create `.kin-code/config.toml` in your project for project-specific settings:

```toml
# Project-specific model
active_model = "claude-3-5-sonnet"

# Disable shell for this project
disabled_tools = ["bash"]

# Enable project-specific skills
enabled_skills = ["project-workflow"]
```

Project configuration merges with user configuration.

## Validating Configuration

Test your configuration:

```bash
kin --setup
```

Invalid configuration produces clear error messages on startup.

## Environment Variables

Key environment variables:

| Variable | Description |
|----------|-------------|
| `KIN_HOME` | Configuration directory |
| `KIN_MODEL` | Override default model |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |

See [Environment Variables](../api-reference/environment-variables.md) for the complete list.

---

**Related Pages**

- [Tools](../tools/index.md) - Tool permissions and configuration
- [Agents](../agents/index.md) - Agent configuration
- [Skills](../skills/index.md) - Skills configuration
- [MCP](../mcp/overview.md) - MCP server configuration
- [Documentation Home](../index.md) - All documentation sections

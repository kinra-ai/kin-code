# Configuration Overview

Kin Code is highly configurable through TOML configuration files. This guide introduces the configuration system.

## Configuration Locations

Kin Code looks for configuration in these locations (in order of precedence):

1. **Project-level**: `./.kin-code/config.toml` (current directory)
2. **User-level**: `~/.kin-code/config.toml` (home directory)

Project-level configuration overrides user-level settings.

## Configuration Directory

The default configuration directory is `~/.kin-code/` and contains:

```
~/.kin-code/
  config.toml        # Main configuration
  .env               # API keys and secrets
  trusted_folders.toml  # Trusted folder list
  agents/            # Custom agent configurations
  prompts/           # Custom system prompts
  skills/            # Global skills
  tools/             # Custom tools
  logs/              # Session logs
```

### Custom Home Directory

Override with the `KIN_HOME` environment variable:

```bash
export KIN_HOME="/path/to/custom/kin/home"
```

## Configuration File Structure

The `config.toml` file is organized into sections:

```toml
# General settings
active_model = "gpt-4o"
system_prompt_id = "cli"
enable_auto_update = true
enable_session_logging = true

# Tool settings
enabled_tools = []
disabled_tools = []

[tools.bash]
permission = "ask"

# MCP servers
[[mcp_servers]]
name = "my-server"
transport = "stdio"
command = "my-server-command"

# Skills
skill_paths = []
enabled_skills = []
disabled_skills = []
```

## Key Configuration Areas

### Model Selection

```toml
active_model = "gpt-4o"
```

Select your default AI model. See [Models](models.md) for options.

### API Keys

API keys are stored in `.env`, not `config.toml`:

```bash
# ~/.kin-code/.env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

See [API Keys](api-keys.md) for details.

### Tool Permissions

Control which tools are enabled and their approval requirements:

```toml
disabled_tools = ["bash"]

[tools.read_file]
permission = "always"  # Never ask
```

See [Tool Configuration](../tools/permissions.md) for details.

### MCP Servers

Integrate external tools via MCP:

```toml
[[mcp_servers]]
name = "fetch"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

See [MCP Configuration](../mcp/configuration.md) for details.

### Skills

Configure skill discovery and enablement:

```toml
skill_paths = ["/path/to/skills"]
enabled_skills = ["code-review"]
disabled_skills = ["experimental-*"]
```

See [Managing Skills](../skills/managing.md) for details.

## Configuration Precedence

When the same setting exists in multiple places:

1. Command-line flags (highest priority)
2. Environment variables
3. Project-level `config.toml`
4. User-level `config.toml`
5. Default values (lowest priority)

## Minimal Configuration

A minimal `config.toml`:

```toml
active_model = "gpt-4o"
```

Everything else uses defaults.

## Full Example

A comprehensive configuration example:

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

## Validating Configuration

Kin Code validates configuration on startup. Invalid configuration produces clear error messages.

To test your configuration:

```bash
kin --setup
```

## Related

- [Config File](config-file.md) - Detailed config.toml reference
- [API Keys](api-keys.md) - Credential configuration
- [Models](models.md) - Model selection

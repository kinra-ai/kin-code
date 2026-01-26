# Config Reference

Complete reference for `config.toml` options.

## Top-Level Options

```toml
# Model to use (by alias)
active_model = "devstral-2"

# UI theme
textual_theme = "terminal"

# Enable vim-style keybindings
vim_keybindings = false

# Disable welcome animation
disable_welcome_banner_animation = false

# Custom working directory display
displayed_workdir = ""

# Token threshold for auto-compaction
auto_compact_threshold = 200000

# Show context usage warnings
context_warnings = false

# Additional instructions appended to system prompt
instructions = ""

# System prompt identifier (built-in or custom)
system_prompt_id = "cli"

# Include commit signature in git operations
include_commit_signature = true

# Include model info in responses
include_model_info = true

# Include project context in system prompt
include_project_context = true

# Include detailed prompt information
include_prompt_detail = true

# Check for updates on startup
enable_update_checks = true

# API request timeout in seconds
api_timeout = 720.0
```

## Providers

```toml
[[providers]]
name = "mistral"                           # Unique identifier
api_base = "https://api.mistral.ai/v1"     # API endpoint
api_key_env_var = "MISTRAL_API_KEY"        # Environment variable for API key
api_style = "openai"                       # API style (openai)
backend = "mistral"                        # Backend type (mistral or generic)
reasoning_field_name = "reasoning_content" # Field name for reasoning
```

## Models

```toml
[[models]]
name = "mistral-vibe-cli-latest"  # Model identifier sent to API
provider = "mistral"              # Must match a provider name
alias = "devstral-2"              # Short name (must be unique)
temperature = 0.2                 # Sampling temperature
input_price = 0.4                 # Price per million input tokens
output_price = 2.0                # Price per million output tokens
context_window = 128000           # Maximum context size
supports_tools = true             # Whether model supports tool calling
```

## Project Context

```toml
[project_context]
max_chars = 40000          # Maximum characters for project context
default_commit_count = 5   # Git commits to include
max_doc_bytes = 32768      # Max bytes for documentation files
truncation_buffer = 1000   # Buffer for truncation
max_depth = 3              # Directory traversal depth
max_files = 1000           # Maximum files to scan
max_dirs_per_level = 20    # Max directories per level
timeout_seconds = 2.0      # Scan timeout
```

## Session Logging

```toml
[session_logging]
enabled = true                    # Enable session logging
save_dir = "~/.kin-code/logs"     # Log directory
session_prefix = "session"        # Log file prefix
```

## Tool Configuration

```toml
# Global tool enable/disable
enabled_tools = []           # Only these tools active (if set)
disabled_tools = []          # Disable these tools

# Additional tool search paths
tool_paths = ["~/.kin-code/tools"]

# Per-tool configuration
[tools.bash]
permission = "ask"           # always, ask, or never
allowlist = ["git *"]        # Auto-approve patterns
denylist = ["rm -rf *"]      # Auto-deny patterns

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "ask"
```

## MCP Servers

### HTTP Transport

```toml
[[mcp_servers]]
name = "my_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer token" }
api_key_env = "MY_API_KEY"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"
prompt = "Usage hint for this server"
```

### Streamable HTTP Transport

```toml
[[mcp_servers]]
name = "streaming_server"
transport = "streamable-http"
url = "http://localhost:8001"
headers = { "X-API-Key" = "key" }
```

### Stdio Transport

```toml
[[mcp_servers]]
name = "local_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

## Skills

```toml
# Additional skill search paths
skill_paths = ["~/.kin-code/skills"]
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `KIN_HOME` | Override default config directory |
| `MISTRAL_API_KEY` | Mistral API key |
| Any `api_key_env_var` | Provider-specific API keys |

## File Locations

| Path | Purpose |
|------|---------|
| `~/.kin-code/config.toml` | Global configuration |
| `./.kin-code/config.toml` | Project-local configuration |
| `~/.kin-code/.env` | API keys |
| `~/.kin-code/agents/` | Custom agent configurations |
| `~/.kin-code/prompts/` | Custom system prompts |
| `~/.kin-code/tools/` | Custom tools |
| `~/.kin-code/logs/` | Session logs |

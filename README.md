# Kin Code

[![PyPI Version](https://img.shields.io/pypi/v/kin-code)](https://pypi.org/project/kin-code)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/release/python-3120/)
[![CI Status](https://github.com/kinra-ai/kin-code/actions/workflows/ci.yml/badge.svg)](https://github.com/kinra-ai/kin-code/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/kinra-ai/kin-code)](https://github.com/kinra-ai/kin-code/blob/main/LICENSE)

**An open-source CLI coding assistant.**

Kin Code is a command-line coding assistant powered by Mistral's models. It provides a conversational interface to your codebase, allowing you to use natural language to explore, modify, and interact with your projects through a powerful set of tools.

> [!WARNING]
> Kin Code works on Windows, but we officially support and target UNIX environments.

### Using uv (recommended)

```bash
uv tool install kin-code
```

### Using pip

```bash
pip install kin-code
```

## Features

- **Interactive Chat**: A conversational AI agent that understands your requests and breaks down complex tasks.
- **Powerful Toolset**: A suite of tools for file manipulation, code searching, version control, and command execution, right from the chat prompt.
  - Read, write, and patch files (`read_file`, `write_file`, `search_replace`).
  - Execute shell commands in a stateful terminal (`bash`).
  - Recursively search code with `grep` (with `ripgrep` support).
  - Manage a `todo` list to track the agent's work.
- **Project-Aware Context**: Kin automatically scans your project's file structure and Git status to provide relevant context to the agent, improving its understanding of your codebase.
- **Advanced CLI Experience**: Built with modern libraries for a smooth and efficient workflow.
  - Autocompletion for slash commands (`/`) and file paths (`@`).
  - Persistent command history.
  - Beautiful Themes.
- **Highly Configurable**: Customize models, providers, tool permissions, and UI preferences through a simple `config.toml` file.
- **Safety First**: Features tool execution approval.

## Quick Start

1. Navigate to your project's root directory:

   ```bash
   cd /path/to/your/project
   ```

2. Run Kin:

   ```bash
   kin
   ```

3. If this is your first time running Kin, it will:

   - Create a default configuration file at `~/.kin-code/config.toml`
   - Prompt you to enter your API key if it's not already configured
   - Save your API key to `~/.kin-code/.env` for future use

4. Start interacting with the agent!

   ```
   > Can you find all instances of the word "TODO" in the project?

   The user wants to find all instances of "TODO". The `grep` tool is perfect for this. I will use it to search the current directory.

   > grep(pattern="TODO", path=".")

   ... (grep tool output) ...

   I found the following "TODO" comments in your project.
   ```

## Usage

### Interactive Mode

Simply run `kin` to enter the interactive chat loop.

- **Multi-line Input**: Press `Ctrl+J` or `Shift+Enter` for select terminals to insert a newline.
- **File Paths**: Reference files in your prompt using the `@` symbol for smart autocompletion (e.g., `> Read the file @src/agent.py`).
- **Shell Commands**: Prefix any command with `!` to execute it directly in your shell, bypassing the agent (e.g., `> !ls -l`).

You can start Kin with a prompt with the following command:

```bash
kin "Refactor the main function in cli/main.py to be more modular."
```

**Note**: The `--auto-approve` flag automatically approves all tool executions without prompting. In interactive mode, you can also toggle auto-approve on/off using `Shift+Tab`.

### Programmatic Mode

You can run Kin non-interactively by piping input or using the `--prompt` flag. This is useful for scripting.

```bash
kin --prompt "Refactor the main function in cli/main.py to be more modular."
```

by default it will use `auto-approve` mode.

### Slash Commands

Use slash commands for meta-actions and configuration changes during a session.

## Configuration

Kin is configured via a `config.toml` file. It looks for this file first in `./.kin-code/config.toml` and then falls back to `~/.kin-code/config.toml`.

### API Key Configuration

Kin supports multiple ways to configure your API keys:

1. **Interactive Setup (Recommended for first-time users)**: When you run Kin for the first time or if your API key is missing, Kin will prompt you to enter it. The key will be securely saved to `~/.kin-code/.env` for future sessions.

2. **Environment Variables**: Set your API key as an environment variable:

   ```bash
   export MISTRAL_API_KEY="your_mistral_api_key"
   ```

3. **`.env` File**: Create a `.env` file in `~/.kin-code/` and add your API keys:

   ```bash
   MISTRAL_API_KEY=your_mistral_api_key
   ```

   Kin automatically loads API keys from `~/.kin-code/.env` on startup. Environment variables take precedence over the `.env` file if both are set.

**Note**: The `.env` file is specifically for API keys and other provider credentials. General Kin configuration should be done in `config.toml`.

### Custom System Prompts

You can create custom system prompts to replace the default one (`prompts/cli.md`). Create a markdown file in the `~/.kin-code/prompts/` directory with your custom prompt content.

To use a custom system prompt, set the `system_prompt_id` in your configuration to match the filename (without the `.md` extension):

```toml
# Use a custom system prompt
system_prompt_id = "my_custom_prompt"
```

This will load the prompt from `~/.kin-code/prompts/my_custom_prompt.md`.

### Custom Agent Configurations

You can create custom agent configurations for specific use cases (e.g., red-teaming, specialized tasks) by adding agent-specific TOML files in the `~/.kin-code/agents/` directory.

To use a custom agent, run Kin with the `--agent` flag:

```bash
kin --agent my_custom_agent
```

Kin will look for a file named `my_custom_agent.toml` in the agents directory and apply its configuration.

Example custom agent configuration (`~/.kin-code/agents/redteam.toml`):

```toml
# Custom agent configuration for red-teaming
active_model = "devstral-2"
system_prompt_id = "redteam"

# Disable some tools for this agent
disabled_tools = ["search_replace", "write_file"]

# Override tool permissions for this agent
[tools.bash]
permission = "always"

[tools.read_file]
permission = "always"
```

Note: this implies that you have setup a redteam prompt names `~/.kin-code/prompts/redteam.md`

### MCP Server Configuration

You can configure MCP (Model Context Protocol) servers to extend Kin's capabilities. Add MCP server configurations under the `mcp_servers` section:

```toml
# Example MCP server configurations
[[mcp_servers]]
name = "my_http_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer my_token" }
api_key_env = "MY_API_KEY_ENV_VAR"
api_key_header = "Authorization"
api_key_format = "Bearer {token}"

[[mcp_servers]]
name = "my_streamable_server"
transport = "streamable-http"
url = "http://localhost:8001"
headers = { "X-API-Key" = "my_api_key" }

[[mcp_servers]]
name = "fetch_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]
```

Supported transports:

- `http`: Standard HTTP transport
- `streamable-http`: HTTP transport with streaming support
- `stdio`: Standard input/output transport (for local processes)

Key fields:

- `name`: A short alias for the server (used in tool names)
- `transport`: The transport type
- `url`: Base URL for HTTP transports
- `headers`: Additional HTTP headers
- `api_key_env`: Environment variable containing the API key
- `command`: Command to run for stdio transport
- `args`: Additional arguments for stdio transport

MCP tools are named using the pattern `{server_name}_{tool_name}` and can be configured with permissions like built-in tools:

```toml
# Configure permissions for specific MCP tools
[tools.fetch_server_get]
permission = "always"

[tools.my_http_server_query]
permission = "ask"
```

### Enable/disable tools with patterns

You can control which tools are active using `enabled_tools` and `disabled_tools`.
These fields support exact names, glob patterns, and regular expressions.

Examples:

```toml
# Only enable tools that start with "serena_" (glob)
enabled_tools = ["serena_*"]

# Regex (prefix with re:) — matches full tool name (case-insensitive)
enabled_tools = ["re:^serena_.*$"]

# Heuristic regex support (patterns like `serena.*` are treated as regex)
enabled_tools = ["serena.*"]

# Disable a group with glob; everything else stays enabled
disabled_tools = ["mcp_*", "grep"]
```

Notes:

- MCP tool names use underscores, e.g., `serena_list` not `serena.list`.
- Regex patterns are matched against the full tool name using fullmatch.

### Custom Kin Home Directory

By default, Kin stores its configuration in `~/.kin-code/`. You can override this by setting the `KIN_HOME` environment variable:

```bash
export KIN_HOME="/path/to/custom/kin/home"
```

This affects where Kin looks for:

- `config.toml` - Main configuration
- `.env` - API keys
- `agents/` - Custom agent configurations
- `prompts/` - Custom system prompts
- `tools/` - Custom tools
- `logs/` - Session logs

## Editors/IDEs

Kin Code can be used in text editors and IDEs that support [Agent Client Protocol](https://agentclientprotocol.com/overview/clients). See the [ACP Setup documentation](docs/acp-setup.md) for setup instructions for various editors and IDEs.

## Resources

- [CHANGELOG](CHANGELOG.md) - See what's new in each version
- [CONTRIBUTING](CONTRIBUTING.md) - Guidelines for feedback and bug reports

## License

Copyright 2025 Kinra

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the [LICENSE](LICENSE) file for the full license text.

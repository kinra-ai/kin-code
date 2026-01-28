# Kin Code

[![PyPI Version](https://img.shields.io/pypi/v/kin-code)](https://pypi.org/project/kin-code)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/github/license/kinra-ai/kin-code)](https://github.com/kinra-ai/kin-code/blob/main/LICENSE)

```
██████████████████░░
██████████████████░░
████  ██████  ████░░
████    ██    ████░░
████          ████░░
████  ██  ██  ████░░
██      ██      ██░░
██████████████████░░
██████████████████░░
```

**An AI-powered CLI coding assistant.**

Kin Code is a command-line coding assistant powered by AI models. It provides a conversational interface to your codebase, allowing you to use natural language to explore, modify, and interact with your projects through a powerful set of tools.

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

## Table of Contents

- [Features](#features)
  - [Built-in Agents](#built-in-agents)
  - [Subagents and Task Delegation](#subagents-and-task-delegation)
  - [Interactive User Questions](#interactive-user-questions)
- [Terminal Requirements](#terminal-requirements)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Trust Folder System](#trust-folder-system)
  - [Programmatic Mode](#programmatic-mode)
- [Slash Commands](#slash-commands)
  - [Built-in Slash Commands](#built-in-slash-commands)
  - [Custom Slash Commands via Skills](#custom-slash-commands-via-skills)
- [Skills System](#skills-system)
  - [Creating Skills](#creating-skills)
  - [Skill Discovery](#skill-discovery)
  - [Managing Skills](#managing-skills)
- [Configuration](#configuration)
  - [Configuration File Location](#configuration-file-location)
  - [API Key Configuration](#api-key-configuration)
  - [Custom System Prompts](#custom-system-prompts)
  - [Custom Agent Configurations](#custom-agent-configurations)
  - [Tool Management](#tool-management)
  - [MCP Server Configuration](#mcp-server-configuration)
  - [Session Management](#session-management)
  - [Update Settings](#update-settings)
  - [Custom Kin Code Home Directory](#custom-kin-code-home-directory)
- [Editors/IDEs](#editorsides)
- [Resources](#resources)
- [License](#license)

## Features

- **Interactive Chat**: A conversational AI agent that understands your requests and breaks down complex tasks.
- **Powerful Toolset**: A suite of tools for file manipulation, code searching, version control, and command execution, right from the chat prompt.
  - Read, write, and patch files (`read_file`, `write_file`, `search_replace`).
  - Execute shell commands in a stateful terminal (`bash`).
  - Recursively search code with `grep` (with `ripgrep` support).
  - Manage a `todo` list to track the agent's work.
  - Ask interactive questions to gather user input (`ask_user_question`).
  - Delegate tasks to subagents for parallel work (`task`).
- **Project-Aware Context**: Kin Code automatically scans your project's file structure and Git status to provide relevant context to the agent, improving its understanding of your codebase.
- **Advanced CLI Experience**: Built with modern libraries for a smooth and efficient workflow.
  - Autocompletion for slash commands (`/`) and file paths (`@`).
  - Persistent command history.
  - Beautiful Themes.
- **Highly Configurable**: Customize models, providers, tool permissions, and UI preferences through a simple `config.toml` file.
- **Safety First**: Features tool execution approval.
- **Multiple Built-in Agents**: Choose from different agent profiles tailored for specific workflows.

### Built-in Agents

Kin Code comes with several built-in agent profiles, each designed for different use cases:

- **`default`**: Standard agent that requires approval for tool executions. Best for general use.
- **`plan`**: Read-only agent for exploration and planning. Auto-approves safe tools like `grep` and `read_file`.
- **`accept-edits`**: Auto-approves file edits only (`write_file`, `search_replace`). Useful for code refactoring.
- **`auto-approve`**: Auto-approves all tool executions. Use with caution.

Use the `--agent` flag to select a different agent:

```bash
kin --agent plan
```

### Subagents and Task Delegation

Kin Code supports subagents for delegating tasks. Subagents run independently and can perform specialized work without user interaction, preventing the context from being overloaded.

The `task` tool allows the agent to delegate work to subagents:

```
> Can you explore the codebase structure while I work on something else?

🤖 I'll use the task tool to delegate this to the explore subagent.

> task(task="Analyze the project structure and architecture", agent="explore")
```

Create custom subagents by adding `agent_type = "subagent"` to your agent configuration. Kin Code comes with a built-in subagent called `explore`, a read-only subagent for codebase exploration used internally for delegation.

### Interactive User Questions

The `ask_user_question` tool allows the agent to ask you clarifying questions during its work. This enables more interactive and collaborative workflows.

```
> Can you help me refactor this function?

🤖 I need to understand your requirements better before proceeding.

> ask_user_question(questions=[{
    "question": "What's the main goal of this refactoring?",
    "options": [
        {"label": "Performance", "description": "Make it run faster"},
        {"label": "Readability", "description": "Make it easier to understand"},
        {"label": "Maintainability", "description": "Make it easier to modify"}
    ]
}])
```

The agent can ask multiple questions at once, displayed as tabs. Each question supports 2-4 options plus an automatic "Other" option for free text responses.

## Terminal Requirements

Kin Code's interactive interface requires a modern terminal emulator. Recommended terminal emulators include:

- **WezTerm** (cross-platform)
- **Alacritty** (cross-platform)
- **Ghostty** (Linux and macOS)
- **Kitty** (Linux and macOS)

Most modern terminals should work, but older or minimal terminal emulators may have display issues.

## Quick Start

1. Navigate to your project's root directory:

   ```bash
   cd /path/to/your/project
   ```

2. Run Kin Code:

   ```bash
   kin
   ```

3. If this is your first time running Kin Code, it will:

   - Create a default configuration file at `~/.kin-code/config.toml`
   - Prompt you to enter your API key if it's not already configured
   - Save your API key to `~/.kin-code/.env` for future use

   Alternatively, you can configure your API key separately using `kin --setup`.

4. Start interacting with the agent!

   ```
   > Can you find all instances of the word "TODO" in the project?

   🤖 The user wants to find all instances of "TODO". The `grep` tool is perfect for this. I will use it to search the current directory.

   > grep(pattern="TODO", path=".")

   ... (grep tool output) ...

   🤖 I found the following "TODO" comments in your project.
   ```

## Usage

### Interactive Mode

Simply run `kin` to enter the interactive chat loop.

- **Multi-line Input**: Press `Ctrl+J` or `Shift+Enter` for select terminals to insert a newline.
- **File Paths**: Reference files in your prompt using the `@` symbol for smart autocompletion (e.g., `> Read the file @src/agent.py`).
- **Shell Commands**: Prefix any command with `!` to execute it directly in your shell, bypassing the agent (e.g., `> !ls -l`).
- **External Editor**: Press `Ctrl+G` to edit your current input in an external editor.
- **Tool Output Toggle**: Press `Ctrl+O` to toggle the tool output view.
- **Todo View Toggle**: Press `Ctrl+T` to toggle the todo list view.
- **Auto-Approve Toggle**: Press `Shift+Tab` to toggle auto-approve mode on/off.

You can start Kin Code with a prompt using the following command:

```bash
kin "Refactor the main function in cli/main.py to be more modular."
```

**Note**: The `--auto-approve` flag automatically approves all tool executions without prompting. In interactive mode, you can also toggle auto-approve on/off using `Shift+Tab`.

### Trust Folder System

Kin Code includes a trust folder system to ensure you only run the agent in directories you trust. When you first run Kin Code in a new directory which contains a `.kin-code` subfolder, it may ask you to confirm whether you trust the folder.

Trusted folders are remembered for future sessions. You can manage trusted folders through its configuration file `~/.kin-code/trusted_folders.toml`.

This safety feature helps prevent accidental execution in sensitive directories.

### Programmatic Mode

You can run Kin Code non-interactively by piping input or using the `--prompt` flag. This is useful for scripting.

```bash
kin --prompt "Refactor the main function in cli/main.py to be more modular."
```

By default, it uses `auto-approve` mode.

#### Programmatic Mode Options

When using `--prompt`, you can specify additional options:

- **`--max-turns N`**: Limit the maximum number of assistant turns. The session will stop after N turns.
- **`--max-price DOLLARS`**: Set a maximum cost limit in dollars. The session will be interrupted if the cost exceeds this limit.
- **`--enabled-tools TOOL`**: Enable specific tools. In programmatic mode, this disables all other tools. Can be specified multiple times. Supports exact names, glob patterns (e.g., `bash*`), or regex with `re:` prefix (e.g., `re:^serena_.*$`).
- **`--output FORMAT`**: Set the output format. Options:
  - `text` (default): Human-readable text output
  - `json`: All messages as JSON at the end
  - `streaming`: Newline-delimited JSON per message

Example:

```bash
kin --prompt "Analyze the codebase" --max-turns 5 --max-price 1.0 --output json
```

## Slash Commands

Use slash commands for meta-actions and configuration changes during a session.

### Built-in Slash Commands

Kin Code provides several built-in slash commands. Use slash commands by typing them in the input box:

```
> /help
```

### Custom Slash Commands via Skills

You can define your own slash commands through the skills system. Skills are reusable components that extend Kin Code's functionality.

To create a custom slash command:

1. Create a skill directory with a `SKILL.md` file
2. Set `user-invocable = true` in the skill metadata
3. Define the command logic in your skill

Example skill metadata:

```markdown
---
name: my-skill
description: My custom skill with slash commands
user-invocable: true
---
```

Custom slash commands appear in the autocompletion menu alongside built-in commands.

## Skills System

Kin Code's skills system allows you to extend functionality through reusable components. Skills can add new tools, slash commands, and specialized behaviors.

Kin Code follows the [Agent Skills specification](https://agentskills.io/specification) for skill format and structure.

### Creating Skills

Skills are defined in directories with a `SKILL.md` file containing metadata in YAML frontmatter. For example, `~/.kin-code/skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: Perform automated code reviews
license: MIT
compatibility: Python 3.12+
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - ask_user_question
---

# Code Review Skill

This skill helps analyze code quality and suggest improvements.
```

### Skill Discovery

Kin Code discovers skills from multiple locations:

1. **Global skills directory**: `~/.kin-code/skills/`
2. **Local project skills**: `.kin-code/skills/` in your project
3. **Custom paths**: Configured in `config.toml`

```toml
skill_paths = ["/path/to/custom/skills"]
```

### Managing Skills

Enable or disable skills using patterns in your configuration:

```toml
# Enable specific skills
enabled_skills = ["code-review", "test-*"]

# Disable specific skills
disabled_skills = ["experimental-*"]
```

Skills support the same pattern matching as tools (exact names, glob patterns, and regex).

## Configuration

### Configuration File Location

Kin Code is configured via a `config.toml` file. It looks for this file first in `./.kin-code/config.toml` and then falls back to `~/.kin-code/config.toml`.

### API Key Configuration

To use Kin Code, you'll need an API key from a supported provider.

You can configure your API key using `kin --setup`, or through one of the methods below.

Kin Code supports multiple ways to configure your API keys:

1. **Interactive Setup (Recommended for first-time users)**: When you run Kin Code for the first time or if your API key is missing, Kin Code will prompt you to enter it. The key will be securely saved to `~/.kin-code/.env` for future sessions.

2. **Environment Variables**: Set your API key as an environment variable (example for OpenAI):

   ```bash
   export OPENAI_API_KEY="your_api_key"
   ```

3. **`.env` File**: Create a `.env` file in `~/.kin-code/` and add your API keys:

   ```bash
   OPENAI_API_KEY=your_api_key
   ```

   Kin Code automatically loads API keys from `~/.kin-code/.env` on startup. Environment variables take precedence over the `.env` file if both are set.

**Note**: The `.env` file is specifically for API keys and other provider credentials. General Kin Code configuration should be done in `config.toml`.

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

To use a custom agent, run Kin Code with the `--agent` flag:

```bash
kin --agent my_custom_agent
```

Kin Code will look for a file named `my_custom_agent.toml` in the agents directory and apply its configuration.

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

Note: This implies that you have set up a redteam prompt named `~/.kin-code/prompts/redteam.md`.

### Tool Management

#### Enable/Disable Tools with Patterns

You can control which tools are active using `enabled_tools` and `disabled_tools`.
These fields support exact names, glob patterns, and regular expressions.

Examples:

```toml
# Only enable tools that start with "serena_" (glob)
enabled_tools = ["serena_*"]

# Regex (prefix with re:) — matches full tool name (case-insensitive)
enabled_tools = ["re:^serena_.*$"]

# Disable a group with glob; everything else stays enabled
disabled_tools = ["mcp_*", "grep"]
```

Notes:

- MCP tool names use underscores, e.g., `serena_list` not `serena.list`.
- Regex patterns are matched against the full tool name using fullmatch.

### MCP Server Configuration

You can configure MCP (Model Context Protocol) servers to extend Kin Code's capabilities. Add MCP server configurations under the `mcp_servers` section:

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
env = { "DEBUG" = "1", "LOG_LEVEL" = "info" }
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
- `startup_timeout_sec`: Timeout in seconds for the server to start and initialize (default 10s)
- `tool_timeout_sec`: Timeout in seconds for tool execution (default 60s)
- `env`: Environment variables to set for the MCP server of transport type stdio

MCP tools are named using the pattern `{server_name}_{tool_name}` and can be configured with permissions like built-in tools:

```toml
# Configure permissions for specific MCP tools
[tools.fetch_server_get]
permission = "always"

[tools.my_http_server_query]
permission = "ask"
```

MCP server configurations support additional features:

- **Environment variables**: Set environment variables for MCP servers
- **Custom timeouts**: Configure startup and tool execution timeouts

Example with environment variables and timeouts:

```toml
[[mcp_servers]]
name = "my_server"
transport = "http"
url = "http://localhost:8000"
env = { "DEBUG" = "1", "LOG_LEVEL" = "info" }
startup_timeout_sec = 15
tool_timeout_sec = 120
```

### Session Management

#### Session Continuation and Resumption

Kin Code supports continuing from previous sessions:

- **`--continue`** or **`-c`**: Continue from the most recent saved session
- **`--resume SESSION_ID`**: Resume a specific session by ID (supports partial matching)

```bash
# Continue from last session
kin --continue

# Resume specific session
kin --resume abc123
```

Session logging must be enabled in your configuration for these features to work.

#### Working Directory Control

Use the `--workdir` option to specify a working directory:

```bash
kin --workdir /path/to/project
```

This is useful when you want to run Kin Code from a different location than your current directory.

### Update Settings

#### Auto-Update

Kin Code includes an automatic update feature that keeps your installation current. This is enabled by default.

To disable auto-updates, add this to your `config.toml`:

```toml
enable_auto_update = false
```

### Custom Kin Code Home Directory

By default, Kin Code stores its configuration in `~/.kin-code/`. You can override this by setting the `KIN_HOME` environment variable:

```bash
export KIN_HOME="/path/to/custom/kin/home"
```

This affects where Kin Code looks for:

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

Licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for the full license text.

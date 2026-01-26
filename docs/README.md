# Kin Code Documentation

Welcome to the Kin Code documentation. Kin Code is an open-source CLI coding assistant powered by AI.

## Quick Links

| Getting Started | I want to... |
|-----------------|--------------|
| [Installation](./getting-started/installation.md) | Install Kin Code |
| [Quick Start](./getting-started/quickstart.md) | Get running fast |
| [First Project](./getting-started/first-project.md) | Walk through a real task |

## Documentation Sections

### [Getting Started](./getting-started/index.md)

Install Kin Code, set up your API key, and complete your first task.

- [Installation](./getting-started/installation.md) - Install via uv or pip
- [Quick Start](./getting-started/quickstart.md) - First-run setup and basic usage
- [First Project](./getting-started/first-project.md) - Complete walkthrough

### [User Guide](./user-guide/index.md)

Learn how to use Kin Code effectively in your daily workflow.

- [Interactive Mode](./user-guide/interactive-mode.md) - TUI usage, multi-line input, file references
- [Programmatic Mode](./user-guide/programmatic-mode.md) - Non-interactive usage and scripting
- [Modes](./user-guide/modes.md) - Default, Plan, Accept-Edits, Auto-Approve
- [Slash Commands](./user-guide/slash-commands.md) - Quick actions like /help, /config
- [Keyboard Shortcuts](./user-guide/keyboard-shortcuts.md) - All keybindings
- [Session Management](./user-guide/session-management.md) - Continue and resume sessions

### [Tools](./tools/index.md)

Reference for Kin Code's built-in tools.

| Tool | Description |
|------|-------------|
| [bash](./tools/bash.md) | Execute shell commands |
| [read_file](./tools/read-file.md) | Read file contents |
| [write_file](./tools/write-file.md) | Create or overwrite files |
| [search_replace](./tools/search-replace.md) | Pattern-based editing |
| [grep](./tools/grep.md) | Search code with regex |
| [todo](./tools/todo.md) | Task management |

### [Configuration](./configuration/index.md)

Customize Kin Code's behavior.

- [Config File](./configuration/config-file.md) - The config.toml structure
- [API Keys](./configuration/api-keys.md) - Setting up provider credentials
- [Providers](./configuration/providers.md) - Configure AI providers
- [Models](./configuration/models.md) - Add and configure models
- [Tool Permissions](./configuration/tool-permissions.md) - Control tool access

### [Customization](./customization/index.md)

Extend Kin Code with custom agents, prompts, and tools.

- [Custom Agents](./customization/custom-agents.md) - Specialized agent configurations
- [Custom Prompts](./customization/custom-prompts.md) - Define system prompts
- [Custom Tools](./customization/custom-tools.md) - Build Python tools

### [Integrations](./integrations/index.md)

Connect with external tools and editors.

- [MCP Servers](./integrations/mcp-servers.md) - Model Context Protocol
- [ACP Setup](./integrations/acp-setup.md) - Editor integration

### [Reference](./reference/index.md)

Complete reference documentation.

- [CLI Options](./reference/cli-options.md) - All command-line arguments
- [Config Reference](./reference/config-reference.md) - Full config.toml schema

### [Troubleshooting](./troubleshooting/index.md)

Diagnose and resolve issues.

- [Common Issues](./troubleshooting/common-issues.md) - FAQ and solutions
- [Logging](./troubleshooting/logging.md) - Session logs and debugging

## Quick Reference

### Essential Commands

```bash
kin                    # Start interactive mode
kin "your prompt"      # Start with a prompt
kin -c                 # Continue last session
kin --plan             # Read-only exploration mode
kin --auto-approve     # Auto-approve all tools
kin -p "prompt"        # Programmatic mode
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit message |
| `Ctrl+J` | Insert newline |
| `Escape` | Interrupt agent |
| `Ctrl+O` | Toggle tool output |
| `Ctrl+T` | Toggle todo list |
| `Shift+Tab` | Cycle modes |

### Slash Commands

| Command | Action |
|---------|--------|
| `/help` | Show help |
| `/config` | Edit settings |
| `/clear` | Clear history |
| `/compact` | Summarize history |
| `/log` | Show log path |
| `/exit` | Exit |

## Getting Help

- **In-app**: Type `/help` for keyboard shortcuts and commands
- **Issues**: [GitHub Issues](https://github.com/kinra-ai/kin-code/issues)
- **Changelog**: See [CHANGELOG.md](../CHANGELOG.md) for version history

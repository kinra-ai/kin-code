# Kin Code Documentation

Welcome to the official documentation for **Kin Code**, an AI-powered CLI coding assistant that brings conversational AI directly to your terminal.

## Overview

Kin Code provides a powerful interface to interact with your codebase using natural language. Whether you're exploring unfamiliar code, refactoring existing projects, or automating repetitive tasks, Kin Code helps you work more efficiently.

### What Kin Code Offers

- **Conversational Interface** - Chat naturally with an AI that understands your codebase
- **Powerful Tool System** - Read, write, search, and execute commands safely
- **Agent Profiles** - Different configurations for different workflows
- **Skills System** - Extend functionality with reusable components
- **MCP Integration** - Connect external tools via Model Context Protocol
- **Editor Support** - Integrate with Zed, JetBrains, Neovim, and more

## Documentation Sections

### Getting Started

New to Kin Code? Start here to get up and running quickly.

| Page | Description |
|------|-------------|
| [Installation](getting-started/installation.md) | Installation methods and system requirements |
| [Quick Start](getting-started/quick-start.md) | Your first Kin Code session in 5 minutes |
| [First Session](getting-started/first-session.md) | Understanding the interface and workflow |
| [API Keys](getting-started/api-keys.md) | Configuring provider credentials |
| [Terminal Requirements](getting-started/terminal-requirements.md) | Supported terminals and setup |

### User Guide

Learn how to use Kin Code effectively in your daily workflow.

| Page | Description |
|------|-------------|
| [Interactive Mode](user-guide/interactive-mode.md) | The main chat interface |
| [Programmatic Mode](user-guide/programmatic-mode.md) | Scripting and automation |
| [Slash Commands](user-guide/slash-commands.md) | Built-in commands reference |
| [Keyboard Shortcuts](user-guide/keyboard-shortcuts.md) | Efficiency shortcuts |
| [File References](user-guide/file-references.md) | Using @ to reference files |
| [Session Management](user-guide/session-management.md) | Continue and resume sessions |
| [Trust Folders](user-guide/trust-folders.md) | Security and trusted directories |

### Configuration

Customize Kin Code to fit your workflow.

| Page | Description |
|------|-------------|
| [Overview](configuration/overview.md) | Configuration system introduction |
| [Config File](configuration/config-file.md) | The config.toml file reference |
| [API Keys](configuration/api-keys.md) | Provider credentials setup |
| [Models](configuration/models.md) | Model selection and providers |
| [Themes](configuration/themes.md) | Visual customization |
| [Auto Updates](configuration/auto-updates.md) | Update settings |

### Tools

Built-in tools that power Kin Code's capabilities.

| Page | Description |
|------|-------------|
| [Overview](tools/overview.md) | Introduction to the tool system |
| [File Tools](tools/file-tools.md) | read_file, write_file, search_replace |
| [Search Tools](tools/search-tools.md) | grep and code searching |
| [Shell Tools](tools/shell-tools.md) | bash command execution |
| [Task Tools](tools/task-tools.md) | todo and task delegation |
| [User Interaction](tools/user-interaction.md) | ask_user_question |
| [Web Tools](tools/web-tools.md) | Web browsing and fetching |
| [Permissions](tools/permissions.md) | Configuring tool access |

### Agents

Agent profiles and customization.

| Page | Description |
|------|-------------|
| [Overview](agents/overview.md) | Agent system introduction |
| [Built-in Agents](agents/built-in.md) | default, plan, accept-edits, auto-approve |
| [Custom Agents](agents/custom-agents.md) | Creating your own agents |
| [Subagents](agents/subagents.md) | Task delegation with subagents |
| [System Prompts](agents/system-prompts.md) | Custom system prompts |

### Skills

Extend Kin Code with reusable components.

| Page | Description |
|------|-------------|
| [Overview](skills/overview.md) | Skills system introduction |
| [Creating Skills](skills/creating-skills.md) | Build your own skills |
| [Discovery](skills/discovery.md) | Where skills are loaded from |
| [Managing Skills](skills/managing.md) | Enable and disable skills |
| [Specification](skills/specification.md) | The Agent Skills format |

### MCP (Model Context Protocol)

Integrate external tools via MCP servers.

| Page | Description |
|------|-------------|
| [Overview](mcp/overview.md) | MCP integration introduction |
| [Configuration](mcp/configuration.md) | Setting up MCP servers |
| [HTTP Transport](mcp/http-transport.md) | HTTP and Streamable HTTP |
| [Stdio Transport](mcp/stdio-transport.md) | Local process servers |
| [Tool Naming](mcp/tool-naming.md) | How MCP tools are named |

### Architecture

Technical details for developers and contributors.

| Page | Description |
|------|-------------|
| [Overview](architecture/overview.md) | System architecture |
| [Agent Loop](architecture/agent-loop.md) | Core execution flow |
| [Tool System](architecture/tool-system.md) | How tools work |
| [Provider System](architecture/provider-system.md) | LLM provider abstraction |

### Development

Contributing to Kin Code.

| Page | Description |
|------|-------------|
| [Contributing](development/contributing.md) | How to contribute |
| [Setup](development/setup.md) | Development environment setup |
| [Testing](development/testing.md) | Running tests |
| [Code Style](development/code-style.md) | Python style guidelines |

### API Reference

Command-line interface and programmatic usage.

| Page | Description |
|------|-------------|
| [CLI Reference](api-reference/cli-reference.md) | Command-line options |
| [Environment Variables](api-reference/environment-variables.md) | Environment configuration |
| [Output Formats](api-reference/output-formats.md) | JSON and streaming output |

### Integrations

Using Kin Code with editors and other tools.

| Page | Description |
|------|-------------|
| [ACP Setup](integrations/acp-setup.md) | Agent Client Protocol setup |
| [Zed](integrations/zed.md) | Zed editor integration |
| [JetBrains](integrations/jetbrains.md) | IntelliJ, PyCharm, etc. |
| [Neovim](integrations/neovim.md) | Neovim with avante.nvim |
| [GitHub Actions](integrations/github-actions.md) | CI/CD integration |

### Troubleshooting

Common issues and solutions.

| Page | Description |
|------|-------------|
| [Common Issues](troubleshooting/common-issues.md) | Frequently encountered problems |
| [Terminal Issues](troubleshooting/terminal-issues.md) | Display and input problems |
| [API Issues](troubleshooting/api-issues.md) | Provider connection problems |
| [Tool Issues](troubleshooting/tool-issues.md) | Tool execution problems |

## Quick Start by User Type

### New Users

1. [Install Kin Code](getting-started/installation.md)
2. [Configure your API key](getting-started/api-keys.md)
3. [Try the quick start guide](getting-started/quick-start.md)
4. [Explore interactive mode](user-guide/interactive-mode.md)

### Power Users

1. [Configure custom agents](agents/custom-agents.md)
2. [Create skills](skills/creating-skills.md)
3. [Set up MCP servers](mcp/configuration.md)
4. [Use programmatic mode](user-guide/programmatic-mode.md)

### Developers

1. [Set up the development environment](development/setup.md)
2. [Understand the architecture](architecture/overview.md)
3. [Run the test suite](development/testing.md)
4. [Read the contribution guide](development/contributing.md)

## Additional Resources

- [Main README](../README.md) - Project overview
- [Changelog](../CHANGELOG.md) - Version history
- [Contributing Guide](../CONTRIBUTING.md) - Contribution guidelines

---

**Need help?** Check [Troubleshooting](troubleshooting/common-issues.md) or open an issue on [GitHub](https://github.com/kinra-ai/kin-code/issues).

# Kin Code Documentation

Welcome to the official documentation for Kin Code, an AI-powered CLI coding assistant.

## Quick Links

- [Installation](getting-started/installation.md) - Get Kin Code installed
- [Quick Start](getting-started/quick-start.md) - Start using Kin Code in minutes
- [Configuration](configuration/overview.md) - Customize your setup

## Documentation Sections

### Getting Started
New to Kin Code? Start here to get up and running quickly.

- [Installation](getting-started/installation.md) - Installation methods and requirements
- [Quick Start](getting-started/quick-start.md) - Your first Kin Code session
- [First Session](getting-started/first-session.md) - Understanding the interface
- [API Keys](getting-started/api-keys.md) - Configuring provider credentials
- [Terminal Requirements](getting-started/terminal-requirements.md) - Supported terminals

### User Guide
Learn how to use Kin Code effectively in your daily workflow.

- [Interactive Mode](user-guide/interactive-mode.md) - The main chat interface
- [Programmatic Mode](user-guide/programmatic-mode.md) - Scripting and automation
- [Slash Commands](user-guide/slash-commands.md) - Built-in commands
- [Keyboard Shortcuts](user-guide/keyboard-shortcuts.md) - Efficiency shortcuts
- [File References](user-guide/file-references.md) - Using @ to reference files
- [Session Management](user-guide/session-management.md) - Continue and resume sessions
- [Trust Folders](user-guide/trust-folders.md) - Security and trusted directories

### Configuration
Customize Kin Code to fit your workflow.

- [Overview](configuration/overview.md) - Configuration system introduction
- [Config File](configuration/config-file.md) - The config.toml file
- [API Keys](configuration/api-keys.md) - Provider credentials
- [Models](configuration/models.md) - Model selection and providers
- [Themes](configuration/themes.md) - Visual customization
- [Auto Updates](configuration/auto-updates.md) - Update settings

### Tools
Built-in tools that power Kin Code's capabilities.

- [Overview](tools/overview.md) - Introduction to the tool system
- [File Tools](tools/file-tools.md) - read_file, write_file, search_replace
- [Search Tools](tools/search-tools.md) - grep and code searching
- [Shell Tools](tools/shell-tools.md) - bash command execution
- [Task Tools](tools/task-tools.md) - todo and task delegation
- [User Interaction](tools/user-interaction.md) - ask_user_question
- [Web Tools](tools/web-tools.md) - Web browsing and fetching
- [Tool Permissions](tools/permissions.md) - Configuring tool access

### Agents
Agent profiles and customization.

- [Overview](agents/overview.md) - Agent system introduction
- [Built-in Agents](agents/built-in.md) - default, plan, accept-edits, auto-approve
- [Custom Agents](agents/custom-agents.md) - Creating your own agents
- [Subagents](agents/subagents.md) - Task delegation with subagents
- [System Prompts](agents/system-prompts.md) - Custom system prompts

### Skills
Extend Kin Code with reusable components.

- [Overview](skills/overview.md) - Skills system introduction
- [Creating Skills](skills/creating-skills.md) - Build your own skills
- [Skill Discovery](skills/discovery.md) - Where skills are loaded from
- [Managing Skills](skills/managing.md) - Enable and disable skills
- [Skill Specification](skills/specification.md) - The Agent Skills format

### MCP (Model Context Protocol)
Integrate external tools via MCP servers.

- [Overview](mcp/overview.md) - MCP integration introduction
- [Configuration](mcp/configuration.md) - Setting up MCP servers
- [HTTP Transport](mcp/http-transport.md) - HTTP and Streamable HTTP
- [Stdio Transport](mcp/stdio-transport.md) - Local process servers
- [Tool Naming](mcp/tool-naming.md) - How MCP tools are named

### Architecture
Technical details for developers and contributors.

- [Overview](architecture/overview.md) - System architecture
- [Agent Loop](architecture/agent-loop.md) - Core execution flow
- [Tool System](architecture/tool-system.md) - How tools work
- [Provider System](architecture/provider-system.md) - LLM provider abstraction

### Development
Contributing to Kin Code.

- [Contributing](development/contributing.md) - How to contribute
- [Development Setup](development/setup.md) - Setting up for development
- [Testing](development/testing.md) - Running tests
- [Code Style](development/code-style.md) - Python style guidelines

### API Reference
Command-line interface and programmatic usage.

- [CLI Reference](api-reference/cli-reference.md) - Command-line options
- [Environment Variables](api-reference/environment-variables.md) - Environment configuration
- [Output Formats](api-reference/output-formats.md) - JSON and streaming output

### Integrations
Using Kin Code with editors and other tools.

- [ACP Setup](integrations/acp-setup.md) - Agent Client Protocol setup
- [Zed](integrations/zed.md) - Zed editor integration
- [JetBrains](integrations/jetbrains.md) - IntelliJ, PyCharm, etc.
- [Neovim](integrations/neovim.md) - Neovim with avante.nvim
- [GitHub Actions](integrations/github-actions.md) - CI/CD integration

### Troubleshooting
Common issues and solutions.

- [Common Issues](troubleshooting/common-issues.md) - Frequently encountered problems
- [Terminal Issues](troubleshooting/terminal-issues.md) - Display and input problems
- [API Issues](troubleshooting/api-issues.md) - Provider connection problems
- [Tool Issues](troubleshooting/tool-issues.md) - Tool execution problems

---

## Additional Resources

- [Main README](../README.md) - Project overview
- [Changelog](../CHANGELOG.md) - Version history
- [Contributing Guide](../CONTRIBUTING.md) - Contribution guidelines
- [License](../LICENSE) - Apache 2.0 License

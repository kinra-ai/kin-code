# Kin Code

[![PyPI Version](https://img.shields.io/pypi/v/kin-code)](https://pypi.org/project/kin-code)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/github/license/kinra-ai/kin-code)](https://github.com/kinra-ai/kin-code/blob/main/LICENSE)

**An AI-powered CLI coding assistant.**

Kin Code provides a conversational interface to your codebase, allowing you to explore, modify, and interact with projects using natural language and a powerful set of tools.

> [!NOTE]
> For complete documentation, see the [docs](docs/README.md) directory.

## Installation

### Using uv (recommended)

```bash
uv tool install kin-code
```

### Using pip

```bash
pip install kin-code
```

## Quick Start

```bash
# Navigate to your project
cd /path/to/project

# Run Kin Code
kin

# Or with an initial prompt
kin "Explain this codebase"
```

On first run, Kin Code will prompt you to configure your API key.

## Features

- **Interactive Chat** - Conversational AI that understands your codebase
- **Powerful Tools** - Read, write, search, and execute commands
- **Project Awareness** - Automatic context from file structure and git
- **Multiple Agents** - Different profiles for different workflows
- **Skills System** - Extend functionality with reusable components
- **MCP Support** - Integrate external tools via Model Context Protocol

## Usage

### Interactive Mode

```bash
kin                          # Start interactive session
kin "your prompt"            # Start with a prompt
kin --agent plan             # Use read-only agent
kin --continue               # Continue last session
```

### Programmatic Mode

```bash
kin --prompt "Analyze code" --max-turns 5 --output json
```

### Key Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Ctrl+J` | New line |
| `Ctrl+C` | Interrupt |
| `Ctrl+O` | Toggle tool output |
| `Shift+Tab` | Toggle auto-approve |

### File References

Reference files with `@`:

```
> Explain what @src/main.py does
```

## Configuration

Configuration is stored in `~/.kin-code/`:

```
~/.kin-code/
  config.toml      # Main configuration
  .env             # API keys
  agents/          # Custom agents
  prompts/         # Custom prompts
  skills/          # Global skills
```

### API Keys

Configure via `kin --setup` or add to `~/.kin-code/.env`:

```bash
OPENAI_API_KEY=sk-...
```

## Built-in Agents

| Agent | Description |
|-------|-------------|
| `default` | Standard agent, asks for approval |
| `plan` | Read-only, auto-approves safe tools |
| `accept-edits` | Auto-approves file edits |
| `auto-approve` | Auto-approves everything |

```bash
kin --agent plan
```

## Editor Integration

Kin Code supports [Agent Client Protocol](https://agentclientprotocol.com/) for editor integration.

See [ACP Setup](docs/integrations/acp-setup.md) for Zed, JetBrains, and Neovim configuration.

## Documentation

Full documentation is available in [docs/](docs/README.md):

- [Getting Started](docs/getting-started/installation.md)
- [User Guide](docs/user-guide/interactive-mode.md)
- [Configuration](docs/configuration/overview.md)
- [Tools](docs/tools/overview.md)
- [Agents](docs/agents/overview.md)
- [Skills](docs/skills/overview.md)
- [Troubleshooting](docs/troubleshooting/common-issues.md)

## Resources

- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

## License

Apache License 2.0. See [LICENSE](LICENSE).

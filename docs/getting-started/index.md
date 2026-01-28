# Getting Started

Welcome to Kin Code. This section will guide you through installation, setup, and your first session with the AI-powered CLI coding assistant.

## Quick Links

| Guide | Time | Description |
|-------|------|-------------|
| [Installation](installation.md) | 2 min | Get Kin Code installed on your system |
| [Quick Start](quick-start.md) | 5 min | Your first Kin Code session |
| [First Session](first-session.md) | 10 min | Deep dive into the interface |
| [API Keys](api-keys.md) | 3 min | Configure your AI provider |
| [Terminal Requirements](terminal-requirements.md) | 5 min | Ensure your terminal is compatible |

## What You Can Do with Kin Code

Kin Code brings AI assistance directly to your terminal. Here's what you can accomplish:

### Explore Codebases

Ask questions about unfamiliar code and get instant answers:

```
> Explain how authentication works in this project
> What does the main entry point do?
> Find all usages of the User class
```

### Modify Code

Make changes through natural language requests:

```
> Add error handling to the database connection
> Refactor this function to use async/await
> Update all imports to use the new module name
```

### Search and Navigate

Find what you need quickly:

```
> Find all TODO comments in the project
> Show me files that import the config module
> What tests cover the payment feature?
```

### Execute Commands

Run shell commands with safety prompts:

```
> Run the test suite
> Install the missing dependencies
> Start the development server
```

### Automate Tasks

Script repetitive workflows:

```bash
kin --prompt "Update all copyright headers to 2025" --max-turns 10
```

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** - Check with `python --version`
- **A terminal** - See [Terminal Requirements](terminal-requirements.md) for compatibility
- **An API key** - From OpenAI, Anthropic, or another supported provider

## Installation Options

### Recommended: Using uv

```bash
uv tool install kin-code
```

### Alternative: Using pip

```bash
pip install kin-code
```

See [Installation](installation.md) for detailed options including Homebrew and development installs.

## First Steps

After installation:

1. **Navigate to a project directory**
   ```bash
   cd /path/to/your/project
   ```

2. **Run Kin Code**
   ```bash
   kin
   ```

3. **Configure your API key** (first run only)
   - Follow the prompts to enter your API key
   - Or configure manually: `kin --setup`

4. **Start chatting**
   ```
   > Explain this codebase
   ```

## Next Steps

Once you're comfortable with the basics:

- [Learn keyboard shortcuts](../user-guide/keyboard-shortcuts.md) for faster navigation
- [Explore slash commands](../user-guide/slash-commands.md) for built-in features
- [Configure tool permissions](../configuration/overview.md) for your workflow
- [Try different agents](../agents/overview.md) for specialized tasks

## Getting Help

If you run into issues:

- Check [Troubleshooting](../troubleshooting/common-issues.md) for solutions
- Review [Terminal Issues](../troubleshooting/terminal-issues.md) for display problems
- See [API Issues](../troubleshooting/api-issues.md) for connection problems

---

**Related Pages**

- [User Guide](../user-guide/index.md) - Detailed usage information
- [Configuration](../configuration/index.md) - Customize your setup
- [Documentation Home](../index.md) - All documentation sections

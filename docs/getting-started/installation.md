# Installation

This guide covers the different ways to install Kin Code on your system.

## Requirements

- **Python 3.12 or higher** - Kin Code requires Python 3.12+
- **A modern terminal** - See [Terminal Requirements](terminal-requirements.md) for recommendations
- **An API key** - From a supported LLM provider (OpenAI, Anthropic, etc.)

## Installation Methods

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer. This is the recommended method.

```bash
uv tool install kin-code
```

This installs `kin` and `kin-acp` as global commands.

### Using pip

If you prefer pip, install Kin Code from PyPI:

```bash
pip install kin-code
```

### Using pipx

For isolated installations with automatic virtual environments:

```bash
pipx install kin-code
```

## Verifying Installation

After installation, verify that Kin Code is available:

```bash
kin --version
```

You should see output like:

```
Kin Code v0.x.x
```

## First-Time Setup

When you first run `kin`, the application will:

1. Create a configuration directory at `~/.kin-code/`
2. Generate a default `config.toml` configuration file
3. Prompt you to enter your API key if not already configured

You can also run the setup wizard explicitly:

```bash
kin --setup
```

## Updating Kin Code

### Automatic Updates

By default, Kin Code checks for updates and can update itself automatically. You can disable this in your configuration:

```toml
enable_auto_update = false
```

### Manual Updates

Update using the same method you used to install:

```bash
# Using uv
uv tool upgrade kin-code

# Using pip
pip install --upgrade kin-code

# Using pipx
pipx upgrade kin-code
```

## Uninstalling

Remove Kin Code using your package manager:

```bash
# Using uv
uv tool uninstall kin-code

# Using pip
pip uninstall kin-code

# Using pipx
pipx uninstall kin-code
```

To also remove configuration files:

```bash
rm -rf ~/.kin-code
```

## Platform Notes

### macOS

Kin Code works well on macOS. Install Python 3.12+ via Homebrew if needed:

```bash
brew install python@3.12
```

### Linux

Ensure Python 3.12+ is installed. On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
```

### Windows

Kin Code works on Windows, but official support targets UNIX environments. For best results on Windows:

- Use Windows Terminal or a modern terminal emulator
- Consider using WSL2 for a native Linux experience

## Next Steps

- [Quick Start](quick-start.md) - Start using Kin Code
- [API Keys](api-keys.md) - Configure your provider credentials
- [Terminal Requirements](terminal-requirements.md) - Ensure your terminal is compatible

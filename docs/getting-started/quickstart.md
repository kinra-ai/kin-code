# Quick Start

Get Kin Code running in your project in under a minute.

## 1. Navigate to Your Project

```bash
cd /path/to/your/project
```

## 2. Launch Kin Code

```bash
kin
```

## 3. First-Time Setup

On first run, Kin Code will:

1. Create a default configuration at `~/.kin-code/config.toml`
2. Prompt you for your API key if not already configured
3. Save your API key to `~/.kin-code/.env` for future sessions

## 4. Start Interacting

Once set up, you can start chatting with the agent:

```
> Can you find all instances of "TODO" in the project?

The user wants to find all "TODO" comments. The grep tool is perfect for this.

> grep(pattern="TODO", path=".")

... (grep tool output) ...

I found the following "TODO" comments in your project.
```

## Starting with a Prompt

You can also start Kin with an initial prompt:

```bash
kin "Refactor the main function in cli/main.py to be more modular."
```

## Quick Reference

| Action | Command |
|--------|---------|
| Start interactive mode | `kin` |
| Start with prompt | `kin "your prompt"` |
| Auto-approve all tools | `kin --auto-approve` |
| Plan mode (read-only) | `kin --plan` |
| Continue last session | `kin -c` |

## Next Steps

- Learn about [Interactive Mode](../user-guide/interactive-mode.md)
- Explore available [Tools](../tools/index.md)
- Configure [API Keys](../configuration/api-keys.md) for different providers

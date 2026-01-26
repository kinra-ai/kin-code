# Slash Commands

Slash commands provide quick actions during a session. Type them directly in the prompt.

## Available Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help message with shortcuts and commands |
| `/config` | Open configuration settings (alias: `/theme`, `/model`) |
| `/reload` | Reload configuration from disk |
| `/clear` | Clear conversation history |
| `/log` | Show path to current session log file |
| `/compact` | Summarize conversation history to reduce context |
| `/status` | Display agent statistics |
| `/terminal-setup` | Configure Shift+Enter for newlines |
| `/exit` | Exit the application |

## Command Details

### /help

Displays keyboard shortcuts, special features, and all available commands.

### /config

Opens the configuration dialog where you can change:
- Active model
- Theme
- Other runtime settings

Aliases: `/theme`, `/model`

### /reload

Reloads `config.toml` from disk without restarting. Useful after editing the config file externally.

### /clear

Clears the conversation history, starting fresh. The agent loses context of previous messages.

### /log

Shows the file path to the current session's interaction log. Useful for debugging or sharing session details.

### /compact

When conversation context grows large, this command summarizes the history to reduce token usage while preserving important context.

### /status

Shows statistics about the current session:
- Token usage
- Cost estimate
- Number of turns

### /exit

Cleanly exits Kin Code. You can also use `Ctrl+C`.

## Tips

- Commands are case-insensitive: `/HELP` works the same as `/help`
- Unknown commands are sent as regular prompts to the agent
- Use Tab for autocompletion after typing `/`

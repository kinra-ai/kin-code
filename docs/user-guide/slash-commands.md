# Slash Commands

Slash commands provide quick actions during a session. Type them directly in the prompt.

## Available Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help message with shortcuts and commands |
| `/config` | Open configuration settings (alias: `/theme`) |
| `/model` | Open model management interface (alias: `/models`) |
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
- Theme
- Other runtime settings

Alias: `/theme`

### /model

Opens the model management interface with three views:

- **LIST**: Select from configured models
- **DISCOVER**: Find new models from providers
- **ADD**: Manually add a model

**Key bindings in LIST view:**
- `Up/Down`: Navigate models
- `Enter`: Select model
- `D`: Switch to discover view
- `A`: Switch to add view
- `Esc`: Close

**Key bindings in DISCOVER view:**
- `Up/Down`: Navigate models
- `Enter`: Add model (or refresh if already configured)
- `Left/Right`: Change provider
- Type to search/filter
- `Esc`: Back to list

**Key bindings in ADD view:**
- `Tab`: Next field
- `Enter`: Save model
- `Esc`: Cancel

Models marked with `*` in the discover view are already configured. Selecting them refreshes their metadata from the provider.

Discovery fetches `context_window` automatically from provider endpoints when available.

Alias: `/models`

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

# Models

Configure available models for Kin Code.

## Default Models

Kin includes these default models:

```toml
[[models]]
name = "mistral-vibe-cli-latest"
provider = "mistral"
alias = "devstral-2"
temperature = 0.2
input_price = 0.4
output_price = 2.0
context_window = 128000

[[models]]
name = "devstral-small-latest"
provider = "mistral"
alias = "devstral-small"
temperature = 0.2
input_price = 0.1
output_price = 0.3
context_window = 128000

[[models]]
name = "devstral"
provider = "llamacpp"
alias = "local"
temperature = 0.2
input_price = 0.0
output_price = 0.0
```

## Adding a Model

Add models in `config.toml`:

```toml
[[models]]
name = "gpt-4o"
provider = "openai"
alias = "gpt4"
temperature = 0.2
input_price = 2.5
output_price = 10.0
context_window = 128000
supports_tools = true
```

## Model Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Model identifier sent to the API |
| `provider` | Yes | Provider name (must match a configured provider) |
| `alias` | No | Short name for CLI usage (defaults to `name`) |
| `temperature` | No | Sampling temperature (default: 0.2) |
| `input_price` | No | Price per million input tokens |
| `output_price` | No | Price per million output tokens |
| `context_window` | No | Maximum context size in tokens |
| `supports_tools` | No | Whether model supports tool calling (default: true) |

## Setting the Active Model

In `config.toml`:

```toml
active_model = "devstral-2"  # Use the alias
```

Or use `/config` during a session to change models.

## Model Aliases

Aliases must be unique across all models. Use them for:
- CLI selection: `active_model = "gpt4"`
- Configuration references

## Cost Tracking

Set `input_price` and `output_price` for accurate cost estimates in `/status`.

Prices are per million tokens.

## Context Window

The `context_window` value is used for:
- Automatic conversation compaction
- Deciding when to truncate context

If not set, falls back to `auto_compact_threshold` from global config.

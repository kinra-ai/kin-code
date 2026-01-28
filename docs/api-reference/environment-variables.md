# Environment Variables

Environment variables for configuring Kin Code.

## Configuration Variables

### KIN_HOME

Override the configuration directory.

```bash
export KIN_HOME="/path/to/custom/home"
```

Default: `~/.kin-code`

### KIN_MODEL

Set the default model.

```bash
export KIN_MODEL="gpt-4o"
```

### KIN_TRUST_ALL_FOLDERS

Bypass trust folder checks (use with caution).

```bash
export KIN_TRUST_ALL_FOLDERS=true
```

## API Key Variables

### OPENAI_API_KEY

OpenAI API key.

```bash
export OPENAI_API_KEY="sk-..."
```

### ANTHROPIC_API_KEY

Anthropic API key.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### OPENROUTER_API_KEY

OpenRouter API key.

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

### GOOGLE_API_KEY

Google AI API key.

```bash
export GOOGLE_API_KEY="..."
```

### MISTRAL_API_KEY

Mistral AI API key.

```bash
export MISTRAL_API_KEY="..."
```

## Editor Variables

### EDITOR

External editor for `Ctrl+G`.

```bash
export EDITOR="vim"
```

## Precedence

Environment variables override:
- `.env` file values
- `config.toml` settings

Command-line arguments override environment variables.

## Related

- [CLI Reference](cli-reference.md)
- [Configuration Overview](../configuration/overview.md)

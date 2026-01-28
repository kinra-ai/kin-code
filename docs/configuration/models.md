# Models

Configure which AI model Kin Code uses.

## Setting the Default Model

In `config.toml`:

```toml
active_model = "gpt-4o"
```

Or via command line:

```bash
kin --model claude-3-5-sonnet
```

## Supported Providers

### OpenAI

- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### Anthropic

- `claude-3-5-sonnet`
- `claude-3-opus`
- `claude-3-sonnet`
- `claude-3-haiku`

### OpenRouter

Access to many models via a single API:

- Models from multiple providers
- Custom model names

### Local Providers

- Ollama
- LM Studio
- Other OpenAI-compatible APIs

## Model Selection Tips

| Use Case | Recommended |
|----------|-------------|
| General coding | GPT-4o, Claude 3.5 Sonnet |
| Complex reasoning | GPT-4, Claude 3 Opus |
| Fast iteration | GPT-4o-mini, Claude 3 Haiku |
| Cost-sensitive | GPT-3.5, Local models |

## Changing Models Mid-Session

```
> /model gpt-4o
```

## Related

- [Configuration Overview](overview.md)
- [API Keys](api-keys.md)

# API Keys

Kin Code requires an API key from a supported LLM provider to function. This guide covers how to configure your credentials.

## Supported Providers

Kin Code supports multiple LLM providers:

- **OpenAI** - GPT-4o, GPT-4, GPT-3.5
- **Anthropic** - Claude 3.5, Claude 3
- **OpenRouter** - Access to many models via one API
- **Google** - Gemini models
- **Mistral** - Mistral models
- **Local providers** - Ollama, LM Studio, etc.

## Configuration Methods

### Interactive Setup (Recommended)

Run the setup wizard:

```bash
kin --setup
```

This guides you through:
1. Selecting a provider
2. Entering your API key
3. Choosing a default model

Your API key is saved to `~/.kin-code/.env`.

### Environment Variables

Set your API key as an environment variable:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."

# Google
export GOOGLE_API_KEY="..."

# Mistral
export MISTRAL_API_KEY="..."
```

### .env File

Create a `.env` file at `~/.kin-code/.env`:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Environment variables take precedence over the `.env` file.

## Multiple Providers

You can configure multiple providers and switch between them:

```bash
# In ~/.kin-code/.env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Then select the model at runtime:

```bash
kin --model gpt-4o      # Uses OpenAI
kin --model claude-3-5  # Uses Anthropic
```

## API Key Security

Best practices for API key security:

1. **Never commit keys to git** - The `.env` file should be in `.gitignore`
2. **Use environment variables in CI** - Don't store keys in config files for CI/CD
3. **Rotate keys periodically** - Regenerate keys if you suspect exposure
4. **Use project-specific keys** - Consider separate keys for different projects

## Verifying Your Key

To verify your API key is configured correctly:

```bash
kin --setup
```

Or simply start Kin Code - it will prompt you if the key is missing or invalid.

## Troubleshooting

### "API key not found"

Ensure your key is:
1. Set in `~/.kin-code/.env` or as an environment variable
2. Named correctly (e.g., `OPENAI_API_KEY`, not `OPENAI_KEY`)
3. Not empty or whitespace-only

### "Invalid API key"

1. Verify the key is correct (no extra spaces)
2. Check the key hasn't expired
3. Ensure the key has the required permissions

### "Rate limit exceeded"

1. Wait and retry
2. Consider upgrading your API plan
3. Use a different model or provider

## Related

- [Configuration Overview](../configuration/overview.md)
- [Models](../configuration/models.md)
- [Troubleshooting API Issues](../troubleshooting/api-issues.md)

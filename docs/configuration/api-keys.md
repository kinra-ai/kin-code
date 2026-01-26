# API Keys

Configure API keys for AI providers.

## Setup Methods

### 1. Interactive Setup (Recommended)

On first run, Kin prompts for your API key and saves it to `~/.kin-code/.env`.

### 2. Environment Variables

Set your API key directly:

```bash
export MISTRAL_API_KEY="your_mistral_api_key"
```

### 3. .env File

Create `~/.kin-code/.env`:

```bash
MISTRAL_API_KEY=your_mistral_api_key
```

## Priority

Environment variables take precedence over the `.env` file if both are set.

## Per-Provider Keys

Different providers use different environment variables:

| Provider | Environment Variable |
|----------|---------------------|
| Mistral | `MISTRAL_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |

Custom providers can specify their key variable in `config.toml`:

```toml
[[providers]]
name = "custom"
api_base = "https://api.example.com/v1"
api_key_env_var = "CUSTOM_API_KEY"
```

## Security Notes

- The `.env` file is only for API keys and credentials
- General configuration belongs in `config.toml`
- Never commit `.env` files to version control
- The `.env` file is loaded automatically on startup

## Verifying Keys

Run Kin and check for API key errors:

```bash
kin
```

If the key is missing or invalid, you'll see an error message with the expected environment variable.

## Setup Command

Re-run the interactive setup:

```bash
kin --setup
```

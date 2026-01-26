# Providers

Configure AI provider endpoints.

## Default Providers

Kin includes two default providers:

```toml
[[providers]]
name = "mistral"
api_base = "https://api.mistral.ai/v1"
api_key_env_var = "MISTRAL_API_KEY"
backend = "mistral"

[[providers]]
name = "llamacpp"
api_base = "http://127.0.0.1:8080/v1"
api_key_env_var = ""
backend = "generic"
```

## Adding a Provider

Add custom providers in `config.toml`:

```toml
[[providers]]
name = "openrouter"
api_base = "https://openrouter.ai/api/v1"
api_key_env_var = "OPENROUTER_API_KEY"
api_style = "openai"
backend = "generic"
```

## Provider Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier for the provider |
| `api_base` | Yes | Base URL for the API |
| `api_key_env_var` | No | Environment variable containing the API key |
| `api_style` | No | API style (`openai` is default) |
| `backend` | No | Backend type (`mistral` or `generic`) |
| `reasoning_field_name` | No | Field name for reasoning content |

## Backend Types

| Backend | Use For |
|---------|---------|
| `mistral` | Mistral's native API |
| `generic` | OpenAI-compatible APIs |

## Interactive Provider Setup

Add a provider interactively:

```bash
kin --add-provider
```

This guides you through entering the provider details.

## Examples

### OpenAI

```toml
[[providers]]
name = "openai"
api_base = "https://api.openai.com/v1"
api_key_env_var = "OPENAI_API_KEY"
backend = "generic"
```

### Local llama.cpp

```toml
[[providers]]
name = "local"
api_base = "http://127.0.0.1:8080/v1"
api_key_env_var = ""
backend = "generic"
```

### Azure OpenAI

```toml
[[providers]]
name = "azure"
api_base = "https://your-resource.openai.azure.com/openai/deployments/your-deployment"
api_key_env_var = "AZURE_OPENAI_API_KEY"
backend = "generic"
```

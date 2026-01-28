"""Provider presets for common OpenAI-compatible services."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderPreset:
    """A preset configuration for an OpenAI-compatible provider."""

    id: str
    name: str
    base_url: str
    requires_api_key: bool
    api_key_env_var: str
    api_key_help_url: str | None = None


PROVIDER_PRESETS = [
    ProviderPreset(
        id="openrouter",
        name="OpenRouter (Recommended)",
        base_url="https://openrouter.ai/api/v1",
        requires_api_key=True,
        api_key_env_var="OPENROUTER_API_KEY",
        api_key_help_url="https://openrouter.ai/keys",
    ),
    ProviderPreset(
        id="groq",
        name="Groq",
        base_url="https://api.groq.com/openai/v1",
        requires_api_key=True,
        api_key_env_var="GROQ_API_KEY",
        api_key_help_url="https://console.groq.com/keys",
    ),
    ProviderPreset(
        id="ollama",
        name="Ollama (Local)",
        base_url="http://localhost:11434/v1",
        requires_api_key=False,
        api_key_env_var="",
    ),
    ProviderPreset(
        id="custom",
        name="Custom OpenAI-Compatible",
        base_url="",
        requires_api_key=True,
        api_key_env_var="CUSTOM_API_KEY",
    ),
]


def get_preset_by_id(preset_id: str) -> ProviderPreset | None:
    """Get a provider preset by its ID."""
    for preset in PROVIDER_PRESETS:
        if preset.id == preset_id:
            return preset
    return None

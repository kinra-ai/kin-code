"""Provider presets for OpenAI-compatible endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class ProviderPreset(BaseModel):
    """A preset configuration for an OpenAI-compatible API provider."""

    id: str
    name: str
    base_url: str
    requires_api_key: bool
    api_key_env_var: str
    help_url: str


PROVIDER_PRESETS: list[ProviderPreset] = [
    ProviderPreset(
        id="openrouter",
        name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        requires_api_key=True,
        api_key_env_var="OPENROUTER_API_KEY",
        help_url="https://openrouter.ai/settings/keys",
    ),
    ProviderPreset(
        id="groq",
        name="Groq",
        base_url="https://api.groq.com/openai/v1",
        requires_api_key=True,
        api_key_env_var="GROQ_API_KEY",
        help_url="https://console.groq.com/keys",
    ),
    ProviderPreset(
        id="custom",
        name="Custom",
        base_url="",
        requires_api_key=False,
        api_key_env_var="",
        help_url="",
    ),
]


def get_preset_by_id(preset_id: str) -> ProviderPreset | None:
    """Get a provider preset by its unique identifier.

    Args:
        preset_id: The unique identifier of the preset to find.

    Returns:
        The matching ProviderPreset, or None if not found.
    """
    for preset in PROVIDER_PRESETS:
        if preset.id == preset_id:
            return preset
    return None

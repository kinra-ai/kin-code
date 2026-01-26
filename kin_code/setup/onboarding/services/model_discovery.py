"""Service for discovering models from OpenAI-compatible endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

_HTTP_SERVER_ERROR_MIN = 500

# Field names for context window across different providers
_CONTEXT_WINDOW_FIELDS = (
    "context_length",  # OpenRouter
    "context_window",  # Groq
    "max_model_len",  # vLLM
    "loaded_context_length",  # LM Studio
)


def _extract_context_window(model_data: dict[str, Any]) -> int | None:
    """Extract context window from model data, checking multiple field names.

    Different providers use different field names:
    - OpenRouter: context_length
    - Groq: context_window
    - vLLM: max_model_len
    - LM Studio: loaded_context_length
    """
    for field in _CONTEXT_WINDOW_FIELDS:
        if (value := model_data.get(field)) is not None:
            return int(value) if isinstance(value, (int, float)) else None
    return None


@dataclass(frozen=True, slots=True)
class DiscoveredModel:
    """A model discovered from an OpenAI-compatible endpoint."""

    id: str
    owned_by: str | None = None
    context_window: int | None = None


async def fetch_models(
    base_url: str,
    api_key: str | None = None,
) -> list[DiscoveredModel]:
    """Fetch available models from an OpenAI-compatible endpoint.

    Args:
        base_url: The base URL of the OpenAI-compatible API.
        api_key: Optional API key for authentication.

    Returns:
        A list of discovered models. Returns an empty list on error.
    """
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = f"{base_url.rstrip('/')}/models"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            models: list[DiscoveredModel] = []
            for model_data in data.get("data", []):
                if model_id := model_data.get("id"):
                    models.append(
                        DiscoveredModel(
                            id=model_id,
                            owned_by=model_data.get("owned_by"),
                            context_window=_extract_context_window(model_data),
                        )
                    )
            return models

    except (httpx.HTTPError, ValueError, KeyError):
        return []


def _http_status_error_message(status_code: int) -> str:
    """Get a descriptive error message for an HTTP status code."""
    match status_code:
        case 401:
            return "Authentication failed: Invalid API key"
        case 403:
            return "Access forbidden: Check API key permissions"
        case 404:
            return "Endpoint not found: Invalid base URL"
        case status if status >= _HTTP_SERVER_ERROR_MIN:
            return f"Server error: {status}"
        case _:
            return f"HTTP error: {status_code}"


async def test_connection(
    base_url: str,
    api_key: str | None = None,
) -> tuple[bool, str]:
    """Test connectivity to an OpenAI-compatible endpoint.

    Args:
        base_url: The base URL of the OpenAI-compatible API.
        api_key: Optional API key for authentication.

    Returns:
        A tuple of (success, message) where success indicates if the
        connection was successful and message provides details.
    """
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = f"{base_url.rstrip('/')}/models"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return (True, "Connection successful")

    except httpx.TimeoutException:
        return (False, "Connection timed out")
    except httpx.ConnectError:
        return (False, "Could not connect to server")
    except httpx.HTTPStatusError as e:
        return (False, _http_status_error_message(e.response.status_code))
    except httpx.HTTPError as e:
        return (False, f"Connection error: {e}")

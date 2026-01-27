"""Service for fetching and caching model pricing from provider APIs.

This module provides functionality to automatically fetch model pricing information
from provider APIs (like OpenRouter) when users haven't explicitly configured prices.
Pricing data is cached locally with a 24-hour TTL to avoid excessive API calls.

Key Components:
    ModelPricing: Immutable dataclass representing pricing per million tokens.
    PricingCache: File-based cache with TTL support for storing pricing data.
    fetch_openrouter_pricing: Fetches pricing from OpenRouter's /api/v1/models endpoint.
    fetch_model_pricing: Main entry point that checks cache then fetches as needed.
    get_model_pricing_sync: Synchronous wrapper for use in non-async contexts.

Typical usage:
    from kin_code.setup.onboarding.services.pricing_service import (
        fetch_model_pricing,
        get_model_pricing_sync,
    )

    # Async context
    pricing = await fetch_model_pricing("openrouter", "https://openrouter.ai/api/v1", "gpt-4o", api_key)

    # Sync context
    pricing = get_model_pricing_sync("openrouter", "https://openrouter.ai/api/v1", "gpt-4o", api_key)
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
from pathlib import Path
import time

import httpx

from kin_code.core.paths.global_paths import KIN_HOME

_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours
_CACHE_FILENAME = "pricing_cache.json"
_HTTP_TIMEOUT = 10.0


@dataclass(frozen=True, slots=True)
class ModelPricing:
    """Pricing information for a model.

    Attributes:
        input_price: Cost per million input tokens.
        output_price: Cost per million output tokens.
        fetched_at: Unix timestamp when pricing was fetched (0 for hardcoded values).
    """

    input_price: float
    output_price: float
    fetched_at: int


class PricingCache:
    """File-based cache for model pricing with 24-hour TTL.

    Stores pricing data in ~/.kin-code/pricing_cache.json as a JSON dict
    mapping cache keys to pricing entries with timestamps.
    """

    def __init__(self, cache_file: Path | None = None) -> None:
        self._cache_file = cache_file or (KIN_HOME.path / _CACHE_FILENAME)
        self._data: dict[str, dict[str, float | int]] | None = None

    def _load(self) -> dict[str, dict[str, float | int]]:
        """Load cache from disk, returning empty dict on any error."""
        if self._data is not None:
            return self._data

        result: dict[str, dict[str, float | int]] = {}
        try:
            if self._cache_file.is_file():
                with self._cache_file.open("r") as f:
                    result = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

        self._data = result
        return result

    def _save(self) -> None:
        """Save cache to disk, creating parent directories if needed."""
        if self._data is None:
            return

        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with self._cache_file.open("w") as f:
                json.dump(self._data, f, indent=2)
        except OSError:
            pass

    def _make_key(self, provider_name: str, model_name: str) -> str:
        """Create a cache key from provider and model names."""
        return f"{provider_name}:{model_name}"

    def get(self, provider_name: str, model_name: str) -> ModelPricing | None:
        """Get cached pricing if present and not expired.

        Args:
            provider_name: Name of the provider (e.g., "openrouter").
            model_name: Name of the model (e.g., "openai/gpt-4o").

        Returns:
            ModelPricing if found and not expired, None otherwise.
        """
        data = self._load()
        key = self._make_key(provider_name, model_name)
        entry = data.get(key)

        if entry is None:
            return None

        fetched_at = int(entry.get("fetched_at", 0))
        now = int(time.time())

        if now - fetched_at > _CACHE_TTL_SECONDS:
            return None

        return ModelPricing(
            input_price=float(entry.get("input_price", 0.0)),
            output_price=float(entry.get("output_price", 0.0)),
            fetched_at=fetched_at,
        )

    def set(self, provider_name: str, model_name: str, pricing: ModelPricing) -> None:
        """Store pricing in the cache.

        Args:
            provider_name: Name of the provider.
            model_name: Name of the model.
            pricing: Pricing data to cache.
        """
        data = self._load()
        key = self._make_key(provider_name, model_name)
        data[key] = {
            "input_price": pricing.input_price,
            "output_price": pricing.output_price,
            "fetched_at": pricing.fetched_at,
        }
        self._save()


# Global cache instance
_pricing_cache = PricingCache()


async def fetch_openrouter_pricing(
    model_name: str, api_key: str | None
) -> ModelPricing | None:
    """Fetch pricing from OpenRouter's /api/v1/models endpoint.

    OpenRouter returns pricing per token as strings that need conversion
    to per-million-tokens float values.

    Args:
        model_name: The OpenRouter model ID (e.g., "openai/gpt-4o").
        api_key: Optional API key for authentication.

    Returns:
        ModelPricing if found, None on any error.
    """
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = "https://openrouter.ai/api/v1/models"

    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for model_data in data.get("data", []):
                if model_data.get("id") == model_name:
                    pricing = model_data.get("pricing", {})
                    prompt_price = pricing.get("prompt")
                    completion_price = pricing.get("completion")

                    if prompt_price is not None and completion_price is not None:
                        # Convert from per-token to per-million-tokens
                        input_price = float(prompt_price) * 1_000_000
                        output_price = float(completion_price) * 1_000_000
                        return ModelPricing(
                            input_price=input_price,
                            output_price=output_price,
                            fetched_at=int(time.time()),
                        )
            return None

    except (httpx.HTTPError, ValueError, KeyError):
        return None


def _is_openrouter_provider(api_base: str) -> bool:
    """Check if the API base URL is for OpenRouter."""
    return "openrouter.ai" in api_base.lower()


async def fetch_model_pricing(
    provider_name: str,
    api_base: str,
    model_name: str,
    api_key: str | None,
) -> ModelPricing | None:
    """Fetch model pricing, checking cache first then provider APIs.

    This is the main entry point for fetching pricing. It:
    1. Checks the local cache for unexpired pricing data
    2. For OpenRouter, fetches from their /api/v1/models endpoint
    3. Caches successful fetches for 24 hours

    Args:
        provider_name: Name of the provider (e.g., "openrouter").
        api_base: Base URL of the provider API.
        model_name: Name of the model to fetch pricing for.
        api_key: Optional API key for authentication.

    Returns:
        ModelPricing if pricing is available, None otherwise.
    """
    # Check cache first
    if cached := _pricing_cache.get(provider_name, model_name):
        return cached

    pricing: ModelPricing | None = None

    # Handle different providers
    if _is_openrouter_provider(api_base):
        pricing = await fetch_openrouter_pricing(model_name, api_key)

    # Cache the result if we got pricing
    if pricing:
        _pricing_cache.set(provider_name, model_name, pricing)

    return pricing


def get_model_pricing_sync(
    provider_name: str,
    api_base: str,
    model_name: str,
    api_key: str | None,
) -> ModelPricing | None:
    """Synchronous wrapper for fetch_model_pricing.

    Uses cached data when available to avoid blocking. Falls back to
    running the async fetch in an event loop only when needed for
    providers that require API calls.

    Args:
        provider_name: Name of the provider.
        api_base: Base URL of the provider API.
        model_name: Name of the model.
        api_key: Optional API key.

    Returns:
        ModelPricing if available, None otherwise.
    """
    # Check cache first (fast path)
    if cached := _pricing_cache.get(provider_name, model_name):
        return cached

    # For providers that need API calls, try to run async
    if _is_openrouter_provider(api_base):
        try:
            # Check if we're in an async context
            try:
                asyncio.get_running_loop()
                # Already in async context - run in a thread to avoid blocking
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        asyncio.run,
                        fetch_model_pricing(provider_name, api_base, model_name, api_key),
                    )
                    return future.result(timeout=15.0)
            except RuntimeError:
                # No running loop, create one directly
                return asyncio.run(
                    fetch_model_pricing(provider_name, api_base, model_name, api_key)
                )
        except Exception:
            return None

    return None

from __future__ import annotations

import os

from kin_code.core.config import VibeConfig
from kin_code.setup.onboarding.services.pricing_service import get_model_pricing_sync


def resolve_model_pricing(config: VibeConfig) -> tuple[float, float]:
    """Resolve model pricing, auto-fetching from provider if not configured.

    Returns:
        Tuple of (input_price_per_million, output_price_per_million).
        Returns (0.0, 0.0) if pricing cannot be determined.
    """
    try:
        model = config.get_active_model()
        provider = config.get_provider_for_model(model)
    except ValueError:
        return 0.0, 0.0

    # Use configured prices if available
    if model.input_price is not None and model.output_price is not None:
        return model.input_price, model.output_price

    # Try to auto-fetch from provider API
    api_key = os.getenv(provider.api_key_env_var) if provider.api_key_env_var else None
    pricing = get_model_pricing_sync(
        provider_name=provider.name,
        api_base=provider.api_base,
        model_name=model.name,
        api_key=api_key,
    )

    if pricing:
        return pricing.input_price, pricing.output_price

    # Fall back to configured prices (may be partial) or 0.0
    return model.input_price or 0.0, model.output_price or 0.0


def resolve_context_window(config: VibeConfig) -> int:
    """Resolve context window size from model config.

    Fallback chain:
    1. model.context_window (set during onboarding)
    2. auto_compact_threshold (user-configurable default)
    """
    try:
        model = config.get_active_model()
        if model.context_window is not None:
            return model.context_window
    except ValueError:
        pass
    return config.auto_compact_threshold

"""Services for the onboarding flow."""

from __future__ import annotations

from kin_code.setup.onboarding.services.model_discovery import (
    DiscoveredModel,
    fetch_models,
    test_connection,
)

__all__ = ["DiscoveredModel", "fetch_models", "test_connection"]

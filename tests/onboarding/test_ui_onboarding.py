from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tomllib
from unittest.mock import AsyncMock, patch

import pytest
from textual.events import Resize
from textual.geometry import Size
from textual.pilot import Pilot
from textual.widgets import Input

from kin_code.core.paths.global_paths import GLOBAL_CONFIG_FILE, GLOBAL_ENV_FILE
from kin_code.setup.onboarding import OnboardingApp
from kin_code.setup.onboarding.screens.api_key import ApiKeyScreen
from kin_code.setup.onboarding.screens.brave_search import BraveSearchScreen
from kin_code.setup.onboarding.screens.model_setup import ModelSetupScreen
from kin_code.setup.onboarding.screens.provider_selection import ProviderSelectionScreen
from kin_code.setup.onboarding.screens.theme_selection import ThemeSelectionScreen
from kin_code.setup.onboarding.services.model_discovery import DiscoveredModel


async def _wait_for(
    condition: Callable[[], bool],
    pilot: Pilot,
    timeout: float = 10.0,
    interval: float = 0.05,
) -> None:
    elapsed = 0.0
    while not condition():
        await pilot.pause(interval)
        if (elapsed := elapsed + interval) >= timeout:
            msg = "Timed out waiting for condition."
            raise AssertionError(msg)


async def pass_welcome_screen(pilot: Pilot) -> None:
    welcome_screen = pilot.app.get_screen("welcome")
    await _wait_for(
        lambda: not welcome_screen.query_one("#enter-hint").has_class("hidden"), pilot
    )
    await pilot.press("enter")
    await _wait_for(lambda: isinstance(pilot.app.screen, ThemeSelectionScreen), pilot)


@pytest.mark.asyncio
async def test_ui_gets_through_the_onboarding_successfully() -> None:
    app = OnboardingApp()
    api_key_value = "sk-onboarding-test-key"
    mock_models = [
        DiscoveredModel(id="gpt-4o", context_window=128000),
        DiscoveredModel(id="gpt-3.5-turbo", context_window=16000),
    ]

    with patch(
        "kin_code.setup.onboarding.screens.model_setup.fetch_models",
        new_callable=AsyncMock,
        return_value=mock_models,
    ):
        async with app.run_test() as pilot:
            # Screen 1: Welcome -> Theme Selection
            await pass_welcome_screen(pilot)

            # Screen 2: Theme Selection -> Provider Selection
            await pilot.press("enter")
            await _wait_for(
                lambda: isinstance(app.screen, ProviderSelectionScreen), pilot
            )

            # Screen 3: Provider Selection -> API Key (default is OpenRouter)
            await pilot.press("enter")
            await _wait_for(lambda: isinstance(app.screen, ApiKeyScreen), pilot)
            api_screen = app.screen
            input_widget = api_screen.query_one("#key", Input)
            await pilot.press(*api_key_value)
            assert input_widget.value == api_key_value

            # Screen 4: API Key -> Model Setup
            await pilot.press("enter")
            await _wait_for(lambda: isinstance(app.screen, ModelSetupScreen), pilot)

            # Wait for model list to load (mocked)
            model_screen = app.screen
            await _wait_for(
                lambda: len(model_screen._filtered_models) > 0,  # type: ignore[union-attr]
                pilot,
            )

            # Screen 5: Model Setup -> Brave Search (select first model)
            await pilot.press("enter")
            await _wait_for(lambda: isinstance(app.screen, BraveSearchScreen), pilot)

            # Screen 6: Brave Search -> Complete (skip with escape)
            await pilot.press("escape")
            await _wait_for(lambda: app.return_value is not None, pilot)

    assert app.return_value == "completed"

    assert GLOBAL_ENV_FILE.path.is_file()
    env_contents = GLOBAL_ENV_FILE.path.read_text(encoding="utf-8")
    # Default provider is OpenRouter
    assert "OPENROUTER_API_KEY" in env_contents
    assert api_key_value in env_contents

    assert GLOBAL_CONFIG_FILE.path.is_file()
    config_contents = GLOBAL_CONFIG_FILE.path.read_text(encoding="utf-8")
    config_dict = tomllib.loads(config_contents)
    assert config_dict.get("textual_theme") == app.theme
    # Check that a model was saved (models are sorted alphabetically)
    assert config_dict.get("active_model") == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_ui_can_pick_a_theme_and_saves_selection(config_dir: Path) -> None:
    app = OnboardingApp()

    async with app.run_test() as pilot:
        await pass_welcome_screen(pilot)

        theme_screen = app.screen
        assert isinstance(theme_screen, ThemeSelectionScreen)
        app.post_message(
            Resize(Size(40, 10), Size(40, 10))
        )  # trigger the resize event handler
        preview = theme_screen.query_one("#preview")
        assert preview.styles.max_height is not None
        target_theme = "gruvbox"
        # Use the screen's available themes which accounts for terminal theme availability
        available_themes = theme_screen._available_themes
        assert target_theme in available_themes
        start_index = theme_screen._theme_index
        target_index = available_themes.index(target_theme)
        steps_down = (target_index - start_index) % len(available_themes)
        await pilot.press(*["down"] * steps_down)
        assert app.theme == target_theme
        await pilot.press("enter")
        # Theme selection now goes to provider selection, not API key directly
        await _wait_for(lambda: isinstance(app.screen, ProviderSelectionScreen), pilot)

    assert GLOBAL_CONFIG_FILE.path.is_file()
    config_contents = GLOBAL_CONFIG_FILE.path.read_text(encoding="utf-8")
    config_dict = tomllib.loads(config_contents)
    assert config_dict.get("textual_theme") == target_theme

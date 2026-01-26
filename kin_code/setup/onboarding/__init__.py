from __future__ import annotations

import sys

from rich import print as rprint
from textual.app import App
from textual.theme import Theme

from kin_code.cli.textual_ui.terminal_theme import (
    TERMINAL_THEME_NAME,
    capture_terminal_theme,
)
from kin_code.core.config import Backend, KinConfig, ModelConfig, ProviderConfig
from kin_code.core.paths.global_paths import GLOBAL_ENV_FILE
from kin_code.setup.onboarding.presets import ProviderPreset
from kin_code.setup.onboarding.screens import (
    ApiKeyScreen,
    OpenAIApiKeyScreen,
    OpenAIModelScreen,
    OpenAIProviderScreen,
    ProviderSelectionScreen,
    ProviderType,
    ThemeSelectionScreen,
    WelcomeScreen,
)


class OnboardingApp(App[str | None]):
    CSS_PATH = "onboarding.tcss"

    def __init__(self) -> None:
        super().__init__()
        self._terminal_theme: Theme | None = capture_terminal_theme()
        # OpenAI-compatible provider flow state
        self.selected_provider: ProviderType | None = None
        self.openai_preset: ProviderPreset | None = None
        self.openai_base_url: str | None = None
        self.openai_api_key: str | None = None
        self.openai_model_name: str | None = None
        self.skip_api_key: bool = False
        self.openai_model_context_window: int | None = None

    def on_mount(self) -> None:
        if self._terminal_theme:
            self.register_theme(self._terminal_theme)
            self.theme = TERMINAL_THEME_NAME

        self.install_screen(WelcomeScreen(), "welcome")
        self.install_screen(ProviderSelectionScreen(), "provider_selection")
        self.install_screen(OpenAIProviderScreen(), "openai_provider")
        self.install_screen(OpenAIApiKeyScreen(), "openai_api_key")
        self.install_screen(OpenAIModelScreen(), "openai_model")
        self.install_screen(ThemeSelectionScreen(), "theme_selection")
        self.install_screen(ApiKeyScreen(), "api_key")
        self.push_screen("welcome")


def _save_openai_provider_config(app: OnboardingApp | AddProviderApp) -> None:
    """Save OpenAI-compatible provider and model configuration.

    Args:
        app: The onboarding app instance containing the provider state.
    """
    preset = app.openai_preset
    base_url = app.openai_base_url
    model_name = app.openai_model_name

    if not preset or not base_url or not model_name:
        return

    provider_id = preset.id if preset.id != "custom" else "custom"
    provider_config = ProviderConfig(
        name=provider_id,
        api_base=base_url,
        api_key_env_var=preset.api_key_env_var,
        backend=Backend.GENERIC,
    )
    model_alias = f"{provider_id}-{model_name}"
    model_config = ModelConfig(
        name=model_name,
        provider=provider_id,
        alias=model_alias,
        temperature=0.2,
        context_window=app.openai_model_context_window,
    )

    KinConfig.save_updates({
        "providers": [provider_config.model_dump()],
        "models": [model_config.model_dump()],
        "active_model": model_alias,
    })


def run_onboarding(app: App | None = None) -> None:
    onboarding_app = app or OnboardingApp()
    result = onboarding_app.run()
    match result:
        case None:
            rprint("\n[yellow]Setup cancelled. See you next time![/]")
            sys.exit(0)
        case str() as s if s.startswith("save_error:"):
            err = s.removeprefix("save_error:")
            rprint(
                f"\n[yellow]Warning: Could not save API key to .env file: {err}[/]"
                "\n[dim]The API key is set for this session only. "
                f"You may need to set it manually in {GLOBAL_ENV_FILE.path}[/]\n"
            )
        case "completed":
            # Save OpenAI provider config if the user completed that flow
            if (
                isinstance(onboarding_app, OnboardingApp)
                and onboarding_app.openai_preset
            ):
                _save_openai_provider_config(onboarding_app)


class AddProviderApp(App[str | None]):
    """App for adding a new OpenAI-compatible provider (--add-provider flow)."""

    CSS_PATH = "onboarding.tcss"

    def __init__(self) -> None:
        super().__init__()
        self._terminal_theme: Theme | None = capture_terminal_theme()
        # OpenAI-compatible provider flow state
        self.selected_provider: ProviderType | None = None
        self.openai_preset: ProviderPreset | None = None
        self.openai_base_url: str | None = None
        self.openai_api_key: str | None = None
        self.openai_model_name: str | None = None
        self.skip_api_key: bool = False
        self.openai_model_context_window: int | None = None

    def on_mount(self) -> None:
        if self._terminal_theme:
            self.register_theme(self._terminal_theme)
            self.theme = TERMINAL_THEME_NAME

        self.install_screen(OpenAIProviderScreen(), "openai_provider")
        self.install_screen(OpenAIApiKeyScreen(), "openai_api_key")
        self.install_screen(OpenAIModelScreen(), "openai_model")
        self.push_screen("openai_provider")


def run_add_provider(app: App | None = None) -> None:
    """Run the add provider flow for OpenAI-compatible endpoints.

    Args:
        app: Optional app instance for testing. If None, creates AddProviderApp.
    """
    add_provider_app = app or AddProviderApp()
    result = add_provider_app.run()
    match result:
        case None:
            rprint("\n[yellow]Provider setup cancelled.[/]")
            sys.exit(0)
        case str() as s if s.startswith("save_error:"):
            err = s.removeprefix("save_error:")
            rprint(
                f"\n[yellow]Warning: Could not save API key to .env file: {err}[/]"
                "\n[dim]The API key is set for this session only. "
                f"You may need to set it manually in {GLOBAL_ENV_FILE.path}[/]\n"
            )
        case "completed":
            if (
                isinstance(add_provider_app, AddProviderApp)
                and add_provider_app.openai_preset
            ):
                _save_openai_provider_config(add_provider_app)
                rprint("\n[green]Provider and model configured successfully![/]")

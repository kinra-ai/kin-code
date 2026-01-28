from __future__ import annotations

import sys

from rich import print as rprint
from textual.app import App
from textual.theme import Theme

from kin_code.cli.textual_ui.terminal_theme import (
    TERMINAL_THEME_NAME,
    capture_terminal_theme,
)
from kin_code.core.paths.global_paths import GLOBAL_ENV_FILE
from kin_code.setup.onboarding.presets import PROVIDER_PRESETS, ProviderPreset
from kin_code.setup.onboarding.screens import (
    ApiKeyScreen,
    BraveSearchScreen,
    ModelSetupScreen,
    ProviderSelectionScreen,
    ThemeSelectionScreen,
    WelcomeScreen,
)


class OnboardingApp(App[str | None]):
    CSS_PATH = "onboarding.tcss"

    def __init__(self) -> None:
        super().__init__()
        self._terminal_theme: Theme | None = capture_terminal_theme()
        self.selected_preset: ProviderPreset = PROVIDER_PRESETS[0]

    def on_mount(self) -> None:
        if self._terminal_theme:
            self.register_theme(self._terminal_theme)
            self.theme = TERMINAL_THEME_NAME

        self.install_screen(WelcomeScreen(), "welcome")
        self.install_screen(ThemeSelectionScreen(), "theme_selection")
        self.install_screen(ProviderSelectionScreen(), "provider_selection")
        self.install_screen(ApiKeyScreen(), "api_key")
        # ModelSetupScreen is created fresh each time to avoid installed screen issues
        self.install_screen(BraveSearchScreen(), "brave_search")
        self.push_screen("welcome")

    def push_model_setup(self) -> None:
        """Push a fresh ModelSetupScreen instance."""
        self.push_screen(ModelSetupScreen())


def run_onboarding(app: App | None = None) -> None:
    result = (app or OnboardingApp()).run()
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
            rprint(
                '\nSetup complete! Run "kin" to start using Kin Code.\n'
            )

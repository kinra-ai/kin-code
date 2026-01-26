"""Screen for entering API key for OpenAI-compatible providers."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from dotenv import set_key
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.events import MouseUp
from textual.validation import Length
from textual.widgets import Input, Link

from kin_code.cli.clipboard import copy_selection_to_clipboard
from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.core.paths.global_paths import GLOBAL_ENV_FILE
from kin_code.setup.onboarding.base import OnboardingScreen
from kin_code.setup.onboarding.presets import ProviderPreset

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp


def _save_api_key_to_env_file(env_key: str, api_key: str) -> None:
    """Save API key to the global .env file.

    Args:
        env_key: Environment variable name.
        api_key: The API key value to save.
    """
    GLOBAL_ENV_FILE.path.parent.mkdir(parents=True, exist_ok=True)
    set_key(GLOBAL_ENV_FILE.path, env_key, api_key)


class OpenAIApiKeyScreen(OnboardingScreen):
    """Screen for entering an API key for OpenAI-compatible providers."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = "openai_model"

    def __init__(self) -> None:
        super().__init__()
        self._preset: ProviderPreset | None = None

    def _compose_provider_link(self) -> ComposeResult:
        if not self._preset or not self._preset.help_url:
            return

        yield NoMarkupStatic("Get your API key from:")
        yield Center(
            Horizontal(
                NoMarkupStatic("-> ", classes="link-chevron"),
                Link(self._preset.help_url, url=self._preset.help_url),
                classes="link-row",
            )
        )

    def compose(self) -> ComposeResult:
        app: OnboardingApp = self.app  # type: ignore[assignment]
        self._preset = getattr(app, "openai_preset", None)

        provider_name = self._preset.name if self._preset else "Provider"

        self.input_widget = Input(
            password=True,
            id="key",
            placeholder="Paste your API key here",
            validators=[Length(minimum=1, failure_description="No API key provided.")],
        )

        with Vertical(id="api-key-outer"):
            yield NoMarkupStatic("", classes="spacer")
            yield Center(
                NoMarkupStatic(
                    f"Enter your {provider_name} API key", id="api-key-title"
                )
            )
            with Center():
                with Vertical(id="api-key-content"):
                    yield from self._compose_provider_link()
                    yield NoMarkupStatic("", classes="spacer-small")
                    yield Center(Horizontal(self.input_widget, id="input-box"))
                    yield NoMarkupStatic("", id="feedback")
            yield NoMarkupStatic("", classes="spacer")

    def on_mount(self) -> None:
        app: OnboardingApp = self.app  # type: ignore[assignment]
        self._preset = getattr(app, "openai_preset", None)
        self.input_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        feedback = self.query_one("#feedback", NoMarkupStatic)
        input_box = self.query_one("#input-box")

        if event.validation_result is None:
            return

        input_box.remove_class("valid", "invalid")
        feedback.remove_class("error", "success")

        if event.validation_result.is_valid:
            feedback.update("Press Enter to submit")
            feedback.add_class("success")
            input_box.add_class("valid")
            return

        descriptions = event.validation_result.failure_descriptions
        feedback.update(descriptions[0])
        feedback.add_class("error")
        input_box.add_class("invalid")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and event.validation_result.is_valid:
            self._save_and_continue(event.value)

    def _save_and_continue(self, api_key: str) -> None:
        """Save the API key and navigate to the next screen.

        Args:
            api_key: The API key entered by the user.
        """
        if not self._preset:
            self.action_next()
            return

        env_key = self._preset.api_key_env_var
        if env_key:
            os.environ[env_key] = api_key
            try:
                _save_api_key_to_env_file(env_key, api_key)
            except OSError as err:
                self.app.exit(f"save_error:{err}")
                return

        app: OnboardingApp = self.app  # type: ignore[assignment]
        app.openai_api_key = api_key  # type: ignore[attr-defined]

        self.action_next()

    def on_mouse_up(self, event: MouseUp) -> None:
        copy_selection_to_clipboard(self.app)

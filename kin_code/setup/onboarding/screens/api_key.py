from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from dotenv import set_key
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.events import MouseUp
from textual.validation import Length
from textual.widgets import Input, Link, Static

from kin_code.cli.clipboard import copy_selection_to_clipboard
from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.core.paths.global_paths import GLOBAL_ENV_FILE
from kin_code.setup.onboarding.base import OnboardingScreen
from kin_code.setup.onboarding.presets import ProviderPreset

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp

CONFIG_DOCS_URL = "https://github.com/binarycodon/kin-code#configuration"


def _save_api_key_to_env_file(env_key: str, api_key: str) -> None:
    GLOBAL_ENV_FILE.path.parent.mkdir(parents=True, exist_ok=True)
    set_key(GLOBAL_ENV_FILE.path, env_key, api_key)


class ApiKeyScreen(OnboardingScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = "model_setup"

    def __init__(self) -> None:
        super().__init__()
        self._preset: ProviderPreset | None = None

    @property
    def preset(self) -> ProviderPreset:
        if self._preset is None:
            app: OnboardingApp = self.app  # type: ignore[assignment]
            self._preset = app.selected_preset
        return self._preset

    def _compose_provider_link(self) -> ComposeResult:
        if not self.preset.api_key_help_url:
            return

        provider_name = self.preset.name.split(" ")[0]
        yield NoMarkupStatic(f"Grab your {provider_name} API key:")
        yield Center(
            Horizontal(
                NoMarkupStatic("\u2192 ", classes="link-chevron"),
                Link(self.preset.api_key_help_url, url=self.preset.api_key_help_url),
                classes="link-row",
            )
        )

    def _compose_config_docs(self) -> ComposeResult:
        yield Static("[dim]Learn more about Kin Code configuration:[/]")
        yield Horizontal(
            NoMarkupStatic("\u2192 ", classes="link-chevron"),
            Link(CONFIG_DOCS_URL, url=CONFIG_DOCS_URL),
            classes="link-row",
        )

    def compose(self) -> ComposeResult:
        self.input_widget = Input(
            password=True,
            id="key",
            placeholder="Paste your API key here",
            validators=[Length(minimum=1, failure_description="No API key provided.")],
        )

        with Vertical(id="api-key-outer"):
            yield NoMarkupStatic("", classes="spacer")
            yield Center(NoMarkupStatic("API Key Required", id="api-key-title"))
            with Center():
                with Vertical(id="api-key-content"):
                    yield from self._compose_provider_link()
                    yield NoMarkupStatic(
                        "Paste your API key below:", id="paste-hint"
                    )
                    yield Center(Horizontal(self.input_widget, id="input-box"))
                    yield NoMarkupStatic("", id="feedback")
            yield NoMarkupStatic("", classes="spacer")
            yield Vertical(
                Vertical(*self._compose_config_docs(), id="config-docs-group"),
                id="config-docs-section",
            )

    def on_mount(self) -> None:
        self.input_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        feedback = self.query_one("#feedback", NoMarkupStatic)
        input_box = self.query_one("#input-box")

        if event.validation_result is None:
            return

        input_box.remove_class("valid", "invalid")
        feedback.remove_class("error", "success")

        if event.validation_result.is_valid:
            feedback.update("Press Enter to submit ↵")
            feedback.add_class("success")
            input_box.add_class("valid")
            return

        descriptions = event.validation_result.failure_descriptions
        feedback.update(descriptions[0])
        feedback.add_class("error")
        input_box.add_class("invalid")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and event.validation_result.is_valid:
            self._save_and_finish(event.value)

    def _save_and_finish(self, api_key: str) -> None:
        env_key = self.preset.api_key_env_var
        os.environ[env_key] = api_key
        try:
            _save_api_key_to_env_file(env_key, api_key)
        except OSError as err:
            self.app.exit(f"save_error:{err}")
            return
        # Push fresh ModelSetupScreen to avoid installed screen issues
        app: OnboardingApp = self.app  # type: ignore[assignment]
        app.push_model_setup()

    def on_mouse_up(self, _: MouseUp) -> None:
        copy_selection_to_clipboard(self.app)

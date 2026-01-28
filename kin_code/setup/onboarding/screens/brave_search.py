"""Brave Search API key screen for onboarding."""

from __future__ import annotations

import os
from typing import ClassVar

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

BRAVE_API_KEY_ENV = "BRAVE_API_KEY"
BRAVE_API_KEY_URL = "https://brave.com/search/api/"


def _save_api_key_to_env_file(env_key: str, api_key: str) -> None:
    GLOBAL_ENV_FILE.path.parent.mkdir(parents=True, exist_ok=True)
    set_key(GLOBAL_ENV_FILE.path, env_key, api_key)


class BraveSearchScreen(OnboardingScreen):
    """Screen for collecting Brave Search API key (optional)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "submit_or_skip", "Submit", show=False, priority=True),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "skip", "Skip", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self.input_widget: Input

    def compose(self) -> ComposeResult:
        self.input_widget = Input(
            password=True,
            id="brave-key",
            placeholder="Paste your Brave Search API key (optional)",
            validators=[Length(minimum=1, failure_description="No API key provided.")],
        )

        with Vertical(id="brave-outer"):
            yield NoMarkupStatic("", classes="spacer")
            yield Center(NoMarkupStatic("Web Search (Optional)", id="brave-title"))
            with Center():
                with Vertical(id="brave-content"):
                    yield NoMarkupStatic(
                        "Enable web search by adding a Brave Search API key:"
                    )
                    yield Center(
                        Horizontal(
                            NoMarkupStatic("\u2192 ", classes="link-chevron"),
                            Link(BRAVE_API_KEY_URL, url=BRAVE_API_KEY_URL),
                            classes="link-row",
                        )
                    )
                    yield NoMarkupStatic(
                        "Paste your API key below, or press Escape to skip:",
                        id="brave-hint",
                    )
                    yield Center(Horizontal(self.input_widget, id="brave-input-box"))
                    yield NoMarkupStatic("", id="brave-feedback")
            yield NoMarkupStatic("", classes="spacer")
            yield Center(
                NoMarkupStatic(
                    "[dim]Press Escape to skip and continue without web search[/]",
                    id="skip-hint",
                )
            )

    def on_mount(self) -> None:
        self.input_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        feedback = self.query_one("#brave-feedback", NoMarkupStatic)
        input_box = self.query_one("#brave-input-box")

        if event.validation_result is None:
            return

        input_box.remove_class("valid", "invalid")
        feedback.remove_class("error", "success")

        if event.validation_result.is_valid:
            feedback.update("Press Enter to save \u21b5")
            feedback.add_class("success")
            input_box.add_class("valid")
            return

        feedback.update("")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and event.validation_result.is_valid:
            self._save_and_finish(event.value)

    def action_submit_or_skip(self) -> None:
        value = self.input_widget.value.strip()
        if value:
            self._save_and_finish(value)
        else:
            self._finish()

    def action_skip(self) -> None:
        self._finish()

    def _save_and_finish(self, api_key: str) -> None:
        os.environ[BRAVE_API_KEY_ENV] = api_key
        try:
            _save_api_key_to_env_file(BRAVE_API_KEY_ENV, api_key)
        except OSError as err:
            self.app.exit(f"save_error:{err}")
            return
        self._finish()

    def _finish(self) -> None:
        self.app.exit("completed")

    def on_mouse_up(self, _: MouseUp) -> None:
        copy_selection_to_clipboard(self.app)

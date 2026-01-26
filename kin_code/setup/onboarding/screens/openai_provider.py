"""Screen for configuring an OpenAI-compatible provider endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, Input

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.setup.onboarding.base import OnboardingScreen
from kin_code.setup.onboarding.presets import PROVIDER_PRESETS, ProviderPreset
from kin_code.setup.onboarding.services.model_discovery import test_connection

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp


class OpenAIProviderScreen(OnboardingScreen):
    """Screen for selecting an OpenAI-compatible provider and configuring the base URL."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "submit", "Continue", show=False, priority=True),
        Binding("up", "prev_preset", "Previous", show=False),
        Binding("down", "next_preset", "Next", show=False),
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self._preset_index = 0
        self._preset_widgets: list[NoMarkupStatic] = []
        self._connection_tested = False
        self._connection_success = False

    @property
    def _selected_preset(self) -> ProviderPreset:
        return PROVIDER_PRESETS[self._preset_index]

    def _compose_preset_list(self) -> ComposeResult:
        for preset in PROVIDER_PRESETS:
            widget = NoMarkupStatic(preset.name, classes="preset-item")
            self._preset_widgets.append(widget)
            yield widget

    def compose(self) -> ComposeResult:
        self._url_input = Input(
            value=self._selected_preset.base_url,
            id="base-url-input",
            placeholder="Enter base URL (e.g., http://localhost:11434/v1)",
        )

        with Center(id="openai-provider-outer"):
            with Vertical(id="openai-provider-content"):
                yield NoMarkupStatic(
                    "Configure OpenAI-Compatible Endpoint", id="openai-provider-title"
                )

                with Center():
                    with Horizontal(id="provider-selection-row"):
                        yield NoMarkupStatic("Navigate \u2191 \u2193", id="nav-hint")
                        yield Vertical(
                            *self._compose_preset_list(), id="preset-list"
                        )
                        yield NoMarkupStatic("", id="spacer-hint")

                yield NoMarkupStatic("Base URL:", id="url-label")
                with Center():
                    yield Horizontal(self._url_input, id="url-input-box")

                with Center():
                    with Horizontal(id="test-row"):
                        yield Button("Test Connection", id="test-button")
                        yield NoMarkupStatic("", id="test-status")

                yield Center(
                    NoMarkupStatic("Press Enter to continue \u21b5", id="continue-hint")
                )

    def on_mount(self) -> None:
        self._update_preset_display()
        self.focus()

    def _update_preset_display(self) -> None:
        for i, widget in enumerate(self._preset_widgets):
            widget.remove_class("selected")
            preset = PROVIDER_PRESETS[i]

            if i == self._preset_index:
                widget.update(f" \u25cf {preset.name} ")
                widget.add_class("selected")
            else:
                widget.update(f" \u25cb {preset.name}")

    def _navigate_preset(self, direction: int) -> None:
        self._preset_index = (self._preset_index + direction) % len(PROVIDER_PRESETS)
        self._update_preset_display()

        selected = self._selected_preset
        if selected.base_url:
            self._url_input.value = selected.base_url

        self._reset_connection_status()

    def _reset_connection_status(self) -> None:
        self._connection_tested = False
        self._connection_success = False
        status = self.query_one("#test-status", NoMarkupStatic)
        status.update("")
        status.remove_class("success", "error", "testing")

    def action_prev_preset(self) -> None:
        self._navigate_preset(-1)

    def action_next_preset(self) -> None:
        self._navigate_preset(1)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "base-url-input":
            self._reset_connection_status()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "test-button":
            await self._test_connection()

    async def _test_connection(self) -> None:
        status = self.query_one("#test-status", NoMarkupStatic)
        button = self.query_one("#test-button", Button)

        status.remove_class("success", "error", "testing")
        status.update("Testing...")
        status.add_class("testing")
        button.disabled = True

        base_url = self._url_input.value.strip()
        if not base_url:
            status.update("\u2717 No URL provided")
            status.remove_class("testing")
            status.add_class("error")
            button.disabled = False
            self._connection_tested = True
            self._connection_success = False
            return

        success, message = await test_connection(base_url)

        status.remove_class("testing")
        self._connection_tested = True
        self._connection_success = success

        if success:
            status.update(f"\u2713 {message}")
            status.add_class("success")
        else:
            status.update(f"\u2717 {message}")
            status.add_class("error")

        button.disabled = False

    def action_submit(self) -> None:
        base_url = self._url_input.value.strip()
        if not base_url:
            status = self.query_one("#test-status", NoMarkupStatic)
            status.remove_class("success", "error", "testing")
            status.update("\u2717 Please enter a base URL")
            status.add_class("error")
            return

        app: OnboardingApp = self.app  # type: ignore[assignment]
        app.openai_preset = self._selected_preset  # type: ignore[attr-defined]
        app.openai_base_url = base_url  # type: ignore[attr-defined]

        if self._selected_preset.requires_api_key:
            self.app.switch_screen("openai_api_key")
        else:
            self.app.switch_screen("openai_model")

"""Provider selection screen for onboarding."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.validation import Length, Regex
from textual.widgets import Input, Static

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.setup.onboarding.base import OnboardingScreen
from kin_code.setup.onboarding.presets import PROVIDER_PRESETS, ProviderPreset

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp

VISIBLE_NEIGHBORS = 2
FADE_CLASSES = ["fade-1", "fade-2", "fade-3"]

URL_PATTERN = r"^https?://[^\s/$.?#].[^\s]*$"


class ProviderSelectionScreen(OnboardingScreen):
    """Screen for selecting an OpenAI-compatible provider."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select", "Select", show=False, priority=True),
        Binding("up", "prev_provider", "Previous", show=False),
        Binding("down", "next_provider", "Next", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = "api_key"

    def __init__(self) -> None:
        super().__init__()
        self._provider_index = 0
        self._provider_widgets: list[Static] = []
        self._custom_url_input: Input | None = None
        self._in_url_input_mode = False

    @property
    def _selected_preset(self) -> ProviderPreset:
        return PROVIDER_PRESETS[self._provider_index]

    def _compose_provider_list(self) -> ComposeResult:
        for _ in range(VISIBLE_NEIGHBORS * 2 + 1):
            widget = NoMarkupStatic("", classes="provider-item")
            self._provider_widgets.append(widget)
            yield widget

    def compose(self) -> ComposeResult:
        self._custom_url_input = Input(
            id="custom-url",
            placeholder="https://your-server.com/v1",
            validators=[
                Length(minimum=1, failure_description="URL required"),
                Regex(URL_PATTERN, failure_description="Invalid URL format"),
            ],
        )

        with Center(id="provider-outer"):
            with Vertical(id="provider-content"):
                yield NoMarkupStatic(
                    "Select your AI provider", id="provider-title"
                )
                yield Center(
                    Horizontal(
                        NoMarkupStatic("Navigate \u2191 \u2193", id="provider-nav-hint"),
                        Vertical(
                            *self._compose_provider_list(), id="provider-list"
                        ),
                        NoMarkupStatic("Press Enter \u21b5", id="provider-enter-hint"),
                        id="provider-row",
                    )
                )
                with Vertical(id="custom-url-section", classes="hidden"):
                    yield NoMarkupStatic(
                        "Enter your API base URL:", id="custom-url-label"
                    )
                    yield Center(Horizontal(self._custom_url_input, id="custom-url-box"))
                    yield NoMarkupStatic("", id="custom-url-feedback")

    def on_mount(self) -> None:
        self._update_display()
        self.focus()

    def _get_provider_at_offset(self, offset: int) -> ProviderPreset:
        index = (self._provider_index + offset) % len(PROVIDER_PRESETS)
        return PROVIDER_PRESETS[index]

    def _update_display(self) -> None:
        for i, widget in enumerate(self._provider_widgets):
            offset = i - VISIBLE_NEIGHBORS
            preset = self._get_provider_at_offset(offset)

            widget.remove_class("selected", *FADE_CLASSES)

            if offset == 0:
                widget.update(f" {preset.name} ")
                widget.add_class("selected")
            else:
                distance = min(abs(offset) - 1, len(FADE_CLASSES) - 1)
                widget.update(preset.name)
                widget.add_class(FADE_CLASSES[distance])

        custom_section = self.query_one("#custom-url-section")
        if self._selected_preset.id == "custom":
            custom_section.remove_class("hidden")
        else:
            custom_section.add_class("hidden")

    def _navigate(self, direction: int) -> None:
        if self._in_url_input_mode:
            return
        self._provider_index = (self._provider_index + direction) % len(
            PROVIDER_PRESETS
        )
        self._update_display()

    def action_next_provider(self) -> None:
        self._navigate(1)

    def action_prev_provider(self) -> None:
        self._navigate(-1)

    def action_select(self) -> None:
        preset = self._selected_preset

        if preset.id == "custom":
            if not self._in_url_input_mode:
                self._in_url_input_mode = True
                if self._custom_url_input:
                    self._custom_url_input.focus()
                return

        self._save_and_continue(preset)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "custom-url":
            return

        feedback = self.query_one("#custom-url-feedback", NoMarkupStatic)
        input_box = self.query_one("#custom-url-box")

        if event.validation_result is None:
            return

        input_box.remove_class("valid", "invalid")
        feedback.remove_class("error", "success")

        if event.validation_result.is_valid:
            feedback.update("Press Enter to continue \u21b5")
            feedback.add_class("success")
            input_box.add_class("valid")
            return

        descriptions = event.validation_result.failure_descriptions
        feedback.update(descriptions[0])
        feedback.add_class("error")
        input_box.add_class("invalid")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "custom-url":
            return

        if event.validation_result and event.validation_result.is_valid:
            custom_preset = ProviderPreset(
                id="custom",
                name="Custom",
                base_url=event.value.rstrip("/"),
                requires_api_key=True,
                api_key_env_var="CUSTOM_API_KEY",
            )
            self._save_and_continue(custom_preset)

    def _save_and_continue(self, preset: ProviderPreset) -> None:
        app: OnboardingApp = self.app  # type: ignore[assignment]
        app.selected_preset = preset

        if preset.requires_api_key:
            self.app.switch_screen("api_key")
        else:
            # Push fresh ModelSetupScreen to avoid installed screen issues
            app.push_model_setup()

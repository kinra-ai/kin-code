"""Model setup screen for onboarding."""

from __future__ import annotations

from enum import StrEnum, auto
import os
from typing import TYPE_CHECKING, ClassVar

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.events import Key
from textual.validation import Length
from textual.widgets import Input, Static

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.core.autocompletion.fuzzy import fuzzy_match
from kin_code.core.config import ModelConfig, ProviderConfig, VibeConfig
from kin_code.setup.onboarding.base import OnboardingScreen
from kin_code.setup.onboarding.presets import ProviderPreset
from kin_code.setup.onboarding.services.model_discovery import (
    DiscoveredModel,
    fetch_models,
)

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp


class ScreenState(StrEnum):
    """State of the model setup screen."""

    LOADING = auto()
    MODEL_LIST = auto()
    MANUAL_ENTRY = auto()
    ERROR = auto()


VISIBLE_MODELS = 5


class ModelSetupScreen(OnboardingScreen):
    """Screen for discovering and selecting a model."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select", "Select", show=False, priority=True),
        Binding("up", "prev_model", "Previous", show=False),
        Binding("down", "next_model", "Next", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "go_back", "Back", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self._state = ScreenState.LOADING
        self._preset: ProviderPreset | None = None
        self._models: list[DiscoveredModel] = []
        self._filtered_models: list[DiscoveredModel] = []
        self._model_index = 0
        self._model_widgets: list[Static] = []
        self._search_input: Input | None = None
        self._manual_input: Input | None = None
        self._error_message = ""

    @property
    def preset(self) -> ProviderPreset:
        if self._preset is None:
            app: OnboardingApp = self.app  # type: ignore[assignment]
            self._preset = app.selected_preset
        return self._preset

    def compose(self) -> ComposeResult:
        self._model_widgets = []  # Clear to prevent stale references
        self._search_input = Input(
            id="model-search",
            placeholder="Type to filter models...",
        )
        self._manual_input = Input(
            id="manual-model",
            placeholder="Enter model ID (e.g., gpt-4o)",
            validators=[Length(minimum=1, failure_description="Model ID required")],
        )

        model_widgets = []
        for _ in range(VISIBLE_MODELS):
            widget = NoMarkupStatic("", classes="model-item")
            self._model_widgets.append(widget)
            model_widgets.append(widget)

        with Vertical(id="model-outer"):
            yield NoMarkupStatic("Select a Model", id="model-title")

            with Vertical(id="loading-section"):
                yield NoMarkupStatic("Discovering models...", id="loading-text")

            with Vertical(id="error-section"):
                yield NoMarkupStatic("", id="error-text")
                yield NoMarkupStatic("[R]etry  [M]anual entry", classes="error-option")

            with Vertical(id="model-list-section"):
                yield self._search_input
                yield Vertical(*model_widgets, id="model-list")
                yield NoMarkupStatic("↑↓ Navigate  Enter Select  [M] Manual", id="manual-hint")

            with Vertical(id="manual-section"):
                yield NoMarkupStatic("Enter the model ID:", id="manual-label")
                yield self._manual_input
                yield NoMarkupStatic("", id="manual-feedback")

    def on_mount(self) -> None:
        self._update_visibility()
        self.focus()
        self._discover_models()

    @work(exclusive=True)
    async def _discover_models(self) -> None:
        """Discover models with proper error handling."""
        try:
            self._state = ScreenState.LOADING
            self._update_visibility()

            api_key = os.getenv(self.preset.api_key_env_var) if self.preset.api_key_env_var else None
            models = await fetch_models(self.preset.base_url, api_key)

            if not models:
                self._state = ScreenState.ERROR
                self._error_message = f"Could not discover models from {self.preset.name}"
                self.query_one("#error-text", NoMarkupStatic).update(self._error_message)
                self._update_visibility()
                return

            self._models = sorted(models, key=lambda m: m.id)
            self._filtered_models = list(self._models)
            self._model_index = 0
            self._state = ScreenState.MODEL_LIST
            self._update_visibility()
            self._update_model_display()

            self.query_one("#model-search", Input).focus()

        except Exception as e:
            self._state = ScreenState.ERROR
            self._error_message = f"Error: {e}"
            self.query_one("#error-text", NoMarkupStatic).update(self._error_message)
            self._update_visibility()

    def _update_visibility(self) -> None:
        loading = self.query_one("#loading-section")
        error = self.query_one("#error-section")
        model_list = self.query_one("#model-list-section")
        manual = self.query_one("#manual-section")

        # Use direct display property instead of CSS classes
        loading.display = self._state == ScreenState.LOADING
        error.display = self._state == ScreenState.ERROR
        model_list.display = self._state == ScreenState.MODEL_LIST
        manual.display = self._state == ScreenState.MANUAL_ENTRY

        self.refresh()

    def _update_model_display(self) -> None:
        if not self._filtered_models:
            for widget in self._model_widgets:
                widget.update("")
                widget.remove_class("selected")
            return

        half = VISIBLE_MODELS // 2
        for i, widget in enumerate(self._model_widgets):
            offset = i - half
            index = self._model_index + offset

            widget.remove_class("selected")

            if 0 <= index < len(self._filtered_models):
                model = self._filtered_models[index]
                display_text = model.id
                if model.context_window:
                    ctx_k = model.context_window // 1000
                    display_text = f"{model.id} ({ctx_k}k)"

                if offset == 0:
                    widget.update(f"> {display_text}")
                    widget.add_class("selected")
                else:
                    widget.update(f"  {display_text}")
            else:
                widget.update("")

    def _filter_models(self, query: str) -> None:
        if not query:
            self._filtered_models = list(self._models)
        else:
            matches: list[tuple[float, DiscoveredModel]] = []
            for model in self._models:
                result = fuzzy_match(query, model.id)
                if result.matched:
                    matches.append((result.score, model))
            matches.sort(key=lambda x: -x[0])
            self._filtered_models = [m for _, m in matches]

        self._model_index = 0
        self._update_model_display()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "model-search":
            self._filter_models(event.value)
        elif event.input.id == "manual-model":
            feedback = self.query_one("#manual-feedback", NoMarkupStatic)

            if event.validation_result is None:
                return

            feedback.remove_class("error", "success")

            if event.validation_result.is_valid:
                feedback.update("Press Enter to continue ↵")
                feedback.add_class("success")
            else:
                descriptions = event.validation_result.failure_descriptions
                feedback.update(descriptions[0])
                feedback.add_class("error")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "manual-model":
            if event.validation_result and event.validation_result.is_valid:
                self._save_and_finish(event.value)

    def on_key(self, event: Key) -> None:
        if self._state == ScreenState.ERROR:
            if event.key in {"r", "R"}:
                self._discover_models()
            elif event.key in {"m", "M"}:
                self._state = ScreenState.MANUAL_ENTRY
                self._update_visibility()
                if self._manual_input:
                    self._manual_input.focus()

        elif self._state == ScreenState.MODEL_LIST:
            if event.key in {"m", "M"}:
                self._state = ScreenState.MANUAL_ENTRY
                self._update_visibility()
                if self._manual_input:
                    self._manual_input.focus()

    def action_prev_model(self) -> None:
        if self._state == ScreenState.MODEL_LIST and self._filtered_models:
            self._model_index = max(0, self._model_index - 1)
            self._update_model_display()

    def action_next_model(self) -> None:
        if self._state == ScreenState.MODEL_LIST and self._filtered_models:
            self._model_index = min(
                len(self._filtered_models) - 1, self._model_index + 1
            )
            self._update_model_display()

    def action_select(self) -> None:
        if self._state == ScreenState.MODEL_LIST and self._filtered_models:
            model = self._filtered_models[self._model_index]
            self._save_and_finish(model.id, model.context_window)

    def action_go_back(self) -> None:
        if self._state == ScreenState.MANUAL_ENTRY:
            if self._models:
                self._state = ScreenState.MODEL_LIST
                self._update_visibility()
                if self._search_input:
                    self._search_input.focus()
            else:
                self._state = ScreenState.ERROR
                self._update_visibility()
        else:
            # Pop this screen to return to previous (api_key or provider_selection)
            self.app.pop_screen()

    def _save_and_finish(
        self, model_id: str, context_window: int | None = None
    ) -> None:
        preset = self.preset

        provider_config = ProviderConfig(
            name=preset.id,
            api_base=preset.base_url,
            api_key_env_var=preset.api_key_env_var,
        )

        model_config = ModelConfig(
            name=model_id,
            provider=preset.id,
            alias=model_id,
            context_window=context_window,
        )

        VibeConfig.save_updates(
            {
                "providers": [provider_config.model_dump()],
                "models": [model_config.model_dump()],
                "active_model": model_id,
            }
        )

        self.app.switch_screen("brave_search")

"""Screen for selecting a model from an OpenAI-compatible endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Input

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.setup.onboarding.base import OnboardingScreen
from kin_code.setup.onboarding.services.model_discovery import (
    DiscoveredModel,
    fetch_models,
)

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp

VISIBLE_NEIGHBORS = 4
FADE_CLASSES = ["fade-1", "fade-2", "fade-3", "fade-4"]


def _format_context_display(context_window: int | None) -> str:
    """Format context window for display."""
    if context_window is None:
        return ""
    ctx_k = context_window // 1000
    return f" ({ctx_k}k)"


class OpenAIModelScreen(OnboardingScreen):
    """Screen for selecting a model from an OpenAI-compatible endpoint."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_model", "Select", show=False, priority=True),
        Binding("up", "prev_model", "Previous", show=False),
        Binding("down", "next_model", "Next", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = "theme_selection"

    def __init__(self) -> None:
        super().__init__()
        self._models: list[DiscoveredModel] = []
        self._selected_index = 0
        self._model_widgets: list[NoMarkupStatic] = []
        self._is_loading = True
        self._error_message: str | None = None

    def _compose_model_list(self) -> ComposeResult:
        for _ in range(VISIBLE_NEIGHBORS * 2 + 1):
            widget = NoMarkupStatic("", classes="model-item")
            self._model_widgets.append(widget)
            yield widget

    def compose(self) -> ComposeResult:
        self._manual_input = Input(
            placeholder="Enter model name",
            id="manual-model-input",
        )

        with Center(id="model-outer"):
            with Vertical(id="model-content"):
                yield NoMarkupStatic("Select a model", id="model-title")
                yield NoMarkupStatic("Loading models...", id="loading-indicator")
                yield NoMarkupStatic("", id="error-message")
                with Center(id="model-list-center"):
                    with Horizontal(id="model-row"):
                        yield NoMarkupStatic("Navigate \u2191 \u2193", id="nav-hint")
                        yield Vertical(*self._compose_model_list(), id="model-list")
                        yield NoMarkupStatic("Press Enter \u21b5", id="enter-hint")
                yield NoMarkupStatic("", classes="spacer")
                with Vertical(id="manual-entry-section"):
                    yield NoMarkupStatic(
                        "Or enter manually:", id="manual-entry-label"
                    )
                    yield Center(Horizontal(self._manual_input, id="manual-input-box"))

    async def on_mount(self) -> None:
        app: OnboardingApp = self.app  # type: ignore[assignment]
        base_url: str = getattr(app, "openai_base_url", "")
        api_key: str | None = getattr(app, "openai_api_key", None)

        self._hide_model_list()
        self.focus()

        if not base_url:
            self._show_error("No endpoint URL configured")
            self._focus_manual_input()
            return

        self._models = await fetch_models(base_url, api_key)

        loading = self.query_one("#loading-indicator", NoMarkupStatic)
        loading.display = False
        self._is_loading = False

        if not self._models:
            self._show_error("No models found")
            self._focus_manual_input()
            return

        self._show_model_list()
        self._update_display()

    def _hide_model_list(self) -> None:
        model_list_center = self.query_one("#model-list-center")
        model_list_center.display = False

    def _show_model_list(self) -> None:
        model_list_center = self.query_one("#model-list-center")
        model_list_center.display = True

    def _show_error(self, message: str) -> None:
        self._error_message = message
        error_widget = self.query_one("#error-message", NoMarkupStatic)
        error_widget.update(message)
        error_widget.add_class("error")

        loading = self.query_one("#loading-indicator", NoMarkupStatic)
        loading.display = False
        self._is_loading = False

    def _focus_manual_input(self) -> None:
        self._manual_input.focus()

    def _get_model_at_offset(self, offset: int) -> str:
        if not self._models:
            return ""
        index = (self._selected_index + offset) % len(self._models)
        return self._models[index].id

    def _update_display(self) -> None:
        if not self._models:
            for widget in self._model_widgets:
                widget.update("")
            return

        for i, widget in enumerate(self._model_widgets):
            offset = i - VISIBLE_NEIGHBORS

            widget.remove_class("selected", *FADE_CLASSES)

            if offset == 0:
                model = self._models[self._selected_index]
                ctx_display = _format_context_display(model.context_window)
                widget.update(f" {model.id}{ctx_display} ")
                widget.add_class("selected")
            else:
                index = (self._selected_index + offset) % len(self._models)
                model = self._models[index]
                ctx_display = _format_context_display(model.context_window)
                distance = min(abs(offset) - 1, len(FADE_CLASSES) - 1)
                widget.update(f"{model.id}{ctx_display}")
                widget.add_class(FADE_CLASSES[distance])

    def _navigate(self, direction: int) -> None:
        if not self._models:
            return
        self._selected_index = (self._selected_index + direction) % len(self._models)
        self._update_display()

    def action_next_model(self) -> None:
        self._navigate(1)

    def action_prev_model(self) -> None:
        self._navigate(-1)

    def action_select_model(self) -> None:
        if self._is_loading:
            return

        if manual_value := self._manual_input.value.strip():
            self._save_and_continue(manual_value)
            return

        if self._models:
            selected_model = self._models[self._selected_index].id
            self._save_and_continue(selected_model)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "manual-model-input" and (value := event.value.strip()):
            self._save_and_continue(value)

    def _save_and_continue(self, model_name: str) -> None:
        app: OnboardingApp = self.app  # type: ignore[assignment]
        app.openai_model_name = model_name  # type: ignore[attr-defined]
        # Store context_window if we have a selected model from the list
        if self._models and not self._manual_input.value.strip():
            selected_model = self._models[self._selected_index]
            app.openai_model_context_window = selected_model.context_window  # type: ignore[attr-defined]
        self.action_next()

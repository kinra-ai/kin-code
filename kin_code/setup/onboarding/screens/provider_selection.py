from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Horizontal, Vertical

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.setup.onboarding.base import OnboardingScreen

if TYPE_CHECKING:
    from kin_code.setup.onboarding import OnboardingApp


class ProviderType(StrEnum):
    MISTRAL = auto()
    OPENAI_COMPATIBLE = auto()
    SKIP = auto()


PROVIDER_OPTIONS = [
    (ProviderType.MISTRAL, "Mistral API", "(Recommended)"),
    (ProviderType.OPENAI_COMPATIBLE, "OpenAI-Compatible Endpoint", ""),
    (ProviderType.SKIP, "Skip for now", ""),
]

VISIBLE_NEIGHBORS = 1
FADE_CLASSES = ["fade-1"]


class ProviderSelectionScreen(OnboardingScreen):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "next", "Select", show=False, priority=True),
        Binding("up", "prev_option", "Previous", show=False),
        Binding("down", "next_option", "Next", show=False),
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    NEXT_SCREEN = None

    def __init__(self) -> None:
        super().__init__()
        self._selected_index = 0
        self._option_widgets: list[NoMarkupStatic] = []

    def _compose_option_list(self) -> ComposeResult:
        for provider_type, label, suffix in PROVIDER_OPTIONS:
            display_text = f"{label} {suffix}".strip() if suffix else label
            widget = NoMarkupStatic(display_text, classes="provider-item")
            widget.data_provider_type = provider_type  # type: ignore[attr-defined]
            self._option_widgets.append(widget)
            yield widget

    def compose(self) -> ComposeResult:
        with Center(id="provider-outer"):
            with Vertical(id="provider-content"):
                yield NoMarkupStatic(
                    "Select your LLM provider", id="provider-title"
                )
                with Center():
                    with Horizontal(id="provider-row"):
                        yield NoMarkupStatic("Navigate \u2191 \u2193", id="nav-hint")
                        yield Vertical(
                            *self._compose_option_list(), id="provider-list"
                        )
                        yield NoMarkupStatic("Press Enter \u21b5", id="enter-hint")

    def on_mount(self) -> None:
        self._update_display()
        self.focus()

    def _update_display(self) -> None:
        for i, widget in enumerate(self._option_widgets):
            widget.remove_class("selected", *FADE_CLASSES)

            provider_type, label, suffix = PROVIDER_OPTIONS[i]
            if i == self._selected_index:
                display_text = f" {label} {suffix}".strip() if suffix else f" {label} "
                widget.update(display_text)
                widget.add_class("selected")
            else:
                display_text = f"{label} {suffix}".strip() if suffix else label
                widget.update(display_text)
                distance = abs(i - self._selected_index)
                if distance > 0:
                    fade_index = min(distance - 1, len(FADE_CLASSES) - 1)
                    widget.add_class(FADE_CLASSES[fade_index])

    def _navigate(self, direction: int) -> None:
        self._selected_index = (self._selected_index + direction) % len(
            PROVIDER_OPTIONS
        )
        self._update_display()

    def action_next_option(self) -> None:
        self._navigate(1)

    def action_prev_option(self) -> None:
        self._navigate(-1)

    def action_next(self) -> None:
        selected_provider = PROVIDER_OPTIONS[self._selected_index][0]
        app: OnboardingApp = self.app  # type: ignore[assignment]
        app.selected_provider = selected_provider  # type: ignore[attr-defined]

        match selected_provider:
            case ProviderType.MISTRAL:
                self.app.switch_screen("theme_selection")
            case ProviderType.OPENAI_COMPATIBLE:
                self.app.switch_screen("openai_provider")
            case ProviderType.SKIP:
                app.skip_api_key = True  # type: ignore[attr-defined]
                self.app.switch_screen("theme_selection")

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
import random
from time import time
from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.cli.textual_ui.widgets.spinner import SpinnerMixin, SpinnerType

if TYPE_CHECKING:
    from kin_code.cli.textual_ui.widgets.loading import LoadingWidget


@contextmanager
def paused_timer(widget: LoadingWidget | None) -> Iterator[None]:
    """Context manager to pause loading widget animation during modal dialogs."""
    if widget is None:
        yield
        return
    widget.stop_spinner_timer()
    try:
        yield
    finally:
        widget.start_spinner_timer()


class LoadingWidget(SpinnerMixin, Static):
    # Minnesota flag colors (lakes + night sky gradient, matching welcome banner)
    TARGET_COLORS = ("#73c6e5", "#52b5dc", "#3a9fc8", "#2b82ae", "#1a6490", "#002c5a")
    SPINNER_TYPE = SpinnerType.BRAILLE

    EASTER_EGGS: ClassVar[list[str]] = [
        "Ope, lemme sneak past",
        "You betcha-ing",
        "Uff da-ing",
        "Being Minnesota Nice",
        "Don't cha know-ing",
        "Making hotdish",
        "Grilling Jucy Lucys",
        "Harvesting wild rice",
        "Eating tater tots",
        "Rolling lefse",
        "Counting lakes",
        "Listening for loons",
        "Finding lake 10,001",
        "Going to the Fair",
        "Doorway chatting",
        "Welp-ing out",
        "Logging with Paul",
        "Petting Babe the Ox",
        "Channeling Prince",
    ]

    EASTER_EGGS_WINTER: ClassVar[list[str]] = [
        "Ice fishing",
        "Surviving winter",
        "Shoveling snow",
        "Polar vortexing",
        "Braving the cold",
        "Playing hockey",
    ]

    EASTER_EGGS_HALLOWEEN: ClassVar[list[str]] = [
        "Carving pumpkins",
        "Haunting the lakes",
        "Summoning loons",
    ]

    EASTER_EGGS_DECEMBER: ClassVar[list[str]] = [
        "Drinking hot cocoa",
        "Ice skating",
        "Building snow forts",
        "Checking the list twice",
        "Wrapping presents",
        "Decorating the tree",
        "Loading the sleigh",
        "Feeding the reindeer",
        "Sliding down chimneys",
    ]

    def __init__(self, status: str | None = None) -> None:
        super().__init__(classes="loading-widget")
        self.init_spinner()
        self.status = status or self._get_default_status()
        self.current_color_index = 0
        self.transition_progress = 0
        self._status_widget: Static | None = None
        self.hint_widget: Static | None = None
        self.start_time: float | None = None
        self._last_elapsed: int = -1

    def _get_easter_egg(self) -> str | None:
        EASTER_EGG_PROBABILITY = 0.10
        if random.random() < EASTER_EGG_PROBABILITY:
            available_eggs = list(self.EASTER_EGGS)

            JANUARY = 1
            FEBRUARY = 2
            OCTOBER = 10
            HALLOWEEN_DAY = 31
            DECEMBER = 12
            now = datetime.now()
            if now.month in {JANUARY, FEBRUARY}:
                available_eggs.extend(self.EASTER_EGGS_WINTER)
            if now.month == OCTOBER and now.day == HALLOWEEN_DAY:
                available_eggs.extend(self.EASTER_EGGS_HALLOWEEN)
            if now.month == DECEMBER:
                available_eggs.extend(self.EASTER_EGGS_DECEMBER)

            return random.choice(available_eggs)
        return None

    def _get_default_status(self) -> str:
        return self._get_easter_egg() or "Generating"

    def _apply_easter_egg(self, status: str) -> str:
        return self._get_easter_egg() or status

    def set_status(self, status: str) -> None:
        self.status = self._apply_easter_egg(status)
        self._update_animation()
        self.refresh()  # Force repaint on next render cycle

    def compose(self) -> ComposeResult:
        with Horizontal(classes="loading-container"):
            self._indicator_widget = Static(
                self._spinner.current_frame(), classes="loading-indicator"
            )
            yield self._indicator_widget

            self._status_widget = Static("", classes="loading-status")
            yield self._status_widget

            self.hint_widget = NoMarkupStatic(
                "(0s esc to interrupt)", classes="loading-hint"
            )
            yield self.hint_widget

    def on_mount(self) -> None:
        self.start_time = time()
        self._update_animation()
        self.start_spinner_timer()

    def on_resize(self) -> None:
        self.refresh_spinner()

    def _update_spinner_frame(self) -> None:
        if not self._is_spinning:
            return
        self._update_animation()

    def _get_color_for_position(self, position: int) -> str:
        current_color = self.TARGET_COLORS[self.current_color_index]
        next_color = self.TARGET_COLORS[
            (self.current_color_index + 1) % len(self.TARGET_COLORS)
        ]
        if position < self.transition_progress:
            return next_color
        return current_color

    def _build_status_text(self) -> str:
        parts = []
        for i, char in enumerate(self.status):
            color = self._get_color_for_position(1 + i)
            parts.append(f"[{color}]{char}[/]")
        ellipsis_start = 1 + len(self.status)
        color_ellipsis = self._get_color_for_position(ellipsis_start)
        parts.append(f"[{color_ellipsis}]… [/]")
        return "".join(parts)

    def _update_animation(self) -> None:
        total_elements = 1 + len(self.status) + 1

        if self._indicator_widget:
            spinner_char = self._spinner.next_frame()
            color = self._get_color_for_position(0)
            self._indicator_widget.update(f"[{color}]{spinner_char}[/]")

        if self._status_widget:
            self._status_widget.update(self._build_status_text())

        self.transition_progress += 1
        if self.transition_progress > total_elements:
            self.current_color_index = (self.current_color_index + 1) % len(
                self.TARGET_COLORS
            )
            self.transition_progress = 0

        if self.hint_widget and self.start_time is not None:
            elapsed = int(time() - self.start_time)
            if elapsed != self._last_elapsed:
                self._last_elapsed = elapsed
                self.hint_widget.update(f"({elapsed}s esc to interrupt)")

"""Widget displaying the current active model in the footer."""

from __future__ import annotations

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic


class ModelDisplay(NoMarkupStatic):
    def __init__(self, model_alias: str) -> None:
        super().__init__()
        self.can_focus = False
        self._model_alias = model_alias
        self._update_display()

    def _update_display(self) -> None:
        self.update(self._model_alias)

    def set_model(self, model_alias: str) -> None:
        self._model_alias = model_alias
        self._update_display()

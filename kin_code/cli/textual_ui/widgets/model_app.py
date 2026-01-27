"""Model management widget for selecting, discovering, and adding models."""

from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, ClassVar

from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Input, Static

from kin_code.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
from kin_code.core.autocompletion.fuzzy import fuzzy_match
from kin_code.setup.onboarding.services.model_discovery import (
    DiscoveredModel,
    fetch_models,
)

if TYPE_CHECKING:
    from kin_code.core.config import KinConfig, ModelConfig, ProviderConfig


class ViewState(StrEnum):
    LIST = auto()
    DISCOVER = auto()
    ADD = auto()


class ModelApp(Container):
    can_focus = True
    can_focus_children = True

    # Focus field indices for add form
    _FOCUS_PROVIDER = 0
    _FOCUS_MODEL_ID = 1
    _FOCUS_ALIAS = 2

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("d", "discover", "Discover", show=False),
        Binding("a", "add", "Add", show=False),
        Binding("left", "prev_provider", "Prev Provider", show=False),
        Binding("right", "next_provider", "Next Provider", show=False),
        Binding("escape", "back", "Back", show=False),
    ]

    class ModelSelected(Message):
        def __init__(self, alias: str) -> None:
            super().__init__()
            self.alias = alias

    class ModelAdded(Message):
        def __init__(
            self, provider: str, model_id: str, alias: str, context_window: int | None
        ) -> None:
            super().__init__()
            self.provider = provider
            self.model_id = model_id
            self.alias = alias
            self.context_window = context_window

    class ModelUpdated(Message):
        """Message sent when an existing model's metadata is refreshed from discovery."""

        def __init__(self, alias: str, context_window: int | None) -> None:
            super().__init__()
            self.alias = alias
            self.context_window = context_window

    class ModelClosed(Message):
        def __init__(self, changed: bool = False) -> None:
            super().__init__()
            self.changed = changed

    def __init__(self, config: KinConfig) -> None:
        super().__init__(id="model-app")
        self.config = config
        self._view_state = ViewState.LIST
        self._selected_index = 0
        self._model_list: list[tuple[str, ModelConfig]] = []
        self._provider_groups: dict[str, list[ModelConfig]] = {}
        self._flat_list: list[tuple[str, ModelConfig | None]] = []

        # Discovery state
        self._discovery_provider_index = 0
        self._discovered_models: list[DiscoveredModel] = []
        self._filtered_models: list[DiscoveredModel] = []
        self._discovery_error: str | None = None
        self._discovery_loading = False
        self._search_query = ""

        # Add form state
        self._add_provider_index = 0
        self._add_model_id = ""
        self._add_alias = ""
        self._add_focus_field = self._FOCUS_PROVIDER

        # Widget references
        self._title_widget: Static | None = None
        self._content_widgets: list[Static] = []
        self._help_widget: Static | None = None
        self._search_input: Input | None = None

        self._build_model_list()

    def _build_model_list(self) -> None:
        """Build the model list grouped by provider."""
        self._provider_groups.clear()
        for model in self.config.models:
            provider = model.provider
            if provider not in self._provider_groups:
                self._provider_groups[provider] = []
            self._provider_groups[provider].append(model)

        self._flat_list = []
        for provider in sorted(self._provider_groups.keys()):
            self._flat_list.append((provider, None))
            for model in self._provider_groups[provider]:
                self._flat_list.append((provider, model))

    def _get_providers(self) -> list[ProviderConfig]:
        """Get list of configured providers."""
        return list(self.config.providers)

    def compose(self) -> ComposeResult:
        with Vertical(id="model-content"):
            self._title_widget = NoMarkupStatic(
                "Model Selection", classes="model-title"
            )
            yield self._title_widget

            yield NoMarkupStatic("", classes="model-separator")

            with VerticalScroll(id="model-list-scroll"):
                for _ in range(20):
                    widget = NoMarkupStatic("", classes="model-option")
                    self._content_widgets.append(widget)
                    yield widget

            self._search_input = Input(
                placeholder="Type to search...",
                id="model-search",
                classes="model-search",
            )
            self._search_input.display = False
            yield self._search_input

            yield NoMarkupStatic("")

            self._help_widget = NoMarkupStatic(
                self._get_help_text(), classes="model-help"
            )
            yield self._help_widget

    def on_mount(self) -> None:
        self._update_display()
        self.focus()

    def _get_help_text(self) -> str:
        match self._view_state:
            case ViewState.LIST:
                return "up/dn navigate  Enter select  D discover  A add  Esc close"
            case ViewState.DISCOVER:
                return "up/dn navigate  Enter add/refresh  <-/-> provider  type search  Esc back"
            case ViewState.ADD:
                return "Tab next field  Enter save  Esc cancel"

    def _update_display(self) -> None:
        if self._title_widget:
            self._title_widget.update(self._get_title())
        if self._help_widget:
            self._help_widget.update(self._get_help_text())

        match self._view_state:
            case ViewState.LIST:
                self._update_list_display()
            case ViewState.DISCOVER:
                self._update_discover_display()
            case ViewState.ADD:
                self._update_add_display()

    def _get_title(self) -> str:
        match self._view_state:
            case ViewState.LIST:
                active = self.config.active_model
                try:
                    model = self.config.get_active_model()
                    ctx = (
                        f"{model.context_window // 1000}k"
                        if model.context_window
                        else "?"
                    )
                    return (
                        f"Model Selection - Active: {active} ({model.provider}) {ctx}"
                    )
                except ValueError:
                    return f"Model Selection - Active: {active}"
            case ViewState.DISCOVER:
                providers = self._get_providers()
                if providers:
                    provider = providers[self._discovery_provider_index]
                    return f"Discover Models from: {provider.name}  <-/->"
                return "Discover Models"
            case ViewState.ADD:
                return "Add Model Manually"

    def _update_list_display(self) -> None:
        if self._search_input:
            self._search_input.display = False

        lines: list[str] = []
        for i, (provider, model) in enumerate(self._flat_list):
            if model is None:
                lines.append(f"{provider}:")
            else:
                is_selected = i == self._selected_index
                is_active = model.alias == self.config.active_model
                cursor = "> " if is_selected else "  "
                active_marker = " *" if is_active else ""
                ctx = (
                    f"{model.context_window // 1000}k" if model.context_window else "?"
                )
                price = ""
                input_p = model.input_price or 0
                output_p = model.output_price or 0
                if input_p > 0 or output_p > 0:
                    price = f"  ${input_p:.2f}/${output_p:.2f}"
                lines.append(
                    f"  {cursor}{model.alias:<20} {ctx:<6}{price}{active_marker}"
                )

        for i, widget in enumerate(self._content_widgets):
            if i < len(lines):
                widget.update(lines[i])
                widget.display = True
            else:
                widget.update("")
                widget.display = False

    def _update_discover_display(self) -> None:
        if self._search_input:
            self._search_input.display = True
            self._search_input.value = self._search_query

        lines: list[str] = []

        if self._discovery_loading:
            lines.append("Loading models...")
        elif self._discovery_error:
            lines.append(f"Error: {self._discovery_error}")
        elif not self._filtered_models:
            if self._search_query:
                lines.append(f"No models match '{self._search_query}'")
            else:
                lines.append("No models found")
        else:
            total = len(self._discovered_models)
            filtered = len(self._filtered_models)
            if self._search_query:
                lines.append(f"Showing {filtered} of {total} models  (* = configured)")
            else:
                lines.append(f"{total} models available  (* = configured)")
            lines.append("")

            display_models = self._filtered_models[:15]
            existing_aliases = {m.alias for m in self.config.models}
            for i, model in enumerate(display_models):
                is_selected = i == self._selected_index
                cursor = "> " if is_selected else "  "
                ctx = (
                    f"{model.context_window // 1000}k" if model.context_window else "?"
                )
                owned = f" ({model.owned_by})" if model.owned_by else ""
                # Mark models that are already configured
                alias = model.id.split("/")[-1] if "/" in model.id else model.id
                configured = " *" if alias in existing_aliases else ""
                lines.append(f"{cursor}{model.id:<40} {ctx}{owned}{configured}")

        for i, widget in enumerate(self._content_widgets):
            if i < len(lines):
                widget.update(lines[i])
                widget.display = True
            else:
                widget.update("")
                widget.display = False

    def _update_add_display(self) -> None:
        if self._search_input:
            self._search_input.display = False

        providers = self._get_providers()
        provider_name = (
            providers[self._add_provider_index].name if providers else "none"
        )

        lines: list[str] = []
        p_cursor = "> " if self._add_focus_field == self._FOCUS_PROVIDER else "  "
        m_cursor = "> " if self._add_focus_field == self._FOCUS_MODEL_ID else "  "
        a_cursor = "> " if self._add_focus_field == self._FOCUS_ALIAS else "  "

        lines.append(f"{p_cursor}Provider: [{provider_name}]  <-/->")
        lines.append(f"{m_cursor}Model ID: [{self._add_model_id or '_' * 30}]")
        lines.append(f"{a_cursor}Alias:    [{self._add_alias or '_' * 30}]")

        for i, widget in enumerate(self._content_widgets):
            if i < len(lines):
                widget.update(lines[i])
                widget.display = True
            else:
                widget.update("")
                widget.display = False

    def _filter_models(self, query: str) -> list[DiscoveredModel]:
        """Filter discovered models using fuzzy matching."""
        if not query:
            return self._discovered_models

        query_lower = query.lower()
        scored: list[tuple[DiscoveredModel, float]] = []

        for model in self._discovered_models:
            result = fuzzy_match(query_lower, model.id.lower())
            if result.matched:
                scored.append((model, result.score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored[:50]]

    def action_move_up(self) -> None:
        match self._view_state:
            case ViewState.LIST:
                self._move_selection(-1, self._flat_list)
            case ViewState.DISCOVER:
                if self._selected_index > 0:
                    self._selected_index -= 1
            case ViewState.ADD:
                self._add_focus_field = (self._add_focus_field - 1) % 3
        self._update_display()

    def action_move_down(self) -> None:
        match self._view_state:
            case ViewState.LIST:
                self._move_selection(1, self._flat_list)
            case ViewState.DISCOVER:
                max_index = min(len(self._filtered_models), 15) - 1
                if self._selected_index < max_index:
                    self._selected_index += 1
            case ViewState.ADD:
                self._add_focus_field = (self._add_focus_field + 1) % 3
        self._update_display()

    def _move_selection(
        self, direction: int, items: list[tuple[str, ModelConfig | None]]
    ) -> None:
        """Move selection, skipping header rows."""
        new_index = self._selected_index
        while True:
            new_index = (new_index + direction) % len(items)
            if items[new_index][1] is not None:
                break
            if new_index == self._selected_index:
                break
        self._selected_index = new_index

    def action_select(self) -> None:
        match self._view_state:
            case ViewState.LIST:
                if self._flat_list and self._selected_index < len(self._flat_list):
                    _, model = self._flat_list[self._selected_index]
                    if model is not None:
                        self.post_message(self.ModelSelected(alias=model.alias))
            case ViewState.DISCOVER:
                if self._filtered_models and self._selected_index < len(
                    self._filtered_models
                ):
                    model = self._filtered_models[self._selected_index]
                    providers = self._get_providers()
                    provider = providers[self._discovery_provider_index]
                    alias = model.id.split("/")[-1] if "/" in model.id else model.id

                    # Check if model with this alias already exists
                    existing_aliases = {m.alias for m in self.config.models}
                    if alias in existing_aliases:
                        # Update existing model's metadata
                        self.post_message(
                            self.ModelUpdated(
                                alias=alias, context_window=model.context_window
                            )
                        )
                    else:
                        self.post_message(
                            self.ModelAdded(
                                provider=provider.name,
                                model_id=model.id,
                                alias=alias,
                                context_window=model.context_window,
                            )
                        )
            case ViewState.ADD:
                self._save_manual_model()

    def _save_manual_model(self) -> None:
        """Save manually entered model."""
        if not self._add_model_id:
            return

        providers = self._get_providers()
        if not providers:
            return

        provider = providers[self._add_provider_index]
        alias = self._add_alias or self._add_model_id

        self.post_message(
            self.ModelAdded(
                provider=provider.name,
                model_id=self._add_model_id,
                alias=alias,
                context_window=None,
            )
        )

    def action_discover(self) -> None:
        if self._view_state != ViewState.LIST:
            return
        self._view_state = ViewState.DISCOVER
        self._selected_index = 0
        self._search_query = ""
        self._discovered_models = []
        self._filtered_models = []
        self._discovery_error = None
        self._update_display()
        self._fetch_models()

    @work(exclusive=True)
    async def _fetch_models(self) -> None:
        """Fetch models from the selected provider."""
        providers = self._get_providers()
        if not providers:
            self._discovery_error = "No providers configured"
            self._update_display()
            return

        provider = providers[self._discovery_provider_index]
        self._discovery_loading = True
        self._update_display()

        try:
            import os

            api_key = (
                os.getenv(provider.api_key_env_var)
                if provider.api_key_env_var
                else None
            )
            models = await fetch_models(provider.api_base, api_key)

            if models:
                self._discovered_models = sorted(models, key=lambda m: m.id)
                self._filtered_models = self._discovered_models
                self._discovery_error = None
            else:
                self._discovery_error = "No models returned from endpoint"
        except Exception as e:
            self._discovery_error = str(e)

        self._discovery_loading = False
        self._update_display()

    def action_add(self) -> None:
        if self._view_state != ViewState.LIST:
            return
        self._view_state = ViewState.ADD
        self._add_focus_field = 1  # Start on model_id field
        self._add_model_id = ""
        self._add_alias = ""
        self._update_display()

    def action_prev_provider(self) -> None:
        providers = self._get_providers()
        if not providers:
            return

        match self._view_state:
            case ViewState.DISCOVER:
                self._discovery_provider_index = (
                    self._discovery_provider_index - 1
                ) % len(providers)
                self._selected_index = 0
                self._search_query = ""
                self._update_display()
                self._fetch_models()
            case ViewState.ADD:
                if self._add_focus_field == 0:
                    self._add_provider_index = (self._add_provider_index - 1) % len(
                        providers
                    )
                    self._update_display()

    def action_next_provider(self) -> None:
        providers = self._get_providers()
        if not providers:
            return

        match self._view_state:
            case ViewState.DISCOVER:
                self._discovery_provider_index = (
                    self._discovery_provider_index + 1
                ) % len(providers)
                self._selected_index = 0
                self._search_query = ""
                self._update_display()
                self._fetch_models()
            case ViewState.ADD:
                if self._add_focus_field == 0:
                    self._add_provider_index = (self._add_provider_index + 1) % len(
                        providers
                    )
                    self._update_display()

    def action_back(self) -> None:
        match self._view_state:
            case ViewState.LIST:
                self.post_message(self.ModelClosed(changed=False))
            case ViewState.DISCOVER | ViewState.ADD:
                self._view_state = ViewState.LIST
                self._selected_index = 0
                self._build_model_list()
                self._skip_to_first_model()
                self._update_display()

    def _skip_to_first_model(self) -> None:
        """Set selection to first actual model (skip header)."""
        for i, (_, model) in enumerate(self._flat_list):
            if model is not None:
                self._selected_index = i
                return

    def action_close(self) -> None:
        self.post_message(self.ModelClosed(changed=False))

    def on_input_changed(self, event: Input.Changed) -> None:
        if self._view_state == ViewState.DISCOVER and event.input.id == "model-search":
            self._search_query = event.value
            self._filtered_models = self._filter_models(self._search_query)
            self._selected_index = 0
            self._update_display()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self._view_state == ViewState.DISCOVER and event.input.id == "model-search":
            self.action_select()

    def on_key(self, event: events.Key) -> None:
        if self._view_state == ViewState.ADD:
            if event.key == "tab":
                self._add_focus_field = (self._add_focus_field + 1) % 3
                self._update_display()
                event.prevent_default()
            elif event.character and self._add_focus_field > self._FOCUS_PROVIDER:
                if self._add_focus_field == self._FOCUS_MODEL_ID:
                    if event.key == "backspace":
                        self._add_model_id = self._add_model_id[:-1]
                    elif len(event.character) == 1 and event.character.isprintable():
                        self._add_model_id += event.character
                elif self._add_focus_field == self._FOCUS_ALIAS:
                    if event.key == "backspace":
                        self._add_alias = self._add_alias[:-1]
                    elif len(event.character) == 1 and event.character.isprintable():
                        self._add_alias += event.character
                self._update_display()
                event.prevent_default()

        if self._view_state == ViewState.DISCOVER:
            if event.character and event.character.isprintable() and self._search_input:
                self._search_input.focus()

    def on_blur(self, _event: events.Blur) -> None:
        if self._view_state != ViewState.DISCOVER:
            self.call_after_refresh(self.focus)

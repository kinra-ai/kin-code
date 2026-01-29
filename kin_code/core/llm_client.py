from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from kin_code.core.config import VibeConfig
from kin_code.core.llm.format import APIToolFormatHandler
from kin_code.core.llm.pricing import resolve_context_window, resolve_model_pricing
from kin_code.core.llm.types import BackendLike
from kin_code.core.types import AgentStats, LLMChunk, LLMMessage, LLMUsage, Role
from kin_code.core.utils import get_user_agent

if TYPE_CHECKING:
    from kin_code.core.tools.manager import ToolManager


class LLMClientError(Exception):
    """Raised when LLM communication fails."""


class LLMResponseError(LLMClientError):
    """Raised when LLM response is malformed or missing expected data."""


class LLMClient:
    """Handles all LLM communication, streaming, and stats tracking."""

    def __init__(
        self,
        config: VibeConfig,
        backend: BackendLike | None = None,
        enable_streaming: bool = False,
        session_id: str = "",
    ) -> None:
        self._config = config
        self._backend_override = backend
        self._backend: BackendLike | None = None
        self.enable_streaming = enable_streaming
        self.session_id = session_id
        self.format_handler = APIToolFormatHandler()
        self.stats = AgentStats()

        # Initialize stats with pricing
        input_price, output_price = resolve_model_pricing(config)
        self.stats.input_price_per_million = input_price
        self.stats.output_price_per_million = output_price
        self.stats.max_context_window = resolve_context_window(config)

    @property
    def backend(self) -> BackendLike:
        """Lazily create backend on first access."""
        if self._backend is None:
            self._backend = self._backend_override or self._select_backend()
        return self._backend

    def reset_backend(self) -> None:
        """Reset backend to force re-selection (e.g., after model change)."""
        self._backend = None

    def _select_backend(self) -> BackendLike:
        from kin_code.core.llm.backend.factory import BACKEND_FACTORY

        active_model = self._config.get_active_model()
        provider = self._config.get_provider_for_model(active_model)
        timeout = self._config.api_timeout
        return BACKEND_FACTORY[provider.backend](provider=provider, timeout=timeout)

    def update_config(self, config: VibeConfig) -> None:
        """Update configuration and reinitialize pricing."""
        self._config = config
        input_price, output_price = resolve_model_pricing(config)
        self.stats.update_pricing(input_price, output_price)
        self.stats.max_context_window = resolve_context_window(config)

    async def chat(
        self,
        messages: list[LLMMessage],
        tool_manager: ToolManager,
        max_tokens: int | None = None,
    ) -> LLMChunk:
        """Non-streaming chat completion."""
        active_model = self._config.get_active_model()
        provider = self._config.get_provider_for_model(active_model)

        available_tools = self.format_handler.get_available_tools(tool_manager)
        tool_choice = self.format_handler.get_tool_choice()

        try:
            start_time = time.perf_counter()
            async with self.backend as backend:
                result = await backend.complete(
                    model=active_model,
                    messages=messages,
                    temperature=active_model.temperature,
                    tools=available_tools,
                    tool_choice=tool_choice,
                    extra_headers={
                        "user-agent": get_user_agent(),
                        "x-affinity": self.session_id,
                    },
                    max_tokens=max_tokens,
                )
            end_time = time.perf_counter()

            if result.usage is None:
                raise LLMResponseError(
                    "Usage data missing in non-streaming completion response"
                )
            self._update_stats(usage=result.usage, time_seconds=end_time - start_time)

            processed_message = self.format_handler.process_api_response_message(
                result.message
            )
            return LLMChunk(message=processed_message, usage=result.usage)

        except Exception as e:
            raise RuntimeError(
                f"API error from {provider.name} (model: {active_model.name}): {e}"
            ) from e

    async def chat_streaming(
        self,
        messages: list[LLMMessage],
        tool_manager: ToolManager,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[LLMChunk]:
        """Streaming chat completion."""
        active_model = self._config.get_active_model()
        provider = self._config.get_provider_for_model(active_model)

        available_tools = self.format_handler.get_available_tools(tool_manager)
        tool_choice = self.format_handler.get_tool_choice()
        try:
            start_time = time.perf_counter()
            usage = LLMUsage()
            chunk_agg = LLMChunk(message=LLMMessage(role=Role.assistant))
            async with self.backend as backend:
                async for chunk in backend.complete_streaming(
                    model=active_model,
                    messages=messages,
                    temperature=active_model.temperature,
                    tools=available_tools,
                    tool_choice=tool_choice,
                    extra_headers={
                        "user-agent": get_user_agent(),
                        "x-affinity": self.session_id,
                    },
                    max_tokens=max_tokens,
                ):
                    processed_message = (
                        self.format_handler.process_api_response_message(chunk.message)
                    )
                    processed_chunk = LLMChunk(
                        message=processed_message, usage=chunk.usage
                    )
                    chunk_agg += processed_chunk
                    usage += chunk.usage or LLMUsage()
                    yield processed_chunk
            end_time = time.perf_counter()

            if chunk_agg.usage is None:
                raise LLMResponseError(
                    "Usage data missing in final chunk of streamed completion"
                )
            self._update_stats(usage=usage, time_seconds=end_time - start_time)

        except Exception as e:
            raise RuntimeError(
                f"API error from {provider.name} (model: {active_model.name}): {e}"
            ) from e

    async def count_tokens(
        self,
        messages: list[LLMMessage],
        tool_manager: ToolManager,
    ) -> int:
        """Count tokens in messages."""
        active_model = self._config.get_active_model()

        async with self.backend as backend:
            return await backend.count_tokens(
                model=active_model,
                messages=messages,
                tools=self.format_handler.get_available_tools(tool_manager),
                extra_headers={"user-agent": get_user_agent()},
            )

    def _update_stats(self, usage: LLMUsage, time_seconds: float) -> None:
        """Update tracking stats after LLM call."""
        self.stats.last_turn_duration = time_seconds
        self.stats.last_turn_prompt_tokens = usage.prompt_tokens
        self.stats.last_turn_completion_tokens = usage.completion_tokens
        self.stats.session_prompt_tokens += usage.prompt_tokens
        self.stats.session_completion_tokens += usage.completion_tokens
        self.stats.context_tokens = usage.prompt_tokens + usage.completion_tokens
        if time_seconds > 0 and usage.completion_tokens > 0:
            self.stats.tokens_per_second = usage.completion_tokens / time_seconds

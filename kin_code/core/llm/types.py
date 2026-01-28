from __future__ import annotations

from collections.abc import AsyncGenerator
import types
from typing import TYPE_CHECKING, Protocol

from kin_code.core.types import AvailableTool, LLMChunk, LLMMessage, StrToolChoice

if TYPE_CHECKING:
    from kin_code.core.config import ModelConfig


class BackendLike(Protocol):
    """Port protocol for dependency-injectable LLM backends.

    Any backend used by AgentLoop should implement this async context manager
    interface with `complete`, `complete_streaming` and `count_tokens` methods.

    The backend manages HTTP connections and provides two completion modes:
    - Non-streaming: Returns complete response after full generation
    - Streaming: Yields incremental chunks as they're generated

    Backends are async context managers to support connection pooling and
    cleanup of HTTP sessions.

    Example:
        Implementing a custom backend::

            from collections.abc import AsyncGenerator
            import types
            from kin_code.core.llm.types import BackendLike
            from kin_code.core.types import (
                AvailableTool, LLMChunk, LLMMessage, StrToolChoice
            )
            from kin_code.core.config import ModelConfig

            class CustomBackend:
                '''Example backend implementation.'''

                def __init__(self, api_key: str, base_url: str) -> None:
                    self.api_key = api_key
                    self.base_url = base_url
                    self._client: httpx.AsyncClient | None = None

                async def __aenter__(self) -> "CustomBackend":
                    self._client = httpx.AsyncClient(
                        base_url=self.base_url,
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    return self

                async def __aexit__(
                    self,
                    exc_type: type[BaseException] | None,
                    exc_val: BaseException | None,
                    exc_tb: types.TracebackType | None,
                ) -> None:
                    if self._client:
                        await self._client.aclose()

                async def complete(
                    self,
                    *,
                    model: ModelConfig,
                    messages: list[LLMMessage],
                    temperature: float,
                    tools: list[AvailableTool] | None,
                    max_tokens: int | None,
                    tool_choice: StrToolChoice | AvailableTool | None,
                    extra_headers: dict[str, str] | None,
                ) -> LLMChunk:
                    # Make API call and return complete response
                    response = await self._client.post(
                        "/chat/completions",
                        json=self._build_request(model, messages, ...)
                    )
                    return self._parse_response(response.json())

                async def complete_streaming(
                    self,
                    *,
                    model: ModelConfig,
                    messages: list[LLMMessage],
                    temperature: float,
                    tools: list[AvailableTool] | None,
                    max_tokens: int | None,
                    tool_choice: StrToolChoice | AvailableTool | None,
                    extra_headers: dict[str, str] | None,
                ) -> AsyncGenerator[LLMChunk, None]:
                    # Stream response chunks
                    async with self._client.stream(
                        "POST", "/chat/completions",
                        json={**self._build_request(...), "stream": True}
                    ) as response:
                        async for line in response.aiter_lines():
                            if chunk := self._parse_sse(line):
                                yield chunk

                async def count_tokens(
                    self,
                    *,
                    model: ModelConfig,
                    messages: list[LLMMessage],
                    temperature: float = 0.0,
                    tools: list[AvailableTool] | None,
                    tool_choice: StrToolChoice | AvailableTool | None = None,
                    extra_headers: dict[str, str] | None,
                ) -> int:
                    # Count tokens without generating
                    # Some APIs support this, otherwise estimate
                    return self._estimate_tokens(messages, tools)

        Using a backend::

            async with CustomBackend(api_key, base_url) as backend:
                # Non-streaming (waits for complete response)
                response = await backend.complete(
                    model=model_config,
                    messages=messages,
                    temperature=0.2,
                    tools=available_tools,
                    max_tokens=4096,
                    tool_choice="auto",
                    extra_headers=None,
                )
                print(response.message.content)

                # Streaming (yields chunks as generated)
                async for chunk in backend.complete_streaming(
                    model=model_config,
                    messages=messages,
                    temperature=0.2,
                    tools=available_tools,
                    max_tokens=4096,
                    tool_choice="auto",
                    extra_headers=None,
                ):
                    if chunk.message:
                        print(chunk.message.content, end="", flush=True)

        Streaming vs non-streaming:
            - **Non-streaming** (``complete``): Best for programmatic use where
              you need the full response before processing. Simpler error handling.
            - **Streaming** (``complete_streaming``): Best for interactive use
              where you want to display text as it's generated. Provides better
              perceived latency for long responses.
    """

    async def __aenter__(self) -> BackendLike: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None: ...

    async def complete(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float,
        tools: list[AvailableTool] | None,
        max_tokens: int | None,
        tool_choice: StrToolChoice | AvailableTool | None,
        extra_headers: dict[str, str] | None,
    ) -> LLMChunk:
        """Complete a chat conversation using the specified model and provider.

        Args:
            model: Model configuration
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            tools: Optional list of available tools
            max_tokens: Maximum tokens to generate
            tool_choice: How to choose tools (auto, none, or specific tool)
            extra_headers: Additional HTTP headers to include

        Returns:
            LLMChunk containing the response message and usage information

        Raises:
            BackendError: If the API request fails
        """
        ...

    # Note: actual implementation should be an async function,
    # but we can't make this one async, as it would lead to wrong type inference
    # https://stackoverflow.com/a/68911014
    def complete_streaming(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float,
        tools: list[AvailableTool] | None,
        max_tokens: int | None,
        tool_choice: StrToolChoice | AvailableTool | None,
        extra_headers: dict[str, str] | None,
    ) -> AsyncGenerator[LLMChunk, None]:
        """Equivalent of the complete method, but yields LLMEvent objects
        instead of a single LLMEvent.

        Args:
            model: Model configuration
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            tools: Optional list of available tools
            max_tokens: Maximum tokens to generate
            tool_choice: How to choose tools (auto, none, or specific tool)
            extra_headers: Additional HTTP headers to include

        Returns:
            AsyncGenerator[LLMEvent, None] yielding LLMEvent objects

        Raises:
            BackendError: If the API request fails
        """
        ...

    async def count_tokens(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.0,
        tools: list[AvailableTool] | None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None,
    ) -> int:
        """Count the number of tokens in the prompt without generating a real response.

        This is useful for:
        - Determining system prompt token count
        - Checking context size after compaction
        - Pre-flight token validation

        Args:
            model: Model configuration
            messages: List of messages to count tokens for
            temperature: Sampling temperature
            tools: Optional list of available tools
            tool_choice: How to choose tools
            extra_headers: Additional HTTP headers to include

        Returns:
            The number of prompt tokens
        """
        ...

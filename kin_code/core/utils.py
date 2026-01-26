"""Utility functions for async operations and cross-platform support.

This module provides common utility functions including async retry decorators,
event loop management, tagged text parsing, user cancellation handling, platform
detection, and dangerous directory checks. These utilities support the core agent
infrastructure and ensure robust operation across different environments.

Key Components:
    TaggedText: Wrapper for text with semantic tags (cancellation, errors, warnings).
    CancellationReason: Enum of possible cancellation reasons for tool execution.
    ConversationLimitException: Raised when conversation limits are exceeded.
    async_retry: Decorator for retrying async functions with exponential backoff.
    async_generator_retry: Decorator for retrying async generators.
    run_sync: Execute async coroutines synchronously, handling nested event loops.
    is_dangerous_directory: Check if a path is a system/user directory that should be protected.
    get_user_agent: Generate appropriate user-agent strings for LLM API requests.
    is_user_cancellation_event: Check if an event represents user cancellation.

Tagged text system:
- CANCELLATION_TAG: User cancellations (interrupts, skips, no response)
- TOOL_ERROR_TAG: Tool execution errors
- VIBE_STOP_EVENT_TAG: Middleware-triggered stops
- VIBE_WARNING_TAG: System warnings

Retry decorators support:
- Exponential backoff with configurable delay and backoff factor
- Custom retry predicate (defaults to retryable HTTP errors)
- Works with both regular async functions and async generators
- Handles httpx.HTTPStatusError for transient failures (408, 429, 5xx)

Typical usage:

    from kin_code.core.utils import (
        async_retry,
        TaggedText,
        is_dangerous_directory,
        run_sync,
    )

    # Retry with exponential backoff
    @async_retry(tries=3, delay_seconds=0.5, backoff_factor=2.0)
    async def fetch_data():
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            response.raise_for_status()
            return response.json()

    # Check for dangerous directories before operations
    is_dangerous, reason = is_dangerous_directory("/Users/alice/Desktop")
    if is_dangerous:
        raise ValueError(f"Cannot operate in {reason}")

    # Parse tagged messages
    tagged = TaggedText.from_string("<user_cancellation>Operation cancelled</user_cancellation>")
    if tagged.tag == "user_cancellation":
        print(f"User cancelled: {tagged.message}")

    # Run async code synchronously (handles nested event loops)
    result = run_sync(some_async_function())
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine
import concurrent.futures
from enum import Enum, auto
import functools
import logging
from pathlib import Path
import re
import sys
from typing import Any

import httpx

from kin_code import __version__
from kin_code.core.config import Backend
from kin_code.core.paths.global_paths import LOG_DIR, LOG_FILE
from kin_code.core.types import BaseEvent, ToolResultEvent

CANCELLATION_TAG = "user_cancellation"
TOOL_ERROR_TAG = "tool_error"
KIN_STOP_EVENT_TAG = "kin_stop_event"
KIN_WARNING_TAG = "kin_warning"

KNOWN_TAGS = [CANCELLATION_TAG, TOOL_ERROR_TAG, KIN_STOP_EVENT_TAG, KIN_WARNING_TAG]


class TaggedText:
    _TAG_PATTERN = re.compile(
        rf"<({'|'.join(re.escape(tag) for tag in KNOWN_TAGS)})>(.*?)</\1>",
        flags=re.DOTALL,
    )

    def __init__(self, message: str, tag: str = "") -> None:
        self.message = message
        self.tag = tag

    def __str__(self) -> str:
        if not self.tag:
            return self.message
        return f"<{self.tag}>{self.message}</{self.tag}>"

    @staticmethod
    def from_string(text: str) -> TaggedText:
        found_tag = ""
        result = text

        def replace_tag(match: re.Match[str]) -> str:
            nonlocal found_tag
            tag_name = match.group(1)
            content = match.group(2)
            if not found_tag:
                found_tag = tag_name
            return content

        result = TaggedText._TAG_PATTERN.sub(replace_tag, text)

        if found_tag:
            return TaggedText(result, found_tag)

        return TaggedText(text, "")


class CancellationReason(Enum):
    OPERATION_CANCELLED = auto()
    TOOL_INTERRUPTED = auto()
    TOOL_NO_RESPONSE = auto()
    TOOL_SKIPPED = auto()


def get_user_cancellation_message(
    cancellation_reason: CancellationReason, tool_name: str | None = None
) -> TaggedText:
    match cancellation_reason:
        case CancellationReason.OPERATION_CANCELLED:
            return TaggedText("User cancelled the operation.", CANCELLATION_TAG)
        case CancellationReason.TOOL_INTERRUPTED:
            return TaggedText("Tool execution interrupted by user.", CANCELLATION_TAG)
        case CancellationReason.TOOL_NO_RESPONSE:
            return TaggedText(
                "Tool execution interrupted - no response available", CANCELLATION_TAG
            )
        case CancellationReason.TOOL_SKIPPED:
            return TaggedText(
                tool_name or "Tool execution skipped by user.", CANCELLATION_TAG
            )


def is_user_cancellation_event(event: BaseEvent) -> bool:
    return (
        isinstance(event, ToolResultEvent)
        and event.skipped
        and event.skip_reason is not None
        and f"<{CANCELLATION_TAG}>" in event.skip_reason
    )


def is_dangerous_directory(path: Path | str = ".") -> tuple[bool, str]:
    """Check if the current directory is a dangerous folder that would cause
    issues if we were to run the tool there.

    Args:
        path: Path to check (defaults to current directory)

    Returns:
        tuple[bool, str]: (is_dangerous, reason) where reason explains why it's dangerous
    """
    path = Path(path).resolve()

    home_dir = Path.home()

    dangerous_paths = {
        home_dir: "home directory",
        home_dir / "Documents": "Documents folder",
        home_dir / "Desktop": "Desktop folder",
        home_dir / "Downloads": "Downloads folder",
        home_dir / "Pictures": "Pictures folder",
        home_dir / "Movies": "Movies folder",
        home_dir / "Music": "Music folder",
        home_dir / "Library": "Library folder",
        Path("/Applications"): "Applications folder",
        Path("/System"): "System folder",
        Path("/Library"): "System Library folder",
        Path("/usr"): "System usr folder",
        Path("/private"): "System private folder",
    }

    for dangerous_path, description in dangerous_paths.items():
        try:
            if path == dangerous_path:
                return True, f"You are in the {description}"
        except (OSError, ValueError):
            continue
    return False, ""


LOG_DIR.path.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE.path, "a", "utf-8")],
)

logger = logging.getLogger("kin")


def get_user_agent(backend: Backend) -> str:
    user_agent = f"Kin-Code/{__version__}"
    if backend == Backend.MISTRAL:
        mistral_sdk_prefix = "mistral-client-python/"
        user_agent = f"{mistral_sdk_prefix}{user_agent}"
    return user_agent


def _is_retryable_http_error(e: Exception) -> bool:
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}
    return False


def async_retry[T, **P](
    tries: int = 3,
    delay_seconds: float = 0.5,
    backoff_factor: float = 2.0,
    is_retryable: Callable[[Exception], bool] = _is_retryable_http_error,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Args:
        tries: Number of retry attempts
        delay_seconds: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        is_retryable: Function to determine if an exception should trigger a retry
                     (defaults to checking for retryable HTTP errors from both urllib and httpx)

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exc = None
            for attempt in range(tries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < tries - 1 and is_retryable(e):
                        current_delay = (delay_seconds * (backoff_factor**attempt)) + (
                            0.05 * attempt
                        )
                        await asyncio.sleep(current_delay)
                        continue
                    raise e
            raise RuntimeError(
                f"Retries exhausted. Last error: {last_exc}"
            ) from last_exc

        return wrapper

    return decorator


def async_generator_retry[T, **P](
    tries: int = 3,
    delay_seconds: float = 0.5,
    backoff_factor: float = 2.0,
    is_retryable: Callable[[Exception], bool] = _is_retryable_http_error,
) -> Callable[[Callable[P, AsyncGenerator[T]]], Callable[P, AsyncGenerator[T]]]:
    """Retry decorator for async generators.

    Args:
        tries: Number of retry attempts
        delay_seconds: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        is_retryable: Function to determine if an exception should trigger a retry
                     (defaults to checking for retryable HTTP errors from both urllib and httpx)

    Returns:
        Decorated async generator function with retry logic
    """

    def decorator(
        func: Callable[P, AsyncGenerator[T]],
    ) -> Callable[P, AsyncGenerator[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncGenerator[T]:
            last_exc = None
            for attempt in range(tries):
                try:
                    async for item in func(*args, **kwargs):
                        yield item
                    return
                except Exception as e:
                    last_exc = e
                    if attempt < tries - 1 and is_retryable(e):
                        current_delay = (delay_seconds * (backoff_factor**attempt)) + (
                            0.05 * attempt
                        )
                        await asyncio.sleep(current_delay)
                        continue
                    raise e
            raise RuntimeError(
                f"Retries exhausted. Last error: {last_exc}"
            ) from last_exc

        return wrapper

    return decorator


class ConversationLimitException(Exception):
    pass


def run_sync[T](coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine synchronously, handling nested event loops.

    If called from within an async context (running event loop), runs the
    coroutine in a thread pool executor. Otherwise, uses asyncio.run().

    This mirrors the pattern used by ToolManager for MCP integration.
    """
    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)


def is_windows() -> bool:
    return sys.platform == "win32"

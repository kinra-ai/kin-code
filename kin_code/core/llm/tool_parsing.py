"""Tool call extraction from LLM responses.

This module provides extractors for extracting tool calls from LLM responses
in various formats. Different providers and models expose tool calls differently:

- OpenAI API: Structured `tool_calls` field in message
- Qwen3-coder/Nemotron: XML tags in content when vLLM tool parser not configured
  Format: <function=name><parameter=key>value</parameter></function>

The extractor system supports auto-detection (tries API first, falls back to XML)
as well as manual mode selection for specific providers.

Key components:
    - ToolCallExtractor: Protocol defining the extractor interface
    - APIToolCallExtractor: Extracts from message.tool_calls field
    - XMLToolCallExtractor: Extracts from XML tags in content
    - AutoToolCallExtractor: Tries API first, falls back to XML
    - NoneToolCallExtractor: No-op extractor
    - get_tool_call_extractor: Factory function to get extractor by mode

Typical usage:
    from kin_code.core.llm.tool_parsing import get_tool_call_extractor

    extractor = get_tool_call_extractor("xml")
    tool_calls, modified_content = extractor.extract(message)
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Protocol
from uuid import uuid4

if TYPE_CHECKING:
    from kin_code.core.llm.format import ParsedToolCall
    from kin_code.core.types import LLMMessage


# Regex patterns for XML tool call format
# Matches: <function=tool_name>...</function>
_FUNCTION_TAG_PATTERN = re.compile(
    r"<function=([^>]+)>(.*?)</function>", re.DOTALL | re.IGNORECASE
)
# Matches: <parameter=param_name>value</parameter>
_PARAMETER_TAG_PATTERN = re.compile(
    r"<parameter=([^>]+)>(.*?)</parameter>", re.DOTALL | re.IGNORECASE
)


class ToolCallExtractor(Protocol):
    """Protocol for tool call extractors."""

    def extract(
        self,
        message: LLMMessage,
        strip_from_content: bool = True,
    ) -> tuple[list[ParsedToolCall], str | None]:
        """Extract tool calls from a message.

        Args:
            message: The LLM message to extract tool calls from.
            strip_from_content: If True, remove extracted tool calls from content.

        Returns:
            Tuple of (list of parsed tool calls, modified content or None).
            If content was not modified, returns None for the second element.
        """
        ...


class APIToolCallExtractor:
    """Extracts tool calls from the structured tool_calls field.

    This is the standard OpenAI-compatible format where tool calls are
    returned in a dedicated `tool_calls` array on the message.
    """

    def extract(
        self,
        message: LLMMessage,
        strip_from_content: bool = True,
    ) -> tuple[list[ParsedToolCall], str | None]:
        """Extract tool calls from message.tool_calls field.

        Args:
            message: The LLM message to extract tool calls from.
            strip_from_content: Unused for API extraction (tool calls are in
                               separate field, not embedded in content).

        Returns:
            Tuple of (list of parsed tool calls, None).
            Content is never modified for API extraction.
        """
        from kin_code.core.llm.format import ParsedToolCall

        del strip_from_content  # Not applicable for API tool calls

        tool_calls: list[ParsedToolCall] = []
        api_tool_calls = message.tool_calls or []

        for tc in api_tool_calls:
            if not (function_call := tc.function):
                continue
            try:
                args = json.loads(function_call.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            tool_calls.append(
                ParsedToolCall(
                    tool_name=function_call.name or "",
                    raw_args=args,
                    call_id=tc.id or "",
                )
            )

        return tool_calls, None


class XMLToolCallExtractor:
    """Extracts tool calls from XML tags in content.

    Some models (like Qwen3-coder and Nemotron) output tool calls as XML
    when vLLM's tool-call-parser isn't configured:

        <function=str_replace_editor>
        <parameter=path>kin_code/core</parameter>
        <parameter=command>view</parameter>
        </function>

    This extractor parses these XML tags and converts them to ParsedToolCall
    objects with synthetic call IDs.
    """

    def extract(
        self,
        message: LLMMessage,
        strip_from_content: bool = True,
    ) -> tuple[list[ParsedToolCall], str | None]:
        """Extract tool calls from XML tags in content.

        Args:
            message: The LLM message to extract tool calls from.
            strip_from_content: If True, remove XML tags from content.

        Returns:
            Tuple of (list of parsed tool calls, modified content or None).
        """
        from kin_code.core.llm.format import ParsedToolCall

        content = message.content
        if not content or not isinstance(content, str):
            return [], None

        tool_calls: list[ParsedToolCall] = []
        matches = _FUNCTION_TAG_PATTERN.findall(content)

        for func_name, func_body in matches:
            func_name = func_name.strip()
            args: dict[str, str] = {}

            # Extract parameters from the function body
            param_matches = _PARAMETER_TAG_PATTERN.findall(func_body)
            for param_name, param_value in param_matches:
                args[param_name.strip()] = param_value.strip()

            # Generate synthetic call ID with xml_ prefix
            call_id = f"xml_{uuid4().hex[:12]}"

            tool_calls.append(
                ParsedToolCall(
                    tool_name=func_name,
                    raw_args=args,
                    call_id=call_id,
                )
            )

        if not tool_calls:
            return [], None

        modified_content: str | None = None
        if strip_from_content:
            modified_content = _FUNCTION_TAG_PATTERN.sub("", content).strip()

        return tool_calls, modified_content


class AutoToolCallExtractor:
    """Auto-detects format and applies appropriate extractor.

    Tries extraction strategies in priority order:
    1. API tool_calls field (if present and non-empty)
    2. XML tags in content (fallback)

    First match wins - if API tool calls are found, XML extraction is skipped.
    """

    def __init__(self) -> None:
        self._api_extractor = APIToolCallExtractor()
        self._xml_extractor = XMLToolCallExtractor()

    def extract(
        self,
        message: LLMMessage,
        strip_from_content: bool = True,
    ) -> tuple[list[ParsedToolCall], str | None]:
        """Auto-detect format and extract tool calls.

        Args:
            message: The LLM message to extract tool calls from.
            strip_from_content: If True, remove extracted tags from content.

        Returns:
            Tuple of (list of parsed tool calls, modified content or None).
        """
        # 1. Try API tool_calls field first
        if message.tool_calls:
            return self._api_extractor.extract(message, strip_from_content)

        # 2. Fall back to XML extraction
        content = message.content
        if content and isinstance(content, str) and "<function=" in content.lower():
            return self._xml_extractor.extract(message, strip_from_content)

        return [], None


class NoneToolCallExtractor:
    """No-op extractor that performs no extraction."""

    def extract(
        self,
        message: LLMMessage,
        strip_from_content: bool = True,
    ) -> tuple[list[ParsedToolCall], str | None]:
        """Return empty list without modification.

        Args:
            message: Unused.
            strip_from_content: Unused.

        Returns:
            Empty tuple of ([], None).
        """
        del message  # Unused
        del strip_from_content  # Unused
        return [], None


# Module-level singleton instances for reuse
_api_extractor = APIToolCallExtractor()
_xml_extractor = XMLToolCallExtractor()
_auto_extractor = AutoToolCallExtractor()
_none_extractor = NoneToolCallExtractor()


def get_tool_call_extractor(mode: str) -> ToolCallExtractor:
    """Get extractor instance by mode name.

    Args:
        mode: Extraction mode name (api, xml, auto, none).

    Returns:
        Appropriate ToolCallExtractor instance.
    """
    match mode.lower():
        case "api":
            return _api_extractor
        case "xml":
            return _xml_extractor
        case "auto":
            return _auto_extractor
        case "none":
            return _none_extractor
        case _:
            # Default to API for unknown modes
            return _api_extractor

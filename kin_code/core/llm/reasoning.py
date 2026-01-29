"""Reasoning content extraction from LLM responses.

This module provides extractors for extracting reasoning/thinking content from
LLM responses in various formats. Different providers and models expose reasoning
content differently:

- DeepSeek R1: `reasoning_content` field
- OpenRouter (Minimax-m2.1, Kimi K2): `reasoning_details` array
- Qwen QwQ: `<think>...</think>` XML tags in content

The extractor system supports auto-detection (default) that tries each format
in priority order, as well as manual mode selection for specific providers.

Key components:
    - ReasoningExtractor: Protocol defining the extractor interface
    - FieldExtractor: Extracts from a named field (e.g., reasoning_content)
    - ReasoningDetailsExtractor: Extracts from OpenRouter's reasoning_details array
    - ThinkTagExtractor: Extracts from <think>...</think> XML tags in content
    - AutoExtractor: Auto-detects format and applies appropriate extractor
    - get_extractor: Factory function to get extractor by mode

Typical usage:
    from kin_code.core.llm.reasoning import get_extractor

    extractor = get_extractor("auto")
    msg_dict = extractor.extract(msg_dict, field_name="reasoning_content")
"""

from __future__ import annotations

import re
from typing import Any, Protocol


class ReasoningExtractor(Protocol):
    """Protocol for reasoning content extractors."""

    def extract(
        self,
        msg_dict: dict[str, Any],
        field_name: str,
        preserve_in_content: bool = False,
    ) -> dict[str, Any]:
        """Extract reasoning content and normalize to reasoning_content field.

        Args:
            msg_dict: Message dictionary from API response.
            field_name: The configured reasoning field name.
            preserve_in_content: If True, keep reasoning in content for context.
                                 If False, strip reasoning from content.

        Returns:
            Modified message dict with reasoning_content normalized.
        """
        ...


class FieldExtractor:
    """Extracts reasoning from a named field.

    Handles the standard case where reasoning is in a simple field like
    `reasoning_content` or `reasoning`.
    """

    def extract(
        self,
        msg_dict: dict[str, Any],
        field_name: str,
        preserve_in_content: bool = False,
    ) -> dict[str, Any]:
        """Extract reasoning from a named field.

        If field_name differs from "reasoning_content" and exists in msg_dict,
        renames it to "reasoning_content" for normalization.

        Args:
            msg_dict: Message dictionary from API response.
            field_name: The field name to extract from.
            preserve_in_content: Unused for field extraction (reasoning is in
                                 separate field, not embedded in content).

        Returns:
            Modified message dict with reasoning_content normalized.
        """
        del (
            preserve_in_content
        )  # Field-based reasoning is already separate from content
        if field_name != "reasoning_content" and field_name in msg_dict:
            msg_dict["reasoning_content"] = msg_dict.pop(field_name)
        return msg_dict


class ReasoningDetailsExtractor:
    """Extracts reasoning from OpenRouter's reasoning_details array.

    OpenRouter returns reasoning in a `reasoning_details` array with typed blocks:
    - `reasoning.summary`: Contains a `summary` field
    - `reasoning.text`: Contains a `text` field
    - `reasoning.encrypted`: Contains encrypted `data` (skipped)

    Example format:
        {
            "reasoning_details": [
                {"type": "reasoning.summary", "summary": "..."},
                {"type": "reasoning.text", "text": "..."},
                {"type": "reasoning.encrypted", "data": "base64..."}
            ]
        }
    """

    def extract(
        self,
        msg_dict: dict[str, Any],
        field_name: str,
        preserve_in_content: bool = False,
    ) -> dict[str, Any]:
        """Extract reasoning from reasoning_details array.

        Combines all readable reasoning blocks (summary and text) with newlines.
        Skips encrypted blocks.

        Args:
            msg_dict: Message dictionary from API response.
            field_name: Unused, kept for protocol compatibility.
            preserve_in_content: Unused for reasoning_details (reasoning is in
                                 separate array, not embedded in content).

        Returns:
            Modified message dict with reasoning_content from details array.
        """
        del field_name  # Unused for this extractor
        del preserve_in_content  # reasoning_details is already separate from content
        details = msg_dict.get("reasoning_details")
        if not details or not isinstance(details, list):
            return msg_dict

        reasoning_parts: list[str] = []
        for block in details:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "")
            match block_type:
                case "reasoning.summary":
                    if summary := block.get("summary"):
                        reasoning_parts.append(str(summary))
                case "reasoning.text":
                    if text := block.get("text"):
                        reasoning_parts.append(str(text))
                case "reasoning.encrypted":
                    # Skip encrypted blocks - not readable
                    pass

        if reasoning_parts:
            msg_dict["reasoning_content"] = "\n".join(reasoning_parts)

        # Remove the original reasoning_details to avoid confusion
        msg_dict.pop("reasoning_details", None)
        return msg_dict


# Regex pattern for think tags - matches <think>...</think> with content
_THINK_TAG_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)


class ThinkTagExtractor:
    """Extracts reasoning from <think>...</think> XML tags in content.

    Some models (like Qwen QwQ) embed reasoning in XML-style think tags
    within the regular content field:
        <think>Let me reason through this...</think>
        The answer is 42.
    """

    def extract(
        self,
        msg_dict: dict[str, Any],
        field_name: str,
        preserve_in_content: bool = False,
    ) -> dict[str, Any]:
        """Extract reasoning from think tags in content.

        Finds all <think>...</think> blocks, combines them as reasoning_content.
        By default, removes the tags from the main content (for STRIP mode).
        If preserve_in_content=True, keeps the original content unchanged
        (for PRESERVE mode where models benefit from seeing prior reasoning).

        Args:
            msg_dict: Message dictionary from API response.
            field_name: Unused, kept for protocol compatibility.
            preserve_in_content: If True, keep think tags in content.
                                 If False, remove them from content.

        Returns:
            Modified message dict with reasoning_content extracted from tags.
        """
        del field_name  # Unused for this extractor
        content = msg_dict.get("content")
        if not content or not isinstance(content, str):
            return msg_dict

        # Find all think blocks
        matches = _THINK_TAG_PATTERN.findall(content)
        if not matches:
            return msg_dict

        # Combine all think blocks
        reasoning_content = "\n".join(
            match.strip() for match in matches if match.strip()
        )

        if reasoning_content:
            msg_dict["reasoning_content"] = reasoning_content

        # Only strip think tags from content if not preserving
        if not preserve_in_content:
            cleaned_content = _THINK_TAG_PATTERN.sub("", content).strip()
            msg_dict["content"] = cleaned_content

        return msg_dict


class AutoExtractor:
    """Auto-detects reasoning format and applies appropriate extractor.

    Tries extraction strategies in priority order:
    1. reasoning_details array (OpenRouter format)
    2. Custom field name (if different from reasoning_content)
    3. Standard reasoning_content field
    4. <think> tags in content

    First match wins - if a format is detected and yields content,
    that content is used.
    """

    def __init__(self) -> None:
        self._reasoning_details = ReasoningDetailsExtractor()
        self._field = FieldExtractor()
        self._think_tags = ThinkTagExtractor()

    def extract(
        self,
        msg_dict: dict[str, Any],
        field_name: str,
        preserve_in_content: bool = False,
    ) -> dict[str, Any]:
        """Auto-detect format and extract reasoning content.

        Args:
            msg_dict: Message dictionary from API response.
            field_name: The configured reasoning field name.
            preserve_in_content: If True, keep reasoning in content for context.
                                 Only affects ThinkTagExtractor (others have
                                 reasoning in separate fields already).

        Returns:
            Modified message dict with reasoning_content normalized.
        """
        # 1. OpenRouter reasoning_details array
        if "reasoning_details" in msg_dict:
            return self._reasoning_details.extract(
                msg_dict, field_name, preserve_in_content
            )

        # 2. Custom field name (if configured differently)
        if field_name != "reasoning_content" and field_name in msg_dict:
            return self._field.extract(msg_dict, field_name, preserve_in_content)

        # 3. Standard reasoning_content field - already in correct format
        if "reasoning_content" in msg_dict:
            return msg_dict

        # 4. Think tags in content
        content = msg_dict.get("content")
        if content and isinstance(content, str) and "<think>" in content.lower():
            return self._think_tags.extract(msg_dict, field_name, preserve_in_content)

        return msg_dict


class NoneExtractor:
    """No-op extractor that performs no extraction."""

    def extract(
        self,
        msg_dict: dict[str, Any],
        field_name: str,
        preserve_in_content: bool = False,
    ) -> dict[str, Any]:
        """Return message dict unchanged.

        Args:
            msg_dict: Message dictionary from API response.
            field_name: Unused.
            preserve_in_content: Unused.

        Returns:
            Unchanged message dict.
        """
        del field_name  # Unused
        del preserve_in_content  # Unused
        return msg_dict


# Module-level singleton instances for reuse
_auto_extractor = AutoExtractor()
_field_extractor = FieldExtractor()
_reasoning_details_extractor = ReasoningDetailsExtractor()
_think_tag_extractor = ThinkTagExtractor()
_none_extractor = NoneExtractor()


def get_extractor(mode: str) -> ReasoningExtractor:
    """Get extractor instance by mode name.

    Args:
        mode: Extraction mode name (auto, field, reasoning_details, think_tags, none).

    Returns:
        Appropriate ReasoningExtractor instance.
    """
    match mode.lower():
        case "auto":
            return _auto_extractor
        case "field":
            return _field_extractor
        case "reasoning_details":
            return _reasoning_details_extractor
        case "think_tags":
            return _think_tag_extractor
        case "none":
            return _none_extractor
        case _:
            # Default to auto for unknown modes
            return _auto_extractor


def extract_think_tags_from_content(content: str) -> tuple[str, str | None]:
    """Extract think tags from content string.

    Utility function for post-processing streamed content that may contain
    think tags spanning multiple chunks.

    Args:
        content: The full accumulated content string.

    Returns:
        Tuple of (cleaned_content, reasoning_content or None).
    """
    if not content or "<think>" not in content.lower():
        return content, None

    matches = _THINK_TAG_PATTERN.findall(content)
    if not matches:
        return content, None

    reasoning_content = "\n".join(match.strip() for match in matches if match.strip())
    cleaned_content = _THINK_TAG_PATTERN.sub("", content).strip()

    return cleaned_content, reasoning_content if reasoning_content else None

"""Tests for tool call parsing from LLM responses."""

from __future__ import annotations

import pytest

from kin_code.core.llm.tool_parsing import (
    APIToolCallExtractor,
    AutoToolCallExtractor,
    NoneToolCallExtractor,
    XMLToolCallExtractor,
    get_tool_call_extractor,
)
from kin_code.core.types import LLMMessage, Role


class TestXMLToolCallExtractor:
    """Tests for XMLToolCallExtractor."""

    def test_single_xml_tool_call(self) -> None:
        """Extract a single XML tool call from content."""
        content = """<function=str_replace_editor>
<parameter=path>kin_code/core</parameter>
<parameter=command>view</parameter>
</function>"""
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "str_replace_editor"
        assert tool_calls[0].raw_args == {"path": "kin_code/core", "command": "view"}
        assert tool_calls[0].call_id.startswith("xml_")
        assert modified_content == ""

    def test_multiple_xml_tool_calls(self) -> None:
        """Extract multiple XML tool calls from content."""
        content = """<function=read_file>
<parameter=path>src/main.py</parameter>
</function>

<function=write_file>
<parameter=path>src/output.py</parameter>
<parameter=content>print("hello")</parameter>
</function>"""
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert len(tool_calls) == 2
        assert tool_calls[0].tool_name == "read_file"
        assert tool_calls[0].raw_args == {"path": "src/main.py"}
        assert tool_calls[1].tool_name == "write_file"
        assert tool_calls[1].raw_args == {
            "path": "src/output.py",
            "content": 'print("hello")',
        }
        assert modified_content is not None
        assert modified_content.strip() == ""

    def test_mixed_content_and_xml(self) -> None:
        """Preserve surrounding text when extracting XML tool calls."""
        content = """Let me read that file for you.

<function=read_file>
<parameter=path>config.toml</parameter>
</function>

I'll analyze the results."""
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "read_file"
        assert modified_content is not None
        assert "Let me read that file for you." in modified_content
        assert "I'll analyze the results." in modified_content
        assert "<function" not in modified_content

    def test_multiline_parameter_values(self) -> None:
        """Handle multiline parameter values correctly."""
        content = """<function=write_file>
<parameter=path>test.py</parameter>
<parameter=content>def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()</parameter>
</function>"""
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, _ = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "write_file"
        content_value = tool_calls[0].raw_args["content"]
        assert "def hello():" in content_value
        assert 'print("Hello, World!")' in content_value
        assert "if __name__" in content_value

    def test_tool_call_without_parameters(self) -> None:
        """Handle tool calls with no parameters."""
        content = "<function=get_status></function>"
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "get_status"
        assert tool_calls[0].raw_args == {}
        assert modified_content == ""

    def test_no_tool_calls_returns_empty(self) -> None:
        """Return empty list when no XML tool calls present."""
        content = "This is just regular text without any tool calls."
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert tool_calls == []
        assert modified_content is None

    def test_empty_content(self) -> None:
        """Handle empty content gracefully."""
        message = LLMMessage(role=Role.assistant, content="")
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert tool_calls == []
        assert modified_content is None

    def test_none_content(self) -> None:
        """Handle None content gracefully."""
        message = LLMMessage(role=Role.assistant, content=None)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert tool_calls == []
        assert modified_content is None

    def test_preserve_content_when_strip_disabled(self) -> None:
        """Keep XML tags in content when strip_from_content is False."""
        content = "<function=test><parameter=x>1</parameter></function>"
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, modified_content = extractor.extract(
            message, strip_from_content=False
        )

        assert len(tool_calls) == 1
        assert modified_content is None  # Content not modified

    def test_case_insensitive_tags(self) -> None:
        """Handle case variations in XML tags."""
        content = "<FUNCTION=test><PARAMETER=x>value</PARAMETER></FUNCTION>"
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = XMLToolCallExtractor()

        tool_calls, _ = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "test"
        assert tool_calls[0].raw_args == {"x": "value"}


class TestAPIToolCallExtractor:
    """Tests for APIToolCallExtractor."""

    def test_extracts_from_tool_calls_field(self) -> None:
        """Extract tool calls from message.tool_calls field."""
        message = LLMMessage(
            role=Role.assistant,
            content="I'll read that file.",
            tool_calls=[
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "arguments": '{"path": "test.py"}',
                    },
                }
            ],
        )
        extractor = APIToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "read_file"
        assert tool_calls[0].raw_args == {"path": "test.py"}
        assert tool_calls[0].call_id == "call_123"
        assert modified_content is None  # API extractor never modifies content

    def test_handles_invalid_json_arguments(self) -> None:
        """Gracefully handle malformed JSON in arguments."""
        message = LLMMessage(
            role=Role.assistant,
            content=None,
            tool_calls=[
                {
                    "id": "call_456",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": "not valid json"},
                }
            ],
        )
        extractor = APIToolCallExtractor()

        tool_calls, _ = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "test_tool"
        assert tool_calls[0].raw_args == {}  # Falls back to empty dict

    def test_no_tool_calls(self) -> None:
        """Return empty list when no tool_calls field."""
        message = LLMMessage(role=Role.assistant, content="Just text")
        extractor = APIToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert tool_calls == []
        assert modified_content is None


class TestAutoToolCallExtractor:
    """Tests for AutoToolCallExtractor."""

    def test_prefers_api_over_xml(self) -> None:
        """Prefer API tool_calls when both formats present."""
        message = LLMMessage(
            role=Role.assistant,
            content="<function=xml_tool><parameter=x>1</parameter></function>",
            tool_calls=[
                {
                    "id": "call_api",
                    "type": "function",
                    "function": {"name": "api_tool", "arguments": "{}"},
                }
            ],
        )
        extractor = AutoToolCallExtractor()

        tool_calls, _ = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "api_tool"
        assert tool_calls[0].call_id == "call_api"

    def test_falls_back_to_xml(self) -> None:
        """Fall back to XML extraction when no API tool calls."""
        content = "<function=xml_only><parameter=p>val</parameter></function>"
        message = LLMMessage(role=Role.assistant, content=content)
        extractor = AutoToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "xml_only"
        assert tool_calls[0].call_id.startswith("xml_")
        assert modified_content == ""

    def test_returns_empty_when_no_tool_calls(self) -> None:
        """Return empty list when neither format has tool calls."""
        message = LLMMessage(role=Role.assistant, content="Plain text response")
        extractor = AutoToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert tool_calls == []
        assert modified_content is None


class TestNoneToolCallExtractor:
    """Tests for NoneToolCallExtractor."""

    def test_returns_empty_always(self) -> None:
        """Always return empty list regardless of content."""
        content = "<function=test><parameter=x>1</parameter></function>"
        message = LLMMessage(
            role=Role.assistant,
            content=content,
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "tool", "arguments": "{}"},
                }
            ],
        )
        extractor = NoneToolCallExtractor()

        tool_calls, modified_content = extractor.extract(message)

        assert tool_calls == []
        assert modified_content is None


class TestGetToolCallExtractor:
    """Tests for the get_tool_call_extractor factory function."""

    @pytest.mark.parametrize(
        ("mode", "expected_type"),
        [
            ("api", APIToolCallExtractor),
            ("API", APIToolCallExtractor),
            ("xml", XMLToolCallExtractor),
            ("XML", XMLToolCallExtractor),
            ("auto", AutoToolCallExtractor),
            ("AUTO", AutoToolCallExtractor),
            ("none", NoneToolCallExtractor),
            ("NONE", NoneToolCallExtractor),
        ],
    )
    def test_returns_correct_extractor(
        self, mode: str, expected_type: type
    ) -> None:
        """Return the correct extractor type for each mode."""
        extractor = get_tool_call_extractor(mode)
        assert isinstance(extractor, expected_type)

    def test_unknown_mode_defaults_to_api(self) -> None:
        """Default to API extractor for unknown modes."""
        extractor = get_tool_call_extractor("unknown_mode")
        assert isinstance(extractor, APIToolCallExtractor)

    def test_returns_singleton_instances(self) -> None:
        """Return the same instance for repeated calls."""
        ext1 = get_tool_call_extractor("xml")
        ext2 = get_tool_call_extractor("xml")
        assert ext1 is ext2

from __future__ import annotations

from kin_code.core.llm.format import ResolvedToolCall
from kin_code.core.types import LLMMessage, Role, ToolCall
from kin_code.core.utils import CancellationReason, get_user_cancellation_message


class ConversationHistory:
    """Manages message history validation, cleaning, and manipulation."""

    def __init__(self, messages: list[LLMMessage]) -> None:
        self.messages = messages

    def clean(self) -> None:
        """Clean message history by filling missing tool responses and ensuring proper structure."""
        acceptable_history_size = 2
        if len(self.messages) < acceptable_history_size:
            return
        self.fill_missing_tool_responses()
        self.ensure_assistant_after_tools()

    def append_tool_response(self, tool_call: ResolvedToolCall, text: str) -> None:
        """Append a tool response message to history."""
        from kin_code.core.llm.format import APIToolFormatHandler

        format_handler = APIToolFormatHandler()
        self.messages.append(
            LLMMessage.model_validate(
                format_handler.create_tool_response_message(tool_call, text)
            )
        )

    def count_tool_responses(self, start_index: int) -> int:
        """Count consecutive tool response messages starting at the given index.

        Args:
            start_index: The index to start counting from.

        Returns:
            The number of consecutive tool response messages.
        """
        count = 0
        j = start_index
        while j < len(self.messages) and self.messages[j].role == "tool":
            count += 1
            j += 1
        return count

    def create_missing_response(self, tool_call_data: ToolCall) -> LLMMessage:
        """Create an empty tool response message for a missing tool call response.

        Args:
            tool_call_data: The tool call data to create a response for.

        Returns:
            An LLMMessage with role=tool indicating no response was received.
        """
        tool_name = ""
        if tool_call_data.function:
            tool_name = tool_call_data.function.name or ""

        return LLMMessage(
            role=Role.tool,
            tool_call_id=tool_call_data.id or "",
            name=tool_name,
            content=str(get_user_cancellation_message(CancellationReason.TOOL_NO_RESPONSE)),
        )

    def fill_missing_tool_responses(self) -> None:
        """Fill in empty responses for tool calls that are missing responses."""
        i = 1
        while i < len(self.messages):
            msg = self.messages[i]

            if msg.role != "assistant" or not msg.tool_calls:
                i += 1
                continue

            expected_responses = len(msg.tool_calls)
            if expected_responses == 0:
                i += 1
                continue

            actual_responses = self.count_tool_responses(i + 1)

            if actual_responses < expected_responses:
                insertion_point = i + 1 + actual_responses
                for call_idx in range(actual_responses, expected_responses):
                    empty_response = self.create_missing_response(
                        msg.tool_calls[call_idx]
                    )
                    self.messages.insert(insertion_point, empty_response)
                    insertion_point += 1

            i = i + 1 + expected_responses

    def ensure_assistant_after_tools(self) -> None:
        """Ensure there's an assistant message after tool responses if needed."""
        min_message_size = 2
        if len(self.messages) < min_message_size:
            return

        last_msg = self.messages[-1]
        if last_msg.role is Role.tool:
            empty_assistant_msg = LLMMessage(role=Role.assistant, content="Understood.")
            self.messages.append(empty_assistant_msg)

    def reset(self, system_message: LLMMessage) -> None:
        """Reset history to just the system message."""
        self.messages.clear()
        self.messages.append(system_message)

    def replace_system_message(self, new_system_prompt: str) -> None:
        """Replace the system message while preserving other messages."""
        non_system_messages = [msg for msg in self.messages if msg.role != Role.system]
        self.messages.clear()
        self.messages.append(LLMMessage(role=Role.system, content=new_system_prompt))
        self.messages.extend(non_system_messages)

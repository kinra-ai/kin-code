from __future__ import annotations

from collections.abc import AsyncGenerator
import re
from typing import ClassVar

from pydantic import BaseModel, Field

from kin_code.core.agent_loop import AgentLoop
from kin_code.core.agents.models import AgentType
from kin_code.core.config import SessionLoggingConfig, VibeConfig
from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    InvokeContext,
    ToolError,
    ToolPermission,
)
from kin_code.core.tools.ui import (
    ToolCallDisplay,
    ToolResultDisplay,
    ToolUIData,
    ToolUIDataAdapter,
)
from kin_code.core.types import (
    AssistantEvent,
    ReasoningEvent,
    Role,
    ToolCallEvent,
    ToolResultEvent,
    ToolStreamEvent,
)

_TASK_SUFFIX = (
    "\n\nAfter completing your work, always provide a summary of your findings. "
    "Do not end with just tool calls - provide a final response."
)

# Regex patterns that indicate content contains malformed tool call attempts.
# These patterns match XML-style tool calls that some models emit incorrectly.
_TOOL_CALL_PATTERN = re.compile(
    r"<(?:function[=\s]|tool_call>|parameter[=\s])", re.IGNORECASE
)


def _is_tool_call_content(content: str) -> bool:
    """Check if content appears to be a malformed tool call rather than real text.

    Detects XML-style tool call patterns anywhere in the content, not just at the
    start. This handles cases where models prefix malformed tool calls with text
    like "Here's my analysis:" before the XML.
    """
    return bool(_TOOL_CALL_PATTERN.search(content))


class TaskArgs(BaseModel):
    task: str = Field(description="The task to delegate to the subagent")
    agent: str = Field(
        default="explore",
        description="Name of the agent profile to use (must be a subagent)",
    )
    include_reasoning: bool = Field(
        default=False,
        description=(
            "If True, include subagent's reasoning trace in response. "
            "Useful for debugging or when parent needs visibility into subagent thinking."
        ),
    )


class TaskResult(BaseModel):
    response: str = Field(description="The accumulated response from the subagent")
    reasoning: str | None = Field(
        default=None,
        exclude=True,
        description=(
            "Subagent reasoning trace (excluded from serialization to prevent "
            "context bloat in parent agent). Only populated when include_reasoning=True."
        ),
    )
    turns_used: int = Field(description="Number of turns the subagent used")
    completed: bool = Field(description="Whether the task completed normally")
    model_alias: str | None = Field(
        default=None, description="The model alias used by the subagent"
    )
    provider: str | None = Field(
        default=None, description="The provider used by the subagent"
    )


class TaskToolConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK


class _EventProcessingState:
    """Mutable state for processing subagent events."""

    accumulated_response: list[str]
    accumulated_reasoning: list[str]
    completed: bool

    def __init__(self) -> None:
        self.accumulated_response = []
        self.accumulated_reasoning = []
        self.completed = True


class Task(
    BaseTool[TaskArgs, TaskResult, TaskToolConfig, BaseToolState],
    ToolUIData[TaskArgs, TaskResult],
):
    description: ClassVar[str] = """Delegate work to a specialized subagent.

Subagents run in isolated context windows. When you delegate, the subagent's
exploration doesn't consume your main context - you receive only the synthesized result.

NATURAL FITS FOR DELEGATION:
- Codebase exploration requiring many file reads → explore agent
- Web research requiring multiple fetches and synthesis → web-research agent
- Implementation planning requiring deep analysis → planner agent
- Autonomous work that doesn't need user feedback → general agent

BETTER HANDLED DIRECTLY:
- Quick lookups where you know the exact file
- Single tool calls (one grep, one read)
- Tasks requiring back-and-forth with the user

Think of subagents as specialists you can consult - they're particularly
valuable when the work is deep but the answer you need is concise.

NOTES:
- Subagents run in-memory without saving logs
- Only subagents can be used (not regular agents)
- Prevents recursive spawning for safety"""

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        args = event.args
        if isinstance(args, TaskArgs):
            return ToolCallDisplay(summary=f"Running {args.agent} agent: {args.task}")
        return ToolCallDisplay(summary="Running subagent")

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        result = event.result
        if isinstance(result, TaskResult):
            turn_word = "turn" if result.turns_used == 1 else "turns"
            model_parts = [p for p in (result.model_alias, result.provider) if p]
            model_info = f" [{', '.join(model_parts)}]" if model_parts else ""
            if not result.completed:
                return ToolResultDisplay(
                    success=False,
                    message=f"Agent interrupted after {result.turns_used} {turn_word}{model_info}",
                )
            return ToolResultDisplay(
                success=True,
                message=f"Agent completed in {result.turns_used} {turn_word}{model_info}",
            )
        return ToolResultDisplay(success=True, message="Agent completed")

    @classmethod
    def get_status_text(cls) -> str:
        return "Running subagent"

    def _get_model_info(self, subagent_loop: AgentLoop) -> tuple[str | None, str | None]:
        """Extract model alias and provider from subagent loop."""
        try:
            active_model = subagent_loop.config.get_active_model()
            return active_model.alias, active_model.provider
        except (ValueError, AttributeError):
            return None, None

    def _process_event(
        self,
        event: AssistantEvent | ToolCallEvent | ReasoningEvent | ToolResultEvent,
        state: _EventProcessingState,
        ctx: InvokeContext,
    ) -> ToolStreamEvent | None:
        """Handle a single event from the subagent loop.

        Updates state in-place and returns a ToolStreamEvent if one should be yielded.
        Only processes AssistantEvent, ToolCallEvent, ReasoningEvent, and ToolResultEvent.
        """
        match event:
            case ToolCallEvent():
                # Clear accumulated response when tool calls start.
                # We only want the final summary after all tool execution.
                state.accumulated_response.clear()
            case AssistantEvent(content=content) if content:
                state.accumulated_response.append(content)
                if event.stopped_by_middleware:
                    state.completed = False
            case ReasoningEvent(content=content) if content:
                state.accumulated_reasoning.append(content)
            case ToolResultEvent(skipped=True):
                state.completed = False
            case ToolResultEvent(result=result, tool_class=tool_class) if result and tool_class:
                adapter = ToolUIDataAdapter(tool_class)
                display = adapter.get_result_display(event)
                return ToolStreamEvent(
                    tool_name=self.get_name(),
                    message=f"{event.tool_name}: {display.message}",
                    tool_call_id=ctx.tool_call_id,
                )
        return None

    def _extract_response_from_history(self, subagent_loop: AgentLoop) -> str:
        """Extract final response from message history when accumulated response is empty.

        Handles models that return empty content on their final turn after tool calls.
        """
        for msg in reversed(subagent_loop.messages):
            if msg.role != Role.assistant or not msg.content:
                continue
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            # Skip empty content and malformed tool call attempts
            if content.strip() and not _is_tool_call_content(content):
                return content
        return ""

    async def run(
        self, args: TaskArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | TaskResult, None]:
        if not ctx or not ctx.agent_manager:
            raise ToolError("Task tool requires agent_manager in context")

        try:
            agent_profile = ctx.agent_manager.get_agent(args.agent)
        except ValueError as e:
            raise ToolError(f"Unknown agent: {args.agent}") from e

        if agent_profile.agent_type != AgentType.SUBAGENT:
            raise ToolError(
                f"Agent '{args.agent}' is a {agent_profile.agent_type.value} agent. "
                f"Only subagents can be used with the task tool. "
                f"This is a security constraint to prevent recursive spawning."
            )

        base_config = VibeConfig.load(
            session_logging=SessionLoggingConfig(enabled=False)
        )
        subagent_loop = AgentLoop(config=base_config, agent_name=args.agent)
        model_alias, provider = self._get_model_info(subagent_loop)

        if ctx.approval_callback:
            subagent_loop.set_approval_callback(ctx.approval_callback)

        state = _EventProcessingState()
        _handled_types = (AssistantEvent, ToolCallEvent, ReasoningEvent, ToolResultEvent)
        try:
            async for event in subagent_loop.act(args.task + _TASK_SUFFIX):
                if isinstance(event, _handled_types):
                    if stream_event := self._process_event(event, state, ctx):
                        yield stream_event

            turns_used = sum(
                msg.role == Role.assistant for msg in subagent_loop.messages
            )
        except Exception as e:
            state.completed = False
            state.accumulated_response.append(f"\n[Subagent error: {e}]")
            turns_used = sum(
                msg.role == Role.assistant for msg in subagent_loop.messages
            )

        response_content = "".join(state.accumulated_response)

        # Filter out malformed tool call content from accumulated response
        if response_content.strip() and _is_tool_call_content(response_content):
            response_content = ""

        # Fallback: check message history if no valid content accumulated
        if not response_content.strip():
            response_content = self._extract_response_from_history(subagent_loop)

        # If still no valid content, provide a fallback message
        if not response_content.strip():
            response_content = (
                "[Subagent completed tool execution but did not provide a summary. "
                "Check the tool results above for details.]"
            )

        reasoning_content = "".join(state.accumulated_reasoning) or None

        # Reasoning is excluded from serialization by default to prevent context bloat.
        # Only populate when explicitly requested for debugging/programmatic access.
        yield TaskResult(
            response=response_content,
            reasoning=reasoning_content if args.include_reasoning else None,
            turns_used=turns_used,
            completed=state.completed,
            model_alias=model_alias,
            provider=provider,
        )

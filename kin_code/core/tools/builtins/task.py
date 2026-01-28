from __future__ import annotations

from collections.abc import AsyncGenerator
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

    async def run(
        self, args: TaskArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | TaskResult, None]:
        if not ctx or not ctx.agent_manager:
            raise ToolError("Task tool requires agent_manager in context")

        agent_manager = ctx.agent_manager

        try:
            agent_profile = agent_manager.get_agent(args.agent)
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

        try:
            active_model = subagent_loop.config.get_active_model()
            model_alias = active_model.alias
            provider = active_model.provider
        except (ValueError, AttributeError):
            model_alias = None
            provider = None

        if ctx and ctx.approval_callback:
            subagent_loop.set_approval_callback(ctx.approval_callback)

        accumulated_response: list[str] = []
        accumulated_reasoning: list[str] = []
        completed = True
        try:
            async for event in subagent_loop.act(args.task):
                if isinstance(event, AssistantEvent) and event.content:
                    accumulated_response.append(event.content)
                    if event.stopped_by_middleware:
                        completed = False
                elif isinstance(event, ReasoningEvent) and event.content:
                    accumulated_reasoning.append(event.content)
                elif isinstance(event, ToolResultEvent):
                    if event.skipped:
                        completed = False
                    elif event.result and event.tool_class:
                        adapter = ToolUIDataAdapter(event.tool_class)
                        display = adapter.get_result_display(event)
                        message = f"{event.tool_name}: {display.message}"
                        yield ToolStreamEvent(
                            tool_name=self.get_name(),
                            message=message,
                            tool_call_id=ctx.tool_call_id,
                        )

            turns_used = sum(
                msg.role == Role.assistant for msg in subagent_loop.messages
            )

        except Exception as e:
            completed = False
            accumulated_response.append(f"\n[Subagent error: {e}]")
            turns_used = sum(
                msg.role == Role.assistant for msg in subagent_loop.messages
            )

        reasoning_content = "".join(accumulated_reasoning) or None
        response_content = "".join(accumulated_response)

        # Reasoning is excluded from serialization by default to prevent context bloat.
        # Only populate when explicitly requested for debugging/programmatic access.
        yield TaskResult(
            response=response_content,
            reasoning=reasoning_content if args.include_reasoning else None,
            turns_used=turns_used,
            completed=completed,
            model_alias=model_alias,
            provider=provider,
        )

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Callable
from enum import StrEnum, auto
import time
from typing import cast

from pydantic import BaseModel

from kin_code.core.agents.manager import AgentManager
from kin_code.core.llm.format import APIToolFormatHandler, ResolvedMessage
from kin_code.core.tools.base import (
    BaseTool,
    InvokeContext,
    ToolError,
    ToolPermission,
    ToolPermissionError,
)
from kin_code.core.tools.manager import ToolManager
from kin_code.core.types import (
    AgentStats,
    ApprovalCallback,
    ApprovalResponse,
    AsyncApprovalCallback,
    LLMMessage,
    Role,
    SyncApprovalCallback,
    ToolCallEvent,
    ToolResultEvent,
    ToolStreamEvent,
    UserInputCallback,
)
from kin_code.core.utils import (
    TOOL_ERROR_TAG,
    CancellationReason,
    get_user_cancellation_message,
)


class ToolExecutionResponse(StrEnum):
    SKIP = auto()
    EXECUTE = auto()


class ToolDecision(BaseModel):
    verdict: ToolExecutionResponse
    feedback: str | None = None


class ToolRunner:
    """Coordinates tool execution with permission handling."""

    def __init__(
        self,
        tool_manager: ToolManager,
        approval_callback: ApprovalCallback | None = None,
        auto_approve: bool = False,
    ) -> None:
        self.tool_manager = tool_manager
        self.approval_callback = approval_callback
        self.auto_approve = auto_approve

    def set_approval_callback(self, callback: ApprovalCallback | None) -> None:
        """Set or update the approval callback."""
        self.approval_callback = callback

    def _make_tool_message(
        self, tool_name: str, content: str, tool_call_id: str
    ) -> LLMMessage:
        """Create a tool response message."""
        return LLMMessage(
            role=Role.tool, name=tool_name, content=content, tool_call_id=tool_call_id
        )

    def _make_error_message(self, tool_name: str, error: str) -> str:
        """Format an error message with the standard error tag."""
        return f"<{TOOL_ERROR_TAG}>{tool_name}: {error}</{TOOL_ERROR_TAG}>"

    async def handle_tool_calls(
        self,
        resolved: ResolvedMessage,
        agent_manager: AgentManager,
        user_input_callback: UserInputCallback | None,
        stats: AgentStats,
        history_append_func: Callable[[LLMMessage], None],
    ) -> AsyncGenerator[ToolCallEvent | ToolResultEvent | ToolStreamEvent]:
        """Handle all tool calls from a resolved message.

        Args:
            resolved: The resolved message containing tool calls
            agent_manager: The agent manager for context
            user_input_callback: Callback for user input during tool execution
            stats: Stats tracker to update
            history_append_func: Function to append tool responses to history
        """
        for failed in resolved.failed_calls:
            error_msg = self._make_error_message(failed.tool_name, failed.error)
            yield ToolResultEvent(
                tool_name=failed.tool_name,
                tool_class=None,
                error=error_msg,
                tool_call_id=failed.call_id,
            )
            stats.tool_calls_failed += 1
            history_append_func(
                LLMMessage.model_validate(
                    APIToolFormatHandler().create_failed_tool_response_message(
                        failed, error_msg
                    )
                )
            )

        for tool_call in resolved.tool_calls:
            yield ToolCallEvent(
                tool_name=tool_call.tool_name,
                tool_class=tool_call.tool_class,
                args=tool_call.validated_args,
                tool_call_id=tool_call.call_id,
            )

            try:
                tool_instance = self.tool_manager.get(tool_call.tool_name)
            except (KeyError, ValueError, AttributeError) as exc:
                error_msg = f"Error getting tool '{tool_call.tool_name}': {exc}"
                yield ToolResultEvent(
                    tool_name=tool_call.tool_name,
                    tool_class=tool_call.tool_class,
                    error=error_msg,
                    tool_call_id=tool_call.call_id,
                )
                history_append_func(
                    self._make_tool_message(
                        tool_call.tool_name, error_msg, tool_call.call_id
                    )
                )
                continue

            decision = await self._should_execute(
                tool_instance, tool_call.validated_args, tool_call.call_id
            )

            if decision.verdict == ToolExecutionResponse.SKIP:
                stats.tool_calls_rejected += 1
                skip_reason = decision.feedback or str(
                    get_user_cancellation_message(
                        CancellationReason.TOOL_SKIPPED, tool_call.tool_name
                    )
                )
                yield ToolResultEvent(
                    tool_name=tool_call.tool_name,
                    tool_class=tool_call.tool_class,
                    skipped=True,
                    skip_reason=skip_reason,
                    tool_call_id=tool_call.call_id,
                )
                history_append_func(
                    self._make_tool_message(
                        tool_call.tool_name, skip_reason, tool_call.call_id
                    )
                )
                continue

            stats.tool_calls_agreed += 1

            try:
                start_time = time.perf_counter()
                result_model = None

                async for item in tool_instance.invoke(
                    ctx=InvokeContext(
                        tool_call_id=tool_call.call_id,
                        approval_callback=self.approval_callback,
                        agent_manager=agent_manager,
                        user_input_callback=user_input_callback,
                    ),
                    **tool_call.args_dict,
                ):
                    if isinstance(item, ToolStreamEvent):
                        yield item
                    else:
                        result_model = item

                duration = time.perf_counter() - start_time

                if result_model is None:
                    raise ToolError("Tool did not yield a result")

                text = "\n".join(
                    f"{k}: {v}" for k, v in result_model.model_dump().items()
                )
                history_append_func(
                    self._make_tool_message(
                        tool_call.tool_name, text, tool_call.call_id
                    )
                )
                yield ToolResultEvent(
                    tool_name=tool_call.tool_name,
                    tool_class=tool_call.tool_class,
                    result=result_model,
                    duration=duration,
                    tool_call_id=tool_call.call_id,
                )

                stats.tool_calls_succeeded += 1

            except asyncio.CancelledError:
                cancel = str(
                    get_user_cancellation_message(CancellationReason.TOOL_INTERRUPTED)
                )
                yield ToolResultEvent(
                    tool_name=tool_call.tool_name,
                    tool_class=tool_call.tool_class,
                    error=cancel,
                    tool_call_id=tool_call.call_id,
                )
                history_append_func(
                    self._make_tool_message(
                        tool_call.tool_name, cancel, tool_call.call_id
                    )
                )
                raise

            except (ToolError, ToolPermissionError) as exc:
                error_msg = f"<{TOOL_ERROR_TAG}>{tool_instance.get_name()} failed: {exc}</{TOOL_ERROR_TAG}>"
                yield ToolResultEvent(
                    tool_name=tool_call.tool_name,
                    tool_class=tool_call.tool_class,
                    error=error_msg,
                    tool_call_id=tool_call.call_id,
                )
                if isinstance(exc, ToolPermissionError):
                    stats.tool_calls_agreed, stats.tool_calls_rejected = (
                        stats.tool_calls_agreed - 1,
                        stats.tool_calls_rejected + 1,
                    )
                else:
                    stats.tool_calls_failed += 1
                history_append_func(
                    self._make_tool_message(
                        tool_call.tool_name, error_msg, tool_call.call_id
                    )
                )
                continue

    async def _should_execute(
        self, tool: BaseTool, args: BaseModel, tool_call_id: str
    ) -> ToolDecision:
        """Check permissions and ask for approval if needed."""
        if self.auto_approve:
            return ToolDecision(verdict=ToolExecutionResponse.EXECUTE)

        allowlist_denylist_result = tool.check_allowlist_denylist(args)
        match allowlist_denylist_result:
            case ToolPermission.ALWAYS:
                return ToolDecision(verdict=ToolExecutionResponse.EXECUTE)
            case ToolPermission.NEVER:
                denylist_patterns = tool.config.denylist
                denylist_str = ", ".join(repr(pattern) for pattern in denylist_patterns)
                return ToolDecision(
                    verdict=ToolExecutionResponse.SKIP,
                    feedback=f"Tool '{tool.get_name()}' blocked by denylist: [{denylist_str}]",
                )

        tool_name = tool.get_name()
        perm = self.tool_manager.get_tool_config(tool_name).permission

        match perm:
            case ToolPermission.ALWAYS:
                return ToolDecision(verdict=ToolExecutionResponse.EXECUTE)
            case ToolPermission.NEVER:
                return ToolDecision(
                    verdict=ToolExecutionResponse.SKIP,
                    feedback=f"Tool '{tool_name}' is permanently disabled",
                )

        return await self._ask_approval(tool_name, args, tool_call_id)

    async def _ask_approval(
        self, tool_name: str, args: BaseModel, tool_call_id: str
    ) -> ToolDecision:
        """Ask user for approval to execute a tool."""
        if not self.approval_callback:
            return ToolDecision(
                verdict=ToolExecutionResponse.SKIP,
                feedback="Tool execution not permitted.",
            )
        if asyncio.iscoroutinefunction(self.approval_callback):
            async_callback = cast(AsyncApprovalCallback, self.approval_callback)
            response, feedback = await async_callback(tool_name, args, tool_call_id)
        else:
            sync_callback = cast(SyncApprovalCallback, self.approval_callback)
            response, feedback = sync_callback(tool_name, args, tool_call_id)

        match response:
            case ApprovalResponse.YES:
                return ToolDecision(
                    verdict=ToolExecutionResponse.EXECUTE, feedback=feedback
                )
            case ApprovalResponse.NO:
                return ToolDecision(
                    verdict=ToolExecutionResponse.SKIP, feedback=feedback
                )

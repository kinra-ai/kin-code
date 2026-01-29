from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from threading import Thread
from uuid import uuid4

from kin_code.core.agents.manager import AgentManager
from kin_code.core.agents.models import AgentProfile, BuiltinAgentName
from kin_code.core.config import VibeConfig
from kin_code.core.conversation_history import ConversationHistory
from kin_code.core.llm.format import APIToolFormatHandler, ResolvedMessage
from kin_code.core.llm.pricing import resolve_context_window, resolve_model_pricing
from kin_code.core.llm.types import BackendLike
from kin_code.core.llm_client import LLMClient
from kin_code.core.middleware import (
    AutoCompactMiddleware,
    ContextWarningMiddleware,
    ConversationContext,
    MiddlewareAction,
    MiddlewarePipeline,
    MiddlewareResult,
    PlanAgentMiddleware,
    PriceLimitMiddleware,
    ResetReason,
    TurnLimitMiddleware,
)
from kin_code.core.prompts import UtilityPrompt
from kin_code.core.session.session_logger import SessionLogger
from kin_code.core.session.session_migration import migrate_sessions_entrypoint
from kin_code.core.skills.manager import SkillManager
from kin_code.core.system_prompt import get_universal_system_prompt
from kin_code.core.tool_runner import ToolRunner
from kin_code.core.tools.base import BaseToolConfig, ToolPermission
from kin_code.core.tools.manager import ToolManager
from kin_code.core.types import (
    AgentStats,
    ApprovalCallback,
    AssistantEvent,
    BaseEvent,
    CompactEndEvent,
    CompactStartEvent,
    LLMChunk,
    LLMMessage,
    LLMUsage,
    ReasoningEvent,
    Role,
    ToolCallEvent,
    ToolResultEvent,
    ToolStreamEvent,
    UserInputCallback,
    UserMessageEvent,
)
from kin_code.core.utils import (
    VIBE_STOP_EVENT_TAG,
    is_user_cancellation_event,
)

# Re-export for backwards compatibility (tests patch this)
from kin_code.setup.onboarding.services.pricing_service import (
    get_model_pricing_sync as _get_model_pricing_sync,
)

# This alias is kept for test compatibility
get_model_pricing_sync = _get_model_pricing_sync


class AgentLoopError(Exception):
    """Base exception for AgentLoop errors."""


class AgentLoopStateError(AgentLoopError):
    """Raised when agent loop is in an invalid state."""


class AgentLoopLLMResponseError(AgentLoopError):
    """Raised when LLM response is malformed or missing expected data."""


class AgentLoop:
    def __init__(
        self,
        config: VibeConfig,
        agent_name: str = BuiltinAgentName.DEFAULT,
        message_observer: Callable[[LLMMessage], None] | None = None,
        max_turns: int | None = None,
        max_price: float | None = None,
        backend: BackendLike | None = None,
        enable_streaming: bool = False,
    ) -> None:
        self._base_config = config
        self._max_turns = max_turns
        self._max_price = max_price

        self.agent_manager = AgentManager(
            lambda: self._base_config, initial_agent=agent_name
        )
        self.tool_manager = ToolManager(lambda: self.config)
        self.skill_manager = SkillManager(lambda: self.config)

        self._backend_override = backend

        self.message_observer = message_observer
        self._last_observed_message_index: int = 0
        self.enable_streaming = enable_streaming
        self.middleware_pipeline = MiddlewarePipeline()
        self._setup_middleware()

        system_prompt = get_universal_system_prompt(
            self.tool_manager, config, self.skill_manager, self.agent_manager
        )
        self.messages: list[LLMMessage] = [
            LLMMessage(role=Role.system, content=system_prompt)
        ]

        if self.message_observer:
            self.message_observer(self.messages[0])
            self._last_observed_message_index = 1

        self.session_id = str(uuid4())
        self.session_logger = SessionLogger(config.session_logging, self.session_id)

        self.approval_callback: ApprovalCallback | None = None
        self.user_input_callback: UserInputCallback | None = None

        # Initialize LLM client
        self.llm_client = LLMClient(
            config=config,
            backend=backend,
            enable_streaming=enable_streaming,
            session_id=self.session_id,
        )

        # Initialize tool runner
        self.tool_runner = ToolRunner(
            tool_manager=self.tool_manager,
            auto_approve=self.config.auto_approve,
        )

        # Start session migration in background
        thread = Thread(
            target=migrate_sessions_entrypoint,
            args=(config.session_logging,),
            daemon=True,
            name="migrate_sessions",
        )
        thread.start()

    @property
    def agent_profile(self) -> AgentProfile:
        return self.agent_manager.active_profile

    @property
    def config(self) -> VibeConfig:
        return self.agent_manager.config

    @property
    def auto_approve(self) -> bool:
        return self.config.auto_approve

    @property
    def stats(self) -> AgentStats:
        return self.llm_client.stats

    @property
    def history(self) -> ConversationHistory:
        """Return a ConversationHistory wrapper for the current messages."""
        return ConversationHistory(self.messages)

    def set_tool_permission(
        self, tool_name: str, permission: ToolPermission, save_permanently: bool = False
    ) -> None:
        if save_permanently:
            VibeConfig.save_updates({
                "tools": {tool_name: {"permission": permission.value}}
            })

        if tool_name not in self.config.tools:
            self.config.tools[tool_name] = BaseToolConfig()

        self.config.tools[tool_name].permission = permission
        self.tool_manager.invalidate_tool(tool_name)

    def _setup_middleware(self) -> None:
        """Configure middleware pipeline for this conversation."""
        self.middleware_pipeline.clear()

        if self._max_turns is not None:
            self.middleware_pipeline.add(TurnLimitMiddleware(self._max_turns))

        if self._max_price is not None:
            self.middleware_pipeline.add(PriceLimitMiddleware(self._max_price))

        max_context = resolve_context_window(self.config)
        if self.config.auto_compact_percent > 0 and max_context > 0:
            hard_ceiling = (
                self.config.auto_compact_threshold
                if self.config.auto_compact_threshold > 0
                else None
            )
            self.middleware_pipeline.add(
                AutoCompactMiddleware(
                    threshold_percent=self.config.auto_compact_percent,
                    max_context=max_context,
                    hard_ceiling=hard_ceiling,
                )
            )
            if self.config.context_warnings:
                self.middleware_pipeline.add(ContextWarningMiddleware(0.5, max_context))

        self.middleware_pipeline.add(PlanAgentMiddleware(lambda: self.agent_profile))

    async def _handle_middleware_result(
        self, result: MiddlewareResult
    ) -> AsyncGenerator[BaseEvent]:
        match result.action:
            case MiddlewareAction.STOP:
                yield AssistantEvent(
                    content=f"<{VIBE_STOP_EVENT_TAG}>{result.reason}</{VIBE_STOP_EVENT_TAG}>",
                    stopped_by_middleware=True,
                )

            case MiddlewareAction.INJECT_MESSAGE:
                if result.message and len(self.messages) > 0:
                    last_msg = self.messages[-1]
                    if last_msg.content:
                        last_msg.content += f"\n\n{result.message}"
                    else:
                        last_msg.content = result.message

            case MiddlewareAction.COMPACT:
                old_tokens = result.metadata.get(
                    "old_tokens", self.stats.context_tokens
                )
                threshold = result.metadata.get(
                    "threshold", self.config.auto_compact_threshold
                )
                tool_call_id = str(uuid4())

                yield CompactStartEvent(
                    tool_call_id=tool_call_id,
                    current_context_tokens=old_tokens,
                    threshold=threshold,
                )

                summary = await self.compact()

                yield CompactEndEvent(
                    tool_call_id=tool_call_id,
                    old_context_tokens=old_tokens,
                    new_context_tokens=self.stats.context_tokens,
                    summary_length=len(summary),
                )

            case MiddlewareAction.CONTINUE:
                pass

    def _get_context(self) -> ConversationContext:
        return ConversationContext(
            messages=self.messages, stats=self.stats, config=self.config
        )

    async def act(self, msg: str) -> AsyncGenerator[BaseEvent]:
        self.history.clean()
        async for event in self._conversation_loop(msg):
            yield event

    async def _conversation_loop(self, user_msg: str) -> AsyncGenerator[BaseEvent]:
        user_message = LLMMessage(role=Role.user, content=user_msg)
        self.messages.append(user_message)
        self.stats.steps += 1

        if user_message.message_id is None:
            raise AgentLoopError("User message must have a message_id")

        yield UserMessageEvent(content=user_msg, message_id=user_message.message_id)

        try:
            should_break_loop = False
            while not should_break_loop:
                result = await self.middleware_pipeline.run_before_turn(
                    self._get_context()
                )
                async for event in self._handle_middleware_result(result):
                    yield event

                if result.action == MiddlewareAction.STOP:
                    return

                self.stats.steps += 1
                user_cancelled = False
                async for event in self._perform_llm_turn():
                    if is_user_cancellation_event(event):
                        user_cancelled = True
                    yield event

                last_message = self.messages[-1]
                should_break_loop = last_message.role != Role.tool

                self._flush_new_messages()

                if user_cancelled:
                    return

                after_result = await self.middleware_pipeline.run_after_turn(
                    self._get_context()
                )
                async for event in self._handle_middleware_result(after_result):
                    yield event

                if after_result.action == MiddlewareAction.STOP:
                    return

        finally:
            self._flush_new_messages()
            await self._save_session()

    async def _save_session(self) -> None:
        """Centralized session logging."""
        await self.session_logger.save_interaction(
            self.messages,
            self.stats,
            self._base_config,
            self.tool_manager,
            self.agent_profile,
        )

    async def _perform_llm_turn(self) -> AsyncGenerator[BaseEvent, None]:
        if self.enable_streaming:
            async for event in self._stream_assistant_events():
                yield event
        else:
            assistant_event = await self._get_assistant_event()
            if assistant_event.content:
                yield assistant_event

        last_message = self.messages[-1]

        format_handler = APIToolFormatHandler()
        parsed = format_handler.parse_message(last_message)
        resolved = format_handler.resolve_tool_calls(parsed, self.tool_manager)

        if not resolved.tool_calls and not resolved.failed_calls:
            return

        async for event in self._handle_tool_calls(resolved):
            yield event

    async def _stream_assistant_events(
        self,
    ) -> AsyncGenerator[AssistantEvent | ReasoningEvent]:
        content_buffer = ""
        reasoning_buffer = ""
        chunks_with_content = 0
        chunks_with_reasoning = 0
        message_id: str | None = None
        BATCH_SIZE = 5

        # Aggregate the full message like the original code did
        chunk_agg = LLMChunk(message=LLMMessage(role=Role.assistant))

        async for chunk in self.llm_client.chat_streaming(
            messages=self.messages,
            tool_manager=self.tool_manager,
        ):
            chunk_agg += chunk

            if message_id is None:
                message_id = chunk.message.message_id

            if chunk.message.reasoning_content:
                if content_buffer:
                    yield AssistantEvent(content=content_buffer, message_id=message_id)
                    content_buffer = ""
                    chunks_with_content = 0

                reasoning_buffer += chunk.message.reasoning_content
                chunks_with_reasoning += 1

                if chunks_with_reasoning >= BATCH_SIZE:
                    yield ReasoningEvent(
                        content=reasoning_buffer, message_id=message_id
                    )
                    reasoning_buffer = ""
                    chunks_with_reasoning = 0

            if chunk.message.content:
                if reasoning_buffer:
                    yield ReasoningEvent(
                        content=reasoning_buffer, message_id=message_id
                    )
                    reasoning_buffer = ""
                    chunks_with_reasoning = 0

                content_buffer += chunk.message.content
                chunks_with_content += 1

                if chunks_with_content >= BATCH_SIZE:
                    if content_buffer.strip():
                        yield AssistantEvent(
                            content=content_buffer, message_id=message_id
                        )
                    content_buffer = ""
                    chunks_with_content = 0

        if reasoning_buffer:
            yield ReasoningEvent(content=reasoning_buffer, message_id=message_id)

        if content_buffer.strip():
            yield AssistantEvent(content=content_buffer, message_id=message_id)

        # Append the aggregated message to history (like original code did)
        self.messages.append(chunk_agg.message)

    async def _get_assistant_event(self) -> AssistantEvent:
        result = await self.llm_client.chat(
            messages=self.messages,
            tool_manager=self.tool_manager,
        )
        self.messages.append(result.message)
        return AssistantEvent(
            content=result.message.content or "",
            message_id=result.message.message_id,
        )

    async def _handle_tool_calls(
        self, resolved: ResolvedMessage
    ) -> AsyncGenerator[ToolCallEvent | ToolResultEvent | ToolStreamEvent]:
        async for event in self.tool_runner.handle_tool_calls(
            resolved=resolved,
            agent_manager=self.agent_manager,
            user_input_callback=self.user_input_callback,
            stats=self.stats,
            history_append_func=self.messages.append,
        ):
            yield event

    def _flush_new_messages(self) -> None:
        if not self.message_observer:
            return

        if self._last_observed_message_index >= len(self.messages):
            return

        for msg in self.messages[self._last_observed_message_index :]:
            self.message_observer(msg)
        self._last_observed_message_index = len(self.messages)

    def set_approval_callback(self, callback: ApprovalCallback) -> None:
        self.tool_runner.set_approval_callback(callback)

    def set_user_input_callback(self, callback: UserInputCallback) -> None:
        self.user_input_callback = callback

    def _reset_session(self) -> None:
        self.session_id = str(uuid4())
        self.session_logger.reset_session(self.session_id)
        self.llm_client.session_id = self.session_id

    async def clear_history(self) -> None:
        await self._save_session()
        self.messages = self.messages[:1]

        self.llm_client.stats = AgentStats()
        self.llm_client.stats.trigger_listeners()

        input_price, output_price = resolve_model_pricing(self.config)
        self.llm_client.stats.update_pricing(input_price, output_price)
        self.llm_client.stats.max_context_window = resolve_context_window(self.config)

        self.middleware_pipeline.reset()
        self.tool_manager.reset_all()
        self._reset_session()

    async def compact(self) -> str:
        """Compact the conversation history."""
        try:
            self.history.clean()
            await self._save_session()

            summary_request = UtilityPrompt.COMPACT.read()
            self.messages.append(LLMMessage(role=Role.user, content=summary_request))
            self.stats.steps += 1

            summary_result = await self.llm_client.chat(
                messages=self.messages,
                tool_manager=self.tool_manager,
            )
            summary_content = summary_result.message.content or ""

            system_message = self.messages[0]
            summary_message = LLMMessage(role=Role.user, content=summary_content)
            self.messages = [system_message, summary_message]

            actual_context_tokens = await self.llm_client.count_tokens(
                messages=self.messages,
                tool_manager=self.tool_manager,
            )
            self.stats.context_tokens = actual_context_tokens

            self._reset_session()
            await self._save_session()

            self.middleware_pipeline.reset(reset_reason=ResetReason.COMPACT)

            return summary_content or ""

        except Exception:
            await self._save_session()
            raise

    async def switch_agent(self, agent_name: str) -> None:
        if agent_name == self.agent_profile.name:
            return
        self.agent_manager.switch_profile(agent_name)
        await self.reload_with_initial_messages()

    async def reload_with_initial_messages(
        self,
        base_config: VibeConfig | None = None,
        max_turns: int | None = None,
        max_price: float | None = None,
    ) -> None:
        await self._save_session()

        if base_config is not None:
            self._base_config = base_config
            self.agent_manager.invalidate_config()

        self.llm_client.reset_backend()

        if max_turns is not None:
            self._max_turns = max_turns
        if max_price is not None:
            self._max_price = max_price

        self.tool_manager = ToolManager(lambda: self.config)
        self.skill_manager = SkillManager(lambda: self.config)

        # Update tool runner with new tool manager
        self.tool_runner = ToolRunner(
            tool_manager=self.tool_manager,
            auto_approve=self.config.auto_approve,
        )

        new_system_prompt = get_universal_system_prompt(
            self.tool_manager, self.config, self.skill_manager, self.agent_manager
        )

        self.history.replace_system_message(new_system_prompt)

        if len(self.messages) == 1:
            self.stats.reset_context_state()

        input_price, output_price = resolve_model_pricing(self.config)
        self.stats.update_pricing(input_price, output_price)
        self.stats.max_context_window = resolve_context_window(self.config)

        self._last_observed_message_index = 0

        self._setup_middleware()

        if self.message_observer:
            for msg in self.messages:
                self.message_observer(msg)
            self._last_observed_message_index = len(self.messages)

        await self._save_session()

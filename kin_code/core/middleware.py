from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any, Protocol

from kin_code.core.agents import AgentProfile
from kin_code.core.agents.models import BuiltinAgentName
from kin_code.core.utils import VIBE_WARNING_TAG

if TYPE_CHECKING:
    from kin_code.core.config import VibeConfig
    from kin_code.core.types import AgentStats, LLMMessage


class MiddlewareAction(StrEnum):
    CONTINUE = auto()
    STOP = auto()
    COMPACT = auto()
    INJECT_MESSAGE = auto()


class ResetReason(StrEnum):
    STOP = auto()
    COMPACT = auto()


@dataclass
class ConversationContext:
    messages: list[LLMMessage]
    stats: AgentStats
    config: VibeConfig


@dataclass
class MiddlewareResult:
    action: MiddlewareAction = MiddlewareAction.CONTINUE
    message: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ConversationMiddleware(Protocol):
    """Protocol for middleware that intercepts conversation turns.

    Middleware can inspect and modify conversation flow by returning actions
    such as STOP, COMPACT, or INJECT_MESSAGE. Implementations are called in
    pipeline order, and the first non-CONTINUE action takes effect.

    The middleware lifecycle is:

    1. ``before_turn()`` called before LLM request
    2. LLM processes and responds
    3. ``after_turn()`` called after response received
    4. ``reset()`` called when conversation ends or compacts

    Example:
        Implementing a custom middleware::

            from kin_code.core.middleware import (
                ConversationMiddleware,
                ConversationContext,
                MiddlewareResult,
                MiddlewareAction,
                ResetReason,
            )

            class TokenBudgetMiddleware:
                '''Stop conversation when token budget is exhausted.'''

                def __init__(self, max_tokens: int) -> None:
                    self.max_tokens = max_tokens
                    self.tokens_used = 0

                async def before_turn(
                    self, context: ConversationContext
                ) -> MiddlewareResult:
                    # Check budget before each turn
                    if self.tokens_used >= self.max_tokens:
                        return MiddlewareResult(
                            action=MiddlewareAction.STOP,
                            reason=f"Token budget exhausted: {self.tokens_used}"
                        )
                    return MiddlewareResult()

                async def after_turn(
                    self, context: ConversationContext
                ) -> MiddlewareResult:
                    # Track token usage after turn
                    self.tokens_used = context.stats.total_tokens
                    return MiddlewareResult()

                def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
                    # Reset counter on conversation end
                    if reset_reason == ResetReason.STOP:
                        self.tokens_used = 0

        Injecting messages::

            class ReminderMiddleware:
                '''Inject periodic reminders into conversation.'''

                def __init__(self, reminder: str, every_n_turns: int = 5) -> None:
                    self.reminder = reminder
                    self.every_n_turns = every_n_turns

                async def before_turn(
                    self, context: ConversationContext
                ) -> MiddlewareResult:
                    if context.stats.steps % self.every_n_turns == 0:
                        return MiddlewareResult(
                            action=MiddlewareAction.INJECT_MESSAGE,
                            message=self.reminder
                        )
                    return MiddlewareResult()

                async def after_turn(
                    self, context: ConversationContext
                ) -> MiddlewareResult:
                    return MiddlewareResult()

                def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
                    pass

        Adding to pipeline::

            from kin_code.core.middleware import MiddlewarePipeline

            pipeline = MiddlewarePipeline()
            pipeline.add(TokenBudgetMiddleware(max_tokens=100_000))
            pipeline.add(ReminderMiddleware("Remember to test your changes!"))

            # Run pipeline before turn
            result = await pipeline.run_before_turn(context)
            match result.action:
                case MiddlewareAction.STOP:
                    print(f"Stopping: {result.reason}")
                case MiddlewareAction.COMPACT:
                    print("Triggering compaction")
                case MiddlewareAction.INJECT_MESSAGE:
                    messages.append(result.message)
                case MiddlewareAction.CONTINUE:
                    pass  # Proceed normally
    """

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        """Called before each conversation turn.

        This method is invoked before the LLM request is sent. Middleware can:
        - Return CONTINUE to proceed normally
        - Return STOP to end the conversation
        - Return COMPACT to trigger context compaction
        - Return INJECT_MESSAGE to add a message to the context

        Args:
            context: Current conversation state containing:
                - messages: List of conversation messages so far
                - stats: AgentStats with token counts, costs, step count
                - config: Current VibeConfig settings

        Returns:
            MiddlewareResult with:
                - action: The action to take (CONTINUE, STOP, COMPACT, INJECT_MESSAGE)
                - message: Text to inject (only for INJECT_MESSAGE)
                - reason: Human-readable explanation (for STOP)
                - metadata: Additional data for the action
        """
        ...

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        """Called after each conversation turn.

        This method is invoked after the LLM response is received and processed.
        Middleware can analyze the response and decide to stop or compact.
        Note: INJECT_MESSAGE is not allowed in after_turn.

        Args:
            context: Updated conversation state including the latest response.
                - messages: Updated with assistant response and tool results
                - stats: Updated token counts and costs
                - config: Current VibeConfig settings

        Returns:
            MiddlewareResult with action (CONTINUE, STOP, or COMPACT only).
        """
        ...

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        """Reset middleware state when conversation ends or compacts.

        Called to clear any accumulated state. The reason indicates whether
        the conversation is ending (STOP) or being compacted (COMPACT).
        Middleware may want to preserve some state across compactions.

        Args:
            reset_reason: Why the reset is occurring:
                - STOP: Conversation is ending, clear all state
                - COMPACT: Context is being compacted, may preserve some state
        """
        ...


class TurnLimitMiddleware:
    def __init__(self, max_turns: int) -> None:
        """Initialize turn limit middleware.

        Args:
            max_turns: Maximum number of turns allowed before stopping.
        """
        self.max_turns = max_turns

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if context.stats.steps - 1 >= self.max_turns:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Turn limit of {self.max_turns} reached",
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        _ = context
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        _ = reset_reason


class PriceLimitMiddleware:
    def __init__(self, max_price: float) -> None:
        """Initialize price limit middleware.

        Args:
            max_price: Maximum session cost in dollars before stopping.
        """
        self.max_price = max_price

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if context.stats.session_cost > self.max_price:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Price limit exceeded: ${context.stats.session_cost:.4f} > ${self.max_price:.2f}",
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        _ = context
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        _ = reset_reason


class AutoCompactMiddleware:
    def __init__(
        self,
        threshold_percent: float,
        max_context: int,
        hard_ceiling: int | None = None,
    ) -> None:
        """Initialize auto-compact middleware.

        Args:
            threshold_percent: Percentage of max_context that triggers compaction
                (e.g., 0.8 for 80%).
            max_context: Maximum context window size in tokens.
            hard_ceiling: Optional absolute token limit that overrides the
                percentage calculation if lower.
        """
        self.threshold_percent = threshold_percent
        self.max_context = max_context
        self.hard_ceiling = hard_ceiling

    def _get_threshold(self) -> int:
        """Calculate effective threshold from percentage of context window."""
        percent_threshold = int(self.max_context * self.threshold_percent)
        if self.hard_ceiling is not None:
            return min(percent_threshold, self.hard_ceiling)
        return percent_threshold

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        threshold = self._get_threshold()
        if context.stats.context_tokens >= threshold:
            return MiddlewareResult(
                action=MiddlewareAction.COMPACT,
                metadata={
                    "old_tokens": context.stats.context_tokens,
                    "threshold": threshold,
                },
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        _ = context
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        _ = reset_reason


class ContextWarningMiddleware:
    def __init__(
        self, threshold_percent: float = 0.5, max_context: int | None = None
    ) -> None:
        """Initialize context warning middleware.

        Args:
            threshold_percent: Percentage of max_context that triggers a warning
                (e.g., 0.5 for 50%). Defaults to 0.5.
            max_context: Maximum context window size in tokens. If None, no
                warning is issued.
        """
        self.threshold_percent = threshold_percent
        self.max_context = max_context
        self.has_warned = False

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if self.has_warned:
            return MiddlewareResult()

        max_context = self.max_context
        if max_context is None:
            return MiddlewareResult()

        if context.stats.context_tokens >= max_context * self.threshold_percent:
            self.has_warned = True

            percentage_used = (context.stats.context_tokens / max_context) * 100
            warning_msg = f"<{VIBE_WARNING_TAG}>You have used {percentage_used:.0f}% of your total context ({context.stats.context_tokens:,}/{max_context:,} tokens)</{VIBE_WARNING_TAG}>"

            return MiddlewareResult(
                action=MiddlewareAction.INJECT_MESSAGE, message=warning_msg
            )

        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        _ = context
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        _ = reset_reason
        self.has_warned = False


PLAN_AGENT_REMINDER = f"""<{VIBE_WARNING_TAG}>Plan mode is active. The user indicated that they do not want you to execute yet -- you MUST NOT make any edits, run any non-readonly tools (including changing configs or making commits), or otherwise make any changes to the system. This supersedes any other instructions you have received (for example, to make edits). Instead, you should:
1. Answer the user's query comprehensively
2. When you're done researching, present your plan by giving the full plan and not doing further tool calls to return input to the user. Do NOT make any file changes or run any tools that modify the system state in any way until the user has confirmed the plan.</{VIBE_WARNING_TAG}>"""


class PlanAgentMiddleware:
    def __init__(
        self,
        profile_getter: Callable[[], AgentProfile],
        reminder: str = PLAN_AGENT_REMINDER,
    ) -> None:
        """Initialize plan agent middleware.

        Injects a reminder message before each turn when the Plan agent is active,
        instructing the model to research and plan without making changes.

        Args:
            profile_getter: Callable that returns the current agent profile.
            reminder: Message to inject when Plan agent is active.
        """
        self._profile_getter = profile_getter
        self.reminder = reminder

    def _is_plan_agent(self) -> bool:
        return self._profile_getter().name == BuiltinAgentName.PLAN

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        _ = context
        if not self._is_plan_agent():
            return MiddlewareResult()
        return MiddlewareResult(
            action=MiddlewareAction.INJECT_MESSAGE, message=self.reminder
        )

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        _ = context
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        _ = reset_reason


class MiddlewarePipeline:
    def __init__(self) -> None:
        self.middlewares: list[ConversationMiddleware] = []

    def add(self, middleware: ConversationMiddleware) -> MiddlewarePipeline:
        self.middlewares.append(middleware)
        return self

    def clear(self) -> None:
        self.middlewares.clear()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        for mw in self.middlewares:
            mw.reset(reset_reason)

    async def run_before_turn(self, context: ConversationContext) -> MiddlewareResult:
        messages_to_inject = []

        for mw in self.middlewares:
            result = await mw.before_turn(context)
            if result.action == MiddlewareAction.INJECT_MESSAGE and result.message:
                messages_to_inject.append(result.message)
            elif result.action in {MiddlewareAction.STOP, MiddlewareAction.COMPACT}:
                return result
        if messages_to_inject:
            combined_message = "\n\n".join(messages_to_inject)
            return MiddlewareResult(
                action=MiddlewareAction.INJECT_MESSAGE, message=combined_message
            )

        return MiddlewareResult()

    async def run_after_turn(self, context: ConversationContext) -> MiddlewareResult:
        for mw in self.middlewares:
            result = await mw.after_turn(context)
            if result.action == MiddlewareAction.INJECT_MESSAGE:
                raise ValueError(
                    f"INJECT_MESSAGE not allowed in after_turn (from {type(mw).__name__})"
                )
            if result.action in {MiddlewareAction.STOP, MiddlewareAction.COMPACT}:
                return result

        return MiddlewareResult()

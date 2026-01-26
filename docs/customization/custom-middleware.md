# Custom Middleware

Build middleware to control conversation flow and enforce custom rules.

## Overview

Middleware intercepts the conversation flow before and after each LLM turn. Use middleware to:

- **Enforce limits** - Turn counts, costs, token usage
- **Inject messages** - Add reminders, warnings, or context
- **Trigger actions** - Context compaction, mode switches
- **Stop execution** - Halt when conditions are met

## Middleware Protocol

Implement the `ConversationMiddleware` protocol:

```python
from kin_code.core.middleware import (
    ConversationMiddleware,
    ConversationContext,
    MiddlewareResult,
    MiddlewareAction,
    ResetReason,
)

class MyMiddleware:
    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        """Called before each LLM call."""
        return MiddlewareResult()  # Continue normally

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        """Called after each LLM response."""
        return MiddlewareResult()  # Continue normally

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        """Reset internal state when conversation is cleared or compacted."""
        pass
```

## Context Structure

The `ConversationContext` provides conversation state:

```python
from dataclasses import dataclass
from kin_code.core.types import LLMMessage, AgentStats
from kin_code.core.config import KinConfig

@dataclass
class ConversationContext:
    messages: list[LLMMessage]  # Full conversation history
    stats: AgentStats           # Token usage, costs, timing
    config: KinConfig           # Current configuration
```

### Available Statistics

Access through `context.stats`:

| Field | Type | Description |
|-------|------|-------------|
| `steps` | int | Number of LLM turns |
| `session_prompt_tokens` | int | Total input tokens |
| `session_completion_tokens` | int | Total output tokens |
| `session_cost` | float | Estimated cost in USD |
| `context_tokens` | int | Current context size |
| `tool_calls_succeeded` | int | Successful tool executions |
| `tool_calls_failed` | int | Failed tool executions |

## Middleware Actions

Return a `MiddlewareResult` with one of these actions:

### CONTINUE (Default)

Proceed with normal execution:

```python
return MiddlewareResult()  # action defaults to CONTINUE
```

### STOP

Halt execution with a reason:

```python
return MiddlewareResult(
    action=MiddlewareAction.STOP,
    reason="Budget limit reached",
)
```

### COMPACT

Trigger context compaction:

```python
return MiddlewareResult(
    action=MiddlewareAction.COMPACT,
    metadata={"threshold": 100000},
)
```

### INJECT_MESSAGE

Add content to the conversation (only in `before_turn`):

```python
return MiddlewareResult(
    action=MiddlewareAction.INJECT_MESSAGE,
    message="Remember: You are in read-only mode.",
)
```

## Built-in Middleware

Kin Code includes several middleware for common use cases.

### TurnLimitMiddleware

Stop after N turns:

```python
from kin_code.core.middleware import TurnLimitMiddleware

middleware = TurnLimitMiddleware(max_turns=10)
```

### PriceLimitMiddleware

Stop when cost exceeds threshold:

```python
from kin_code.core.middleware import PriceLimitMiddleware

middleware = PriceLimitMiddleware(max_price=1.0)  # $1.00 USD
```

### AutoCompactMiddleware

Trigger compaction at token threshold:

```python
from kin_code.core.middleware import AutoCompactMiddleware

middleware = AutoCompactMiddleware(threshold=150000)  # tokens
```

### ContextWarningMiddleware

Warn when approaching context limit:

```python
from kin_code.core.middleware import ContextWarningMiddleware

middleware = ContextWarningMiddleware(
    threshold_percent=0.5,  # Warn at 50% usage
    max_context=200000,     # Total context window
)
```

### PlanModeMiddleware

Enforce read-only behavior in plan mode:

```python
from kin_code.core.middleware import PlanModeMiddleware
from kin_code.core.modes import AgentMode

middleware = PlanModeMiddleware(
    mode_getter=lambda: AgentMode.PLAN,
)
```

## Custom Middleware Examples

### Usage Logger

Log each turn to a file:

```python
from pathlib import Path
from datetime import datetime
from kin_code.core.middleware import (
    ConversationContext,
    MiddlewareResult,
    ResetReason,
)

class UsageLoggerMiddleware:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.session_start = datetime.now()

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        with self.log_path.open("a") as f:
            f.write(
                f"{datetime.now().isoformat()} | "
                f"Turn {context.stats.steps} | "
                f"Tokens: {context.stats.context_tokens} | "
                f"Cost: ${context.stats.session_cost:.4f}\n"
            )
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        self.session_start = datetime.now()
```

### Rate Limiter

Limit requests per minute:

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta
from kin_code.core.middleware import (
    ConversationContext,
    MiddlewareResult,
    MiddlewareAction,
    ResetReason,
)

class RateLimiterMiddleware:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: deque[datetime] = deque()

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        now = datetime.now()

        # Remove old requests outside the window
        while self.requests and now - self.requests[0] > self.window:
            self.requests.popleft()

        # Check rate limit
        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] + self.window - now).seconds
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Rate limit exceeded. Try again in {wait_time}s",
            )

        self.requests.append(now)
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        self.requests.clear()
```

### Topic Guard

Ensure conversation stays on topic:

```python
from kin_code.core.middleware import (
    ConversationContext,
    MiddlewareResult,
    MiddlewareAction,
    ResetReason,
)

class TopicGuardMiddleware:
    def __init__(self, topic: str, reminder_interval: int = 5):
        self.topic = topic
        self.reminder_interval = reminder_interval
        self.turns_since_reminder = 0

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        self.turns_since_reminder += 1

        if self.turns_since_reminder >= self.reminder_interval:
            self.turns_since_reminder = 0
            return MiddlewareResult(
                action=MiddlewareAction.INJECT_MESSAGE,
                message=f"Reminder: Focus on {self.topic}. Stay on task.",
            )

        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        self.turns_since_reminder = 0
```

### Multi-Condition Stopper

Stop on any of multiple conditions:

```python
from kin_code.core.middleware import (
    ConversationContext,
    MiddlewareResult,
    MiddlewareAction,
    ResetReason,
)

class MultiConditionStopperMiddleware:
    def __init__(
        self,
        max_turns: int | None = None,
        max_tokens: int | None = None,
        max_cost: float | None = None,
        max_tool_failures: int | None = None,
    ):
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.max_tool_failures = max_tool_failures

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        stats = context.stats

        if self.max_turns and stats.steps >= self.max_turns:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Turn limit ({self.max_turns}) reached",
            )

        if self.max_tokens and stats.session_total_llm_tokens >= self.max_tokens:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Token limit ({self.max_tokens}) reached",
            )

        if self.max_cost and stats.session_cost >= self.max_cost:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Cost limit (${self.max_cost:.2f}) reached",
            )

        if self.max_tool_failures and stats.tool_calls_failed >= self.max_tool_failures:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Too many tool failures ({stats.tool_calls_failed})",
            )

        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
        pass
```

## Pipeline Integration

### Adding Middleware to Agent

```python
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig

config = KinConfig.load()
agent = Agent(config)

# Add custom middleware
agent.middleware_pipeline.add(UsageLoggerMiddleware(Path("usage.log")))
agent.middleware_pipeline.add(RateLimiterMiddleware(max_requests=20))
```

### Middleware Order

Middleware executes in the order added. Order matters for:

1. **Message injection** - Messages are combined from all middleware
2. **Early exit** - First STOP or COMPACT action wins
3. **State dependencies** - Later middleware sees earlier state changes

```python
# Recommended order:
pipeline.add(RateLimiterMiddleware())      # Check rate limit first
pipeline.add(PriceLimitMiddleware(1.0))    # Then check budget
pipeline.add(TurnLimitMiddleware(10))      # Then check turns
pipeline.add(TopicGuardMiddleware("bugs")) # Then inject reminders
pipeline.add(UsageLoggerMiddleware(path))  # Finally log everything
```

### Clearing and Resetting

```python
# Remove all middleware
agent.middleware_pipeline.clear()

# Reset middleware state (called on conversation clear/compact)
agent.middleware_pipeline.reset(ResetReason.STOP)
```

## Reset Reasons

When `reset()` is called, the reason indicates why:

| Reason | Description |
|--------|-------------|
| `ResetReason.STOP` | Conversation was stopped or cleared |
| `ResetReason.COMPACT` | Context was compacted |

Use this to preserve or reset state appropriately:

```python
def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None:
    match reset_reason:
        case ResetReason.STOP:
            # Full reset - new conversation
            self.turn_count = 0
            self.total_cost = 0.0
        case ResetReason.COMPACT:
            # Partial reset - preserve cumulative stats
            self.turn_count = 0
            # Keep total_cost unchanged
```

## Best Practices

1. **Keep middleware stateless when possible** - Easier to reason about and test
2. **Use reset() properly** - Clean up state based on reset reason
3. **Return early** - Check conditions and return quickly
4. **Avoid side effects in before_turn** - Save logging/metrics for after_turn
5. **Document behavior** - Explain what your middleware does and when
6. **Test thoroughly** - Cover all action paths and edge cases

## Related Documentation

- [Architecture Overview](../architecture/overview.md) - How middleware fits in the system
- [Python API](../api/python-api.md) - Programmatic usage patterns
- [Custom Tools](./custom-tools.md) - Build your own tools

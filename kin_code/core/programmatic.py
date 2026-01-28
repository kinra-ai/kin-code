from __future__ import annotations

import asyncio

from kin_code.core.agent_loop import AgentLoop
from kin_code.core.agents.models import BuiltinAgentName
from kin_code.core.config import VibeConfig
from kin_code.core.output_formatters import create_formatter
from kin_code.core.types import AssistantEvent, LLMMessage, OutputFormat, Role
from kin_code.core.utils import ConversationLimitException, logger


def run_programmatic(
    config: VibeConfig,
    prompt: str,
    max_turns: int | None = None,
    max_price: float | None = None,
    output_format: OutputFormat = OutputFormat.TEXT,
    previous_messages: list[LLMMessage] | None = None,
    agent_name: str = BuiltinAgentName.AUTO_APPROVE,
) -> str | None:
    """Execute an agent loop programmatically without interactive CLI.

    Runs a complete agent conversation synchronously, processing the prompt
    through the agent loop and collecting formatted output.

    Args:
        config: Application configuration containing LLM and tool settings.
        prompt: User message to send to the agent.
        max_turns: Maximum number of conversation turns before stopping.
        max_price: Maximum cost in dollars before stopping.
        output_format: Output format for results (text, JSON, or streaming JSON).
        previous_messages: Optional conversation history to resume from.
        agent_name: Name of the agent profile to use.

    Returns:
        Formatted response string, or None if the formatter handles output directly.

    Raises:
        ConversationLimitException: When agent is stopped by middleware limits.
    """
    formatter = create_formatter(output_format)

    agent_loop = AgentLoop(
        config,
        agent_name=agent_name,
        message_observer=formatter.on_message_added,
        max_turns=max_turns,
        max_price=max_price,
        enable_streaming=False,
    )
    logger.info("USER: %s", prompt)

    async def _async_run() -> str | None:
        if previous_messages:
            non_system_messages = [
                msg for msg in previous_messages if not (msg.role == Role.system)
            ]
            agent_loop.messages.extend(non_system_messages)
            logger.info(
                "Loaded %d messages from previous session", len(non_system_messages)
            )

        async for event in agent_loop.act(prompt):
            formatter.on_event(event)
            if isinstance(event, AssistantEvent) and event.stopped_by_middleware:
                raise ConversationLimitException(event.content)

        return formatter.finalize()

    return asyncio.run(_async_run())

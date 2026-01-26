"""Programmatic entry point for non-interactive agent execution.

This module provides the main interface for running Kin Code agents in automated,
non-interactive contexts such as scripts, services, or batch processing. It handles
the full lifecycle of executing a prompt and returning the result, with support for
conversation continuity, cost/turn limits, and multiple output formats.

The programmatic interface defaults to AUTO_APPROVE mode for automation use cases,
but can be configured with any mode. It integrates with the middleware system to
enforce limits and properly surfaces errors as exceptions.

Key Features:
    - Single-function entry point for programmatic execution
    - Support for conversation continuity via previous_messages
    - Built-in cost and turn limiting with middleware
    - Multiple output formats (TEXT, JSON, STREAMING)
    - Automatic async/sync bridging with asyncio.run()

Typical Usage:
    config = KinConfig.load()
    result = run_programmatic(
        config=config,
        prompt="Analyze this codebase",
        max_turns=5,
        max_price=0.50,
        output_format=OutputFormat.TEXT,
    )
    print(result)

    # Continue conversation
    messages = agent.messages  # Save from previous run
    result = run_programmatic(
        config=config,
        prompt="What about the tests?",
        previous_messages=messages,
    )
"""

from __future__ import annotations

import asyncio

from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig
from kin_code.core.modes import AgentMode
from kin_code.core.output_formatters import create_formatter
from kin_code.core.types import AssistantEvent, LLMMessage, OutputFormat, Role
from kin_code.core.utils import ConversationLimitException, logger


def run_programmatic(
    config: KinConfig,
    prompt: str,
    max_turns: int | None = None,
    max_price: float | None = None,
    output_format: OutputFormat = OutputFormat.TEXT,
    previous_messages: list[LLMMessage] | None = None,
    mode: AgentMode = AgentMode.AUTO_APPROVE,
) -> str | None:
    """Run in programmatic mode: execute prompt and return the assistant response.

    Args:
        config: Configuration for the Vibe agent
        prompt: The user prompt to process
        max_turns: Maximum number of assistant turns (LLM calls) to allow
        max_price: Maximum cost in dollars before stopping
        output_format: Format for the output
        previous_messages: Optional messages from a previous session to continue
        mode: Operational mode (defaults to AUTO_APPROVE for programmatic use)

    Returns:
        The final assistant response text, or None if no response
    """
    formatter = create_formatter(output_format)

    agent = Agent(
        config,
        mode=mode,
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
            agent.messages.extend(non_system_messages)
            logger.info(
                "Loaded %d messages from previous session", len(non_system_messages)
            )

        async for event in agent.act(prompt):
            formatter.on_event(event)
            if isinstance(event, AssistantEvent) and event.stopped_by_middleware:
                raise ConversationLimitException(event.content)

        return formatter.finalize()

    return asyncio.run(_async_run())

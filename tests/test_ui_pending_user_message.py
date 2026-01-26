from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Callable
import time
from types import SimpleNamespace

import pytest

from kin_code.cli.textual_ui.app import KinApp
from kin_code.cli.textual_ui.widgets.chat_input.container import ChatInputContainer
from kin_code.cli.textual_ui.widgets.messages import InterruptMessage, UserMessage
from kin_code.core.agent import Agent
from kin_code.core.config import KinConfig, SessionLoggingConfig
from kin_code.core.types import BaseEvent


async def _wait_for(
    pilot, condition: Callable[[], object | None], timeout: float = 3.0
) -> object | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = condition()
        if result:
            return result
        await pilot.pause(0.05)
    return None


class StubAgent(Agent):
    def __init__(self) -> None:
        self.messages: list = []
        self.stats = SimpleNamespace(context_tokens=0)
        self.approval_callback = None

    async def initialize(self) -> None:
        return

    async def act(self, msg: str) -> AsyncGenerator[BaseEvent]:
        if False:
            yield msg


@pytest.fixture
def kin_config() -> KinConfig:
    return KinConfig(
        session_logging=SessionLoggingConfig(enabled=False), enable_update_checks=False
    )


@pytest.fixture
def kin_app(kin_config: KinConfig) -> KinApp:
    return KinApp(config=kin_config)


def _patch_delayed_init(
    monkeypatch: pytest.MonkeyPatch, init_event: asyncio.Event
) -> None:
    async def _fake_initialize(self: KinApp) -> None:
        if self.agent or self._agent_initializing:
            return

        self._agent_initializing = True
        try:
            await init_event.wait()
            self.agent = StubAgent()
        except asyncio.CancelledError:
            self.agent = None
            return
        finally:
            self._agent_initializing = False
            self._agent_init_task = None

    monkeypatch.setattr(KinApp, "_initialize_agent", _fake_initialize, raising=True)


@pytest.mark.asyncio
async def test_shows_user_message_as_pending_until_agent_is_initialized(
    kin_app: KinApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_event = asyncio.Event()
    _patch_delayed_init(monkeypatch, init_event)

    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "Hello"

        press_task = asyncio.create_task(pilot.press("enter"))

        user_message = await _wait_for(
            pilot, lambda: next(iter(kin_app.query(UserMessage)), None)
        )
        assert isinstance(user_message, UserMessage)
        assert user_message.has_class("pending")
        init_event.set()
        await press_task
        assert not user_message.has_class("pending")


@pytest.mark.asyncio
async def test_can_interrupt_pending_message_during_initialization(
    kin_app: KinApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_event = asyncio.Event()
    _patch_delayed_init(monkeypatch, init_event)

    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "Hello"

        press_task = asyncio.create_task(pilot.press("enter"))

        user_message = await _wait_for(
            pilot, lambda: next(iter(kin_app.query(UserMessage)), None)
        )
        assert isinstance(user_message, UserMessage)
        assert user_message.has_class("pending")

        await pilot.press("escape")
        await press_task
        assert not user_message.has_class("pending")
        assert kin_app.query(InterruptMessage)
        assert kin_app.agent is None


@pytest.mark.asyncio
async def test_retry_initialization_after_interrupt(
    kin_app: KinApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_event = asyncio.Event()
    _patch_delayed_init(monkeypatch, init_event)

    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "First Message"
        press_task = asyncio.create_task(pilot.press("enter"))

        await _wait_for(pilot, lambda: next(iter(kin_app.query(UserMessage)), None))
        await pilot.press("escape")
        await press_task
        assert kin_app.agent is None
        assert kin_app._agent_init_task is None

        chat_input.value = "Second Message"
        press_task_2 = asyncio.create_task(pilot.press("enter"))

        def get_second_message():
            messages = list(kin_app.query(UserMessage))
            if len(messages) >= 2:
                return messages[-1]
            return None

        user_message_2 = await _wait_for(pilot, get_second_message)
        assert isinstance(user_message_2, UserMessage)
        assert user_message_2.has_class("pending")
        assert kin_app.agent is None

        init_event.set()
        await press_task_2
        assert not user_message_2.has_class("pending")
        assert kin_app.agent is not None

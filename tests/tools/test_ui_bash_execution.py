from __future__ import annotations

from pathlib import Path
import time

import pytest
from textual.widgets import Static

from kin_code.cli.textual_ui.app import KinApp
from kin_code.cli.textual_ui.widgets.chat_input.container import ChatInputContainer
from kin_code.cli.textual_ui.widgets.messages import BashOutputMessage, ErrorMessage
from kin_code.core.config import KinConfig, SessionLoggingConfig


@pytest.fixture
def kin_config(tmp_path: Path) -> KinConfig:
    return KinConfig(
        session_logging=SessionLoggingConfig(enabled=False), workdir=tmp_path
    )


@pytest.fixture
def kin_app(kin_config: KinConfig) -> KinApp:
    return KinApp(config=kin_config)


async def _wait_for_bash_output_message(
    kin_app: KinApp, pilot, timeout: float = 1.0
) -> BashOutputMessage:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if message := next(iter(kin_app.query(BashOutputMessage)), None):
            return message
        await pilot.pause(0.05)
    raise TimeoutError(f"BashOutputMessage did not appear within {timeout}s")


def assert_no_command_error(kin_app: KinApp) -> None:
    errors = list(kin_app.query(ErrorMessage))
    if not errors:
        return

    disallowed = {
        "Command failed",
        "Command timed out",
        "No command provided after '!'",
    }
    offending = [
        getattr(err, "_error", "")
        for err in errors
        if getattr(err, "_error", "")
        and any(phrase in getattr(err, "_error", "") for phrase in disallowed)
    ]
    assert not offending, f"Unexpected command errors: {offending}"


@pytest.mark.asyncio
async def test_ui_reports_no_output(kin_app: KinApp) -> None:
    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "!true"

        await pilot.press("enter")
        message = await _wait_for_bash_output_message(kin_app, pilot)
        output_widget = message.query_one(".bash-output", Static)
        assert str(output_widget.render()) == "(no output)"
        assert_no_command_error(kin_app)


@pytest.mark.asyncio
async def test_ui_shows_success_in_case_of_zero_code(kin_app: KinApp) -> None:
    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "!true"

        await pilot.press("enter")
        message = await _wait_for_bash_output_message(kin_app, pilot)
        icon = message.query_one(".bash-exit-success", Static)
        assert str(icon.render()) == "✓"
        assert not list(message.query(".bash-exit-failure"))


@pytest.mark.asyncio
async def test_ui_shows_failure_in_case_of_non_zero_code(kin_app: KinApp) -> None:
    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "!bash -lc 'exit 7'"

        await pilot.press("enter")
        message = await _wait_for_bash_output_message(kin_app, pilot)
        icon = message.query_one(".bash-exit-failure", Static)
        assert str(icon.render()) == "✗"
        code = message.query_one(".bash-exit-code", Static)
        assert "7" in str(code.render())
        assert not list(message.query(".bash-exit-success"))


@pytest.mark.asyncio
async def test_ui_handles_non_utf8_output(kin_app: KinApp) -> None:
    """Assert the UI accepts decoding a non-UTF8 sequence like `printf '\xf0\x9f\x98'`.
    Whereas `printf '\xf0\x9f\x98\x8b'` prints a smiley face and would work even without those changes.
    """
    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "!printf '\\xff\\xfe'"

        await pilot.press("enter")
        message = await _wait_for_bash_output_message(kin_app, pilot)
        output_widget = message.query_one(".bash-output", Static)
        # accept both possible encodings, as some shells emit escaped bytes as literal strings
        assert str(output_widget.render()) in {"", "\xff\xfe", r"\xff\xfe"}
        assert_no_command_error(kin_app)


@pytest.mark.asyncio
async def test_ui_handles_utf8_output(kin_app: KinApp) -> None:
    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "!echo hello"

        await pilot.press("enter")
        message = await _wait_for_bash_output_message(kin_app, pilot)
        output_widget = message.query_one(".bash-output", Static)
        assert str(output_widget.render()) == "hello\n"
        assert_no_command_error(kin_app)


@pytest.mark.asyncio
async def test_ui_handles_non_utf8_stderr(kin_app: KinApp) -> None:
    async with kin_app.run_test() as pilot:
        chat_input = kin_app.query_one(ChatInputContainer)
        chat_input.value = "!bash -lc \"printf '\\\\xff\\\\xfe' 1>&2\""

        await pilot.press("enter")
        message = await _wait_for_bash_output_message(kin_app, pilot)
        output_widget = message.query_one(".bash-output", Static)
        assert str(output_widget.render()) == ""
        assert_no_command_error(kin_app)

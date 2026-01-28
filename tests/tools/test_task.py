from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from kin_code.core.agents.manager import AgentManager
from kin_code.core.agents.models import BUILTIN_AGENTS, AgentType
from kin_code.core.config import VibeConfig
from kin_code.core.tools.base import BaseToolState, InvokeContext, ToolError
from kin_code.core.tools.builtins.task import (
    Task,
    TaskArgs,
    TaskResult,
    TaskToolConfig,
    _is_tool_call_content,
)
from kin_code.core.types import AssistantEvent, LLMMessage, Role
from tests.mock.utils import collect_result


@pytest.fixture
def task_tool() -> Task:
    return Task(config=TaskToolConfig(), state=BaseToolState())


class TestTaskArgs:
    def test_default_agent_is_explore(self) -> None:
        args = TaskArgs(task="do something")
        assert args.agent == "explore"

    def test_custom_values(self) -> None:
        args = TaskArgs(task="do something", agent="explore")
        assert args.task == "do something"
        assert args.agent == "explore"


class TestTaskToolValidation:
    @pytest.fixture
    def ctx(self) -> InvokeContext:
        config = VibeConfig(include_project_context=False, include_prompt_detail=False)
        manager = AgentManager(lambda: config)
        return InvokeContext(tool_call_id="test-call-id", agent_manager=manager)

    @pytest.mark.asyncio
    async def test_rejects_primary_agent(
        self, task_tool: Task, ctx: InvokeContext
    ) -> None:
        args = TaskArgs(task="do something", agent="default")

        with pytest.raises(ToolError) as exc_info:
            await collect_result(task_tool.run(args, ctx))

        assert "agent" in str(exc_info.value).lower()
        assert "subagent" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rejects_nonexistent_agent(
        self, task_tool: Task, ctx: InvokeContext
    ) -> None:
        args = TaskArgs(task="do something", agent="nonexistent")

        with pytest.raises(ToolError) as exc_info:
            await collect_result(task_tool.run(args, ctx))

        assert "Unknown agent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_requires_agent_manager_in_context(self, task_tool: Task) -> None:
        args = TaskArgs(task="do something", agent="explore")
        ctx = InvokeContext(tool_call_id="test-call-id")  # No agent_manager

        with pytest.raises(ToolError) as exc_info:
            await collect_result(task_tool.run(args, ctx))

        assert "agent_manager" in str(exc_info.value).lower()

    def test_explore_agent_is_valid_subagent(self) -> None:
        agent = BUILTIN_AGENTS["explore"]
        assert agent.agent_type == AgentType.SUBAGENT


class TestTaskToolExecution:
    @pytest.fixture
    def ctx(self) -> InvokeContext:
        config = VibeConfig(include_project_context=False, include_prompt_detail=False)
        manager = AgentManager(lambda: config)
        return InvokeContext(tool_call_id="test-call-id", agent_manager=manager)

    @pytest.mark.asyncio
    async def test_happy_path_returns_subagent_response(
        self, task_tool: Task, ctx: InvokeContext
    ) -> None:
        """Test that task tool successfully runs a subagent and returns its response."""
        mock_messages = [
            LLMMessage(role=Role.system, content="system"),
            LLMMessage(role=Role.user, content="task"),
            LLMMessage(role=Role.assistant, content="response 1"),
            LLMMessage(role=Role.assistant, content="response 2"),
        ]

        async def mock_act(task: str):
            yield AssistantEvent(content="Hello from subagent!")
            yield AssistantEvent(content=" More content.")

        with patch(
            "kin_code.core.tools.builtins.task.AgentLoop"
        ) as mock_agent_loop_class:
            mock_model = MagicMock()
            mock_model.alias = "test-model"
            mock_model.provider = "test-provider"

            mock_agent_loop = MagicMock()
            mock_agent_loop.act = mock_act
            mock_agent_loop.messages = mock_messages
            mock_agent_loop.set_approval_callback = MagicMock()
            mock_agent_loop.config.get_active_model.return_value = mock_model
            mock_agent_loop_class.return_value = mock_agent_loop

            args = TaskArgs(task="explore the codebase", agent="explore")
            result = await collect_result(task_tool.run(args, ctx))

            assert isinstance(result, TaskResult)
            assert result.response == "Hello from subagent! More content."
            assert result.turns_used == 2  # 2 assistant messages in mock_messages
            assert result.completed is True
            assert result.model_alias == "test-model"
            assert result.provider == "test-provider"

    @pytest.mark.asyncio
    async def test_handles_stopped_by_middleware(
        self, task_tool: Task, ctx: InvokeContext
    ) -> None:
        """Test that task tool reports incomplete when stopped by middleware."""
        mock_messages = [
            LLMMessage(role=Role.system, content="system"),
            LLMMessage(role=Role.assistant, content="partial"),
        ]

        async def mock_act(task: str):
            yield AssistantEvent(content="Partial response", stopped_by_middleware=True)

        with patch(
            "kin_code.core.tools.builtins.task.AgentLoop"
        ) as mock_agent_loop_class:
            mock_model = MagicMock()
            mock_model.alias = "test-model"
            mock_model.provider = "test-provider"

            mock_agent_loop = MagicMock()
            mock_agent_loop.act = mock_act
            mock_agent_loop.messages = mock_messages
            mock_agent_loop.set_approval_callback = MagicMock()
            mock_agent_loop.config.get_active_model.return_value = mock_model
            mock_agent_loop_class.return_value = mock_agent_loop

            args = TaskArgs(task="do something", agent="explore")
            result = await collect_result(task_tool.run(args, ctx))

            assert isinstance(result, TaskResult)
            assert result.completed is False

    @pytest.mark.asyncio
    async def test_handles_subagent_exception(
        self, task_tool: Task, ctx: InvokeContext
    ) -> None:
        """Test that task tool gracefully handles exceptions from subagent."""
        mock_messages = [LLMMessage(role=Role.system, content="system")]

        async def mock_act(task: str):
            yield AssistantEvent(content="Starting...")
            raise RuntimeError("Simulated error")

        with patch(
            "kin_code.core.tools.builtins.task.AgentLoop"
        ) as mock_agent_loop_class:
            mock_model = MagicMock()
            mock_model.alias = "test-model"
            mock_model.provider = "test-provider"

            mock_agent_loop = MagicMock()
            mock_agent_loop.act = mock_act
            mock_agent_loop.messages = mock_messages
            mock_agent_loop.set_approval_callback = MagicMock()
            mock_agent_loop.config.get_active_model.return_value = mock_model
            mock_agent_loop_class.return_value = mock_agent_loop

            args = TaskArgs(task="do something", agent="explore")
            result = await collect_result(task_tool.run(args, ctx))

            assert isinstance(result, TaskResult)
            assert result.completed is False
            assert "Simulated error" in result.response


class TestMalformedContentDetection:
    """Tests for _is_tool_call_content() malformed tool call detection."""

    def test_detects_function_tag_at_start(self) -> None:
        assert _is_tool_call_content("<function=read_file>")
        assert _is_tool_call_content("<function name='read_file'>")

    def test_detects_tool_call_tag_at_start(self) -> None:
        assert _is_tool_call_content("<tool_call>read_file</tool_call>")

    def test_detects_parameter_tag_at_start(self) -> None:
        assert _is_tool_call_content("<parameter=file_path>test.py</parameter>")
        assert _is_tool_call_content("<parameter name='file_path'>test.py</parameter>")

    def test_detects_patterns_mid_text(self) -> None:
        """Verify detection works when pattern appears after preamble text."""
        assert _is_tool_call_content("Here's my analysis: <function=read_file>")
        assert _is_tool_call_content("Let me help: <tool_call>read_file</tool_call>")
        assert _is_tool_call_content("Some text\n<parameter=path>test.py</parameter>")

    def test_case_insensitive(self) -> None:
        assert _is_tool_call_content("<FUNCTION=read>")
        assert _is_tool_call_content("<Tool_Call>read</Tool_Call>")
        assert _is_tool_call_content("<PARAMETER=path>test</PARAMETER>")

    def test_ignores_normal_text(self) -> None:
        assert not _is_tool_call_content("This is normal text.")
        assert not _is_tool_call_content("The function was called successfully.")
        assert not _is_tool_call_content("Parameters: a=1, b=2")

    def test_handles_empty_and_whitespace(self) -> None:
        assert not _is_tool_call_content("")
        assert not _is_tool_call_content("   ")
        assert not _is_tool_call_content("\n\t\n")

    def test_ignores_similar_but_valid_xml(self) -> None:
        """Ensure we don't false-positive on valid XML-like content."""
        assert not _is_tool_call_content("<example>some content</example>")
        assert not _is_tool_call_content("<code>print('hello')</code>")
        assert not _is_tool_call_content("<functionDescription>reads files</functionDescription>")

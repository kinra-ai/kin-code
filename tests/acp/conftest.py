from __future__ import annotations

from unittest.mock import patch

import pytest

from kin_code.acp.acp_agent_loop import KinAcpAgentLoop
from kin_code.core.agent_loop import AgentLoop
from kin_code.core.types import LLMChunk, LLMMessage, LLMUsage, Role
from tests.stubs.fake_backend import FakeBackend
from tests.stubs.fake_client import FakeClient


@pytest.fixture
def backend() -> FakeBackend:
    backend = FakeBackend(
        LLMChunk(
            message=LLMMessage(role=Role.assistant, content="Hi"),
            usage=LLMUsage(prompt_tokens=1, completion_tokens=1),
        )
    )
    return backend


def _create_acp_agent() -> KinAcpAgentLoop:
    kin_acp_agent = KinAcpAgentLoop()
    client = FakeClient()

    kin_acp_agent.on_connect(client)
    client.on_connect(kin_acp_agent)

    return kin_acp_agent  # pyright: ignore[reportReturnType]


@pytest.fixture
def acp_agent_loop(backend: FakeBackend) -> KinAcpAgentLoop:
    class PatchedAgent(AgentLoop):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs, backend=backend)

    patch("kin_code.acp.acp_agent_loop.AgentLoop", side_effect=PatchedAgent).start()
    return _create_acp_agent()

"""Agent operational modes with safety levels and configuration overrides.

This module defines the operational modes that control agent behavior and
permission levels. Each mode has a distinct safety profile, auto-approval
setting, and optional configuration overrides that affect tool availability
and execution policies.

Modes range from safe read-only (PLAN) to fully automated (AUTO_APPROVE),
allowing users to balance convenience with safety. The mode system integrates
with the agent's approval workflow and middleware to enforce appropriate
restrictions.

Available Modes:
    DEFAULT: Standard interactive mode requiring user approval for tools.
    PLAN: Read-only exploration mode with limited safe tools.
    ACCEPT_EDITS: Auto-approves file edits but requires approval for other tools.
    AUTO_APPROVE: Fully automated mode, auto-approves all tool executions.

Safety Levels:
    SAFE: No destructive operations, read-only access.
    NEUTRAL: Balanced, requires user confirmation.
    DESTRUCTIVE: Allows modifications with some automation.
    YOLO: Fully automated, no safety checks.

Typical Usage:
    mode = AgentMode.PLAN
    print(mode.display_name)  # "Plan"
    print(mode.safety)  # ModeSafety.SAFE
    print(mode.auto_approve)  # True

    agent = Agent(config, mode=mode)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any


class ModeSafety(StrEnum):
    SAFE = auto()
    NEUTRAL = auto()
    DESTRUCTIVE = auto()
    YOLO = auto()


class AgentMode(StrEnum):
    DEFAULT = auto()
    AUTO_APPROVE = auto()
    PLAN = auto()
    ACCEPT_EDITS = auto()

    @property
    def display_name(self) -> str:
        return MODE_CONFIGS[self].display_name

    @property
    def description(self) -> str:
        return MODE_CONFIGS[self].description

    @property
    def config_overrides(self) -> dict[str, Any]:
        return MODE_CONFIGS[self].config_overrides

    @property
    def auto_approve(self) -> bool:
        return MODE_CONFIGS[self].auto_approve

    @property
    def safety(self) -> ModeSafety:
        return MODE_CONFIGS[self].safety

    @classmethod
    def from_string(cls, value: str) -> AgentMode | None:
        try:
            return cls(value.lower())
        except ValueError:
            return None


@dataclass(frozen=True)
class ModeConfig:
    display_name: str
    description: str
    safety: ModeSafety = ModeSafety.NEUTRAL
    auto_approve: bool = False
    config_overrides: dict[str, Any] = field(default_factory=dict)


PLAN_MODE_TOOLS = ["grep", "read_file", "todo"]
ACCEPT_EDITS_TOOLS = ["write_file", "search_replace"]

MODE_CONFIGS: dict[AgentMode, ModeConfig] = {
    AgentMode.DEFAULT: ModeConfig(
        display_name="Default",
        description="Requires approval for tool executions",
        safety=ModeSafety.NEUTRAL,
        auto_approve=False,
    ),
    AgentMode.PLAN: ModeConfig(
        display_name="Plan",
        description="Read-only mode for exploration and planning",
        safety=ModeSafety.SAFE,
        auto_approve=True,
        config_overrides={"enabled_tools": PLAN_MODE_TOOLS},
    ),
    AgentMode.ACCEPT_EDITS: ModeConfig(
        display_name="Accept Edits",
        description="Auto-approves file edits only",
        safety=ModeSafety.DESTRUCTIVE,
        auto_approve=False,
        config_overrides={
            "tools": {
                "write_file": {"permission": "always"},
                "search_replace": {"permission": "always"},
            }
        },
    ),
    AgentMode.AUTO_APPROVE: ModeConfig(
        display_name="Auto Approve",
        description="Auto-approves all tool executions",
        safety=ModeSafety.YOLO,
        auto_approve=True,
    ),
}


def get_mode_order() -> list[AgentMode]:
    return [
        AgentMode.DEFAULT,
        AgentMode.PLAN,
        AgentMode.ACCEPT_EDITS,
        AgentMode.AUTO_APPROVE,
    ]


def next_mode(current: AgentMode) -> AgentMode:
    order = get_mode_order()
    idx = order.index(current)
    return order[(idx + 1) % len(order)]

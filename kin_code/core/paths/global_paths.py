from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path

from kin_code import KIN_ROOT


class GlobalPath:
    def __init__(self, resolver: Callable[[], Path]) -> None:
        self._resolver = resolver

    @property
    def path(self) -> Path:
        return self._resolver()


_DEFAULT_KIN_HOME = Path.home() / ".kin-code"


def _get_kin_home() -> Path:
    if kin_home := os.getenv("KIN_HOME"):
        return Path(kin_home).expanduser().resolve()
    return _DEFAULT_KIN_HOME


KIN_HOME = GlobalPath(_get_kin_home)
VIBE_HOME = KIN_HOME  # Backwards compatibility alias
GLOBAL_CONFIG_FILE = GlobalPath(lambda: KIN_HOME.path / "config.toml")
GLOBAL_ENV_FILE = GlobalPath(lambda: KIN_HOME.path / ".env")
GLOBAL_TOOLS_DIR = GlobalPath(lambda: KIN_HOME.path / "tools")
GLOBAL_SKILLS_DIR = GlobalPath(lambda: KIN_HOME.path / "skills")
GLOBAL_AGENTS_DIR = GlobalPath(lambda: KIN_HOME.path / "agents")
SESSION_LOG_DIR = GlobalPath(lambda: KIN_HOME.path / "logs" / "session")
TRUSTED_FOLDERS_FILE = GlobalPath(lambda: KIN_HOME.path / "trusted_folders.toml")
LOG_DIR = GlobalPath(lambda: KIN_HOME.path / "logs")
LOG_FILE = GlobalPath(lambda: KIN_HOME.path / "kin.log")

DEFAULT_TOOL_DIR = GlobalPath(lambda: KIN_ROOT / "core" / "tools" / "builtins")

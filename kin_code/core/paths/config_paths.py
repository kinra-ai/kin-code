from __future__ import annotations

from pathlib import Path
from typing import Literal

from kin_code.core.paths.global_paths import KIN_HOME, GlobalPath
from kin_code.core.trusted_folders import trusted_folders_manager

_config_paths_locked: bool = True


class ConfigPath(GlobalPath):
    @property
    def path(self) -> Path:
        if _config_paths_locked:
            raise RuntimeError("Config path is locked")
        return super().path


def _resolve_config_path(basename: str, type: Literal["file", "dir"]) -> Path:
    cwd = Path.cwd()
    is_folder_trusted = trusted_folders_manager.is_trusted(cwd)
    if not is_folder_trusted:
        return KIN_HOME.path / basename
    if type == "file":
        if (candidate := cwd / ".kin-code" / basename).is_file():
            return candidate
    elif type == "dir":
        if (candidate := cwd / ".kin-code" / basename).is_dir():
            return candidate
    return KIN_HOME.path / basename


def resolve_local_tools_dir(dir: Path) -> Path | None:
    if not trusted_folders_manager.is_trusted(dir):
        return None
    if (candidate := dir / ".kin-code" / "tools").is_dir():
        return candidate
    return None


def resolve_local_skills_dir(dir: Path) -> Path | None:
    if not trusted_folders_manager.is_trusted(dir):
        return None
    if (candidate := dir / ".kin-code" / "skills").is_dir():
        return candidate
    return None


def unlock_config_paths() -> None:
    global _config_paths_locked
    _config_paths_locked = False


CONFIG_FILE = ConfigPath(lambda: _resolve_config_path("config.toml", "file"))
CONFIG_DIR = ConfigPath(lambda: CONFIG_FILE.path.parent)
AGENT_DIR = ConfigPath(lambda: _resolve_config_path("agents", "dir"))
PROMPT_DIR = ConfigPath(lambda: _resolve_config_path("prompts", "dir"))
INSTRUCTIONS_FILE = ConfigPath(lambda: _resolve_config_path("instructions.md", "file"))
HISTORY_FILE = ConfigPath(lambda: _resolve_config_path("vibehistory", "file"))

"""Configuration path resolution with trust-based local overrides.

This module provides path resolution for configuration files and directories,
supporting both global (user-level) and local (project-level) configurations.
The resolution logic respects the trust status of directories, allowing trusted
projects to use local .kin-code/ configurations while untrusted directories fall
back to global settings for security.

The path resolution system enables per-project customization of agents, prompts,
tools, and skills when working in trusted directories, while maintaining a secure
default of using only global configurations for untrusted locations.

Key components:
    - ConfigPath: Locked path wrapper that enforces initialization ordering
    - CONFIG_FILE: Path to config.toml (global or local)
    - CONFIG_DIR: Parent directory of config.toml
    - AGENT_DIR: Directory containing agent definitions
    - PROMPT_DIR: Directory containing prompt templates
    - INSTRUCTIONS_FILE: Path to instructions.md
    - HISTORY_FILE: Path to vibehistory command history

Resolution logic:
    1. Check if current working directory is trusted
    2. If untrusted, return global path from KIN_HOME
    3. If trusted, check for local .kin-code/{resource}
    4. Use local path if it exists, otherwise fall back to global

Path locking:
    ConfigPath instances are locked by default to prevent premature access before
    the trusted folders system is initialized. Call unlock_config_paths() during
    startup to enable access.

Typical usage:
    # During initialization
    unlock_config_paths()

    # Access configuration
    config_path = CONFIG_FILE.path
    if config_path.exists():
        config = load_config(config_path)

    # Resolve local tools/skills for a directory
    tools_dir = resolve_local_tools_dir(Path.cwd())
    if tools_dir:
        load_local_tools(tools_dir)

Security:
    This module is security-critical. Local configuration paths are only resolved
    for trusted directories to prevent untrusted projects from injecting malicious
    agents, tools, or prompts.
"""

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
    """Resolve a config file or directory path based on trust status.

    For trusted folders, checks for a local .kin-code/{basename} file or directory.
    Falls back to the global KIN_HOME directory if the folder is untrusted or
    the local path doesn't exist.

    Args:
        basename: The name of the config file or directory to resolve.
        type: Whether to look for a "file" or "dir".

    Returns:
        Resolved Path to the config file or directory.
    """
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
    """Resolve the local tools directory if it exists in a trusted folder.

    Checks if the given directory is trusted and contains a .kin-code/tools
    subdirectory. Returns None if the folder is untrusted or the tools
    directory doesn't exist.

    Args:
        dir: The directory to check for local tools.

    Returns:
        Path to the local tools directory, or None if not found or untrusted.
    """
    if not trusted_folders_manager.is_trusted(dir):
        return None
    if (candidate := dir / ".kin-code" / "tools").is_dir():
        return candidate
    return None


def resolve_local_skills_dir(dir: Path) -> Path | None:
    """Resolve the local skills directory if it exists in a trusted folder.

    Checks if the given directory is trusted and contains a .kin-code/skills
    subdirectory. Returns None if the folder is untrusted or the skills
    directory doesn't exist.

    Args:
        dir: The directory to check for local skills.

    Returns:
        Path to the local skills directory, or None if not found or untrusted.
    """
    if not trusted_folders_manager.is_trusted(dir):
        return None
    if (candidate := dir / ".kin-code" / "skills").is_dir():
        return candidate
    return None


def unlock_config_paths() -> None:
    """Unlock config paths to allow access.

    Disables the config path lock that prevents access to ConfigPath instances.
    This should be called during initialization to enable configuration loading.
    """
    global _config_paths_locked
    _config_paths_locked = False


CONFIG_FILE = ConfigPath(lambda: _resolve_config_path("config.toml", "file"))
CONFIG_DIR = ConfigPath(lambda: CONFIG_FILE.path.parent)
AGENT_DIR = ConfigPath(lambda: _resolve_config_path("agents", "dir"))
PROMPT_DIR = ConfigPath(lambda: _resolve_config_path("prompts", "dir"))
INSTRUCTIONS_FILE = ConfigPath(lambda: _resolve_config_path("instructions.md", "file"))
HISTORY_FILE = ConfigPath(lambda: _resolve_config_path("kinhistory", "file"))

from __future__ import annotations

import asyncio
from functools import lru_cache
import os
import signal
import sys
from typing import ClassVar, Literal, final

from pydantic import BaseModel, Field
from tree_sitter import Language, Node, Parser
import tree_sitter_bash as tsbash

from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    ToolError,
    ToolPermission,
)
from kin_code.core.utils import is_windows


@lru_cache(maxsize=1)
def _get_parser() -> Parser:
    return Parser(Language(tsbash.language()))


def _extract_commands(command: str) -> list[str]:
    """Extract individual command names from a bash command string.

    Uses tree-sitter to parse bash syntax and extract command nodes,
    handling compound statements, pipes, and redirections.

    Args:
        command: The bash command string to parse.

    Returns:
        List of command strings extracted from the input.
    """
    parser = _get_parser()
    tree = parser.parse(command.encode("utf-8"))

    commands: list[str] = []

    def find_commands(node: Node) -> None:
        if node.type == "command":
            parts = []
            for child in node.children:
                if (
                    child.type
                    in {"command_name", "word", "string", "raw_string", "concatenation"}
                    and child.text is not None
                ):
                    parts.append(child.text.decode("utf-8"))
            if parts:
                commands.append(" ".join(parts))

        for child in node.children:
            find_commands(child)

    find_commands(tree.root_node)
    return commands


def _get_subprocess_encoding() -> str:
    """Determine the correct encoding for subprocess output.

    On Windows, uses the OEM code page (e.g., cp850, cp1252).
    On other platforms, defaults to UTF-8.

    Returns:
        Encoding name suitable for decoding subprocess output.
    """
    if sys.platform == "win32":
        # Windows console uses OEM code page (e.g., cp850, cp1252)
        import ctypes

        return f"cp{ctypes.windll.kernel32.GetOEMCP()}"
    return "utf-8"


def _get_base_env() -> dict[str, str]:
    """Build base environment variables for non-interactive command execution.

    Sets CI flags and disables interactive features, TTY, colors, and pagers
    to ensure commands run in a predictable non-interactive mode suitable
    for automation.

    Returns:
        Dictionary of environment variables with the current environment
        plus non-interactive overrides.
    """
    base_env = {
        **os.environ,
        "CI": "true",
        "NONINTERACTIVE": "1",
        "NO_TTY": "1",
        "NO_COLOR": "1",
    }

    if is_windows():
        base_env["GIT_PAGER"] = "more"
        base_env["PAGER"] = "more"
    else:
        base_env["TERM"] = "dumb"
        base_env["DEBIAN_FRONTEND"] = "noninteractive"
        base_env["GIT_PAGER"] = "cat"
        base_env["PAGER"] = "cat"
        base_env["LESS"] = "-FX"
        base_env["LC_ALL"] = "en_US.UTF-8"

    return base_env


async def _kill_process_tree(proc: asyncio.subprocess.Process) -> None:
    """Forcefully terminate a subprocess and all its children.

    On Windows, uses taskkill with /F /T flags. On Unix, kills the
    process group with SIGKILL. Silently handles processes that have
    already terminated or can't be accessed.

    Args:
        proc: The subprocess to terminate.
    """
    if proc.returncode is not None:
        return

    try:
        if sys.platform == "win32":
            try:
                subprocess_proc = await asyncio.create_subprocess_exec(
                    "taskkill",
                    "/F",
                    "/T",
                    "/PID",
                    str(proc.pid),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await subprocess_proc.wait()
            except (FileNotFoundError, OSError):
                proc.terminate()
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

        await proc.wait()
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _get_default_allowlist() -> list[str]:
    common = ["echo", "find", "git diff", "git log", "git status", "tree", "whoami"]

    if is_windows():
        return common + ["dir", "findstr", "more", "type", "ver", "where"]
    else:
        return common + [
            "cat",
            "file",
            "head",
            "ls",
            "pwd",
            "stat",
            "tail",
            "uname",
            "wc",
            "which",
        ]


def _get_default_denylist() -> list[str]:
    common = ["gdb", "pdb", "passwd"]

    if is_windows():
        return common + ["cmd /k", "powershell -NoExit", "pwsh -NoExit", "notepad"]
    else:
        return common + [
            "nano",
            "vim",
            "vi",
            "emacs",
            "bash -i",
            "sh -i",
            "zsh -i",
            "fish -i",
            "dash -i",
            "screen",
            "tmux",
        ]


def _get_default_denylist_standalone() -> list[str]:
    common = ["python", "python3", "ipython"]

    if is_windows():
        return common + ["cmd", "powershell", "pwsh", "notepad"]
    else:
        return common + ["bash", "sh", "nohup", "vi", "vim", "emacs", "nano", "su"]


class BashToolConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK
    max_output_bytes: int = Field(
        default=16_000, description="Maximum bytes to capture from stdout and stderr."
    )
    default_timeout: int = Field(
        default=30, description="Default timeout for commands in seconds."
    )
    allowlist: list[str] = Field(
        default_factory=_get_default_allowlist,
        description="Command prefixes that are automatically allowed",
    )
    denylist: list[str] = Field(
        default_factory=_get_default_denylist,
        description="Command prefixes that are automatically denied",
    )
    denylist_standalone: list[str] = Field(
        default_factory=_get_default_denylist_standalone,
        description="Commands that are denied only when run without arguments",
    )


class BashArgs(BaseModel):
    command: str
    timeout: int | None = Field(
        default=None, description="Override the default command timeout."
    )


class BashResult(BaseModel):
    stdout: str
    stderr: str
    returncode: int


class Bash(BaseTool[BashArgs, BashResult, BashToolConfig, BaseToolState]):
    description: ClassVar[str] = "Run a one-off bash command and capture its output."

    def check_allowlist_denylist(self, args: BashArgs) -> ToolPermission | None:
        """Check if command should be automatically allowed or denied.

        Parses the command to extract individual commands, then checks them
        against allowlist, denylist, and standalone denylist patterns.
        Returns ALWAYS if all commands are allowlisted, NEVER if any are
        denylisted, or None if user approval is needed.

        Args:
            args: The bash arguments containing the command to check.

        Returns:
            ToolPermission.ALWAYS if automatically allowed,
            ToolPermission.NEVER if denied, or None for manual approval.
        """
        if is_windows():
            return None

        command_parts = _extract_commands(args.command)
        if not command_parts:
            return None

        def is_denylisted(command: str) -> bool:
            return any(command.startswith(pattern) for pattern in self.config.denylist)

        def is_standalone_denylisted(command: str) -> bool:
            parts = command.split()
            if not parts:
                return False

            base_command = parts[0]
            has_args = len(parts) > 1

            if not has_args:
                command_name = os.path.basename(base_command)
                if command_name in self.config.denylist_standalone:
                    return True
                if base_command in self.config.denylist_standalone:
                    return True

            return False

        def is_allowlisted(command: str) -> bool:
            return any(command.startswith(pattern) for pattern in self.config.allowlist)

        for part in command_parts:
            if is_denylisted(part):
                return ToolPermission.NEVER
            if is_standalone_denylisted(part):
                return ToolPermission.NEVER

        if all(is_allowlisted(part) for part in command_parts):
            return ToolPermission.ALWAYS

        return None

    @final
    def _build_timeout_error(self, command: str, timeout: int) -> ToolError:
        return ToolError(f"Command timed out after {timeout}s: {command!r}")

    @final
    def _build_result(
        self, *, command: str, stdout: str, stderr: str, returncode: int
    ) -> BashResult:
        if returncode != 0:
            error_msg = f"Command failed: {command!r}\n"
            error_msg += f"Return code: {returncode}"
            if stderr:
                error_msg += f"\nStderr: {stderr}"
            if stdout:
                error_msg += f"\nStdout: {stdout}"
            raise ToolError(error_msg.strip())

        return BashResult(stdout=stdout, stderr=stderr, returncode=returncode)

    async def run(self, args: BashArgs) -> BashResult:
        """Execute a bash command and capture its output.

        Runs the command in a subprocess with a timeout, captures stdout and stderr,
        and returns the result. The subprocess runs in non-interactive mode with
        a clean environment. Output is truncated to max_output_bytes.

        Args:
            args: Arguments containing the command and optional timeout.

        Returns:
            BashResult with stdout, stderr, and return code.

        Raises:
            ToolError: If the command times out, fails, or encounters an error.
        """
        timeout = args.timeout or self.config.default_timeout
        max_bytes = self.config.max_output_bytes

        proc = None
        try:
            # start_new_session is Unix-only, on Windows it's ignored
            kwargs: dict[Literal["start_new_session"], bool] = (
                {} if is_windows() else {"start_new_session": True}
            )

            proc = await asyncio.create_subprocess_shell(
                args.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.DEVNULL,
                cwd=self.config.effective_workdir,
                env=_get_base_env(),
                **kwargs,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except TimeoutError:
                await _kill_process_tree(proc)
                raise self._build_timeout_error(args.command, timeout)

            encoding = _get_subprocess_encoding()
            stdout = (
                stdout_bytes.decode(encoding, errors="replace")[:max_bytes]
                if stdout_bytes
                else ""
            )
            stderr = (
                stderr_bytes.decode(encoding, errors="replace")[:max_bytes]
                if stderr_bytes
                else ""
            )

            returncode = proc.returncode or 0

            return self._build_result(
                command=args.command,
                stdout=stdout,
                stderr=stderr,
                returncode=returncode,
            )

        except (ToolError, asyncio.CancelledError):
            raise
        except Exception as exc:
            raise ToolError(f"Error running command {args.command!r}: {exc}") from exc
        finally:
            if proc is not None:
                await _kill_process_tree(proc)

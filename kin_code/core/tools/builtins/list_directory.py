from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal

import pathspec
from pydantic import BaseModel, Field

from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    InvokeContext,
    ToolError,
    ToolPermission,
)
from kin_code.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData
from kin_code.core.types import ToolStreamEvent

if TYPE_CHECKING:
    from kin_code.core.types import ToolCallEvent, ToolResultEvent


class ListDirectoryConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS

    max_entries: int = Field(
        default=200, description="Maximum number of entries to return."
    )
    max_depth: int = Field(
        default=10, description="Maximum recursion depth for recursive listing."
    )
    exclude_patterns: list[str] = Field(
        default=[
            ".git/",
            "node_modules/",
            "__pycache__/",
            ".venv/",
            "venv/",
            ".pytest_cache/",
            ".mypy_cache/",
        ],
        description="Patterns to exclude from listings.",
    )
    codeignore_file: str = Field(
        default=".kin-codeignore",
        description="Name of the file to read for additional exclusion patterns.",
    )
    respect_gitignore: bool = Field(
        default=True, description="Whether to respect .gitignore files for recursive."
    )


class ListDirectoryState(BaseToolState):
    pass


class DirectoryEntry(BaseModel):
    name: str = Field(description="Name of the file or directory")
    type: Literal["file", "directory", "symlink"] = Field(
        description="Type of the entry"
    )
    size: int | None = Field(
        default=None, description="Size in bytes (None for directories)"
    )
    modified: str | None = Field(
        default=None, description="ISO timestamp of last modification"
    )


class ListDirectoryArgs(BaseModel):
    path: str = Field(default=".", description="Directory to list")
    recursive: bool = Field(default=False, description="List recursively")
    max_depth: int = Field(
        default=3, ge=1, le=10, description="Maximum depth for recursive listing"
    )
    include_hidden: bool = Field(
        default=False, description="Include hidden files/directories"
    )


class ListDirectoryResult(BaseModel):
    path: str = Field(description="The listed directory path")
    entries: list[DirectoryEntry] = Field(description="Directory entries")
    truncated: bool = Field(default=False, description="True if results were truncated")
    total_files: int = Field(description="Total number of files found")
    total_directories: int = Field(description="Total number of directories found")


class ListDirectory(
    BaseTool[
        ListDirectoryArgs, ListDirectoryResult, ListDirectoryConfig, ListDirectoryState
    ],
    ToolUIData[ListDirectoryArgs, ListDirectoryResult],
):
    description: ClassVar[str] = """List contents of a directory.

USE WHEN:
- Exploring the structure of a directory
- Finding files and subdirectories in a location
- Understanding project layout
- Checking if files or directories exist

DO NOT USE WHEN:
- Finding files by pattern (use glob)
- Searching for content in files (use grep)
- Reading file contents (use read_file)

EXAMPLES:
- path="." - List current directory
- path="src", recursive=True - List src/ recursively
- path=".", include_hidden=True - Include hidden files

NOTES:
- Directories shown first, then files alphabetically
- Respects .gitignore for recursive listing
- File sizes included for files
- Symlinks shown but not followed"""

    async def run(
        self, args: ListDirectoryArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | ListDirectoryResult, None]:
        base_path = self._resolve_path(args.path)
        exclude_spec = self._build_exclude_spec(base_path) if args.recursive else None

        effective_depth = min(args.max_depth, self.config.max_depth)

        entries = self._collect_entries(
            base_path,
            base_path,
            args.recursive,
            effective_depth,
            args.include_hidden,
            exclude_spec,
        )

        dirs = [e for e in entries if e.type == "directory"]
        files = [e for e in entries if e.type in {"file", "symlink"}]

        sorted_dirs = sorted(dirs, key=lambda e: e.name.lower())
        sorted_files = sorted(files, key=lambda e: e.name.lower())
        sorted_entries = sorted_dirs + sorted_files

        truncated = len(sorted_entries) > self.config.max_entries
        result_entries = sorted_entries[: self.config.max_entries]

        yield ListDirectoryResult(
            path=str(base_path),
            entries=result_entries,
            truncated=truncated,
            total_files=len(files),
            total_directories=len(dirs),
        )

    def _resolve_path(self, path: str) -> Path:
        path_obj = Path(path).expanduser()
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj

        if not path_obj.exists():
            raise ToolError(f"Path does not exist: {path}")
        if not path_obj.is_dir():
            raise ToolError(f"Path is not a directory: {path}")

        return path_obj

    def _build_exclude_spec(self, base_path: Path) -> pathspec.PathSpec:
        patterns: list[str] = list(self.config.exclude_patterns)

        codeignore_path = base_path / self.config.codeignore_file
        if codeignore_path.is_file():
            patterns.extend(self._load_ignore_file(codeignore_path))

        if self.config.respect_gitignore:
            gitignore_path = base_path / ".gitignore"
            if gitignore_path.is_file():
                patterns.extend(self._load_ignore_file(gitignore_path))

        return pathspec.PathSpec.from_lines("gitignore", patterns)

    def _load_ignore_file(self, path: Path) -> list[str]:
        patterns = []
        try:
            content = path.read_text("utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        except OSError:
            pass
        return patterns

    def _collect_entries(
        self,
        current_path: Path,
        base_path: Path,
        recursive: bool,
        depth: int,
        include_hidden: bool,
        exclude_spec: pathspec.PathSpec | None,
    ) -> list[DirectoryEntry]:
        entries: list[DirectoryEntry] = []

        if depth <= 0:
            return entries

        try:
            items = sorted(current_path.iterdir(), key=lambda p: p.name.lower())
        except PermissionError:
            return entries

        for item in items:
            if not include_hidden and item.name.startswith("."):
                continue

            try:
                rel_path = item.relative_to(base_path)
                rel_str = str(rel_path)
            except ValueError:
                continue

            if exclude_spec and exclude_spec.match_file(
                rel_str + "/" if item.is_dir() else rel_str
            ):
                continue

            entry = self._create_entry(item, base_path)
            if entry:
                entries.append(entry)

            if recursive and item.is_dir() and not item.is_symlink():
                sub_entries = self._collect_entries(
                    item, base_path, True, depth - 1, include_hidden, exclude_spec
                )
                entries.extend(sub_entries)

        return entries

    def _create_entry(self, path: Path, base_path: Path) -> DirectoryEntry | None:
        try:
            rel_path = path.relative_to(base_path)
            name = str(rel_path)
        except ValueError:
            name = path.name

        try:
            stat = path.lstat()
        except OSError:
            return None

        if path.is_symlink():
            entry_type: Literal["file", "directory", "symlink"] = "symlink"
            size = None
        elif path.is_dir():
            entry_type = "directory"
            size = None
        else:
            entry_type = "file"
            size = stat.st_size

        try:
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat()
        except (OSError, ValueError):
            mtime = None

        return DirectoryEntry(name=name, type=entry_type, size=size, modified=mtime)

    def check_allowlist_denylist(
        self, args: ListDirectoryArgs
    ) -> ToolPermission | None:
        path_obj = Path(args.path).expanduser()
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj
        path_str = str(path_obj)

        for pattern in self.config.denylist:
            if fnmatch.fnmatch(path_str, pattern):
                return ToolPermission.NEVER

        for pattern in self.config.allowlist:
            if fnmatch.fnmatch(path_str, pattern):
                return ToolPermission.ALWAYS

        return None

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, ListDirectoryArgs):
            return ToolCallDisplay(summary="list_directory")

        summary = f"Listing {event.args.path}"
        if event.args.recursive:
            summary += f" (recursive, depth {event.args.max_depth})"
        if event.args.include_hidden:
            summary += " [+hidden]"

        return ToolCallDisplay(summary=summary)

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, ListDirectoryResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )

        dirs = event.result.total_directories
        files = event.result.total_files
        message = f"{dirs} director{'ies' if dirs != 1 else 'y'}, {files} file{'s' if files != 1 else ''}"
        if event.result.truncated:
            message += " (truncated)"

        warnings = []
        if event.result.truncated:
            warnings.append("Results truncated due to entry limit")

        return ToolResultDisplay(success=True, message=message, warnings=warnings)

    @classmethod
    def get_status_text(cls) -> str:
        return "Listing directory"

from __future__ import annotations

from collections.abc import AsyncGenerator
import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

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


class GlobToolConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS

    max_results: int = Field(
        default=100, description="Maximum number of matching files to return."
    )
    exclude_patterns: list[str] = Field(
        default=[
            ".git/",
            "node_modules/",
            "__pycache__/",
            ".venv/",
            "venv/",
            ".env/",
            "env/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".pytest_cache/",
            ".mypy_cache/",
            ".tox/",
            ".nox/",
            ".coverage/",
            "htmlcov/",
            "dist/",
            "build/",
            ".idea/",
            ".vscode/",
            "*.egg-info/",
            ".DS_Store",
            "Thumbs.db",
        ],
        description="Glob patterns to exclude from results.",
    )
    codeignore_file: str = Field(
        default=".kin-codeignore",
        description="Name of the file to read for additional exclusion patterns.",
    )
    respect_gitignore: bool = Field(
        default=True, description="Whether to respect .gitignore files."
    )
    max_state_history: int = Field(
        default=10, description="Number of recent patterns to remember in state."
    )


class GlobState(BaseToolState):
    recent_patterns: list[str] = Field(default_factory=list)


class GlobArgs(BaseModel):
    pattern: str = Field(description="Glob pattern (e.g., '**/*.py', 'src/**/*.ts')")
    path: str = Field(default=".", description="Directory to search in")


class GlobResult(BaseModel):
    files: list[str] = Field(description="List of matching file paths")
    truncated: bool = Field(
        default=False, description="True if results were truncated at max_results"
    )
    total_matches: int = Field(description="Total number of matches found")


class Glob(
    BaseTool[GlobArgs, GlobResult, GlobToolConfig, GlobState],
    ToolUIData[GlobArgs, GlobResult],
):
    description: ClassVar[str] = """Find files matching a glob pattern.

USE WHEN:
- Finding files by name pattern (e.g., all Python files)
- Locating configuration files across the project
- Discovering test files or modules
- Exploring directory structure

DO NOT USE WHEN:
- Searching for content within files (use grep)
- Reading a specific known file (use read_file)
- Listing directory contents (use bash ls or list_directory)

EXAMPLES:
- "**/*.py" - Find all Python files recursively
- "src/**/*.ts" - Find TypeScript files under src/
- "*.json" - Find JSON files in current directory
- "tests/**/test_*.py" - Find test files

NOTES:
- Results sorted by modification time (most recent first)
- Respects .gitignore and .kin-codeignore
- Does not follow symlinks
- Excludes common build/cache directories by default"""

    async def run(
        self, args: GlobArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | GlobResult, None]:
        self._validate_args(args)

        base_path = self._resolve_path(args.path)
        exclude_spec = self._build_exclude_spec(base_path)

        matching_files = self._find_matching_files(
            base_path, args.pattern, exclude_spec
        )
        sorted_files = self._sort_by_mtime(matching_files)

        self._update_state(args.pattern)

        truncated = len(sorted_files) > self.config.max_results
        result_files = sorted_files[: self.config.max_results]

        relative_paths = [self._make_relative(f, base_path) for f in result_files]

        yield GlobResult(
            files=relative_paths, truncated=truncated, total_matches=len(sorted_files)
        )

    def _validate_args(self, args: GlobArgs) -> None:
        if not args.pattern.strip():
            raise ToolError("Pattern cannot be empty")

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
        patterns: list[str] = []

        patterns.extend(self.config.exclude_patterns)

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

    def _find_matching_files(
        self, base_path: Path, pattern: str, exclude_spec: pathspec.PathSpec
    ) -> list[Path]:
        matching = []

        for file_path in base_path.glob(pattern):
            if not file_path.is_file():
                continue

            if file_path.is_symlink():
                continue

            try:
                relative = file_path.relative_to(base_path)
                rel_str = str(relative)
            except ValueError:
                continue

            if exclude_spec.match_file(rel_str):
                continue

            matching.append(file_path)

        return matching

    def _sort_by_mtime(self, files: list[Path]) -> list[Path]:
        def get_mtime(p: Path) -> float:
            try:
                return p.stat().st_mtime
            except OSError:
                return 0.0

        return sorted(files, key=get_mtime, reverse=True)

    def _make_relative(self, file_path: Path, base_path: Path) -> str:
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return str(file_path)

    def _update_state(self, pattern: str) -> None:
        self.state.recent_patterns.append(pattern)
        if len(self.state.recent_patterns) > self.config.max_state_history:
            self.state.recent_patterns.pop(0)

    def check_allowlist_denylist(self, args: GlobArgs) -> ToolPermission | None:
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
        if not isinstance(event.args, GlobArgs):
            return ToolCallDisplay(summary="glob")

        summary = f"Globbing '{event.args.pattern}'"
        if event.args.path != ".":
            summary += f" in {event.args.path}"

        return ToolCallDisplay(summary=summary)

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, GlobResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )

        count = len(event.result.files)
        message = f"Found {count} file{'s' if count != 1 else ''}"
        if event.result.truncated:
            message += f" (showing {count} of {event.result.total_matches})"

        warnings = []
        if event.result.truncated:
            warnings.append(
                f"Results truncated. {event.result.total_matches} total matches."
            )

        return ToolResultDisplay(success=True, message=message, warnings=warnings)

    @classmethod
    def get_status_text(cls) -> str:
        return "Finding files"

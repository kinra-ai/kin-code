from __future__ import annotations

import pytest

from kin_code.core.tools.base import ToolError
from kin_code.core.tools.builtins.glob import (
    Glob,
    GlobArgs,
    GlobState,
    GlobToolConfig,
)
from tests.mock.utils import collect_result


@pytest.fixture
def glob(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = GlobToolConfig()
    return Glob(config=config, state=GlobState())


@pytest.mark.asyncio
async def test_finds_files_with_pattern(glob, tmp_path):
    (tmp_path / "file1.py").write_text("content")
    (tmp_path / "file2.py").write_text("content")
    (tmp_path / "file3.txt").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py")))

    assert len(result.files) == 2
    assert "file1.py" in result.files
    assert "file2.py" in result.files
    assert "file3.txt" not in result.files
    assert not result.truncated


@pytest.mark.asyncio
async def test_finds_files_recursively(glob, tmp_path):
    subdir = tmp_path / "src"
    subdir.mkdir()
    (subdir / "main.py").write_text("content")
    (tmp_path / "test.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="**/*.py")))

    assert len(result.files) == 2
    assert any("main.py" in f for f in result.files)
    assert any("test.py" in f for f in result.files)


@pytest.mark.asyncio
async def test_searches_in_specific_path(glob, tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    tests = tmp_path / "tests"
    tests.mkdir()
    (src / "app.py").write_text("content")
    (tests / "test_app.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py", path="src")))

    assert len(result.files) == 1
    assert "app.py" in result.files


@pytest.mark.asyncio
async def test_returns_empty_on_no_matches(glob, tmp_path):
    (tmp_path / "file.txt").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py")))

    assert len(result.files) == 0
    assert not result.truncated


@pytest.mark.asyncio
async def test_fails_with_empty_pattern(glob):
    with pytest.raises(ToolError) as err:
        await collect_result(glob.run(GlobArgs(pattern="")))

    assert "Pattern cannot be empty" in str(err.value)


@pytest.mark.asyncio
async def test_fails_with_nonexistent_path(glob):
    with pytest.raises(ToolError) as err:
        await collect_result(glob.run(GlobArgs(pattern="*.py", path="nonexistent")))

    assert "Path does not exist" in str(err.value)


@pytest.mark.asyncio
async def test_fails_with_file_path(glob, tmp_path):
    (tmp_path / "file.py").write_text("content")

    with pytest.raises(ToolError) as err:
        await collect_result(glob.run(GlobArgs(pattern="*.py", path="file.py")))

    assert "not a directory" in str(err.value)


@pytest.mark.asyncio
async def test_truncates_to_max_results(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = GlobToolConfig(max_results=5)
    glob = Glob(config=config, state=GlobState())

    for i in range(10):
        (tmp_path / f"file{i}.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py")))

    assert len(result.files) == 5
    assert result.truncated
    assert result.total_matches == 10


@pytest.mark.asyncio
async def test_respects_default_exclude_patterns(glob, tmp_path):
    (tmp_path / "included.py").write_text("content")
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "excluded.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="**/*.py")))

    assert "included.py" in result.files
    assert not any("node_modules" in f for f in result.files)


@pytest.mark.asyncio
async def test_respects_kincodeignore_file(glob, tmp_path):
    (tmp_path / ".kin-codeignore").write_text("custom_dir/\n*.tmp\n")
    custom_dir = tmp_path / "custom_dir"
    custom_dir.mkdir()
    (custom_dir / "excluded.py").write_text("content")
    (tmp_path / "excluded.tmp").write_text("content")
    (tmp_path / "included.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="**/*")))

    assert "included.py" in result.files
    assert not any("custom_dir" in f for f in result.files)
    assert not any(".tmp" in f for f in result.files)


@pytest.mark.asyncio
async def test_respects_gitignore_file(glob, tmp_path):
    (tmp_path / ".gitignore").write_text("ignored_dir/\n*.log\n")
    ignored_dir = tmp_path / "ignored_dir"
    ignored_dir.mkdir()
    (ignored_dir / "file.py").write_text("content")
    (tmp_path / "debug.log").write_text("content")
    (tmp_path / "included.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="**/*")))

    assert "included.py" in result.files
    assert not any("ignored_dir" in f for f in result.files)
    assert not any(".log" in f for f in result.files)


@pytest.mark.asyncio
async def test_ignores_comments_in_ignore_files(glob, tmp_path):
    (tmp_path / ".kin-codeignore").write_text("# comment\npattern/\n# another\n")
    (tmp_path / "file.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py")))

    assert len(result.files) >= 1


@pytest.mark.asyncio
async def test_sorts_by_modification_time(glob, tmp_path):
    import time

    (tmp_path / "old.py").write_text("content")
    time.sleep(0.1)
    (tmp_path / "newer.py").write_text("content")
    time.sleep(0.1)
    (tmp_path / "newest.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py")))

    assert result.files[0] == "newest.py"
    assert result.files[1] == "newer.py"
    assert result.files[2] == "old.py"


@pytest.mark.asyncio
async def test_does_not_follow_symlinks(glob, tmp_path):
    (tmp_path / "real.py").write_text("content")
    (tmp_path / "link.py").symlink_to(tmp_path / "real.py")

    result = await collect_result(glob.run(GlobArgs(pattern="*.py")))

    assert "real.py" in result.files
    assert "link.py" not in result.files


@pytest.mark.asyncio
async def test_tracks_recent_patterns(glob, tmp_path):
    (tmp_path / "test.py").write_text("content")

    await collect_result(glob.run(GlobArgs(pattern="*.py")))
    await collect_result(glob.run(GlobArgs(pattern="*.txt")))
    await collect_result(glob.run(GlobArgs(pattern="**/*.md")))

    assert glob.state.recent_patterns == ["*.py", "*.txt", "**/*.md"]


@pytest.mark.asyncio
async def test_excludes_pycache_directory(glob, tmp_path):
    (tmp_path / "included.py").write_text("content")
    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "module.cpython-312.pyc").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="**/*")))

    assert "included.py" in result.files
    assert not any("__pycache__" in f for f in result.files)


@pytest.mark.asyncio
async def test_excludes_venv_directory(glob, tmp_path):
    (tmp_path / "included.py").write_text("content")
    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "lib.py").write_text("content")

    result = await collect_result(glob.run(GlobArgs(pattern="**/*.py")))

    assert "included.py" in result.files
    assert not any(".venv" in f for f in result.files)

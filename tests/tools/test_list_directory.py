from __future__ import annotations

import pytest

from kin_code.core.tools.base import ToolError
from kin_code.core.tools.builtins.list_directory import (
    ListDirectory,
    ListDirectoryArgs,
    ListDirectoryConfig,
    ListDirectoryState,
)
from tests.mock.utils import collect_result


@pytest.fixture
def list_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = ListDirectoryConfig()
    return ListDirectory(config=config, state=ListDirectoryState())


@pytest.mark.asyncio
async def test_lists_directory_contents(list_dir, tmp_path):
    (tmp_path / "file1.py").write_text("content")
    (tmp_path / "file2.txt").write_text("content")
    (tmp_path / "subdir").mkdir()

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    assert result.total_files == 2
    assert result.total_directories == 1
    names = [e.name for e in result.entries]
    assert "file1.py" in names
    assert "file2.txt" in names
    assert "subdir" in names


@pytest.mark.asyncio
async def test_directories_listed_first(list_dir, tmp_path):
    (tmp_path / "alpha.py").write_text("content")
    (tmp_path / "beta_dir").mkdir()
    (tmp_path / "gamma.txt").write_text("content")

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    types = [e.type for e in result.entries]
    dir_indices = [i for i, t in enumerate(types) if t == "directory"]
    file_indices = [i for i, t in enumerate(types) if t == "file"]

    if dir_indices and file_indices:
        assert max(dir_indices) < min(file_indices)


@pytest.mark.asyncio
async def test_lists_specific_path(list_dir, tmp_path):
    subdir = tmp_path / "mydir"
    subdir.mkdir()
    (subdir / "inside.py").write_text("content")
    (tmp_path / "outside.py").write_text("content")

    result = await collect_result(list_dir.run(ListDirectoryArgs(path="mydir")))

    names = [e.name for e in result.entries]
    assert "inside.py" in names
    assert "outside.py" not in names


@pytest.mark.asyncio
async def test_recursive_listing(list_dir, tmp_path):
    subdir = tmp_path / "level1"
    subdir.mkdir()
    subsubdir = subdir / "level2"
    subsubdir.mkdir()
    (tmp_path / "root.py").write_text("content")
    (subdir / "l1.py").write_text("content")
    (subsubdir / "l2.py").write_text("content")

    result = await collect_result(
        list_dir.run(ListDirectoryArgs(recursive=True, max_depth=10))
    )

    names = [e.name for e in result.entries]
    assert any("root.py" in n for n in names)
    assert any("l1.py" in n for n in names)
    assert any("l2.py" in n for n in names)


@pytest.mark.asyncio
async def test_respects_max_depth(list_dir, tmp_path):
    l1 = tmp_path / "l1"
    l1.mkdir()
    l2 = l1 / "l2"
    l2.mkdir()
    l3 = l2 / "l3"
    l3.mkdir()
    (l3 / "deep.py").write_text("content")

    result = await collect_result(
        list_dir.run(ListDirectoryArgs(recursive=True, max_depth=2))
    )

    names = [e.name for e in result.entries]
    assert not any("deep.py" in n for n in names)


@pytest.mark.asyncio
async def test_excludes_hidden_by_default(list_dir, tmp_path):
    (tmp_path / ".hidden").write_text("content")
    (tmp_path / "visible.py").write_text("content")

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    names = [e.name for e in result.entries]
    assert "visible.py" in names
    assert ".hidden" not in names


@pytest.mark.asyncio
async def test_includes_hidden_when_requested(list_dir, tmp_path):
    (tmp_path / ".hidden").write_text("content")
    (tmp_path / "visible.py").write_text("content")

    result = await collect_result(
        list_dir.run(ListDirectoryArgs(include_hidden=True))
    )

    names = [e.name for e in result.entries]
    assert "visible.py" in names
    assert ".hidden" in names


@pytest.mark.asyncio
async def test_fails_with_nonexistent_path(list_dir):
    with pytest.raises(ToolError) as err:
        await collect_result(list_dir.run(ListDirectoryArgs(path="nonexistent")))

    assert "Path does not exist" in str(err.value)


@pytest.mark.asyncio
async def test_fails_with_file_path(list_dir, tmp_path):
    (tmp_path / "file.py").write_text("content")

    with pytest.raises(ToolError) as err:
        await collect_result(list_dir.run(ListDirectoryArgs(path="file.py")))

    assert "not a directory" in str(err.value)


@pytest.mark.asyncio
async def test_truncates_to_max_entries(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = ListDirectoryConfig(max_entries=5)
    list_dir = ListDirectory(config=config, state=ListDirectoryState())

    for i in range(10):
        (tmp_path / f"file{i}.py").write_text("content")

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    assert len(result.entries) == 5
    assert result.truncated


@pytest.mark.asyncio
async def test_entries_have_correct_types(list_dir, tmp_path):
    (tmp_path / "file.py").write_text("content")
    (tmp_path / "directory").mkdir()
    (tmp_path / "symlink").symlink_to(tmp_path / "file.py")

    result = await collect_result(
        list_dir.run(ListDirectoryArgs(include_hidden=True))
    )

    entries_by_name = {e.name: e for e in result.entries}

    assert entries_by_name["file.py"].type == "file"
    assert entries_by_name["directory"].type == "directory"
    assert entries_by_name["symlink"].type == "symlink"


@pytest.mark.asyncio
async def test_files_have_size(list_dir, tmp_path):
    (tmp_path / "file.py").write_text("hello world")

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    file_entry = next(e for e in result.entries if e.name == "file.py")
    assert file_entry.size == 11


@pytest.mark.asyncio
async def test_directories_have_no_size(list_dir, tmp_path):
    (tmp_path / "directory").mkdir()

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    dir_entry = next(e for e in result.entries if e.name == "directory")
    assert dir_entry.size is None


@pytest.mark.asyncio
async def test_entries_have_modified_timestamp(list_dir, tmp_path):
    (tmp_path / "file.py").write_text("content")

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    file_entry = next(e for e in result.entries if e.name == "file.py")
    assert file_entry.modified is not None
    assert "T" in file_entry.modified


@pytest.mark.asyncio
async def test_respects_exclude_patterns_recursive(list_dir, tmp_path):
    (tmp_path / "included.py").write_text("content")
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "excluded.js").write_text("content")

    result = await collect_result(
        list_dir.run(ListDirectoryArgs(recursive=True))
    )

    names = [e.name for e in result.entries]
    assert "included.py" in names
    assert not any("node_modules" in n for n in names)


@pytest.mark.asyncio
async def test_respects_gitignore_recursive(list_dir, tmp_path):
    (tmp_path / ".gitignore").write_text("ignored_dir/\n")
    ignored = tmp_path / "ignored_dir"
    ignored.mkdir()
    (ignored / "file.py").write_text("content")
    (tmp_path / "included.py").write_text("content")

    result = await collect_result(
        list_dir.run(ListDirectoryArgs(recursive=True, include_hidden=True))
    )

    names = [e.name for e in result.entries]
    assert "included.py" in names
    assert not any("ignored_dir" in n for n in names)


@pytest.mark.asyncio
async def test_sorted_alphabetically_within_type(list_dir, tmp_path):
    (tmp_path / "zebra.py").write_text("content")
    (tmp_path / "alpha.py").write_text("content")
    (tmp_path / "beta.py").write_text("content")

    result = await collect_result(list_dir.run(ListDirectoryArgs()))

    file_names = [e.name for e in result.entries if e.type == "file"]
    assert file_names == sorted(file_names, key=str.lower)

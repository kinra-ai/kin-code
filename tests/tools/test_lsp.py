from __future__ import annotations

import shutil

import pytest

from kin_code.core.tools.base import ToolError
from kin_code.core.tools.builtins.lsp import (
    LSP,
    LSPArgs,
    LSPOperation,
    LSPState,
    LSPToolConfig,
)
from tests.mock.utils import collect_result


@pytest.fixture
def lsp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = LSPToolConfig()
    tool = LSP(config=config, state=LSPState())
    LSP._servers.clear()
    return tool


@pytest.fixture
def python_file(tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("""
def hello():
    '''Say hello.'''
    print("Hello, world!")

def greet(name: str) -> str:
    return f"Hello, {name}!"

class MyClass:
    def method(self):
        pass
""")
    return file_path


class TestLSPBasics:
    def test_detects_python_language(self, lsp, python_file):
        assert lsp._detect_language(python_file) == "python"

    def test_detects_typescript_language(self, lsp, tmp_path):
        ts_file = tmp_path / "app.ts"
        ts_file.write_text("const x = 1;")
        assert lsp._detect_language(ts_file) == "typescript"

    def test_detects_tsx_language(self, lsp, tmp_path):
        tsx_file = tmp_path / "component.tsx"
        tsx_file.write_text("export const App = () => <div />;")
        assert lsp._detect_language(tsx_file) == "typescript"

    def test_returns_none_for_unknown_language(self, lsp, tmp_path):
        rust_file = tmp_path / "main.rs"
        rust_file.write_text("fn main() {}")
        assert lsp._detect_language(rust_file) is None

    def test_resolves_relative_path(self, lsp, python_file, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        resolved = lsp._resolve_path("test.py")
        assert resolved == python_file

    def test_raises_on_nonexistent_path(self, lsp):
        with pytest.raises(ToolError) as err:
            lsp._resolve_path("nonexistent.py")
        assert "does not exist" in str(err.value)

    def test_raises_on_directory_path(self, lsp, tmp_path):
        with pytest.raises(ToolError) as err:
            lsp._resolve_path(str(tmp_path))
        assert "not a file" in str(err.value)


class TestLSPParsing:
    def test_parse_locations_single(self, lsp):
        response = {
            "uri": "file:///path/to/file.py",
            "range": {
                "start": {"line": 9, "character": 4},
                "end": {"line": 9, "character": 10},
            },
        }

        locations = lsp._parse_locations(response)

        assert len(locations) == 1
        assert locations[0].file_path == "/path/to/file.py"
        assert locations[0].line == 10
        assert locations[0].character == 5

    def test_parse_locations_list(self, lsp):
        response = [
            {
                "uri": "file:///path/to/a.py",
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 5},
                },
            },
            {
                "uri": "file:///path/to/b.py",
                "range": {
                    "start": {"line": 10, "character": 3},
                    "end": {"line": 10, "character": 8},
                },
            },
        ]

        locations = lsp._parse_locations(response)

        assert len(locations) == 2
        assert locations[0].file_path == "/path/to/a.py"
        assert locations[1].file_path == "/path/to/b.py"
        assert locations[1].line == 11

    def test_parse_locations_none(self, lsp):
        assert lsp._parse_locations(None) == []

    def test_parse_locations_empty_list(self, lsp):
        assert lsp._parse_locations([]) == []

    def test_parse_hover_string(self, lsp):
        response = {"contents": "Documentation text"}
        assert lsp._parse_hover(response) == "Documentation text"

    def test_parse_hover_markdown(self, lsp):
        response = {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef hello()\n```\n\nDocstring here.",
            }
        }
        result = lsp._parse_hover(response)
        assert "def hello()" in result

    def test_parse_hover_list(self, lsp):
        response = {"contents": [{"value": "First part"}, {"value": "Second part"}]}
        result = lsp._parse_hover(response)
        assert "First part" in result
        assert "Second part" in result

    def test_parse_hover_none(self, lsp):
        assert lsp._parse_hover(None) is None
        assert lsp._parse_hover({}) is None

    def test_parse_symbols(self, lsp, python_file):
        response = [
            {
                "name": "hello",
                "kind": 12,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 2, "character": 0},
                },
                "children": [],
            },
            {
                "name": "MyClass",
                "kind": 5,
                "range": {
                    "start": {"line": 5, "character": 0},
                    "end": {"line": 10, "character": 0},
                },
                "children": [
                    {
                        "name": "method",
                        "kind": 6,
                        "range": {
                            "start": {"line": 6, "character": 4},
                            "end": {"line": 7, "character": 0},
                        },
                        "children": [],
                    }
                ],
            },
        ]

        symbols = lsp._parse_symbols(response, python_file)

        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "hello" in names
        assert "MyClass" in names
        assert "MyClass.method" in names

    def test_parse_workspace_symbols(self, lsp):
        response = [
            {
                "name": "global_func",
                "kind": 12,
                "location": {
                    "uri": "file:///path/to/utils.py",
                    "range": {
                        "start": {"line": 10, "character": 0},
                        "end": {"line": 15, "character": 0},
                    },
                },
            }
        ]

        symbols = lsp._parse_workspace_symbols(response)

        assert len(symbols) == 1
        assert symbols[0].name == "global_func"
        assert symbols[0].kind == "function"
        assert symbols[0].file_path == "/path/to/utils.py"

    def test_parse_incoming_calls(self, lsp):
        response = [
            {
                "from": {
                    "name": "caller_func",
                    "kind": 12,
                    "uri": "file:///path/to/caller.py",
                    "range": {
                        "start": {"line": 5, "character": 0},
                        "end": {"line": 10, "character": 0},
                    },
                },
                "fromRanges": [],
            }
        ]

        calls = lsp._parse_incoming_calls(response)

        assert len(calls) == 1
        assert calls[0].name == "caller_func"
        assert calls[0].file_path == "/path/to/caller.py"
        assert calls[0].line == 6

    def test_parse_outgoing_calls(self, lsp):
        response = [
            {
                "to": {
                    "name": "callee_func",
                    "kind": 12,
                    "uri": "file:///path/to/callee.py",
                    "range": {
                        "start": {"line": 20, "character": 0},
                        "end": {"line": 25, "character": 0},
                    },
                },
                "fromRanges": [],
            }
        ]

        calls = lsp._parse_outgoing_calls(response)

        assert len(calls) == 1
        assert calls[0].name == "callee_func"
        assert calls[0].line == 21

    def test_symbol_kind_to_string(self, lsp):
        assert lsp._symbol_kind_to_string(5) == "class"
        assert lsp._symbol_kind_to_string(6) == "method"
        assert lsp._symbol_kind_to_string(12) == "function"
        assert lsp._symbol_kind_to_string(13) == "variable"
        assert lsp._symbol_kind_to_string(999) == "unknown"


class TestLSPUIDisplay:
    def test_get_status_text(self):
        assert LSP.get_status_text() == "Running LSP"


@pytest.mark.asyncio
async def test_raises_for_unsupported_file_type(lsp, tmp_path):
    rust_file = tmp_path / "main.rs"
    rust_file.write_text("fn main() {}")

    with pytest.raises(ToolError) as err:
        await collect_result(
            lsp.run(
                LSPArgs(
                    operation=LSPOperation.GO_TO_DEFINITION,
                    file_path=str(rust_file),
                    line=1,
                    character=1,
                )
            )
        )

    assert "No LSP server configured" in str(err.value)


@pytest.mark.asyncio
@pytest.mark.skipif(
    not shutil.which("pyright-langserver"), reason="pyright not installed"
)
async def test_go_to_definition_with_pyright(lsp, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    file_path = tmp_path / "test_def.py"
    file_path.write_text("""def my_function():
    pass

my_function()
""")

    result = await collect_result(
        lsp.run(
            LSPArgs(
                operation=LSPOperation.GO_TO_DEFINITION,
                file_path=str(file_path),
                line=4,
                character=1,
            )
        )
    )

    assert result.operation == LSPOperation.GO_TO_DEFINITION
    assert result.locations is not None
    assert len(result.locations) >= 1


@pytest.mark.asyncio
@pytest.mark.skipif(
    not shutil.which("pyright-langserver"), reason="pyright not installed"
)
async def test_hover_with_pyright(lsp, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    file_path = tmp_path / "test_hover.py"
    file_path.write_text('''def documented():
    """This is a docstring."""
    pass

documented()
''')

    result = await collect_result(
        lsp.run(
            LSPArgs(
                operation=LSPOperation.HOVER,
                file_path=str(file_path),
                line=5,
                character=1,
            )
        )
    )

    assert result.operation == LSPOperation.HOVER


@pytest.mark.asyncio
@pytest.mark.skipif(
    not shutil.which("pyright-langserver"), reason="pyright not installed"
)
async def test_document_symbols_with_pyright(lsp, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    file_path = tmp_path / "test_symbols.py"
    file_path.write_text("""
def function_a():
    pass

def function_b():
    pass

class MyClass:
    def method(self):
        pass
""")

    result = await collect_result(
        lsp.run(
            LSPArgs(
                operation=LSPOperation.DOCUMENT_SYMBOL,
                file_path=str(file_path),
                line=1,
                character=1,
            )
        )
    )

    assert result.operation == LSPOperation.DOCUMENT_SYMBOL
    assert result.symbols is not None
    names = [s.name for s in result.symbols]
    assert "function_a" in names
    assert "function_b" in names


@pytest.mark.asyncio
@pytest.mark.skipif(
    not shutil.which("pyright-langserver"), reason="pyright not installed"
)
async def test_find_references_with_pyright(lsp, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    file_path = tmp_path / "test_refs.py"
    file_path.write_text("""def target():
    pass

target()
target()
""")

    result = await collect_result(
        lsp.run(
            LSPArgs(
                operation=LSPOperation.FIND_REFERENCES,
                file_path=str(file_path),
                line=1,
                character=5,
            )
        )
    )

    assert result.operation == LSPOperation.FIND_REFERENCES
    assert result.locations is not None

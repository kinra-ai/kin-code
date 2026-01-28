from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import StrEnum, auto
import json
from pathlib import Path
import shutil
from typing import TYPE_CHECKING, Any, ClassVar

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


class LSPOperation(StrEnum):
    GO_TO_DEFINITION = auto()
    FIND_REFERENCES = auto()
    HOVER = auto()
    DOCUMENT_SYMBOL = auto()
    WORKSPACE_SYMBOL = auto()
    GO_TO_IMPLEMENTATION = auto()
    INCOMING_CALLS = auto()
    OUTGOING_CALLS = auto()


@dataclass
class LSPServerConfig:
    command: list[str]
    languages: list[str] = field(default_factory=list)


@dataclass
class LSPServerProcess:
    process: asyncio.subprocess.Process
    request_id: int = 0
    initialized: bool = False


@dataclass
class _OperationContext:
    server: LSPServerProcess
    args: LSPArgs
    file_path: Path
    position: dict[str, int]
    text_document: dict[str, str]
    text_document_position: dict[str, Any]


LANGUAGE_SERVERS: dict[str, LSPServerConfig] = {
    "python": LSPServerConfig(
        command=["pyright-langserver", "--stdio"], languages=["py"]
    ),
    "typescript": LSPServerConfig(
        command=["typescript-language-server", "--stdio"],
        languages=["ts", "tsx", "js", "jsx"],
    ),
}

EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "typescript",
    ".jsx": "typescript",
}


class LSPToolConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS

    timeout: int = Field(default=30, description="Timeout for LSP requests in seconds.")
    max_references: int = Field(default=50, description="Maximum references to return.")
    max_symbols: int = Field(default=100, description="Maximum symbols to return.")


class LSPState(BaseToolState):
    pass


class Location(BaseModel):
    file_path: str = Field(description="Path to the file")
    line: int = Field(description="1-based line number")
    character: int = Field(description="1-based character offset")
    end_line: int | None = Field(default=None, description="End line if range")
    end_character: int | None = Field(
        default=None, description="End character if range"
    )


class Symbol(BaseModel):
    name: str = Field(description="Symbol name")
    kind: str = Field(description="Symbol kind (function, class, variable, etc.)")
    file_path: str = Field(description="File containing the symbol")
    line: int = Field(description="1-based line number")
    character: int = Field(description="1-based character offset")


class CallItem(BaseModel):
    name: str = Field(description="Function/method name")
    file_path: str = Field(description="File containing the function")
    line: int = Field(description="1-based line number")


class LSPArgs(BaseModel):
    operation: LSPOperation = Field(description="The LSP operation to perform")
    file_path: str = Field(description="The file to operate on")
    line: int = Field(ge=1, description="1-based line number")
    character: int = Field(ge=1, description="1-based character offset")
    query: str | None = Field(
        default=None, description="Query for workspace symbol search"
    )


class LSPResult(BaseModel):
    operation: LSPOperation = Field(description="The operation performed")
    locations: list[Location] | None = Field(
        default=None, description="For definition/references/implementation"
    )
    hover_content: str | None = Field(default=None, description="For hover")
    symbols: list[Symbol] | None = Field(
        default=None, description="For document/workspace symbols"
    )
    call_items: list[CallItem] | None = Field(
        default=None, description="For call hierarchy"
    )
    message: str | None = Field(default=None, description="Human-readable summary")


class LSP(
    BaseTool[LSPArgs, LSPResult, LSPToolConfig, LSPState],
    ToolUIData[LSPArgs, LSPResult],
):
    description: ClassVar[
        str
    ] = """Language Server Protocol operations for code intelligence.

USE WHEN:
- Finding where a symbol is defined (goToDefinition)
- Finding all references to a symbol (findReferences)
- Getting hover information/documentation (hover)
- Finding all symbols in a file (documentSymbol)
- Searching symbols across the workspace (workspaceSymbol)
- Finding implementations of an interface (goToImplementation)
- Finding what calls a function (incomingCalls)
- Finding what a function calls (outgoingCalls)

DO NOT USE WHEN:
- Searching for text patterns (use grep)
- Reading file contents (use read_file)
- Finding files by name (use glob)

EXAMPLES:
- operation="go_to_definition", file_path="src/main.py", line=10, character=5
- operation="find_references", file_path="src/utils.py", line=25, character=8
- operation="hover", file_path="src/api.py", line=15, character=12

NOTES:
- Requires language server to be installed (pyright for Python)
- Line and character numbers are 1-based
- Supports Python and TypeScript/JavaScript
- Server is started lazily on first use"""

    _servers: ClassVar[dict[str, LSPServerProcess]] = {}

    async def run(
        self, args: LSPArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | LSPResult, None]:
        file_path = self._resolve_path(args.file_path)
        language = self._detect_language(file_path)

        if language is None:
            raise ToolError(
                f"No LSP server configured for file type: {file_path.suffix}"
            )

        server = await self._ensure_server(language, file_path.parent)

        result = await self._execute_operation(server, args, file_path, language)
        yield result

    def _resolve_path(self, path: str) -> Path:
        path_obj = Path(path).expanduser()
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj

        if not path_obj.exists():
            raise ToolError(f"File does not exist: {path}")
        if not path_obj.is_file():
            raise ToolError(f"Path is not a file: {path}")

        return path_obj

    def _detect_language(self, file_path: Path) -> str | None:
        suffix = file_path.suffix.lower()
        return EXTENSION_TO_LANGUAGE.get(suffix)

    async def _ensure_server(
        self, language: str, workspace_root: Path
    ) -> LSPServerProcess:
        if language in LSP._servers:
            server = LSP._servers[language]
            if server.process.returncode is None:
                return server
            del LSP._servers[language]

        server_config = LANGUAGE_SERVERS.get(language)
        if server_config is None:
            raise ToolError(f"No LSP server configured for language: {language}")

        command = server_config.command
        if not shutil.which(command[0]):
            raise ToolError(
                f"LSP server not found: {command[0]}. "
                f"Install it with: pip install pyright (for Python) "
                f"or npm install -g typescript-language-server (for TypeScript)"
            )

        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workspace_root),
        )

        server = LSPServerProcess(process=process)
        LSP._servers[language] = server

        await self._initialize_server(server, workspace_root)

        return server

    async def _initialize_server(
        self, server: LSPServerProcess, workspace_root: Path
    ) -> None:
        init_params = {
            "processId": None,
            "rootUri": workspace_root.as_uri(),
            "rootPath": str(workspace_root),
            "capabilities": {
                "textDocument": {
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "definition": {"linkSupport": True},
                    "references": {},
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "callHierarchy": {},
                },
                "workspace": {"symbol": {"symbolKind": {}}},
            },
        }

        await self._send_request(server, "initialize", init_params)
        await self._send_notification(server, "initialized", {})
        server.initialized = True

    async def _send_request(
        self, server: LSPServerProcess, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        server.request_id += 1
        request_id = server.request_id

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"

        if server.process.stdin is None:
            raise ToolError("LSP server stdin not available")

        server.process.stdin.write((header + content).encode())
        await server.process.stdin.drain()

        response = await self._read_response(server, request_id)
        return response

    async def _send_notification(
        self, server: LSPServerProcess, method: str, params: dict[str, Any]
    ) -> None:
        message = {"jsonrpc": "2.0", "method": method, "params": params}

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"

        if server.process.stdin is None:
            raise ToolError("LSP server stdin not available")

        server.process.stdin.write((header + content).encode())
        await server.process.stdin.drain()

    async def _read_response(
        self, server: LSPServerProcess, expected_id: int
    ) -> dict[str, Any]:
        if server.process.stdout is None:
            raise ToolError("LSP server stdout not available")

        try:
            return await self._read_response_loop(server, expected_id)
        except TimeoutError:
            raise ToolError(f"LSP request timed out after {self.config.timeout}s")

    async def _read_response_loop(
        self, server: LSPServerProcess, expected_id: int
    ) -> dict[str, Any]:
        stdout = server.process.stdout
        assert stdout is not None

        while True:
            header_line = await asyncio.wait_for(
                stdout.readline(), timeout=self.config.timeout
            )
            if not header_line:
                raise ToolError("LSP server closed connection")

            header = header_line.decode().strip()
            if not header.startswith("Content-Length:"):
                continue

            content_length = int(header.split(":")[1].strip())
            await stdout.readline()

            content = await asyncio.wait_for(
                stdout.read(content_length), timeout=self.config.timeout
            )
            response = json.loads(content.decode())

            if response.get("id") != expected_id:
                continue

            if "error" in response:
                error = response["error"]
                raise ToolError(f"LSP error: {error.get('message', 'Unknown error')}")

            return response.get("result", {})

    async def _execute_operation(
        self, server: LSPServerProcess, args: LSPArgs, file_path: Path, language: str
    ) -> LSPResult:
        await self._open_document(server, file_path, language)

        position = {"line": args.line - 1, "character": args.character - 1}
        text_document = {"uri": file_path.as_uri()}
        text_document_position = {"textDocument": text_document, "position": position}

        ctx = _OperationContext(
            server=server,
            args=args,
            file_path=file_path,
            position=position,
            text_document=text_document,
            text_document_position=text_document_position,
        )

        handlers = {
            LSPOperation.GO_TO_DEFINITION: self._op_go_to_definition,
            LSPOperation.FIND_REFERENCES: self._op_find_references,
            LSPOperation.HOVER: self._op_hover,
            LSPOperation.DOCUMENT_SYMBOL: self._op_document_symbol,
            LSPOperation.WORKSPACE_SYMBOL: self._op_workspace_symbol,
            LSPOperation.GO_TO_IMPLEMENTATION: self._op_go_to_implementation,
            LSPOperation.INCOMING_CALLS: self._op_incoming_calls,
            LSPOperation.OUTGOING_CALLS: self._op_outgoing_calls,
        }

        handler = handlers[args.operation]
        return await handler(ctx)

    async def _op_go_to_definition(self, ctx: _OperationContext) -> LSPResult:
        response = await self._send_request(
            ctx.server, "textDocument/definition", ctx.text_document_position
        )
        locations = self._parse_locations(response)
        return LSPResult(
            operation=ctx.args.operation,
            locations=locations,
            message=f"Found {len(locations)} definition(s)",
        )

    async def _op_find_references(self, ctx: _OperationContext) -> LSPResult:
        params = {**ctx.text_document_position, "context": {"includeDeclaration": True}}
        response = await self._send_request(
            ctx.server, "textDocument/references", params
        )
        locations = self._parse_locations(response)[: self.config.max_references]
        return LSPResult(
            operation=ctx.args.operation,
            locations=locations,
            message=f"Found {len(locations)} reference(s)",
        )

    async def _op_hover(self, ctx: _OperationContext) -> LSPResult:
        response = await self._send_request(
            ctx.server, "textDocument/hover", ctx.text_document_position
        )
        hover_content = self._parse_hover(response)
        return LSPResult(
            operation=ctx.args.operation,
            hover_content=hover_content,
            message="Hover information retrieved"
            if hover_content
            else "No hover information",
        )

    async def _op_document_symbol(self, ctx: _OperationContext) -> LSPResult:
        response = await self._send_request(
            ctx.server,
            "textDocument/documentSymbol",
            {"textDocument": ctx.text_document},
        )
        symbols = self._parse_symbols(response, ctx.file_path)[
            : self.config.max_symbols
        ]
        return LSPResult(
            operation=ctx.args.operation,
            symbols=symbols,
            message=f"Found {len(symbols)} symbol(s)",
        )

    async def _op_workspace_symbol(self, ctx: _OperationContext) -> LSPResult:
        query = ctx.args.query or ""
        response = await self._send_request(
            ctx.server, "workspace/symbol", {"query": query}
        )
        symbols = self._parse_workspace_symbols(response)[: self.config.max_symbols]
        return LSPResult(
            operation=ctx.args.operation,
            symbols=symbols,
            message=f"Found {len(symbols)} symbol(s)",
        )

    async def _op_go_to_implementation(self, ctx: _OperationContext) -> LSPResult:
        response = await self._send_request(
            ctx.server, "textDocument/implementation", ctx.text_document_position
        )
        locations = self._parse_locations(response)
        return LSPResult(
            operation=ctx.args.operation,
            locations=locations,
            message=f"Found {len(locations)} implementation(s)",
        )

    async def _op_incoming_calls(self, ctx: _OperationContext) -> LSPResult:
        prep_response = await self._send_request(
            ctx.server, "textDocument/prepareCallHierarchy", ctx.text_document_position
        )
        if not prep_response:
            return LSPResult(
                operation=ctx.args.operation,
                call_items=[],
                message="No call hierarchy item at position",
            )

        items = prep_response if isinstance(prep_response, list) else [prep_response]
        all_calls: list[CallItem] = []
        for item in items:
            calls_response = await self._send_request(
                ctx.server, "callHierarchy/incomingCalls", {"item": item}
            )
            all_calls.extend(self._parse_incoming_calls(calls_response))

        return LSPResult(
            operation=ctx.args.operation,
            call_items=all_calls,
            message=f"Found {len(all_calls)} incoming call(s)",
        )

    async def _op_outgoing_calls(self, ctx: _OperationContext) -> LSPResult:
        prep_response = await self._send_request(
            ctx.server, "textDocument/prepareCallHierarchy", ctx.text_document_position
        )
        if not prep_response:
            return LSPResult(
                operation=ctx.args.operation,
                call_items=[],
                message="No call hierarchy item at position",
            )

        items = prep_response if isinstance(prep_response, list) else [prep_response]
        all_calls: list[CallItem] = []
        for item in items:
            calls_response = await self._send_request(
                ctx.server, "callHierarchy/outgoingCalls", {"item": item}
            )
            all_calls.extend(self._parse_outgoing_calls(calls_response))

        return LSPResult(
            operation=ctx.args.operation,
            call_items=all_calls,
            message=f"Found {len(all_calls)} outgoing call(s)",
        )

    async def _open_document(
        self, server: LSPServerProcess, file_path: Path, language: str
    ) -> None:
        try:
            content = file_path.read_text("utf-8")
        except OSError as e:
            raise ToolError(f"Failed to read file: {e}")

        params = {
            "textDocument": {
                "uri": file_path.as_uri(),
                "languageId": language,
                "version": 1,
                "text": content,
            }
        }
        await self._send_notification(server, "textDocument/didOpen", params)

    def _parse_locations(self, response: Any) -> list[Location]:
        if response is None:
            return []

        items = response if isinstance(response, list) else [response]
        locations = []

        for item in items:
            if item is None:
                continue

            uri = item.get("uri") or item.get("targetUri")
            if not uri:
                continue

            file_path = uri.replace("file://", "")

            range_data = item.get("range") or item.get("targetSelectionRange")
            if range_data:
                start = range_data.get("start", {})
                end = range_data.get("end", {})
                locations.append(
                    Location(
                        file_path=file_path,
                        line=start.get("line", 0) + 1,
                        character=start.get("character", 0) + 1,
                        end_line=end.get("line", 0) + 1,
                        end_character=end.get("character", 0) + 1,
                    )
                )
            else:
                locations.append(Location(file_path=file_path, line=1, character=1))

        return locations

    def _parse_hover(self, response: Any) -> str | None:
        if response is None:
            return None

        contents = response.get("contents")
        if contents is None:
            return None

        if isinstance(contents, str):
            return contents

        if isinstance(contents, dict):
            return contents.get("value", str(contents))

        if isinstance(contents, list):
            parts = []
            for item in contents:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(item.get("value", str(item)))
            return "\n".join(parts)

        return str(contents)

    def _parse_symbols(self, response: Any, file_path: Path) -> list[Symbol]:
        if response is None:
            return []

        items = response if isinstance(response, list) else [response]
        symbols = []

        def process_symbol(item: dict[str, Any], parent_name: str = "") -> None:
            name = item.get("name", "")
            if parent_name:
                name = f"{parent_name}.{name}"

            kind = self._symbol_kind_to_string(item.get("kind", 0))

            range_data = item.get("range") or item.get("location", {}).get("range", {})
            start = range_data.get("start", {})

            symbols.append(
                Symbol(
                    name=name,
                    kind=kind,
                    file_path=str(file_path),
                    line=start.get("line", 0) + 1,
                    character=start.get("character", 0) + 1,
                )
            )

            for child in item.get("children", []):
                process_symbol(child, name)

        for item in items:
            if item:
                process_symbol(item)

        return symbols

    def _parse_workspace_symbols(self, response: Any) -> list[Symbol]:
        if response is None:
            return []

        items = response if isinstance(response, list) else [response]
        symbols = []

        for item in items:
            if item is None:
                continue

            location = item.get("location", {})
            uri = location.get("uri", "")
            file_path = uri.replace("file://", "")

            range_data = location.get("range", {})
            start = range_data.get("start", {})

            symbols.append(
                Symbol(
                    name=item.get("name", ""),
                    kind=self._symbol_kind_to_string(item.get("kind", 0)),
                    file_path=file_path,
                    line=start.get("line", 0) + 1,
                    character=start.get("character", 0) + 1,
                )
            )

        return symbols

    def _parse_incoming_calls(self, response: Any) -> list[CallItem]:
        if response is None:
            return []

        items = response if isinstance(response, list) else [response]
        calls = []

        for item in items:
            if item is None:
                continue

            from_item = item.get("from", {})
            uri = from_item.get("uri", "")
            file_path = uri.replace("file://", "")

            range_data = from_item.get("range", {})
            start = range_data.get("start", {})

            calls.append(
                CallItem(
                    name=from_item.get("name", ""),
                    file_path=file_path,
                    line=start.get("line", 0) + 1,
                )
            )

        return calls

    def _parse_outgoing_calls(self, response: Any) -> list[CallItem]:
        if response is None:
            return []

        items = response if isinstance(response, list) else [response]
        calls = []

        for item in items:
            if item is None:
                continue

            to_item = item.get("to", {})
            uri = to_item.get("uri", "")
            file_path = uri.replace("file://", "")

            range_data = to_item.get("range", {})
            start = range_data.get("start", {})

            calls.append(
                CallItem(
                    name=to_item.get("name", ""),
                    file_path=file_path,
                    line=start.get("line", 0) + 1,
                )
            )

        return calls

    def _symbol_kind_to_string(self, kind: int) -> str:
        kinds = {
            1: "file",
            2: "module",
            3: "namespace",
            4: "package",
            5: "class",
            6: "method",
            7: "property",
            8: "field",
            9: "constructor",
            10: "enum",
            11: "interface",
            12: "function",
            13: "variable",
            14: "constant",
            15: "string",
            16: "number",
            17: "boolean",
            18: "array",
            19: "object",
            20: "key",
            21: "null",
            22: "enum_member",
            23: "struct",
            24: "event",
            25: "operator",
            26: "type_parameter",
        }
        return kinds.get(kind, "unknown")

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, LSPArgs):
            return ToolCallDisplay(summary="lsp")

        op_name = event.args.operation.name.lower().replace("_", " ")
        summary = f"LSP {op_name} at {event.args.file_path}:{event.args.line}"

        return ToolCallDisplay(summary=summary)

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, LSPResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )

        return ToolResultDisplay(
            success=True, message=event.result.message or "LSP operation completed"
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Running LSP"

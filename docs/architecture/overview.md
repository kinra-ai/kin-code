# Architecture Overview

This document provides a comprehensive overview of Kin Code's architecture, explaining how components interact to create an AI coding assistant powered by LLM backends.

## Table of Contents

- [System Overview](#system-overview)
- [Core Components](#core-components)
- [Conversation Flow](#conversation-flow)
- [Tool System](#tool-system)
- [Middleware Pipeline](#middleware-pipeline)
- [Backend Architecture](#backend-architecture)
- [Configuration System](#configuration-system)
- [Event System](#event-system)
- [Session Management](#session-management)
- [Extension Points](#extension-points)

## System Overview

Kin Code is built as a layered architecture that orchestrates LLM interactions, tool execution, and conversation management.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                       │
│                    (TUI / Programmatic)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                          Agent                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Middleware  │  │ Tool Manager │  │ Config Mgr   │     │
│  │   Pipeline   │  └──────────────┘  └──────────────┘     │
│  └──────────────┘                                          │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐    ┌─────────────────────────────┐
│    LLM Backend         │    │      Tool Execution         │
│  ┌──────────────────┐  │    │  ┌────────┐  ┌──────────┐  │
│  │ Generic/Mistral  │  │    │  │ Built-in│ │  MCP     │  │
│  │    Adapters      │  │    │  │  Tools │  │  Proxy   │  │
│  └──────────────────┘  │    │  └────────┘  └──────────┘  │
└────────────┬───────────┘    └─────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Provider APIs (OpenAI, Mistral, etc.)          │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Provider Abstraction**: LLM providers are abstracted through a unified `BackendLike` protocol
2. **Event-Driven**: Conversation turns emit typed events for UI rendering and logging
3. **Middleware Composition**: Behavior can be modified through composable middleware
4. **Tool Discoverability**: Tools are discovered dynamically from search paths
5. **Configuration Layering**: Settings cascade from defaults → config file → env vars → runtime overrides

## Core Components

### Agent (`kin_code/core/agent.py`)

The `Agent` class is the central orchestrator that coordinates all system components.

**Key Responsibilities:**
- Manages conversation history (list of `LLMMessage`)
- Orchestrates conversation turns through `_conversation_loop`
- Coordinates middleware execution (before/after turn)
- Invokes LLM backend for completions
- Parses and executes tool calls
- Tracks session statistics and costs
- Handles context compaction when limits are reached

**Initialization:**
```python
agent = Agent(
    config=config,
    mode=AgentMode.DEFAULT,
    message_observer=callback,
    max_turns=10,
    max_price=1.0,
    backend=custom_backend,
    enable_streaming=True
)
```

**Key Methods:**
- `act(msg)`: Process a user message and yield events
- `compact()`: Summarize conversation history to reduce context
- `clear_history()`: Reset conversation and session
- `switch_mode(mode)`: Change operating mode
- `set_approval_callback(callback)`: Register tool approval handler

### Tool Manager (`kin_code/core/tools/manager.py`)

Discovers and manages tool instances for the agent.

**Tool Discovery:**
1. Scans default tools directory (`kin_code/core/tools/default`)
2. Scans user-configured tool paths
3. Scans local `.kin-code/tools/` directory
4. Scans global `~/.kin-code/tools/` directory
5. Integrates MCP (Model Context Protocol) servers

**Tool Lifecycle:**
- Tools are discovered at initialization
- Instances are created lazily on first use
- Configuration is merged from defaults + user overrides
- Instances are cached for reuse within a session

**MCP Integration:**
```python
# HTTP-based MCP tools
await _register_http_server(srv)  # List tools via HTTP, create proxy classes

# Stdio-based MCP tools
await _register_stdio_server(srv)  # Spawn subprocess, create proxy classes
```

### Configuration (`kin_code/core/config.py`)

Multi-source configuration system with precedence hierarchy.

**Configuration Sources (highest to lowest priority):**
1. Runtime overrides (passed to `Agent` constructor)
2. Environment variables (prefixed with `KIN_`)
3. TOML configuration file (`~/.kin-code/config.toml`)
4. Agent-specific TOML files (`~/.kin-code/agents/{name}.toml`)
5. Defaults

**Key Configuration Areas:**
- **Models**: Available LLMs with pricing and capabilities
- **Providers**: API endpoints and authentication
- **Tools**: Per-tool settings (permission, allowlist, denylist)
- **MCP Servers**: Remote tool servers
- **Project Context**: Context window management
- **Session Logging**: Interaction persistence

### LLM Backend (`kin_code/core/llm/backend/`)

Abstraction layer for LLM provider APIs.

**Backend Types:**
- **GenericBackend**: OpenAI-compatible APIs (OpenRouter, local llama.cpp, etc.)
- **MistralBackend**: Mistral-specific API features

**API Adapters:**
```python
# OpenAI-compatible adapter
@register_adapter(BACKEND_ADAPTERS, "openai")
class OpenAIAdapter:
    def prepare_request(...) -> PreparedRequest
    def parse_response(...) -> LLMChunk
```

**Backend Protocol:**
```python
class BackendLike(Protocol):
    async def complete(...) -> LLMChunk
    def complete_streaming(...) -> AsyncGenerator[LLMChunk]
    async def count_tokens(...) -> int
```

### Middleware (`kin_code/core/middleware.py`)

Interceptors that run before/after conversation turns.

**Built-in Middleware:**
- `TurnLimitMiddleware`: Stops after N turns
- `PriceLimitMiddleware`: Stops when cost exceeds threshold
- `AutoCompactMiddleware`: Triggers compaction at token threshold
- `ContextWarningMiddleware`: Warns when approaching context limit
- `PlanModeMiddleware`: Enforces read-only behavior in plan mode

**Middleware Actions:**
- `CONTINUE`: Proceed normally
- `STOP`: Halt execution with reason
- `COMPACT`: Trigger context compaction
- `INJECT_MESSAGE`: Add content to last user message

## Conversation Flow

### Request Processing Sequence

```
User Input
    │
    ▼
┌────────────────────────────────┐
│ 1. Add user message to history│
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 2. Run before-turn middleware  │
│    - Check turn/price limits   │
│    - Inject plan mode reminder │
│    - Check for compaction      │
└────────┬───────────────────────┘
         │
         ├─[STOP]──────────────────> Stop Execution
         ├─[COMPACT]───────────────> Compact History
         │
         ▼
┌────────────────────────────────┐
│ 3. Call LLM Backend            │
│    - Prepare request payload   │
│    - Send to provider API      │
│    - Parse response            │
│    - Update statistics         │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 4. Parse Tool Calls            │
│    - Extract function calls    │
│    - Validate arguments        │
│    - Resolve tool instances    │
└────────┬───────────────────────┘
         │
         ├─[No Tools]──────────────> Done (assistant message)
         │
         ▼
┌────────────────────────────────┐
│ 5. Check Tool Permissions      │
│    - Allowlist/Denylist        │
│    - Permission level (ASK)    │
│    - Approval callback         │
└────────┬───────────────────────┘
         │
         ├─[Rejected]──────────────> Add error message
         │
         ▼
┌────────────────────────────────┐
│ 6. Execute Tool                │
│    - Invoke tool.run(args)     │
│    - Capture result/error      │
│    - Format as tool response   │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 7. Add tool response to history│
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ 8. Run after-turn middleware   │
└────────┬───────────────────────┘
         │
         ├─[Role=tool]─────────────> Loop back to step 2 (continue with LLM)
         │
         ▼
     Done (assistant message)
```

### Streaming Flow

When `enable_streaming=True`:

```python
async for chunk in backend.complete_streaming(...):
    # Accumulate chunks
    content_buffer += chunk.message.content
    reasoning_buffer += chunk.message.reasoning_content

    # Yield events in batches (every 5 chunks)
    if chunks >= BATCH_SIZE:
        yield AssistantEvent(content=content_buffer)
        content_buffer = ""
```

### Message Format

All messages follow the `LLMMessage` structure:

```python
LLMMessage(
    role: Role,                        # system, user, assistant, tool
    content: str | None,               # Main content
    reasoning_content: str | None,     # Reasoning/thinking content
    tool_calls: list[ToolCall] | None, # Function calls
    name: str | None,                  # Tool name (for role=tool)
    tool_call_id: str | None,          # Reference to tool call
)
```

## Tool System

### Tool Architecture

```
┌───────────────────────────────────────────────────────────┐
│                      ToolManager                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Tool Discovery                                     │ │
│  │  - Scan search paths for *.py files                │ │
│  │  - Import and inspect classes                      │ │
│  │  - Filter BaseTool subclasses                      │ │
│  │  - Integrate MCP servers                           │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Available Tools: {name: class}                          │
│  Tool Instances: {name: instance} (lazy cache)           │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│                   BaseTool[Args, Result, Config, State]   │
│                                                           │
│  Class Variables:                                        │
│  - description: str (shown to LLM)                       │
│  - prompt_path: Path (tool-specific prompt)              │
│                                                           │
│  Instance:                                               │
│  - config: ToolConfig (permission, workdir, etc.)        │
│  - state: ToolState (persistent state)                   │
│                                                           │
│  Methods:                                                │
│  - async run(args) -> result                             │
│  - get_info() -> ToolInfo (name, description, schema)    │
│  - check_allowlist_denylist(args) -> ToolPermission      │
└───────────────────────────────────────────────────────────┘
```

### Tool Execution Flow

```
LLM returns tool_calls
    │
    ▼
┌─────────────────────────────────┐
│ Parse & Validate Arguments      │
│ - JSON decode arguments string  │
│ - Validate against Pydantic     │
│ - Capture validation errors     │
└────────┬────────────────────────┘
         │
         ├─[ValidationError]────────> ToolResultEvent(error=...)
         │
         ▼
┌─────────────────────────────────┐
│ Get Tool Instance               │
│ - Retrieve from cache or create │
│ - Merge config with defaults    │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Permission Check                │
│ 1. Check auto_approve mode      │
│ 2. Check allowlist patterns     │
│ 3. Check denylist patterns      │
│ 4. Check tool permission level  │
│ 5. Call approval callback       │
└────────┬────────────────────────┘
         │
         ├─[ALWAYS]─────────────────> Execute
         ├─[NEVER]──────────────────> Skip (add error message)
         ├─[ASK]────────────────────> Approval callback
         │
         ▼
┌─────────────────────────────────┐
│ Execute Tool                    │
│ result = await tool.run(args)   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Format Result                   │
│ - Convert to string             │
│ - Create tool response message │
│ - Emit ToolResultEvent          │
└─────────────────────────────────┘
```

### Tool Schema Generation

Tools automatically generate JSON schemas for LLM function calling:

```python
# From tool class:
class Grep(BaseTool[GrepArgs, GrepResult, ...]):
    description = "Search for patterns in files"

# Generates schema:
{
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search for patterns in files\n\n[Tool-specific prompt content]",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "..."},
                "path": {"type": "string", "description": "..."},
                ...
            },
            "required": ["pattern"]
        }
    }
}
```

### MCP Tool Proxies

MCP servers expose tools over HTTP or stdio. Kin Code creates proxy tool classes:

```python
# HTTP MCP Tool
class MCPHttpProxyTool(BaseTool):
    async def run(self, args):
        # Make HTTP request to MCP server
        response = await http_client.post(url, json={
            "method": "tools/call",
            "params": {
                "name": self.remote_name,
                "arguments": args.model_dump()
            }
        })
        return parse_response(response)

# Stdio MCP Tool
class MCPStdioProxyTool(BaseTool):
    async def run(self, args):
        # Send JSON-RPC over stdio
        request = {"method": "tools/call", "params": {...}}
        await process.stdin.write(json.dumps(request))
        response = await process.stdout.readline()
        return parse_response(response)
```

## Middleware Pipeline

### Pipeline Execution Model

```
┌──────────────────────────────────────────────────────────┐
│                 MiddlewarePipeline                       │
│                                                          │
│  Middlewares: [MW1, MW2, MW3, ...]                      │
│                                                          │
│  async run_before_turn(context):                        │
│      for middleware in middlewares:                     │
│          result = await middleware.before_turn(context) │
│          if result.action == STOP/COMPACT:              │
│              return result  # Early exit                │
│          if result.action == INJECT_MESSAGE:            │
│              accumulate message                         │
│      return combined result                             │
│                                                          │
│  async run_after_turn(context):                         │
│      for middleware in middlewares:                     │
│          result = await middleware.after_turn(context)  │
│          if result.action == STOP/COMPACT:              │
│              return result  # Early exit                │
│      return CONTINUE                                    │
└──────────────────────────────────────────────────────────┘
```

### Middleware Interface

```python
class ConversationMiddleware(Protocol):
    async def before_turn(self, context: ConversationContext) -> MiddlewareResult
    async def after_turn(self, context: ConversationContext) -> MiddlewareResult
    def reset(self, reset_reason: ResetReason) -> None
```

### Context Structure

```python
@dataclass
class ConversationContext:
    messages: list[LLMMessage]  # Full conversation history
    stats: AgentStats           # Token usage, costs, timing
    config: KinConfig           # Configuration snapshot
```

### Example: TurnLimitMiddleware

```python
class TurnLimitMiddleware:
    def __init__(self, max_turns: int):
        self.max_turns = max_turns

    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        if context.stats.steps - 1 >= self.max_turns:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason=f"Turn limit of {self.max_turns} reached"
            )
        return MiddlewareResult()  # CONTINUE
```

## Backend Architecture

### Provider Abstraction Layers

```
┌────────────────────────────────────────────────────────┐
│                   Agent (Consumer)                     │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼ BackendLike Protocol
┌────────────────────────────────────────────────────────┐
│              Backend Implementation                    │
│  ┌────────────────┐         ┌────────────────┐        │
│  │ GenericBackend │         │ MistralBackend │        │
│  └────────┬───────┘         └────────┬───────┘        │
│           │                          │                │
│           ▼                          ▼                │
│  ┌─────────────────────────────────────────────────┐  │
│  │          API Adapter Registry                   │  │
│  │  - OpenAIAdapter (default)                      │  │
│  │  - Custom adapters via registration             │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                 │
                 ▼ HTTP/HTTPS
┌────────────────────────────────────────────────────────┐
│               Provider API                             │
│  (OpenAI, Mistral, OpenRouter, llama.cpp, etc.)       │
└────────────────────────────────────────────────────────┘
```

### Request Preparation

```python
# 1. Adapter prepares request
prepared = adapter.prepare_request(
    model_name=model.name,
    messages=messages,
    temperature=temperature,
    tools=available_tools,
    tool_choice=tool_choice,
    enable_streaming=False,
    provider=provider,
    api_key=api_key
)

# 2. Backend adds provider-specific headers
headers.update({
    "user-agent": get_user_agent(provider.backend),
    "x-affinity": session_id,  # Session affinity for load balancing
})

# 3. Make HTTP request
response = await client.post(url, content=prepared.body, headers=headers)

# 4. Parse response through adapter
chunk = adapter.parse_response(response.json(), provider)
```

### Retry Logic

Backends use retry decorators for resilience:

```python
@async_retry(tries=3)
async def _make_request(self, url: str, data: bytes, headers: dict) -> HTTPResponse:
    response = await client.post(url, content=data, headers=headers)
    response.raise_for_status()
    return HTTPResponse(response.json(), dict(response.headers))

@async_generator_retry(tries=3)
async def _make_streaming_request(self, url: str, ...) -> AsyncGenerator[dict]:
    async with client.stream("POST", url, ...) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            yield parse_sse_line(line)
```

### Error Handling

```python
try:
    result = await backend.complete(...)
except httpx.HTTPStatusError as e:
    raise BackendErrorBuilder.build_http_error(
        provider=provider.name,
        endpoint=url,
        response=e.response,
        model=model.name,
        ...
    )
except httpx.RequestError as e:
    raise BackendErrorBuilder.build_request_error(
        provider=provider.name,
        error=e,
        ...
    )
```

## Configuration System

### Configuration Precedence

```
Runtime Overrides (highest)
    │
    ├─> Environment Variables (KIN_*)
    │       │
    │       ├─> TOML Config File (~/.kin-code/config.toml)
    │       │       │
    │       │       ├─> Agent TOML (~/.kin-code/agents/{name}.toml)
    │       │       │       │
    │       │       │       └─> Defaults (lowest)
```

### Configuration Loading

```python
# 1. Load base config with defaults
config = KinConfig.load(
    agent="custom",           # Load custom agent config
    workdir="/path/to/project",
    active_model="devstral-2"
)

# 2. Mode-specific overrides
new_config = KinConfig.load(
    workdir=config.workdir,
    **AgentMode.PLAN.config_overrides  # Apply mode overrides
)

# 3. Save updates
KinConfig.save_updates({
    "active_model": "devstral-small",
    "tools": {
        "bash": {"permission": "always"}
    }
})
```

### Tool Configuration Merging

```python
# 1. Get tool's default config
default_config = tool_class._get_tool_config_class()()

# 2. Get user overrides from config.toml
user_overrides = config.tools.get(tool_name)

# 3. Merge (user overrides win)
merged_dict = {
    **default_config.model_dump(),
    **user_overrides.model_dump()
}

# 4. Apply global workdir
if config.workdir is not None:
    merged_dict["workdir"] = config.workdir

# 5. Validate and instantiate
tool_config = config_class.model_validate(merged_dict)
```

### Validation Hooks

Configuration validates on load:

```python
@model_validator(mode="after")
def _check_api_key(self) -> KinConfig:
    # Ensure required API keys are present
    provider = self.get_provider_for_model(self.get_active_model())
    if provider.api_key_env_var and not os.getenv(provider.api_key_env_var):
        raise MissingAPIKeyError(provider.api_key_env_var, provider.name)
    return self

@model_validator(mode="after")
def _check_system_prompt(self) -> KinConfig:
    # Validate system prompt file exists
    _ = self.system_prompt  # Raises if not found
    return self
```

## Event System

### Event Types

All events inherit from `BaseEvent`:

```python
class AssistantEvent(BaseEvent):
    content: str                        # Text response
    stopped_by_middleware: bool = False

class ReasoningEvent(BaseEvent):
    content: str                        # Thinking/reasoning content

class ToolCallEvent(BaseEvent):
    tool_name: str
    tool_class: type[BaseTool]
    args: BaseModel
    tool_call_id: str

class ToolResultEvent(BaseEvent):
    tool_name: str
    tool_class: type[BaseTool] | None
    result: BaseModel | None = None
    error: str | None = None
    skipped: bool = False
    skip_reason: str | None = None
    duration: float | None = None
    tool_call_id: str

class CompactStartEvent(BaseEvent):
    current_context_tokens: int
    threshold: int

class CompactEndEvent(BaseEvent):
    old_context_tokens: int
    new_context_tokens: int
    summary_length: int
```

### Event Flow

```python
# Agent emits events through async generator
async for event in agent.act("Write a hello world program"):
    match event:
        case AssistantEvent(content=content):
            display(content)

        case ToolCallEvent(tool_name=name, args=args):
            show_tool_call(name, args)

        case ToolResultEvent(result=result, error=error):
            if error:
                show_error(error)
            else:
                show_result(result)

        case CompactStartEvent():
            show_compaction_started()

        case CompactEndEvent(old_context_tokens=old, new_context_tokens=new):
            show_compaction_complete(old, new)
```

### Message Observer

For tracking all messages added to history:

```python
def message_observer(message: LLMMessage):
    print(f"{message.role}: {message.content[:50]}")

agent = Agent(config, message_observer=message_observer)
```

## Session Management

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ 1. Session Creation                                     │
│    - Generate UUID                                      │
│    - Initialize InteractionLogger                       │
│    - Create system message                              │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Conversation Turns                                   │
│    - User message → LLM response → Tool execution       │
│    - Auto-save after each turn                          │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Session Events                                       │
│    - Compaction: Save, reset UUID, save again           │
│    - Config reload: Preserve messages, new system msg   │
│    - Clear history: Save, reset to system msg only      │
└─────────────────────────────────────────────────────────┘
```

### Persistence Format

Sessions are saved as JSON files:

```json
{
  "metadata": {
    "session_id": "uuid",
    "start_time": "2024-01-26T10:30:00",
    "end_time": "2024-01-26T11:00:00",
    "git_commit": "abc123",
    "git_branch": "main",
    "environment": {...},
    "auto_approve": false,
    "username": "blake"
  },
  "messages": [
    {
      "role": "system",
      "content": "..."
    },
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "tool_calls": null
    }
  ],
  "stats": {
    "steps": 2,
    "session_prompt_tokens": 1000,
    "session_completion_tokens": 50,
    ...
  },
  "config_snapshot": {
    "active_model": "devstral-2",
    "tools": {...}
  }
}
```

### Session Operations

```python
# Start new session
agent = Agent(config)
# session_id = uuid4()

# Clear history (resets session)
await agent.clear_history()
# - Saves current session
# - Resets messages to [system_message]
# - Generates new session_id
# - Resets stats and middleware

# Compact (preserves session with new UUID)
summary = await agent.compact()
# - Asks LLM to summarize history
# - Replaces messages with [system, summary]
# - Generates new session_id
# - Saves both old and new sessions

# Reload config (preserves session)
await agent.reload_with_initial_messages(config=new_config)
# - Saves current session
# - Regenerates system prompt
# - Preserves user/assistant/tool messages
# - Keeps same session_id
```

## Extension Points

### Custom Tools

Create tools by subclassing `BaseTool`:

```python
from pydantic import BaseModel, Field
from kin_code.core.tools.base import BaseTool, BaseToolConfig, BaseToolState

class MyToolArgs(BaseModel):
    input: str = Field(description="Input string")

class MyToolResult(BaseModel):
    output: str

class MyToolConfig(BaseToolConfig):
    custom_setting: str = "default"

class MyToolState(BaseToolState):
    call_count: int = 0

class MyTool(BaseTool[MyToolArgs, MyToolResult, MyToolConfig, MyToolState]):
    description = "Does something useful"

    async def run(self, args: MyToolArgs) -> MyToolResult:
        self.state.call_count += 1
        return MyToolResult(output=f"Processed: {args.input}")
```

Place in a search path:
- `~/.kin-code/tools/my_tool.py`
- `{project}/.kin-code/tools/my_tool.py`
- Custom path in `config.toml`: `tool_paths = ["./my_tools"]`

### Custom Middleware

Implement the middleware protocol:

```python
class CustomMiddleware:
    async def before_turn(self, context: ConversationContext) -> MiddlewareResult:
        # Run before each LLM call
        if context.stats.steps > 100:
            return MiddlewareResult(
                action=MiddlewareAction.STOP,
                reason="Too many steps"
            )
        return MiddlewareResult()

    async def after_turn(self, context: ConversationContext) -> MiddlewareResult:
        # Run after each LLM response
        return MiddlewareResult()

    def reset(self, reset_reason: ResetReason) -> None:
        # Reset internal state
        pass

# Add to agent
agent.middleware_pipeline.add(CustomMiddleware())
```

### Custom Backends

Implement the `BackendLike` protocol:

```python
from kin_code.core.llm.types import BackendLike

class CustomBackend:
    async def __aenter__(self) -> BackendLike:
        # Initialize resources
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # Cleanup resources
        pass

    async def complete(self, *, model, messages, temperature, tools,
                       max_tokens, tool_choice, extra_headers) -> LLMChunk:
        # Non-streaming completion
        response = await custom_api_call(...)
        return LLMChunk(message=..., usage=...)

    async def complete_streaming(self, **kwargs) -> AsyncGenerator[LLMChunk]:
        # Streaming completion
        async for chunk in custom_streaming_call(...):
            yield LLMChunk(message=..., usage=...)

    async def count_tokens(self, **kwargs) -> int:
        # Token counting
        return count_tokens_somehow(...)

# Use custom backend
agent = Agent(config, backend=CustomBackend(provider=provider, timeout=60))
```

### Custom API Adapters

Register adapters for new API formats:

```python
from kin_code.core.llm.backend.generic import register_adapter, BACKEND_ADAPTERS, APIAdapter

@register_adapter(BACKEND_ADAPTERS, "custom_api")
class CustomAPIAdapter(APIAdapter):
    endpoint = "/v1/custom/endpoint"

    def prepare_request(self, *, model_name, messages, temperature,
                       tools, max_tokens, tool_choice, enable_streaming,
                       provider, api_key=None) -> PreparedRequest:
        # Convert to custom API format
        payload = {...}
        headers = {...}
        body = json.dumps(payload).encode()
        return PreparedRequest(self.endpoint, headers, body)

    def parse_response(self, data: dict, provider: ProviderConfig) -> LLMChunk:
        # Parse custom API response
        message = LLMMessage(...)
        usage = LLMUsage(...)
        return LLMChunk(message=message, usage=usage)
```

Configure in `config.toml`:

```toml
[[providers]]
name = "my_custom_provider"
api_base = "https://api.custom.com"
api_key_env_var = "CUSTOM_API_KEY"
api_style = "custom_api"  # References registered adapter
```

### Custom Agent Modes

Create mode configurations:

```python
from kin_code.core.modes import AgentMode

# Define in agent config
# ~/.kin-code/agents/strict.toml
enabled_tools = ["grep", "read_file", "todo"]
context_warnings = true
auto_compact_threshold = 50000
```

Load with:

```python
config = KinConfig.load(agent="strict")
agent = Agent(config)
```

### Custom System Prompts

Create prompt files in `~/.kin-code/prompts/`:

```markdown
# my_prompt.md
You are a specialized coding assistant focused on security.
Always consider security implications.
```

Configure in `config.toml`:

```toml
system_prompt_id = "my_prompt"
```

---

## Design Rationale

### Why Async?

All I/O operations (LLM API calls, tool execution, file operations) are async to:
- Enable concurrent tool execution in the future
- Support streaming responses efficiently
- Allow cancellation during long-running operations
- Integrate cleanly with async HTTP clients

### Why Middleware?

Middleware provides cross-cutting concerns without cluttering the core agent logic:
- Turn/price limits can be added/removed without changing agent code
- Custom behavior can be injected at well-defined points
- Middleware can be composed and reused across different agent configurations

### Why Lazy Tool Loading?

Tools are instantiated on first use to:
- Reduce startup time (don't initialize unused tools)
- Allow tool state to be isolated per session
- Enable dynamic tool configuration based on first call

### Why Event-Driven?

Events enable:
- Decoupled UI rendering (TUI doesn't depend on agent internals)
- Streaming progress updates
- Structured logging and observability
- Multiple simultaneous consumers (UI + logger + metrics)

### Why Provider Abstraction?

The backend/adapter pattern allows:
- Supporting new providers without changing agent code
- Testing with mock backends
- Custom backends for specialized use cases
- Protocol-level abstraction (BackendLike) for dependency injection

---

## Related Documentation

- [User Guide](../user-guide/index.md) - Learn how to use Kin Code
- [Configuration Reference](../reference/config-reference.md) - All configuration options
- [Custom Tools](../customization/custom-tools.md) - Build your own tools
- [MCP Servers](../integrations/mcp-servers.md) - Integrate external tools

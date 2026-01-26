# Type Definitions Reference

Complete reference for all core types used in Kin Code's Python API.

## Overview

Kin Code uses Pydantic models and Python protocols for type safety. This reference covers:

- **Message types** - Conversation data structures
- **Event types** - Agent execution events
- **Statistics types** - Usage and cost tracking
- **Tool types** - Function calling structures
- **Callback types** - Approval and observation handlers

All types use modern Python 3.12+ syntax with built-in generics (`list`, `dict`) and union operators (`|`).

## Message Types

### LLMMessage

Represents a single message in the conversation:

```python
from kin_code.core.types import LLMMessage, Role

class LLMMessage(BaseModel):
    role: Role                              # system, user, assistant, tool
    content: str | None = None              # Main message content
    reasoning_content: str | None = None    # Thinking/reasoning (if available)
    tool_calls: list[ToolCall] | None = None  # Function calls
    name: str | None = None                 # Tool name (for role=tool)
    tool_call_id: str | None = None         # Reference to tool call
```

**Usage:**

```python
# User message
user_msg = LLMMessage(role=Role.user, content="Hello")

# Assistant message with tool call
assistant_msg = LLMMessage(
    role=Role.assistant,
    content="Let me check that file.",
    tool_calls=[
        ToolCall(
            id="call_123",
            function=FunctionCall(name="read_file", arguments='{"path": "main.py"}')
        )
    ]
)

# Tool result message
tool_msg = LLMMessage(
    role=Role.tool,
    content="File contents here...",
    name="read_file",
    tool_call_id="call_123",
)
```

### Role

Enum for message roles:

```python
from kin_code.core.types import Role

class Role(StrEnum):
    system = auto()     # System prompt
    user = auto()       # User input
    assistant = auto()  # LLM response
    tool = auto()       # Tool result
```

### LLMChunk

Streaming response chunk:

```python
class LLMChunk(BaseModel):
    message: LLMMessage              # Partial or complete message
    usage: LLMUsage | None = None    # Token usage (may be in final chunk only)
```

### LLMUsage

Token usage statistics:

```python
class LLMUsage(BaseModel):
    prompt_tokens: int = 0       # Input tokens
    completion_tokens: int = 0   # Output tokens
```

## Event Types

Events are emitted during agent execution for UI rendering and logging.

### BaseEvent

Abstract base class for all events:

```python
from kin_code.core.types import BaseEvent

class BaseEvent(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

### AssistantEvent

Assistant response text:

```python
class AssistantEvent(BaseEvent):
    content: str                         # Response text
    stopped_by_middleware: bool = False  # True if middleware halted execution
```

**Example handling:**

```python
async for event in agent.act(prompt):
    match event:
        case AssistantEvent(content=text, stopped_by_middleware=stopped):
            print(text)
            if stopped:
                print("[Stopped by middleware]")
```

### ReasoningEvent

Reasoning/thinking content (for models that support it):

```python
class ReasoningEvent(BaseEvent):
    content: str  # Reasoning text
```

### ToolCallEvent

Tool invocation:

```python
from kin_code.core.tools.base import BaseTool

class ToolCallEvent(BaseEvent):
    tool_name: str               # Name of the tool
    tool_class: type[BaseTool]   # Tool class (for type checking)
    args: BaseModel              # Parsed arguments
    tool_call_id: str            # Unique identifier
```

### ToolResultEvent

Tool execution result:

```python
class ToolResultEvent(BaseEvent):
    tool_name: str
    tool_class: type[BaseTool] | None
    result: BaseModel | None = None    # Success result
    error: str | None = None           # Error message if failed
    skipped: bool = False              # True if user rejected
    skip_reason: str | None = None     # Rejection reason
    duration: float | None = None      # Execution time in seconds
    tool_call_id: str
```

**Example handling:**

```python
case ToolResultEvent(tool_name=name, result=result, error=error):
    if error:
        print(f"Tool {name} failed: {error}")
    elif result:
        print(f"Tool {name} succeeded: {result}")
```

### CompactStartEvent

Context compaction starting:

```python
class CompactStartEvent(BaseEvent):
    current_context_tokens: int  # Tokens before compaction
    threshold: int               # Threshold that triggered compaction
```

### CompactEndEvent

Context compaction complete:

```python
class CompactEndEvent(BaseEvent):
    old_context_tokens: int    # Tokens before
    new_context_tokens: int    # Tokens after
    summary_length: int        # Length of summary
```

## Statistics Types

### AgentStats

Session statistics and tracking:

```python
class AgentStats(BaseModel):
    # Turn tracking
    steps: int = 0                         # Number of LLM turns

    # Token usage (cumulative)
    session_prompt_tokens: int = 0         # Total input tokens
    session_completion_tokens: int = 0     # Total output tokens

    # Context tracking
    context_tokens: int = 0                # Current context size

    # Last turn metrics
    last_turn_prompt_tokens: int = 0
    last_turn_completion_tokens: int = 0
    last_turn_duration: float = 0.0
    tokens_per_second: float = 0.0

    # Tool metrics
    tool_calls_agreed: int = 0             # User approved
    tool_calls_rejected: int = 0           # User rejected
    tool_calls_failed: int = 0             # Execution failed
    tool_calls_succeeded: int = 0          # Executed successfully

    # Pricing (for cost calculation)
    input_price_per_million: float = 0.0
    output_price_per_million: float = 0.0

    # Computed properties
    @property
    def session_total_llm_tokens(self) -> int: ...
    @property
    def last_turn_total_tokens(self) -> int: ...
    @property
    def session_cost(self) -> float: ...  # Estimated cost in USD
```

**Usage:**

```python
stats = agent.stats

print(f"Turns: {stats.steps}")
print(f"Total tokens: {stats.session_total_llm_tokens}")
print(f"Estimated cost: ${stats.session_cost:.4f}")
print(f"Tools succeeded: {stats.tool_calls_succeeded}")
```

### SessionInfo

Current session information:

```python
class SessionInfo(BaseModel):
    session_id: str           # UUID
    start_time: str           # ISO 8601 timestamp
    message_count: int        # Number of messages
    stats: AgentStats         # Session statistics
    save_dir: str             # Directory for session files
```

### SessionMetadata

Saved session metadata:

```python
class SessionMetadata(BaseModel):
    session_id: str
    start_time: str
    end_time: str | None
    git_commit: str | None
    git_branch: str | None
    environment: dict[str, str | None]
    auto_approve: bool = False
    username: str
```

## Tool Types

### ToolCall

Function call from LLM:

```python
class ToolCall(BaseModel):
    id: str | None = None         # Unique identifier
    index: int | None = None      # Position in parallel calls
    function: FunctionCall        # Function details
    type: str = "function"        # Always "function"
```

### FunctionCall

Function name and arguments:

```python
class FunctionCall(BaseModel):
    name: str | None = None       # Function name
    arguments: str | None = None  # JSON-encoded arguments
```

### AvailableTool

Tool definition for LLM:

```python
class AvailableTool(BaseModel):
    type: Literal["function"] = "function"
    function: AvailableFunction
```

### AvailableFunction

Function schema for LLM:

```python
class AvailableFunction(BaseModel):
    name: str                      # Tool name
    description: str               # Description with prompt
    parameters: dict[str, Any]     # JSON Schema for arguments
```

**Example schema:**

```python
{
    "name": "grep",
    "description": "Search for patterns in files...",
    "parameters": {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "..."},
            "path": {"type": "string", "description": "..."},
        },
        "required": ["pattern"]
    }
}
```

### StrToolChoice

Tool selection hint for LLM:

```python
StrToolChoice = Literal["auto", "none", "any", "required"]
```

| Value | Behavior |
|-------|----------|
| `"auto"` | LLM decides whether to use tools |
| `"none"` | Disable tool calling |
| `"any"` | Force tool use (any tool) |
| `"required"` | Must use at least one tool |

## Callback Types

### ApprovalCallback

Callback for tool approval:

```python
# Async version
type AsyncApprovalCallback = Callable[
    [str, BaseModel, str],  # tool_name, args, tool_call_id
    Awaitable[tuple[ApprovalResponse, str | None]]  # (response, message)
]

# Sync version
type SyncApprovalCallback = Callable[
    [str, BaseModel, str],
    tuple[ApprovalResponse, str | None]
]

# Either type
type ApprovalCallback = AsyncApprovalCallback | SyncApprovalCallback
```

**Usage:**

```python
def my_approval(
    tool_name: str,
    args: BaseModel,
    tool_call_id: str,
) -> tuple[ApprovalResponse, str | None]:
    if tool_name in ["grep", "read_file"]:
        return (ApprovalResponse.YES, None)
    return (ApprovalResponse.NO, "Tool not allowed")

agent.set_approval_callback(my_approval)
```

### ApprovalResponse

Approval decision:

```python
class ApprovalResponse(StrEnum):
    YES = "y"  # Approve tool execution
    NO = "n"   # Reject tool execution
```

## Output Format

### OutputFormat

Output format selection:

```python
class OutputFormat(StrEnum):
    TEXT = auto()       # Return final response as text
    JSON = auto()       # Return all messages as JSON
    STREAMING = auto()  # Emit messages as NDJSON
```

## Content Types

### Content

Annotated type for message content that handles various formats:

```python
from pydantic import BeforeValidator

def _content_before(v: Any) -> str:
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        # Handle multi-part content (images, etc.)
        parts = []
        for p in v:
            if isinstance(p, dict) and isinstance(p.get("text"), str):
                parts.append(p["text"])
            else:
                parts.append(str(p))
        return "\n".join(parts)
    return str(v)

Content = Annotated[str, BeforeValidator(_content_before)]
```

This normalizes content from various LLM response formats to strings.

## Skill Types

### SkillMetadata

Skill definition from YAML frontmatter:

```python
class SkillMetadata(BaseModel):
    name: str                    # Skill identifier
    description: str             # What the skill does
    license: str | None = None   # License info
    compatibility: str | None = None  # Requirements
    metadata: dict[str, str]     # Arbitrary key-value pairs
    allowed_tools: list[str]     # Pre-approved tools
```

### SkillInfo

Loaded skill information:

```python
class SkillInfo(BaseModel):
    name: str
    description: str
    license: str | None
    compatibility: str | None
    metadata: dict[str, str]
    allowed_tools: list[str]
    skill_path: Path             # Path to SKILL.md

    @property
    def skill_dir(self) -> Path:  # Parent directory
        ...
```

## Middleware Types

### ConversationContext

Context passed to middleware:

```python
from dataclasses import dataclass

@dataclass
class ConversationContext:
    messages: list[LLMMessage]   # Conversation history
    stats: AgentStats            # Session statistics
    config: KinConfig            # Configuration
```

### MiddlewareResult

Middleware decision:

```python
@dataclass
class MiddlewareResult:
    action: MiddlewareAction = MiddlewareAction.CONTINUE
    message: str | None = None   # For INJECT_MESSAGE
    reason: str | None = None    # For STOP
    metadata: dict[str, Any] = field(default_factory=dict)
```

### MiddlewareAction

Available middleware actions:

```python
class MiddlewareAction(StrEnum):
    CONTINUE = auto()        # Proceed normally
    STOP = auto()            # Halt execution
    COMPACT = auto()         # Trigger compaction
    INJECT_MESSAGE = auto()  # Add content to conversation
```

### ResetReason

Why middleware is being reset:

```python
class ResetReason(StrEnum):
    STOP = auto()     # Conversation cleared
    COMPACT = auto()  # Context compacted
```

## Protocol Types

### BackendLike

Protocol for LLM backends:

```python
from typing import Protocol, AsyncGenerator

class BackendLike(Protocol):
    async def __aenter__(self) -> BackendLike: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    async def complete(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float,
        tools: list[AvailableTool],
        max_tokens: int | None,
        tool_choice: StrToolChoice,
        extra_headers: dict[str, str],
    ) -> LLMChunk: ...

    async def complete_streaming(
        self,
        **kwargs,
    ) -> AsyncGenerator[LLMChunk]: ...

    async def count_tokens(
        self,
        **kwargs,
    ) -> int: ...
```

### ConversationMiddleware

Protocol for middleware:

```python
class ConversationMiddleware(Protocol):
    async def before_turn(self, context: ConversationContext) -> MiddlewareResult: ...
    async def after_turn(self, context: ConversationContext) -> MiddlewareResult: ...
    def reset(self, reset_reason: ResetReason = ResetReason.STOP) -> None: ...
```

## Import Locations

```python
# Core types
from kin_code.core.types import (
    LLMMessage,
    LLMChunk,
    LLMUsage,
    Role,
    AgentStats,
    SessionInfo,
    SessionMetadata,
    ToolCall,
    FunctionCall,
    AvailableTool,
    AvailableFunction,
    StrToolChoice,
    ApprovalResponse,
    ApprovalCallback,
    OutputFormat,
    # Events
    BaseEvent,
    AssistantEvent,
    ReasoningEvent,
    ToolCallEvent,
    ToolResultEvent,
    CompactStartEvent,
    CompactEndEvent,
)

# Middleware types
from kin_code.core.middleware import (
    ConversationContext,
    MiddlewareResult,
    MiddlewareAction,
    ResetReason,
)

# Skill types
from kin_code.core.skills.models import (
    SkillMetadata,
    SkillInfo,
)

# Tool types
from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    ToolPermission,
    ToolError,
)
```

## Related Documentation

- [Python API](../api/python-api.md) - Using the API
- [Custom Tools](../customization/custom-tools.md) - Building tools
- [Custom Middleware](../customization/custom-middleware.md) - Creating middleware
- [Architecture Overview](../architecture/overview.md) - System design

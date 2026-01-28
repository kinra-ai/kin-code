# Agent Loop

The core execution flow that processes user requests.

## Overview

The agent loop is the central component that:
1. Receives user messages
2. Sends requests to the LLM
3. Processes tool calls
4. Returns responses

## Flow Diagram

```
User Message
     |
     v
+--------------------+
|    Agent Loop      |
+--------------------+
     |
     v
Build Context
(history + tools + skills)
     |
     v
+--------------------+
|   LLM Provider     |
+--------------------+
     |
     v
Parse Response
     |
     +---> Text: Display to user
     |
     +---> Tool Calls: Execute tools
               |
               v
          Tool Results
               |
               v
          Return to LLM
               |
               v
          Continue loop
```

## Key Responsibilities

### Context Management

- Maintains conversation history
- Includes tool definitions
- Injects skill instructions
- Manages context window limits

### Tool Coordination

- Receives tool calls from LLM
- Checks permissions
- Executes tools
- Returns results to LLM

### Error Handling

- Catches tool errors
- Handles API failures
- Manages rate limits
- Provides graceful degradation

## Implementation

Located in `kin_code/core/agent_loop.py`.

Key methods:
- `run()` - Main loop entry
- `process_message()` - Handle single message
- `execute_tool()` - Run a tool call

## Configuration

The agent loop behavior is affected by:
- Tool permissions
- Agent profile
- Model selection

## Related

- [Architecture Overview](overview.md)
- [Tool System](tool-system.md)

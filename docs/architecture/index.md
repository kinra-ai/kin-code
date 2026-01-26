# Architecture

Deep dive into Kin Code's internal architecture and design.

## In This Section

- [Architecture Overview](./overview.md) - Comprehensive system architecture documentation

## Overview

Kin Code is built as a layered, event-driven architecture that orchestrates LLM interactions, tool execution, and conversation management. The system is designed around several key principles:

- **Provider Abstraction**: LLM providers are abstracted through a unified backend protocol
- **Event-Driven**: Conversation turns emit typed events for UI rendering and logging
- **Middleware Composition**: Behavior can be modified through composable middleware
- **Tool Discoverability**: Tools are discovered dynamically from search paths
- **Configuration Layering**: Settings cascade through multiple sources

## Core Components

### Agent
The central orchestrator that manages conversation history, coordinates middleware execution, invokes LLM backends, and executes tools.

### Tool Manager
Discovers and manages tool instances, including built-in tools, custom tools from search paths, and MCP (Model Context Protocol) proxy tools.

### Configuration System
Multi-source configuration with precedence hierarchy supporting TOML files, environment variables, and runtime overrides.

### LLM Backend
Abstraction layer for LLM provider APIs with support for OpenAI-compatible endpoints and Mistral-specific features.

### Middleware Pipeline
Composable interceptors that run before/after conversation turns for cross-cutting concerns like turn limits, price limits, and context management.

## Key Flows

### Conversation Turn
User input → Middleware (before) → LLM call → Tool parsing → Permission checks → Tool execution → Middleware (after) → Response

### Tool Discovery
Scan search paths → Import Python modules → Filter BaseTool subclasses → Integrate MCP servers → Build tool registry

### Configuration Loading
Defaults → Agent TOML → Config TOML → Environment variables → Runtime overrides

## Extension Points

Kin Code can be extended through:
- **Custom Tools**: Subclass `BaseTool` to add new capabilities
- **Custom Middleware**: Implement middleware protocol for custom behavior
- **Custom Backends**: Implement `BackendLike` protocol for new LLM providers
- **Custom API Adapters**: Register adapters for new API formats
- **Custom System Prompts**: Create `.md` files in prompts directory

## Architecture Documentation

The [Architecture Overview](./overview.md) provides comprehensive documentation including:

1. **System Overview** - High-level architecture diagram and design principles
2. **Core Components** - Detailed component descriptions and responsibilities
3. **Conversation Flow** - Step-by-step flow from user input to LLM response
4. **Tool System** - Tool discovery, execution, and permission checking
5. **Middleware Pipeline** - How middleware intercepts and modifies behavior
6. **Backend Architecture** - LLM provider abstraction and API adapters
7. **Configuration System** - Settings hierarchy and override precedence
8. **Event System** - Event types and message observers
9. **Session Management** - Conversation history and state persistence
10. **Extension Points** - How to customize with detailed code examples

## Design Rationale

### Async-First Design
All I/O operations are async to enable streaming, concurrent execution, and cancellation support.

### Event-Driven Architecture
Events enable decoupled UI rendering, structured logging, streaming progress updates, and multiple simultaneous consumers.

### Middleware Pattern
Provides cross-cutting concerns without cluttering core agent logic, enabling composition and reuse.

### Lazy Tool Loading
Tools are instantiated on first use to reduce startup time and enable dynamic configuration.

### Provider Abstraction
Backend/adapter pattern allows supporting new providers without changing agent code and enables testing with mock backends.

## Related Documentation

- [User Guide](../user-guide/index.md) - Learn how to use Kin Code effectively
- [Customization](../customization/index.md) - Extend Kin Code with custom tools and prompts
- [Configuration Reference](../reference/config-reference.md) - Complete configuration options
- [Python API](../api/python-api.md) - Programmatic usage

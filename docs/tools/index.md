# Tools

Kin Code includes 6 built-in tools that the AI agent can use to interact with your codebase.

## Built-in Tools

| Tool | Description |
|------|-------------|
| [bash](./bash.md) | Execute shell commands |
| [read_file](./read-file.md) | Read file contents with chunking support |
| [write_file](./write-file.md) | Create or overwrite files |
| [search_replace](./search-replace.md) | Make targeted edits using pattern matching |
| [grep](./grep.md) | Search code recursively with regex |
| [todo](./todo.md) | Track tasks and progress |

## How Tools Work

When the agent needs to perform an action, it requests permission to use a tool. By default, you'll be asked to approve each tool execution. This can be configured per-tool or globally.

See [Tool Permissions](../configuration/tool-permissions.md) for details on controlling tool access.

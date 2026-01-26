# Your First Project

This guide walks through a complete task with Kin Code, from start to finish.

## Scenario

You have a Python project and want to add type hints to an existing function.

## Step 1: Start Kin Code

Navigate to your project and launch Kin:

```bash
cd ~/my-python-project
kin
```

## Step 2: Explore the Codebase

Ask Kin to help you understand the project:

```
> What Python files are in the src/ directory?
```

Kin will use the `grep` tool to search and report back.

## Step 3: Read a File

Ask Kin to examine a specific file:

```
> Read the file src/utils.py
```

Kin uses `read_file` to show you the contents.

## Step 4: Request Changes

Now ask Kin to make changes:

```
> Add type hints to the calculate_total function in src/utils.py
```

Kin will:
1. Read the file to understand the current code
2. Propose changes using `search_replace`
3. Ask for your approval before applying

## Step 5: Review and Approve

When Kin proposes a tool execution, you'll see:

```
> search_replace(file_path="src/utils.py", content="...")

[y]es / [n]o / [a]lways / ne[v]er?
```

- **y** - Approve this execution
- **n** - Deny this execution
- **a** - Always approve this tool
- **v** - Never allow this tool

Type `y` to approve the change.

## Step 6: Verify

Ask Kin to confirm the changes:

```
> Show me the updated calculate_total function
```

## Tips for Success

1. **Be specific** - Clear prompts get better results
2. **Review changes** - Always verify tool executions before approving
3. **Use Plan mode** - For exploration without making changes, use `kin --plan`
4. **Track progress** - Kin's todo tool helps manage multi-step tasks

## Next Steps

- Explore [Modes](../user-guide/modes.md) for different workflows
- Learn about [Slash Commands](../user-guide/slash-commands.md)
- Configure [Tool Permissions](../configuration/tool-permissions.md)

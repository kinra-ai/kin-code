# Modes

Kin Code has four operating modes that control tool approval behavior.

## Mode Overview

| Mode | Description | Safety Level |
|------|-------------|--------------|
| Default | Asks for approval before each tool execution | Neutral |
| Plan | Read-only mode for exploration | Safe |
| Accept Edits | Auto-approves file edits only | Destructive |
| Auto Approve | Auto-approves all tool executions | YOLO |

## Default Mode

The standard mode. You'll be prompted before each tool execution:

```
> search_replace(file_path="src/main.py", content="...")

[y]es / [n]o / [a]lways / ne[v]er?
```

Start in default mode (the default):
```bash
kin
```

## Plan Mode

A read-only mode for safely exploring your codebase. Only these tools are available:
- `grep` - Search code
- `read_file` - Read files
- `todo` - Manage task list

All tools in plan mode auto-approve since they can't modify your code.

Start in plan mode:
```bash
kin --plan
```

## Accept Edits Mode

Auto-approves file editing tools (`write_file`, `search_replace`) while still prompting for other tools like `bash`.

Useful when you trust the agent's code changes but want control over shell commands.

## Auto Approve Mode

All tools execute without prompting. Use with caution.

Start in auto-approve mode:
```bash
kin --auto-approve
```

Or toggle during a session with `Shift+Tab`.

## Cycling Modes

Press `Shift+Tab` in interactive mode to cycle through modes:

Default → Plan → Accept Edits → Auto Approve → Default

The current mode is displayed in the status bar.

## Choosing the Right Mode

| Scenario | Recommended Mode |
|----------|------------------|
| Exploring unfamiliar code | Plan |
| Making careful edits | Default |
| Trusting code changes, cautious on bash | Accept Edits |
| Automation/CI | Auto Approve |
| Learning what the agent can do | Plan |

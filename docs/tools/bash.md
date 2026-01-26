# bash

Execute shell commands in a stateless environment.

## Overview

The `bash` tool runs one-off shell commands. Each command runs independently in a fresh environment.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | The shell command to execute |

## When to Use bash

**Appropriate uses:**
- System information: `pwd`, `whoami`, `date`, `uname -a`
- Directory listings: `ls -la`, `tree`
- Git operations: `git status`, `git log --oneline -10`, `git diff`
- Process info: `ps aux | grep process`
- Network checks: `ping -c 1 example.com`, `curl -I https://example.com`
- Package management: `pip list`, `npm list`
- Environment checks: `env | grep VAR`, `which python`
- File metadata: `stat filename`, `file filename`, `wc -l filename`

**Do NOT use bash for:**
- Reading files → Use `read_file`
- Writing files → Use `write_file`
- Searching code → Use `grep`
- Editing files → Use `search_replace`

## Examples

```python
# Check git status
bash(command="git status")

# List files
bash(command="ls -la src/")

# Check Python version
bash(command="python --version")
```

## Permissions

By default, `bash` requires approval before execution. Configure in `config.toml`:

```toml
[tools.bash]
permission = "ask"  # "always", "never", or "ask"
allowlist = ["git *", "ls *"]  # Auto-approve matching commands
denylist = ["rm -rf *"]  # Auto-deny matching commands
```

See [Tool Permissions](../configuration/tool-permissions.md) for details.

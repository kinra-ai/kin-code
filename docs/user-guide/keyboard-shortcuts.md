# Keyboard Shortcuts

Kin Code provides keyboard shortcuts for efficient navigation and control.

## Input Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Ctrl+J` | Insert newline (multi-line input) |
| `Shift+Enter` | Insert newline (some terminals) |
| `Ctrl+G` | Open external editor |
| `Tab` | Autocomplete |
| `Up/Down` | Navigate message history |
| `Ctrl+P` | Previous message in history |
| `Ctrl+N` | Next message in history |

## Control Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Interrupt current operation |
| `Ctrl+C` (twice) | Exit Kin Code |
| `Ctrl+D` | Exit Kin Code |
| `Shift+Tab` | Toggle auto-approve mode |

## View Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Toggle tool output view |
| `Ctrl+T` | Toggle todo list view |

## Navigation

| Shortcut | Action |
|----------|--------|
| `Page Up` | Scroll up |
| `Page Down` | Scroll down |
| `Home` | Go to start of input |
| `End` | Go to end of input |

## Editing

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Select all |
| `Ctrl+U` | Clear input line |
| `Ctrl+W` | Delete word before cursor |
| `Ctrl+K` | Delete from cursor to end |

## Autocompletion

| Shortcut | Action |
|----------|--------|
| `Tab` | Show/cycle completions |
| `Shift+Tab` | Cycle completions backward |
| `Enter` | Accept completion |
| `Escape` | Cancel completion |

## Tool Approval

When a tool approval prompt appears:

| Key | Action |
|-----|--------|
| `y` | Approve execution |
| `n` | Deny execution |
| `a` | Always approve this tool |

## Customization

Keyboard shortcuts cannot be customized directly, but you can:

1. **Use your terminal's shortcuts** - Most terminals allow key remapping
2. **Set $EDITOR** - For the external editor shortcut
3. **Use agent profiles** - To change default approval behavior

## Terminal Compatibility

Some shortcuts may not work in all terminals:

- `Shift+Enter` requires terminal support
- Mouse shortcuts depend on terminal mouse support
- Some terminals capture `Ctrl+` combinations

If a shortcut doesn't work:
1. Try the alternative shortcut
2. Check your terminal's settings
3. Use slash commands instead

## Quick Reference Card

```
Essential Shortcuts
-------------------
Enter         Send message
Ctrl+J        New line
Ctrl+C        Interrupt / Exit
Ctrl+G        External editor
Shift+Tab     Toggle auto-approve
Ctrl+O        Toggle tool output
Ctrl+T        Toggle todo list
Tab           Autocomplete
```

## Related

- [Interactive Mode](interactive-mode.md)
- [Terminal Requirements](../getting-started/terminal-requirements.md)

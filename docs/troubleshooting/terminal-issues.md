# Terminal Issues

Solutions for display and input problems.

## Display Issues

### Colors Look Wrong

Colors appear incorrect or missing.

**Solutions:**
1. Check TERM variable: `echo $TERM`
2. Set to 256 colors: `export TERM=xterm-256color`
3. Use a modern terminal emulator

### Characters Not Displaying

Unicode characters appear as boxes or question marks.

**Solutions:**
1. Ensure terminal supports UTF-8
2. Set locale: `export LANG=en_US.UTF-8`
3. Use a font with Unicode support

### UI Glitches

Screen corruption or layout issues.

**Solutions:**
1. Resize terminal window
2. Try a different terminal
3. Disable transparency effects
4. Update terminal emulator

## Input Issues

### Shortcuts Not Working

Keyboard shortcuts don't respond.

**Solutions:**
1. Check terminal isn't capturing the shortcut
2. Try alternative shortcuts
3. Use slash commands instead

### Can't Enter Multi-line Input

`Ctrl+J` or `Shift+Enter` not working.

**Solutions:**
1. Try both shortcuts
2. Check terminal keybindings
3. Use `Ctrl+G` for external editor

### Paste Not Working

Pasting text has issues.

**Solutions:**
1. Try `Ctrl+V` or `Cmd+V`
2. Right-click paste
3. Check terminal paste settings

## tmux/screen Issues

### Display Problems in tmux

**Solutions:**
1. Add to `~/.tmux.conf`:
   ```
   set -g default-terminal "tmux-256color"
   set -ag terminal-overrides ",xterm-256color:RGB"
   ```
2. Restart tmux

### Shortcuts Captured by tmux

**Solutions:**
1. Use tmux prefix first
2. Remap conflicting keys
3. Run outside tmux initially

## SSH Issues

### Display Issues Over SSH

**Solutions:**
1. Ensure local terminal supports features
2. Use `ssh -t` for proper terminal handling
3. Check SSH configuration

## Recommended Terminals

For best experience:
- WezTerm (cross-platform)
- Alacritty (cross-platform)
- Ghostty (macOS/Linux)
- Kitty (macOS/Linux)
- Windows Terminal (Windows)

## Related

- [Terminal Requirements](../getting-started/terminal-requirements.md)
- [Common Issues](common-issues.md)

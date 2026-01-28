# Terminal Requirements

Kin Code's interactive interface is built with modern terminal capabilities. This guide covers terminal compatibility and recommendations.

## Recommended Terminals

These terminals provide the best experience with Kin Code:

### Cross-Platform

- **[WezTerm](https://wezfurlong.org/wezterm/)** - GPU-accelerated, highly configurable
- **[Alacritty](https://alacritty.org/)** - Fast, minimal, GPU-accelerated

### macOS

- **[Ghostty](https://ghostty.org/)** - Native macOS terminal
- **[Kitty](https://sw.kovidgoyal.net/kitty/)** - Feature-rich, GPU-accelerated
- **Terminal.app** - Built-in macOS terminal (works but limited)
- **iTerm2** - Popular macOS terminal

### Linux

- **[Ghostty](https://ghostty.org/)** - Fast, native terminal
- **[Kitty](https://sw.kovidgoyal.net/kitty/)** - Feature-rich
- **GNOME Terminal** - Default on many distros
- **Konsole** - KDE's default terminal

### Windows

- **[Windows Terminal](https://aka.ms/terminal)** - Microsoft's modern terminal
- **[WezTerm](https://wezfurlong.org/wezterm/)** - Cross-platform option

## Required Capabilities

Kin Code requires these terminal features:

### Essential

- **True color support** - 24-bit color (16 million colors)
- **Unicode support** - UTF-8 encoding
- **ANSI escape sequences** - For cursor movement and styling
- **Minimum size** - At least 80x24 characters

### Recommended

- **Mouse support** - For clicking and scrolling
- **Bracketed paste** - For safe multi-line pasting
- **Alternate screen buffer** - For full-screen UI

## Checking Your Terminal

### True Color Support

Run this command to test true color:

```bash
awk 'BEGIN{
    for (i=0; i<256; i++) {
        printf "\033[48;5;%dm  \033[0m", i
        if ((i+1)%16==0) print ""
    }
}'
```

You should see a smooth gradient of colors.

### Unicode Support

Test Unicode rendering:

```bash
echo "Unicode test: Hello World"
```

All characters should display correctly.

## Common Issues

### Colors Look Wrong

1. Ensure `TERM` is set correctly:
   ```bash
   echo $TERM
   # Should be xterm-256color or similar
   ```

2. Try setting it explicitly:
   ```bash
   export TERM=xterm-256color
   ```

### Display Glitches

1. Try a different terminal emulator
2. Ensure your terminal is up to date
3. Check terminal window size (expand if too small)

### Input Issues

1. Check keyboard shortcuts aren't captured by the terminal
2. Disable any terminal multiplexer keybindings that conflict
3. Try running outside of tmux/screen initially

## Terminal Multiplexers

Kin Code works with terminal multiplexers:

### tmux

Works well. Ensure true color is enabled in `~/.tmux.conf`:

```
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"
```

### screen

Basic support. Some features may be limited.

## SSH Sessions

Kin Code works over SSH. Ensure:

1. Your local terminal supports required features
2. SSH is configured to forward terminal capabilities
3. Consider using `ssh -t` for better terminal handling

## Related

- [Installation](installation.md)
- [Troubleshooting Terminal Issues](../troubleshooting/terminal-issues.md)

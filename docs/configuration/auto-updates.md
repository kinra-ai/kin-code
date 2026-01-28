# Auto Updates

Kin Code includes an automatic update feature to keep your installation current.

## Configuration

Enable or disable auto-updates in `config.toml`:

```toml
enable_auto_update = true   # Enabled by default
```

To disable:

```toml
enable_auto_update = false
```

## How It Works

When auto-update is enabled:
1. Kin Code checks for new versions periodically
2. If an update is available, it notifies you
3. Updates are applied automatically (or prompted, depending on settings)

## Manual Updates

Update manually using your package manager:

```bash
# uv
uv tool upgrade kin-code

# pip
pip install --upgrade kin-code

# pipx
pipx upgrade kin-code
```

## Version Checking

Check your current version:

```bash
kin --version
```

## Related

- [Installation](../getting-started/installation.md)
- [Configuration Overview](overview.md)

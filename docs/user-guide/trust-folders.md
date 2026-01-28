# Trust Folders

Kin Code includes a trust folder system to ensure you only run the agent in directories you explicitly trust. This security feature helps prevent accidental execution in sensitive directories.

## How It Works

When you run Kin Code in a directory containing a `.kin-code` subfolder, it checks if the directory is trusted. If not, you'll be prompted to confirm.

```
This folder contains a .kin-code directory.
Do you trust this folder? [y/n]
```

## Why Trust Matters

The `.kin-code` directory can contain:
- Custom configuration (`config.toml`)
- Custom skills
- Custom prompts
- Custom agents

These can modify Kin Code's behavior. The trust system ensures you're aware of project-specific customizations.

## Trusting a Folder

When prompted:
- **y** - Trust this folder for future sessions
- **n** - Don't trust (Kin Code may run with limited features)

## Managing Trusted Folders

### Configuration File

Trusted folders are stored in `~/.kin-code/trusted_folders.toml`:

```toml
[[trusted_folders]]
path = "/Users/name/project-a"
trusted_at = "2026-01-01T00:00:00Z"

[[trusted_folders]]
path = "/Users/name/project-b"
trusted_at = "2026-01-02T00:00:00Z"
```

### Adding Trust Manually

Edit `trusted_folders.toml` to add paths:

```toml
[[trusted_folders]]
path = "/path/to/project"
```

### Removing Trust

Remove entries from `trusted_folders.toml` or delete the file to reset all trust.

## Trust Scope

Trust is granted to:
- The specific directory path
- Not automatically inherited by subdirectories

Each directory with a `.kin-code` folder needs its own trust grant.

## Security Considerations

### What to Trust

Trust directories where:
- You created the `.kin-code` folder
- You trust the project author
- You've reviewed the configuration

### What to Be Careful With

Be cautious with:
- Downloaded projects with `.kin-code` folders
- Shared repositories
- Unknown configurations

### Reviewing Configuration

Before trusting, review:

```bash
cat /path/to/project/.kin-code/config.toml
ls /path/to/project/.kin-code/skills/
```

## Bypassing Trust Checks

For automation or CI environments, you may need to bypass trust checks:

### Environment Variable

```bash
export KIN_TRUST_ALL_FOLDERS=true
kin
```

**Warning**: Only use this in controlled environments.

### Programmatic Mode

In programmatic mode (`--prompt`), trust checks may behave differently depending on configuration.

## Project-Specific Configuration

The trust system enables safe project-specific customization:

```
project/
  .kin-code/
    config.toml      # Project-specific config
    skills/          # Project-specific skills
    prompts/         # Project-specific prompts
```

Once trusted, Kin Code uses these configurations alongside global settings.

## Troubleshooting

### "Trust required" error

- Trust the folder when prompted
- Or add it to `trusted_folders.toml`

### Trust not being saved

- Check write permissions on `~/.kin-code/`
- Verify `trusted_folders.toml` isn't locked

### Unexpected configuration applied

1. Check for `.kin-code` in current directory
2. Review what's in that directory
3. Remove trust if needed

## Related

- [Configuration Overview](../configuration/overview.md)
- [Skills Overview](../skills/overview.md)

# Neovim Integration

Using Kin Code with Neovim via avante.nvim.

## Prerequisites

1. Install Kin Code: `uv tool install kin-code`
2. Configure API keys: `kin --setup`
3. Neovim with avante.nvim plugin

## Configuration

Add to your Neovim configuration:

```lua
{
  acp_providers = {
    ["kin-code"] = {
      command = "kin-acp",
      env = {
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY"),
        -- Or your provider's API key
      },
    }
  }
}
```

## Usage

1. Open Neovim
2. Invoke avante.nvim
3. Select kin-code provider
4. Start chatting

## Environment Variables

Pass API keys through the `env` table:

```lua
env = {
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY"),
  ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY"),
}
```

## Custom Model

Set a specific model:

```lua
env = {
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY"),
  KIN_MODEL = "gpt-4o",
}
```

## Troubleshooting

### Provider Not Available

1. Verify avante.nvim configuration
2. Check `kin-acp` is in PATH
3. Restart Neovim

### API Errors

1. Verify environment variables are set
2. Test `kin-acp` directly
3. Check API key validity

## Related

- [ACP Setup](acp-setup.md)
- [Configuration](../configuration/overview.md)

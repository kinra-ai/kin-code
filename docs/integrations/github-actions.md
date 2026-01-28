# GitHub Actions Integration

Using Kin Code in CI/CD pipelines.

## Basic Usage

```yaml
name: Code Analysis
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install Kin Code
        run: uv tool install kin-code

      - name: Run Analysis
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          kin --prompt "Analyze code quality" \
              --max-turns 10 \
              --output text
```

## Configuration

### Secrets

Store API keys as GitHub secrets:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

### Options

Useful flags for CI:

```yaml
- name: Run Kin Code
  run: |
    kin --prompt "..." \
        --max-turns 5 \
        --max-price 0.50 \
        --output json
```

## Examples

### Code Review

```yaml
- name: Review PR
  run: |
    kin --prompt "Review the changes in this PR" \
        --enabled-tools read_file \
        --enabled-tools grep \
        --output text
```

### Documentation Check

```yaml
- name: Check Docs
  run: |
    kin --prompt "Check documentation coverage" \
        --max-turns 5 \
        --output text
```

## Best Practices

1. **Set cost limits** - Use `--max-price`
2. **Limit turns** - Use `--max-turns`
3. **Restrict tools** - Use `--enabled-tools`
4. **Store secrets securely** - Use GitHub secrets

## Related

- [Programmatic Mode](../user-guide/programmatic-mode.md)
- [CLI Reference](../api-reference/cli-reference.md)

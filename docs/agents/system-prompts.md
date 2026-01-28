# System Prompts

Customize agent behavior with custom system prompts.

## What Are System Prompts?

System prompts are instructions given to the AI model that define how it behaves. They set the context, personality, and capabilities of the agent.

## Default Prompt

Kin Code uses a default prompt (`cli.md`) optimized for coding assistance.

## Custom Prompts

### Creating a Custom Prompt

1. Create a markdown file in `~/.kin-code/prompts/`:

```markdown
<!-- ~/.kin-code/prompts/reviewer.md -->

# Code Reviewer

You are a code review assistant. Focus on:

1. Security vulnerabilities
2. Performance issues
3. Code style and best practices
4. Documentation gaps

Be constructive and specific in your feedback.
```

2. Use the prompt in your agent:

```toml
# ~/.kin-code/agents/reviewer.toml
system_prompt_id = "reviewer"
```

### Or in config.toml

```toml
system_prompt_id = "reviewer"
```

## Prompt Structure

Effective prompts include:

1. **Role definition** - Who the agent is
2. **Capabilities** - What it can do
3. **Guidelines** - How to behave
4. **Constraints** - What to avoid

## Example Prompts

### Minimal

```markdown
You are a helpful coding assistant.
```

### Specialized

```markdown
# Security Analyst

You specialize in finding security vulnerabilities.

## Focus Areas
- SQL injection
- XSS attacks
- Authentication flaws
- Sensitive data exposure

## Approach
1. Read code carefully
2. Identify potential issues
3. Explain the risk
4. Suggest fixes
```

## Related

- [Agents Overview](overview.md)
- [Custom Agents](custom-agents.md)

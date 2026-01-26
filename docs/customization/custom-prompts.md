# Custom Prompts

Define custom system prompts to change agent behavior.

## Overview

System prompts control how the agent responds to your requests. Custom prompts let you tailor the agent for specific tasks or domains.

## Creating a Prompt

Create a Markdown file in `~/.kin-code/prompts/`:

```bash
mkdir -p ~/.kin-code/prompts
touch ~/.kin-code/prompts/myprompt.md
```

Write your prompt:

```markdown
# My Custom Agent

You are a helpful assistant specialized in Python development.

## Guidelines

- Always follow PEP 8 style guidelines
- Prefer type hints in all function definitions
- Use pathlib for file operations
- Write docstrings for all public functions

## Response Style

Be concise and focus on code quality.
```

## Using a Custom Prompt

Set `system_prompt_id` in `config.toml`:

```toml
system_prompt_id = "myprompt"
```

Or in an agent config:

```toml
# ~/.kin-code/agents/python.toml
system_prompt_id = "myprompt"
```

The ID matches the filename without the `.md` extension.

## Built-in Prompts

Kin includes a default prompt (`cli`) optimized for general coding tasks. You can reference it with:

```toml
system_prompt_id = "cli"
```

## Prompt Structure

Effective prompts typically include:

1. **Role definition**: What the agent is and its expertise
2. **Guidelines**: Rules for behavior and code style
3. **Response format**: How to structure answers
4. **Constraints**: What to avoid or be careful about

## Example: Security Auditor

```markdown
# Security Auditor

You are a security-focused code reviewer.

## Focus Areas

- Input validation and sanitization
- Authentication and authorization
- SQL injection and XSS vulnerabilities
- Secure handling of credentials
- OWASP Top 10 vulnerabilities

## Response Format

When reviewing code:
1. Identify the vulnerability
2. Explain the risk
3. Provide a fix

Be thorough but avoid false positives.
```

## Example: Documentation Writer

```markdown
# Documentation Writer

You help write and improve documentation.

## Guidelines

- Use clear, simple language
- Include code examples
- Follow the project's existing documentation style
- Keep explanations concise

## When Asked to Document Code

1. Understand what the code does
2. Write a clear summary
3. Document parameters and return values
4. Include usage examples
```

## Tips

1. **Be specific**: Vague prompts produce vague results
2. **Test iteratively**: Refine prompts based on actual behavior
3. **Include examples**: Show the agent what good output looks like
4. **Consider context**: The prompt combines with project context

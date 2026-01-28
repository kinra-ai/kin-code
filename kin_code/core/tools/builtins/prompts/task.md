Use `task` to delegate work to a subagent running in an isolated context window.

## Why Delegate?

Subagents work in their own context space. When a task requires:
- Reading many files to find patterns
- Fetching and comparing multiple web sources
- Deep analysis that would expand context significantly

...the subagent can do this work and return a synthesized result, preserving
your main context for coordination and user interaction.

## Matching Work to Specialists

| Work Type | Natural Fit | Why |
|-----------|-------------|-----|
| Finding code patterns across files | explore | Reads many files, returns findings |
| Web research and synthesis | web-research | Fetches sources, returns recommendations |
| Planning implementation | planner | Deep analysis, returns structured plan |
| Autonomous code changes | general | Full execution, returns summary |

## Cost-Benefit

Delegation has overhead (spinning up subagent, communicating context, processing result).
For simple tasks - a single file read, a quick grep - doing it directly is more efficient.

Delegate when: specialized work OR context-expensive exploration
Handle directly when: quick lookups OR single tool calls

## Best Practices

1. **Write clear, detailed task descriptions** - The subagent works autonomously, so provide enough context for it to succeed independently

2. **Trust the subagent's judgment** - Let it explore and find information without micromanaging the approach

## Limitations

- Subagents cannot write or modify files
- Subagents cannot ask the user questions
- Results are returned as text when the subagent completes

---
description: "Execute plans, next steps, or fixes from previous analysis"
argument-hint: "[optional: all|critical|task-name or item numbers]"
---

# Execute

Automatically detects and executes work items from the previous response: plans, next steps, fixes, or proposals.

## Usage

```bash
/execute                # Execute everything proposed
/execute critical       # Only critical items
/execute 1,2,5          # Specific items
/execute auth           # Items matching keyword
```

## Flags

- `--research` - Gather fresh context before execution
- `--skip-tests` - Skip testing phase
- `--dry-run` - Show what would execute without running

## What It Does

1. **Detect work items** - Finds plans/fixes/next steps from previous response
2. **Parse tasks** - Extracts actionable items with clear type/category
3. **Delegate to agents** - Launches specialized agents using Task tool
4. **Report** - Documents what agents were launched, what changed, outcomes

## Smart Delegation

**Use the Task tool to launch specialized agents based on work type:**

| Work Type | Agent(s) | When to Use |
|-----------|----------|------------|
| **Code Implementation** | `task-executor` | Writing features, bug fixes, refactoring |
| **Architecture Review** | `architect` | File structure, modularity, coupling issues |
| **Code Quality/Patterns** | `code-reviewer` | Type hints, patterns, linting issues |
| **UX/CLI** | `ux-reviewer` | CLI help text, error messages, user flows |
| **Testing** | `test-validator` | Running tests, coverage analysis |
| **Documentation** | `doc-auditor` | Docstrings, link validation, completeness |
| **Troubleshooting** | `troubleshooter` | Diagnosing bugs, root cause analysis |
| **Design/Planning** | `design-partner` | Feature exploration, architecture decisions |
| **Roadmap** | `roadmap-guide` | Next logical step, dependency ordering |
| **Dependency Health** | `dependency-manager` | Security audit, outdated packages |
| **Security Analysis** | `security-auditor` | Threat modeling, OWASP Top 10 |

## Execution Strategy

**Launch agents in parallel when independent:**
- Independent tasks → Use multiple Task tool calls in one message
- Dependent tasks → Wait for results before launching next agent
- Sequential workflows → Plan steps in roadmap-guide first

**Recommended order for typical work:**
1. **Design/Planning** (if needed) → `design-partner` or `roadmap-guide`
2. **Implementation** (core work) → `task-executor`
3. **Quality & Security** (parallel) → `code-reviewer`, `security-auditor`, `ux-reviewer`
4. **Testing** → `test-validator`
5. **Documentation** → `doc-auditor`
6. **Troubleshooting** (if issues) → `troubleshooter`

## Wave-Based Execution (for `/execute all`)

Large task sets use **managed waves** to prevent context overflow.

**How it works:**
1. Detect total work items from previous response
2. Launch `execute-orchestrator` agent to plan waves
3. Orchestrator groups tasks: 3-5 simple OR 1-2 medium OR 1 complex per wave
4. Orchestrator launches `task-executor` for each wave sequentially
5. Progress tracked in `.claude/wave-state.md`

**Wave allocation:**
- Small (1-3 items) → Single wave
- Medium (4-10 items) → 2-3 waves
- Large (11+ items) → 4+ waves

## When You Execute This Command

**Do this explicitly:**

1. Parse the work items from the previous response
2. **Categorize each item** using the Smart Delegation table
3. **Launch agents in parallel** using the Task tool for independent work
4. Collect results and synthesize findings
5. Report outcomes and any follow-up actions

**DO NOT just do the work yourself.** Delegate to specialized agents.

## Output

Execution report summarizes:
- Agents launched and what they were assigned
- Tasks completed by each agent
- Files changed
- Quality/security status
- Test results
- Issues found and recommendations

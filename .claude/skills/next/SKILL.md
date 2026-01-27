---
description: "Get guided to most logical next step based on project state"
argument-hint: "[optional: describe what you finished or want to work on]"
---

# What Next?

Get guidance on the most logical next development step.

## Usage

```bash
/next                          # What's the next logical task?
/next "I finished task X"      # What comes after X?
/next "I want to work on Y"    # Is that the right next step?
```

## What It Does

Launches the **roadmap-guide agent** (via Task tool) which will:

1. **Check project state** - What's done, in progress, blocked?
2. **Read roadmap** - ROADMAP.md, TODO files, git history
3. **Validate prerequisites** - What must happen first?
4. **Recommend next step** - Most logical task
5. **Explain reasoning** - Why this step matters
6. **Push back if needed** - Warn if skipping prerequisites

## Agent Delegation

| Task | Agent | What It Does |
|------|-------|--------------|
| Roadmap analysis | `roadmap-guide` | Read project state, recommend next step |
| Dependency check | `roadmap-guide` | Validate prerequisites are met |
| Design needed? | `design-partner` | (If recommended) Launch brainstorm for complex tasks |

## How It Works

1. Reads CLAUDE.md and any roadmap files for project context
2. Checks git status and recent commits
3. Runs health checks (`uv run pytest`, `uv run pyright`)
4. Looks for blockers or prerequisites
5. Recommends the most logical next task

## Output Format

```
Roadmap Guide: Your Next Step

## Current Status
- Last completed: [task]
- Tests: PASSING / X failures
- Types: PASSING / X errors
- Blockers: [list or "none"]

## Most Logical Next Step
**What:** [Specific task]
**Why:** [Reasoning]

## Prerequisites Check
- [ ] Design exists?
- [ ] Dependencies met?
- [ ] Tests can validate?

## After This
1. [Following task]
2. [Following task]
```

## When to Use

- Starting a work session
- After completing a task
- Considering a new feature
- Feeling stuck
- Questioning priorities

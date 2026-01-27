---
description: "Explore and design a concept before building"
argument-hint: "<feature or concept to explore>"
---

# Brainstorm

Deep exploration and design thinking for new features before implementation.

## Usage

```bash
/brainstorm "user authentication flow"
/brainstorm "where should config management live?"
/brainstorm "how to handle API rate limiting"
/brainstorm "refactoring the service layer"
```

## What It Does

Launches the **design-partner agent** (via Task tool) which will:

1. **Ask clarifying questions** - Goals, constraints, users, edge cases
2. **Explore existing code** - Find patterns to follow or avoid
3. **Consider architecture** - How does this fit? What's the impact?
4. **Sketch designs** - Data structures, modules, flows
5. **Explore alternatives** - Compare approaches with trade-offs
6. **Surface risks** - What could go wrong? What's unclear?
7. **Create design doc** - Saved to `.claude/notes/brainstorm-[feature].md`
8. **Recommend next steps** - Implementation path

## Agent Delegation

| Phase | Agent | What It Does |
|-------|-------|--------------|
| Design exploration | `design-partner` | Main brainstorming, alternatives, trade-offs |
| Architecture validation | `architect` | (Optional) Validate design fits existing patterns |
| Research | `researcher` | (If applicable) Look up current best practices |

## Architecture Considerations

The design-partner will specifically consider:

| Aspect | Questions |
|--------|-----------|
| **Modularity** | Will this create a monolithic module? How to split responsibilities? |
| **Coupling** | What dependencies are introduced? Can we minimize them? |
| **Boundaries** | Where does this feature's responsibility end? |
| **Patterns** | Does this follow or conflict with existing patterns? |
| **Scale** | Will this approach work as the codebase grows? |

## When to Use

- **New modules or packages** - Need design before building
- **Architectural changes** - Affects multiple parts of system
- **Refactoring plans** - How to restructure without breaking things
- **Pattern decisions** - "Should we use X or Y approach?"
- **Risk assessment** - Feature has complexity or unknowns
- **Trade-off exploration** - Multiple valid approaches exist

## Output Format

```markdown
# Design: [Feature Name]

## Problem Statement
[What we're solving and why]

## Goals
- [Goal 1]
- [Goal 2]

## Proposed Architecture

### Data Models
```python
class FeatureModel(BaseModel):
    ...
```

### Module Structure
```
src/
  feature/
    __init__.py
    models.py
    service.py
```

### Flow
[Description or diagram]

## Alternatives Considered
1. **Option A** - Pros / Cons
2. **Option B** - Pros / Cons

## Risks & Unknowns
- [Risk 1]
- [Unknown that needs research]

## Implementation Path
1. [First step]
2. [Second step]
3. [Testing approach]
```

## Next Steps After Brainstorm

```bash
# Review the design doc
cat .claude/notes/brainstorm-[feature].md

# If design is approved, implement
/execute                     # Execute the implementation plan

# After implementation
/review                      # Review the changes
/test                        # Validate
```

## Tips

- Be specific about what you're exploring
- Mention constraints upfront ("must work with existing auth")
- Ask for alternatives if the first proposal doesn't fit
- Use brainstorm for refactoring plans, not just new features

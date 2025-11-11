You are a technical project manager creating a pull request breakdown plan for a large migration project.

## Context

You have access to a comprehensive Pydantic V2 migration plan at `/home/user/octohook/plan.md`. This plan outlines migrating the Octohook library from manual class initialization to Pydantic V2, affecting:
- ~59 model classes in `octohook/models.py`
- ~48 event classes in `octohook/events.py`
- Test infrastructure in `tests/test_models.py`
- The `parse()` function and related utilities

## Your Task

Read the migration plan and create a **functionality-based PR breakdown**. Group changes by functional area (infrastructure, models, events, tests) rather than by pattern or complexity.

## Approach: By Functionality

Break the work into PRs based on logical functional boundaries:
1. **Foundation PR(s)**: Dependencies, base classes, helper functions
2. **Models PR(s)**: All model class migrations (may split if too large)
3. **Events PR(s)**: All event class migrations
4. **Parse Function PR**: Update `parse()` to use `model_validate()`
5. **Tests PR**: Update test infrastructure

For the models migration (59 classes), consider whether it makes sense as:
- Single large PR (establish all patterns at once)
- 2 PRs split by complexity (simple/nested first, then complex/template URLs)
- 3+ PRs if needed for reviewability

## Output Format

Create **separate documents** for each PR:

1. First, create an overview document at `/home/user/octohook/pr-overview.md`:

---
# Pydantic V2 Migration - Pull Request Overview

## Summary
[Total number of PRs and strategy summary]

## PR Sequence
1. PR #1: [Title] - [One-line description]
2. PR #2: [Title] - [One-line description]
3. PR #3: [Title] - [One-line description]
...

## Critical Path
[Which PRs block others, minimum viable sequence]

## Rollback Strategy
[Brief guidance on reverting if needed]

## Breaking Changes
[Summary of frozen=True and strict=True implications]
---

2. Then, create individual PR documents at `/home/user/octohook/pr-{N}.md` for each PR:

---
# PR #{N}: [Title]

## Scope
[One-line description]

## Files Changed
- `path/to/file.py` - [what changes]
- `path/to/other.py` - [what changes]

## Detailed Changes

### [Section 1]
- [Specific task 1]
- [Specific task 2]

### [Section 2]
- [Specific task 3]
- [Specific task 4]

## Dependencies
[None / Requires PR #X to be merged first]

## Testing Strategy

---
# Run these commands to verify
uv run pytest tests/test_x.py -v

# Additional verification
[Manual steps if needed]
---

## Risk Level
[Low / Medium / High]

## Rationale
[Why these changes are grouped together, why this order]

## Lines Changed (Est)
~XXX lines

## Rollback Instructions
[How to revert this specific PR if needed]
---

## Requirements

- **Atomic PRs**: Each PR leaves codebase in working state
- **Reviewable size**: Target 200-500 lines, max 800 if possible
- **Clear dependencies**: Mark which PRs must come first
- **Testable**: Include verification commands
- **Breaking changes documented**: Note immutability and strict typing implications

## Key Considerations

1. **Base infrastructure must come first** - BaseGithubModel changes are foundational
2. **The `_transform()` bug fix** (Step 2.2) fixes a critical bug - include in appropriate PR
3. **Model dependencies** - Some models reference others (e.g., Repository needs User)
4. **Test updates** - Can be incremental or final validation step
5. **Breaking changes** - frozen=True and strict=True need clear documentation

## Implementation Instructions

1. Read `/home/user/octohook/plan.md` completely
2. Determine the optimal number of PRs (likely 4-6 PRs)
3. Use the Write tool to create `/home/user/octohook/pr-overview.md`
4. Use the Write tool to create each PR document: `/home/user/octohook/pr-1.md`, `/home/user/octohook/pr-2.md`, etc.
5. Ensure each PR document is detailed and actionable
6. Cross-reference PR dependencies clearly

## Deliverable

A set of markdown files that a development team can use to execute this migration:
- `pr-overview.md` - High-level overview and strategy
- `pr-1.md` through `pr-N.md` - Detailed specifications for each pull request

Each file should be complete, self-contained, and ready for implementation.

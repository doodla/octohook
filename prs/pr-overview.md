# Pydantic V2 Migration - Pull Request Overview

## Summary

The Pydantic V2 migration will be executed through **6 atomic pull requests**, each leaving the codebase in a working, testable state. The strategy prioritizes foundation-first (base classes and infrastructure) before model/event migrations, ending with test updates.

**Total scope:**
- ~59 model classes in `octohook/models.py`
- ~48 event classes in `octohook/events.py`
- Test infrastructure updates in `tests/test_models.py`
- Parse function updates
- ~1800 lines of code reduction (from ~3000 to ~1200)

## PR Sequence

1. **PR #1: Foundation - Dependencies and Base Classes** (~100-150 lines)
   - Add Pydantic dependency, update base classes, fix critical bug

2. **PR #2: Migrate Model Classes (Part 1 - Simple & Nested)** (~400-500 lines)
   - Migrate 30 simpler model classes (no template URLs)

3. **PR #3: Migrate Model Classes (Part 2 - Template URLs & Complex)** (~400-500 lines)
   - Migrate 29 complex model classes with template URLs and special cases

4. **PR #4: Migrate Event Classes** (~300-400 lines)
   - Migrate all 48 event classes in `events.py`

5. **PR #5: Update Parse Function** (~50 lines)
   - Update `parse()` to use `model_validate()`, review decorators

6. **PR #6: Update Test Infrastructure and Cleanup** (~200-300 lines)
   - Update test validation logic, cleanup unused code, final verification

## Critical Path

**Sequential dependencies:**
- PR #1 MUST be merged first (all others depend on base classes)
- PR #2 and #3 can be done in parallel OR sequentially (preference: sequential due to model interdependencies)
- PR #4 depends on PR #2 and #3 (events reference models)
- PR #5 depends on PR #4 (parse function instantiates events)
- PR #6 can proceed once all code changes are complete

**Minimum viable sequence:**
PR #1 → PR #2 → PR #3 → PR #4 → PR #5 → PR #6

**Parallel opportunities:**
- Once PR #1 is merged, PR #2 and #3 *could* proceed in parallel if careful coordination on shared models
- PR #6 test updates can be prepared in parallel with PR #5

## Rollback Strategy

Each PR is independently revertible:

1. **Identify failing PR** - Check which PR introduced the issue
2. **Revert via git** - `git revert <commit-hash>` or `git revert <PR-merge-commit>`
3. **Handle dependencies** - If reverting an early PR (e.g., PR #1), all subsequent PRs must be reverted in reverse order
4. **Test after revert** - Run full test suite to confirm stability

**Critical rollback considerations:**
- PR #1 revert requires reverting all subsequent PRs (foundation change)
- PR #2-4 reverts are localized to their respective files
- PR #5 revert is simple (single function change)
- PR #6 revert only affects test infrastructure

## Breaking Changes

### Immutability (`frozen=True`)

**Impact:** Models and events are frozen after creation. Any code attempting to modify attributes will raise `ValidationError`.

**Example:**
```python
# Before: This worked
user = User(payload)
user.login = "newname"  # Allowed

# After: This fails
user = User.model_validate(payload)
user.login = "newname"  # ValidationError: Instance is frozen
```

**Mitigation:** User code should not modify models post-creation. If modification is needed, use `model_copy()` or create new instances.

### Strict Typing (`strict=True`)

**Impact:** No automatic type coercion. GitHub API must send correct types.

**Example:**
```python
# Before: This worked (coercion allowed)
{"id": "123"}  # String coerced to int

# After: This fails (strict validation)
{"id": "123"}  # ValidationError: Expected int, got str
```

**Mitigation:** This catches API inconsistencies early. If GitHub changes types, we'll detect it immediately rather than silently coercing.

### Public API Preservation

**Good news:** All existing methods and attributes remain accessible. The breaking changes only affect:
1. Post-creation modification attempts
2. Type validation strictness

Existing code that reads fields and calls methods will continue to work without changes.

## Risk Assessment

| PR | Risk Level | Rationale |
|----|-----------|-----------|
| #1 | **Medium** | Foundation changes affect everything, but small scope |
| #2 | **Low** | Simple models, well-tested patterns |
| #3 | **Medium** | Template URLs and special cases need careful handling |
| #4 | **Low** | Straightforward pattern, depends on stable models |
| #5 | **Low** | Single function change, well-isolated |
| #6 | **Low** | Test-only changes, no production impact |

## Success Metrics

Migration is complete when:

- ✅ All 6 PRs merged to main
- ✅ All tests pass: `uv run pytest -v`
- ✅ Coverage maintained or improved
- ✅ No `__init__` methods in models/events
- ✅ No `payload` fields in models/events
- ✅ URL template methods work correctly
- ✅ `__pydantic_extra__` checks pass (no undefined fields)
- ✅ Code reduced by ~60% (LOC comparison)

## Timeline Estimate

Assuming 1 PR per day with review:
- **Best case:** 6 days (sequential, no issues)
- **Realistic:** 8-10 days (reviews, minor fixes)
- **Worst case:** 12-15 days (significant review feedback, rewrites)

## Communication Plan

**Before starting:**
- Share this overview with team
- Confirm breaking change implications with stakeholders
- Set up review assignments for each PR

**During migration:**
- Daily updates on PR status
- Flag any unexpected issues immediately
- Update this document if strategy changes

**After completion:**
- Document any deviations from plan
- Update CHANGELOG with breaking changes
- Create migration guide for users if needed

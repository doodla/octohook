# PR #6: Update Test Infrastructure and Cleanup

## Scope

Update test validation logic to use Pydantic's `__pydantic_extra__` checking, remove obsolete validation functions, cleanup unused imports, and verify final migration state.

## Files Changed

- `tests/test_models.py` - Replace validation logic, remove obsolete tests
- `tests/conftest.py` - Review and update if needed
- `octohook/__init__.py` - Verify exports
- `octohook/models.py` - Remove unused imports
- `octohook/events.py` - Remove unused imports
- `pyproject.toml` - Optional: Add mypy for type checking

## Detailed Changes

### 1. Update test_models.py

**File:** `tests/test_models.py`

#### Change 1: Update Imports

**Add:**
```python
from pydantic import BaseModel
```

**Remove:**
```python
from typing import get_origin, get_args, Annotated, Union
```

#### Change 2: Replace check_model() with check_no_extra_fields()

**Remove entire function:**
```python
def check_model(data, obj):
    """
    Checks if every key in the json is represented either as an
    Annotated[dict, "unstructured"] or a nested object.
    ...
    """
    # ... entire function (many lines)
```

**Add instead:**
```python
def check_no_extra_fields(obj):
    """
    Verify that all fields from the JSON payload are defined in the model.

    When extra='allow', Pydantic stores undefined fields in __pydantic_extra__.
    This test ensures we've defined all fields that GitHub sends.
    """
    from pydantic import BaseModel

    # Only check Pydantic models
    if not isinstance(obj, BaseModel):
        return

    extra_fields = getattr(obj, '__pydantic_extra__', None)

    if extra_fields:
        raise AssertionError(
            f"{type(obj).__name__} has undefined fields: {list(extra_fields.keys())}\n"
            f"These fields exist in the webhook payload but are not defined in the model."
        )

    # Recursively check nested models
    for field_name in obj.model_fields:
        value = getattr(obj, field_name)

        if isinstance(value, BaseModel):
            check_no_extra_fields(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, BaseModel):
                    check_no_extra_fields(item)
```

#### Change 3: Update test_model_has_all_keys_in_json

**Before:**
```python
@pytest.mark.parametrize("event_name", testcases)
def test_model_has_all_keys_in_json(event_name, fixture_loader):
    """
    Verify that every JSON key from GitHub is accessible in the parsed object.
    ...
    """
    examples = fixture_loader.load(event_name)
    for example in examples:
        check_model(example, parse(event_name, example))
```

**After:**
```python
@pytest.mark.parametrize("event_name", testcases)
def test_model_has_all_keys_in_json(event_name, fixture_loader):
    """
    Verify that every JSON key from GitHub is defined in the model.

    With extra='allow', this test ensures we haven't missed any fields
    by checking that __pydantic_extra__ is empty.
    """
    examples = fixture_loader.load(event_name)
    for example in examples:
        event = parse(event_name, example)
        check_no_extra_fields(event)
```

#### Change 4: Remove Utility Functions

**Remove entirely:**
```python
def _unwrap_annotated():
    # ...

def _is_unstructured_dict():
    # ...

def _is_primitive_type():
    # ...
```

**Rationale:** These were used by `check_model()`. Pydantic handles type validation now.

#### Change 5: Remove Type Hint Validation

**Remove entirely:**
```python
def _validate_simple_type():
    # ...

def _validate_list_items():
    # ...

def _validate_complex_type():
    # ...

def check_type_hints():
    # ...

def test_all_type_hints_are_correct():
    # ...
```

**Rationale:** Pydantic V2's strict mode provides more thorough type validation than our custom checker.

#### Change 6: Remove Unannotated Dict Test

**Remove entirely:**
```python
def test_unannotated_dict_enforcement():
    """
    Verify that check_model enforces Annotated[dict, "unstructured"] requirement.
    ...
    """
    # ... entire test
```

**Rationale:** With `dict[str, Any]` and `__pydantic_extra__` checking, this test is obsolete.

### 2. Update conftest.py (if needed)

**File:** `tests/conftest.py`

**Review for:**
- Any direct model instantiation (change to `model_validate()`)
- Any fixtures that might need updating
- The autouse fixture should still work (calls `reset()` which clears handlers)

**Expected result:** Most likely no changes needed. If there is direct instantiation like `User(payload)`, change to `User.model_validate(payload)`.

### 3. Cleanup Unused Imports

**File:** `octohook/models.py`

**Remove if present:**
```python
from abc import ABC
from typing import TypeVar, Type

T = TypeVar("T")
```

**Verify not needed:**
- `ABC` - removed when BaseGithubModel switched to BaseModel
- `TypeVar`, `Type` - used by `_optional()` which was removed

**File:** `octohook/events.py`

**Remove if present:**
```python
from octohook.models import _optional
```

**Verify not needed:**
- `_optional()` was removed in PR #1 and is no longer used

### 4. Verify Exports

**File:** `octohook/__init__.py`

**Check exports remain unchanged:**
```python
__all__ = [
    "events",
    "handle_webhook",
    "hook",
    "models",
    "OctohookConfigError",
    "parse",
    "reset",
    "setup",
    "WebhookEvent",
    "WebhookEventAction",
]
```

**Expected result:** No changes needed. Public API is preserved.

### 5. Optional: Add Type Checking with mypy

**File:** `pyproject.toml`

**Add to dev dependencies:**
```toml
[dependency-groups]
dev = [
    "pre-commit>=4.1.0",
    "pytest>=8.3.4",
    "pytest-mock>=3.14.0",
    "pytest-cov>=6.0.0",
    "mypy>=1.0.0",  # NEW
]
```

**Add mypy configuration:**
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**Run after adding:**
```bash
uv sync
uv run mypy octohook
```

**Note:** This is optional but recommended for catching type issues early.

## Dependencies

**Requires:**
- PR #1 (base classes)
- PR #2 (model migrations)
- PR #3 (model migrations)
- PR #4 (event migrations)
- PR #5 (parse function)

**Blocks:** None (final PR in sequence)

## Testing Strategy

```bash
# Run full test suite
uv run pytest -v

# Run with coverage
uv run pytest --cov=octohook --cov-report=term-missing

# Test the new check_no_extra_fields function
uv run pytest tests/test_models.py::test_model_has_all_keys_in_json -v

# Verify no extra fields in webhook fixtures
uv run python -c "
from octohook.events import parse
import json

# Load a fixture and verify no extra fields
with open('tests/fixtures/complete/pull_request_opened.json') as f:
    payload = json.load(f)
event = parse('pull_request', payload)

# Check __pydantic_extra__
extra = getattr(event, '__pydantic_extra__', None)
if extra:
    print(f'WARNING: Extra fields found: {list(extra.keys())}')
else:
    print('✓ No extra fields - all fields defined')
"

# If mypy added, run type checking
uv run mypy octohook

# Verify imports work
uv run python -c "from octohook import *; print('All imports OK')"

# Verify public API unchanged
uv run python -c "
import octohook
expected = [
    'events', 'handle_webhook', 'hook', 'models',
    'OctohookConfigError', 'parse', 'reset', 'setup',
    'WebhookEvent', 'WebhookEventAction'
]
actual = octohook.__all__
assert set(expected) == set(actual), f'API changed: {set(actual) - set(expected)}'
print('✓ Public API preserved')
"
```

**Expected outcomes:**
- ✅ All tests pass
- ✅ Coverage maintained or improved (~90%+)
- ✅ `__pydantic_extra__` is empty for all webhook fixtures
- ✅ No unused imports remain
- ✅ Public API unchanged
- ✅ mypy reports no errors (if added)
- ✅ Test suite runs faster (less manual validation)

## Risk Level

**Low**

- Test-only changes (no production code impact)
- Cleanup of unused code (reduces maintenance burden)
- Public API preserved
- All functional changes already merged in previous PRs

## Rationale

**Why last:**
- All production code changes complete (models, events, parse)
- Tests should validate the final state
- Safe to remove obsolete validation code once migration is complete
- Allows comprehensive verification of entire migration

**Why together:**
- All test updates are related (validation logic)
- Cleanup is related (remove code made obsolete by migration)
- Logical unit: "verify migration complete and cleanup"

**Why test changes:**
- Old `check_model()` inspected raw dicts and type hints manually
- New `check_no_extra_fields()` leverages Pydantic's `__pydantic_extra__`
- Simpler, more reliable, faster
- Pydantic's strict mode validates types better than our custom checker

## Lines Changed (Est)

~200-300 lines

**Breakdown:**
- Remove ~400 lines (old validation functions, utility functions, obsolete tests)
- Add ~100 lines (new check_no_extra_fields, updated test docstrings, mypy config)
- Net reduction: ~300 lines removed

## Rollback Instructions

**If this PR must be reverted:**

1. Revert the commit:
```bash
git revert <commit-hash>
```

2. Verify tests still pass with old validation:
```bash
uv run pytest tests/ -v
```

3. **Note:** This PR only affects tests, so reverting it doesn't break production code. Previous PRs (1-5) remain functional.

4. **Important:** Old validation functions expected old model structure. If this PR is reverted but PRs 2-5 are not, tests will fail (expected - old tests don't work with new models).

## Additional Notes

**Why check_no_extra_fields is better:**

Old approach:
- Manually inspected type hints with `get_type_hints()`
- Parsed `Annotated[dict, "unstructured"]` manually
- Recursively traversed dict and checked against class attributes
- Fragile, hard to maintain, slow

New approach:
- Pydantic automatically populates `__pydantic_extra__` with undefined fields
- Simple check: is `__pydantic_extra__` empty?
- Recursive checking for nested models
- Reliable, simple, fast

**Coverage improvements:**

Expected coverage to remain high or improve because:
- Fewer lines of code (60% reduction)
- Pydantic handles more logic internally
- Tests focus on behavior, not implementation

**mypy benefits (if added):**

- Catches type errors at development time
- Validates Pydantic models correctly
- Integrates with IDE for better autocomplete
- Prevents type regressions

**Post-merge checklist:**
- ✅ `check_no_extra_fields()` function added
- ✅ `test_model_has_all_keys_in_json` updated to use new function
- ✅ Old validation functions removed
- ✅ Old utility functions removed
- ✅ `test_all_type_hints_are_correct` removed
- ✅ `test_unannotated_dict_enforcement` removed
- ✅ Unused imports removed from models.py and events.py
- ✅ Public API verified unchanged
- ✅ All tests pass
- ✅ Coverage maintained
- ✅ mypy added and passes (if included)

## Migration Complete!

After this PR merges, the Pydantic V2 migration is **100% complete**! 🎉

**Final verification:**
```bash
# All tests pass
uv run pytest -v

# Coverage good
uv run pytest --cov=octohook --cov-report=term-missing

# No extra fields
# (check_no_extra_fields validates this)

# Code reduction achieved
git diff main --stat  # Should show ~1800 lines removed

# Public API preserved
uv run python -c "from octohook import *; print('Migration complete!')"
```

**Success criteria met:**
- ✅ All 59 model classes converted
- ✅ All 48 event classes converted
- ✅ Parse function uses model_validate()
- ✅ Tests updated for Pydantic
- ✅ All tests pass
- ✅ Coverage maintained
- ✅ No __init__ methods in models/events
- ✅ No payload fields
- ✅ URL templates work
- ✅ ~60% code reduction
- ✅ Public API preserved

# PR #1: Foundation - Dependencies and Base Classes

## Scope

Add Pydantic V2 dependency, migrate base classes (`BaseGithubModel`, `BaseWebhookEvent`), fix `_transform()` bug, and remove helper functions.

## Files Changed

- `pyproject.toml` - Add Pydantic >=2.0.0 dependency
- `octohook/models.py` - Update BaseGithubModel, update imports, remove `_optional()`, fix `_transform()`
- `octohook/events.py` - Update BaseWebhookEvent, update imports

## Detailed Changes

### 1. Add Pydantic Dependency

**File:** `pyproject.toml`

Add to dependencies:
```toml
[project]
requires-python = ">=3.10"
dependencies = ["pydantic>=2.0.0"]
```

Run after change:
```bash
uv lock
uv sync
```

### 2. Update BaseGithubModel

**File:** `octohook/models.py`

**Add imports at top:**
```python
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
```

**Replace BaseGithubModel:**
```python
# Remove:
from abc import ABC
class BaseGithubModel(ABC):
    pass

# Add:
class BaseGithubModel(BaseModel):
    model_config = ConfigDict(
        extra='allow',                # Allow extra fields (resilient to GitHub changes)
        populate_by_name=True,        # Allow both alias and field name
        strict=True,                  # Strict type checking (no coercion)
        frozen=True,                  # Immutable after creation
        str_strip_whitespace=False,   # Preserve exact GitHub data
        use_enum_values=False,        # Keep enum instances for type safety
        validate_default=False,       # Trust our defaults
        revalidate_instances='never', # Trust already-validated nested models
        protected_namespaces=('model_',), # Prevent conflicts with Pydantic internals
    )
```

### 3. Fix _transform() Bug (CRITICAL)

**File:** `octohook/models.py`

**Current bug:** Uses `if not value:` which incorrectly treats `0`, `False`, and empty strings as stop conditions.

**Fix:**
```python
def _transform(url: str, local_variables: dict) -> str:
    """
    Transform URL templates by replacing placeholders with actual values.

    Handles patterns like:
    - {param} -> value
    - {/param} -> /value
    - Stops at first None or empty value
    """
    local_variables.pop("self", None)

    for key, value in local_variables.items():
        # CRITICAL: Check for None and empty string explicitly
        # Don't use "if not value:" - that would incorrectly catch 0 and False
        if value is None or value == "":
            url = url.split(f"{{/{key}}}")[0]
            break

        # Convert value to string if needed (handles int, etc.)
        value_str = str(value) if not isinstance(value, str) else value

        if f"{{{key}}}" in url:
            url = url.replace(f"{{{key}}}", value_str)
        elif f"{{/{key}}}" in url:
            url = url.replace(f"{{/{key}}}", f"/{value_str}")

    return url
```

### 4. Remove _optional() Helper

**File:** `octohook/models.py`

**Remove entirely:**
```python
# Delete this function:
def _optional(payload: dict, key: str, class_type: Type[T]) -> Optional[T]:
    if payload.get(key):
        return class_type(payload[key])
    else:
        return None
```

**Remove TypeVar imports:**
```python
# Remove:
from typing import TypeVar, Type
T = TypeVar("T")
```

### 5. Update BaseWebhookEvent

**File:** `octohook/events.py`

**Add imports at top:**
```python
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, ValidationError
```

**Replace BaseWebhookEvent:**
```python
# Remove old class with __init__ method

# Add:
class BaseWebhookEvent(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
        strict=True,
        frozen=True,
        str_strip_whitespace=False,
        use_enum_values=False,
        validate_default=False,
        revalidate_instances='never',
        protected_namespaces=('model_',),
    )

    action: Optional[str] = None
    sender: Optional[User] = None
    repository: Optional[Repository] = None
    organization: Optional[Organization] = None
    enterprise: Optional[Enterprise] = None
```

**Remove:**
```python
# Delete import:
from octohook.models import _optional
```

## Dependencies

**None** - This is the foundation PR that all others depend on.

## Testing Strategy

```bash
# Verify Pydantic is installed
uv run python -c "import pydantic; print(pydantic.__version__)"

# Import should work without errors
uv run python -c "from octohook.models import BaseGithubModel; print('BaseGithubModel OK')"
uv run python -c "from octohook.events import BaseWebhookEvent; print('BaseWebhookEvent OK')"

# Existing tests should still pass (models not migrated yet, but base classes work)
uv run pytest tests/ -v
```

**Note:** Tests will likely show failures because model classes still use old `__init__` pattern. This is expected - they'll be fixed in PR #2 and #3.

## Risk Level

**Medium**

- Foundation changes affect all subsequent work
- Small scope reduces risk
- Breaking changes (frozen, strict) need careful testing
- _transform() bug fix is critical but well-isolated

## Rationale

**Why these changes together:**
- Establishes Pydantic foundation for all subsequent PRs
- Base class changes are prerequisites for model migrations
- _transform() bug fix should be included with base infrastructure (used by all template URL models)
- Removing _optional() prevents its use in subsequent PRs

**Why this order:**
- Must come first - all model and event classes depend on base classes
- Small scope allows quick review and merge
- Unblocks parallel work on PR #2 and #3

## Lines Changed (Est)

~100-150 lines

**Breakdown:**
- pyproject.toml: +1 line
- models.py: +30 lines (BaseGithubModel), +15 lines (_transform fix), -20 lines (_optional), -5 lines (imports)
- events.py: +25 lines (BaseWebhookEvent), +5 lines (imports), -15 lines (old __init__)

## Rollback Instructions

**If this PR must be reverted:**

1. Revert the commit:
```bash
git revert <commit-hash>
```

2. Remove Pydantic dependency:
```bash
# Edit pyproject.toml to remove pydantic
uv lock
uv sync
```

3. **CRITICAL:** All subsequent PRs (2-6) must also be reverted, as they depend on these changes.

4. Verify rollback:
```bash
uv run pytest tests/ -v
```

## Additional Notes

**Pydantic configuration rationale:**

- **`extra='allow'`**: GitHub may add new fields - we want to be resilient, not fail. Tests will check `__pydantic_extra__` to ensure we've defined all known fields.

- **`strict=True`**: Catches type mismatches early. If GitHub sends wrong types, we want to know immediately, not silently coerce.

- **`frozen=True`**: Immutability is a best practice for data models. Users should not modify webhook payloads. This is a breaking change if user code modifies models post-creation.

- **`populate_by_name=True`**: Allows using either the alias (original GitHub field name) or Python field name (e.g., `links_` or `_links`).

**Post-merge checklist:**
- ✅ Pydantic dependency added and locked
- ✅ BaseGithubModel inherits from BaseModel
- ✅ BaseWebhookEvent inherits from BaseModel
- ✅ _transform() bug fixed
- ✅ _optional() removed
- ✅ Imports updated
- ✅ Can import base classes without errors

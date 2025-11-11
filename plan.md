# Pydantic V2 Migration Plan

## Executive Summary

This document outlines the complete migration of Octohook from manual class initialization to Pydantic V2 models.

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Pydantic Version** | V2 (2.x) | Latest, better performance, long-term support |
| **Template URL Fields** | Field aliases | Explicit, self-documenting, Pydantic-idiomatic |
| **Unstructured Dicts** | `dict[str, Any]` | Standard Pydantic approach, clear typing |
| **Extra Fields** | `extra='allow'` in production | Resilient to GitHub API changes |
| **Test Validation** | Check `__pydantic_extra__` | Ensures all fields are defined without breaking production |
| **Strict Mode** | `strict=True` | No type coercion, catch type issues early |
| **Immutability** | `frozen=True` | Models immutable after creation, safer |

### Impact

- **Code Reduction:** ~3000 lines → ~1200 lines (60% reduction)
- **Models Affected:** ~40 model classes + ~40 event classes
- **Template URL Fields:** ~60 fields across all models
- **Dependencies:** Add `pydantic>=2.0.0`
- **Breaking Changes:**
  - **Immutability**: Models frozen after creation (`frozen=True`) - user code cannot modify attributes
  - **Strict typing**: No type coercion (`strict=True`) - may catch issues if GitHub API sends wrong types
  - Public API preserved - all existing methods and attributes remain accessible

---

## Phase 1: Setup & Dependencies

### Step 1.1: Add Pydantic Dependency

**File:** `pyproject.toml`

**Change:**
```toml
[project]
requires-python = ">=3.10"
dependencies = ["pydantic>=2.0.0"]
```

**Action:** Run `uv lock` to update lock file

**Verification:**
```bash
uv lock
uv sync
```

---

### Step 1.2: Update BaseGithubModel

**File:** `octohook/models.py`

**Before:**
```python
from abc import ABC

class BaseGithubModel(ABC):
    pass
```

**After:**
```python
from pydantic import BaseModel, ConfigDict

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

**Critical configuration notes:**

- **`strict=True`**: GitHub must send correct types (no coercion). If GitHub sends `"123"` for an `int` field, validation will fail. This is intentional - catches API changes early.

- **`frozen=True`**: Models are immutable after creation. Any code that tries to modify attributes will fail with `ValidationError`. This is a potential breaking change if user code modifies models post-creation.

- **`extra='allow'`**: Unknown fields are stored in `__pydantic_extra__` dict. Tests check this is empty to ensure all fields are defined.

- **`validate_assignment=False`**: Removed from original plan - redundant since `frozen=True` already prevents assignment.

**Verification:** Import should work without errors

---

## Phase 2: Migrate Model Classes (models.py)

### Step 2.1: Update Imports at Top of File

**File:** `octohook/models.py` (top)

**Add:**
```python
from __future__ import annotations  # Enable forward references for type hints

from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field
```

**Remove:**
```python
from abc import ABC
from typing import TypeVar, Type

T = TypeVar("T")
```

**Note on forward references:** The `from __future__ import annotations` import enables using class names in type hints before they're defined (e.g., `User` can reference `Organization` even if `Organization` is defined later). This prevents circular dependency issues and is a Python best practice for type hints.

---

### Step 2.2: Remove Helper Functions

**File:** `octohook/models.py`

**Remove entirely:**
```python
def _optional(payload: dict, key: str, class_type: Type[T]) -> Optional[T]:
    if payload.get(key):
        return class_type(payload[key])
    else:
        return None
```

**Keep and update:**
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

**Critical fix:** The original code uses `if not value:` which incorrectly treats `0`, `False`, and empty strings as stop conditions. The updated version explicitly checks for `None` and empty string only.

---

### Step 2.3: Model Migration Pattern

For each model class, follow this pattern:

#### Pattern for Simple Models (No Template URLs)

**Before:**
```python
class Enterprise(BaseGithubModel):
    payload: dict
    id: int
    slug: str
    name: str
    node_id: str
    avatar_url: str
    description: Optional[str]
    website_url: Optional[str]
    html_url: str
    created_at: str
    updated_at: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.slug = payload.get("slug")
        self.name = payload.get("name")
        self.node_id = payload.get("node_id")
        self.avatar_url = payload.get("avatar_url")
        self.description = payload.get("description")
        self.website_url = payload.get("website_url")
        self.html_url = payload.get("html_url")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")

    def __str__(self):
        return self.name
```

**After:**
```python
class Enterprise(BaseGithubModel):
    id: int
    slug: str
    name: str
    node_id: str
    avatar_url: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    html_url: str
    created_at: str
    updated_at: str

    def __str__(self):
        return self.name
```

**Key changes:**
- ✅ Remove `payload: dict` field
- ✅ Remove `__init__` method entirely
- ✅ Add `= None` defaults for all `Optional` fields
- ✅ Keep `__str__`, `__repr__`, `__eq__`, `__hash__` and other custom methods
- ⚠️ **Important:** Only `Label` class has custom `__eq__` and `__repr__` methods - preserve these!

---

#### Pattern for Models with Nested Objects

**Before:**
```python
class Repository(BaseGithubModel):
    payload: dict
    id: int
    owner: User
    permissions: Optional[Permissions]
    topics: List[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.owner = User(payload.get("owner"))
        self.permissions = _optional(payload, "permissions", Permissions)
        self.topics = payload.get("topics") or []
```

**After:**
```python
class Repository(BaseGithubModel):
    id: int
    owner: User                          # Pydantic auto-validates nested model
    permissions: Optional[Permissions] = None  # Auto-handles None
    topics: List[str] = []               # Default to empty list
```

**Key changes:**
- ✅ Nested models: Just type as `User`, Pydantic handles instantiation
- ✅ Optional nested: `Optional[Permissions] = None`
- ✅ Lists with defaults: `List[str] = []` (Pydantic V2 handles this safely)
- ✅ Lists of models: `List[User]` - Pydantic auto-validates each item
- ✅ No manual instantiation needed (`User(...)` or `_optional(...)`)
- ✅ No list comprehensions needed (`[User(x) for x in ...]` becomes just the type hint)

---

#### Pattern for Models with List Comprehensions

**Before:**
```python
class Thread(BaseGithubModel):
    payload: dict
    node_id: str
    comments: List[Comment]

    def __init__(self, payload: dict):
        self.payload = payload
        self.node_id = payload.get("node_id")
        self.comments = [Comment(comment) for comment in payload.get("comments")]
```

**After:**
```python
class Thread(BaseGithubModel):
    node_id: str
    comments: List[Comment]  # Pydantic auto-validates each Comment
```

**Key pattern:**
- ✅ Remove list comprehension entirely
- ✅ Pydantic automatically validates each list item against the model type
- ✅ Works for: `List[Comment]`, `List[Label]`, `List[User]`, etc.
- ✅ For empty list defaults: Use `List[Comment] = []` (safe with Pydantic V2)

**Models with list comprehensions to migrate:**
- `Thread.comments`: `[Comment(comment) for comment in ...]`
- `Issue.labels`: `[Label(label) for label in ...]`
- `Issue.assignees`: `[User(assignee) for assignee in ...]`
- `Release.assets`: `[Asset(asset) for asset in payload.get("assets", [])]`
- `PullRequest.assignees`: `[User(assignee) for assignee in ...]`
- `PullRequest.labels`: `[Label(item) for item in ...]`
- `StatusCommit.parents`: `[StatusBranchCommit(parent) for parent in ...]`

---

#### Pattern for Models with Template URLs

**Before:**
```python
class User(BaseGithubModel):
    payload: dict
    login: str
    # ... other fields

    def __init__(self, payload: dict):
        self.payload = payload
        self.login = payload.get("login")
        # ...

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.payload["following_url"], locals())

    def gists_url(self, gist_id: str = None) -> str:
        return _transform(self.payload["gists_url"], locals())
```

**After:**
```python
class User(BaseGithubModel):
    login: str
    # ... other regular fields

    # Template URL fields with aliases
    following_url_template: str = Field(alias="following_url")
    gists_url_template: str = Field(alias="gists_url")

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.following_url_template, locals())

    def gists_url(self, gist_id: str = None) -> str:
        return _transform(self.gists_url_template, locals())
```

**Key pattern for template URLs:**
1. ✅ Field name: `{method_name}_template`
2. ✅ Add alias: `Field(alias="{original_name}")`
3. ✅ Update method to use `self.{field_name}_template` instead of `self.payload["{field_name}"]`
4. ✅ Keep method signature and logic unchanged

---

#### Pattern for Models with Unstructured Dicts

**Before:**
```python
class Comment(BaseGithubModel):
    payload: dict
    id: int
    body: str
    reactions: Optional[Annotated[dict, "unstructured"]]
    _links: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.body = payload.get("body")
        self.reactions = payload.get("reactions")
        self._links = payload.get("_links")
```

**After:**
```python
class Comment(BaseGithubModel):
    id: int
    body: str
    reactions: Optional[dict[str, Any]] = None
    links_: Optional[dict[str, Any]] = Field(None, alias="_links")
```

**Key changes:**
- ✅ `Annotated[dict, "unstructured"]` → `dict[str, Any]`
- ✅ Fields starting with `_` must be renamed (Pydantic restriction)
  - `_links` → `links_` with `Field(alias="_links")`
  - Or use any other non-underscore-prefixed name

---

#### Special Case: Field Name Collision

**Problem:** `Deployment` model has a field named `payload` which collides with the constructor parameter.

**Before:**
```python
class Deployment(BaseGithubModel):
    payload: dict
    url: str
    id: int
    payload: Annotated[dict, "unstructured"]  # Collision!

    def __init__(self, payload: dict):
        self.payload = payload
        # ...
        self.payload = payload.get("payload")  # Overwrites itself!
```

**After:**
```python
class Deployment(BaseGithubModel):
    url: str
    id: int
    payload_data: dict[str, Any] = Field(alias="payload")  # Renamed to avoid collision
```

**Note:** GitHub sends a field literally named `"payload"` in deployment webhooks. We must rename it.

---

### Step 2.4: Complete Model Migration List

**Migration order strategy:** Migrate in dependency order - models with no dependencies first, then models that depend on them. The list below is organized by complexity for learning, but verify dependencies when actually migrating.

**Critical:** Before migrating a model, ensure all models it references are already migrated (e.g., migrate `User` before `Repository` since `Repository` has a `owner: User` field).

Migrate these models in order (simplest to most complex):

**Simple models (no template URLs, no nested objects):**
1. `CommitUser`
2. `ShortRepository`
3. `ShortInstallation`
4. `PackageVersionInfo`
5. `VulnerablePackage`
6. `SecurityVulnerabilityIdentifier`
7. `SecurityAdvisoryReference`

**Models with nested objects only:**
8. `Permissions`
9. `Enterprise`
10. `StatusBranchCommit`
11. `StatusNestedCommitUser`
12. `StatusCommitVerification`
13. `PurchaseAccount`
14. `Plan`

**Models with template URLs:**
15. `User` - 4 template URLs
16. `Organization` - 2 template URLs
17. `Repository` - 19 template URLs
18. `Issue` - 1 template URL
19. `Team` - 1 template URL
20. `PullRequest` - 1 template URL

**Models with unstructured dicts:**
21. `Comment` - has `_links`, `reactions`
22. `Hook` - has `config`
23. `PageBuild` - has `error`
24. `Review` - has `_links`
25. `ChecksPullRequest` - has `head`, `base`

**Complex models (multiple features):**
26. `Commit`
27. `CheckSuite`
28. `CheckRunOutput`
29. `CheckRun`
30. `Installation`
31. `DeployKey`
32. `Deployment` - **has field name collision!**
33. `DeploymentStatus`
34. `Page`
35. `Label`
36. `Milestone`
37. `MarketplacePurchase`
38. `Membership`
39. `Asset`
40. `Release`
41. `PackageFile`
42. `PackageVersion`
43. `Registry`
44. `Package`
45. `ProjectCard`
46. `ProjectColumn`
47. `Project`
48. `Ref`
49. `VulnerabilityAlert`
50. `Vulnerability`
51. `SecurityAdvisory`
52. `SponsorshipTier`
53. `Sponsorship`
54. `Branch`
55. `StatusNestedCommit`
56. `StatusCommit`
57. `Rule`
58. `ChecksApp`
59. `Thread`

---

## Phase 3: Migrate Event Classes (events.py)

### Step 3.1: Update Imports

**File:** `octohook/events.py` (top)

**Add:**
```python
from __future__ import annotations  # Enable forward references

from pydantic import BaseModel, ConfigDict, ValidationError
```

**Note:** `ValidationError` needed for updated `parse()` function

---

### Step 3.2: Update BaseWebhookEvent

**Before:**
```python
class BaseWebhookEvent:
    payload: dict
    action: Optional[str] = None
    sender: Optional[User]
    repository: Optional[Repository] = None
    organization: Optional[Organization] = None
    enterprise: Optional[Enterprise] = None

    def __init__(self, payload: dict):
        self.payload = payload
        self.action = payload.get("action")
        self.sender = _optional(payload, "sender", User)

        # Not present in GitHubAppAuthorizationEvent, InstallationEvent, SponsorshipEvent
        try:
            self.repository = Repository(payload.get("repository"))
        except AttributeError:
            pass

        # Only present in some events
        try:
            self.organization = Organization(payload.get("organization"))
        except AttributeError:
            pass

        self.enterprise = _optional(payload, "enterprise", Enterprise)
```

**After:**
```python
class BaseWebhookEvent(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
        strict=True,
        frozen=True,
        validate_assignment=False,
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

**Key changes:**
- ✅ Inherit from `BaseModel` instead of plain class
- ✅ Add same `model_config` as `BaseGithubModel`
- ✅ Remove `payload: dict`
- ✅ Remove `__init__` - Pydantic handles it
- ✅ Remove try/except - Pydantic handles None gracefully for Optional fields
- ✅ All Optional fields get `= None` default

---

### Step 3.3: Migrate Individual Event Classes

**Pattern for ALL event classes:**

**Before:**
```python
class PullRequestEvent(BaseWebhookEvent):
    number: int
    pull_request: PullRequest
    assignee: Optional[User]
    label: Optional[Label]
    changes: Optional[Annotated[dict, "unstructured"]]
    before: Optional[str]
    after: Optional[str]
    requested_reviewer: Optional[User]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.number = payload.get("number")
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.assignee = _optional(payload, "assignee", User)
        self.label = _optional(payload, "label", Label)
        self.changes = payload.get("changes")
        self.before = payload.get("before")
        self.after = payload.get("after")
        self.requested_reviewer = _optional(payload, "requested_reviewer", User)
```

**After:**
```python
class PullRequestEvent(BaseWebhookEvent):
    number: int
    pull_request: PullRequest
    assignee: Optional[User] = None
    label: Optional[Label] = None
    changes: Optional[dict[str, Any]] = None
    before: Optional[str] = None
    after: Optional[str] = None
    requested_reviewer: Optional[User] = None
```

**Pattern:**
1. ✅ Remove `__init__` entirely (including `super().__init__()`)
2. ✅ Keep all field definitions
3. ✅ Add `= None` to all Optional fields
4. ✅ Change `Annotated[dict, "unstructured"]` → `dict[str, Any]`
5. ✅ Keep docstrings

---

### Step 3.4: Complete Event Migration List

Migrate all event classes in `events.py`:

1. `BranchProtectionRuleEvent`
2. `CheckRunEvent`
3. `CheckSuiteEvent`
4. `CommitCommentEvent`
5. `CreateEvent`
6. `DeleteEvent`
7. `DeployKeyEvent`
8. `DeploymentEvent`
9. `DeploymentStatusEvent`
10. `ForkEvent`
11. `GitHubAppAuthorizationEvent`
12. `GollumEvent`
13. `InstallationEvent`
14. `InstallationRepositoriesEvent`
15. `IssueCommentEvent`
16. `IssuesEvent`
17. `LabelEvent`
18. `MarketplacePurchaseEvent`
19. `MemberEvent`
20. `MembershipEvent`
21. `MetaEvent`
22. `MilestoneEvent`
23. `OrganizationEvent`
24. `OrgBlockEvent`
25. `PackageEvent`
26. `PageBuildEvent`
27. `ProjectCardEvent`
28. `ProjectColumnEvent`
29. `ProjectEvent`
30. `PublicEvent`
31. `PullRequestEvent`
32. `PullRequestReviewEvent`
33. `PullRequestReviewCommentEvent`
34. `PullRequestReviewThreadEvent`
35. `PushEvent`
36. `ReleaseEvent`
37. `RepositoryDispatchEvent`
38. `RepositoryEvent`
39. `RepositoryImportEvent`
40. `RepositoryVulnerabilityAlertEvent`
41. `SecurityAdvisoryEvent` (Note: doesn't inherit from BaseWebhookEvent, needs special handling)
42. `SponsorshipEvent`
43. `StarEvent`
44. `StatusEvent`
45. `TeamEvent`
46. `TeamAddEvent`
47. `WatchEvent`
48. `PingEvent`

**Special case:** `SecurityAdvisoryEvent` doesn't inherit from `BaseWebhookEvent`. Apply same pattern but without the inheritance benefits.

---

## Phase 4: Update Parse Function

### Step 4.1: Update parse() Function

**File:** `octohook/events.py`

**Before:**
```python
def parse(event_name, payload: dict):
    try:
        return event_map[WebhookEvent(event_name)](payload)
    except Exception:
        logger.exception(f"Could not parse event {event_name}")
        return BaseWebhookEvent(payload)
```

**After:**
```python
def parse(event_name, payload: dict):
    try:
        event_class = event_map[WebhookEvent(event_name)]
        return event_class.model_validate(payload)
    except (KeyError, ValidationError) as e:
        logger.exception(f"Could not parse event {event_name}: {e}")
        return BaseWebhookEvent.model_validate(payload)
```

**Note:** `ValidationError` was already added in Step 3.1

**Key changes:**
- ✅ Use `model_validate()` instead of direct instantiation `()`
- ✅ Catch specific exceptions: `KeyError` (unknown event), `ValidationError` (bad data)
- ✅ More informative logging (include exception in message)

---

## Phase 5: Update Tests

### Step 5.1: Update test_models.py

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

---

#### Change 2: Replace check_model() Function

**Remove:**
```python
def check_model(data, obj):
    """
    Checks if every key in the json is represented either as an
    Annotated[dict, "unstructured"] or a nested object.
    ...
    """
    # ... entire function
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

**Key changes from old `check_model()`:**
- Only checks Pydantic models (isinstance check at start)
- Uses `__pydantic_extra__` instead of manual dict inspection
- Uses `obj.model_fields` instead of parsing type hints
- Simpler and more reliable - lets Pydantic do the work

---

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

---

#### Change 4: Remove Utility Functions

**Remove entirely:**
- `_unwrap_annotated()`
- `_is_unstructured_dict()`
- `_is_primitive_type()`

These are no longer needed - Pydantic handles type validation.

---

#### Change 5: Remove Type Hint Validation

**Remove entirely:**
- `_validate_simple_type()`
- `_validate_list_items()`
- `_validate_complex_type()`
- `check_type_hints()`
- `test_all_type_hints_are_correct()`

**Rationale:** Pydantic V2's strict mode provides more thorough type validation than our custom checker.

---

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

---

### Step 5.2: Update conftest.py (if needed)

**File:** `tests/conftest.py`

Review the file for:
- Any direct model instantiation (change to `model_validate()`)
- Any fixtures that might need updating
- The autouse fixture should still work (calls `reset()` which clears handlers)

**Most likely:** No changes needed, but verify after migration.

---

## Phase 6: Update Decorators (if needed)

### Step 6.1: Review decorators.py

**File:** `octohook/decorators.py`

**Analysis:** The decorator system calls `parse()`, which we've updated to use `model_validate()`. The wrapper function should work transparently.

**Expected result:** No changes needed.

**Verification:** Run decorator tests after migration.

---

## Phase 7: Final Cleanup & Verification

### Step 7.1: Remove Unused Imports

**File:** `octohook/models.py`

**Remove:**
```python
from abc import ABC
from typing import TypeVar, Type

T = TypeVar("T")
```

**File:** `octohook/events.py`

**Remove:**
```python
from octohook.models import _optional
```

---

### Step 7.2: Verify Exports

**File:** `octohook/__init__.py`

**Check:** Exports should remain the same:
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

**Expected result:** No changes needed.

---

### Step 7.3: Run Full Test Suite

```bash
uv run pytest -v
```

**Expected results:**
- ✅ All existing tests pass
- ✅ Type hints validated by Pydantic
- ✅ Extra fields caught by `__pydantic_extra__` check
- ✅ URL template methods work correctly

**If tests fail:**
1. Check error messages for missing fields
2. Verify Field aliases are correct
3. Check Optional fields have `= None`
4. Verify nested model types are correct

---

### Step 7.4: Run Coverage Report

```bash
uv run pytest --cov=octohook --cov-report=term-missing
```

**Expected:** Coverage should remain similar or improve (fewer lines of code to cover).

---

### Step 7.5: Add Type Checking (Optional)

**File:** `pyproject.toml`

**Add to dev dependencies:**
```toml
[dependency-groups]
dev = [
    "pre-commit>=4.1.0",
    "pytest>=8.3.4",
    "pytest-mock>=3.14.0",
    "pytest-cov>=6.0.0",
    "mypy>=1.0.0",
]
```

**Create mypy config:**
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

**Run:**
```bash
uv sync
uv run mypy octohook
```

---

## Success Criteria

Migration is complete when:

- ✅ All 59 model classes converted to Pydantic
- ✅ All 48 event classes converted to Pydantic
- ✅ `parse()` function uses `model_validate()`
- ✅ Tests updated to check `__pydantic_extra__`
- ✅ All tests pass: `uv run pytest -v`
- ✅ Coverage maintained or improved
- ✅ No `__init__` methods in models/events
- ✅ No `payload` fields in models/events
- ✅ URL template methods work correctly
- ✅ Type hints validated by Pydantic
- ✅ Code reduced by ~60%

---

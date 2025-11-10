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
- **Breaking Changes:** None (public API preserved)

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
        validate_assignment=False,    # N/A since frozen=True
        str_strip_whitespace=False,   # Preserve exact GitHub data
        use_enum_values=False,        # Keep enum instances for type safety
        validate_default=False,       # Trust our defaults
        revalidate_instances='never', # Trust already-validated nested models
        protected_namespaces=('model_',), # Prevent conflicts with Pydantic internals
    )
```

**Verification:** Import should work without errors

---

## Phase 2: Migrate Model Classes (models.py)

### Step 2.1: Update Imports at Top of File

**File:** `octohook/models.py` (top)

**Add:**
```python
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field
```

**Remove:**
```python
from abc import ABC
from typing import TypeVar, Type

T = TypeVar("T")
```

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
    - Stops at first None value
    """
    local_variables.pop("self", None)

    for key, value in local_variables.items():
        # Convert value to string if needed (handles int, etc.)
        if value is None or value == "":
            url = url.split(f"{{/{key}}}")[0]
            break

        value_str = str(value) if not isinstance(value, str) else value

        if f"{{{key}}}" in url:
            url = url.replace(f"{{{key}}}", value_str)
        elif f"{{/{key}}}" in url:
            url = url.replace(f"{{/{key}}}", f"/{value_str}")

    return url
```

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
- ✅ Keep `__str__`, `__repr__`, `__eq__` and other methods

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
- ✅ Lists with defaults: `List[str] = []`
- ✅ Lists of models: `List[User]` - Pydantic auto-validates each item
- ✅ No manual instantiation needed (`User(...)` or `_optional(...)`)

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

Migrate these models in order (simplest to most complex):

**Simple models (no template URLs, no nested objects):**
1. `CommitUser` (lines 597-608)
2. `ShortRepository` (lines 140-158)
3. `ShortInstallation` (lines 738-747)
4. `PackageVersionInfo` (lines 1643-1650)
5. `VulnerablePackage` (lines 1632-1641)
6. `SecurityVulnerabilityIdentifier` (lines 1669-1678)
7. `SecurityAdvisoryReference` (lines 1680-1687)

**Models with nested objects only:**
8. `Permissions` (lines 160-209)
9. `Enterprise` (lines 54-82)
10. `StatusBranchCommit` (lines 1762-1773)
11. `StatusNestedCommitUser` (lines 1803-1814)
12. `StatusCommitVerification` (lines 1788-1801)
13. `PurchaseAccount` (lines 1017-1030)
14. `Plan` (lines 1032-1057)

**Models with template URLs:**
15. `User` (lines 84-138) - 4 template URLs
16. `Organization` (lines 440-476) - 2 template URLs
17. `Repository` (lines 211-437) - 19 template URLs
18. `Issue` (lines 963-1016) - 1 template URL
19. `Team` (lines 1080-1108) - 1 template URL
20. `PullRequest` (lines 1475-1582) - 1 template URL

**Models with unstructured dicts:**
21. `Comment` (lines 478-538) - has `_links`, `reactions`
22. `Hook` (lines 1110-1131) - has `config`
23. `PageBuild` (lines 1344-1365) - has `error`
24. `Review` (lines 1584-1611) - has `_links`
25. `ChecksPullRequest` (lines 580-595) - has `head`, `base`

**Complex models (multiple features):**
26. `Commit` (lines 610-637)
27. `CheckSuite` (lines 639-678)
28. `CheckRunOutput` (lines 680-695)
29. `CheckRun` (lines 697-736)
30. `Installation` (lines 749-784)
31. `DeployKey` (lines 786-805)
32. `Deployment` (lines 807-842) - **has field name collision!**
33. `DeploymentStatus` (lines 844-873)
34. `Page` (lines 875-892)
35. `Label` (lines 894-922)
36. `Milestone` (lines 924-961)
37. `MarketplacePurchase` (lines 1059-1078)
38. `Membership` (lines 1133-1148)
39. `Asset` (lines 1150-1181)
40. `Release` (lines 1183-1224)
41. `PackageFile` (lines 1226-1253)
42. `PackageVersion` (lines 1255-1300)
43. `Registry` (lines 1302-1317)
44. `Package` (lines 1319-1342)
45. `ProjectCard` (lines 1367-1398)
46. `ProjectColumn` (lines 1400-1423)
47. `Project` (lines 1425-1456)
48. `Ref` (lines 1458-1473)
49. `VulnerabilityAlert` (lines 1613-1630)
50. `Vulnerability` (lines 1652-1667)
51. `SecurityAdvisory` (lines 1689-1722)
52. `SponsorshipTier` (lines 1724-1741)
53. `Sponsorship` (lines 1743-1760)
54. `Branch` (lines 1775-1786)
55. `StatusNestedCommit` (lines 1816-1835)
56. `StatusCommit` (lines 1837-1860)
57. `Rule` (lines 1861-1946)
58. `ChecksApp` (lines 551-578)
59. `Thread` (lines 540-549)

---

## Phase 3: Migrate Event Classes (events.py)

### Step 3.1: Update Imports

**File:** `octohook/events.py` (top)

**Add:**
```python
from pydantic import BaseModel, ConfigDict
```

---

### Step 3.2: Update BaseWebhookEvent

**Before (lines 49-75):**
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

Migrate all event classes (lines 77-785 in events.py):

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

**Special case:** `SecurityAdvisoryEvent` (lines 663-676) doesn't inherit from `BaseWebhookEvent`. Apply same pattern but without the inheritance benefits.

---

## Phase 4: Update Parse Function

### Step 4.1: Update parse() Function

**File:** `octohook/events.py` (lines 986-992)

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
from pydantic import ValidationError

def parse(event_name, payload: dict):
    try:
        event_class = event_map[WebhookEvent(event_name)]
        return event_class.model_validate(payload)
    except (KeyError, ValidationError) as e:
        logger.exception(f"Could not parse event {event_name}: {e}")
        return BaseWebhookEvent.model_validate(payload)
```

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

**Remove (lines 33-86):**
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
    from octohook.models import BaseGithubModel

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

---

#### Change 3: Update test_model_has_all_keys_in_json

**Before (lines 88-99):**
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

**Remove entirely (lines 126-206):**
- `_unwrap_annotated()` (lines 126-158)
- `_is_unstructured_dict()` (lines 160-189)
- `_is_primitive_type()` (lines 191-206)

These are no longer needed - Pydantic handles type validation.

---

#### Change 5: Remove Type Hint Validation

**Remove entirely (lines 208-342):**
- `_validate_simple_type()` (lines 208-238)
- `_validate_list_items()` (lines 240-265)
- `_validate_complex_type()` (lines 267-295)
- `check_type_hints()` (lines 297-328)
- `test_all_type_hints_are_correct()` (lines 330-342)

**Rationale:** Pydantic V2's strict mode provides more thorough type validation than our custom checker.

---

#### Change 6: Remove Unannotated Dict Test

**Remove entirely (lines 358-384):**
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

## Migration Checklist

### Pre-Migration
- [ ] Read and understand entire plan
- [ ] Create backup branch
- [ ] Ensure all tests pass on current code

### Phase 1: Setup
- [ ] Add pydantic>=2.0.0 to pyproject.toml
- [ ] Run `uv lock && uv sync`
- [ ] Update BaseGithubModel with ConfigDict
- [ ] Verify imports work

### Phase 2: Models (octohook/models.py)
- [ ] Update imports (add pydantic, remove ABC)
- [ ] Remove `_optional()` helper
- [ ] Update `_transform()` for robustness
- [ ] Migrate simple models (7 models)
- [ ] Migrate models with nested objects (7 models)
- [ ] Migrate models with template URLs (6 models)
- [ ] Migrate models with unstructured dicts (5 models)
- [ ] Migrate complex models (34 models)
- [ ] Verify all 59 models migrated
- [ ] Run tests: `uv run pytest tests/test_models.py -v`

### Phase 3: Events (octohook/events.py)
- [ ] Update imports (add pydantic)
- [ ] Update BaseWebhookEvent to inherit BaseModel
- [ ] Remove BaseWebhookEvent.__init__
- [ ] Migrate all 48 event classes
- [ ] Update parse() to use model_validate()
- [ ] Run tests: `uv run pytest tests/ -v -k event`

### Phase 4: Tests (tests/test_models.py)
- [ ] Update imports
- [ ] Replace check_model() with check_no_extra_fields()
- [ ] Update test_model_has_all_keys_in_json
- [ ] Remove utility functions (_unwrap_annotated, etc.)
- [ ] Remove check_type_hints and related code
- [ ] Remove test_unannotated_dict_enforcement
- [ ] Run full test suite: `uv run pytest -v`

### Phase 5: Cleanup
- [ ] Remove unused imports from models.py
- [ ] Remove unused imports from events.py
- [ ] Verify __init__.py exports
- [ ] Run final test suite: `uv run pytest -v`
- [ ] Run coverage: `uv run pytest --cov=octohook`
- [ ] (Optional) Add mypy and run type checking

### Post-Migration
- [ ] Review all changes
- [ ] Update CHANGELOG (if applicable)
- [ ] Commit with clear message
- [ ] Create PR with migration summary

---

## Estimated Effort

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Setup | 30 minutes |
| Phase 2: Models (59 classes) | 10 hours |
| Phase 3: Events (48 classes) | 3.5 hours |
| Phase 4: Tests | 2 hours |
| Phase 5: Cleanup & Verification | 2 hours |
| **Total** | **~18 hours** |

**Breakdown by complexity:**
- Simple models (5-10 min each): 7 × 7 min = ~50 min
- Nested models (10-15 min each): 7 × 12 min = ~85 min
- Template URL models (20-30 min each): 6 × 25 min = ~150 min
- Unstructured dict models (10-15 min each): 5 × 12 min = ~60 min
- Complex models (15-25 min each): 34 × 20 min = ~680 min
- Event classes (5 min each): 48 × 5 min = ~240 min

---

## Risk Mitigation Strategies

1. **Incremental Migration**
   - Start with simplest models
   - Build confidence with patterns
   - Test frequently

2. **Test-Driven Approach**
   - Run tests after each model
   - Fix issues immediately
   - Don't accumulate errors

3. **Version Control**
   - Small, atomic commits
   - Clear commit messages
   - Easy to revert if needed

4. **Pattern Consistency**
   - Follow examples exactly
   - Document deviations
   - Review before moving on

5. **Validation Checkpoints**
   - After Phase 2: `pytest tests/test_models.py`
   - After Phase 3: `pytest tests/test_decorator.py`
   - After Phase 4: `pytest tests/`
   - After Phase 5: `pytest --cov`

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting `= None` for Optional Fields
**Error:** `ValidationError: field required`
**Solution:** All `Optional[X]` fields need `= None` default

### Pitfall 2: Wrong Field Alias
**Error:** Extra fields in `__pydantic_extra__`
**Solution:** Check JSON key name matches `Field(alias="...")`

### Pitfall 3: Forgetting to Update Method Bodies
**Error:** `KeyError: 'following_url'` in template methods
**Solution:** Update `self.payload["x"]` to `self.x_template`

### Pitfall 4: Fields Starting with Underscore
**Error:** `ValueError: "_links" is not a valid field name`
**Solution:** Rename to `links_` with `Field(alias="_links")`

### Pitfall 5: List Defaults
**Error:** Mutable default argument warning
**Solution:** Use `List[str] = []` - Pydantic handles this safely

### Pitfall 6: Nested Model Validation
**Error:** `ValidationError: value is not a valid dict`
**Solution:** Ensure nested data is dict, not None (or use Optional)

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

## Post-Migration Opportunities

After successful migration, consider:

1. **JSON Schema Export**
   ```python
   from octohook.models import User
   schema = User.model_json_schema()
   ```

2. **Serialization Improvements**
   ```python
   user.model_dump()  # Dict
   user.model_dump_json()  # JSON string
   ```

3. **Validation Utilities**
   ```python
   try:
       event = PullRequestEvent.model_validate(payload)
   except ValidationError as e:
       print(e.json())  # Detailed error info
   ```

4. **Documentation Generation**
   - Auto-generate API docs from Pydantic schemas
   - Field descriptions via `Field(description="...")`

5. **Performance Monitoring**
   - Pydantic V2 is faster than manual parsing
   - Consider benchmarking before/after

---

## Rollback Plan

If critical issues arise:

1. **Identify the issue**
   - Check error messages
   - Review recent commits
   - Isolate failing tests

2. **Attempt fix**
   - Review pattern examples
   - Check for typos in aliases
   - Verify Optional fields have defaults

3. **If unfixable, rollback**
   ```bash
   git reset --hard HEAD~1  # Last commit
   # or
   git revert <commit-hash>  # Specific commit
   ```

4. **Document issue**
   - What went wrong
   - Why it happened
   - How to prevent next time

---

## Questions & Support

For issues during migration:

1. Review relevant section of this plan
2. Check pattern examples
3. Review Pydantic V2 docs: https://docs.pydantic.dev/latest/
4. Check test failures for clues
5. Document and report blockers

---

**Document Version:** 1.0
**Created:** 2025-11-10
**Author:** Claude (Anthropic)
**Status:** Ready for Implementation

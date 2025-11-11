# PR #4: Migrate Event Classes

## Scope

Migrate all 48 event classes in `octohook/events.py` to use Pydantic models instead of manual initialization.

## Files Changed

- `octohook/events.py` - Migrate 48 event classes

## Detailed Changes

### Migration Pattern

For **ALL** event classes, apply this transformation:

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

**Transformation steps:**
1. ✅ Remove `__init__` entirely (including `super().__init__()`)
2. ✅ Keep all field definitions
3. ✅ Add `= None` to all `Optional` fields
4. ✅ Change `Annotated[dict, "unstructured"]` → `dict[str, Any]`
5. ✅ Keep docstrings if present

### Event Classes to Migrate (48 total)

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
41. `SecurityAdvisoryEvent` ⚠️ **Special case**
42. `SponsorshipEvent`
43. `StarEvent`
44. `StatusEvent`
45. `TeamEvent`
46. `TeamAddEvent`
47. `WatchEvent`
48. `PingEvent`

### Special Case: SecurityAdvisoryEvent

**Note:** `SecurityAdvisoryEvent` does NOT inherit from `BaseWebhookEvent` (it's a standalone Pydantic model).

**Before:**
```python
class SecurityAdvisoryEvent:
    payload: dict
    action: str
    security_advisory: SecurityAdvisory

    def __init__(self, payload: dict):
        self.payload = payload
        self.action = payload.get("action")
        self.security_advisory = SecurityAdvisory(payload.get("security_advisory"))
```

**After:**
```python
from pydantic import BaseModel, ConfigDict

class SecurityAdvisoryEvent(BaseModel):
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

    action: str
    security_advisory: SecurityAdvisory
```

### Example: Simple Event

**Before:**
```python
class CreateEvent(BaseWebhookEvent):
    ref: str
    ref_type: str
    master_branch: str
    description: Optional[str]
    pusher_type: str

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.ref = payload.get("ref")
        self.ref_type = payload.get("ref_type")
        self.master_branch = payload.get("master_branch")
        self.description = payload.get("description")
        self.pusher_type = payload.get("pusher_type")
```

**After:**
```python
class CreateEvent(BaseWebhookEvent):
    ref: str
    ref_type: str
    master_branch: str
    description: Optional[str] = None
    pusher_type: str
```

### Example: Event with Nested Models

**Before:**
```python
class IssuesEvent(BaseWebhookEvent):
    issue: Issue
    assignee: Optional[User]
    label: Optional[Label]
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.assignee = _optional(payload, "assignee", User)
        self.label = _optional(payload, "label", Label)
        self.changes = payload.get("changes")
```

**After:**
```python
class IssuesEvent(BaseWebhookEvent):
    issue: Issue  # Pydantic auto-validates
    assignee: Optional[User] = None
    label: Optional[Label] = None
    changes: Optional[dict[str, Any]] = None
```

### Example: Event with Lists

**Before:**
```python
class GollumEvent(BaseWebhookEvent):
    pages: List[Page]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.pages = [Page(page) for page in payload.get("pages", [])]
```

**After:**
```python
class GollumEvent(BaseWebhookEvent):
    pages: List[Page] = []  # Pydantic validates each Page
```

## Dependencies

**Requires:**
- PR #1 (BaseWebhookEvent)
- PR #2 (simple models)
- PR #3 (complex models)

**Blocks:** PR #5 (parse function needs migrated events)

**Critical:** All model classes must be migrated before event classes, since events reference models.

## Testing Strategy

```bash
# Run full test suite
uv run pytest -v

# Test event parsing specifically
uv run pytest tests/test_models.py::test_model_has_all_keys_in_json -v

# Test event instantiation
uv run python -c "
from octohook.events import PullRequestEvent
event = PullRequestEvent.model_validate({
    'action': 'opened',
    'number': 123,
    'pull_request': {
        'id': 1,
        'number': 123,
        'state': 'open',
        'title': 'Test PR',
        # ... other required fields
    },
    # ... other fields
})
print(f'Event action: {event.action}')
print(f'PR number: {event.number}')
"

# Test SecurityAdvisoryEvent (special case)
uv run python -c "
from octohook.events import SecurityAdvisoryEvent
event = SecurityAdvisoryEvent.model_validate({
    'action': 'published',
    'security_advisory': {
        'ghsa_id': 'GHSA-xxxx-xxxx-xxxx',
        'summary': 'Test advisory',
        # ... other required fields
    }
})
print(f'Advisory action: {event.action}')
"

# Verify BaseWebhookEvent fields inherited correctly
uv run python -c "
from octohook.events import IssuesEvent
event = IssuesEvent.model_validate({
    'action': 'opened',
    'issue': {...},  # Required issue data
    'sender': {...},  # BaseWebhookEvent field
    'repository': {...},  # BaseWebhookEvent field
})
print(f'Has sender: {event.sender is not None}')
print(f'Has repository: {event.repository is not None}')
"
```

**Expected outcomes:**
- ✅ All 48 events can be instantiated via `model_validate()`
- ✅ Nested models (User, Label, Issue, etc.) are auto-validated
- ✅ Optional fields handle None gracefully
- ✅ List fields auto-validate each item
- ✅ BaseWebhookEvent fields (sender, repository, etc.) inherited correctly
- ✅ SecurityAdvisoryEvent works as standalone model
- ✅ All tests pass

## Risk Level

**Low**

- Straightforward pattern (simpler than models with template URLs)
- All dependencies (models) are already migrated
- BaseWebhookEvent provides consistent foundation
- Well-tested webhook fixtures catch issues

## Rationale

**Why all 48 events together:**
- Events are simpler than models (no template URLs, fewer special cases)
- Consistent pattern across all events (remove __init__, add defaults)
- Logical unit: "all event parsing" in one PR
- Events depend on models, so must come after PR #2 and #3

**Why after model PRs:**
- Events reference models (User, Issue, PullRequest, etc.)
- Must wait for all models to be migrated
- Clean dependency chain: base → models → events

**Why before parse function:**
- Parse function instantiates events
- Better to have events migrated before changing parse logic
- Allows testing events with old parse, then update parse separately

## Lines Changed (Est)

~300-400 lines

**Breakdown:**
- Remove ~600 lines (48 __init__ methods)
- Add ~200 lines (defaults for Optional fields)
- Net reduction: ~400 lines removed

## Rollback Instructions

**If this PR must be reverted:**

1. Revert the commit:
```bash
git revert <commit-hash>
```

2. **Note:** If PR #5 is already merged, it should be reverted first.

3. Verify rollback:
```bash
uv run pytest tests/ -v
```

4. Check event instantiation:
```bash
# Ensure old pattern works
uv run python -c "from octohook.events import PullRequestEvent; print('Import OK')"
```

## Additional Notes

**Critical reminders:**

- **super().__init__(payload)** must be removed - Pydantic handles parent initialization
- **All Optional fields need = None** - even though inherited fields from BaseWebhookEvent have defaults
- **Nested models are automatic** - no `User(...)` or `_optional(...)` needed
- **List comprehensions go away** - `[Page(p) for p in ...]` becomes just `List[Page]`
- **SecurityAdvisoryEvent is special** - needs full `model_config` since it doesn't inherit from BaseWebhookEvent

**Event inheritance:**
All events (except SecurityAdvisoryEvent) inherit these fields from BaseWebhookEvent:
- `action: Optional[str] = None`
- `sender: Optional[User] = None`
- `repository: Optional[Repository] = None`
- `organization: Optional[Organization] = None`
- `enterprise: Optional[Enterprise] = None`

**Events with unstructured dicts:**
Several events have `changes` field:
- `IssuesEvent`
- `PullRequestEvent`
- `MilestoneEvent`
- Others

Change `Optional[Annotated[dict, "unstructured"]]` to `Optional[dict[str, Any]] = None`

**Post-merge checklist:**
- ✅ 48 event classes migrated
- ✅ No __init__ methods remain
- ✅ No super().__init__() calls remain
- ✅ All Optional fields have `= None`
- ✅ All Annotated[dict, "unstructured"] changed to dict[str, Any]
- ✅ SecurityAdvisoryEvent has model_config
- ✅ Tests pass
- ✅ All webhook fixtures parse correctly

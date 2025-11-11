# PR #2: Migrate Model Classes (Part 1 - Simple & Nested)

## Scope

Migrate 30 simpler model classes in `octohook/models.py` - those without template URLs or minimal complexity.

## Files Changed

- `octohook/models.py` - Migrate 30 model classes

## Detailed Changes

### Migration Pattern

For each model, apply these transformations:

1. **Remove `payload: dict` field**
2. **Remove `__init__` method entirely**
3. **Add `= None` defaults for all `Optional` fields**
4. **For nested models:** Just use type hint (e.g., `owner: User`) - Pydantic handles instantiation
5. **For lists:** Use `List[ModelType]` - Pydantic validates each item
6. **For lists with defaults:** Use `List[str] = []` or `List[Model] = []`
7. **Keep custom methods:** `__str__`, `__repr__`, `__eq__`, `__hash__` (only Label has custom __eq__ and __repr__)

### Models to Migrate (30 models)

**Simple models (no nested objects, no template URLs):**

1. `CommitUser`
2. `Permissions`
3. `Enterprise`
4. `ShortRepository`
5. `ShortInstallation`
6. `PackageVersionInfo`
7. `VulnerablePackage`
8. `SecurityVulnerabilityIdentifier`
9. `SecurityAdvisoryReference`

**Models with nested objects only:**

10. `StatusBranchCommit`
11. `StatusNestedCommitUser`
12. `StatusCommitVerification`
13. `PurchaseAccount`
14. `Plan`
15. `Commit`
16. `CheckSuite`
17. `CheckRunOutput`
18. `CheckRun`
19. `DeployKey`
20. `Page`
21. `Milestone`
22. `MarketplacePurchase`
23. `Membership`
24. `Asset`
25. `ProjectCard`
26. `ProjectColumn`
27. `Project`
28. `Ref`
29. `StatusNestedCommit`
30. `StatusCommit`

### Example: Simple Model

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

### Example: Model with Nested Objects

**Before:**
```python
class Commit(BaseGithubModel):
    payload: dict
    sha: str
    author: CommitUser
    committer: CommitUser
    message: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.sha = payload.get("sha")
        self.author = CommitUser(payload.get("author"))
        self.committer = CommitUser(payload.get("committer"))
        self.message = payload.get("message")
```

**After:**
```python
class Commit(BaseGithubModel):
    sha: str
    author: CommitUser  # Pydantic auto-validates
    committer: CommitUser  # Pydantic auto-validates
    message: str
```

### Example: Model with Optional Nested and Lists

**Before:**
```python
class CheckSuite(BaseGithubModel):
    payload: dict
    id: int
    head_branch: Optional[str]
    repository: Repository
    pull_requests: List[ChecksPullRequest]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.head_branch = payload.get("head_branch")
        self.repository = Repository(payload.get("repository"))
        self.pull_requests = [ChecksPullRequest(pr) for pr in payload.get("pull_requests", [])]
```

**After:**
```python
class CheckSuite(BaseGithubModel):
    id: int
    head_branch: Optional[str] = None
    repository: Repository  # Auto-validates
    pull_requests: List[ChecksPullRequest] = []  # Auto-validates each item
```

### Special Cases

**Models with list comprehensions:**
- `StatusCommit.parents`: `[StatusBranchCommit(parent) for parent in ...]` → `List[StatusBranchCommit]`

**Models with `or []` pattern:**
- Change `payload.get("topics") or []` pattern to just `List[str] = []` in field definition

## Dependencies

**Requires:** PR #1 (base classes)

**Blocks:** PR #4 (events depend on models)

**Coordination note:** Some models in this PR are referenced by models in PR #3. Migration order within this file matters:
- Migrate dependency-free models first
- Then models that reference them
- E.g., `CommitUser` before `Commit` (since Commit references CommitUser)

## Testing Strategy

```bash
# Run full test suite
uv run pytest -v

# Check specific model tests
uv run pytest tests/test_models.py -v

# Verify imports work
uv run python -c "from octohook.models import Enterprise, Commit, CheckSuite; print('OK')"

# Test instantiation with Pydantic
uv run python -c "
from octohook.models import Enterprise
e = Enterprise.model_validate({'id': 1, 'slug': 'test', 'name': 'Test', 'node_id': 'x', 'avatar_url': 'url', 'html_url': 'url', 'created_at': '2020-01-01', 'updated_at': '2020-01-01'})
print(f'Enterprise: {e.name}')
"
```

**Expected outcomes:**
- ✅ All migrated models can be instantiated via `model_validate()`
- ✅ Nested models are automatically validated
- ✅ Optional fields handle None gracefully
- ✅ List fields with defaults work correctly
- ✅ Custom __str__ methods still work

## Risk Level

**Low**

- Well-established patterns from PR #1
- Simple transformations (remove __init__, add defaults)
- Pydantic handles complexity automatically
- No template URLs or special cases in this batch

## Rationale

**Why these 30 models:**
- Grouped by similarity: simple models and models with nested objects
- No template URLs (those are more complex, saved for PR #3)
- Establishes migration patterns for team
- Gets bulk of "easy" models done quickly

**Why this before PR #3:**
- Many models in PR #3 depend on models in this PR
- E.g., `User`, `Repository`, `Issue` (PR #3) all reference models from this PR
- Sequential execution prevents dependency issues

**Why separate from PR #3:**
- Keeps PR reviewable (30 models vs 29 models)
- Allows parallel review if needed (reviewer can start on this while PR #1 is being finalized)
- Different complexity levels (simple vs template URLs)

## Lines Changed (Est)

~400-500 lines

**Breakdown:**
- Remove ~600 lines (30 __init__ methods, payload fields)
- Add ~100 lines (defaults for Optional fields)
- Net reduction: ~500 lines removed

## Rollback Instructions

**If this PR must be reverted:**

1. Revert the commit:
```bash
git revert <commit-hash>
```

2. Verify rollback:
```bash
uv run pytest tests/ -v
```

3. **Note:** If PR #3 or #4 is already merged, they may need to be reverted first (reverse order).

4. Check for breakage:
- Models will revert to old __init__ pattern
- Any code using `model_validate()` on these models will break (should be minimal at this stage)

## Additional Notes

**Critical reminders:**

- **Don't remove custom methods:** Only `Label` class has custom `__eq__` and `__repr__` - preserve these!
- **List defaults are safe:** Pydantic V2 handles mutable defaults correctly (doesn't share instances)
- **Nested validation is automatic:** Don't manually instantiate nested models (e.g., `User(...)`)
- **Optional always needs = None:** Even with Pydantic, be explicit about Optional defaults

**Model dependency order within this PR:**

Migrate in this sequence to avoid forward references:
1. Leaf models (no dependencies): CommitUser, Permissions, Enterprise, etc.
2. Models with dependencies: Commit (needs CommitUser), CheckSuite (needs Repository), etc.

**Post-merge checklist:**
- ✅ 30 models migrated
- ✅ No __init__ methods remain in these models
- ✅ No `payload` fields remain
- ✅ All Optional fields have `= None`
- ✅ Nested models use type hints only
- ✅ Lists use type hints with defaults
- ✅ Tests pass

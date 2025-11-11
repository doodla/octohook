# PR #3: Migrate Model Classes (Part 2 - Template URLs & Complex)

## Scope

Migrate remaining 29 model classes in `octohook/models.py` - those with template URLs, unstructured dicts, and special cases.

## Files Changed

- `octohook/models.py` - Migrate 29 remaining model classes

## Detailed Changes

### Migration Patterns

This PR handles three complex patterns:

#### Pattern 1: Template URLs

**Before:**
```python
class User(BaseGithubModel):
    payload: dict
    login: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.login = payload.get("login")

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.payload["following_url"], locals())
```

**After:**
```python
class User(BaseGithubModel):
    login: str
    following_url_template: str = Field(alias="following_url")

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.following_url_template, locals())
```

**Key changes:**
1. Field name: `{method_name}_template`
2. Add alias: `Field(alias="{original_name}")`
3. Update method to use `self.{field_name}_template`
4. Keep method signature unchanged

#### Pattern 2: Unstructured Dicts

**Before:**
```python
class Comment(BaseGithubModel):
    payload: dict
    reactions: Optional[Annotated[dict, "unstructured"]]
    _links: Optional[Annotated[dict, "unstructured"]]
```

**After:**
```python
class Comment(BaseGithubModel):
    reactions: Optional[dict[str, Any]] = None
    links_: Optional[dict[str, Any]] = Field(None, alias="_links")
```

**Key changes:**
1. `Annotated[dict, "unstructured"]` → `dict[str, Any]`
2. Fields starting with `_` must be renamed: `_links` → `links_` with `Field(alias="_links")`

#### Pattern 3: Field Name Collision (Deployment only)

**Before:**
```python
class Deployment(BaseGithubModel):
    payload: dict
    payload: Annotated[dict, "unstructured"]  # Collision!
```

**After:**
```python
class Deployment(BaseGithubModel):
    payload_data: dict[str, Any] = Field(alias="payload")
```

### Models to Migrate (29 models)

**Models with template URLs (6 models):**

1. **User** - 4 template URLs: following_url, gists_url, starred_url, subscriptions_url
2. **Organization** - 2 template URLs: repos_url, issues_url
3. **Repository** - 19 template URLs (most complex!)
4. **Issue** - 1 template URL: labels_url
5. **Team** - 1 template URL: repositories_url
6. **PullRequest** - 1 template URL: review_comments_url

**Models with unstructured dicts (5 models):**

7. **Comment** - `_links`, `reactions`
8. **Hook** - `config`
9. **PageBuild** - `error`
10. **Review** - `_links`
11. **ChecksPullRequest** - `head`, `base`

**Complex models with multiple features (17 models):**

12. **Installation** - nested objects, lists
13. **Label** - **SPECIAL: Has custom __eq__ and __repr__ - MUST preserve!**
14. **Thread** - list comprehension: `comments`
15. **Issue** - list comprehensions: `labels`, `assignees`
16. **Release** - list comprehension: `assets`
17. **PullRequest** - list comprehensions: `assignees`, `labels`
18. **Deployment** - **SPECIAL: Field name collision! (payload)**
19. **DeploymentStatus**
20. **VulnerabilityAlert**
21. **Vulnerability**
22. **SecurityAdvisory**
23. **PackageFile**
24. **PackageVersion**
25. **Registry**
26. **Package**
27. **SponsorshipTier**
28. **Sponsorship**
29. **Branch**
30. **Rule**
31. **ChecksApp**

**Note:** Count is actually 31 models (adjusted from original estimate).

### Example: User with Template URLs

**Before:**
```python
class User(BaseGithubModel):
    payload: dict
    login: str
    id: int
    # ... other fields

    def __init__(self, payload: dict):
        self.payload = payload
        self.login = payload.get("login")
        self.id = payload.get("id")
        # ...

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.payload["following_url"], locals())

    def gists_url(self, gist_id: str = None) -> str:
        return _transform(self.payload["gists_url"], locals())

    def starred_url(self, owner: str = None, repo: str = None) -> str:
        return _transform(self.payload["starred_url"], locals())

    def subscriptions_url(self) -> str:
        return self.payload["subscriptions_url"]
```

**After:**
```python
class User(BaseGithubModel):
    login: str
    id: int
    # ... other fields

    # Template URL fields
    following_url_template: str = Field(alias="following_url")
    gists_url_template: str = Field(alias="gists_url")
    starred_url_template: str = Field(alias="starred_url")
    subscriptions_url_template: str = Field(alias="subscriptions_url")

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.following_url_template, locals())

    def gists_url(self, gist_id: str = None) -> str:
        return _transform(self.gists_url_template, locals())

    def starred_url(self, owner: str = None, repo: str = None) -> str:
        return _transform(self.starred_url_template, locals())

    def subscriptions_url(self) -> str:
        return self.subscriptions_url_template
```

### Example: Comment with Unstructured Dicts

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
from typing import Any

class Comment(BaseGithubModel):
    id: int
    body: str
    reactions: Optional[dict[str, Any]] = None
    links_: Optional[dict[str, Any]] = Field(None, alias="_links")
```

### Example: Issue with List Comprehensions

**Before:**
```python
class Issue(BaseGithubModel):
    payload: dict
    number: int
    labels: List[Label]
    assignees: List[User]

    def __init__(self, payload: dict):
        self.payload = payload
        self.number = payload.get("number")
        self.labels = [Label(label) for label in payload.get("labels", [])]
        self.assignees = [User(assignee) for assignee in payload.get("assignees", [])]
```

**After:**
```python
class Issue(BaseGithubModel):
    number: int
    labels: List[Label] = []  # Pydantic validates each Label
    assignees: List[User] = []  # Pydantic validates each User
```

### Example: Deployment with Field Collision

**Before:**
```python
class Deployment(BaseGithubModel):
    payload: dict
    url: str
    id: int
    payload: Annotated[dict, "unstructured"]  # Collision!

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.id = payload.get("id")
        self.payload = payload.get("payload")  # Overwrites!
```

**After:**
```python
class Deployment(BaseGithubModel):
    url: str
    id: int
    payload_data: dict[str, Any] = Field(alias="payload")
```

### Special Cases to Remember

**1. Label class - Preserve custom methods:**
```python
class Label(BaseGithubModel):
    # ... fields ...

    def __eq__(self, other):
        # KEEP THIS!
        if isinstance(other, Label):
            return self.name == other.name
        return False

    def __repr__(self):
        # KEEP THIS!
        return f"Label(name='{self.name}', color='{self.color}')"
```

**2. Repository - 19 template URLs:**
Most complex model in the codebase. Template URLs include:
- assignees_url, blobs_url, branches_url, collaborators_url, comments_url
- commits_url, compare_url, contents_url, contributors_url, deployments_url
- downloads_url, events_url, forks_url, git_commits_url, git_refs_url
- git_tags_url, hooks_url, issue_comment_url, issue_events_url

**3. Models with `_links` fields:**
Must rename to `links_` with `Field(alias="_links")`:
- Comment
- Review
- (Any other model with underscore-prefixed field)

## Dependencies

**Requires:**
- PR #1 (base classes)
- PR #2 (many models in this PR reference models from PR #2)

**Blocks:** PR #4 (events depend on models)

## Testing Strategy

```bash
# Run full test suite
uv run pytest -v

# Test template URL models specifically
uv run python -c "
from octohook.models import User
u = User.model_validate({
    'login': 'test',
    'id': 123,
    'following_url': 'https://api.github.com/users/test/following{/other_user}',
    'gists_url': 'https://api.github.com/users/test/gists{/gist_id}',
    'starred_url': 'https://api.github.com/users/test/starred{/owner}{/repo}',
    'subscriptions_url': 'https://api.github.com/users/test/subscriptions',
    # ... other required fields
})
print(u.following_url('johndoe'))  # Should return URL with 'johndoe'
print(u.gists_url())  # Should return base URL
"

# Test unstructured dict aliasing
uv run python -c "
from octohook.models import Comment
c = Comment.model_validate({
    'id': 1,
    'body': 'test',
    '_links': {'self': 'url'},
    'reactions': {'+1': 5}
})
print(c.links_)  # Should print {'self': 'url'}
print(c.reactions)  # Should print {'+1': 5}
"

# Test Label custom methods
uv run python -c "
from octohook.models import Label
l1 = Label.model_validate({'id': 1, 'name': 'bug', 'color': 'red', 'node_id': 'x', 'url': 'url', 'default': False})
l2 = Label.model_validate({'id': 2, 'name': 'bug', 'color': 'blue', 'node_id': 'y', 'url': 'url', 'default': False})
print(l1 == l2)  # Should be True (same name)
print(repr(l1))  # Should show custom repr
"

# Test Deployment field collision resolution
uv run python -c "
from octohook.models import Deployment
d = Deployment.model_validate({
    'url': 'http://example.com',
    'id': 1,
    'payload': {'key': 'value'},  # This goes to payload_data
    # ... other required fields
})
print(d.payload_data)  # Should print {'key': 'value'}
"
```

**Expected outcomes:**
- ✅ Template URL methods work correctly with parameters
- ✅ Unstructured dicts accessible via renamed fields
- ✅ Field aliases work (can pass both `_links` and `links_`)
- ✅ Label equality and repr work correctly
- ✅ Deployment.payload_data receives the "payload" field
- ✅ All tests pass

## Risk Level

**Medium**

- Template URLs are more complex than simple models
- Field aliasing must be correct or data won't parse
- Deployment field collision is a tricky edge case
- Repository has 19 template URLs (error-prone)
- Custom Label methods must be preserved

## Rationale

**Why these 29 models:**
- All models with special complexity (template URLs, unstructured dicts)
- Separates "hard" models from "easy" models (PR #2)
- Allows focused review on complex patterns
- Deployment field collision is unique edge case

**Why after PR #2:**
- Many models here depend on models from PR #2 (e.g., Repository → User, Issue → Label)
- Sequential execution prevents dependency issues
- Reviewers can reference PR #2 patterns for basic structure

**Why separate from PR #2:**
- Different complexity level requires different review focus
- Template URL pattern is distinct from simple models
- Keeps each PR reviewable (~400-500 lines each)

## Lines Changed (Est)

~400-500 lines

**Breakdown:**
- Remove ~700 lines (29 __init__ methods, payload fields)
- Add ~200 lines (template URL fields with aliases, dict[str, Any] types)
- Net reduction: ~500 lines removed

## Rollback Instructions

**If this PR must be reverted:**

1. Revert the commit:
```bash
git revert <commit-hash>
```

2. **Note:** If PR #4 is already merged, it must be reverted first.

3. Verify rollback:
```bash
uv run pytest tests/ -v
```

4. Check template URL functionality:
```bash
# Ensure old pattern works
uv run python -c "from octohook.models import User; print('User import OK')"
```

## Additional Notes

**Critical reminders:**

- **Label class is special:** Custom `__eq__` and `__repr__` must be preserved!
- **Template URL field naming:** Must be `{method_name}_template`, not just `{method_name}`
- **Field aliases are case-sensitive:** `Field(alias="following_url")` must match GitHub exactly
- **Underscore fields:** Pydantic forbids field names starting with `_` - must use aliases
- **Deployment is unique:** Only model with field name collision - use `payload_data`

**Repository template URLs (19 total):**
```python
assignees_url_template: str = Field(alias="assignees_url")
blobs_url_template: str = Field(alias="blobs_url")
branches_url_template: str = Field(alias="branches_url")
collaborators_url_template: str = Field(alias="collaborators_url")
comments_url_template: str = Field(alias="comments_url")
commits_url_template: str = Field(alias="commits_url")
compare_url_template: str = Field(alias="compare_url")
contents_url_template: str = Field(alias="contents_url")
contributors_url_template: str = Field(alias="contributors_url")
deployments_url_template: str = Field(alias="deployments_url")
downloads_url_template: str = Field(alias="downloads_url")
events_url_template: str = Field(alias="events_url")
forks_url_template: str = Field(alias="forks_url")
git_commits_url_template: str = Field(alias="git_commits_url")
git_refs_url_template: str = Field(alias="git_refs_url")
git_tags_url_template: str = Field(alias="git_tags_url")
hooks_url_template: str = Field(alias="hooks_url")
issue_comment_url_template: str = Field(alias="issue_comment_url")
issue_events_url_template: str = Field(alias="issue_events_url")
```

**Post-merge checklist:**
- ✅ 29 models migrated
- ✅ All template URL fields have `_template` suffix and aliases
- ✅ All template URL methods updated to use `self.*_template`
- ✅ All underscore fields renamed with aliases
- ✅ Label custom methods preserved
- ✅ Deployment uses `payload_data` field
- ✅ All unstructured dicts use `dict[str, Any]`
- ✅ Tests pass

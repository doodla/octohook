from abc import ABC
from typing import TypeVar, Optional, Type, List, Any

T = TypeVar("T")


def _optional(payload: dict, key: str, class_type: Type[T]) -> Optional[T]:
    if payload.get(key):
        return class_type(payload[key])
    else:
        return None


def _transform(url: str, local_variables: dict) -> str:
    local_variables.pop("self", None)

    for key, value in local_variables.items():
        if not value:
            url = url.split(f"{{/{key}}}")[0]
            # If we find a None value, we shouldn't process the url any more.
            break
        elif f"{{{key}}}" in url:
            url = url.replace(f"{{{key}}}", value)
        elif f"{{/{key}}}" in url:
            url = url.replace(f"{{/{key}}}", f"/{value}")

    return url


class BaseGithubModel(ABC):
    def __new__(cls, *args, **kwargs):
        from octohook import model_overrides

        cls = model_overrides.get(cls) or cls
        return object.__new__(cls)


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


class User(BaseGithubModel):
    payload: dict
    name: Optional[str]
    login: str
    email: Optional[str]
    id: int
    node_id: Optional[str]
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    subscriptions_url: str
    organization_url: str
    repos_url: str
    organizations_url: str
    received_events_url: str
    type: str
    site_admin: bool

    def __init__(self, payload: dict):
        self.payload = payload
        self.name = payload.get("name")
        self.login = payload.get("login")
        self.email = payload.get("email")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.avatar_url = payload.get("avatar_url")
        self.gravatar_id = payload.get("gravatar_id")
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.followers_url = payload.get("followers_url")
        self.subscriptions_url = payload.get("subscriptions_url")
        self.organization_url = payload.get("organizations_url")
        self.repos_url = payload.get("repos_url")
        self.organizations_url = payload.get("organizations_url")
        self.received_events_url = payload.get("received_events_url")
        self.type = payload.get("type")
        self.site_admin = payload.get("site_admin")

    def following_url(self, other_user: str = None) -> str:
        return _transform(self.payload["following_url"], locals())

    def gists_url(self, gist_id: str = None) -> str:
        return _transform(self.payload["gists_url"], locals())

    def starred_url(self, owner: str = None, repo: str = None) -> str:
        return _transform(self.payload["starred_url"], locals())

    def events_url(self, privacy: str = None) -> str:
        return _transform(self.payload["events_url"], locals())

    def __str__(self):
        return self.login


class ShortRepository(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.full_name = payload.get("full_name")
        self.private = payload.get("private")

    def __str__(self):
        return self.full_name


class RawDict(dict):
    def __init__(self, payload: dict):
        super().__init__(payload)


class Permissions(BaseGithubModel):
    payload: dict
    metadata: str
    contents: str
    issues: str
    administration: str
    statuses: str
    repository_projects: str
    members: str
    repository_hooks: str
    pull_requests: str
    pull: Optional[str]
    push: Optional[str]
    admin: Optional[str]
    pages: str
    deployments: str
    checks: str
    vulnerability_alerts: str
    organization_administration: str
    organization_hooks: str
    organization_plan: str
    organization_projects: str
    organization_user_blocking: str
    team_discussions: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.metadata = payload.get("metadata")
        self.contents = payload.get("contents")
        self.issues = payload.get("issues")
        self.administration = payload.get("administration")
        self.statuses = payload.get("statuses")
        self.repository_projects = payload.get("repository_projects")
        self.members = payload.get("members")
        self.repository_hooks = payload.get("repository_hooks")
        self.pull_requests = payload.get("pull_requests")
        self.pull = payload.get("pull")
        self.push = payload.get("push")
        self.admin = payload.get("admin")
        self.pages = payload.get("pages")
        self.deployments = payload.get("deployments")
        self.checks = payload.get("checks")
        self.vulnerability_alerts = payload.get("vulnerability_alerts")
        self.organization_administration = payload.get("organization_administration")
        self.organization_hooks = payload.get("organization_hooks")
        self.organization_plan = payload.get("organization_plan")
        self.organization_projects = payload.get("organization_projects")
        self.organization_user_blocking = payload.get("organization_user_blocking")
        self.team_discussions = payload.get("team_discussions")


class Repository(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: User
    html_url: str
    description: str
    fork: bool
    url: str
    forks_url: str
    teams_url: str
    hooks_url: str
    events_url: str
    tags_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    merges_url: str
    downloads_url: str
    deployments_url: str
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: Optional[str]
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str]
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    forks_count: int
    mirror_url: Optional[str]
    archived: bool
    disabled: bool
    open_issues_count: int
    license: Optional[str]
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    stargazers: Optional[int]
    public: Optional[bool]
    master_branch: Optional[str]
    permissions: Optional[Permissions]
    allow_forking: Optional[bool]
    allow_squash_merge: Optional[bool]
    allow_merge_commit: Optional[bool]
    allow_rebase_merge: Optional[bool]
    allow_update_branch: Optional[bool]
    allow_auto_merge: Optional[bool]
    delete_branch_on_merge: Optional[bool]
    use_squash_pr_title_as_default: Optional[bool]
    squash_merge_commit_message: Optional[str]
    squash_merge_commit_title: Optional[str]
    merge_commit_message: Optional[str]
    merge_commit_title: Optional[str]
    is_template: Optional[bool]
    topics: List[str]
    visibility: Optional[str]
    web_commit_signoff_required: Optional[bool]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.full_name = payload.get("full_name")
        self.private = payload.get("private")
        self.owner = User(payload.get("owner"))
        self.html_url = payload.get("html_url")
        self.description = payload.get("description")
        self.fork = payload.get("fork")
        self.url = payload.get("url")
        self.forks_url = payload.get("forks_url")
        self.teams_url = payload.get("teams_url")
        self.hooks_url = payload.get("hooks_url")
        self.events_url = payload.get("events_url")
        self.tags_url = payload.get("tags_url")
        self.languages_url = payload.get("languages_url")
        self.stargazers_url = payload.get("stargazers_url")
        self.contributors_url = payload.get("contributors_url")
        self.subscribers_url = payload.get("subscribers_url")
        self.subscription_url = payload.get("subscription_url")
        self.merges_url = payload.get("merges_url")
        self.downloads_url = payload.get("downloads_url")
        self.deployments_url = payload.get("deployments_url")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.pushed_at = payload.get("pushed_at")
        self.git_url = payload.get("git_url")
        self.ssh_url = payload.get("ssh_url")
        self.clone_url = payload.get("clone_url")
        self.svn_url = payload.get("svn_url")
        self.homepage = payload.get("homepage")
        self.size = payload.get("size")
        self.stargazers_count = payload.get("stargazers_count")
        self.watchers_count = payload.get("watchers_count")
        self.language = payload.get("language")
        self.has_issues = payload.get("has_issues")
        self.has_projects = payload.get("has_projects")
        self.has_downloads = payload.get("has_downloads")
        self.has_wiki = payload.get("has_wiki")
        self.has_pages = payload.get("has_pages")
        self.forks_count = payload.get("forks_count")
        self.mirror_url = payload.get("mirror_url")
        self.archived = payload.get("archived")
        self.disabled = payload.get("disabled")
        self.open_issues_count = payload.get("open_issues_count")
        self.license = payload.get("license")
        self.forks = payload.get("forks")
        self.open_issues = payload.get("open_issues")
        self.watchers = payload.get("watchers")
        self.default_branch = payload.get("default_branch")
        self.stargazers = payload.get("stargazers")
        self.public = payload.get("public")
        self.master_branch = payload.get("master_branch")
        self.permissions = _optional(payload, "permissions", Permissions)
        self.allow_forking = payload.get("allow_forking")
        self.allow_squash_merge = payload.get("allow_squash_merge")
        self.allow_merge_commit = payload.get("allow_merge_commit")
        self.allow_rebase_merge = payload.get("allow_rebase_merge")
        self.allow_auto_merge = payload.get("allow_auto_merge")
        self.allow_update_branch = payload.get("allow_auto_merge")
        self.use_squash_pr_title_as_default = payload.get(
            "use_squash_pr_title_as_default"
        )
        self.squash_merge_commit_message = payload.get("squash_merge_commit_message")
        self.squash_merge_commit_title = payload.get("squash_merge_commit_title")
        self.merge_commit_message = payload.get("merge_commit_message")
        self.merge_commit_title = payload.get("merge_commit_title")
        self.delete_branch_on_merge = payload.get("delete_branch_on_merge")
        self.is_template = payload.get("is_template")
        self.topics = payload.get("topics") or []
        self.visibility = payload.get("visibility")
        self.web_commit_signoff_required = _optional(
            payload, "web_commit_signoff_required", bool
        )

    def keys_url(self, key_id: str = None) -> str:
        return _transform(self.payload["keys_url"], locals())

    def collaborators_url(self, collaborator: str = None) -> str:
        return _transform(self.payload["collaborators_url"], locals())

    def issue_events_url(self, number: int = None) -> str:
        return _transform(self.payload["issue_events_url"], locals())

    def assignees_url(self, user: str = None) -> str:
        return _transform(self.payload["assignees_url"], locals())

    def branches_url(self, branch: str = None) -> str:
        return _transform(self.payload["branches_url"], locals())

    def blobs_url(self, sha: str = None) -> str:
        return _transform(self.payload["blobs_url"], locals())

    def git_tags_url(self, sha: str = None) -> str:
        return _transform(self.payload["git_tags_url"], locals())

    def git_refs_url(self, sha: str = None) -> str:
        return _transform(self.payload["git_refs_url"], locals())

    def trees_url(self, sha: str = None) -> str:
        return _transform(self.payload["trees_url"], locals())

    def statuses_url(self, sha: str) -> str:
        return _transform(self.payload["statuses_url"], locals())

    def commits_url(self, sha: str = None) -> str:
        return _transform(self.payload["commits_url"], locals())

    def git_commits_url(self, sha=None) -> str:
        return _transform(self.payload["git_commits_url"], locals())

    def comments_url(self, number: int = None) -> str:
        return _transform(self.payload["comments_url"], locals())

    def issue_comment_url(self, number: int = None) -> str:
        return _transform(self.payload["issue_comment_url"], locals())

    def contents_url(self, path: str) -> str:
        return _transform(self.payload["contents_url"].replace("+", ""), locals())

    def compare_url(self, base: str, head: str) -> str:
        return _transform(self.payload["compare_url"], locals())

    def archive_url(self, archive_format: str, ref: str = None) -> str:
        return _transform(self.payload["archive_url"], locals())

    def issues_url(self, number: str = None) -> str:
        return _transform(self.payload["issues_url"], locals())

    def pulls_url(self, number: str = None) -> str:
        return _transform(self.payload["pulls_url"], locals())

    def milestones_url(self, number: str = None) -> str:
        return _transform(self.payload["milestones_url"], locals())

    def notifications_url(self, params: str = None) -> str:
        if params is not None:
            if not params.startswith("?"):
                raise AttributeError("Params must be a query string starting with ?")
        replace_with = params if params else ""
        return self.payload["notifications_url"].replace(
            "{?since,all,participating}", replace_with
        )

    def labels_url(self, name: str = None) -> str:
        return _transform(self.payload["labels_url"], locals())

    def releases_url(self, id: str = None) -> str:
        return _transform(self.payload["releases_url"], locals())

    def __str__(self):
        return self.full_name


class Organization(BaseGithubModel):
    payload: dict
    login: str
    id: int
    node_id: str
    url: str
    repos_url: str
    events_url: str
    hooks_url: str
    issues_url: str
    public_members_url: str
    avatar_url: str
    description: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.login = payload.get("login")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.url = payload.get("url")
        self.repos_url = payload.get("repos_url")
        self.events_url = payload.get("events_url")
        self.hooks_url = payload.get("hooks_url")
        self.issues_url = payload.get("issues_url")
        self.public_members_url = payload.get("public_members_url")
        self.avatar_url = payload.get("avatar_url")
        self.description = payload.get("description")

    def members_url(self, member: str = None) -> str:
        return _transform(self.payload["members_url"], locals())

    def public_members_url(self, member: str = None) -> str:
        return _transform(self.payload["public_members_url"], locals())

    def __str__(self):
        return self.login


class Comment(BaseGithubModel):
    payload: dict
    url: str
    html_url: str
    issue_url: Optional[str]
    id: int
    pull_request_review_id: Optional[int]
    original_position: Optional[int]
    original_commit_id: Optional[str]
    pull_request_url: Optional[str]
    diff_hunk: Optional[str]
    node_id: str
    user: User
    position: Optional[int]
    line: Optional[int]
    path: Optional[str]
    commit_id: Optional[str]
    created_at: str
    updated_at: str
    author_association: str
    body: str
    start_line: Optional[int]
    original_start_line: Optional[int]
    start_side: Optional[str]
    original_line: Optional[int]
    side: Optional[str]
    reactions: Optional[RawDict]

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.issue_url = payload.get("issue_url")
        self.id = payload.get("id")
        self.pull_request_review_id = payload.get("pull_request_review_id")
        self.original_position = payload.get("original_position")
        self.original_commit_id = payload.get("original_commit_id")
        self.pull_request_url = payload.get("pull_request_url")
        self.diff_hunk = payload.get("diff_hunk")
        self.node_id = payload.get("node_id")
        self.user = User(payload.get("user"))
        self.position = payload.get("position")
        self.line = payload.get("line")
        self.path = payload.get("path")
        self.commit_id = payload.get("commit_id")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.author_association = payload.get("author_association")
        self.body = payload.get("body")
        self._links = _optional(payload, "_links", RawDict)
        self.start_line = payload.get("start_line")
        self.original_start_line = payload.get("original_start_line")
        self.start_side = payload.get("start_side")
        self.original_line = payload.get("original_line")
        self.side = payload.get("side")
        self.reactions = _optional(payload, "reactions", RawDict)

    def __str__(self):
        return self.body


class Thread(BaseGithubModel):
    payload: dict
    node_id: str
    comments: List[Comment]

    def __init__(self, payload: dict):
        self.payload = payload
        self.node_id = payload.get("node_id")
        self.comments = [Comment(comment) for comment in payload.get("comments")]


class ChecksApp(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    owner: User
    name: str
    description: str
    external_url: str
    html_url: str
    created_at: str
    updated_at: str
    permissions: Permissions
    events: List[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.owner = User(payload.get("owner"))
        self.name = payload.get("name")
        self.description = payload.get("description")
        self.external_url = payload.get("external_url")
        self.html_url = payload.get("html_url")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.permissions = Permissions(payload.get("permissions"))
        self.events = payload.get("events")


class ChecksPullRequest(BaseGithubModel):
    payload: dict
    url: str
    id: int
    number: int
    head: RawDict
    base: RawDict

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.id = payload.get("id")
        self.number = payload.get("number")
        self.head = RawDict(payload.get("head"))
        self.base = RawDict(payload.get("base"))


class CommitUser(BaseGithubModel):
    payload: dict
    name: str
    email: str
    username: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.name = payload.get("name")
        self.email = payload.get("email")
        self.username = payload.get("username")


class Commit(BaseGithubModel):
    payload: dict
    id: str
    tree_id: str
    distinct: bool
    message: str
    url: str
    timestamp: str
    author: CommitUser
    committer: CommitUser
    added: List[str]
    removed: List[str]
    modified: List[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.tree_id = payload.get("tree_id")
        self.distinct = payload.get("distinct")
        self.message = payload.get("message")
        self.url = payload.get("url")
        self.timestamp = payload.get("timestamp")
        self.author = CommitUser(payload.get("author"))
        self.committer = CommitUser(payload.get("committer"))
        self.added = payload.get("added")
        self.removed = payload.get("removed")
        self.modified = payload.get("modified")


class CheckSuite(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    head_branch: str
    head_sha: str
    status: str
    conclusion: Optional[str]
    url: str
    before: str
    after: str
    pull_requests: List[ChecksPullRequest]
    app: ChecksApp
    created_at: str
    updated_at: str
    latest_check_runs_count: Optional[int]
    check_runs_url: Optional[str]
    head_commit: Optional[Commit]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.head_branch = payload.get("head_branch")
        self.head_sha = payload.get("head_sha")
        self.status = payload.get("status")
        self.conclusion = payload.get("conclusion")
        self.url = payload.get("url")
        self.before = payload.get("before")
        self.after = payload.get("after")
        self.pull_requests = [
            ChecksPullRequest(pr) for pr in payload.get("pull_requests")
        ]
        self.app = ChecksApp(payload.get("app"))
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.latest_check_runs_count = payload.get("latest_check_runs_count")
        self.check_runs_url = payload.get("check_runs_url")
        self.head_commit = _optional(payload, "head_commit", Commit)


class CheckRunOutput(BaseGithubModel):
    payload: dict
    title: Optional[str]
    summary: Optional[str]
    text: Optional[str]
    annotations_count: int
    annotations_url: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.title = payload.get("title")
        self.summary = payload.get("summary")
        self.text = payload.get("text")
        self.annotations_count = payload.get("annotations_count")
        self.annotations_url = payload.get("annotations_url")


class CheckRun(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    head_sha: str
    external_id: str
    url: str
    html_url: str
    details_url: str
    status: str
    conclusion: Optional[str]
    started_at: str
    completed_at: Optional[str]
    output: CheckRunOutput
    name: str
    check_suite: CheckSuite
    app: ChecksApp
    pull_requests: List[ChecksPullRequest]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.head_sha = payload.get("head_sha")
        self.external_id = payload.get("external_id")
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.details_url = payload.get("details_url")
        self.status = payload.get("status")
        self.conclusion = payload.get("conclusion")
        self.started_at = payload.get("started_at")
        self.completed_at = payload.get("completed_at")
        self.output = CheckRunOutput(payload.get("output"))
        self.name = payload.get("name")
        self.check_suite = CheckSuite(payload.get("check_suite"))
        self.app = ChecksApp(payload.get("app"))
        self.pull_requests = [
            ChecksPullRequest(pr) for pr in payload.get("pull_requests")
        ]


class ShortInstallation(BaseGithubModel):
    payload: dict
    id: int
    node_id: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")


class Installation(BaseGithubModel):
    payload: dict
    id: int
    node_id: Optional[str]
    account: User
    repository_selection: str
    access_tokens_url: str
    repositories_url: str
    html_url: str
    app_id: int
    target_id: int
    permissions: Optional[Permissions]
    events: List[str]
    created_at: int
    updated_at: int
    single_file_name: Optional[str]
    target_type: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id", None)
        self.account = _optional(payload, "account", User)
        self.repository_selection = payload.get("repository_selection")
        self.access_tokens_url = payload.get("access_tokens_url")
        self.repositories_url = payload.get("repositories_url")
        self.html_url = payload.get("html_url")
        self.app_id = payload.get("app_id")
        self.target_id = payload.get("target_id")
        self.permissions = _optional(payload, "permissions", Permissions)
        self.events = payload.get("events")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.single_file_name = payload.get("single_file_name")
        self.target_type = payload.get("target_type")


class DeployKey(BaseGithubModel):
    payload: dict
    id: int
    key: str
    url: str
    title: str
    verified: bool
    created_at: str
    read_only: bool

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.key = payload.get("key")
        self.url = payload.get("url")
        self.title = payload.get("title")
        self.verified = payload.get("verified")
        self.created_at = payload.get("created_at")
        self.read_only = payload.get("read_only")


class Deployment(BaseGithubModel):
    payload: dict
    url: str
    id: int
    node_id: str
    sha: str
    ref: str
    task: str
    payload: RawDict
    original_environment: str
    environment: str
    description: Optional[str]
    creator: User
    created_at: str
    updated_at: str
    statuses_url: str
    repository_url: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.sha = payload.get("sha")
        self.ref = payload.get("ref")
        self.task = payload.get("task")
        self.payload = RawDict(payload.get("payload"))
        self.original_environment = payload.get("original_environment")
        self.environment = payload.get("environment")
        self.description = payload.get("description")
        self.creator = User(payload.get("creator"))
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.statuses_url = payload.get("statuses_url")
        self.repository_url = payload.get("repository_url")


class DeploymentStatus(BaseGithubModel):
    payload: dict
    url: str
    id: int
    node_id: str
    state: str
    creator: User
    description: str
    environment: str
    target_url: str
    created_at: str
    updated_at: str
    deployment_url: str
    repository_url: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.state = payload.get("state")
        self.creator = User(payload.get("creator"))
        self.description = payload.get("description")
        self.environment = payload.get("environment")
        self.target_url = payload.get("target_url")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.deployment_url = payload.get("deployment_url")
        self.repository_url = payload.get("repository_url")


class Page(BaseGithubModel):
    payload: dict
    page_name: str
    title: str
    summary: str
    action: str
    sha: str
    html_url: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.page_name = payload.get("page_name")
        self.title = payload.get("title")
        self.summary = payload.get("summary")
        self.action = payload.get("action")
        self.sha = payload.get("sha")
        self.html_url = payload.get("html_url")


class Label(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    url: str
    name: str
    color: str
    description: str
    default: bool

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.url = payload.get("url")
        self.name = payload.get("name")
        self.color = payload.get("color")
        self.description = payload.get("description")
        self.default = payload.get("default")

    def __eq__(self, other):
        return self.name == other

    def __repr__(self):
        return f"{self.name}(#{self.color})"

    def __str__(self):
        return self.name


class Milestone(BaseGithubModel):
    payload: dict
    url: str
    html_url: str
    labels_url: str
    id: int
    node_id: str
    number: int
    title: str
    description: str
    creator: Optional[User]
    open_issues: int
    closed_issues: int
    state: str
    created_at: str
    updated_at: str
    due_on: Optional[str]
    closed_at: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.labels_url = payload.get("labels_url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.number = payload.get("number")
        self.title = payload.get("title")
        self.description = payload.get("description")
        self.creator = _optional(payload, "creator", User)
        self.open_issues = payload.get("open_issues")
        self.closed_issues = payload.get("closed_issues")
        self.state = payload.get("state")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.due_on = payload.get("due_on")
        self.closed_at = payload.get("closed_at")


class Issue(BaseGithubModel):
    payload: dict
    url: str
    repository_url: str
    comments_url: str
    events_url: str
    html_url: str
    id: int
    node_id: str
    number: int
    title: str
    user: User
    labels: List[Label]
    state: str
    locked: bool
    assignee: Optional[User]
    assignees: List[User]
    milestone: Optional[Milestone]
    comments: int
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    author_association: str
    body: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.repository_url = payload.get("repository_url")
        self.comments_url = payload.get("comments_url")
        self.events_url = payload.get("events_url")
        self.html_url = payload.get("html_url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.number = payload.get("number")
        self.title = payload.get("title")
        self.user = User(payload.get("user"))
        self.labels = [Label(label) for label in payload.get("labels")]
        self.state = payload.get("state")
        self.locked = payload.get("locked")
        self.assignee = _optional(payload, "assignee", User)
        self.assignees = [User(assignee) for assignee in payload.get("assignees")]
        self.milestone = _optional(payload, "milestone", Milestone)
        self.comments = payload.get("comments")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.closed_at = payload.get("closed_at")
        self.author_association = payload.get("author_association")
        self.body = payload.get("body")

    def labels_url(self, name: str = None) -> str:
        return _transform(self.payload["labels_url"], locals())


class PurchaseAccount(BaseGithubModel):
    payload: dict
    type: str
    id: int
    login: str
    organization_billing_email: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.type = payload.get("type")
        self.id = payload.get("id")
        self.login = payload.get("login")
        self.organization_billing_email = payload.get("organization_billing_email")


class Plan(BaseGithubModel):
    payload: dict
    id: int
    name: str
    description: str
    monthly_price_in_cents: int
    yearly_price_in_cents: int
    yearly_price: Optional[int]
    price_model: str
    has_free_trial: bool
    unit_name: str
    bullets: List[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.name = payload.get("name")
        self.description = payload.get("description")
        self.monthly_price_in_cents = payload.get("monthly_price_in_cents")
        self.yearly_price_in_cents = payload.get("yearly_price_in_cents")
        self.yearly_price = payload.get("yearly_price")
        self.price_model = payload.get("price_model")
        self.has_free_trial = payload.get("has_free_trial")
        self.unit_name = payload.get("unit_name")
        self.bullets = payload.get("bullets")


class MarketplacePurchase(BaseGithubModel):
    payload: dict
    account: PurchaseAccount
    billing_cycle: str
    unit_count: int
    on_free_trial: bool
    free_trial_ends_on: Optional[str]
    next_billing_date: str
    plan: Plan

    def __init__(self, payload: dict):
        self.payload = payload
        self.account = PurchaseAccount(payload.get("account"))
        self.billing_cycle = payload.get("billing_cycle")
        self.unit_count = payload.get("unit_count")
        self.on_free_trial = payload.get("on_free_trial")
        self.free_trial_ends_on = payload.get("free_trial_ends_on")
        self.next_billing_date = payload.get("next_billing_date")
        self.plan = Plan(payload.get("plan"))


class Team(BaseGithubModel):
    payload: dict
    name: str
    id: int
    node_id: str
    slug: str
    description: str
    privacy: str
    url: str
    html_url: str
    repositories_url: str
    permission: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.name = payload.get("name")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.slug = payload.get("slug")
        self.description = payload.get("description")
        self.privacy = payload.get("privacy")
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.repositories_url = payload.get("repositories_url")
        self.permission = payload.get("permission")

    def members_url(self, member: str = None) -> str:
        return _transform(self.payload["members_url"], locals())


class Hook(BaseGithubModel):
    payload: dict
    type: str
    id: int
    name: str
    active: bool
    events: List[str]
    config: RawDict
    updated_at: str
    created_at: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.type = payload.get("type")
        self.id = payload.get("id")
        self.name = payload.get("name")
        self.active = payload.get("active")
        self.events = payload.get("events")
        self.config = RawDict(payload.get("config"))
        self.updated_at = payload.get("updated_at")
        self.created_at = payload.get("created_at")


class Membership(BaseGithubModel):
    payload: dict
    url: str
    state: str
    role: str
    organization_url: str
    user: User

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.state = payload.get("state")
        self.role = payload.get("role")
        self.organization_url = payload.get("organization_url")
        self.user = User(payload.get("user"))


class Asset(BaseGithubModel):
    payload: dict
    url: str
    id: str
    node_id: str
    name: str
    label: str
    uploader: User
    content_type: str
    state: str
    size: str
    download_count: str
    created_at: str
    updated_at: str
    browser_download_url: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.label = payload.get("label")
        self.uploader = User(payload.get("uploader"))
        self.content_type = payload.get("content_type")
        self.state = payload.get("state")
        self.size = payload.get("size")
        self.download_count = payload.get("download_count")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.browser_download_url = payload.get("browser_download_url")


class Release(BaseGithubModel):
    payload: dict
    url: str
    assets_url: Optional[str]
    upload_url: Optional[str]
    html_url: str
    id: int
    node_id: Optional[str]
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    author: User
    prerelease: bool
    created_at: str
    published_at: Optional[str]
    assets: List[Asset]
    tarball_url: Optional[str]
    zipball_url: Optional[str]
    body: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.assets_url = payload.get("assets_url", None)
        self.upload_url = payload.get("upload_url", None)
        self.html_url = payload.get("html_url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id", None)
        self.tag_name = payload.get("tag_name")
        self.target_commitish = payload.get("target_commitish")
        self.name = payload.get("name")
        self.draft = payload.get("draft")
        self.author = User(payload.get("author"))
        self.prerelease = payload.get("prerelease")
        self.created_at = payload.get("created_at")
        self.published_at = payload.get("published_at")
        self.assets = [Asset(asset) for asset in payload.get("assets", [])]
        self.tarball_url = payload.get("tarball_url", None)
        self.zipball_url = payload.get("zipball_url", None)
        self.body = payload.get("body", None)


class PackageFile(BaseGithubModel):
    payload: dict
    download_url: str
    id: str
    name: str
    sha256: str
    sha1: str
    md5: str
    content_type: str
    state: str
    size: str
    created_at: str
    updated_at: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.download_url = payload.get("download_url")
        self.id = payload.get("id")
        self.name = payload.get("name")
        self.sha256 = payload.get("sha256")
        self.sha1 = payload.get("sha1")
        self.md5 = payload.get("md5")
        self.content_type = payload.get("content_type")
        self.state = payload.get("state")
        self.size = payload.get("size")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")


class PackageVersion(BaseGithubModel):
    payload: dict
    id: int
    version: str
    summary: str
    body: str
    body_html: str
    release: Release
    manifest: str
    html_url: str
    tag_name: str
    target_commitish: str
    target_oid: str
    draft: bool
    prerelease: bool
    created_at: str
    updated_at: str
    metadata: List[Any]
    package_files: List[PackageFile]
    author: User
    installation_command: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.version = payload.get("version")
        self.summary = payload.get("summary")
        self.body = payload.get("body")
        self.body_html = payload.get("body_html")
        self.release = Release(payload.get("release"))
        self.manifest = payload.get("manifest")
        self.html_url = payload.get("html_url")
        self.tag_name = payload.get("tag_name")
        self.target_commitish = payload.get("target_commitish")
        self.target_oid = payload.get("target_oid")
        self.draft = payload.get("draft")
        self.prerelease = payload.get("prerelease")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.metadata = payload.get("metadata")
        self.package_files = [
            PackageFile(file) for file in payload.get("package_files")
        ]
        self.author = User(payload.get("author"))
        self.installation_command = payload.get("installation_command")


class Registry(BaseGithubModel):
    payload: dict
    about_url: str
    name: str
    type: str
    url: str
    vendor: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.about_url = payload.get("about_url")
        self.name = payload.get("name")
        self.type = payload.get("type")
        self.url = payload.get("url")
        self.vendor = payload.get("vendor")


class Package(BaseGithubModel):
    payload: dict
    id: int
    name: str
    package_type: str
    html_url: str
    created_at: str
    updated_at: str
    owner: User
    package_version: PackageVersion
    registry: Registry

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.name = payload.get("name")
        self.package_type = payload.get("package_type")
        self.html_url = payload.get("html_url")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.owner = User(payload.get("owner"))
        self.package_version = PackageVersion(payload.get("package_version"))
        self.registry = Registry(payload.get("registry"))


class PageBuild(BaseGithubModel):
    payload: dict
    url: str
    status: str
    error: RawDict
    pusher: User
    commit: str
    duration: int
    created_at: str
    updated_at: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.status = payload.get("status")
        self.error = RawDict(payload.get("error"))
        self.pusher = User(payload.get("pusher"))
        self.commit = payload.get("commit")
        self.duration = payload.get("duration")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")


class ProjectCard(BaseGithubModel):
    payload: dict
    url: str
    project_url: str
    column_url: str
    column_id: int
    id: int
    node_id: str
    note: Optional[str]
    archived: bool
    after_id: Optional[str]
    creator: User
    created_at: str
    updated_at: str
    content_url: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.project_url = payload.get("project_url")
        self.column_url = payload.get("column_url")
        self.column_id = payload.get("column_id")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.note = payload.get("note")
        self.archived = payload.get("archived")
        self.after_id = payload.get("after_id")
        self.creator = User(payload.get("creator"))
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.content_url = payload.get("content_url")


class ProjectColumn(BaseGithubModel):
    payload: dict
    url: str
    project_url: str
    cards_url: str
    id: int
    node_id: str
    name: str
    created_at: str
    updated_at: str
    after_id: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.project_url = payload.get("project_url")
        self.cards_url = payload.get("cards_url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.after_id = payload.get("after_id")


class Project(BaseGithubModel):
    payload: dict
    owner_url: str
    url: str
    html_url: str
    columns_url: str
    id: int
    node_id: str
    name: str
    body: str
    number: int
    state: str
    creator: User
    created_at: str
    updated_at: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.owner_url = payload.get("owner_url")
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.columns_url = payload.get("columns_url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.body = payload.get("body")
        self.number = payload.get("number")
        self.state = payload.get("state")
        self.creator = User(payload.get("creator"))
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")


class Ref(BaseGithubModel):
    payload: dict
    label: str
    ref: str
    sha: str
    user: User
    repo: Repository

    def __init__(self, payload: dict):
        self.payload = payload
        self.label = payload.get("label")
        self.ref = payload.get("ref")
        self.sha = payload.get("sha")
        self.user = User(payload.get("user"))
        self.repo = Repository(payload.get("repo"))


class PullRequest(BaseGithubModel):
    payload: dict
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: User
    body: str
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    merged_at: Optional[str]
    merge_commit_sha: Optional[str]
    assignee: Optional[User]
    assignees: List[User]
    requested_reviewers: List[User]
    requested_teams: List[str]
    labels: List[Label]
    milestone: Optional[str]
    commits_url: str
    review_comments_url: str
    comments_url: str
    statuses_url: str
    head: Ref
    base: Ref
    _links: RawDict
    author_association: str
    draft: bool
    merged: Optional[bool]
    mergeable: Optional[bool]
    rebaseable: Optional[bool]
    mergeable_state: Optional[str]
    merged_by: Optional[str]
    comments: Optional[int]
    review_comments: Optional[int]
    maintainer_can_modify: Optional[bool]
    commits: Optional[int]
    additions: Optional[int]
    deletions: Optional[int]
    changed_files: Optional[int]
    auto_merge: Optional[bool]
    active_lock_reason: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.html_url = payload.get("html_url")
        self.diff_url = payload.get("diff_url")
        self.patch_url = payload.get("patch_url")
        self.issue_url = payload.get("issue_url")
        self.number = payload.get("number")
        self.state = payload.get("state")
        self.locked = payload.get("locked")
        self.title = payload.get("title")
        self.user = User(payload.get("user"))
        self.body = payload.get("body")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.closed_at = payload.get("closed_at")
        self.merged_at = payload.get("merged_at")
        self.merge_commit_sha = payload.get("merge_commit_sha")
        self.assignee = _optional(payload, "assignee", User)
        self.assignees = [User(assignee) for assignee in payload.get("assignees")]
        self.requested_reviewers = [
            User(reviewer) for reviewer in payload.get("requested_reviewers")
        ]
        self.requested_teams = payload.get("requested_teams")
        self.labels = [Label(item) for item in payload.get("labels")]
        self.milestone = payload.get("milestone")
        self.commits_url = payload.get("commits_url")
        self.review_comments_url = payload.get("review_comments_url")
        self.comments_url = payload.get("comments_url")
        self.statuses_url = payload.get("statuses_url")
        self.head = Ref(payload.get("head"))
        self.base = Ref(payload.get("base"))
        self._links = RawDict(payload.get("_links"))
        self.author_association = payload.get("author_association")
        self.draft = payload.get("draft")
        self.merged = payload.get("merged")
        self.mergeable = payload.get("mergeable")
        self.rebaseable = payload.get("rebaseable")
        self.mergeable_state = payload.get("mergeable_state")
        self.merged_by = payload.get("merged_by")
        self.comments = payload.get("comments")
        self.review_comments = payload.get("review_comments")
        self.maintainer_can_modify = payload.get("maintainer_can_modify")
        self.commits = payload.get("commits")
        self.additions = payload.get("additions")
        self.deletions = payload.get("deletions")
        self.changed_files = payload.get("changed_files")
        self.auto_merge = payload.get("auto_merge")
        self.active_lock_reason = payload.get("active_lock_reason")

    def review_comment_url(self, number: int = None) -> str:
        return _transform(self.payload["review_comment_url"], locals())

    def __str__(self):
        return f"#{self.number} {self.title}"


class Review(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    user: User
    body: Optional[str]
    commit_id: str
    submitted_at: str
    state: str
    html_url: str
    pull_request_url: str
    author_association: str
    _links: RawDict

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.user = User(payload.get("user"))
        self.body = payload.get("body")
        self.commit_id = payload.get("commit_id")
        self.submitted_at = payload.get("submitted_at")
        self.state = payload.get("state")
        self.html_url = payload.get("html_url")
        self.pull_request_url = payload.get("pull_request_url")
        self.author_association = payload.get("author_association")
        self._links = RawDict(payload.get("_links"))


class VulnerabilityAlert(BaseGithubModel):
    payload: dict
    id: int
    affected_range: str
    affected_package_name: str
    external_reference: str
    external_identifier: str
    fixed_in: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.affected_range = payload.get("affected_range")
        self.affected_package_name = payload.get("affected_package_name")
        self.external_reference = payload.get("external_reference")
        self.external_identifier = payload.get("external_identifier")
        self.fixed_in = payload.get("fixed_in")


class VulnerablePackage(BaseGithubModel):
    payload: dict
    ecosystem: str
    name: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.ecosystem = payload.get("ecosystem")
        self.name = payload.get("name")


class PackageVersionInfo(BaseGithubModel):
    payload: dict
    identifier: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.identifier = payload.get("identifier")


class Vulnerability(BaseGithubModel):
    payload: dict
    package: VulnerablePackage
    severity: str
    vulnerable_version_range: str
    first_patched_version: PackageVersionInfo

    def __init__(self, payload: dict):
        self.payload = payload
        self.package = VulnerablePackage(payload.get("package"))
        self.severity = payload.get("severity")
        self.vulnerable_version_range = payload.get("vulnerable_version_range")
        self.first_patched_version = PackageVersionInfo(
            payload.get("first_patched_version")
        )


class SecurityVulnerabilityIdentifier(BaseGithubModel):
    payload: dict
    value: str
    type: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.value: str = payload.get("value")
        self.type: str = payload.get("type")


class SecurityAdvisoryReference(BaseGithubModel):
    payload: dict
    url: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.url = payload.get("url")


class SecurityAdvisory(BaseGithubModel):
    payload: dict
    ghsa_id: str
    summary: str
    description: str
    severity: str
    identifiers: List[SecurityVulnerabilityIdentifier]
    references: List[SecurityAdvisoryReference]
    published_at: str
    updated_at: str
    withdrawn_at: Optional[str]
    vulnerabilities: List[Vulnerability]

    def __init__(self, payload: dict):
        self.payload = payload
        self.ghsa_id = payload.get("ghsa_id")
        self.summary = payload.get("summary")
        self.description = payload.get("description")
        self.severity = payload.get("severity")
        self.identifiers = [
            SecurityVulnerabilityIdentifier(identifier)
            for identifier in payload.get("identifiers")
        ]
        self.references = [
            SecurityAdvisoryReference(item) for item in payload.get("references")
        ]
        self.published_at = payload.get("published_at")
        self.updated_at = payload.get("updated_at")
        self.withdrawn_at = payload.get("withdrawn_at")
        self.vulnerabilities = [
            Vulnerability(vulnerability)
            for vulnerability in payload.get("vulnerabilities")
        ]


class SponsorshipTier(BaseGithubModel):
    payload: dict
    node_id: str
    created_at: str
    description: str
    monthly_price_in_cents: int
    monthly_price_in_dollars: int
    name: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.node_id = payload.get("node_id")
        self.created_at = payload.get("created_at")
        self.description = payload.get("description")
        self.monthly_price_in_cents = payload.get("monthly_price_in_cents")
        self.monthly_price_in_dollars = payload.get("monthly_price_in_dollars")
        self.name = payload.get("name")


class Sponsorship(BaseGithubModel):
    payload: dict
    node_id: str
    created_at: str
    maintainer: User
    sponsor: User
    privacy_level: str
    tier: SponsorshipTier

    def __init__(self, payload: dict):
        self.payload = payload
        self.node_id = payload.get("node_id")
        self.created_at = payload.get("created_at")
        self.maintainer = User(payload.get("maintainer"))
        self.sponsor = User(payload.get("sponsor"))
        self.privacy_level = payload.get("privacy_level")
        self.tier = SponsorshipTier(payload.get("tier"))


class StatusBranchCommit(BaseGithubModel):
    payload: dict
    sha: str
    url: str
    html_url: Optional[str]

    def __init__(self, payload: dict):
        self.payload = payload
        self.sha = payload.get("sha")
        self.url = payload.get("url")
        self.html_url = payload.get("html_url", None)


class Branch(BaseGithubModel):
    payload: dict
    name: str
    commit: StatusBranchCommit
    protected: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.name = payload.get("name")
        self.commit = StatusBranchCommit(payload.get("commit"))
        self.protected = payload.get("protected")


class StatusCommitVerification(BaseGithubModel):
    payload: dict
    verified: bool
    reason: str
    signature: str
    payload: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.verified = payload.get("verified")
        self.reason = payload.get("reason")
        self.signature = payload.get("signature")
        self.payload = payload.get("payload")


class StatusNestedCommitUser(BaseGithubModel):
    payload: dict
    name: str
    email: str
    date: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.name = payload.get("name")
        self.email = payload.get("email")
        self.date = payload.get("date")


class StatusNestedCommit(BaseGithubModel):
    payload: dict
    author: StatusNestedCommitUser
    committer: StatusNestedCommitUser
    message: str
    tree: StatusBranchCommit
    url: str
    comment_count: int
    verification: StatusCommitVerification

    def __init__(self, payload: dict):
        self.payload = payload
        self.author = StatusNestedCommitUser(payload.get("author"))
        self.committer = StatusNestedCommitUser(payload.get("committer"))
        self.message = payload.get("message")
        self.tree = StatusBranchCommit(payload.get("tree"))
        self.url = payload.get("url")
        self.comment_count = payload.get("comment_count")
        self.verification = StatusCommitVerification(payload.get("verification"))


class StatusCommit(BaseGithubModel):
    payload: dict
    sha: str
    node_id: str
    commit: StatusNestedCommit
    url: str
    html_url: str
    comments_url: str
    author: Optional[User]
    committer: Optional[User]
    parents: List[StatusBranchCommit]

    def __init__(self, payload: dict):
        self.payload = payload
        self.sha = payload.get("sha")
        self.node_id = payload.get("node_id")
        self.commit = StatusNestedCommit(payload.get("commit"))
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.comments_url = payload.get("comments_url")
        self.author = _optional(payload, "author", User)
        self.committer = _optional(payload, "committer", User)
        self.parents = [StatusBranchCommit(parent) for parent in payload.get("parents")]


class ContentReference(BaseGithubModel):
    payload: dict
    id: int
    node_id: str
    reference: str

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.reference = payload.get("reference")


class Rule(BaseGithubModel):
    payload: dict
    id: int
    repository_id: int
    name: str
    created_at: str
    updated_at: str
    pull_request_reviews_enforcement_level: str
    required_approving_review_count: int
    dismiss_stale_reviews_on_push: bool
    require_code_owner_review: bool
    authorized_dismissal_actors_only: bool
    ignore_approvals_from_contributors: bool
    required_status_checks: List[str]
    required_status_checks_enforcement_level: str
    strict_required_status_checks_policy: bool
    signature_requirement_enforcement_level: str
    linear_history_requirement_enforcement_level: str
    admin_enforced: bool
    create_protected: bool
    allow_force_pushes_enforcement_level: str
    allow_deletions_enforcement_level: str
    merge_queue_enforcement_level: str
    required_deployments_enforcement_level: str
    required_conversation_resolution_level: str
    authorized_actors_only: bool
    authorized_actor_names: List[str]
    require_last_push_approval: bool

    def __init__(self, payload: dict):
        self.payload = payload
        self.id = payload.get("id")
        self.repository_id = payload.get("repository_id")
        self.name = payload.get("name")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.pull_request_reviews_enforcement_level = payload.get(
            "pull_request_reviews_enforcement_level"
        )
        self.required_approving_review_count = payload.get(
            "required_approving_review_count"
        )
        self.dismiss_stale_reviews_on_push = payload.get(
            "dismiss_stale_reviews_on_push"
        )
        self.require_code_owner_review = payload.get("require_code_owner_review")
        self.authorized_dismissal_actors_only = payload.get(
            "authorized_dismissal_actors_only"
        )
        self.ignore_approvals_from_contributors = payload.get(
            "ignore_approvals_from_contributors"
        )
        self.required_status_checks = payload.get("required_status_checks")
        self.required_status_checks_enforcement_level = payload.get(
            "required_status_checks_enforcement_level"
        )
        self.strict_required_status_checks_policy = payload.get(
            "strict_required_status_checks_policy"
        )
        self.signature_requirement_enforcement_level = payload.get(
            "signature_requirement_enforcement_level"
        )
        self.linear_history_requirement_enforcement_level = payload.get(
            "linear_history_requirement_enforcement_level"
        )
        self.admin_enforced = payload.get("admin_enforced")
        self.create_protected = payload.get("create_protected")
        self.allow_force_pushes_enforcement_level = payload.get(
            "allow_force_pushes_enforcement_level"
        )
        self.allow_deletions_enforcement_level = payload.get(
            "allow_deletions_enforcement_level"
        )
        self.merge_queue_enforcement_level = payload.get(
            "merge_queue_enforcement_level"
        )
        self.required_deployments_enforcement_level = payload.get(
            "required_deployments_enforcement_level"
        )
        self.required_conversation_resolution_level = payload.get(
            "required_conversation_resolution_level"
        )
        self.authorized_actors_only = payload.get("authorized_actors_only")
        self.authorized_actor_names = payload.get("authorized_actor_names")
        self.require_last_push_approval = payload.get("require_last_push_approval")

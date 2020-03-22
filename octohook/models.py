from typing import TypeVar, Optional

T = TypeVar("T")


def _optional(payload, key, class_type: T) -> Optional[T]:
    if payload.get(key):
        return class_type(payload[key])
    else:
        return None


def _transform(url: str, local_variables):
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


class User:
    def __init__(self, payload: dict):
        self._payload = payload
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

    def following_url(self, other_user: str = None):
        return _transform(self._payload["following_url"], locals())

    def gists_url(self, gist_id: str = None):
        return _transform(self._payload["gists_url"], locals())

    def starred_url(self, owner: str = None, repo: str = None):
        return _transform(self._payload["starred_url"], locals())

    def events_url(self, privacy: str = None):
        return _transform(self._payload["events_url"], locals())


class ShortRepository:
    def __init__(self, payload: dict):
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.full_name = payload.get("full_name")
        self.private = payload.get("private")


class Repository:
    def __init__(self, payload: dict):
        self._payload = payload
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

    def keys_url(self, key_id: str = None):
        return _transform(self._payload["keys_url"], locals())

    def collaborators_url(self, collaborator: str = None):
        return _transform(self._payload["collaborators_url"], locals())

    def issue_events_url(self, number: int = None):
        return _transform(self._payload["issue_events_url"], locals())

    def assignees_url(self, user: str = None):
        return _transform(self._payload["assignees_url"], locals())

    def branches_url(self, branch: str = None):
        return _transform(self._payload["branches_url"], locals())

    def blobs_url(self, sha: str = None):
        return _transform(self._payload["blobs_url"], locals())

    def git_tags_url(self, sha: str = None):
        return _transform(self._payload["git_tags_url"], locals())

    def git_refs_url(self, sha: str = None):
        return _transform(self._payload["git_refs_url"], locals())

    def trees_url(self, sha: str = None):
        return _transform(self._payload["trees_url"], locals())

    def statuses_url(self, sha: str):
        return _transform(self._payload["statuses_url"], locals())

    def commits_url(self, sha: str = None):
        return _transform(self._payload["commits_url"], locals())

    def git_commits_url(self, sha=None):
        return _transform(self._payload["git_commits_url"], locals())

    def comments_url(self, number: int = None):
        return _transform(self._payload["comments_url"], locals())

    def issue_comment_url(self, number: int = None):
        return _transform(self._payload["issue_comment_url"], locals())

    def contents_url(self, path: str):
        return _transform(self._payload["contents_url"].replace("+", ""), locals())

    def compare_url(self, base: str, head: str):
        return _transform(self._payload["compare_url"], locals())

    def archive_url(self, archive_format: str, ref: str = None):
        return _transform(self._payload["archive_url"], locals())

    def issues_url(self, number: str = None):
        return _transform(self._payload["issues_url"], locals())

    def pulls_url(self, number: str = None):
        return _transform(self._payload["pulls_url"], locals())

    def milestones_url(self, number: str = None):
        return _transform(self._payload["milestones_url"], locals())

    def notifications_url(self, params: str = None):
        if params is not None:
            if not params.startswith("?"):
                raise AttributeError("Params must be a query string starting with ?")
        replace_with = params if params else ""
        return self._payload["notifications_url"].replace(
            "{?since,all,participating}", replace_with
        )

    def labels_url(self, name: str = None):
        return _transform(self._payload["labels_url"], locals())

    def releases_url(self, id: str = None):
        return _transform(self._payload["releases_url"], locals())


class Organization:
    def __init__(self, payload):
        self._payload = payload
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

    def members_url(self, member: str = None):
        return _transform(self._payload["members_url"], locals())

    def public_members_url(self, member: str = None):
        return _transform(self._payload["public_members_url"], locals())


class Comment:
    def __init__(self, payload):
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


class ChecksApp:
    def __init__(self, payload):
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


class ChecksPullRequest:
    def __init__(self, payload):
        pass


class CommitUser:
    def __init__(self, payload):
        self.name = payload.get("name")
        self.email = payload.get("email")
        self.username = payload.get("username")


class Commit:
    def __init__(self, payload: dict):
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


class CheckSuite:
    def __init__(self, payload):
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


class CheckRunOutput:
    def __init__(self, payload):
        self.title = payload.get("title")
        self.summary = payload.get("summary")
        self.text = payload.get("text")
        self.annotations_count = payload.get("annotations_count")
        self.annotations_url = payload.get("annotations_url")


class CheckRun:
    def __init__(self, payload):
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


class Permissions:
    def __init__(self, payload):
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


class Installation:
    def __init__(self, payload):
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


class DeployKey:
    def __init__(self, payload):
        self.id = payload.get("id")
        self.key = payload.get("key")
        self.url = payload.get("url")
        self.title = payload.get("title")
        self.verified = payload.get("verified")
        self.created_at = payload.get("created_at")
        self.read_only = payload.get("read_only")


class Deployment:
    def __init__(self, payload):
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


class DeploymentStatus:
    def __init__(self, payload):
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


class Page:
    def __init__(self, payload):
        self.page_name = payload.get("page_name")
        self.title = payload.get("title")
        self.summary = payload.get("summary")
        self.action = payload.get("action")
        self.sha = payload.get("sha")
        self.html_url = payload.get("html_url")


class Label:
    def __init__(self, payload):
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.url = payload.get("url")
        self.name = payload.get("name")
        self.color = payload.get("color")
        self.description = payload.get("description")
        self.default = payload.get("default")


class Milestone:
    def __init__(self, payload):
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


class RawDict(dict):
    def __init__(self, payload):
        super().__init__(payload)


class Issue:
    def __init__(self, payload):
        self._payload = payload
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

    def labels_url(self, name: str = None):
        return _transform(self._payload["labels_url"], locals())


class PurchaseAccount:
    def __init__(self, payload):
        self.type = payload.get("type")
        self.id = payload.get("id")
        self.login = payload.get("login")
        self.organization_billing_email = payload.get("organization_billing_email")


class Plan:
    def __init__(self, payload):
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


class MarketplacePurcahase:
    def __init__(self, payload):
        self.account = PurchaseAccount(payload.get("account"))
        self.billing_cycle = payload.get("billing_cycle")
        self.unit_count = payload.get("unit_count")
        self.on_free_trial = payload.get("on_free_trial")
        self.free_trial_ends_on = payload.get("free_trial_ends_on")
        self.next_billing_date = payload.get("next_billing_date")
        self.plan = Plan(payload.get("plan"))


class Team:
    def __init__(self, payload):
        self._payload = payload
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

    def members_url(self, member: str = None):
        return _transform(self._payload["members_url"], locals())


class Hook:
    def __init__(self, payload):
        self.type = payload.get("type")
        self.id = payload.get("id")
        self.name = payload.get("name")
        self.active = payload.get("active")
        self.events = payload.get("events")
        self.config = RawDict(payload.get("config"))
        self.updated_at = payload.get("updated_at")
        self.created_at = payload.get("created_at")


class Membership:
    def __init__(self, payload):
        self.url = payload.get("url")
        self.state = payload.get("state")
        self.role = payload.get("role")
        self.organization_url = payload.get("organization_url")
        self.user = User(payload.get("user"))


class Release:
    def __init__(self, payload):
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
        self.assets = payload.get("assets", [])
        self.tarball_url = payload.get("tarball_url", None)
        self.zipball_url = payload.get("zipball_url", None)
        self.body = payload.get("body", None)


class PackageFile:
    def __init__(self, payload):
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


class PackageVersion:
    def __init__(self, payload):
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


class Registry:
    def __init__(self, payload):
        self.about_url = payload.get("about_url")
        self.name = payload.get("name")
        self.type = payload.get("type")
        self.url = payload.get("url")
        self.vendor = payload.get("vendor")


class Package:
    def __init__(self, payload):
        self.id = payload.get("id")
        self.name = payload.get("name")
        self.package_type = payload.get("package_type")
        self.html_url = payload.get("html_url")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.owner = User(payload.get("owner"))
        self.package_version = PackageVersion(payload.get("package_version"))
        self.registry = Registry(payload.get("registry"))


class PageBuild:
    def __init__(self, payload):
        self.url = payload.get("url")
        self.status = payload.get("status")
        self.error = RawDict(payload.get("error"))
        self.pusher = User(payload.get("pusher"))
        self.commit = payload.get("commit")
        self.duration = payload.get("duration")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")


class ProjectCard:
    def __init__(self, payload):
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


class ProjectColumn:
    def __init__(self, payload):
        self.url = payload.get("url")
        self.project_url = payload.get("project_url")
        self.cards_url = payload.get("cards_url")
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.name = payload.get("name")
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")
        self.after_id = payload.get("after_id")


class Project:
    def __init__(self, payload):
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


class Ref:
    def __init__(self, payload):
        self.label = payload.get("label")
        self.ref = payload.get("ref")
        self.sha = payload.get("sha")
        self.user = User(payload.get("user"))
        self.repo = Repository(payload.get("repo"))


class PullRequest:
    def __init__(self, payload):
        self._payload = payload
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
        self.requested_reviewers = payload.get("requested_reviewers")
        self.requested_teams = payload.get("requested_teams")
        self.labels = payload.get("labels")
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

    def review_comment_url(self, number: int = None):
        return _transform(self._payload["review_comment_url"], locals())


class Review:
    def __init__(self, payload):
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


class VulnerabilityAlert:
    def __init__(self, payload):
        self.id = payload.get("id")
        self.affected_range = payload.get("affected_range")
        self.affected_package_name = payload.get("affected_package_name")
        self.external_reference = payload.get("external_reference")
        self.external_identifier = payload.get("external_identifier")
        self.fixed_in = payload.get("fixed_in")


class Vulnerability:
    def __init__(self, payload):
        self.package = payload.get("package")
        self.severity = payload.get("severity")
        self.vulnerable_version_range = payload.get("vulnerable_version_range")
        self.first_patched_version = payload.get("first_patched_version")


class SecurityVulnerabilityIdentifier:
    def __init__(self, payload):
        self.value = payload.get("value")
        self.type = payload.get("type")


class SecurityAdvisory:
    def __init__(self, payload):
        self.ghsa_id = payload.get("ghsa_id")
        self.summary = payload.get("summary")
        self.description = payload.get("description")
        self.severity = payload.get("severity")
        self.identifiers = [
            SecurityVulnerabilityIdentifier(identifier)
            for identifier in payload.get("identifiers")
        ]
        self.references = payload.get("references")
        self.published_at = payload.get("published_at")
        self.updated_at = payload.get("updated_at")
        self.withdrawn_at = payload.get("withdrawn_at")
        self.vulnerabilities = [
            Vulnerability(vulnerability)
            for vulnerability in payload.get("vulnerabilities")
        ]


class SponsorshipTier:
    def __init__(self, payload):
        self.node_id = payload.get("node_id")
        self.created_at = payload.get("created_at")
        self.description = payload.get("description")
        self.monthly_price_in_cents = payload.get("monthly_price_in_cents")
        self.monthly_price_in_dollars = payload.get("monthly_price_in_dollars")
        self.name = payload.get("name")


class Sponsorship:
    def __init__(self, payload):
        self.node_id = payload.get("node_id")
        self.created_at = payload.get("created_at")
        self.maintainer = User(payload.get("maintainer"))
        self.sponsor = User(payload.get("sponsor"))
        self.privacy_level = payload.get("privacy_level")
        self.tier = SponsorshipTier(payload.get("tier"))


class StatusBranchCommit:
    def __init__(self, payload):
        self.sha = payload.get("sha")
        self.url = payload.get("url")
        self.html_url = payload.get("html_url", None)


class Branch:
    def __init__(self, payload):
        self.name = payload.get("name")
        self.commit = StatusBranchCommit(payload.get("commit"))
        self.protected = payload.get("protected")


class StatusCommitVerification:
    def __init__(self, payload):
        self.verified = payload.get("verified")
        self.reason = payload.get("reason")
        self.signature = payload.get("signature")
        self.payload = payload.get("payload")


class StatusNestedCommitUser:
    def __init__(self, payload):
        self.name = payload.get("name")
        self.email = payload.get("email")
        self.date = payload.get("date")


class StatusNestedCommit:
    def __init__(self, payload):
        self.author = StatusNestedCommitUser(payload.get("author"))
        self.committer = StatusNestedCommitUser(payload.get("committer"))
        self.message = payload.get("message")
        self.tree = StatusBranchCommit(payload.get("tree"))
        self.url = payload.get("url")
        self.comment_count = payload.get("comment_count")
        self.verification = StatusCommitVerification(payload.get("verification"))


class StatusCommit:
    def __init__(self, payload):
        self.sha = payload.get("sha")
        self.node_id = payload.get("node_id")
        self.commit = StatusNestedCommit(payload.get("commit"))
        self.url = payload.get("url")
        self.html_url = payload.get("html_url")
        self.comments_url = payload.get("comments_url")
        self.author = User(payload.get("author"))
        self.committer = User(payload.get("committer"))
        self.parents = [StatusBranchCommit(parent) for parent in payload.get("parents")]


class ContentReference:
    def __init__(self, payload):
        self.id = payload.get("id")
        self.node_id = payload.get("node_id")
        self.reference = payload.get("reference")

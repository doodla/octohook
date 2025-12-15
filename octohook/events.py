import logging
from enum import Enum
from typing import Optional, List, Any, Annotated

from octohook.models import (
    Repository,
    Organization,
    User,
    Comment,
    CheckRun,
    CheckSuite,
    Installation,
    DeployKey,
    Deployment,
    DeploymentStatus,
    Page,
    ShortRepository,
    Issue,
    Label,
    MarketplacePurchase,
    Team,
    Hook,
    Milestone,
    Membership,
    Package,
    PageBuild,
    ProjectCard,
    ProjectColumn,
    Project,
    PullRequest,
    Review,
    Release,
    VulnerabilityAlert,
    SecurityAdvisory,
    Sponsorship,
    Branch,
    StatusCommit,
    Commit,
    CommitUser,
    _optional,
    ShortInstallation,
    Enterprise,
    Thread,
    Rule,
)

logger = logging.getLogger("octohook")

class BaseWebhookEvent:
    """Base class for all GitHub webhook events.

    Provides common fields present in most webhook payloads: sender, repository,
    organization, and enterprise. Subclasses add event-specific fields.
    """

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


class BranchProtectionRuleEvent(BaseWebhookEvent):
    """Triggered when a branch protection rule is created, edited, or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#branch_protection_rule
    """

    payload: dict
    rule: Rule
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.rule = Rule(payload.get("rule"))
        self.changes = payload.get("changes")


class CheckRunEvent(BaseWebhookEvent):
    """Triggered when a check run is created, rerequested, completed, or has a requested action.

    Check runs are individual CI jobs within a check suite.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#check_run
    """

    check_run: CheckRun

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.check_run = CheckRun(payload.get("check_run"))


class CheckSuiteEvent(BaseWebhookEvent):
    """Triggered when a check suite is completed, requested, or rerequested.

    Check suites group related check runs for a specific commit.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#check_suite
    """

    check_suite: CheckSuite

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.check_suite = CheckSuite(payload.get("check_suite"))


class CommitCommentEvent(BaseWebhookEvent):
    """Triggered when a commit comment is created.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#commit_comment
    """

    comment: Comment

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.comment = Comment(payload.get("comment"))


class CreateEvent(BaseWebhookEvent):
    """Triggered when a branch or tag is created.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#create
    """

    ref: str
    ref_type: str
    master_branch: str
    description: str
    pusher_type: str

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.ref = payload.get("ref")
        self.ref_type = payload.get("ref_type")
        self.master_branch = payload.get("master_branch")
        self.description = payload.get("description")
        self.pusher_type = payload.get("pusher_type")


class DeleteEvent(BaseWebhookEvent):
    """Triggered when a branch or tag is deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#delete
    """

    ref: str
    ref_type: str
    pusher_type: str

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.ref = payload.get("ref")
        self.ref_type = payload.get("ref_type")
        self.pusher_type = payload.get("pusher_type")


class DeployKeyEvent(BaseWebhookEvent):
    """Triggered when a deploy key is created or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#deploy_key
    """

    key: DeployKey

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.key = DeployKey(payload.get("key"))


class DeploymentEvent(BaseWebhookEvent):
    """Triggered when a deployment is created.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#deployment
    """

    deployment: Deployment

    def __init__(self, payload: dict):
        super().__init__(payload)

        self.deployment = Deployment(payload.get("deployment"))


class DeploymentStatusEvent(BaseWebhookEvent):
    """Triggered when a deployment status is created.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#deployment_status
    """

    deployment_status: DeploymentStatus
    deployment: Deployment

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.deployment_status = DeploymentStatus(payload.get("deployment_status"))
        self.deployment = Deployment(payload.get("deployment"))


class ForkEvent(BaseWebhookEvent):
    """Triggered when a user forks a repository.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#fork
    """

    forkee: Repository

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.forkee = Repository(payload.get("forkee"))


class GitHubAppAuthorizationEvent(BaseWebhookEvent):
    """Triggered when a user revokes authorization of a GitHub App.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#github_app_authorization
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class GollumEvent(BaseWebhookEvent):
    """Triggered when a wiki page is created or updated.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#gollum
    """

    pages: List[Page]

    def __init__(self, payload: dict):
        super().__init__(payload)

        self.pages = [Page(page) for page in payload.get("pages")]


class InstallationEvent(BaseWebhookEvent):
    """Triggered when a GitHub App is installed, uninstalled, or has permissions changed.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#installation
    """

    installation: Installation
    repositories: List[ShortRepository]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.installation = Installation(payload.get("installation"))

        self.repositories = [
            ShortRepository(repo) for repo in payload.get("repositories", [])
        ]


class InstallationRepositoriesEvent(BaseWebhookEvent):
    """Triggered when repositories are added or removed from an installation.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#installation_repositories
    """

    installation: Installation
    repository_selection: str
    repositories_added: List[ShortRepository]
    repositories_removed: List[ShortRepository]

    def __init__(self, payload: dict):
        super().__init__(payload)

        self.installation = Installation(payload.get("installation"))
        self.repository_selection = payload.get("repository_selection")
        self.repositories_added = [
            ShortRepository(repo) for repo in payload.get("repositories_added")
        ]
        self.repositories_removed = [
            ShortRepository(repo) for repo in payload.get("repositories_removed")
        ]


class IssueCommentEvent(BaseWebhookEvent):
    """Triggered when an issue or pull request comment is created, edited, or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#issue_comment
    """

    issue: Issue
    comment: Comment
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.comment = Comment(payload.get("comment"))
        self.changes = payload.get("changes")


class IssuesEvent(BaseWebhookEvent):
    """Triggered when an issue is opened, edited, deleted, transferred, pinned, and more.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#issues
    """

    issue: Issue
    changes: Optional[Annotated[dict, "unstructured"]]
    label: Optional[Label]
    assignee: Optional[User]
    milestone: Optional[Milestone]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.changes = payload.get("changes")
        self.label = _optional(payload, "label", Label)
        self.assignee = _optional(payload, "assignee", User)
        self.milestone = _optional(payload, "milestone", Milestone)


class LabelEvent(BaseWebhookEvent):
    """Triggered when a label is created, edited, or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#label
    """

    label: Label
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.label = Label(payload.get("label"))
        self.changes = payload.get("changes")


class MarketplacePurchaseEvent(BaseWebhookEvent):
    """Triggered when a GitHub Marketplace plan is purchased, cancelled, or changed.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#marketplace_purchase
    """

    effective_date: str
    marketplace_purchase: MarketplacePurchase

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.effective_date = payload.get("effective_date")
        self.marketplace_purchase = MarketplacePurchase(
            payload.get("marketplace_purchase")
        )


class MemberEvent(BaseWebhookEvent):
    """Triggered when a user is added or removed as a collaborator to a repository.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#member
    """

    member: User

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.member = User(payload.get("member"))


class MembershipEvent(BaseWebhookEvent):
    """Triggered when a user is added or removed from a team.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#membership
    """

    scope: str
    member: User
    team: Team

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.scope = payload.get("scope")
        self.member = User(payload.get("member"))
        self.team = Team(payload.get("team"))


class MetaEvent(BaseWebhookEvent):
    """Triggered when a webhook is deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#meta
    """

    hook_id: int
    hook: Hook

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.hook_id = payload.get("hook_id")
        self.hook = Hook(payload.get("hook"))


class MilestoneEvent(BaseWebhookEvent):
    """Triggered when a milestone is created, closed, opened, edited, or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#milestone
    """

    milestone: Milestone
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.milestone = Milestone(payload.get("milestone"))
        self.changes = payload.get("changes")


class OrganizationEvent(BaseWebhookEvent):
    """Triggered when an organization is renamed or a user is added, removed, or invited.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#organization
    """

    invitation: Optional[Any]
    membership: Membership

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.invitation = payload.get("invitation")  # TODO: What does this look like?
        self.membership = Membership(payload.get("membership"))


class OrgBlockEvent(BaseWebhookEvent):
    """Triggered when an organization blocks or unblocks a user.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#org_block
    """

    blocked_user: User

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.blocked_user = User(payload.get("blocked_user"))


class PackageEvent(BaseWebhookEvent):
    """Triggered when a GitHub Package is published or updated.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#package
    """

    package: Package

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.package = Package(payload.get("package"))


class PageBuildEvent(BaseWebhookEvent):
    """Triggered when a GitHub Pages build attempt is completed.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#page_build
    """

    id: int
    build: PageBuild

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.id = payload.get("id")
        self.build = PageBuild(payload.get("build"))


class ProjectCardEvent(BaseWebhookEvent):
    """Triggered when a project card is created, edited, moved, converted, or deleted.

    Note: This is for classic Projects. See projects_v2 events for new Projects.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#project_card
    """

    project_card: ProjectCard
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.project_card = ProjectCard(payload.get("project_card"))
        self.changes = payload.get("changes")


class ProjectColumnEvent(BaseWebhookEvent):
    """Triggered when a project column is created, updated, moved, or deleted.

    Note: This is for classic Projects. See projects_v2 events for new Projects.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#project_column
    """

    project_column: ProjectColumn
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.project_column = ProjectColumn(payload.get("project_column"))
        self.changes = payload.get("changes")


class ProjectEvent(BaseWebhookEvent):
    """Triggered when a project is created, updated, closed, reopened, or deleted.

    Note: This is for classic Projects. See projects_v2 events for new Projects.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#project
    """

    project: Project

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.project = Project(payload.get("project"))


class PublicEvent(BaseWebhookEvent):
    """Triggered when a private repository is made public.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#public
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class PullRequestEvent(BaseWebhookEvent):
    """Triggered when a pull request is opened, closed, edited, assigned, and more.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request
    """

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


class PullRequestReviewEvent(BaseWebhookEvent):
    """Triggered when a pull request review is submitted, edited, or dismissed.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request_review
    """

    review: Review
    pull_request: PullRequest
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.review = Review(payload.get("review"))
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.changes = payload.get("changes")


class PullRequestReviewCommentEvent(BaseWebhookEvent):
    """Triggered when a pull request review comment is created, edited, or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request_review_comment
    """

    comment: Comment
    pull_request: PullRequest
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.comment = Comment(payload.get("comment"))
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.changes = payload.get("changes")


class PullRequestReviewThreadEvent(BaseWebhookEvent):
    """Triggered when a pull request review thread is resolved or unresolved.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request_review_thread
    """

    pull_request: PullRequest
    thread: Thread

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.thread = Thread(payload.get("thread"))


class PushEvent(BaseWebhookEvent):
    """Triggered when one or more commits are pushed to a repository branch or tag.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
    """

    ref: str
    before: str
    after: str
    created: bool
    deleted: bool
    forced: bool
    base_ref: Optional[str]
    compare: str
    commits: List[Commit]
    head_commit: Optional[Commit]
    pusher: CommitUser

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.ref = payload.get("ref")
        self.before = payload.get("before")
        self.after = payload.get("after")
        self.created = payload.get("created")
        self.deleted = payload.get("deleted")
        self.forced = payload.get("forced")
        self.base_ref = payload.get("base_ref")
        self.compare = payload.get("compare")
        self.commits = [Commit(commit) for commit in payload.get("commits")]
        self.head_commit = _optional(payload, "head_commit", Commit)
        self.pusher = CommitUser(payload.get("pusher"))


class ReleaseEvent(BaseWebhookEvent):
    """Triggered when a release is published, unpublished, created, edited, or deleted.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#release
    """

    release: Release
    changes: Optional[Annotated[dict, "unstructured"]]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.release = Release(payload.get("release"))
        self.changes = payload.get("changes")


class RepositoryDispatchEvent(BaseWebhookEvent):
    """Triggered when a repository dispatch event is created via the GitHub API.

    Used to trigger workflows or other automation with custom event types.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#repository_dispatch
    """

    branch: str
    client_payload: Annotated[dict, "unstructured"]
    installation: ShortInstallation

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.branch = payload.get("branch")
        self.client_payload = payload.get("client_payload")
        self.installation = ShortInstallation(payload.get("installation"))


class RepositoryEvent(BaseWebhookEvent):
    """Triggered when a repository is created, deleted, archived, unarchived, and more.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#repository
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class RepositoryImportEvent(BaseWebhookEvent):
    """Triggered when a repository import succeeds, fails, or is cancelled.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#repository_import
    """

    status: str

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.status = payload.get("status")


class RepositoryVulnerabilityAlertEvent(BaseWebhookEvent):
    """Triggered when a security vulnerability alert is created, dismissed, or resolved.

    Note: This event is deprecated. Use dependabot_alert instead.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#repository_vulnerability_alert
    """

    alert: VulnerabilityAlert

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.alert = VulnerabilityAlert(payload.get("alert"))


class SecurityAdvisoryEvent:
    """Triggered when a security advisory is published, updated, or withdrawn.

    Note: This event does not inherit from BaseWebhookEvent as it lacks common fields.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#security_advisory
    """

    payload: dict
    action: str
    security_advisory: SecurityAdvisory

    def __init__(self, payload: dict):
        self.payload = payload
        self.action = payload.get("action")
        self.security_advisory = SecurityAdvisory(payload.get("security_advisory"))


class SponsorshipEvent(BaseWebhookEvent):
    """Triggered when a sponsorship is created, cancelled, edited, or has a tier change.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#sponsorship
    """

    sponsorship: Sponsorship
    changes: Optional[Annotated[dict, "unstructured"]]
    effective_date: Optional[str]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.sponsorship = Sponsorship(payload.get("sponsorship"))
        self.changes = payload.get("changes")
        self.effective_date = payload.get("effective_date", None)


class StarEvent(BaseWebhookEvent):
    """Triggered when a user stars or unstars a repository.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#star
    """

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.starred_at = payload.get("starred_at")


class StatusEvent(BaseWebhookEvent):
    """Triggered when a commit status is created or updated.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#status
    """

    id: int
    sha: str
    name: str
    target_url: Optional[str]
    avatar_url: Optional[str]
    context: str
    description: Optional[str]
    state: str
    commit: StatusCommit
    branches: List[Branch]
    created_at: str
    updated_at: str

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.id = payload.get("id")
        self.sha = payload.get("sha")
        self.name = payload.get("name")
        self.target_url = payload.get("target_url")
        self.avatar_url = payload.get("avatar_url")
        self.context = payload.get("context")
        self.description = payload.get("description")
        self.state = payload.get("state")
        self.commit = StatusCommit(payload.get("commit"))
        self.branches = [Branch(branch) for branch in payload.get("branches")]
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")


class TeamEvent(BaseWebhookEvent):
    """Triggered when a team is created, deleted, edited, or has repository access changed.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#team
    """

    team: Team

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.team = Team(payload.get("team"))


class TeamAddEvent(BaseWebhookEvent):
    """Triggered when a repository is added to a team.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#team_add
    """

    team: Team

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.team = Team(payload.get("team"))


class WatchEvent(BaseWebhookEvent):
    """Triggered when a user watches a repository (subscribes to notifications).

    Note: Despite the name, this fires when a user stars a repo. Use StarEvent instead.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#watch
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class PingEvent(BaseWebhookEvent):
    """Triggered when a webhook is created to verify the endpoint is working.

    See Also:
        https://docs.github.com/en/webhooks/webhook-events-and-payloads#ping
    """

    zen: str
    hook_id: int
    hook: Hook

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.zen = payload.get("zen")
        self.hook_id = payload.get("hook_id")
        self.hook = Hook(payload.get("hook"))


class WebhookEvent(Enum):
    """Enumeration of all GitHub webhook event types.

    Use these values with the @hook decorator to specify which events to handle.
    """

    BRANCH_PROTECTION_CONFIGURATION = "branch_protection_configuration"
    BRANCH_PROTECTION_RULE = "branch_protection_rule"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"
    CODE_SCANNING_ALERT = "code_scanning_alert"
    COMMIT_COMMENT = "commit_comment"
    CREATE = "create"
    CUSTOM_PROPERTY = "custom_property"
    CUSTOM_PROPERTY_VALUES = "custom_property_values"
    DELETE = "delete"
    DEPENDABOT_ALERT = "dependabot_alert"
    DEPLOY_KEY = "deploy_key"
    DEPLOYMENT = "deployment"
    DEPLOYMENT_PROTECTION_RULE = "deployment_protection_rule"
    DEPLOYMENT_REVIEW = "deployment_review"
    DEPLOYMENT_STATUS = "deployment_status"
    DISCUSSION = "discussion"
    DISCUSSION_COMMENT = "discussion_comment"
    FORK = "fork"
    GITHUB_APP_AUTHORIZATION = "github_app_authorization"
    GOLLUM = "gollum"
    INSTALLATION = "installation"
    INSTALLATION_REPOSITORIES = "installation_repositories"
    INSTALLATION_TARGET = "installation_target"
    ISSUE_COMMENT = "issue_comment"
    ISSUES = "issues"
    LABEL = "label"
    MARKETPLACE_PURCHASE = "marketplace_purchase"
    MEMBER = "member"
    MEMBERSHIP = "membership"
    MERGE_GROUP = "merge_group"
    META = "meta"
    MILESTONE = "milestone"
    ORG_BLOCK = "org_block"
    ORGANIZATION = "organization"
    PACKAGE = "package"
    PAGE_BUILD = "page_build"
    PERSONAL_ACCESS_TOKEN_REQUEST = "personal_access_token_request"
    PING = "ping"
    PROJECT_CARD = "project_card"
    PROJECT = "project"
    PROJECT_COLUMN = "project_column"
    PROJECTS_V2 = "projects_v2"
    PROJECTS_V2_ITEM = "projects_v2_item"
    PROJECTS_V2_STATUS_UPDATE = "projects_v2_status_update"
    PUBLIC = "public"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_THREAD = "pull_request_review_thread"
    PUSH = "push"
    REGISTRY_PACKAGE = "registry_package"
    RELEASE = "release"
    REPOSITORY_ADVISORY = "repository_advisory"
    REPOSITORY = "repository"
    REPOSITORY_DISPATCH = "repository_dispatch"
    REPOSITORY_IMPORT = "repository_import"
    REPOSITORY_RULESET = "repository_ruleset"
    REPOSITORY_VULNERABILITY_ALERT = "repository_vulnerability_alert"
    SECRET_SCANNING_ALERT = "secret_scanning_alert"
    SECRET_SCANNING_ALERT_LOCATION = "secret_scanning_alert_location"
    SECRET_SCANNING_SCAN = "secret_scanning_scan"
    SECURITY_ADVISORY = "security_advisory"
    SECURITY_AND_ANALYSIS = "security_and_analysis"
    SPONSORSHIP = "sponsorship"
    STAR = "star"
    STATUS = "status"
    SUB_ISSUES = "sub_issues"
    TEAM_ADD = "team_add"
    TEAM = "team"
    WATCH = "watch"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    WORKFLOW_JOB = "workflow_job"
    WORKFLOW_RUN = "workflow_run"


class WebhookEventAction(Enum):
    """Enumeration of common GitHub webhook action types.

    Use these values with the @hook decorator's actions parameter to filter events.
    """

    ADDED = "added"
    ADDED_TO_REPOSITORY = "added_to_repository"
    ARCHIVED = "archived"
    ASSIGNED = "assigned"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    CHANGED = "changed"
    CLOSED = "closed"
    COMPLETED = "completed"
    CONVERTED = "converted"
    CONVERTED_TO_DRAFT = "converted_to_draft"
    CREATE = "create"
    CREATED = "created"
    DELETED = "deleted"
    DEMILESTONED = "demilestoned"
    DISMISS = "dismiss"
    DISMISSED = "dismissed"
    EDITED = "edited"
    LABELED = "labeled"
    LOCKED = "locked"
    MEMBER_ADDED = "member_added"
    MEMBER_INVITED = "member_invited"
    MEMBER_REMOVED = "member_removed"
    MILESTONED = "milestoned"
    MOVED = "moved"
    NEW_PERMISSIONS_ACCEPTED = "new_permissions_accepted"
    ON_DEMAND_TEST = "on-demand-test"
    OPENED = "opened"
    PENDING_CANCELLATION = "pending_cancellation"
    PENDING_CHANGE = "pending_change"
    PENDING_CHANGE_CANCELLED = "pending_change_cancelled"
    PENDING_TIER_CHANGE = "pending_tier_change"
    PERFORMED = "performed"
    PINNED = "pinned"
    PRERELEASED = "prereleased"
    PRIVATIZED = "privatized"
    PUBLICIZED = "publicized"
    PUBLISHED = "published"
    PURCHASED = "purchased"
    READY_FOR_REVIEW = "ready_for_review"
    RELEASED = "released"
    REMOVED = "removed"
    REMOVED_FROM_REPOSITORY = "removed_from_repository"
    RENAMED = "renamed"
    REOPENED = "reopened"
    REREQUESTED = "rerequested"
    RESOLVE = "resolve"
    RESOLVED = "resolved"
    REQUESTED = "requested"
    REQUESTED_ACTION = "requested_action"
    REVIEW_REQUESTED = "review_requested"
    REVIEW_REQUEST_REMOVED = "review_request_removed"
    REVOKED = "revoked"
    STARTED = "started"
    SUBMITTED = "submitted"
    SYNCHRONIZE = "synchronize"
    TIER_CHANGED = "tier_changed"
    TRANSFERRED = "transferred"
    UNARCHIVED = "unarchived"
    UNASSIGNED = "unassigned"
    UNBLOCKED = "unblocked"
    UNLABELED = "unlabeled"
    UNLOCKED = "unlocked"
    UNPINNED = "unpinned"
    UNPUBLISHED = "unpublished"
    UNRESOLVED = "unresolved"
    UPDATED = "updated"


event_map = {
    WebhookEvent.BRANCH_PROTECTION_RULE: BranchProtectionRuleEvent,
    WebhookEvent.CHECK_RUN: CheckRunEvent,
    WebhookEvent.CHECK_SUITE: CheckSuiteEvent,
    WebhookEvent.COMMIT_COMMENT: CommitCommentEvent,
    WebhookEvent.CREATE: CreateEvent,
    WebhookEvent.DELETE: DeleteEvent,
    WebhookEvent.DEPLOY_KEY: DeployKeyEvent,
    WebhookEvent.DEPLOYMENT: DeploymentEvent,
    WebhookEvent.DEPLOYMENT_STATUS: DeploymentStatusEvent,
    WebhookEvent.FORK: ForkEvent,
    WebhookEvent.GITHUB_APP_AUTHORIZATION: GitHubAppAuthorizationEvent,
    WebhookEvent.GOLLUM: GollumEvent,
    WebhookEvent.INSTALLATION: InstallationEvent,
    WebhookEvent.INSTALLATION_REPOSITORIES: InstallationRepositoriesEvent,
    WebhookEvent.ISSUE_COMMENT: IssueCommentEvent,
    WebhookEvent.ISSUES: IssuesEvent,
    WebhookEvent.LABEL: LabelEvent,
    WebhookEvent.MARKETPLACE_PURCHASE: MarketplacePurchaseEvent,
    WebhookEvent.MEMBER: MemberEvent,
    WebhookEvent.MEMBERSHIP: MembershipEvent,
    WebhookEvent.META: MetaEvent,
    WebhookEvent.MILESTONE: MilestoneEvent,
    WebhookEvent.ORG_BLOCK: OrgBlockEvent,
    WebhookEvent.ORGANIZATION: OrganizationEvent,
    WebhookEvent.PACKAGE: PackageEvent,
    WebhookEvent.PAGE_BUILD: PageBuildEvent,
    WebhookEvent.PING: PingEvent,
    WebhookEvent.PROJECT: ProjectEvent,
    WebhookEvent.PUBLIC: PublicEvent,
    WebhookEvent.PULL_REQUEST: PullRequestEvent,
    WebhookEvent.PULL_REQUEST_REVIEW: PullRequestReviewEvent,
    WebhookEvent.PULL_REQUEST_REVIEW_COMMENT: PullRequestReviewCommentEvent,
    WebhookEvent.PULL_REQUEST_REVIEW_THREAD: PullRequestReviewThreadEvent,
    WebhookEvent.PUSH: PushEvent,
    WebhookEvent.PROJECT_CARD: ProjectCardEvent,
    WebhookEvent.PROJECT_COLUMN: ProjectColumnEvent,
    WebhookEvent.RELEASE: ReleaseEvent,
    WebhookEvent.REPOSITORY: RepositoryEvent,
    WebhookEvent.REPOSITORY_DISPATCH: RepositoryDispatchEvent,
    WebhookEvent.REPOSITORY_IMPORT: RepositoryImportEvent,
    WebhookEvent.REPOSITORY_VULNERABILITY_ALERT: RepositoryVulnerabilityAlertEvent,
    WebhookEvent.SECURITY_ADVISORY: SecurityAdvisoryEvent,
    WebhookEvent.SPONSORSHIP: SponsorshipEvent,
    WebhookEvent.STAR: StarEvent,
    WebhookEvent.STATUS: StatusEvent,
    WebhookEvent.TEAM: TeamEvent,
    WebhookEvent.TEAM_ADD: TeamAddEvent,
    WebhookEvent.WATCH: WatchEvent,
}


def parse(event_name, payload: dict):
    """Parse a raw webhook payload into a typed event object.

    Args:
        event_name: The GitHub event name (from the X-GitHub-Event header).
        payload: The raw webhook payload dictionary.

    Returns:
        A typed event object (e.g., PullRequestEvent, IssuesEvent) or
        BaseWebhookEvent if the event type is not recognized.

    Example:
        event = parse("pull_request", request.json)
        if isinstance(event, PullRequestEvent):
            print(event.pull_request.title)
    """
    try:
        return event_map[WebhookEvent(event_name)](payload)
    except Exception:
        logger.exception(f"Could not parse event {event_name}")
        return BaseWebhookEvent(payload)

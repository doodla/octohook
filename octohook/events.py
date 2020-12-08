from enum import Enum
from typing import Optional, List, Any

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
    RawDict,
    ContentReference,
    Commit,
    CommitUser,
    _optional,
    ShortInstallation,
    Enterprise,
)


class BaseWebhookEvent:
    payload: dict
    action: Optional[str] = None
    sender: User
    repository: Optional[Repository] = None
    organization: Optional[Organization] = None
    enterprise: Optional[Enterprise] = None

    def __init__(self, payload: dict):
        self.payload = payload
        self.action = payload.get("action")
        self.sender = User(payload.get("sender"))

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


class CheckRunEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#checkrunevent
    """

    check_run: CheckRun

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.check_run = CheckRun(payload.get("check_run"))


class CheckSuiteEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#checksuiteevent
    """

    check_suite: CheckSuite

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.check_suite = CheckSuite(payload.get("check_suite"))


class CommitCommentEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#commitcommentevent
    """

    comment: Comment

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.comment = Comment(payload.get("comment"))


class ContentReferenceEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#contentreferenceevent
    """

    content_reference: ContentReference
    installation: ShortInstallation

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.content_reference = ContentReference(payload.get("content_reference"))
        self.installation = ShortInstallation(payload.get("installation"))


class CreateEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#createevent
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
    """
    https://developer.github.com/v3/activity/events/types/#deleteevent
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
    """
    https://developer.github.com/v3/activity/events/types/#deploykeyevent
    """

    key: DeployKey

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.key = DeployKey(payload.get("key"))


class DeploymentEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#deploymentevent
    """

    deployment: Deployment

    def __init__(self, payload: dict):
        super().__init__(payload)

        self.deployment = Deployment(payload.get("deployment"))


class DeploymentStatusEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#deploymentstatusevent
    """

    deployment_status: DeploymentStatus
    deployment: Deployment

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.deployment_status = DeploymentStatus(payload.get("deployment_status"))
        self.deployment = Deployment(payload.get("deployment"))


class ForkEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#forkevent
    """

    forkee: Repository

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.forkee = Repository(payload.get("forkee"))


class GitHubAppAuthorizationEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#forkapplyevent
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class GollumEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#gollumevent
    """

    pages: List[Page]

    def __init__(self, payload: dict):
        super().__init__(payload)

        self.pages = [Page(page) for page in payload.get("pages")]


class InstallationEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#installationevent
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
    """
    https://developer.github.com/v3/activity/events/types/#installationrepositoriesevent
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
    """
    https://developer.github.com/v3/activity/events/types/#issuecommentevent
    """

    issue: Issue
    comment: Comment
    changes: Optional[RawDict]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.comment = Comment(payload.get("comment"))
        self.changes = _optional(payload, "changes", RawDict)


class IssuesEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#issuesevent
    """

    issue: Issue
    changes: Optional[RawDict]
    label: Optional[Label]
    assignee: Optional[User]
    milestone: Optional[Milestone]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.changes = _optional(payload, "changes", RawDict)
        self.label = _optional(payload, "label", Label)
        self.assignee = _optional(payload, "assignee", User)
        self.milestone = _optional(payload, "milestone", Milestone)


class LabelEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#labelevent
    """

    label: Label
    changes: Optional[RawDict]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.label = Label(payload.get("label"))
        self.changes = _optional(payload, "changes", RawDict)


class MarketplacePurchaseEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#marketplacepurchaseevent
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
    """
    https://developer.github.com/v3/activity/events/types/#memberevent
    """

    member: User

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.member = User(payload.get("member"))


class MembershipEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#membershipevent
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
    """
    https://developer.github.com/v3/activity/events/types/#metaevent
    """

    hook_id: int
    hook: Hook

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.hook_id = payload.get("hook_id")
        self.hook = Hook(payload.get("hook"))


class MilestoneEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#milestoneevent
    """

    milestone: Milestone
    changes: Optional[RawDict]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.milestone = Milestone(payload.get("milestone"))
        self.changes = _optional(payload, "changes", RawDict)


class OrganizationEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#organizationevent
    """

    invitation: Optional[Any]
    membership: Membership

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.invitation = payload.get("invitation")  # TODO: What does this look like?
        self.membership = Membership(payload.get("membership"))


class OrgBlockEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#orgblockevent
    """

    blocked_user: User

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.blocked_user = User(payload.get("blocked_user"))


class PackageEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#packageevent
    """

    package: Package

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.package = Package(payload.get("package"))


class PageBuildEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pagebuildevent
    """

    id: int
    build: PageBuild

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.id = payload.get("id")
        self.build = PageBuild(payload.get("build"))


class ProjectCardEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#projectcardevent
    """

    project_card: ProjectCard
    changes: Optional[RawDict]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.project_card = ProjectCard(payload.get("project_card"))
        self.changes = _optional(payload, "changes", RawDict)


class ProjectColumnEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#projectcolumnevent
    """

    project_column: ProjectColumn
    changes: Optional[RawDict]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.project_column = ProjectColumn(payload.get("project_column"))
        self.changes = _optional(payload, "changes", RawDict)


class ProjectEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#projectevent
    """

    project: Project

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.project = Project(payload.get("project"))


class PublicEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#publicevent
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class PullRequestEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pullrequestevent
    """

    number: int
    pull_request: PullRequest
    assignee: Optional[User]
    label: Optional[Label]
    changes: Optional[RawDict]
    before: Optional[str]
    after: Optional[str]
    requested_reviewer: Optional[User]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.number = payload.get("number")
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.assignee = _optional(payload, "assignee", User)
        self.label = _optional(payload, "label", Label)
        self.changes = _optional(payload, "changes", RawDict)
        self.before = payload.get("before")
        self.after = payload.get("after")
        self.requested_reviewer = _optional(payload, "requested_reviewer", User)


class PullRequestReviewEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pullrequestreviewevent
    """

    review: Review
    pull_request: PullRequest
    changes: RawDict

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.review = Review(payload.get("review"))
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.changes = RawDict(payload.get("pull_request"))


class PullRequestReviewCommentEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pullrequestreviewcommentevent
    """

    comment: Comment
    pull_request: PullRequest
    changes: Optional[RawDict]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.comment = Comment(payload.get("comment"))
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.changes = _optional(payload, "changes", RawDict)


class PushEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pushevent
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
    """
    https://developer.github.com/v3/activity/events/types/#releaseevent
    """

    release: Release
    changes: RawDict

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.release = Release(payload.get("release"))
        self.changes = RawDict(payload.get("release"))


class RepositoryDispatchEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositorydispatchevent
    """

    branch: str
    client_payload: RawDict
    installation: ShortInstallation

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.branch = payload.get("branch")
        self.client_payload = RawDict(payload.get("client_payload"))
        self.installation = ShortInstallation(payload.get("installation"))


class RepositoryEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositoryevent
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class RepositoryImportEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositoryimportevent
    """

    status: str

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.status = payload.get("status")


class RepositoryVulnerabilityAlertEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositoryvulnerabilityalertevent
    """

    alert: VulnerabilityAlert

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.alert = VulnerabilityAlert(payload.get("alert"))


class SecurityAdvisoryEvent:
    """
    https://developer.github.com/v3/activity/events/types/#securityadvisoryevent
    """

    payload: dict
    action: str
    security_advisory: SecurityAdvisory

    def __init__(self, payload: dict):
        self.payload = payload
        self.action = payload.get("action")
        self.security_advisory = SecurityAdvisory(payload.get("security_advisory"))


class SponsorshipEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#sponsorshipevent
    """

    sponsorship: Sponsorship
    changes: Optional[RawDict]
    effective_date: Optional[str]

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.sponsorship = Sponsorship(payload.get("sponsorship"))
        self.changes = _optional(payload, "changes", RawDict)
        self.effective_date = payload.get("effective_date", None)


class StarEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#starevent
    """

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.starred_at = payload.get("starred_at")


class StatusEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#statusevent
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
    """
    https://developer.github.com/v3/activity/events/types/#teamevent
    """

    team: Team

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.team = Team(payload.get("team"))


class TeamAddEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#teamaddevent
    """

    team: Team

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.team = Team(payload.get("team"))


class WatchEvent(BaseWebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#watchevent
    """

    def __init__(self, payload: dict):
        super().__init__(payload)


class PingEvent(BaseWebhookEvent):
    """
    https://developer.github.com/webhooks/#ping-event
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
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"
    COMMIT_COMMENT = "commit_comment"
    CONTENT_REFERENCE = "content_reference"
    CREATE = "create"
    DELETE = "delete"
    DEPLOY_KEY = "deploy_key"
    DEPLOYMENT = "deployment"
    DEPLOYMENT_STATUS = "deployment_status"
    FORK = "fork"
    GITHUB_APP_AUTHORIZATION = "github_app_authorization"
    GOLLUM = "gollum"
    INSTALLATION = "installation"
    INSTALLATION_REPOSITORIES = "installation_repositories"
    ISSUE_COMMENT = "issue_comment"
    ISSUES = "issues"
    LABEL = "label"
    MARKETPLACE_PURCHASE = "marketplace_purchase"
    MEMBER = "member"
    MEMBERSHIP = "membership"
    META = "meta"
    MILESTONE = "milestone"
    ORG_BLOCK = "org_block"
    ORGANIZATION = "organization"
    PACKAGE = "package"
    PAGE_BUILD = "page_build"
    PING = "ping"
    PROJECT = "project"
    PUBLIC = "public"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    PUSH = "push"
    PROJECT_CARD = "project_card"
    PROJECT_COLUMN = "project_column"
    RELEASE = "release"
    REPOSITORY = "repository"
    REPOSITORY_DISPATCH = "repository_dispatch"
    REPOSITORY_IMPORT = "repository_import"
    REPOSITORY_VULNERABILITY_ALERT = "repository_vulnerability_alert"
    SECURITY_ADVISORY = "security_advisory"
    SPONSORSHIP = "sponsorship"
    STAR = "star"
    STATUS = "status"
    TEAM = "team"
    TEAM_ADD = "team_add"
    WATCH = "watch"


class WebhookEventAction(Enum):
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
    REMOVED = "removed"
    REMOVED_FROM_REPOSITORY = "removed_from_repository"
    RENAMED = "renamed"
    REOPENED = "reopened"
    REREQUESTED = "rerequested"
    RESOLVE = "resolve"
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
    UPDATED = "updated"


event_map = {
    WebhookEvent.CHECK_RUN: CheckRunEvent,
    WebhookEvent.CHECK_SUITE: CheckSuiteEvent,
    WebhookEvent.COMMIT_COMMENT: CommitCommentEvent,
    WebhookEvent.CONTENT_REFERENCE: ContentReferenceEvent,
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
    return event_map[WebhookEvent(event_name)](payload)

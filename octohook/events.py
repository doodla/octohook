from abc import ABC

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
    MarketplacePurcahase,
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
)


class WebhookEvent(ABC):
    def __init__(self, payload: dict):
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


class CheckRunEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#checkrunevent
    """

    event = "check_run"

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.check_run = CheckRun(payload.get("check_run"))


class CheckSuiteEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#checksuiteevent
    """

    event = "check_suite"

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.check_suite = CheckSuite(payload.get("check_suite"))


class CommitCommentEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#commitcommentevent
    """

    event = "commit_comment"

    def __init__(self, payload: dict):
        super().__init__(payload)
        self.comment = Comment(payload.get("comment"))


class ContentReferenceEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#contentreferenceevent
    """

    event = "content_reference"

    def __init__(self, payload):
        super().__init__(payload)
        self.content_reference = ContentReference(payload.get("content_reference"))
        self.installation = Installation(payload.get("installation"))


class CreateEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#createevent
    """

    event = "create"

    def __init__(self, payload):
        super().__init__(payload)
        self.ref = payload.get("ref")
        self.ref_type = payload.get("ref_type")
        self.master_branch = payload.get("master_branch")
        self.description = payload.get("description")
        self.pusher_type = payload.get("pusher_type")


class DeleteEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#deleteevent
    """

    event = "delete"

    def __init__(self, payload):
        super().__init__(payload)
        self.ref = payload.get("ref")
        self.ref_type = payload.get("ref_type")
        self.pusher_type = payload.get("pusher_type")


class DeployKeyEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#deploykeyevent
    """

    event = "deploy_key"

    def __init__(self, payload):
        super().__init__(payload)
        self.key = DeployKey(payload.get("key"))


class DeploymentEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#deploymentevent
    """

    event = "deployment"

    def __init__(self, payload):
        super().__init__(payload)

        self.deployment = Deployment(payload.get("deployment"))


class DeploymentStatusEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#deploymentstatusevent
    """

    event = "deployment_status"

    def __init__(self, payload):
        super().__init__(payload)
        self.deployment_status = DeploymentStatus(payload.get("deployment_status"))
        self.deployment = Deployment(payload.get("deployment"))


class ForkEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#forkevent
    """

    event = "fork"

    def __init__(self, payload):
        super().__init__(payload)
        self.forkee = Repository(payload.get("forkee"))


class GitHubAppAuthorizationEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#forkapplyevent
    """

    event = "github_app_authorization"

    def __init__(self, payload):
        super().__init__(payload)


class GollumEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#gollumevent
    """

    event = "gollum"

    def __init__(self, payload):
        super().__init__(payload)

        self.pages = [Page(page) for page in payload.get("pages")]


class InstallationEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#installationevent
    """

    event = "installation"

    def __init__(self, payload):
        super().__init__(payload)
        self.installation = Installation(payload.get("installation"))

        self.repositories = [
            ShortRepository(repo) for repo in payload.get("repositories")
        ]


class InstallationRepositoriesEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#installationrepositoriesevent
    """

    event = "installation_repositories"

    def __init__(self, payload):
        super().__init__(payload)

        self.installation = Installation(payload.get("installation"))
        self.repository_selection = payload.get("repository_selection")
        self.repositories_added = [
            ShortRepository(repo) for repo in payload.get("repositories_added")
        ]
        self.repositories_removed = [
            ShortRepository(repo) for repo in payload.get("repositories_removed")
        ]


class IssueCommentEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#issuecommentevent
    """

    event = "issue_comment"

    def __init__(self, payload):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.comment = Comment(payload.get("comment"))
        self.changes = _optional(payload, "changes", RawDict)


class IssuesEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#issuesevent
    """

    event = "issues"

    def __init__(self, payload):
        super().__init__(payload)
        self.issue = Issue(payload.get("issue"))
        self.changes = _optional(payload, "changes", RawDict)
        self.label = _optional(payload, "label", Label)
        self.assignee = _optional(payload, "assignee", User)
        self.milestone = _optional(payload, "milestone", Milestone)


class LabelEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#labelevent
    """

    event = "label"

    def __init__(self, payload):
        super().__init__(payload)
        self.label = Label(payload.get("label"))
        self.changes = _optional(payload, "changes", RawDict)


class MarketplacePurchaseEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#marketplacepurchaseevent
    """

    event = "marketplace_purchase"

    def __init__(self, payload):
        super().__init__(payload)
        self.effective_date = payload.get("effective_date")
        self.marketplace_purchase = MarketplacePurcahase(
            payload.get("marketplace_purchase")
        )


class MemberEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#memberevent
    """

    event = "member"

    def __init__(self, payload):
        super().__init__(payload)
        self.member = User(payload.get("member"))


class MembershipEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#membershipevent
    """

    event = "membership"

    def __init__(self, payload):
        super().__init__(payload)
        self.scope = payload.get("scope")
        self.member = User(payload.get("member"))
        self.team = Team(payload.get("team"))


class MetaEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#metaevent
    """

    event = "meta"

    def __init__(self, payload):
        super().__init__(payload)
        self.hook_id = payload.get("hook_id")
        self.hook = Hook(payload.get("hook"))


class MilestoneEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#milestoneevent
    """

    event = "milestone"

    def __init__(self, payload):
        super().__init__(payload)
        self.milestone = Milestone(payload.get("milestone"))
        self.changes = _optional(payload, "changes", RawDict)


class OrganizationEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#organizationevent
    """

    event = "organization"

    def __init__(self, payload):
        super().__init__(payload)
        self.invitation = payload.get("invitation")  # TODO: What does this look like?
        self.membership = Membership(payload.get("membership"))


class OrgBlockEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#orgblockevent
    """

    event = "org_block"

    def __init__(self, payload):
        super().__init__(payload)
        self.blocked_user = User(payload.get("blocked_user"))


class PackageEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#packageevent
    """

    event = "package"

    def __init__(self, payload):
        super().__init__(payload)
        self.package = Package(payload.get("package"))


class PageBuildEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pagebuildevent
    """

    event = "page_build"

    def __init__(self, payload):
        super().__init__(payload)
        self.id = payload.get("id")
        self.build = PageBuild(payload.get("build"))


class ProjectCardEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#projectcardevent
    """

    event = "project_card"

    def __init__(self, payload):
        super().__init__(payload)
        self.project_card = ProjectCard(payload.get("project_card"))
        self.changes = _optional(payload, "changes", RawDict)


class ProjectColumnEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#projectcolumnevent
    """

    event = "project_column"

    def __init__(self, payload):
        super().__init__(payload)
        self.project_column = ProjectColumn(payload.get("project_column"))
        self.changes = _optional(payload, "changes", RawDict)


class ProjectEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#projectevent
    """

    event = "project"

    def __init__(self, payload):
        super().__init__(payload)
        self.project = Project(payload.get("project"))


class PublicEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#publicevent
    """

    event = "public"

    def __init__(self, payload):
        super().__init__(payload)


class PullRequestEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pullrequestevent
    """

    event = "pull_request"

    def __init__(self, payload):
        super().__init__(payload)
        self.number = payload.get("number")
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.assignee = _optional(payload, "assignee", User)
        self.label = _optional(payload, "label", Label)
        self.changes = _optional(payload, "changes", RawDict)
        self.before = payload.get("before")
        self.after = payload.get("after")
        self.requested_reviewer = _optional(payload, "requested_reviewer", User)


class PullRequestReviewEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pullrequestreviewevent
    """

    event = "pull_request_review"

    def __init__(self, payload):
        super().__init__(payload)
        self.review = Review(payload.get("review"))
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.changes = RawDict(payload.get("pull_request"))


class PullRequestReviewCommentEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pullrequestreviewcommentevent
    """

    event = "pull_request_review_comment"

    def __init__(self, payload):
        super().__init__(payload)
        self.comment = Comment(payload.get("comment"))
        self.pull_request = PullRequest(payload.get("pull_request"))
        self.changes = _optional(payload, "changes", RawDict)


class PushEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#pushevent
    """

    event = "push"

    def __init__(self, payload):
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


class ReleaseEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#releaseevent
    """

    event = "release"

    def __init__(self, payload):
        super().__init__(payload)
        self.release = Release(payload.get("release"))
        self.changes = RawDict(payload.get("release"))


class RepositoryDispatchEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositorydispatchevent
    """

    event = "repository_dispatch"

    def __init__(self, payload):
        super().__init__(payload)
        self.branch = payload.get("branch")
        self.client_payload = RawDict(payload.get("client_payload"))
        self.installation = Installation(payload.get("installation"))


class RepositoryEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositoryevent
    """

    event = "repository"

    def __init__(self, payload):
        super().__init__(payload)


class RepositoryImportEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositoryimportevent
    """

    event = "repository_import"

    def __init__(self, payload):
        super().__init__(payload)
        self.status = payload.get("status")


class RepositoryVulnerabilityAlertEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#repositoryvulnerabilityalertevent
    """

    event = "repository_vulnerability_alert"

    def __init__(self, payload):
        super().__init__(payload)
        self.alert = VulnerabilityAlert(payload.get("alert"))


class SecurityAdvisoryEvent:
    """
    https://developer.github.com/v3/activity/events/types/#securityadvisoryevent
    """

    event = "security_advisory"

    def __init__(self, payload):
        self.action = payload.get("action")
        self.security_advisory = SecurityAdvisory(payload.get("security_advisory"))


class SponsorshipEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#sponsorshipevent
    """

    event = "sponsorship"

    def __init__(self, payload):
        super().__init__(payload)
        self.sponsorship = Sponsorship(payload.get("sponsorship"))
        try:
            self.changes = _optional(payload, "changes", RawDict)
            self.effective_date = payload.get("effective_date", None)
        except KeyError:
            pass


class StarEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#starevent
    """

    event = "star"

    def __init__(self, payload):
        super().__init__(payload)
        self.starred_at = payload.get("starred_at")


class StatusEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#statusevent
    """

    event = "status"

    def __init__(self, payload):
        super().__init__(payload)
        self.id = payload.get("id")
        self.sha = payload.get("sha")
        self.name = payload.get("name")
        self.target_url = payload.get("target_url")
        self.context = payload.get("context")
        self.description = payload.get("description")
        self.state = payload.get("state")
        self.commit = StatusCommit(payload.get("commit"))
        self.branches = [Branch(branch) for branch in payload.get("branches")]
        self.created_at = payload.get("created_at")
        self.updated_at = payload.get("updated_at")


class TeamEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#teamevent
    """

    event = "team"

    def __init__(self, payload):
        super().__init__(payload)
        self.team = Team(payload.get("team"))


class TeamAddEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#teamaddevent
    """

    event = "team_add"

    def __init__(self, payload):
        super().__init__(payload)
        self.team = Team(payload.get("team"))


class WatchEvent(WebhookEvent):
    """
    https://developer.github.com/v3/activity/events/types/#watchevent
    """

    event = "watch"

    def __init__(self, payload):
        super().__init__(payload)


class PingEvent(WebhookEvent):
    """
    https://developer.github.com/webhooks/#ping-event
    """

    event = "ping"

    def __init__(self, payload):
        super().__init__(payload)
        self.zen = payload.get("zen")
        self.hook_id = payload.get("hook_id")
        self.hook = Hook(payload.get("hook"))


event_map = {
    PingEvent.event: PingEvent,
    TeamAddEvent.event: TeamAddEvent,
    DeploymentStatusEvent.event: DeploymentStatusEvent,
    DeleteEvent.event: DeleteEvent,
    MilestoneEvent.event: MilestoneEvent,
    DeploymentEvent.event: DeploymentEvent,
    ProjectEvent.event: ProjectEvent,
    IssueCommentEvent.event: IssueCommentEvent,
    PullRequestReviewCommentEvent.event: PullRequestReviewCommentEvent,
    DeployKeyEvent.event: DeployKeyEvent,
    ContentReferenceEvent.event: ContentReferenceEvent,
    ProjectColumnEvent.event: ProjectColumnEvent,
    RepositoryDispatchEvent.event: RepositoryDispatchEvent,
    PushEvent.event: PushEvent,
    GitHubAppAuthorizationEvent.event: GitHubAppAuthorizationEvent,
    PageBuildEvent.event: PageBuildEvent,
    IssuesEvent.event: IssuesEvent,
    CreateEvent.event: CreateEvent,
    PullRequestReviewEvent.event: PullRequestReviewEvent,
    PublicEvent.event: PublicEvent,
    WatchEvent.event: WatchEvent,
    ForkEvent.event: ForkEvent,
    CommitCommentEvent.event: CommitCommentEvent,
    StarEvent.event: StarEvent,
    RepositoryImportEvent.event: RepositoryImportEvent,
    LabelEvent.event: LabelEvent,
    ProjectCardEvent.event: ProjectCardEvent,
    GollumEvent.event: GollumEvent,
    StatusEvent.event: StatusEvent,
    PullRequestEvent.event: PullRequestEvent,
    MetaEvent.event: MetaEvent,
    SponsorshipEvent.event: SponsorshipEvent,
    InstallationEvent.event: InstallationEvent,
    MembershipEvent.event: MembershipEvent,
    MemberEvent.event: MemberEvent,
    RepositoryEvent.event: RepositoryEvent,
    InstallationRepositoriesEvent.event: InstallationRepositoriesEvent,
    ReleaseEvent.event: ReleaseEvent,
    OrgBlockEvent.event: OrgBlockEvent,
    PackageEvent.event: PackageEvent,
    OrganizationEvent.event: OrganizationEvent,
    CheckRunEvent.event: CheckRunEvent,
    RepositoryVulnerabilityAlertEvent.event: RepositoryVulnerabilityAlertEvent,
    TeamEvent.event: TeamEvent,
    CheckSuiteEvent.event: CheckSuiteEvent,
    MarketplacePurchaseEvent.event: MarketplacePurchaseEvent,
    SecurityAdvisoryEvent.event: SecurityAdvisoryEvent,
}


def parse(event_name, payload):
    return event_map[event_name](payload)

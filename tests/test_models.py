import json

import pytest

from flamingo.event_payloads import PushEvent, TeamAddEvent, DeploymentStatusEvent, DeleteEvent, MilestoneEvent, \
    DeploymentEvent, ProjectEvent, IssueCommentEvent, PullRequestReviewCommentEvent, DeployKeyEvent, \
    ContentReferenceEvent, ProjectColumnEvent, RepositoryDispatchEvent, PageBuildEvent, IssuesEvent, \
    GitHubAppAuthorizationEvent, CreateEvent, PullRequestReviewEvent, PublicEvent, WatchEvent, ForkEvent, \
    CommitCommentEvent, StarEvent, RepositoryImportEvent, LabelEvent, ProjectCardEvent, GollumEvent, StatusEvent, \
    PullRequestEvent, MetaEvent, SponsorshipEvent, InstallationEvent, MembershipEvent, MemberEvent, RepositoryEvent, \
    InstallationRepositoriesEvent, ReleaseEvent, OrgBlockEvent, PackageEvent, OrganizationEvent, CheckRunEvent, \
    RepositoryVulnerabilityAlertEvent, TeamEvent, CheckSuiteEvent, MarketplacePurchaseEvent, SecurityAdvisoryEvent

paths = ['fixtures/complete', 'fixtures/incomplete']
testcases = [
    ('team_add', TeamAddEvent),
    ('deployment_status', DeploymentStatusEvent),
    ('delete', DeleteEvent),
    ('milestone', MilestoneEvent),
    ('deployment', DeploymentEvent),
    ('project', ProjectEvent),
    ('issue_comment', IssueCommentEvent),
    ('pull_request_review_comment', PullRequestReviewCommentEvent),
    ('deploy_key', DeployKeyEvent),
    ('content_reference', ContentReferenceEvent),
    ('project_column', ProjectColumnEvent),
    ('repository_dispatch', RepositoryDispatchEvent),
    ('push', PushEvent),
    ('github_app_authorization', GitHubAppAuthorizationEvent),
    ('page_build', PageBuildEvent),
    ('issues', IssuesEvent),
    ('create', CreateEvent),
    ('pull_request_review', PullRequestReviewEvent),
    ('public', PublicEvent),
    ('watch', WatchEvent),
    ('fork', ForkEvent),
    ('commit_comment', CommitCommentEvent),
    ('star', StarEvent),
    ('repository_import', RepositoryImportEvent),
    ('label', LabelEvent),
    ('project_card', ProjectCardEvent),
    ('gollum', GollumEvent),
    ('status', StatusEvent),
    ('pull_request', PullRequestEvent),
    ('meta', MetaEvent),
    ('sponsorship', SponsorshipEvent),
    ('installation', InstallationEvent),
    ('membership', MembershipEvent),
    ('member', MemberEvent),
    ('repository', RepositoryEvent),
    ('installation_repositories', InstallationRepositoriesEvent),
    ('release', ReleaseEvent),
    ('org_block', OrgBlockEvent),
    ('package', PackageEvent),
    ('organization', OrganizationEvent),
    ('check_run', CheckRunEvent),
    ('repository_vulnerability_alert', RepositoryVulnerabilityAlertEvent),
    ('team', TeamEvent),
    ('check_suite', CheckSuiteEvent),
    ('marketplace_purchase', MarketplacePurchaseEvent),
    ('security_advisory', SecurityAdvisoryEvent),
]


@pytest.mark.parametrize('event_name, class_type', testcases)
def test_models_load(event_name, class_type):
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    class_type(example)
        except FileNotFoundError:
            pass

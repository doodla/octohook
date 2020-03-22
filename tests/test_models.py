import json

import pytest

from octohook.models import RawDict
from octohook.events import (
    PushEvent,
    TeamAddEvent,
    DeploymentStatusEvent,
    DeleteEvent,
    MilestoneEvent,
    DeploymentEvent,
    ProjectEvent,
    IssueCommentEvent,
    PullRequestReviewCommentEvent,
    DeployKeyEvent,
    ContentReferenceEvent,
    ProjectColumnEvent,
    RepositoryDispatchEvent,
    PageBuildEvent,
    IssuesEvent,
    GitHubAppAuthorizationEvent,
    CreateEvent,
    PullRequestReviewEvent,
    PublicEvent,
    WatchEvent,
    ForkEvent,
    CommitCommentEvent,
    StarEvent,
    RepositoryImportEvent,
    LabelEvent,
    ProjectCardEvent,
    GollumEvent,
    StatusEvent,
    PullRequestEvent,
    MetaEvent,
    SponsorshipEvent,
    InstallationEvent,
    MembershipEvent,
    MemberEvent,
    RepositoryEvent,
    InstallationRepositoriesEvent,
    ReleaseEvent,
    OrgBlockEvent,
    PackageEvent,
    OrganizationEvent,
    CheckRunEvent,
    RepositoryVulnerabilityAlertEvent,
    TeamEvent,
    CheckSuiteEvent,
    MarketplacePurchaseEvent,
    SecurityAdvisoryEvent,
)

paths = ["tests/fixtures/complete", "tests/fixtures/incomplete"]
testcases = [
    ("team_add", TeamAddEvent),
    ("deployment_status", DeploymentStatusEvent),
    ("delete", DeleteEvent),
    ("milestone", MilestoneEvent),
    ("deployment", DeploymentEvent),
    ("project", ProjectEvent),
    ("issue_comment", IssueCommentEvent),
    ("pull_request_review_comment", PullRequestReviewCommentEvent),
    ("deploy_key", DeployKeyEvent),
    ("content_reference", ContentReferenceEvent),
    ("project_column", ProjectColumnEvent),
    ("repository_dispatch", RepositoryDispatchEvent),
    ("push", PushEvent),
    ("github_app_authorization", GitHubAppAuthorizationEvent),
    ("page_build", PageBuildEvent),
    ("issues", IssuesEvent),
    ("create", CreateEvent),
    ("pull_request_review", PullRequestReviewEvent),
    ("public", PublicEvent),
    ("watch", WatchEvent),
    ("fork", ForkEvent),
    ("commit_comment", CommitCommentEvent),
    ("star", StarEvent),
    ("repository_import", RepositoryImportEvent),
    ("label", LabelEvent),
    ("project_card", ProjectCardEvent),
    ("gollum", GollumEvent),
    ("status", StatusEvent),
    ("pull_request", PullRequestEvent),
    ("meta", MetaEvent),
    ("sponsorship", SponsorshipEvent),
    ("installation", InstallationEvent),
    ("membership", MembershipEvent),
    ("member", MemberEvent),
    ("repository", RepositoryEvent),
    ("installation_repositories", InstallationRepositoriesEvent),
    ("release", ReleaseEvent),
    ("org_block", OrgBlockEvent),
    ("package", PackageEvent),
    ("organization", OrganizationEvent),
    ("check_run", CheckRunEvent),
    ("repository_vulnerability_alert", RepositoryVulnerabilityAlertEvent),
    ("team", TeamEvent),
    ("check_suite", CheckSuiteEvent),
    ("marketplace_purchase", MarketplacePurchaseEvent),
    ("security_advisory", SecurityAdvisoryEvent),
]


@pytest.mark.parametrize("event_name, class_type", testcases)
def test_model_loads(event_name, class_type):
    path_failures = 0
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    class_type(example)
        except FileNotFoundError:
            path_failures += 1

    if path_failures == 2:
        raise FileNotFoundError("The test fixtures were not loaded properly")


def validate_model(data, obj):
    """
    Checks if every key in the json is represented either as a RawDict or a nested object.
    :param data: The JSON dictionary
    :param obj: The Class Object for the dictionary
    """
    for key in data:
        json_value = data[key]
        try:
            obj_value = getattr(obj, key)
        except AttributeError:
            obj_value = getattr(obj, key, None)

            if not callable(obj_value):
                raise AttributeError(f"Couldn't find function or attribute for {key}")

        if not isinstance(obj_value, RawDict) and isinstance(json_value, dict):
            if isinstance(obj_value, dict):
                raise AttributeError(f"Object is a plain dictionary for {key}")
            else:
                validate_model(json_value, obj_value)

        # Validate the values
        if json_value is None or (
            isinstance(json_value, str) and not callable(obj_value)
        ):
            assert json_value == obj_value


@pytest.mark.parametrize("event_name, class_type", testcases)
def test_validate_models(event_name, class_type):
    path_failures = 0
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    validate_model(example, class_type(example))
        except FileNotFoundError:
            path_failures += 1

    if path_failures == 2:
        raise FileNotFoundError("The test fixtures were not loaded properly")

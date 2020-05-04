import json

import pytest

from octohook.events import parse
from octohook.models import RawDict

paths = ["tests/fixtures/complete", "tests/fixtures/incomplete"]
testcases = [
    "team_add",
    "deployment_status",
    "delete",
    "milestone",
    "deployment",
    "project",
    "issue_comment",
    "pull_request_review_comment",
    "deploy_key",
    "content_reference",
    "project_column",
    "repository_dispatch",
    "push",
    "github_app_authorization",
    "page_build",
    "issues",
    "create",
    "pull_request_review",
    "public",
    "watch",
    "fork",
    "commit_comment",
    "star",
    "repository_import",
    "label",
    "project_card",
    "gollum",
    "status",
    "pull_request",
    "meta",
    "sponsorship",
    "installation",
    "membership",
    "member",
    "repository",
    "installation_repositories",
    "release",
    "org_block",
    "package",
    "organization",
    "check_run",
    "repository_vulnerability_alert",
    "team",
    "check_suite",
    "marketplace_purchase",
    "security_advisory",
]


@pytest.mark.parametrize("event_name", testcases)
def test_model_loads(event_name):
    path_failures = 0
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    parse(event_name, example)
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

        # When the nested object is another dictionary
        if not isinstance(obj_value, RawDict) and isinstance(json_value, dict):
            if isinstance(obj_value, dict):
                raise AttributeError(f"Object is a plain dictionary for {key}")
            else:
                validate_model(json_value, obj_value)

        # When the nested object is a list of objects
        if isinstance(json_value, list):
            for item_json, item_obj in zip(json_value, obj_value):
                if isinstance(item_json, dict):
                    validate_model(item_json, item_obj)
                else:
                    assert item_json == item_obj

        # Validate the values
        if json_value is None or (
            isinstance(json_value, str) and not callable(obj_value)
        ):
            assert json_value == obj_value


@pytest.mark.parametrize("event_name", testcases)
def test_validate_models(event_name):
    path_failures = 0
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    validate_model(example, parse(event_name, example))
        except FileNotFoundError:
            path_failures += 1

    if path_failures == 2:
        raise FileNotFoundError("The test fixtures were not loaded properly")

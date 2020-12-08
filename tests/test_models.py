import json
import os
from typing import get_type_hints, get_origin, get_args

import pytest

from octohook.events import parse, WebhookEventAction
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


class TypeHintError(Exception):
    pass


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


def check_model(data, obj):
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
                check_model(json_value, obj_value)

        # When the nested object is a list of objects
        if isinstance(json_value, list):
            for item_json, item_obj in zip(json_value, obj_value):
                if isinstance(item_json, dict):
                    check_model(item_json, item_obj)
                else:
                    assert item_json == item_obj

        # Validate the values
        if json_value is None or (
            isinstance(json_value, str) and not callable(obj_value)
        ):
            assert json_value == obj_value


@pytest.mark.parametrize("event_name", testcases)
def test_model_has_all_keys_in_json(event_name):
    path_failures = 0
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    check_model(example, parse(event_name, example))
        except FileNotFoundError:
            path_failures += 1

    if path_failures == 2:
        raise FileNotFoundError("The test fixtures were not loaded properly")


@pytest.mark.parametrize("path", paths)
def test_all_event_actions_are_in_enum(path):
    actions = []
    for file in os.listdir(path):
        with open(f"{path}/{file}") as f:
            actions.extend(
                [
                    event["action"]
                    for event in json.load(f)
                    if event.get("action") is not None
                ]
            )

    for action in actions:
        WebhookEventAction(action)


def check_type_hints(obj):
    primitives = [str, int, type(None), bool, RawDict]
    hints = get_type_hints(type(obj))

    assert "payload" in hints.keys()
    for attr, type_hint in hints.items():
        if attr == "payload":
            continue
        obj_value = getattr(obj, attr)

        try:
            if isinstance(obj_value, type_hint):
                if type_hint not in primitives:
                    check_type_hints(obj_value)
            else:
                raise TypeHintError(
                    f"{type(obj)} {attr}. Expected {type_hint} Received {type(obj_value)}"
                )
        except TypeError:
            origin = get_origin(type_hint)
            args = get_args(type_hint)

            if type(obj_value) not in args:
                if type(obj_value) != origin:
                    raise TypeHintError(
                        f"{type(obj)} {attr}. Expected {type_hint} Received {type(obj_value)}"
                    )
                elif type(obj_value) == list:
                    try:
                        first_value = obj_value.pop()
                        if type(first_value) != args[0]:
                            raise TypeHintError(
                                f"{type(obj)} {attr}. Expected {type_hint} Received {origin}[{type(first_value)}]"
                            )
                    except IndexError:
                        pass


@pytest.mark.parametrize("event_name", testcases)
def test_all_type_hints_are_correct(event_name):
    path_failures = 0
    for path in paths:
        try:
            with open(f"{path}/{event_name}.json") as file:
                examples = json.load(file)

                for example in examples:
                    check_type_hints(parse(event_name, example))
        except FileNotFoundError:
            path_failures += 1

    if path_failures == 2:
        raise FileNotFoundError("The test fixtures were not loaded properly")

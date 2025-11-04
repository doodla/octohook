import json
import os
from typing import get_type_hints, get_origin, get_args

import pytest

from octohook.events import parse, WebhookEventAction, BaseWebhookEvent
from octohook.models import RawDict
from tests.conftest import discover_fixtures

paths = ["tests/fixtures/complete", "tests/fixtures/incomplete"]

# Auto-discovered from fixture files using shared utility
testcases = discover_fixtures()


class TypeHintError(Exception):
    pass


@pytest.mark.parametrize("event_name", testcases)
def test_model_loads(event_name, fixture_loader):
    """
    Verify that parse() correctly instantiates event models from fixtures.

    Tests that all webhook event fixtures can be successfully parsed into
    their corresponding event model classes without errors.
    """
    examples = fixture_loader.load(event_name)
    for example in examples:
        parse(event_name, example)


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
def test_model_has_all_keys_in_json(event_name, fixture_loader):
    """
    Verify that every JSON key from GitHub is accessible in the parsed object.

    Tests that no data is lost during parsing - every key in the GitHub webhook
    payload must be present either as a direct attribute, nested object, or RawDict.
    This ensures users can access all webhook data without information loss.
    """
    examples = fixture_loader.load(event_name)
    for example in examples:
        check_model(example, parse(event_name, example))


@pytest.mark.parametrize("path", paths)
def test_all_event_actions_are_in_enum(path):
    """
    Verify that all action values in fixtures are defined in WebhookEventAction enum.

    Tests that every action string found in the webhook fixtures corresponds to
    a valid WebhookEventAction enum value. This ensures the enum is kept up-to-date
    with GitHub's webhook actions.
    """
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
                if type_hint not in primitives and type(None) not in get_args(type_hint):
                    check_type_hints(obj_value)
            else:
                raise TypeHintError(
                    f"{type(obj)} {attr}. Expected {type_hint} Received {type(obj_value)}"
                )
        except TypeError:
            origin = get_origin(type_hint)
            args = get_args(type_hint)

            if type(obj_value) not in args:
                if type(obj_value) is not origin:
                    raise TypeHintError(
                        f"{type(obj)} {attr}. Expected {type_hint} Received {type(obj_value)}"
                    )
                elif type(obj_value) is list:
                    try:
                        first_value = obj_value.pop()
                        if type(first_value) is not args[0]:
                            raise TypeHintError(
                                f"{type(obj)} {attr}. Expected {type_hint} Received {origin}[{type(first_value)}]"
                            )
                    except IndexError:
                        pass


@pytest.mark.parametrize("event_name", testcases)
def test_all_type_hints_are_correct(event_name, fixture_loader):
    """
    Verify that type hints match actual runtime types.

    Tests that all type annotations on model classes accurately reflect the
    actual types of the attributes at runtime. This ensures IDE autocomplete,
    type checkers like mypy, and other tooling work correctly.
    """
    examples = fixture_loader.load(event_name)
    for example in examples:
        check_type_hints(parse(event_name, example))


def test_missing_models_return_basewebhookevent():
    """
    Verify that events without specific model classes fall back to BaseWebhookEvent.

    Tests that when a webhook event doesn't have a dedicated event class defined,
    the parse() function gracefully falls back to returning a BaseWebhookEvent
    instance instead of raising an error.
    """
    with open("tests/fixtures/incomplete/code_scanning_alert.json") as file:
        payload = json.load(file)[0]

        assert isinstance(parse("code_scanning_alert", payload), BaseWebhookEvent)

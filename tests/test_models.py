import json
import os
from typing import get_type_hints, get_origin, get_args, Annotated, Union

import pytest

from octohook.events import parse, WebhookEventAction, BaseWebhookEvent
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
    Checks if every key in the json is represented either as an Annotated[dict, "unstructured"] or a nested object.

    This enforces that all dicts are intentionally marked as unstructured, preventing accidental
    use of plain dicts where model classes should exist.

    :param data: The JSON dictionary
    :param obj: The Class Object for the dictionary
    """
    # Get type hints with annotations preserved
    hints = get_type_hints(type(obj), include_extras=True)

    for key in data:
        json_value = data[key]
        try:
            obj_value = getattr(obj, key)
        except AttributeError:
            obj_value = getattr(obj, key, None)

            if not callable(obj_value):
                raise AttributeError(f"Couldn't find function or attribute for {key}")

        # When the nested object is another dictionary
        if isinstance(json_value, dict):
            type_hint = hints.get(key)

            if _is_unstructured_dict(type_hint):
                # Intentionally unstructured - skip validation
                continue
            elif isinstance(obj_value, dict):
                # Plain dict without "unstructured" annotation - ERROR!
                raise AttributeError(
                    f"Plain dict for '{key}' in {type(obj).__name__} - "
                    f"should be a model class or Annotated[dict, 'unstructured']"
                )
            else:
                # It's a model class - recursively validate
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


def _unwrap_annotated(type_hint):
    """
    Extract the actual type from Annotated and Optional wrappers.

    Handles:
    - Annotated[T, ...] -> T
    - Optional[Annotated[T, ...]] -> T
    - Optional[T] -> T
    - T -> T

    Args:
        type_hint: Type hint to unwrap

    Returns:
        The unwrapped type, or the original if not wrapped
    """
    origin = get_origin(type_hint)

    # Handle Optional/Union - extract non-None type
    if origin is Union:
        args = get_args(type_hint)
        for arg in args:
            if arg is not type(None):
                # Recursively unwrap in case it's Optional[Annotated[...]]
                return _unwrap_annotated(arg)

    # Handle Annotated - extract the actual type
    if origin is Annotated:
        args = get_args(type_hint)
        return args[0]

    return type_hint


def _is_unstructured_dict(type_hint) -> bool:
    """
    Check if a type hint is Annotated[dict, "unstructured"].

    Handles both direct annotation and Optional[Annotated[dict, "unstructured"]].

    Args:
        type_hint: Type hint to check

    Returns:
        bool: True if it's an unstructured dict annotation
    """
    origin = get_origin(type_hint)

    # Handle Optional[Annotated[dict, "unstructured"]]
    if origin is Union:
        args = get_args(type_hint)
        # Check non-None args
        for arg in args:
            if arg is not type(None):
                return _is_unstructured_dict(arg)

    # Check if it's Annotated[dict, "unstructured"]
    if origin is Annotated:
        args = get_args(type_hint)
        # First arg is the actual type, rest are metadata
        return args[0] is dict and "unstructured" in args[1:]

    return False


def _is_primitive_type(type_hint):
    """
    Check if a type hint represents a primitive type.

    Args:
        type_hint: Type hint to check

    Returns:
        bool: True if the type is primitive (str, int, None, bool, or Annotated[dict, "unstructured"])
    """
    primitives = [str, int, type(None), bool]
    if type_hint in primitives:
        return True
    # Also treat unstructured dicts as primitives
    return _is_unstructured_dict(type_hint)


def _validate_simple_type(obj, attr, type_hint, obj_value):
    """
    Validate that an attribute's value matches its simple type hint.

    Args:
        obj: The object being validated
        attr: The attribute name
        type_hint: Expected type hint
        obj_value: Actual value of the attribute

    Raises:
        TypeHintError: If the type doesn't match
    """
    # Handle None values for Optional types
    if obj_value is None and type(None) in get_args(type_hint):
        return  # None is valid for Optional types

    # Extract actual type from Annotated/Optional wrappers
    check_type = _unwrap_annotated(type_hint)

    if isinstance(obj_value, check_type):
        # Recursively validate nested objects (non-primitives without None in Union)
        # Example: For PullRequest type, recursively validate its nested User objects
        # Skip primitives (str, int, etc.) and Optional types (which include None)
        if not _is_primitive_type(type_hint) and type(None) not in get_args(type_hint):
            check_type_hints(obj_value)
    else:
        raise TypeHintError(
            f"{type(obj)} {attr}. Expected {type_hint} Received {type(obj_value)}"
        )


def _validate_list_items(obj, attr, type_hint, obj_value, origin, args):
    """
    Validate items in a list match the expected type.

    Args:
        obj: The object being validated
        attr: The attribute name
        type_hint: Expected type hint
        obj_value: The list to validate
        origin: Origin type (e.g., list)
        args: Type arguments (e.g., [str] for List[str])

    Raises:
        TypeHintError: If list items don't match expected type
    """
    if not obj_value:  # Empty list is valid
        return

    # Check first item (non-destructive - use indexing)
    # No need for try/except since we already checked for empty list
    first_value = obj_value[0]
    if type(first_value) is not args[0]:
        raise TypeHintError(
            f"{type(obj)} {attr}. Expected {type_hint} Received {origin}[{type(first_value)}]"
        )


def _validate_complex_type(obj, attr, type_hint, obj_value):
    """
    Validate that an attribute's value matches its complex type hint.

    Handles Union types, List types, and other generic types.

    Args:
        obj: The object being validated
        attr: The attribute name
        type_hint: Expected type hint (e.g., Optional[str], List[int])
        obj_value: Actual value of the attribute

    Raises:
        TypeHintError: If the type doesn't match
    """
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Check if the actual type is one of the Union args (e.g., Optional[X] = Union[X, None])
    if type(obj_value) not in args:
        # Check if the origin type matches (e.g., list)
        if type(obj_value) is not origin:
            raise TypeHintError(
                f"{type(obj)} {attr}. Expected {type_hint} Received {type(obj_value)}"
            )
        # For lists, validate the items
        elif type(obj_value) is list:
            _validate_list_items(obj, attr, type_hint, obj_value, origin, args)


def check_type_hints(obj):
    """
    Recursively validate that all type hints on an object match actual runtime types.

    This ensures that type annotations accurately reflect the actual types at runtime,
    which is critical for IDE autocomplete, type checkers, and documentation.

    Args:
        obj: The object to validate (typically a parsed webhook event)

    Raises:
        TypeHintError: If any type hint doesn't match the actual runtime type
        AssertionError: If the object doesn't have a 'payload' attribute
    """
    hints = get_type_hints(type(obj), include_extras=True)

    # All webhook objects should have a payload attribute
    assert "payload" in hints.keys()

    for attr, type_hint in hints.items():
        if attr == "payload":
            continue

        obj_value = getattr(obj, attr)

        try:
            # Try simple type validation first
            _validate_simple_type(obj, attr, type_hint, obj_value)
        except TypeError:
            # TypeError means we have a complex type (Union, List, etc.)
            _validate_complex_type(obj, attr, type_hint, obj_value)


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


def test_unannotated_dict_enforcement():
    """
    Verify that check_model enforces Annotated[dict, "unstructured"] requirement.

    Tests that using a plain dict without the annotation raises an AttributeError,
    preventing accidental use of unstructured data where model classes should exist.
    """
    from octohook.models import BaseGithubModel

    # Create a test model with a plain dict field (missing annotation)
    class BadModel(BaseGithubModel):
        payload: dict
        bad_field: dict  # This should be Annotated[dict, "unstructured"]

        def __init__(self, payload: dict):
            self.payload = payload
            self.bad_field = payload.get("bad_field")

    test_payload = {"bad_field": {"key": "value"}}
    obj = BadModel(test_payload)

    # This should raise an error because bad_field is a plain dict without annotation
    with pytest.raises(
        AttributeError,
        match="Plain dict for 'bad_field' in BadModel - should be a model class or Annotated",
    ):
        check_model(test_payload, obj)

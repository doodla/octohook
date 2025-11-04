import io
import json
import sys
from contextlib import redirect_stdout

import octohook.decorators
from octohook import load_hooks
from octohook.decorators import _WebhookDecorator
from octohook.events import WebhookEvent, WebhookEventAction

ANY_REPO = "*"
ANY_ACTION = "*"

# Expected hook counts for test fixture modules
# tests/hooks contains:
#   - debug_hooks/label.py: 4 hooks (2 debug, 2 normal)
#   - handle_hooks/label.py: 4 hooks
#   - handle_hooks/inner/label.py: 4 hooks
#   - handle_hooks/pull_request_review_event.py: 4 hooks
#   - handle_hooks/inner/pull_request_review_event.py: 4 hooks
#   - repo_hooks/pull_request_review_event.py: 2 hooks (repository-specific)
EXPECTED_TOTAL_HOOKS = 22
EXPECTED_DEBUG_HOOKS_ONLY = 4
EXPECTED_HANDLE_HOOKS_ONLY = 18  # Total hooks excluding debug_hooks module


def setup_function():
    octohook._imported_modules = []


def teardown_function():
    octohook._loaded = False

    for module in octohook._imported_modules:
        try:
            sys.modules.pop(module)
        except KeyError:
            pass

    octohook._imported_modules = list()


def test_load_hooks_calls_hook(mocker):
    """
    Verify that load_hooks() correctly discovers and registers all hooks in test modules.

    The tests/hooks directory contains 22 total hooks across 6 files. This test
    ensures all are discovered when load_hooks() is called with the parent module.
    """
    mock = mocker.patch("octohook.decorators.hook")

    load_hooks(["tests.hooks"])

    assert mock.call_count == EXPECTED_TOTAL_HOOKS

def test_load_hooks_only_parses_specified_modules(mocker):
    """
    Verify that load_hooks() only loads hooks from specified modules.

    Tests that when a specific submodule is provided (e.g., tests.hooks.debug_hooks),
    only hooks from that module are loaded, not from sibling or parent modules.
    """
    mock = mocker.patch("octohook.decorators.hook")

    load_hooks(["tests.hooks.debug_hooks"])

    assert mock.call_count == EXPECTED_DEBUG_HOOKS_ONLY

def test_load_hooks_parses_python_module(mocker):
    """
    Verify that load_hooks() can load a single Python module file.

    Tests that load_hooks() works with fully-qualified module paths pointing
    to individual Python files, not just packages.
    """
    mock = mocker.patch("octohook.decorators.hook")

    load_hooks(["tests.hooks.debug_hooks.label"])

    assert mock.call_count == EXPECTED_DEBUG_HOOKS_ONLY

def test_load_hooks_parses_properly(mocker):
    """
    Verify that hooks are correctly organized in the three-level filtering structure.

    Tests the internal handler storage structure: event → action → repo → handlers.
    This ensures the filtering system (specific action + specific repo, wildcard action,
    wildcard repo, etc.) is set up correctly after load_hooks() runs.
    """
    decorator = _WebhookDecorator()
    mocker.patch("octohook.decorators.hook", side_effect=decorator.webhook)

    load_hooks(["tests.hooks"])

    handlers = decorator.handlers

    label = handlers[WebhookEvent.LABEL]
    review = handlers[WebhookEvent.PULL_REQUEST_REVIEW]

    assert len(handlers) == 2

    # LabelEvent
    assert len(label) == 5  # (*, created, edited, deleted and debug)
    assert len(label[ANY_ACTION][ANY_REPO]) == 6
    assert len(label[WebhookEventAction.CREATED][ANY_REPO]) == 4
    assert len(label[WebhookEventAction.EDITED][ANY_REPO]) == 6
    assert len(label[WebhookEventAction.DELETED][ANY_REPO]) == 4

    # PullRequestReviewEvent
    assert len(review) == 4
    assert len(review[ANY_ACTION][ANY_REPO]) == 2
    assert len(review[WebhookEventAction.SUBMITTED][ANY_REPO]) == 4
    assert len(review[WebhookEventAction.EDITED][ANY_REPO]) == 3
    assert len(review[WebhookEventAction.DISMISSED][ANY_REPO]) == 3
    assert len(review[WebhookEventAction.DISMISSED]["doodla/octohook-playground"]) == 1
    assert len(review[WebhookEventAction.SUBMITTED]["doodla/octohook-playground2"]) == 1


def test_calling_load_hooks_multiple_times_does_not_have_side_effects(mocker):
    """
    Verify that calling load_hooks() multiple times doesn't register hooks multiple times.

    Tests that load_hooks() is idempotent - calling it repeatedly with the same
    modules doesn't result in duplicate hook registrations or other side effects.
    """
    mock = mocker.patch("octohook.decorators.hook")

    load_hooks(["tests.hooks"])
    load_hooks(["tests.hooks"])
    load_hooks(["tests.hooks"])

    assert mock.call_count == EXPECTED_TOTAL_HOOKS


def test_handle_hooks(mocker):
    """
    Verify that the correct handlers fire for webhook events based on action filtering.

    Tests that handle_webhook() correctly dispatches to registered handlers based on
    the webhook's action. Verifies that:
    - Handlers registered for specific actions only fire for those actions
    - Wildcard handlers (ANY_ACTION) fire for all actions
    - All matching handlers fire (no short-circuiting)
    - Each handler fires exactly once (no duplicates)
    """
    decorator = _WebhookDecorator()
    mocker.patch("octohook.decorators.hook", side_effect=decorator.webhook)

    load_hooks(["tests.hooks.handle_hooks"])

    assertions = {
        WebhookEvent.LABEL: {
            WebhookEventAction.EDITED: {
                "label a",
                "label b",
                "label c",
                "label d",
                "inner label a",
                "inner label b",
                "inner label c",
                "inner label d",
            },
            WebhookEventAction.CREATED: {
                "inner label a",
                "inner label c",
                "inner label d",
                "label a",
                "label c",
                "label d",
            },
            WebhookEventAction.DELETED: {
                "label b",
                "label c",
                "label d",
                "inner label b",
                "inner label c",
                "inner label d",
            },
        },
        WebhookEvent.PULL_REQUEST_REVIEW: {
            WebhookEventAction.SUBMITTED: {
                "inner review a",
                "inner review c",
                "inner review d",
                "review b",
                "review c",
                "review d",
            },
            WebhookEventAction.EDITED: {
                "review b",
                "review c",
                "review d",
                "inner review b",
                "inner review d",
            },
            WebhookEventAction.DISMISSED: {
                "inner review b",
                "inner review c",
                "inner review d",
                "review a",
                "review d",
            },
        },
    }

    test_cases = [
        (WebhookEvent.LABEL, "tests/fixtures/complete/label.json"),
        (
            WebhookEvent.PULL_REQUEST_REVIEW,
            "tests/fixtures/complete/pull_request_review.json",
        ),
    ]

    for event_name, path in test_cases:
        with open(path) as f:
            events = json.load(f)

        for event in events:
            out = io.StringIO()
            with redirect_stdout(out):
                decorator.handle_webhook(event_name.value, event)

            output = out.getvalue().strip().split("\n")
            output_set = set(output)

            assert len(output) == len(output_set)

            assert (
                output_set
                == assertions[event_name][WebhookEventAction(event["action"])]
            )


def test_debug_hooks_are_handled(mocker):
    """
    Verify that debug hooks completely override normal hooks for their event type.

    Tests the debug mode behavior:
    - When ANY debug hook exists for an event, ONLY debug hooks fire for that event
    - Normal hooks for that event are ignored when debug hooks are present
    - Debug mode is event-specific (doesn't affect other event types)
    - Events without debug hooks continue to fire normally
    """
    decorator = _WebhookDecorator()
    mocker.patch("octohook.decorators.hook", side_effect=decorator.webhook)

    load_hooks(["tests.hooks"])

    # LabelEvent has `debug=True`. Only debug hooks should be fired.
    with open("tests/fixtures/complete/label.json") as f:
        events = json.load(f)

    for event in events:
        out = io.StringIO()
        with redirect_stdout(out):
            decorator.handle_webhook(WebhookEvent.LABEL.value, event)

        output = set(out.getvalue().strip().split("\n"))

        assert output == {"label a debug", "label d debug"}

    # PullRequestReview has no debug. All relevant hooks should be fired.
    expected = {
        WebhookEventAction.SUBMITTED: {
            "inner review a",
            "inner review c",
            "inner review d",
            "review b",
            "review c",
            "review d",
        },
        WebhookEventAction.EDITED: {
            "review b",
            "review c",
            "review d",
            "inner review b",
            "inner review d",
        },
        WebhookEventAction.DISMISSED: {
            "inner review b",
            "inner review c",
            "inner review d",
            "review a",
            "review d",
            "repo a",
        },
    }
    with open("tests/fixtures/complete/pull_request_review.json") as f:
        events = json.load(f)

        for event in events:
            out = io.StringIO()
            with redirect_stdout(out):
                decorator.handle_webhook(WebhookEvent.PULL_REQUEST_REVIEW.value, event)

            output = set(out.getvalue().strip().split("\n"))

            assert output == expected[WebhookEventAction(event["action"])]

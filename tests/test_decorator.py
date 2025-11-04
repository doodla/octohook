import sys

import pytest

import octohook
import octohook.decorators
from octohook import load_hooks
from octohook.decorators import _WebhookDecorator
from octohook.events import WebhookEvent, WebhookEventAction
from tests.hooks import _tracker

ANY_REPO = "*"
ANY_ACTION = "*"

# Expected hook counts for test fixture modules
# tests/hooks contains:
#   - debug_hooks/label.py: 4 hooks (2 debug, 2 normal)
#   - handle_hooks/label.py: 4 hooks
#   - handle_hooks/pull_request_review_event.py: 4 hooks
#   - repo_hooks/pull_request_review_event.py: 2 hooks (repository-specific)
# Note: Removed duplicate inner/ directory to eliminate code duplication
EXPECTED_TOTAL_HOOKS = 14
EXPECTED_DEBUG_HOOKS_ONLY = 4
EXPECTED_HANDLE_HOOKS_ONLY = 10  # Total hooks excluding debug_hooks module


@pytest.fixture(autouse=True)
def clean_imported_modules(monkeypatch):
    """
    Clean up module imports after each test to prevent test pollution.

    This fixture:
    1. Saves current state of imported modules
    2. Resets octohook._imported_modules before test
    3. Cleans up sys.modules after test

    Using autouse=True applies this to all tests in this file automatically.
    """
    # Save current imported modules
    original_modules = set(sys.modules.keys())

    # Reset octohook's module tracking
    monkeypatch.setattr(octohook, "_imported_modules", [])

    yield  # Run the test

    # Clean up any modules imported during test
    for module_name in list(sys.modules.keys()):
        if module_name not in original_modules and module_name.startswith("tests.hooks"):
            sys.modules.pop(module_name, None)

    # Reset module tracking again
    octohook._imported_modules = []


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

    # LabelEvent (counts updated after removing inner/ directory)
    assert len(label) == 5  # (*, created, edited, deleted and debug)
    assert len(label[ANY_ACTION][ANY_REPO]) == 5  # Was 6, removed inner/label d
    assert len(label[WebhookEventAction.CREATED][ANY_REPO]) == 2  # Was 4, removed inner/label a, c
    assert len(label[WebhookEventAction.EDITED][ANY_REPO]) == 3  # Was 6, removed inner/label a, b, c
    assert len(label[WebhookEventAction.DELETED][ANY_REPO]) == 2  # Was 4, removed inner/label b, c

    # PullRequestReviewEvent (counts updated after removing inner/ directory)
    assert len(review) == 4
    assert len(review[ANY_ACTION][ANY_REPO]) == 1  # Was 2, removed inner/pr_review d
    assert len(review[WebhookEventAction.SUBMITTED][ANY_REPO]) == 2  # Was 4, removed inner/pr_review a, c
    assert len(review[WebhookEventAction.EDITED][ANY_REPO]) == 2  # Was 3, removed inner/pr_review b
    assert len(review[WebhookEventAction.DISMISSED][ANY_REPO]) == 1  # Was 3, removed inner/pr_review b, c
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


def test_handle_hooks(mocker, fixture_loader):
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

    # Expected hooks for each action (after removing inner/ directory)
    assertions = {
        WebhookEvent.LABEL: {
            WebhookEventAction.EDITED: {
                "label a",
                "label b",
                "label c",
                "label d",
            },
            WebhookEventAction.CREATED: {
                "label a",
                "label c",
                "label d",
            },
            WebhookEventAction.DELETED: {
                "label b",
                "label c",
                "label d",
            },
        },
        WebhookEvent.PULL_REQUEST_REVIEW: {
            WebhookEventAction.SUBMITTED: {
                "review b",
                "review c",
                "review d",
            },
            WebhookEventAction.EDITED: {
                "review b",
                "review c",
                "review d",
            },
            WebhookEventAction.DISMISSED: {
                "review a",
                "review d",
            },
        },
    }

    test_cases = [
        (WebhookEvent.LABEL, "label"),
        (WebhookEvent.PULL_REQUEST_REVIEW, "pull_request_review"),
    ]

    for event_name, fixture_name in test_cases:
        events = fixture_loader.load(fixture_name)

        for event in events:
            # Reset tracker before each test
            _tracker.reset()

            # Handle the webhook
            decorator.handle_webhook(event_name.value, event)

            # Get tracked calls
            calls = _tracker.get_calls()
            calls_set = set(calls)

            # Verify no duplicates
            assert len(calls) == len(calls_set), "Hooks were called multiple times"

            # Verify correct hooks fired
            expected = assertions[event_name][WebhookEventAction(event["action"])]
            assert calls_set == expected, f"Expected {expected}, got {calls_set}"


def test_debug_hooks_are_handled(mocker, fixture_loader):
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
    label_events = fixture_loader.load("label")

    for event in label_events:
        _tracker.reset()
        decorator.handle_webhook(WebhookEvent.LABEL.value, event)
        calls = set(_tracker.get_calls())
        assert calls == {"label a debug", "label d debug"}

    # PullRequestReview has no debug. All relevant hooks should be fired.
    # (after removing inner/ directory)
    expected = {
        WebhookEventAction.SUBMITTED: {
            "review b",
            "review c",
            "review d",
        },
        WebhookEventAction.EDITED: {
            "review b",
            "review c",
            "review d",
        },
        WebhookEventAction.DISMISSED: {
            "review a",
            "review d",
            "repo a",
        },
    }

    pr_review_events = fixture_loader.load("pull_request_review")

    for event in pr_review_events:
        _tracker.reset()
        decorator.handle_webhook(WebhookEvent.PULL_REQUEST_REVIEW.value, event)
        calls = set(_tracker.get_calls())
        assert calls == expected[WebhookEventAction(event["action"])]

import io
import json
from contextlib import redirect_stdout

import pytest

import octohook.decorators
from octohook.decorators import load_hooks, _WebhookDecorator
from octohook.events import WebhookEvent, WebhookEventAction


def setup_function():
    octohook.decorators._loaded = False


def test_load_hooks_calls_hook(mocker):
    mock = mocker.patch("octohook.decorators.hook")

    load_hooks(["tests/hooks"])

    assert mock.call_count == 20


def test_load_hooks_parses_properly(mocker):
    decorator = _WebhookDecorator()
    mocker.patch("octohook.decorators.hook", side_effect=decorator.webhook)

    load_hooks(["tests/hooks"])

    handlers = decorator.handlers

    label = handlers[WebhookEvent.LABEL]
    review = handlers[WebhookEvent.PULL_REQUEST_REVIEW]

    assert len(handlers) == 2

    # LabelEvent
    assert len(label) == 5  # (*, created, edited, deleted and debug)
    assert len(label["*"]) == 6
    assert len(label[WebhookEventAction.CREATED]) == 4
    assert len(label[WebhookEventAction.EDITED]) == 6
    assert len(label[WebhookEventAction.DELETED]) == 4

    # PullRequestReviewEvent
    assert len(review) == 4
    assert len(review["*"]) == 2
    assert len(review[WebhookEventAction.SUBMITTED]) == 4
    assert len(review[WebhookEventAction.EDITED]) == 3
    assert len(review[WebhookEventAction.DISMISSED]) == 3


def test_calling_load_hooks_multiple_times_raises_error(mocker):
    mocker.patch("octohook.decorators.hook")

    load_hooks(["tests/hooks"])

    with pytest.raises(RuntimeError) as excinfo:
        load_hooks(["tests/hooks"])

    assert "load_hooks should only be called once" in str(excinfo.value)


def test_handle_hooks(mocker):
    decorator = _WebhookDecorator()
    mocker.patch("octohook.decorators.hook", side_effect=decorator.webhook)

    load_hooks(["tests/hooks/handle_hooks"])

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
    decorator = _WebhookDecorator()
    mocker.patch("octohook.decorators.hook", side_effect=decorator.webhook)

    load_hooks(["tests/hooks/"])

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

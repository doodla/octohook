import json

import octohook
from octohook.events import PullRequestEvent
from octohook.models import PullRequest


class MyPullRequest(PullRequest):
    @property
    def test(self):
        return "test"


def setup_function():
    octohook._loaded = False
    octohook.model_overrides = {
        PullRequest: MyPullRequest,
    }


def test_model_override_works():
    with open("tests/fixtures/complete/pull_request.json") as f:
        payload = json.load(f)

    event = PullRequestEvent(payload[0])

    pr = event.pull_request

    assert pr.test == "test"

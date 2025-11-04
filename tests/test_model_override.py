import pytest

import octohook
from octohook.events import PullRequestEvent
from octohook.models import PullRequest


class MyPullRequest(PullRequest):
    @property
    def test(self):
        return "test"


@pytest.fixture
def model_override(monkeypatch):
    """
    Set up model override for testing custom model classes.

    This fixture configures octohook to use MyPullRequest instead of
    the standard PullRequest class, allowing us to test the model
    override system.
    """
    monkeypatch.setattr(octohook, "model_overrides", {
        PullRequest: MyPullRequest,
    })
    return MyPullRequest


def test_model_override_works(model_override, fixture_loader):
    """
    Verify that model_overrides dict correctly substitutes custom classes.

    Tests that when a model class is registered in the model_overrides dict,
    instances of that model use the custom class instead of the base class,
    allowing users to add custom methods and properties to GitHub objects.
    """
    payloads = fixture_loader.load("pull_request")
    event = PullRequestEvent(payloads[0])

    pr = event.pull_request

    # Verify override is active
    assert isinstance(pr, model_override)
    assert pr.test == "test"

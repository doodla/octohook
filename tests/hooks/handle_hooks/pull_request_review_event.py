from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, PullRequestReviewEvent
from tests.hooks._tracker import track_call


@hook(WebhookEvent.PULL_REQUEST_REVIEW, [WebhookEventAction.DISMISSED])
def a(event: PullRequestReviewEvent):
    track_call("review a")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.EDITED, WebhookEventAction.SUBMITTED],
)
def b(event: PullRequestReviewEvent):
    track_call("review b")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.SUBMITTED, WebhookEventAction.EDITED],
)
def c(event: PullRequestReviewEvent):
    track_call("review c")
    assert isinstance(event, PullRequestReviewEvent)


@hook(WebhookEvent.PULL_REQUEST_REVIEW)
def d(event: PullRequestReviewEvent):
    track_call("review d")
    assert isinstance(event, PullRequestReviewEvent)


def some_function():
    pass


some_function()

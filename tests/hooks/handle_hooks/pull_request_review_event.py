from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, PullRequestReviewEvent


@hook(WebhookEvent.PULL_REQUEST_REVIEW, [WebhookEventAction.DISMISSED])
def a(event: PullRequestReviewEvent):
    print("review a")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.EDITED, WebhookEventAction.SUBMITTED],
)
def b(event: PullRequestReviewEvent):
    print("review b")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.SUBMITTED, WebhookEventAction.EDITED],
)
def c(event: PullRequestReviewEvent):
    print("review c")
    assert isinstance(event, PullRequestReviewEvent)


@hook(WebhookEvent.PULL_REQUEST_REVIEW)
def d(event: PullRequestReviewEvent):
    print("review d")
    assert isinstance(event, PullRequestReviewEvent)


def some_function():
    pass


some_function()

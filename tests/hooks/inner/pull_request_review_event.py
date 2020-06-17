from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, PullRequestReviewEvent


@hook(WebhookEvent.PULL_REQUEST_REVIEW, [WebhookEventAction.SUBMITTED])
def a(event: PullRequestReviewEvent):
    print("inner review a")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.EDITED, WebhookEventAction.DISMISSED],
)
def b(event: PullRequestReviewEvent):
    print("inner review b")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.DISMISSED, WebhookEventAction.SUBMITTED],
)
def c(event: PullRequestReviewEvent):
    print("inner review c")
    assert isinstance(event, PullRequestReviewEvent)


@hook(WebhookEvent.PULL_REQUEST_REVIEW)
def d(event: PullRequestReviewEvent):
    print("inner review d")
    assert isinstance(event, PullRequestReviewEvent)

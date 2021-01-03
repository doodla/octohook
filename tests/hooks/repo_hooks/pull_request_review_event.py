from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, PullRequestReviewEvent


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.DISMISSED],
    repositories=["doodla/octohook-playground"],
)
def a(event: PullRequestReviewEvent):
    print("repo a")
    assert isinstance(event, PullRequestReviewEvent)


@hook(
    WebhookEvent.PULL_REQUEST_REVIEW,
    [WebhookEventAction.EDITED, WebhookEventAction.SUBMITTED],
    repositories=["doodla/octohook-playground2"],
)
def b(event: PullRequestReviewEvent):
    print("repo b")
    assert isinstance(event, PullRequestReviewEvent)

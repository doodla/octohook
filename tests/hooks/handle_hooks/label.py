from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, LabelEvent
from tests.hooks._tracker import track_call
from tests.hooks.handle_hooks.pull_request_review_event import some_function


@hook(WebhookEvent.LABEL, [WebhookEventAction.CREATED, WebhookEventAction.EDITED])
def a(event: LabelEvent):
    track_call("label a")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [WebhookEventAction.EDITED, WebhookEventAction.DELETED])
def b(event: LabelEvent):
    track_call("label b")
    assert isinstance(event, LabelEvent)


@hook(
    WebhookEvent.LABEL,
    [WebhookEventAction.CREATED, WebhookEventAction.EDITED, WebhookEventAction.DELETED],
)
def c(event: LabelEvent):
    track_call("label c")
    assert isinstance(event, LabelEvent)


@hook(
    WebhookEvent.LABEL,
)
def d(event: LabelEvent):
    track_call("label d")
    assert isinstance(event, LabelEvent)


some_function()

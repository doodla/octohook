from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, LabelEvent


@hook(WebhookEvent.LABEL, [WebhookEventAction.CREATED, WebhookEventAction.EDITED])
def a(event: LabelEvent):
    print("inner label a")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [WebhookEventAction.EDITED, WebhookEventAction.DELETED])
def b(event: LabelEvent):
    print("inner label b")
    assert isinstance(event, LabelEvent)


@hook(
    WebhookEvent.LABEL,
    [WebhookEventAction.CREATED, WebhookEventAction.EDITED, WebhookEventAction.DELETED],
)
def c(event: LabelEvent):
    print("inner label c")
    assert isinstance(event, LabelEvent)


@hook(
    WebhookEvent.LABEL,
)
def d(event: LabelEvent):
    print("inner label d")
    assert isinstance(event, LabelEvent)

from octohook.decorators import hook
from octohook.events import WebhookEvent, WebhookEventAction, LabelEvent


@hook(WebhookEvent.LABEL, [WebhookEventAction.CREATED, WebhookEventAction.EDITED])
def a(event: LabelEvent):
    print("label a")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [WebhookEventAction.EDITED, WebhookEventAction.DELETED])
def b(event: LabelEvent):
    print("label b")
    assert isinstance(event, LabelEvent)


@hook(
    WebhookEvent.LABEL,
    [WebhookEventAction.CREATED, WebhookEventAction.EDITED, WebhookEventAction.DELETED],
)
def c(event: LabelEvent):
    print("label c")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL,)
def d(event: LabelEvent):
    print("label d")
    assert isinstance(event, LabelEvent)

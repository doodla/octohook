from octohook.decorators import hook
from octohook.events import WebhookEvent, LabelEvent


@hook(WebhookEvent.LABEL, [], debug=True)
def a(event: LabelEvent):
    print("label a debug")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [])
def b(event: LabelEvent):
    print("label b")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [])
def c(event: LabelEvent):
    print("label c")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [], debug=True)
def d(event: LabelEvent):
    print("label d debug")
    assert isinstance(event, LabelEvent)

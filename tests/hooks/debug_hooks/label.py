from octohook.decorators import hook
from octohook.events import WebhookEvent, LabelEvent
from tests.hooks._tracker import track_call


@hook(WebhookEvent.LABEL, [], debug=True)
def a(event: LabelEvent):
    track_call("label a debug")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [])
def b(event: LabelEvent):
    track_call("label b")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [])
def c(event: LabelEvent):
    track_call("label c")
    assert isinstance(event, LabelEvent)


@hook(WebhookEvent.LABEL, [], debug=True)
def d(event: LabelEvent):
    track_call("label d debug")
    assert isinstance(event, LabelEvent)

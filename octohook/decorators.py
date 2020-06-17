import logging
from collections import defaultdict
from functools import wraps
from typing import List

from octohook.events import WebhookEvent, WebhookEventAction, parse

logger = logging.getLogger("octohook")


class _WebhookDecorator:
    def __init__(self):
        self.handlers = defaultdict(lambda: defaultdict(set))

    def webhook(self, event: WebhookEvent, actions: List[WebhookEventAction] = None):
        def real_decorator(fn):
            @wraps(fn)
            def wrapper(*, event_name, payload):
                fn(parse(event_name, payload))

            if actions is None:
                self.handlers[event]["*"].add(wrapper)
            else:
                for action in actions:
                    self.handlers[event][action].add(wrapper)

            return wrapper

        return real_decorator

    def handle_webhook(self, event_name, payload):
        action_handlers = self.handlers[WebhookEvent(event_name)]

        handlers = action_handlers["*"].copy()
        if payload.get("action") is not None:
            handlers.update(action_handlers[WebhookEventAction(payload["action"])])

        for handler in handlers:
            # noinspection PyBroadException
            try:
                logger.info(f"Evaluating {handler.__name__}")
                handler(event_name=event_name, payload=payload)
            except Exception:
                logger.exception(f"Exception when handling {handler.__name__}")


_loaded = False
_decorator = _WebhookDecorator()

hook = _decorator.webhook
handle_webhook = _decorator.handle_webhook


def load_hooks(module_path):
    global _loaded

    if _loaded:
        raise RuntimeError("load_hooks should only be called once")
    else:
        _loaded = True

    import pkgutil

    for loader, name, is_pkg in pkgutil.walk_packages([module_path]):
        loader.find_module(name).load_module(name)

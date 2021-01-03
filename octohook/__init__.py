from typing import List

import octohook.models
from .decorators import hook, handle_webhook
from .events import parse, WebhookEvent, WebhookEventAction

__all__ = [
    "events",
    "handle_webhook",
    "hook",
    "load_hooks",
    "models",
    "model_overrides",
    "parse",
    "WebhookEvent",
    "WebhookEventAction",
]

_loaded = False
model_overrides = {}


def load_hooks(module_paths: List[str]):
    global _loaded

    if _loaded:
        raise RuntimeError("load_hooks should only be called once")
    else:
        _loaded = True

    import pkgutil

    for loader, name, is_pkg in pkgutil.walk_packages(module_paths):
        loader.find_module(name).load_module(name)

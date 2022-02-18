from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
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

_imported_modules = []
model_overrides = {}


def _import_module(module: str) -> List[str]:
    module_path = import_module(module).__file__

    package_dir = Path(module_path).resolve().parent

    imported_modules = []
    for _, module_name, is_package in walk_packages([str(package_dir)]):
        module_to_be_imported = f"{module}.{module_name}"
        if is_package:
            imported_modules.extend(_import_module(module_to_be_imported))
        else:
            imported_modules.append(import_module(module_to_be_imported).__name__)
    return imported_modules


def load_hooks(modules: List[str]):
    """
    Iterates through the given modules recursively and imports all the modules to load hook information.

    @param modules List of modules to be imported. The modules cannot be relative. For example, you may use
                   "module_a.module_b" or "module_a", but not ".module_a" or "module_a/module_b"
    """
    global _imported_modules

    for module in modules:
        _imported_modules.extend(_import_module(module))

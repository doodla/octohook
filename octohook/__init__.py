import logging
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
from typing import List

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

logger = logging.getLogger("octohook")

_imported_modules = []
model_overrides = {}

def _import_module(module: str) -> List[str]:
    try:
        imported = import_module(module)
    except Exception as e:
        logger.error("Failed to import module %s", module, exc_info=e)
        return []

    module_path = imported.__file__

    if module_path.endswith("__init__.py"):
        package_dir = Path(module_path).resolve().parent
    else:
        return [imported.__name__]

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

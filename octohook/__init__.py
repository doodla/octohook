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
    "models",
    "OctohookConfigError",
    "parse",
    "reset",
    "setup",
    "WebhookEvent",
    "WebhookEventAction",
]

logger = logging.getLogger("octohook")

_imported_modules = []


class OctohookConfigError(Exception):
    """Raised when octohook configuration is invalid."""
    pass

def _import_module(module: str) -> List[str]:
    imported = import_module(module)
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


def setup(*, modules: List[str]) -> None:
    """
    Configure octohook by loading webhook handlers.

    This function clears any existing configuration via reset(), then recursively
    imports the specified modules to discover and register all decorated webhook
    handlers.

    Args:
        modules: List of fully-qualified module paths containing webhook handlers.
                 Modules are imported recursively. Cannot use relative imports.

    Raises:
        ImportError: If any specified module cannot be imported.

    Example:
        >>> import octohook
        >>> octohook.setup(modules=["hooks.github", "hooks.slack"])
    """
    global _imported_modules

    reset()

    for module in modules:
        _imported_modules.extend(_import_module(module))


def reset() -> None:
    """
    Clear all octohook configuration and return to unconfigured state.

    Removes all registered webhook handlers and clears the list of imported modules.
    After calling reset(), setup() must be called again before handling webhooks.

    This function is automatically called by setup() to ensure a clean configuration.
    It can also be called directly to clear octohook state.

    Example:
        >>> import octohook
        >>> octohook.reset()
        >>> octohook.setup(modules=["hooks"])
    """
    global _imported_modules
    from octohook.decorators import _decorator

    _decorator.handlers.clear()
    _imported_modules.clear()

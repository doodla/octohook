import logging
from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
from typing import List, Optional, Dict, Type

from .decorators import hook, handle_webhook
from .events import parse, WebhookEvent, WebhookEventAction

__all__ = [
    "events",
    "handle_webhook",
    "hook",
    "models",
    "model_overrides",
    "OctohookConfigError",
    "parse",
    "reset",
    "setup",
    "WebhookEvent",
    "WebhookEventAction",
]

logger = logging.getLogger("octohook")

_imported_modules = []
model_overrides = {}


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


def setup(
    *,
    modules: List[str],
    model_overrides: Optional[Dict[Type, Type]] = None,
) -> None:
    """
    Configure octohook (one-time initialization).

    Args:
        modules: List of module paths to load hooks from (required).
        model_overrides: Dict mapping base models to custom implementations.
                        Validates that overrides are subclasses.

    Raises:
        OctohookConfigError: If configuration is invalid.
        ImportError: If any module fails to import.
        TypeError: If model_overrides contains invalid mappings.

    Example:
        >>> octohook.setup(modules=["hooks.github", "hooks.slack"])
        >>> octohook.setup(
        ...     modules=["hooks"],
        ...     model_overrides={PullRequest: CustomPullRequest}
        ... )
    """
    global _imported_modules
    from octohook.decorators import _decorator

    if _decorator.handlers:
        logger.warning("octohook.setup() called multiple times - reconfiguring")
        reset()

    if model_overrides:
        for base_class, override_class in model_overrides.items():
            if not isinstance(override_class, type):
                raise TypeError(
                    f"Model override for {base_class.__name__} must be a class, "
                    f"got {type(override_class).__name__}"
                )
            if not issubclass(override_class, base_class):
                raise TypeError(
                    f"Model override {override_class.__name__} must be a subclass of "
                    f"{base_class.__name__}"
                )

        globals()["model_overrides"].update(model_overrides)

    for module in modules:
        _imported_modules.extend(_import_module(module))


def reset() -> None:
    """
    Reset octohook to initial state.

    Clears all registered hooks, imported modules, and model overrides.
    Useful for testing isolation.

    Example:
        >>> octohook.reset()
        >>> octohook.setup(modules=["tests.hooks"])
    """
    global _imported_modules, model_overrides
    from octohook.decorators import _decorator

    _decorator.handlers.clear()
    _imported_modules.clear()
    model_overrides.clear()

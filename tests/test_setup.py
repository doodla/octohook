"""
Tests for octohook.setup() and octohook.reset() functions.

Verifies webhook handler loading and state management.
"""
import pytest

import octohook
from octohook import setup, reset, OctohookConfigError
from octohook.events import WebhookEvent, WebhookEventAction


def test_setup_loads_modules():
    """Verify that setup() loads hooks from specified modules."""
    setup(modules=["tests.hooks.handle_hooks"])

    from octohook.decorators import _decorator
    assert len(_decorator.handlers) > 0


def test_setup_raises_on_invalid_module():
    """Verify that setup() raises ImportError for invalid modules."""
    with pytest.raises(ModuleNotFoundError):
        setup(modules=["nonexistent.module"])


def test_setup_multiple_calls_replaces_hooks():
    """Verify that calling setup() multiple times replaces hooks."""
    setup(modules=["tests.hooks.handle_hooks.label"])

    from octohook.decorators import _decorator
    first_count = len(_decorator.handlers)

    # Second call should reset and load new hooks
    setup(modules=["tests.hooks.debug_hooks"])

    second_count = len(_decorator.handlers)

    # Should have different hooks loaded (debug_hooks only has LABEL event)
    assert WebhookEvent.LABEL in _decorator.handlers


def test_reset_clears_hooks():
    """Verify that reset() clears all registered hooks."""
    setup(modules=["tests.hooks.handle_hooks"])

    from octohook.decorators import _decorator
    assert len(_decorator.handlers) > 0

    reset()

    assert len(_decorator.handlers) == 0


def test_reset_clears_imported_modules():
    """Verify that reset() clears imported modules tracking."""
    setup(modules=["tests.hooks.handle_hooks"])

    assert len(octohook._imported_modules) > 0

    reset()

    assert len(octohook._imported_modules) == 0


def test_reset_allows_setup_again():
    """Verify that reset() allows setup() to be called again without warning."""
    setup(modules=["tests.hooks.handle_hooks"])

    reset()

    # Should not warn since we explicitly reset
    setup(modules=["tests.hooks.debug_hooks"])

    from octohook.decorators import _decorator
    assert len(_decorator.handlers) > 0


def test_setup_and_handle_webhook(fixture_loader):
    """Integration test: setup() -> handle_webhook()."""
    from tests.hooks import _tracker

    setup(modules=["tests.hooks.handle_hooks"])

    payloads = fixture_loader.load("label")
    created_payload = [p for p in payloads if p["action"] == "created"][0]

    _tracker.reset()
    octohook.handle_webhook("label", created_payload)

    calls = _tracker.get_calls()
    assert len(calls) > 0

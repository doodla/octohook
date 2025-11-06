"""
Shared pytest fixtures and utilities for octohook tests.

This module provides reusable fixtures and helper functions to reduce
code duplication across test files.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

import pytest
import octohook
from octohook.decorators import _WebhookDecorator


@pytest.fixture(autouse=True)
def reset_octohook():
    """
    Reset octohook state before each test to ensure isolation.

    This fixture automatically runs before every test, clearing all hooks,
    imported modules, and model overrides. It also clears test module imports
    from sys.modules to ensure decorators re-register on each test.
    """
    import sys

    octohook.reset()
    original_modules = set(sys.modules.keys())

    yield

    octohook.reset()

    for module_name in list(sys.modules.keys()):
        if module_name not in original_modules and module_name.startswith("tests.hooks"):
            sys.modules.pop(module_name, None)


@pytest.fixture
def isolated_decorator():
    """
    Provide a fresh _WebhookDecorator instance for each test.

    This eliminates the need for global state manipulation and ensures
    tests don't interfere with each other.

    Usage:
        def test_something(isolated_decorator):
            isolated_decorator.webhook(...)
    """
    return _WebhookDecorator()


@pytest.fixture
def fixture_loader():
    """
    Provide a fixture loading helper for tests that need webhook payloads.

    Usage:
        def test_something(fixture_loader):
            payload = fixture_loader.load("label")
    """
    class FixtureLoader:
        def __init__(self):
            self.base_path = Path(__file__).parent / "fixtures"

        def load(self, event_name: str, directory: str = None) -> List[Dict[str, Any]]:
            """Load fixture file and return list of example payloads."""
            if directory:
                path = self.base_path / directory / f"{event_name}.json"
                with path.open() as f:
                    return json.load(f)

            # Try complete first, then incomplete
            for dir_name in ["complete", "incomplete"]:
                path = self.base_path / dir_name / f"{event_name}.json"
                if path.exists():
                    with path.open() as f:
                        return json.load(f)

            raise FileNotFoundError(f"No fixture found for {event_name}")

        def discover_all(self) -> List[str]:
            """Get list of all available fixture names."""
            fixtures = set()
            for directory in ["complete", "incomplete"]:
                dir_path = self.base_path / directory
                if dir_path.exists():
                    for json_file in dir_path.glob("*.json"):
                        fixtures.add(json_file.stem)
            return sorted(fixtures)

    return FixtureLoader()


def discover_fixtures() -> List[str]:
    """
    Auto-discover test fixture files from complete and incomplete directories.

    This function can be used at module level to generate parametrize values.

    Note: Some fixtures are excluded because they lack dedicated event classes
    and fall back to BaseWebhookEvent, which would fail tests that expect
    specific event type implementations with all their fields.

    Returns:
        Sorted list of fixture names (without .json extension)
    """
    # Fixtures that exist but lack dedicated event classes (fall back to BaseWebhookEvent)
    # These would fail tests that expect specific event type implementations
    EXCLUDED_FIXTURES = {
        "code_scanning_alert",  # No CodeScanningAlertEvent class implemented
        "ping_event",  # No PingEvent class implemented
    }

    fixtures = set()
    base_path = Path(__file__).parent / "fixtures"

    for directory in ["complete", "incomplete"]:
        fixture_path = base_path / directory
        if fixture_path.exists():
            for json_file in fixture_path.glob("*.json"):
                fixture_name = json_file.stem
                if fixture_name not in EXCLUDED_FIXTURES:
                    fixtures.add(fixture_name)

    return sorted(fixtures)

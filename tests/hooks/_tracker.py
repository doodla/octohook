"""
Hook call tracker for testing.

This module provides a simple mechanism to track which hooks are called
during tests, replacing the old print-based verification approach.
"""

# Global list to track hook calls
_calls = []


def track_call(hook_name: str):
    """Record that a hook was called."""
    _calls.append(hook_name)


def get_calls():
    """Get list of all tracked hook calls."""
    return _calls.copy()


def reset():
    """Clear all tracked calls."""
    _calls.clear()

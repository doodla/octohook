## Project Overview

Octohook is a Python library that simplifies working with GitHub Webhooks by parsing incoming payloads into typed Python classes. It provides automatic payload parsing, URL interpolation helpers, and a decorator-based system for registering webhook handlers.

## Development Commands

### Testing
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v
```

### Building
```bash
# Build the package
uv build
```

## Architecture

### Core Components

**octohook/__init__.py** - Entry point providing:
- `setup(modules, model_overrides)` - Configures octohook by loading webhook handlers and registering model overrides. Validates that model overrides inherit from base classes. Raises on import errors. Always calls reset() first to clear existing state.
- `reset()` - Clears all registered hooks, imported modules, and model overrides. Returns octohook to unconfigured state.
- `_model_overrides` - Internal dict for extending/replacing model classes (private, set via setup())
- `OctohookConfigError` - Exception raised for configuration errors
- Exports: `hook`, `handle_webhook`, `parse`, `setup`, `reset`, `WebhookEvent`, `WebhookEventAction`, `OctohookConfigError`

**octohook/decorators.py** - Decorator system (`_WebhookDecorator` class):
- `@hook(event, actions, repositories, debug)` - Registers functions as webhook handlers
- `handle_webhook(event_name, payload)` - Dispatches webhooks to registered handlers
- Handler storage: nested defaultdicts organized by event → action → repo → handlers
- Debug mode: when `debug=True` on any hook, only debug hooks fire for that event
- Sequential execution: handlers run in order, exceptions are logged but don't stop execution

**octohook/events.py** - Event classes:
- `BaseWebhookEvent` - Base class with common fields (sender, repository, organization, enterprise)
- 40+ specific event classes (e.g., `PullRequestEvent`, `IssuesEvent`, `LabelEvent`)
- `WebhookEvent` enum - All GitHub event types (check_run, pull_request, etc.)
- `WebhookEventAction` enum - All GitHub actions (opened, closed, synchronize, etc.)
- `parse(event_name, payload)` - Factory function that returns appropriate event object

**octohook/models.py** - Model classes:
- `BaseGithubModel` - Uses `__new__` to check `model_overrides` dict and instantiate override classes
- Core models: `User`, `Repository`, `PullRequest`, `Issue`, `Comment`, etc.
- URL interpolation: Many models have methods like `archive_url(format, ref)` that fill in URL templates
- `_transform(url, local_variables)` - Helper that replaces `{param}` and `{/param}` patterns in URLs
- `_optional(payload, key, class_type)` - Helper for nullable fields

### Hook System

The hook system uses a three-level filtering mechanism:

1. **Event filtering** - Match on `WebhookEvent` (e.g., PULL_REQUEST, LABEL)
2. **Action filtering** - Match on `WebhookEventAction` (e.g., OPENED, CLOSED) or `ANY_ACTION` (*)
3. **Repository filtering** - Match specific repo full_name or `ANY_REPO` (*)

Handler resolution order:
1. If any debug hooks exist for the event, ONLY debug hooks run
2. Otherwise: handlers for (event, specific_action, ANY_REPO) + (event, specific_action, specific_repo) + (event, ANY_ACTION, ANY_REPO)

### Model Override System

Users can extend/replace models via `setup()`:

```python
from octohook.models import PullRequest

class MyPullRequest(PullRequest):
    def custom_method(self):
        pass

octohook.setup(
    modules=["hooks"],
    model_overrides={PullRequest: MyPullRequest}
)
```

When any model is instantiated, `BaseGithubModel.__new__` checks `_model_overrides` and substitutes the custom class. This allows adding custom methods/properties to GitHub objects without modifying octohook source.

### Payload Inconsistencies

GitHub sends different payload structures for the same model depending on the event type and action. For example:
- `changes` key is only present for some actions with "edited" events
- Not all fields are populated in all contexts

Octohook uses `Optional` types extensively and the `_optional()` helper to handle missing fields gracefully. Models conform to the "least common denominator" - required fields are only those present in ALL payloads for that model.

## Testing Notes

- Tests use `pytest` and `pytest-mock`
- Test fixtures in `tests/fixtures/complete/` contain real GitHub webhook payloads
- Hook tests verify that the decorator system correctly routes events to handlers
- Model tests verify parsing and URL interpolation
- `tests/conftest.py` provides an autouse fixture that calls `reset()` before/after each test for isolation
- The autouse fixture also clears test module imports from `sys.modules` to ensure decorators re-register on each test

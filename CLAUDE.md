## Project Overview

Octohook is a Python library that simplifies working with GitHub Webhooks by parsing incoming payloads into typed Python classes. It provides automatic payload parsing, URL interpolation helpers, and a decorator-based system for registering webhook handlers.

## Key Concepts

### Hook System

The hook system uses a three-level filtering mechanism:

1. **Event filtering** - Match on `WebhookEvent` (e.g., PULL_REQUEST, LABEL)
2. **Action filtering** - Match on `WebhookEventAction` (e.g., OPENED, CLOSED) or `ANY_ACTION` (*)
3. **Repository filtering** - Match specific repo full_name or `ANY_REPO` (*)

**Handler resolution order:**
1. If any debug hooks exist for the event, ONLY debug hooks run
2. Otherwise: handlers for (event, specific_action, ANY_REPO) + (event, specific_action, specific_repo) + (event, ANY_ACTION, ANY_REPO)

**Execution behavior:**
- Handlers run sequentially in registration order
- Exceptions are logged but don't stop execution
- Debug mode (`debug=True` on any hook) causes only debug hooks to fire for that event

### Payload Handling

GitHub sends different payload structures for the same model depending on the event type and action. For example:
- `changes` key is only present for some actions with "edited" events
- Not all fields are populated in all contexts

Octohook uses `Optional` types extensively to handle missing fields gracefully. Models conform to the "least common denominator" - required fields are only those present in ALL payloads for that model.

## Architecture

### Module Organization

**octohook/__init__.py** - Entry point
- `setup(modules)` - Configures octohook by loading webhook handlers. Raises on import errors. Always calls reset() first.
- `reset()` - Clears all registered hooks and imported modules
- `OctohookConfigError` - Exception raised for configuration errors
- Exports: `hook`, `handle_webhook`, `parse`, `setup`, `reset`, `WebhookEvent`, `WebhookEventAction`, `OctohookConfigError`

**octohook/decorators.py** - Decorator system
- `@hook` decorator - Registers functions as webhook handlers
- `handle_webhook(event_name, payload)` - Dispatches webhooks to registered handlers
- `_WebhookDecorator` class - Manages handler registration and routing

**octohook/events.py** - Event classes
- `BaseWebhookEvent` - Base class with common fields (sender, repository, organization, enterprise)
- Specific event classes (e.g., `PullRequestEvent`, `IssuesEvent`, `LabelEvent`)
- `WebhookEvent` enum - All GitHub event types
- `WebhookEventAction` enum - All GitHub actions
- `parse(event_name, payload)` - Factory function that returns appropriate event object

**octohook/models.py** - Model classes
- `BaseGithubModel` - Base class for all GitHub models
- Core models: `User`, `Repository`, `PullRequest`, `Issue`, `Comment`, etc.
- URL interpolation helpers that fill in URL templates with parameters

## Development

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v
```

**Test organization:**
- Tests use `pytest` and `pytest-mock`
- Test fixtures in `tests/fixtures/complete/` contain real GitHub webhook payloads
- Hook tests verify decorator system routing
- Model tests verify parsing and URL interpolation
- `tests/conftest.py` provides autouse fixture that calls `reset()` before/after each test for isolation

### Building

```bash
# Build the package
uv build
```

## Documentation Standards

### Code Documentation

**Public API functions** (exported in `__all__`):
- Google-style docstrings with Args, Raises, Example sections
- Include at least one runnable usage example
- Type hints required on all signatures

### User Documentation

**Tone:**
- Direct and technical - assume reader competence
- No marketing language or superlatives
- Imperative mood for instructions
- Explain "why" before "how"

**Content:**
- Show real, runnable examples first
- Link to external docs rather than duplicating them
- Keep explanations concise

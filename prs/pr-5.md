# PR #5: Update Parse Function

## Scope

Update the `parse()` function in `octohook/events.py` to use Pydantic's `model_validate()` method instead of direct instantiation. Review `decorators.py` for any needed changes.

## Files Changed

- `octohook/events.py` - Update `parse()` function
- `octohook/decorators.py` - Review (likely no changes)

## Detailed Changes

### 1. Update parse() Function

**File:** `octohook/events.py`

**Before:**
```python
def parse(event_name, payload: dict):
    try:
        return event_map[WebhookEvent(event_name)](payload)
    except Exception:
        logger.exception(f"Could not parse event {event_name}")
        return BaseWebhookEvent(payload)
```

**After:**
```python
def parse(event_name, payload: dict):
    try:
        event_class = event_map[WebhookEvent(event_name)]
        return event_class.model_validate(payload)
    except (KeyError, ValidationError) as e:
        logger.exception(f"Could not parse event {event_name}: {e}")
        return BaseWebhookEvent.model_validate(payload)
```

**Key changes:**
1. ✅ Use `model_validate()` instead of direct call `(payload)`
2. ✅ Catch specific exceptions: `KeyError` (unknown event), `ValidationError` (bad data)
3. ✅ Include exception in log message for better debugging
4. ✅ Apply `model_validate()` to fallback `BaseWebhookEvent` as well

**Note:** `ValidationError` was already imported in PR #1 (Step 3.1).

### 2. Review decorators.py

**File:** `octohook/decorators.py`

**Analysis:**
The decorator system's `handle_webhook()` function calls `parse()` internally:

```python
def handle_webhook(event_name: str, payload: dict):
    event = parse(event_name, payload)
    # ... dispatch to registered handlers
```

**Expected result:** No changes needed. The `parse()` function returns an event object, and the decorator doesn't care how it was instantiated.

**Verification:** Review the file to confirm no changes are needed, then note in PR description that decorators.py was reviewed and requires no modifications.

## Dependencies

**Requires:**
- PR #1 (BaseWebhookEvent and ValidationError import)
- PR #2 (model migrations)
- PR #3 (model migrations)
- PR #4 (event migrations)

**Blocks:** None (PR #6 can proceed independently)

**Critical:** All models and events must be migrated before updating parse(), since parse() instantiates events which reference models.

## Testing Strategy

```bash
# Run full test suite
uv run pytest -v

# Test parse function with real webhook payloads
uv run python -c "
from octohook.events import parse
import json

# Test valid event
payload = {
    'action': 'opened',
    'number': 123,
    'pull_request': {
        'id': 1,
        'number': 123,
        'state': 'open',
        'title': 'Test',
        # ... minimal required fields
    }
}
event = parse('pull_request', payload)
print(f'Parsed event type: {type(event).__name__}')
print(f'Event action: {event.action}')
"

# Test unknown event fallback
uv run python -c "
from octohook.events import parse, BaseWebhookEvent

payload = {'action': 'unknown_action', 'sender': {...}}
event = parse('unknown_event', payload)
print(f'Fallback type: {type(event).__name__}')
print(f'Is BaseWebhookEvent: {isinstance(event, BaseWebhookEvent)}')
"

# Test validation error handling
uv run python -c "
from octohook.events import parse
import json

# Invalid payload (missing required fields)
payload = {'action': 'opened'}  # Missing required pull_request field
event = parse('pull_request', payload)
print(f'Fallback on error: {type(event).__name__}')
"

# Test with actual webhook fixtures
uv run pytest tests/test_models.py::test_model_has_all_keys_in_json -v -k pull_request
```

**Expected outcomes:**
- ✅ Valid events parse correctly using `model_validate()`
- ✅ Unknown events fall back to `BaseWebhookEvent`
- ✅ Invalid payloads are caught and logged, falling back to `BaseWebhookEvent`
- ✅ All webhook fixtures parse without errors
- ✅ Decorator system continues to work (handlers receive proper event objects)
- ✅ All tests pass

## Risk Level

**Low**

- Small, focused change (single function)
- Well-isolated (only affects parsing logic)
- Fallback behavior preserved (unknown events → BaseWebhookEvent)
- All dependencies (models, events) already migrated and tested

## Rationale

**Why separate PR:**
- Small, logical unit: "how we instantiate events"
- Easy to review (< 10 lines changed)
- Can be quickly approved and merged
- Allows testing models/events with old parse logic first

**Why after event migrations:**
- Events must be Pydantic models before we can call `model_validate()`
- Clean separation: "migrate events" → "update how we instantiate them"
- Reduces risk: events are tested with old parse before new parse is introduced

**Why before tests PR:**
- Parse function changes affect test behavior
- Better to update parse first, then update tests to match
- Tests in PR #6 will validate the new parse logic

## Lines Changed (Est)

~10-15 lines

**Breakdown:**
- `parse()` function: 5 lines changed
- `decorators.py`: 0 lines (review only, no changes expected)
- Documentation/comments: ~5 lines if needed

## Rollback Instructions

**If this PR must be reverted:**

1. Revert the commit:
```bash
git revert <commit-hash>
```

2. Verify rollback:
```bash
uv run pytest tests/ -v
```

3. **Note:** This PR is independent enough that reverting it doesn't require reverting other PRs (unless tests in PR #6 specifically depend on new parse behavior).

4. Check parse functionality:
```bash
# Ensure old pattern works
uv run python -c "from octohook.events import parse; print('Parse import OK')"
```

## Additional Notes

**Why model_validate() instead of model_validate_json()?**

- GitHub webhooks are received as Python dicts (already parsed from JSON)
- `model_validate()` accepts dicts
- `model_validate_json()` would require re-serializing to JSON string (inefficient)

**Error handling improvements:**

The new version provides better error information:
- **Before:** Generic `Exception` catch → hard to debug
- **After:** Specific `KeyError` (unknown event) and `ValidationError` (bad data) → clear error type
- **Logging:** Exception included in message → easier debugging

**Fallback behavior:**

Both old and new versions fall back to `BaseWebhookEvent` on error, but new version:
- Uses `model_validate()` for consistency
- Provides more specific error logging
- Catches validation errors explicitly

**Integration with decorators:**

The decorator system calls `parse()` and expects an event object back:
```python
def handle_webhook(event_name: str, payload: dict):
    event = parse(event_name, payload)  # Returns event object
    # ... filters and dispatches to handlers
```

No changes needed in decorators because:
- Return type doesn't change (still returns event object)
- Event object interface doesn't change (same attributes and methods)
- Pydantic models are transparent to the decorator system

**Post-merge checklist:**
- ✅ `parse()` uses `model_validate()`
- ✅ `BaseWebhookEvent` fallback uses `model_validate()`
- ✅ Catches `KeyError` and `ValidationError` specifically
- ✅ Log messages include exception details
- ✅ `decorators.py` reviewed (no changes needed)
- ✅ All webhook fixtures parse correctly
- ✅ Tests pass
- ✅ Error cases fall back gracefully

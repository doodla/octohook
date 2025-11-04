"""
Edge case tests for octohook.

Tests error handling, boundary conditions, and edge cases that could occur
in production but aren't covered by the main test suite.
"""
import json
from unittest.mock import Mock


from octohook.events import WebhookEvent, WebhookEventAction, parse, BaseWebhookEvent
from octohook.models import User
import octohook


def test_handler_exception_does_not_stop_other_handlers(isolated_decorator, fixture_loader):
    """
    Verify that if one handler raises an exception, other handlers still run.

    This is critical for reliability - one bad handler shouldn't break everything.
    """
    failing_handler = Mock(side_effect=Exception("Handler failed"))
    successful_handler = Mock()

    # Register both handlers
    isolated_decorator.webhook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])(
        failing_handler
    )
    isolated_decorator.webhook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])(
        successful_handler
    )

    # Handle webhook
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")

    # Should not raise exception
    isolated_decorator.handle_webhook("label", created_event)

    # Both handlers should be called
    failing_handler.assert_called_once()
    successful_handler.assert_called_once()  # This is the critical assertion


def test_repository_filter_does_not_fire_for_wrong_repo(
    isolated_decorator, fixture_loader
):
    """
    Verify that repository-filtered hooks DON'T fire for other repositories.

    Critical for multi-repo setups - prevents hooks from affecting wrong repos.
    """
    handler = Mock()
    target_repo = "owner/repo-a"

    isolated_decorator.webhook(
        WebhookEvent.LABEL, [WebhookEventAction.CREATED], repositories=[target_repo]
    )(handler)

    # Load fixture and modify repo name
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")
    created_event = json.loads(json.dumps(created_event))  # Deep copy
    created_event["repository"]["full_name"] = "owner/repo-b"  # Different repo

    # Handle webhook
    isolated_decorator.handle_webhook("label", created_event)

    # Handler should NOT be called (negative assertion)
    handler.assert_not_called()


def test_wildcard_and_specific_action_both_fire_for_matching_action(
    isolated_decorator, fixture_loader
):
    """
    Verify that both wildcard and specific-action handlers fire when action matches.

    Documents the expected overlap behavior.
    """
    wildcard_handler = Mock()
    specific_handler = Mock()

    isolated_decorator.webhook(WebhookEvent.LABEL, [])(wildcard_handler)  # ANY_ACTION
    isolated_decorator.webhook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])(
        specific_handler
    )

    # Handle webhook
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")
    isolated_decorator.handle_webhook("label", created_event)

    # Both should fire
    wildcard_handler.assert_called_once()
    specific_handler.assert_called_once()


def test_wildcard_fires_alone_for_non_matching_action(
    isolated_decorator, fixture_loader
):
    """
    Verify that only wildcard handler fires when action doesn't match specific handler.

    Completes the overlap behavior documentation.
    """
    wildcard_handler = Mock()
    specific_handler = Mock()

    isolated_decorator.webhook(WebhookEvent.LABEL, [])(wildcard_handler)  # ANY_ACTION
    isolated_decorator.webhook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])(
        specific_handler
    )

    # Handle webhook with different action
    fixtures = fixture_loader.load("label")
    edited_event = next(e for e in fixtures if e["action"] == "edited")
    isolated_decorator.handle_webhook("label", edited_event)

    # Only wildcard should fire
    wildcard_handler.assert_called_once()
    specific_handler.assert_not_called()  # Should NOT fire for non-matching action


def test_all_fixture_examples_parse_correctly(fixture_loader):
    """
    Verify that ALL examples in each fixture file parse correctly.

    Each JSON fixture contains multiple event examples (created, edited, deleted).
    This ensures we test all action variants.
    """
    for event_name in fixture_loader.discover_all():
        fixtures = fixture_loader.load(event_name)

        # Each fixture should have multiple examples
        for i, fixture in enumerate(fixtures):
            result = parse(event_name, fixture)
            assert result is not None, f"{event_name} fixture[{i}] failed to parse"

            # Verify action-specific fields exist when present
            if "action" in fixture:
                assert result.action == fixture["action"]

            # Verify changes field exists when present (e.g., edited actions)
            if "changes" in fixture:
                assert hasattr(result, "changes"), f"{event_name} missing 'changes' attribute"


def test_nested_model_overrides_apply_recursively(monkeypatch, fixture_loader):
    """
    Verify that model overrides apply to nested objects.

    E.g., if we override User, does PR.user use the override?
    Tests that overrides apply to all User instances throughout the object tree.
    """

    class MyUser(User):
        @property
        def custom_field(self):
            return "custom"

    monkeypatch.setattr(octohook, "model_overrides", {User: MyUser})

    # Load fixture
    payload = fixture_loader.load("pull_request")[0]

    from octohook.events import PullRequestEvent

    event = PullRequestEvent(payload)

    # Test 1: Primary nested User object (pull_request.user)
    assert isinstance(event.pull_request.user, MyUser)
    assert event.pull_request.user.custom_field == "custom"

    # Test 2: Top-level sender User object
    assert isinstance(event.sender, MyUser)
    assert event.sender.custom_field == "custom"

    # Test 3: Repository owner User object (if present)
    if hasattr(event.repository, "owner") and event.repository.owner:
        assert isinstance(event.repository.owner, MyUser)
        assert event.repository.owner.custom_field == "custom"

    # Note: The fixture has assignee=None, so we can't test that path
    # This is acceptable as we've verified the override applies to multiple
    # User instances across different nesting levels


def test_malformed_payload_missing_required_fields():
    """
    Verify that parsing handles payloads with missing required fields gracefully.

    Tests that the parser doesn't crash when required fields are missing,
    which could happen if GitHub's webhook format changes.
    """
    # Minimal payload missing many expected fields
    malformed_payload = {
        "action": "opened",
        "sender": {"login": "user", "id": 123},
        # Missing: repository, pull_request, etc.
    }

    # Should not crash, but may return BaseWebhookEvent
    result = parse("pull_request", malformed_payload)
    assert result is not None
    assert isinstance(result, BaseWebhookEvent)


def test_unknown_event_type_returns_base_event():
    """
    Verify that completely unknown event types fall back to BaseWebhookEvent.

    Tests the fallback behavior when GitHub introduces new webhook events
    that octohook doesn't have models for yet.
    """
    payload = {
        "action": "some_new_action",
        "sender": {"login": "user", "id": 123},
    }

    result = parse("brand_new_event_type", payload)
    assert isinstance(result, BaseWebhookEvent)


def test_empty_handler_list_does_not_crash(isolated_decorator, fixture_loader):
    """
    Verify that handling a webhook with no registered handlers doesn't crash.

    Tests that the system gracefully handles webhooks when no handlers match.
    """
    # Don't register any handlers
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")

    # Should not crash
    isolated_decorator.handle_webhook("label", created_event)


def test_multiple_repository_filters(isolated_decorator, fixture_loader):
    """
    Verify that handlers can be registered for multiple specific repositories.

    Tests that repository filtering works when a handler targets multiple repos.
    """
    handler = Mock()
    target_repos = ["owner/repo-a", "owner/repo-b"]

    isolated_decorator.webhook(
        WebhookEvent.LABEL, [WebhookEventAction.CREATED], repositories=target_repos
    )(handler)

    # Test with repo-a
    fixtures = fixture_loader.load("label")
    created_event = json.loads(json.dumps(fixtures[0]))  # Deep copy
    created_event["repository"]["full_name"] = "owner/repo-a"

    isolated_decorator.handle_webhook("label", created_event)
    assert handler.call_count == 1

    # Test with repo-b
    created_event["repository"]["full_name"] = "owner/repo-b"
    isolated_decorator.handle_webhook("label", created_event)
    assert handler.call_count == 2

    # Test with repo-c (should not fire)
    created_event["repository"]["full_name"] = "owner/repo-c"
    isolated_decorator.handle_webhook("label", created_event)
    assert handler.call_count == 2  # Still 2, didn't increase


def test_debug_mode_overrides_normal_handlers_for_specific_event(
    isolated_decorator, fixture_loader
):
    """
    Verify that debug hooks completely override normal hooks for that specific event.

    Tests that debug mode is event-specific and all-or-nothing.
    """
    normal_handler = Mock()
    debug_handler = Mock()

    # Register both normal and debug handlers for LABEL
    isolated_decorator.webhook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])(
        normal_handler
    )
    isolated_decorator.webhook(
        WebhookEvent.LABEL, [WebhookEventAction.CREATED], debug=True
    )(debug_handler)

    # Handle label webhook
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")
    isolated_decorator.handle_webhook("label", created_event)

    # Only debug handler should fire
    debug_handler.assert_called_once()
    normal_handler.assert_not_called()


def test_debug_mode_does_not_affect_other_events(isolated_decorator, fixture_loader):
    """
    Verify that debug mode for one event doesn't affect handlers for other events.

    Tests that debug mode is truly event-specific.
    """
    label_normal_handler = Mock()
    label_debug_handler = Mock()
    issues_normal_handler = Mock()

    # Register debug hook for LABEL only
    isolated_decorator.webhook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])(
        label_normal_handler
    )
    isolated_decorator.webhook(
        WebhookEvent.LABEL, [WebhookEventAction.CREATED], debug=True
    )(label_debug_handler)

    # Register normal hook for ISSUES
    isolated_decorator.webhook(WebhookEvent.ISSUES, [WebhookEventAction.OPENED])(
        issues_normal_handler
    )

    # Handle label webhook - should only fire debug
    label_fixtures = fixture_loader.load("label")
    created_event = next(e for e in label_fixtures if e["action"] == "created")
    isolated_decorator.handle_webhook("label", created_event)

    label_debug_handler.assert_called_once()
    label_normal_handler.assert_not_called()

    # Handle issues webhook - should fire normal handler (no debug mode)
    issues_fixtures = fixture_loader.load("issues")
    opened_event = next(e for e in issues_fixtures if e["action"] == "opened")
    isolated_decorator.handle_webhook("issues", opened_event)

    issues_normal_handler.assert_called_once()


def test_debug_mode_with_repository_filter(isolated_decorator, fixture_loader):
    """
    Verify that debug mode works correctly with repository-specific handlers.

    Tests the combination of debug mode and repository filtering, which are
    independent features that should work together correctly.
    This addresses coverage gap at decorators.py lines 39-40.
    """
    debug_handler_any_repo = Mock()
    debug_handler_specific_repo = Mock()
    normal_handler = Mock()

    # Get the actual repository from the fixture
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")
    target_repo = created_event["repository"]["full_name"]

    # Register debug handler for any repository
    isolated_decorator.webhook(
        WebhookEvent.LABEL, [WebhookEventAction.CREATED], debug=True
    )(debug_handler_any_repo)

    # Register debug handler for specific repository
    isolated_decorator.webhook(
        WebhookEvent.LABEL,
        [WebhookEventAction.CREATED],
        repositories=[target_repo],
        debug=True,
    )(debug_handler_specific_repo)

    # Register normal handler (should not fire due to debug mode)
    isolated_decorator.webhook(
        WebhookEvent.LABEL, [WebhookEventAction.CREATED], repositories=[target_repo]
    )(normal_handler)

    # Handle webhook
    isolated_decorator.handle_webhook("label", created_event)

    # Both debug handlers should fire (ANY_REPO and specific repo match)
    debug_handler_any_repo.assert_called_once()
    debug_handler_specific_repo.assert_called_once()

    # Normal handler should not fire (overridden by debug mode)
    normal_handler.assert_not_called()


def test_wildcard_action_with_specific_action_and_repository_filter(
    isolated_decorator, fixture_loader
):
    """
    Verify that specific actions work correctly with repository filters.

    Tests that handlers can filter by both specific action and repository.
    This addresses coverage gap at decorators.py lines 50-54.
    """
    handler_specific = Mock()
    handler_wrong_repo = Mock()

    # Load fixtures and get actual repository name
    fixtures = fixture_loader.load("label")
    created_event = next(e for e in fixtures if e["action"] == "created")
    target_repo = created_event["repository"]["full_name"]
    wrong_repo = "other/repo"

    # Register handler for specific action on specific repository
    isolated_decorator.webhook(
        WebhookEvent.LABEL,
        [WebhookEventAction.CREATED],
        repositories=[target_repo],
    )(handler_specific)

    # Register handler for same action on different repository
    isolated_decorator.webhook(
        WebhookEvent.LABEL,
        [WebhookEventAction.CREATED],
        repositories=[wrong_repo],
    )(handler_wrong_repo)

    # Handle webhook with target repo
    isolated_decorator.handle_webhook("label", created_event)

    # Only the matching repo handler should fire
    handler_specific.assert_called_once()
    handler_wrong_repo.assert_not_called()

    # Now test with a different action to verify action filtering works
    edited_event = next(e for e in fixtures if e["action"] == "edited")
    isolated_decorator.handle_webhook("label", edited_event)

    # Neither handler should fire (they're registered for CREATED, not EDITED)
    assert handler_specific.call_count == 1  # Still 1 from before
    handler_wrong_repo.assert_not_called()

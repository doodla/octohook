import logging
from collections import defaultdict
from functools import wraps
from typing import List

from octohook.events import WebhookEvent, WebhookEventAction, parse

logger = logging.getLogger("octohook")

DEBUG = "debug"
ANY_REPO = "*"
ANY_ACTION = "*"


class _WebhookDecorator:
    """Internal class managing webhook handler registration and dispatch.

    Maintains a three-level handler registry: event -> action -> repository.
    Handles debug mode where only debug handlers fire for an event.
    """

    def __init__(self):
        self.handlers = defaultdict(  # event_name
            lambda: defaultdict(lambda: defaultdict(set))  # action  # repo  # handlers
        )

    def webhook(
        self,
        event: WebhookEvent,
        actions: List[WebhookEventAction] = None,
        repositories: List[str] = None,
        debug=False,
    ):
        """Decorator to register a function as a webhook handler.

        Args:
            event: The webhook event type to handle.
            actions: Optional list of actions to filter on. If None, handles all actions.
            repositories: Optional list of repository full names (owner/repo) to filter on.
            debug: If True, only this handler runs for the event (other handlers are skipped).

        Example:
            @hook(WebhookEvent.PULL_REQUEST, actions=[WebhookEventAction.OPENED])
            def on_pr_opened(event: PullRequestEvent):
                print(f"PR opened: {event.pull_request.title}")
        """

        def real_decorator(fn):
            @wraps(fn)
            def wrapper(*, event_name, payload):
                fn(parse(event_name, payload))

            repos = repositories or []

            if debug:
                if not repos:
                    self.handlers[event][DEBUG][ANY_REPO].add(wrapper)
                else:
                    for repo in repos:
                        self.handlers[event][DEBUG][repo].add(wrapper)

            if not actions:
                if not repos:
                    self.handlers[event][ANY_ACTION][ANY_REPO].add(wrapper)
                else:
                    for repo in repos:
                        self.handlers[event][ANY_ACTION][repo].add(wrapper)
            else:
                for action in actions:
                    if not repos:
                        self.handlers[event][action][ANY_REPO].add(wrapper)
                    else:
                        for repo in repos:
                            self.handlers[event][action][repo].add(wrapper)

            return wrapper

        return real_decorator

    def handle_webhook(self, event_name: str, payload: dict):
        """Dispatch a webhook payload to registered handlers.

        Finds all matching handlers for the event/action/repository combination
        and executes them sequentially. Exceptions are logged but don't stop execution.

        Args:
            event_name: The GitHub event name (e.g., "pull_request", "issues").
            payload: The raw webhook payload dictionary from GitHub.

        Example:
            handle_webhook("pull_request", request.json)
        """
        action_handlers = self.handlers[WebhookEvent(event_name)]

        # These handlers are invoked all the time.
        handlers = action_handlers[ANY_ACTION][ANY_REPO].copy()

        repo_name = payload["repository"]["full_name"]

        if payload.get("action") is not None:
            handlers.update(
                action_handlers[WebhookEventAction(payload["action"])][ANY_REPO]
            )
            handlers.update(
                action_handlers[WebhookEventAction(payload["action"])][repo_name]
            )

        if action_handlers[DEBUG]:
            logger.info("Debug handlers found.")
            handlers = action_handlers[DEBUG][ANY_REPO].copy()
            handlers.update(action_handlers[DEBUG][repo_name])

        for handler in handlers:
            # noinspection PyBroadException
            try:
                logger.info(f"Evaluating {handler.__name__}")
                handler(event_name=event_name, payload=payload)
            except Exception:
                logger.exception(f"Exception when handling {handler.__name__}")


_decorator = _WebhookDecorator()

hook = _decorator.webhook
handle_webhook = _decorator.handle_webhook

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/octohook) ![PyPI - Status](https://img.shields.io/pypi/status/octohook) ![PyPI - License](https://img.shields.io/pypi/l/octohook)

# Octohook

Octohook parses [GitHub webhook](https://docs.github.com/en/webhooks) payloads into typed Python classes and provides a decorator-based system for routing webhooks to handlers.

## Installation

```bash
pip install octohook
```

## Quick Start

Define a handler for pull request events:

```python
# handlers.py
from octohook import hook, WebhookEvent, WebhookEventAction
from octohook.events import PullRequestEvent

@hook(WebhookEvent.PULL_REQUEST, [WebhookEventAction.OPENED])
def on_pr_opened(event: PullRequestEvent):
    print(f"PR opened: {event.pull_request.title}")
```

Wire it up in your web framework (example using Flask):

```python
# app.py
from flask import Flask, request, Response
import octohook

app = Flask(__name__)
octohook.setup(modules=["handlers"])

@app.route('/webhook', methods=['POST'])
def webhook():
    github_event = request.headers.get('X-GitHub-Event')
    octohook.handle_webhook(event_name=github_event, payload=request.json)
    return Response("OK", status=200)
```

## Usage

### Manual Parsing

Use `octohook.parse()` when you want direct control over webhook handling:

```python
from flask import Flask, request, Response
import octohook
from octohook.events import PullRequestEvent

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    github_event = request.headers.get('X-GitHub-Event')
    event = octohook.parse(github_event, request.json)

    if isinstance(event, PullRequestEvent):
        return Response(event.pull_request.title, status=200)

    return Response("OK", status=200)
```

### Decorator Routing

Use `@hook` when you have multiple handlers or want cleaner routing. The decorator takes four parameters:

- `event`: A `WebhookEvent` enum value (required)
- `actions`: List of `WebhookEventAction` values (optional - omit to match any action)
- `repositories`: List of repository full names to filter on (optional)
- `debug`: When `True`, only debug hooks fire for that event (default: `False`)

```python
from octohook import hook, WebhookEvent, WebhookEventAction
from octohook.events import PullRequestEvent

@hook(WebhookEvent.PULL_REQUEST, [WebhookEventAction.OPENED, WebhookEventAction.EDITED])
def on_pr_change(event: PullRequestEvent):
    print(event.pull_request.title)
```

`on_pr_change()` is called with the parsed `PullRequestEvent` whenever a `pull_request` webhook arrives with an `opened` or `edited` action.

If you omit the actions parameter, the handler fires for any action. For events like `push` that have no action field, always omit actions.

#### Handler Discovery

Use `setup()` to load handlers from your modules:

```python
import octohook

# Recursively imports handlers from the specified modules
octohook.setup(modules=["hooks", "webhooks.github"])
```

#### Repository Filtering

Filter hooks to specific repositories using their full name (e.g., `"owner/repo"`):

```python
from octohook import hook, WebhookEvent
from octohook.events import PushEvent

@hook(WebhookEvent.PUSH, repositories=["myorg/backend", "myorg/frontend"])
def on_push(event: PushEvent):
    print(f"Push to {event.repository.full_name}")
```

#### Debug Mode

Set `debug=True` on any hook to make only debug hooks fire for that event type:

```python
from octohook import hook, WebhookEvent
from octohook.events import PullRequestEvent

@hook(WebhookEvent.PULL_REQUEST, debug=True)
def debug_pr(event: PullRequestEvent):
    print(event)  # Only this runs for PR events when debug=True
```

#### Complete Example

```python
# hooks/github.py
from octohook import hook, WebhookEvent, WebhookEventAction
from octohook.events import LabelEvent, PullRequestEvent

@hook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])
def on_label_created(event: LabelEvent):
    print(f"Label created: {event.label.name}")

@hook(WebhookEvent.PULL_REQUEST)
def on_any_pr_event(event: PullRequestEvent):
    print(f"PR #{event.number}: {event.action}")
```

```python
# app.py
from flask import Flask, request, Response
import octohook

app = Flask(__name__)

octohook.setup(modules=["hooks"])

@app.route('/webhook', methods=['POST'])
def webhook():
    github_event = request.headers.get('X-GitHub-Event')
    octohook.handle_webhook(event_name=github_event, payload=request.json)
    return Response("OK", status=200)
```

- `handle_webhook` runs handlers sequentially and blocks until complete.
- Exceptions are logged to `logging.getLogger('octohook')` but don't stop execution.

## URL Helpers

GitHub webhook payloads include URL templates with placeholders:

```json
{
  "repository": {
    "archive_url": "https://api.github.com/repos/owner/repo/{archive_format}{/ref}"
  }
}
```

Octohook models provide methods to interpolate these templates:

```python
# event.repository is a Repository model with helper methods
>>> event.repository.archive_url("tarball")
'https://api.github.com/repos/owner/repo/tarball'
>>> event.repository.archive_url("tarball", "main")
'https://api.github.com/repos/owner/repo/tarball/main'
```

## Limitations

GitHub sends different payload structures depending on the event type and action. Not all fields are present in all payloads, so octohook uses `Optional` types extensively. Fields are only marked as required if they appear in all known payloads for that model.

For example, the `changes` key only appears with `edited` actions. For other actions, `event.changes` is `None`.

Current test coverage is documented in [tests/TestCases.md](tests/TestCases.md). PRs adding missing event payloads are welcome.

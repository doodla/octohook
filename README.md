![PyPI - Python Version](https://img.shields.io/pypi/pyversions/octohook) ![PyPI - Status](https://img.shields.io/pypi/status/octohook) ![PyPI - License](https://img.shields.io/pypi/l/octohook)

# Octohook

Octohook makes working with incoming [Github Webhooks](https://developer.github.com/v3/activity/events/types/) extremely easy. 

It parses the incoming payload into Python classes to allow for auto-complete and other goodies. For example, `octohook` provides functions for payload values which require string interpolation.

For example, almost every repository payload has an `archive_url` with some required and conditional parameters.
```json
{
  "repository" : {
    "archive_url": "https://api.github.com/repos/doodla/octohook-playground/{archive_format}{/ref}"
  }
}

```

The `Repository` model provides an `archive_url()` method which has `archive_format` as an argument and `ref` as an optional variable.

```
>>> repo.archive_url("hello")
https://api.github.com/repos/doodla/octohook-playground/hello
>>> repo.archive_url("hello","world")
https://api.github.com/repos/doodla/octohook-playground/hello/world"
```

## Gotchas

Github doesn't send consistent payloads for each model necessitating that the non-optional model type hints conform to the least common denominator. 

Depending on the event type, you can get more information for a particular model, or less.
For example, Github sends a `changes` key with some payloads with the `edited` action. For other actions, the key is not present. In such cases, our `event.changes` is `None`.

This can happen for arbitrary payloads, so I'd suggest tailoring your code to the expected incoming webhook.

If anyone has a good suggestion on how to tackle this issue, feel free to email me, or create a PR!

Because Github sends different payloads for a combination of `event type` and `action`, unless I have access to all the variations, I cannot be sure that the corresponding model is correct.

Current coverage is documented [here](tests/TestCases.md). If you can provide any of the missing events, please make a PR.
## Sample Usage

#### app.py
```python
from flask import Flask, request, Response
import octohook
from octohook.events import PullRequestEvent

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    github_event = request.headers.get('X-GitHub-Event') # pull_request
    
    # Assuming the incoming event was a PullRequestEvent
    event : PullRequestEvent = octohook.parse(github_event, request.json)

    # Do work with this event

    return Response(event.pull_request.head.user.name, status=200)
```

### @hook
Alternatively, you can also let `octohook` do the heavy lifting of finding and executing the appropriate handlers for any given webhook.

The `@hook` decorator takes in three parameters, the `WebhookEvent`, a list of `WebhookEventAction`s and a `debug` flag (defaults to `False`). 

Any function this decorator is applied to is invoked whenever you receive an event with the specified `WebhookEvent` and a listed `WebhookEventAction`.

If you set `debug=True` on any `@hook`, only those hooks fire for the corresponding webhook event.

```python
@hook(WebhookEvent.PULL_REQUEST,[WebhookEventAction.CREATED, WebhookEventAction.EDITED])
def work(event: PullRequestEvent):
    pass
```

`work()` is automatically called with the parsed `PullRequestEvent` anytime you receive a webhook event with `X-Github-Event: pull_request` and it has any of the `created` or `edited` actions.

If you don't specify a list of actions, then the function is invoked for _any_ action. For some events like `Push`, which do not have an `action`, take care not to specify any actions in the decorator. 

#### hooks/do_something.py
```python
from octohook import hook,WebhookEvent,WebhookEventAction
from octohook.events import LabelEvent,PullRequestEvent

@hook(WebhookEvent.LABEL, [WebhookEventAction.CREATED])
def runs_when_label_event_with_created_action_is_received(event: LabelEvent):
    print(event.label.name)

@hook(WebhookEvent.PULL_REQUEST)
def runs_when_pull_request_event_with_any_action_is_received(event: PullRequestEvent):
    print(event.changes)
```
#### app.py
```python
from flask import Flask, request, Response

import octohook

app = Flask(__name__)

octohook.load_hooks(["hooks"]) 

@app.route('/webhook', methods=['POST'])
def webhook():
    github_event = request.headers.get('X-GitHub-Event')
    
    octohook.handle_webhook(event_name=github_event, payload=request.json)

    return Response("OK", status=200)
```

**Note**

`load_hooks` can only be called once and raises a `RuntimeError` if called multiple times. This is because every time it parses a given module structure, it creates new instances of the functions. So if you parse them multiple times, your handlers will get invoked multiple times.
```python
load_hooks(['module_a','module_b','path_a'])
load_hooks(['path_a']) # RuntimeError
``` 

`handle_hooks` goes through all the handlers sequentially and blocks till everything is done. It does wrap the method in a `try/catch`. Any exceptions are logged to `logging.getLogger('octohook')`. You can configure the output stream of this logger to capture the logs.

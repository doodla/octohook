![PyPI - Python Version](https://img.shields.io/pypi/pyversions/octohook) ![PyPI - Status](https://img.shields.io/pypi/status/octohook) ![PyPI - License](https://img.shields.io/pypi/l/octohook)

## Octohook

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

### Gotchas

Github doesn't send consistent payloads for each model. Depending on the event type, you can get more information for a particular model, or less.
For example, Github sends a `changes` key with some payloads with the `edited` action. For other actions, the key is not present. In such cases, our `event.changes` is `None`.

This can happen for arbitrary payloads, so I'd suggest tailoring your code to the expected incoming webhook.

If anyone has a good suggestion on how to tackle this issue, feel free to email me, or create a PR!

Because Github sends different payloads for a combination of `event type` and `action`, unless I have access to all the variations, I cannot be sure that the corresponding model is correct.

Current coverage is documented [here](tests/TestCases.md). If you can provide any of the missing events, please make a PR.
### Sample Usage

#### app.py
```python
from flask import Flask, request, Response
import octohook
from octohook.events import PullRequestEvent
from octohook.models import PullRequest, Repository

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    github_event = request.headers.get('X-GitHub-Event') # pull_request
    
    # Assuming the incoming event was a PullRequestEvent
    event : PullRequestEvent = octohook.parse(github_event, request.json)

    return Response(event.pull_request.head.user.name, status=200)
```


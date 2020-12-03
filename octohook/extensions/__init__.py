from octohook.extensions.github import SimpleGithubClient
from octohook.extensions.issue import init_issue_extensions
from octohook.extensions.pull_request import init_pull_request_extensions
from octohook.extensions.release import init_release_extensions
from octohook.extensions.repository import init_repository_extensions


def initialize_extensions(github_token: str):
    client = SimpleGithubClient(github_token)

    init_issue_extensions(client)
    init_pull_request_extensions(client)
    init_release_extensions(client)
    init_repository_extensions(client)

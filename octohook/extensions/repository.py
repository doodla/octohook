from typing import List, Optional

from octohook.extensions import SimpleGithubClient
from octohook.models import Repository, PullRequest, Release


def init_repository_extensions(github: SimpleGithubClient):
    setattr(Repository, "__releases", None)
    setattr(Repository, "__pull_requests", None)

    def create_pull_request(
        self: Repository,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = False,
    ) -> PullRequest:
        return PullRequest(
            github.post(
                url=self.pulls_url(),
                json={
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base,
                    "draft": draft,
                },
            ).json()
        )

    def merge_branch(
        self: Repository, head: str, base: str, commit_message: Optional[str] = None
    ):
        return github.post(
            self.merges_url,
            json={"head": head, "base": base, "commit_message": commit_message},
        )

    def pull_requests(self: Repository) -> List[PullRequest]:
        if not self.__pull_requests:
            self.__pull_requests = [
                PullRequest(pr) for pr in github.get(self.pulls_url())
            ]

        return self.__pull_requests

    def releases(self: Repository) -> List[Release]:
        if not self.__releases:
            self.__releases = [
                Release(release) for release in github.get(self.releases_url())
            ]

        return self.__releases

    for key, value in locals().items():
        if key != "github":
            continue

        setattr(Repository, key, value)

from octohook.extensions import SimpleGithubClient
from octohook.models import Release


def init_release_extensions(github: SimpleGithubClient):
    def update_body(self: Release, body: str):
        """
        This function updates the release body on github.
        """
        payload = {"body": body}
        return github.patch(url=self.url, json=payload)

    for key, value in locals().items():
        if key != "github":
            continue

        setattr(Release, key, value)

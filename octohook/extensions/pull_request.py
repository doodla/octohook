from collections import Counter
from typing import List, Dict, Optional

from octohook.extensions import SimpleGithubClient
from octohook.models import PullRequest, Review


def init_pull_request_extensions(github: SimpleGithubClient):
    setattr(PullRequest, "__reviews", None)
    setattr(PullRequest, "__files", None)

    def label_names(self: PullRequest) -> List[str]:
        return [label.name for label in self.labels]

    def apply_label(self: PullRequest, label: str):
        payload = {"labels": list(set(self.label_names() + [label]))}
        return github.patch(url=self.issue_url, json=payload)

    def apply_labels(self: PullRequest, labels: List[str]):
        payload = {"labels": list(set(self.label_names() + labels))}
        return github.patch(url=self.issue_url, json=payload)

    def remove_label(self: PullRequest, label: str):
        labels = self.label_names()
        if label in labels:
            labels.remove(label)

            self.apply_labels(labels)

    def remove_labels(self: PullRequest, labels: List[str]):
        original_labels_set = set(self.label_names())
        incoming_label_set = set(labels)

        new_label_set = original_labels_set - incoming_label_set
        if new_label_set != original_labels_set:
            self.apply_labels(list(new_label_set))

    def reviews_count(self: PullRequest) -> Dict[str, int]:
        if not self.__reviews:
            self.__reviews = [
                Review(review) for review in github.get(url=f"{self.url}/reviews")
            ]

        user_review_state = {}

        # reviews contains ALL the recent states, which can include multiple actions per user.
        # We map the user to their latest review state
        for review in self.__reviews:
            user_review_state[review.user.name] = review.state

        return Counter(user_review_state.values())

    def modified_files(self: PullRequest) -> List[str]:
        if not self.__files:
            self.__files = github.get(f"{self.url}/files")

        return [file["filename"] for file in self.__files]

    def send_status(
        self: PullRequest,
        context: str,
        state: str,
        description: str,
        target_url: Optional[str] = None,
    ):
        payload = {
            "description": description,
            "state": state,
            "context": context,
            "target_url": target_url,
        }

        return github.post(url=self.statuses_url, json=payload)

    def request_reviews(
        self: PullRequest,
        reviewers: Optional[List[str]] = None,
        team_reviewers: Optional[List[str]] = None,
    ):
        if not reviewers:
            reviewers = []

        if not team_reviewers:
            team_reviewers = []

        if reviewers or team_reviewers:
            return github.post(
                f"{self.url}/requested_reviewers",
                {"reviewers": reviewers, "team_reviewers": team_reviewers},
            )

    for key, value in dict(locals()).items():
        if key == "github":
            continue

        setattr(PullRequest, key, value)

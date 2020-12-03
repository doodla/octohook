from typing import List

from octohook.extensions import SimpleGithubClient
from octohook.models import Issue


def init_issue_extensions(github: SimpleGithubClient):
    def apply_label(self: Issue, label: str):
        payload = {"labels": list(set([lbl.name for lbl in self.labels] + [label]))}
        return github.patch(url=self.url, json=payload)

    def apply_labels(self: Issue, labels: List[str]):
        payload = {"labels": list(set([lbl.name for lbl in self.labels] + labels))}
        return github.patch(url=self.url, json=payload)

    def remove_label(self: Issue, label: str):
        labels = [label.name for label in self.labels]
        if label in labels:
            labels.remove(label)

            self.apply_labels(labels)

    def remove_labels(self: Issue, labels: List[str]):
        original_labels_set = {label.name for label in self.labels}
        incoming_label_set = set(labels)

        new_label_set = original_labels_set - incoming_label_set
        if new_label_set != original_labels_set:
            self.apply_labels(list(new_label_set))

    for key, value in locals().items():
        if key != "github":
            continue

        setattr(Issue, key, value)

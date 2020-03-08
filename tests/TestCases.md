# Test Case Availability
This document tracks the presence of all the test cases making up the different kinds of webhook payloads.

## CheckRunEvent

- [ ] created
- [ ] completed
- [ ] rerequested
- [ ] requested_action

## CheckSuiteEvent

- [ ] completed
- [ ] requested
- [ ] rerequested

## CommitCommentEvent

- [x] created

## ContentReferenceEvent

- [x] created

## CreateEvent
### Types
- [x] Branch
- [x] Tag

## DeleteEvent
Covered

## DeployKey

- [x] created
- [x] deleted

## DeploymentEvent

- [x] created

## DeploymentStatusEvent

- [x] created

## ForkEvent
Covered

## GithubAppAuthorization

- [x] revoked

## GollumEvent

### Page Action
- [x] create
- [x] update

## InstallationEvent

- [ ] created
- [x] deleted
- [ ] new_permissions_accepted

## InstallationRepositoriesEvent

- [x] added
- [ ] removed

## IssueCommentEvent

- [x] created
- [x] edited
- [x] deleted

## IssuesEvent

- [x] opened
- [x] edited
- [x] deleted
- [x] pinned
- [x] unpinned
- [x] closed
- [x] reopened
- [x] assigned
- [x] unassigned
- [x] labeled
- [x] unlabeled
- [x] locked
- [x] unlocked
- [x] transferred
- [x] milestoned
- [x] demilestoned

## LabelEvent

- [x] created
- [x] edited
- [x] deleted

## MarketplacePurchaseEvent

- [x] purchased
- [ ] cancelled
- [ ] pending_change
- [ ] pending_change_cancelled
- [ ] changed

## MemberEvent

- [x] added
- [x] removed
- [ ] edited

## MembershipEvent

- [ ] added
- [x] removed

## MetaEvent

- [x] deleted

## MilestoneEvent

- [x] created
- [x] closed
- [x] opened
- [x] edited
- [x] deleted

## OrganizationEvent

- [ ] deleted
- [ ] renamed
- [x] member_added
- [ ] member_removed
- [ ] member_invited

## OrgBlockEvent

- [x] blocked
- [ ] unblocked

## PackageEvent

- [x] published
- [ ] updated

## PageBuildEvent
Covered

## ProjectCardEvent

- [x] created
- [x] edited
- [x] moved
- [x] converted
- [x] deleted

## ProjectColumnEvent

- [x] created
- [x] edited
- [x] moved
- [x] deleted

## ProjectEvent

- [x] created
- [x] edited
- [x] closed
- [x] reopened
- [x] deleted

## PublicEvent
Covered

## PullRequestEvent

- [x] assigned
- [x] unassigned
- [x] labeled
- [x] unlabeled
- [x] opened
- [x] closed
- [x] edited
- [x] reopened
- [x] synchronize
- [x] ready_for_review
- [x] locked
- [x] unlocked
- [x] review_requested
- [x] review_request_removed

## PullRequestReviewEvent

- [x] submitted
- [x] edited
- [x] dismissed

## PullRequestReviewCommentEvent

- [x] created
- [x] edited
- [x] deleted

## PushEvent
Covered

## ReleaseEvent

- [ ] published
- [ ] unpublished
- [ ] created
- [ ] edited
- [ ] deleted
- [ ] prereleased

## RepositoryDispatchEvent

- [ ] on-demand-test

## RepositoryEvent

- [ ] created
- [ ] archived
- [ ] unarchived
- [ ] renamed
- [ ] edited
- [ ] transferred
- [ ] publicized
- [ ] privatized
- [ ] deleted

## RepositoryImportEvent
Covered

## RepositoryVulnerabilityAlertEvent

- [ ] create
- [ ] dismiss
- [ ] resolve

## SecurityAdvisoryEvent

- [ ] published
- [ ] updated
- [ ] performed

## SponsorshipEvent

- [ ] created
- [ ] cancelled
- [ ] edited
- [ ] tier_changed
- [ ] pending_cancellation
- [ ] pending_tier_change


## StarEvent

- [x] created
- [x] deleted

## StatusEvent

Seems like this one has no variations(?)

## TeamEvent

- [ ] created
- [ ] deleted
- [ ] edited
- [ ] added_to_repository
- [ ] removed_from_repository

## TeamAddEvent
Covered

## WatchEvent

- [x] started

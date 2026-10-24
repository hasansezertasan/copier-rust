# Release flow

How the generated release workflow is shaped and why. Carried from the design notes in `docs/design.md`, which were proven on amb through real releases.

## One workflow for release, builds and publish

**Id:** 105aab70-0087-402e-8e46-83b82c27875d
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Decisions"
**Revisit when:** a personal access token or app token replaces `GITHUB_TOKEN` for releases

The release job, the native builds, the publish steps and the final "publish the release" step all live in one `release.yml`.

**Reason:** tags and releases created with `GITHUB_TOKEN` do not trigger other workflows, so a split across workflows could not chain.

**Rejected alternative:** separate workflows for release, build and publish. Rejected because they would need a personal access token to be triggered.

## Draft first, publish last

**Id:** 813bc40c-8510-417a-858f-1e4d8e244dc4
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Decisions"

release-please runs with `draft: true` and `force-tag-creation: true`; the last step of the workflow publishes the draft, after every asset is uploaded to it.

**Reason:** with release immutability on, tag and assets are locked the moment the release is published, so assets must be uploaded to the draft beforehand.

**Rejected alternative:** unknown. The design notes name no alternative; uploading after publishing is ruled out by immutability itself.

## Build the tagged commit, not the triggering one

**Id:** 67347b92-e608-4940-84fb-71f4d6dfea0f
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Traps" 2

Build jobs check out release-please's `sha` output instead of the commit that triggered the run.

**Reason:** the attested binaries and the published crate then match the tag.

**Rejected alternative:** unknown. The design notes name no alternative.

## A failed run leaves a draft and a tag

**Id:** 1e387fce-005f-4ba6-8cb0-ff93948d80c3
**Type:** constraint
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Traps" 4
**Revisit when:** GitHub changes how immutable releases or tag reuse behave

An unpublished draft burns nothing: delete the draft with its tag and revert the release commit's version bump, so release-please proposes the same version again. A published immutable release's tag can never be reused, so recovery has to happen before the final publish step.

## Release PRs opened with GITHUB_TOKEN do not run CI

**Id:** 9e9e5709-263f-45ea-8df8-977c7eb524d4
**Type:** constraint
**Type:** workaround
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Traps" 6
**Revisit when:** a token that triggers workflows is adopted for release-please

Required checks stay pending on release-please's pull request, because a PR opened with `GITHUB_TOKEN` triggers no workflow runs. The generated ruleset lets repository admins bypass through a pull request.

**Reason:** unknown for the bypass itself; see "One workflow for release, builds and publish" for why no personal access token is used (the design notes list both traps but do not link them).

## The release-please branch name carries the component

**Id:** 2a790be9-57e2-4627-b58d-37e91d78e703
**Type:** constraint
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Traps" 3

The branch is `release-please--branches--main--components--<crate>`. The phantom-PR lookup matches by prefix and lists enough PRs (`--limit 200`), because `gh pr list` returns only 30 by default.

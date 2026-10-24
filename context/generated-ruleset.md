# Generated ruleset

What the branch ruleset shipped to generated projects requires.

## Which checks the main ruleset requires

**Id:** 0e3d7d26-fb7a-4487-926c-e2b9ca996e85
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** the description of the ruleset pull request (found on amb's adoption PR); `docs/design.md`

The generated ruleset requires the `ci.yml` jobs and `Dependency review`, and requires `Package check` only when `include_crates_publish` is on, which is why `main.json` is a `.jinja`. It does not require the `Build` jobs from `release-build-check.yml`. `REPOSITORY_SETUP.md` says to enable the dependency graph before applying the ruleset.

**Reason:** a failing `cargo publish --dry-run` or a newly introduced vulnerable dependency must not be able to merge; `Package check` does not exist without crates publishing, and the dependency review fails without the dependency graph.

**Rejected alternative:** unknown. No alternative is recorded.

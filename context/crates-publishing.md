# crates.io publishing

How the generated release workflow publishes to crates.io.

## Trusted publishing, no stored token

**Id:** b2ce283f-e8eb-45fd-83c7-0fad9635abf1
**Type:** decision
**Type:** constraint
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Decisions" and "Traps" 5; `copier.yml` help for `include_crates_publish`
**Revisit when:** crates.io supports trusted publishing for a crate that does not exist yet

The publish job exchanges its OIDC token through `rust-lang/crates-io-auth-action`. Trusted publishing only works for a crate that already exists, so `REPOSITORY_SETUP.md` has the author publish the `0.0.0` placeholder once from their machine, which also claims the name, and then configure the trusted publisher. The publish environment is `publish`, restricted to `main`. The first publish needs a verified email on the crates.io account.

**Reason:** no long-lived registry token is stored in the repository.

**Rejected alternative:** a stored crates.io API token. Not recorded in the design notes as considered; the exception that remains is the one-off local placeholder publish.

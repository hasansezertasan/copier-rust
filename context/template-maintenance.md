# Template maintenance

How this repository keeps the template and its seeds honest.

## Renovate freezes everything under `template/`

**Id:** 2385e853-19ed-40d8-9ff6-2a77d450109f
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `.github/renovate.json` rule description; `docs/design.md`, "Decisions"

Renovate is told to leave `template/**` alone. The pins inside it are seeds; refresh them by hand when cutting a release of the template.

**Reason:** each generated project ships its own Renovate config and owns its bumps, and managing them here too makes `copier update` conflict: Copier's 3-way merge sees the template render and the downstream file moving the same literal to different values.

**Rejected alternative:** letting Renovate bump the seeds here, rejected because of those merge conflicts.

## amb is the reference render

**Id:** b03013a6-00bf-4e54-bacd-5fd99d9404f8
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, intro and "Checking the template against amb"; `AGENTS.md`
**Revisit when:** amb stops being the proving ground for the release flow

The workflows were built and proven on amb through real releases, and this template generalises them. After changing one, render with amb's answers and diff against amb before trusting it.

**Reason:** the flow was proven by real releases there, where its traps were found.

**Rejected alternative:** unknown. No alternative is recorded.

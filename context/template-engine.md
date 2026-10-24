# Template engine

How the Copier payload is rendered and why it is configured the way it is.

## Custom Jinja delimiters

**Id:** ce393e31-07fb-4081-961b-b8bdc4da63f6
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Template traps" 1; `copier.yml` `_envops`

The payload renders with `[[ ]]`, `[% %]` and `[# #]`. They also apply to the expressions in `copier.yml` itself, and a literal `[[` in a rendered file (Cargo's `[[bin]]`, bash `[[ ]]`) is wrapped in `[% raw %]...[% endraw %]`.

**Reason:** the generated workflows contain `${{ }}` and bash `[[ ]]`, which collide with Jinja's defaults.

**Rejected alternative:** Jinja's default delimiters, rejected because of that collision.

## Only `.jinja` files are rendered

**Id:** 67f3b7b3-37ca-4e1e-9dd5-db450dc4162b
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Template traps" 3; `AGENTS.md`

Files without the `.jinja` suffix are copied byte for byte, so a file with no variables does not get the suffix.

**Reason:** bash such as `check-branch-name.yml` survives untouched, with no escaping.

**Rejected alternative:** unknown. No alternative is recorded.

## `trim_blocks` and `lstrip_blocks` are on

**Id:** 596f237e-e3a2-4457-b44f-7f16def74dbe
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `copier.yml` `_envops` comment; `AGENTS.md`; the description of the LICENSE newline pull request

Block tags on their own line leave no blank lines behind. The newline after a block tag, `[% endraw %]` included, is dropped, so a blank line is needed after `[% endraw %]` or `[[bin]]` glues onto the next line. The `-` whitespace-control markers are not needed and must not be used: they also stripped the newline before the tag and left a rendered LICENSE with no final newline.

**Reason:** output files render clean without per-tag whitespace markers.

**Rejected alternative:** per-tag `-` whitespace control, rejected because it removed a newline that had to stay.

## No `_tasks` in `copier.yml`

**Id:** 0af11a45-fd6b-4c72-ad34-081b5e5c203a
**Type:** decision
**Type:** constraint
**Status:** active
**Evidence:** confirmed
**Source:** `copier.yml`; `docs/design.md`, "Decisions"; `AGENTS.md`
**Revisit when:** Renovate's copier manager can pass `--trust`

Neither this template nor its generated projects run Copier tasks.

**Reason:** a task makes the template unsafe and forces `--trust`, which Renovate's copier manager does not pass, so Renovate could no longer open `copier update` pull requests.

**Rejected alternative:** unknown. Tasks themselves are what is ruled out; the next steps are printed through `_message_after_copy` instead.

## What a generated project owns after the first render

**Id:** 89cd9e0d-d2ec-44ec-a8a7-13bcc39f704f
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `copier.yml` `_skip_if_exists` comment; `AGENTS.md`

`_skip_if_exists` lists `Cargo.toml`, `Cargo.lock`, `src`, `README.md`, `AGENTS.md` and the release-please manifest. Anything the template must keep refreshing, such as the workflows, stays out of it.

**Reason:** `copier update` must not fight a project's own dependencies, sources or release state.

**Rejected alternative:** unknown. No alternative is recorded.

## The answers-file template lives in the payload

**Id:** d5865c8a-ef78-40f7-b557-15a14cac8edf
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `AGENTS.md`

`template/[[ _copier_conf.answers_file ]].jinja` is shipped in the payload.

**Reason:** it is what lets generated projects run `copier update`.

**Rejected alternative:** unknown. No alternative is recorded.

## `copyright_year` is a visible question

**Id:** e072f67b-2899-4f3b-9d63-6f5e7c7a5fd4
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `copier.yml` comment above `copyright_year`

The first copyright year is asked, not computed, and rendered as `<year>-present`.

**Reason:** Copier only stores asked questions in the answers file, so a hidden default would be re-evaluated and drift on every `copier update`; the `-present` form keeps the LICENSE from going stale.

**Rejected alternative:** a hidden question with a computed default, rejected because it drifts.

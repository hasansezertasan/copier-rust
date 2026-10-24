# Design notes

The release flow in `template/` is not new: it was built and proven on
[amb](https://github.com/hasansezertasan/amb) through real releases, and this template generalises it.
These notes record the decisions and the traps, so they are not rediscovered.

## Decisions

- **release-please, all in one workflow.** The release job, the native builds, the publish steps and the final
  "publish the release" step live in one `release.yml`. Tags and releases created with `GITHUB_TOKEN` do not
  trigger other workflows, so splitting them would need a personal access token; one workflow needs none.
- **Draft first, publish last.** release-please runs with `draft: true` and `force-tag-creation: true`. With
  release immutability on, tag and assets are locked the moment the release is published, so assets must be
  uploaded to the draft beforehand.
- **Native runners, glibc only.** System libraries (ALSA for audio, for example) link dynamically, so musl and
  cross builds are not offered. `apt_packages` installs what the build needs.
- **Trusted publishing, no stored token.** The publish job exchanges its OIDC token through
  `rust-lang/crates-io-auth-action`. It only works for a crate that already exists, so
  `REPOSITORY_SETUP.md` has the author publish the `0.0.0` placeholder once from their machine, which also
  claims the name, and then configure the trusted publisher. The publish environment is `publish`, restricted
  to `main`.
- **Release assets work with mise unconfigured.** `<bin>-<target>.tar.gz` (`.zip` on Windows) holding one
  `<bin>-<target>/` directory, a `.sha256` each, and an SBOM. mise's `github:` backend picks the asset by OS
  and architecture, strips the single top-level directory and verifies attestations.
- **No `_tasks`.** A task makes the template unsafe and forces `--trust`, which Renovate's copier manager does
  not pass.

- **The pins inside `template/` are seeds.** Renovate is told to leave `template/**` alone (see
  `.github/renovate.json`): each generated project ships its own Renovate config and owns its bumps, and
  managing them here too would make `copier update` conflict. Refresh the seeds by hand when cutting a
  release of the template.

## Traps

Each of these cost a failed run or a broken release on amb.

1. **Windows runners default to PowerShell.** `"$TARGET"` stays empty there, so the toolchain install ran with
   an empty target. Every step that expands a variable runs with `shell: bash`. The release build check builds
   and packages every target in pull requests so this surfaces before a release.
2. **Build the tagged commit.** Build jobs check out release-please's `sha` output, not the commit that
   triggered the run, so attested binaries and the published crate match the tag.
3. **The release-please branch carries the component**, `release-please--branches--main--components--<crate>`.
   The phantom-PR lookup matches by prefix and lists enough PRs (`--limit 200`; `gh pr list` returns 30).
4. **A failed run leaves a draft and a tag.** An unpublished draft burns nothing: delete it with its tag and
   revert the release commit's version bump, so release-please proposes the same version again. A published
   immutable release's tag can never be reused.
5. **crates.io needs a verified email** on the account before anything can be published.
6. **Release PRs opened with `GITHUB_TOKEN` cannot satisfy every required check.** Their `pull_request` workflows
   start in an approval-required state (`action_required`) and run once a user with write access approves them.
   `Validate PR title` and `Validate branch name` run on `pull_request_target`, which release-please's own
   creation and updates (made with `GITHUB_TOKEN`) never trigger, so they stay pending. Reopening the PR by hand
   starts both and editing its title starts the title check, but the ruleset also lets repository admins bypass
   through a pull request, which is how the release PR is merged.
7. **mise `minimum_release_age`** can hide a fresh release from `@latest`, and the versions host can lag a few
   hours; `MISE_USE_VERSIONS_HOST=0` asks GitHub directly.

## Template traps

1. **Custom delimiters.** The generated workflows contain `${{ }}` and bash `[[ ]]`, so the payload renders with
   `[[ ]]`, `[% %]` and `[# #]`. The delimiters also apply to expressions in `copier.yml`.
2. **`trim_blocks` swallows the newline after a block tag**, including `[% endraw %]`; add a blank line after
   it or `[[bin]]` glues onto the next line.
3. **Only `.jinja` files are rendered.** Others are copied byte for byte, which is why the bash in
   `check-branch-name.yml` survives untouched.
4. **mise shims fail in an untrusted repo.** Run `copier`, `uv` and `python3` from outside, or `mise trust`.

## Checking the template against amb

The workflows are derived from amb. After changing one, render with amb's answers and diff:

```bash
cd /tmp && copier copy --defaults --overwrite --vcs-ref=HEAD \
  -d github_user=hasansezertasan -d github_repo_name=amb \
  -d author_email=hasansezertasan@gmail.com -d copyright_year=2026 \
  -d short_description="A terminal ambient-sound mixer" \
  -d apt_packages="libasound2-dev pkg-config" \
  path/to/copier-rust /tmp/amb-render
diff path/to/amb/.github/workflows/release.yml /tmp/amb-render/.github/workflows/release.yml
```

The expected differences are the generic "system packages" wording and, until it is merged there, amb's
token-based publish step.

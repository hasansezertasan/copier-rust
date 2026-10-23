# copier-rust

A [Copier](https://copier.readthedocs.io) template for Rust command-line tools: CI, a release-please driven
release flow with immutable GitHub releases and native binaries, and crates.io trusted publishing.

## Usage

```bash
copier copy https://github.com/hasansezertasan/copier-rust.git path/to/project
```

Then follow `REPOSITORY_SETUP.md` in the generated project: it lists the one-time GitHub settings the release
flow needs, with `gh` commands where an API exists.

## Questions

| Question | Purpose |
| --- | --- |
| `github_user`, `github_repo_name` | Where the repository lives |
| `crate_name`, `bin_name` | Crate on crates.io and the installed binary; the binary also names the release archives |
| `short_description`, `author_full_name`, `author_email` | Cargo metadata and the LICENSE |
| `copyright_year`, `license` | LICENSE (MIT or Apache-2.0); the year is rendered as `<year>-present` |
| `rust_version` | Minimum supported Rust version, written to `Cargo.toml` and checked in CI |
| `apt_packages` | System packages needed to build on Linux, for example `libasound2-dev pkg-config` |
| `targets` | Release targets, each built natively on its own runner |
| `include_crates_publish` | Publish to crates.io with trusted publishing |
| `include_repo_settings`, `include_repo_ruleset` | `.github/settings.yml` and a branch ruleset for `main` |

## What the generated project gets

- `Cargo.toml`, `Cargo.lock`, a minimal `src/main.rs`, `LICENSE`, `README.md`.
- CI: formatting, clippy with warnings as errors, tests on Linux, macOS and Windows, an MSRV check, and (with crates.io) a `cargo publish --dry-run`.
- A release workflow driven by release-please: a draft release, native builds with provenance attestations and a CycloneDX SBOM, crates.io publishing, and the release published last so that release immutability works. Archives are named so that mise's `github:` backend installs them with no configuration.
- A release build check that builds and packages every target in pull requests that touch the release files.
- PR title and branch name lint, zizmor, dependency review, OpenSSF Scorecard, labels, issue and PR templates, Renovate, `CODEOWNERS` and `SECURITY.md`.
- `REPOSITORY_SETUP.md` (how releases work and the one-time settings), `AGENTS.md` and `CONTRIBUTING.md`.

`Cargo.toml`, `Cargo.lock`, `src/`, `README.md`, `AGENTS.md` and the release-please manifest are written once and
then belong to the project; `copier update` refreshes everything else.

## Development

```bash
mise trust .config/mise.toml
mise install
mise run test
```

The tests render the template with many combinations of answers, check the output (YAML and JSON parse, no
leaked delimiters, toggles, validators, `copier update`), and run `cargo fmt`, `clippy` and `cargo test` on a
rendered project.

See [docs/design.md](docs/design.md) for why the template is built the way it is, and the traps found on the way.

Generated from [copier-copier](https://github.com/hasansezertasan/copier-copier).

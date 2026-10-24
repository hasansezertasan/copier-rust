# Builds and release assets

What the native build matrix and the release archives look like, and the traps that shaped them.

## Native runners, glibc only

**Id:** 79ff97a5-c3b3-42a5-8736-dbd6c22ba647
**Type:** decision
**Type:** constraint
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Decisions"; `copier.yml` help for `apt_packages`

Every release target is built natively on its own runner. Linux builds are glibc-only; musl and cross builds are not offered, and `apt_packages` installs what the build needs.

**Reason:** system libraries (ALSA for audio, for example) link dynamically, which musl and cross builds cannot satisfy.

**Rejected alternative:** musl and cross-compiled builds, not offered because of the dynamic system libraries.

## Release assets work with mise unconfigured

**Id:** a9a870d3-b22b-450e-acd5-32625ce455b5
**Type:** decision
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Decisions"

Assets are `<bin>-<target>.tar.gz` (`.zip` on Windows) holding one `<bin>-<target>/` directory, a `.sha256` each, and an SBOM.

**Reason:** mise's `github:` backend picks the asset by OS and architecture, strips the single top-level directory and verifies attestations, so users need no mise configuration.

**Rejected alternative:** unknown. The design notes name no alternative layout.

## Every step that expands a variable runs with `shell: bash`

**Id:** fe73f588-459e-4e20-95e9-2eddd3e7e835
**Type:** decision
**Type:** incident
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Traps" 1

Windows runners default to PowerShell, where `"$TARGET"` stayed empty and the toolchain install ran with an empty target on amb. The release build check builds and packages every target in pull requests so a failure surfaces before a release.

**Reason:** unknown. The design notes record the fix, not the reasoning behind choosing bash over per-platform scripts.

**Rejected alternative:** unknown. The design notes name no alternative.

## mise can hide a fresh release from `@latest`

**Id:** 2bc02fa3-585b-4b90-a5a3-22d2d06ede38
**Type:** workaround
**Status:** active
**Evidence:** confirmed
**Source:** `docs/design.md`, "Traps" 7
**Revisit when:** mise changes how it resolves `@latest` or the versions host

mise's `minimum_release_age` can hide a freshly published release from `@latest`, and the versions host can lag a few hours. `MISE_USE_VERSIONS_HOST=0` asks GitHub directly.

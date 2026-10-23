import json
import re
import shutil

import pytest
import yaml
from conftest import copier, git, run

UNRENDERED = re.compile(r"\[\[ ?[a-z_]+(\.[a-z_]+)* ?(\|[^\]]*)?\]\]")
REQUIRED = ("-d", "github_user=owner", "-d", "github_repo_name=demo", "-d", "author_email=a@b.c")
APT = "libasound2-dev pkg-config"
ALL_TARGETS = (
    "x86_64-unknown-linux-gnu",
    "aarch64-unknown-linux-gnu",
    "aarch64-apple-darwin",
    "x86_64-apple-darwin",
    "x86_64-pc-windows-msvc",
)


def render(tmp_path, template, *extra, name="project"):
    dest = tmp_path / name
    result = copier("copy", "--defaults", *REQUIRED, *extra, str(template), str(dest), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    return dest


def text(dest, rel):
    return (dest / rel).read_text()


def workflows(dest):
    return {p.name: p.read_text() for p in (dest / ".github" / "workflows").glob("*.yml")}


def test_default_render_has_the_project_and_release_files(tmp_path, versioned_template):
    dest = render(tmp_path, versioned_template)
    for rel in (
        ".copier-answers.yml",
        "Cargo.toml",
        "Cargo.lock",
        "src/main.rs",
        "LICENSE",
        "README.md",
        "AGENTS.md",
        "REPOSITORY_SETUP.md",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
        ".github/workflows/release-build-check.yml",
        ".github/scripts/package-release.sh",
        ".github/release-please-config.json",
        ".github/rulesets/main.json",
        ".github/settings.yml",
    ):
        assert (dest / rel).exists(), rel
    assert "cobo gitignore dump Rust" in text(dest, "REPOSITORY_SETUP.md")
    cargo = text(dest, "Cargo.toml")
    assert 'name = "demo"' in cargo
    assert 'version = "0.0.0"' in cargo
    assert (dest / ".github/scripts/package-release.sh").stat().st_mode & 0o111


def test_rendered_yaml_and_json_parse(tmp_path, versioned_template):
    dest = render(tmp_path, versioned_template, "-d", f"apt_packages={APT}")
    for path in (dest / ".github").rglob("*.yml"):
        yaml.safe_load(path.read_text())
    for path in dest.rglob("*.json"):
        json.loads(path.read_text())


def test_no_template_delimiters_leak_into_the_output(tmp_path, versioned_template):
    dest = render(tmp_path, versioned_template, "-d", f"apt_packages={APT}")
    for path in dest.rglob("*"):
        if not path.is_file() or ".git/" in path.as_posix():
            continue
        for number, line in enumerate(path.read_text().splitlines(), 1):
            assert "[%" not in line and "[#" not in line, f"{path.name}:{number}: {line}"
            # `[[` is Cargo's array-of-tables syntax, nothing else.
            if "[[" in line and path.name in ("Cargo.toml", "Cargo.lock"):
                assert line.strip() in ("[[bin]]", "[[package]]"), line
            elif path.suffix in (".yml", ".json", ".md", ".sh"):
                # Verbatim files may hold bash `[[ "$x" == y ]]`; an unrendered Jinja
                # variable looks like `[[ name ]]` or `[[ name | filter ]]`.
                assert not UNRENDERED.search(line), f"{path.name}:{number}: {line}"


def test_crates_publish_is_optional(tmp_path, versioned_template):
    on = render(tmp_path, versioned_template, name="on")
    release = text(on, ".github/workflows/release.yml")
    assert "crates-publish:" in release
    assert "needs: [release-please, build, sbom, crates-publish]" in release
    assert "rust-lang/crates-io-auth-action@" in release
    assert "id-token: write" in release
    assert "CARGO_REGISTRY_TOKEN: ${{ steps.auth.outputs.token }}" in release
    assert "secrets.CARGO_REGISTRY_TOKEN" not in release
    assert "cargo publish --dry-run" in text(on, ".github/workflows/ci.yml")
    setup = text(on, "REPOSITORY_SETUP.md")
    assert "Trusted Publishing" in setup
    assert "First publish of a crate needs a token" in setup
    assert "gh secret delete CARGO_REGISTRY_TOKEN --env publish" in setup
    assert "gh secret delete CARGO_REGISTRY_TOKEN --repo" in setup
    assert "grep -q CARGO_REGISTRY_TOKEN" not in setup
    assert "secret list --org" in setup
    assert not (on / "docs/RELEASING.md").exists()

    off = render(tmp_path, versioned_template, "-d", "include_crates_publish=false", name="off")
    release = text(off, ".github/workflows/release.yml")
    assert "crates-publish" not in release
    assert "needs: [release-please, build, sbom]" in release
    assert "cargo publish" not in text(off, ".github/workflows/ci.yml")
    assert "crates.io" not in text(off, "REPOSITORY_SETUP.md")
    assert "cargo install demo" not in text(off, "README.md")


def test_apt_packages_drive_every_linux_package_step(tmp_path, versioned_template):
    without = render(tmp_path, versioned_template, name="without")
    for name, body in workflows(without).items():
        assert "apt-get" not in body, name

    with_apt = render(tmp_path, versioned_template, "-d", f"apt_packages={APT}", name="with")
    for name in ("ci.yml", "release.yml", "release-build-check.yml"):
        assert f"apt-get install -y --no-install-recommends {APT}" in workflows(with_apt)[name], name
    assert APT in text(with_apt, "README.md")


def test_targets_select_the_build_matrix(tmp_path, versioned_template):
    full = render(tmp_path, versioned_template, name="full")
    for body in (
        text(full, ".github/workflows/release.yml"),
        text(full, ".github/workflows/release-build-check.yml"),
    ):
        for target in ALL_TARGETS:
            assert f"target: {target}" in body, target

    one = render(
        tmp_path, versioned_template, "-d", 'targets=["x86_64-unknown-linux-gnu"]', name="one"
    )
    for body in (
        text(one, ".github/workflows/release.yml"),
        text(one, ".github/workflows/release-build-check.yml"),
    ):
        assert "target: x86_64-unknown-linux-gnu" in body
        assert "aarch64-apple-darwin" not in body
        assert "windows-2022" not in body


def test_repo_files_are_optional(tmp_path, versioned_template):
    dest = render(
        tmp_path,
        versioned_template,
        "-d",
        "include_repo_settings=false",
        "-d",
        "include_repo_ruleset=false",
    )
    assert not (dest / ".github/settings.yml").exists()
    assert not (dest / ".github/rulesets").exists()
    assert "Branch ruleset" not in text(dest, "REPOSITORY_SETUP.md")


def test_names_flow_into_archives_and_release_config(tmp_path, versioned_template):
    dest = render(
        tmp_path, versioned_template, "-d", "crate_name=demo-crate", "-d", "bin_name=dm", name="x"
    )
    assert 'name = "demo-crate"' in text(dest, "Cargo.toml")
    assert 'name = "dm"' in text(dest, "Cargo.toml")
    assert '"package-name": "demo-crate"' in text(dest, ".github/release-please-config.json")
    assert 'name="dm-${TARGET}"' in text(dest, ".github/scripts/package-release.sh")
    assert "crates.io/crates/demo-crate/" in text(dest, ".github/workflows/release.yml")
    assert "dist/dm-*." in text(dest, ".github/workflows/release.yml")


@pytest.mark.parametrize(
    "answer",
    ["crate_name=Bad_Name", "bin_name=9lives", "rust_version=latest", "apt_packages=Bad Package;"],
)
def test_invalid_answers_are_rejected(tmp_path, versioned_template, answer):
    result = copier(
        "copy",
        "--defaults",
        *REQUIRED,
        "-d",
        answer,
        str(versioned_template),
        str(tmp_path / "project"),
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "Validation error" in result.stderr


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo is not installed")
def test_rendered_project_builds_and_passes_its_own_checks(tmp_path, versioned_template):
    dest = render(tmp_path, versioned_template)
    for cmd in (
        ("cargo", "fmt", "--all", "--check"),
        ("cargo", "clippy", "--locked", "--all-targets", "--", "-D", "warnings"),
        ("cargo", "test", "--locked"),
    ):
        result = run(*cmd, cwd=dest)
        assert result.returncode == 0, f"{' '.join(cmd)}\n{result.stdout}\n{result.stderr}"


def test_update_leaves_project_owned_files_alone(tmp_path, versioned_template):
    dest = render(tmp_path, versioned_template)
    git("init", "-q", "-b", "main", cwd=dest)
    git("add", "-A", cwd=dest)
    git("commit", "-q", "-m", "chore: render", cwd=dest)

    (dest / "src/main.rs").write_text("fn main() { println!(\"mine\"); }\n")
    (dest / "Cargo.toml").write_text(text(dest, "Cargo.toml") + "\n# mine\n")
    git("commit", "-q", "-am", "feat: customise", cwd=dest)

    git("commit", "-q", "--allow-empty", "-m", "chore: release", cwd=versioned_template)
    git("tag", "v0.0.1", cwd=versioned_template)

    result = copier("update", "--defaults", "--skip-answered", cwd=dest)
    assert result.returncode == 0, result.stderr
    assert "mine" in text(dest, "src/main.rs")
    assert "# mine" in text(dest, "Cargo.toml")
    changed = {line[3:] for line in git("status", "--porcelain", cwd=dest).stdout.splitlines()}
    assert changed == {".copier-answers.yml"}
    answers = yaml.safe_load(text(dest, ".copier-answers.yml"))
    assert answers["_commit"] == "v0.0.1"


def test_update_to_a_new_version_only_moves_the_answers_commit(tmp_path, versioned_template):
    dest = render(tmp_path, versioned_template)
    git("init", "-q", "-b", "main", cwd=dest)
    git("add", "-A", cwd=dest)
    git("commit", "-q", "-m", "chore: render", cwd=dest)

    git("commit", "-q", "--allow-empty", "-m", "chore: release", cwd=versioned_template)
    git("tag", "v0.0.1", cwd=versioned_template)

    result = copier("update", "--defaults", "--skip-answered", cwd=dest)
    assert result.returncode == 0, result.stderr
    changed = {line[3:] for line in git("status", "--porcelain", cwd=dest).stdout.splitlines()}
    assert changed == {".copier-answers.yml"}


def test_license_ends_with_a_single_newline_for_every_license(tmp_path, versioned_template):
    for name, spdx in (("mit", "MIT"), ("apache", "Apache-2.0")):
        dest = render(tmp_path, versioned_template, "-d", f"license={spdx}", name=name)
        body = text(dest, "LICENSE")
        assert body.endswith("\n") and not body.endswith("\n\n"), spdx
        assert body.startswith(("MIT License", "\n                                 Apache")), spdx

# Local releases

Redemption Chronicle Maker releases are built, audited and published **from the
developer's machine**. GitHub is used only as the Git repository, tag store and
GitHub Releases host. **No GitHub Actions minutes are consumed** by pushes,
pull requests or releases: `.github/workflows/ci.yml` and
`.github/workflows/release.yml` keep their historical job definitions as
reference but run only on explicit manual dispatch (`workflow_dispatch`).

The official entry point is:

```powershell
.\tools\release\release_local.ps1 -<mode>
```

`tools/release/release_local.ps1` is a thin, safe PowerShell front-end over
`tools/release/release_local.py`, which contains the testable pipeline logic.
**The `tools/release/` directory is maintainer-local**: it is excluded via
`.git/info/exclude` and intentionally not distributed in the public repository.
Clones do not contain the release tooling; only the maintainer's machine can
publish, because publication requires `gh` authenticated with write access.

## Modes

```powershell
.\tools\release\release_local.ps1 -Check
```

Environment diagnostics only: Python (>= 3.10; CI reference is 3.12),
`cache/vendor` and `cache/devtools` dependencies, JDK 21 + `jlink`,
`cache/toolchain/ecj-3.26.0.jar` against its pinned SHA-256, Git repository and
`origin` remote, GitHub CLI presence, `gh auth status`, effective repository
permissions, free disk space and workspace write access.

```powershell
.\tools\release\release_local.ps1 -Prepare
```

Validates the version in `src/rcm/__init__.py` (`X.Y.Z` or `X.Y.Z-rcN`), that
`RELEASE_NOTES.md` and `CHANGELOG.md` contain a heading for it, the state of
`main` against `origin/main`, local and remote `v*` tags, and whether any
product inputs (sources, tools, docs, chronicles, manifests of dependencies)
have uncommitted changes.

```powershell
.\tools\release\release_local.ps1 -Build
```

Runs the complete offline quality suite `python tools/quality.py --no-coverage`
(the fast 28-test gate is **not** sufficient for a release), then
`tools/build_portable.py`, `tools/verify_frozen_sources.py`, and
`tools/product_release.py`; verifies the manifest, archive name, size and every
file hash; regenerates `SHA256SUMS.txt`; and re-reads the ZIP. All output is
staged under `build/release/<version>/` together with `build_receipt.json`
(state `COMPILED_LOCALLY`). **Nothing is uploaded and no tag is created.**
`-SkipQuality` exists only for diagnostics: a build whose receipt lacks a
passed full suite can never be published.

```powershell
.\tools\release\release_local.ps1 -DryRun
```

Verifies remote readiness read-only: `gh` authentication, push permission on
`MetisC/RedemptionChronicleMaker`, that `HEAD` is pushed, that the remote tag
does not already exist on another commit, that no published release already
occupies the tag, and that the staged build receipt matches `HEAD` with a
passed quality suite. Prints the exact plan. **Zero remote writes.**

```powershell
.\tools\release\release_local.ps1 -Publish
```

Requires every `-DryRun` gate to pass, plus an explicit human confirmation
(type the exact tag, or pass `-ConfirmTag <tag>`). Publishing a stable `X.Y.Z`
additionally requires `-Stable`; `-rcN` versions publish as prereleases marked
`--latest=false`. The flow is:

1. create annotated tag `v<version>` on the recorded source commit (never
   moved if it exists), push it, and verify the remote peeled SHA;
2. create a **draft** release with title, `RELEASE_NOTES.md` notes and the
   three assets, or reuse/fix an existing draft (missing assets only);
3. verify draft assets by name, size and downloaded bytes;
4. flip the draft to published (`draft=false`);
5. re-download every published asset and compare SHA-256 with the staged
   files;
6. write `build/release/<version>/publish_receipt.json` distinguishing
   `COMPILED_LOCALLY`, `PUBLISHED_TO_GITHUB` and `REMOTE_DOWNLOAD_VERIFIED`.

```powershell
.\tools\release\release_local.ps1 -Verify [ -Tag v<X.Y.Z> ]
```

Re-checks a published release afterwards: not a draft, correct prerelease
flag, expected asset set, and byte-for-byte SHA-256 of re-downloaded assets
against the local staging manifest/SHA256SUMS.

```powershell
.\tools\release\release_local.ps1 -Notes
```

Writes `build/release/notes_draft.md` — an editable draft summarising commits
and changed files since the previous tag. Draft only: final notes must be
reviewed by a human in `RELEASE_NOTES.md` before publishing.

## Release source of truth

The application version lives in `src/rcm/__init__.py`. Supported public
versions are `X.Y.Z` and `X.Y.Z-rcN`. Windows executable metadata, the
portable `VERSION` file and the release ZIP name derive from it.

Published assets:

```text
RedemptionChronicleMaker-<version>-win64.zip
SHA256SUMS.txt
release_manifest.json
```

## Immutability policy

- Once a release is published its assets are immutable: the tool never uses
  `--clobber`, never moves tags and never deletes drafts or assets on its own.
- A remote tag already pointing at the expected commit is reused (resume
  path); pointing anywhere else blocks the release — bump the version.
- An already-published release for the tag blocks unconditionally.
- If publication fails mid-flight, the pushed tag and any partial draft are
  left in place; re-running `-Publish` resumes from them safely.
- Errors after publication require a **new** version, never an overwrite.

## What is deliberately not automated

Local builds do not claim native-engine verification and do not run the game.
The release remains a release candidate until the human acceptance items
(`DYN01-12`, `docs/MANUAL_RUNTIME_CHECKLIST.md`) pass in Vampire itself.
Offline tests, doubles, compilation against the real Codex API and packaging
audits do not certify gameplay.

## A failed gate means no new release

`-Build` and `-Publish` stop on any failure: version/tag mismatch, ECJ hash
mismatch, quality suite failure, portable build failure, product audit
failure, archive/manifest mismatch, checksum mismatch, missing push
permission, occupied tag or pre-existing published release.

Do not bypass a failed gate by manually uploading an unverified ZIP under an
existing release. Fix the source, move to a new version, rebuild and publish
through the tool.

## GitHub CLI

Install once with `winget install --id GitHub.cli`, then `gh auth login`
(or reuse the Git credential-manager token). The tool never stores tokens in
the repository; `gh` handles authentication.

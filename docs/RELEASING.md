# Automated releases

Redemption Chronicle Maker uses GitHub Actions for CI and tagged Windows releases.

## CI

`.github/workflows/ci.yml` runs on every push to `main`, on pull requests and on manual dispatch.

The CI job uses Python 3.12 on `windows-latest`, installs the backend/development dependencies into the same workspace-local locations used by the project and runs:

```powershell
python tools/quality.py --fast
```

This is an offline gate. It does not launch or automate Vampire: The Masquerade — Redemption.

## Release source of truth

The application version lives in:

```text
src/rcm/__init__.py
```

Supported public release versions are:

```text
X.Y.Z
X.Y.Z-rcN
```

Examples:

```text
1.0.0-rc4
1.0.0
1.1.0-rc1
```

Windows executable metadata, the portable `VERSION` file and the default release ZIP name are derived from that application version. RC builds map the RC number to the fourth integer in Windows file-version metadata; final releases use zero there.

The release workflow refuses to publish if the Git tag and the application version differ.

## Publishing a release

Before tagging:

1. Run the complete local quality gate on the exact commit to be tagged: `python tools/quality.py --no-coverage`. The CI fast gate covers only `test_safety_unit.py`; GUI, Java, catalogue and Qt checks run in the full suite.
2. Update `src/rcm/__init__.py` to the version you intend to publish.
3. Update `RELEASE_NOTES.md` for that version.
4. Commit and push those changes to `main`.
5. Create and push the matching tag.

Example:

```powershell
git tag v1.0.0-rc5
git push origin v1.0.0-rc5
```

That tag push triggers `.github/workflows/release.yml`.

## What the release workflow does

On a `v*` tag the Windows release job:

1. checks out the exact tagged source;
2. installs Python 3.12;
3. installs Temurin JDK 21;
4. installs backend, editor and build dependencies into `cache/vendor` / `cache/devtools`;
5. downloads ECJ 3.26.0 and verifies its pinned SHA-256;
6. checks that `v<app-version>` exactly matches the pushed tag;
7. runs the fast quality gate;
8. builds the portable application with `tools/build_portable.py`;
9. audits and packages it with `tools/product_release.py`;
10. verifies `release_manifest.json` and the expected archive name;
11. generates `SHA256SUMS.txt`;
12. preserves the release files as a GitHub Actions artifact for 30 days;
13. creates the GitHub Release and uploads the verified files.

Published assets are:

```text
RedemptionChronicleMaker-<version>-win64.zip
SHA256SUMS.txt
release_manifest.json
```

GitHub supplies its normal source-code archives separately.

Release candidates such as `v1.0.0-rc5` are published as **pre-releases**. A final tag such as `v1.0.0` is marked as the latest release.

If the GitHub Release already exists (for example after rerunning a partially failed workflow), the workflow refreshes its generated assets with `--clobber` instead of creating a duplicate release.

## What is deliberately not automated

GitHub-hosted runners do not contain a licensed Redemption installation. The release workflow therefore does not claim native-engine verification and does not run the game.

Native/manual acceptance remains separate from:

- static analysis;
- synthetic/unit tests;
- generated Java tests/doubles;
- portable packaging;
- release auditing.

See [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md) for native tests.

## A failed gate means no new release

The workflow stops before publication if any of these fail:

- version/tag match;
- ECJ hash verification;
- fast quality gate;
- portable build;
- product audit;
- archive/manifest verification;
- checksum generation.

Do not bypass a failed gate by manually uploading an unverified ZIP under the same release tag. Fix the source, move to a new tag/version when appropriate, and let the workflow build the public artifact from tagged source.

Only artifacts produced by the release workflow are published. A locally rebuilt portable can differ from the CI artifact under the same version string; never attach a local ZIP to a release — bump the version and tag instead.

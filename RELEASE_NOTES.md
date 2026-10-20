# Redemption Chronicle Maker 1.0.0-rc8

RC8 packages the audited main branch with the latest authoring, map and project-management fixes. This is a **pre-release**, not final 1.0. Projects remain outside the program folder; formats 9 and 10 remain supported.

## Authoring and maps

- Choose original game map illustrations, with automatic defaults for levels that have an associated map. Use a different original illustration when needed, or create a custom map with editable names, markers, visibility and refuges. Fixed the game-map picker failing when a selected map had no associated level.
- The existing editor panels cover scene layers, actors/objects, clickable scenery, conversations, notes, quests, flags, inventories, dynamic encounters, cinematics, audio and environment controls. Original level geometry stays immutable.
- Author native script parameters and box regions, instance overrides, interest groups, temporary music, party conversation staging, camera paths and timed camera turns through the existing tools. Sound/light activation zones and narrative actor actions provide the documented functional alternatives; private campaign scripts and arbitrary external binary code are not universally supported.
- Optional local content libraries and Within The Darkness imports retain their existing ownership and dependency checks. Original game and mod assets are not included in the application ZIP.

## Project management and safety

- Delete a local chronicle from the welcome screen using the button, context menu or Delete key. Confirmation shows its exact location. Installed game modules and saved games are preserved. Removing an entry from recent projects remains a separate action.
- Opening a chronicle shows loading feedback and blocks repeated activation until loading finishes. Failed opens restore the cursor and controls.
- Project search, resource filtering, keyboard navigation, readable controls and persistent English/Spanish selection remain available.
- Automated tests now isolate shared-fixture rolling backups in a disposable directory. Two regressions verify retention and preservation of existing local recovery files. Autosaves, backup files, locks and rotated logs have preventive Git exclusions; existing local recovery data is preserved.

## Verification and compatibility

- The immediately preceding audited main completed **634 tests with zero failures, errors or skips**, plus Ruff and the configured mypy checks. Seven canonical examples recompiled against the real Codex API with Java class format **45.3**, retaining identical source/package hashes. A separate authored project also validated and compiled without editing its YAML.
- RC8 packaging is checked separately for version consistency, archive hashes, frozen-source matching and bilingual portable startup. GitHub Actions builds the published Windows archive from the exact release tag and attaches its manifest and SHA-256 checksum.
- The accepted format-9 tutorial and mini chronicle are preserved. Dynamic encounters remain opt-in format 10. Startup inventory definitions remain available before LAN character restoration.
- **Manual runtime checks remain required** for the applicable native save/load, re-entry, cameras/audio, encounters and multiplayer cases. Portable checks on the build machine do not certify a separate PC, physical DPI or GPU behaviour. See the included manual checklist.

Requires your own complete installation of Vampire: The Masquerade - Redemption. Normal authoring does not require any original authoring tool.

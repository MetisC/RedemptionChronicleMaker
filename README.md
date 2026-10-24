# Redemption Chronicle Maker · 1.0.0-rc10

Create chronicles for **Vampire: The Masquerade — Redemption** using an independent editor and generators. Original level geometry is a reusable, immutable base. Normal authoring does not require Embrace, NOT Editor or another original authoring program.

This is a release candidate. Authoring coverage, offline tests and native game acceptance are recorded separately.

## Start the editor

Open **Redemption Chronicle Maker.lnk** in the repository root, or **RedemptionChronicleMaker.exe** in the portable distribution. The local build lives at `build/portable/RedemptionChronicleMaker/`.

Select your own game installation when asked. The portable application includes its Java runtime; end users do not need Python or a system JDK. English is the default. The language menu also offers Spanish and remembers the selection.

Create or open a project, choose an existing base level and author its content in the existing 3D, story, campaign and resource panels. Press **F5 / Test in Redemption** to validate, compile and deploy. Close Redemption before updating loaded files. You perform the gameplay checks yourself.

The original installation remains read-only except its managed **RCM** directory. Deployment tracks file ownership and preserves saved-character inventory definitions. A normal launch without RCM does not use the shared imported content.

## Examples

- **Quick tutorial — A letter before dawn**: accepted tutorial, project format 9. The user's acceptance is scoped to that tutorial.
- **Full showcase — Narrator's Workshop**: the book story plus optional dynamic and cinematic laboratories. The canonical repository project is `chronicles/showcase/project.yaml`; suffixed folders such as `showcase_2` are separate copies. Initial module loading was confirmed after the CASH metadata repair on 18 October 2026.
- **Mini chronicle**: a small campaign with linked scenes.
- **Dynamic Encounter Lab**: independent format-10 combat acceptance example.
- **Arrival at the refuge**: a short Director acceptance chronicle. Original door click, named native party staging, dialogue, a travelling, temporary music, spatial sound, a weak rat, quest progress and travel. New native behaviour remains subject to the manual checklist.

**Help → Authoring laboratory** opens the separate optional example for own maps, timed camera turns, native box scripts, dynamic role control and environment zones. See [Authoring completion](docs/AUTHORING_COMPLETION.en.md).

Help opens editable example copies. Existing personal copies are not overwritten when bundled examples change. User projects and resources belong in their workspace, outside the replaceable program directory.

## Authoring

- Actors, objects, inventory, transforms, starts, waypoints, patrols, triggers and persistent flags. Preview textured actor/object models in the resource picker before placing them; use its arrows to turn the preview. Rotation is free by default (set a degree step to snap).
- Right-click an authored actor/object in the viewport or project tree to create and bind a conversation. Objects use a chosen speaking character; existing modal actions require confirmation before replacement.
- Branching conversations, line actions, camera presets, quests, notes, events and scene/layout changes.
- Native hover/click actions on original objects and bounded selectable overlays on fixed surfaces. Existing Actions handle conversations, events and travel; self-scene links are rejected.
- Compatible original door/prop control without geometry changes. Fixed surfaces do not acquire invented frame animations.
- Existing encounters plus optional format-10 generators, waves, reinforcements and boss phases.
- Cinematic cues reuse normal Actions: shots, original or authored paths, gestures, LookAt, movement, sound, effects and events.
- Own linear NCP paths captured in the 3D viewport, up to 128 points. Original cubic files round-trip without modification. Optional Time per segment allows stationary turns and holds, with explicit durations.
- Conversation staging is automatic, an existing RCM Entry, or a native conversation group using one to four existing named markers. No raw convstart indices or new marker editor.
- Normal music/ambient start and stop, plus temporary music/restore. Codex has **one previous-track snapshot**, not a nested stack. RCM guards ownership; it does not invent persistent music-stack state.
- Positioned or actor-attached sounds/owned loops, entity-attached dynamic lights, trigger activation sound/light zones and demonstrated weather choices. Optional runtime roomtype reverb needs compatible3D audio. These do not edit baked lighting.
- References, safe deletion with a validated cascade preview, undo/redo, validation, project export/import, packages and bounded traces.
- Optional selective Within The Darkness import from a user-supplied NOB. Usable resources and Penthouse are exposed; demo/interface replacements are excluded. Verified shared content belongs to managed RCM launches rather than one chronicle. Mod assets are not shipped in public releases.

## Boundaries

No geometry creation/editing, CSG, structural sectors/portals, UV/texturing, model authoring or lightmap generation. No universal NSD codec, universal door animation, save migration or claim of verified network replication. Custom Java remains an explicit escape hatch.

Project formats **9 and 10** remain compatible; opening a project does not convert it. Format 10 is optional for dynamic encounters. The accepted tutorial, mini and independent Dynamic Lab are preserved.

Camera framing, native party formation/collision, temporary music save/load behaviour, re-entry and multiplayer require user observation. A passing double or packaged offscreen UI test does not certify Redemption's rendering, audio or another PC.

## Source workflow

With the local dependencies prepared, the workspace CLI is:

```powershell
python tools/rcm.py diagnostics
python tools/rcm.py validate chronicles/showcase/project.yaml
python tools/rcm.py build chronicles/showcase/project.yaml
python tools/rcm.py deploy rcm_showcase
```

Builds contain generated original formats and Java compiled against the real Codex API as classfile **45.3**. Geometry is referenced, not repackaged. `.rcmpack` packages and project archives have separate purposes; see the authoring guide. Deployment never launches gameplay automatically as part of the quality gate.

Development setup uses `tools/bootstrap.ps1` with a legitimate game path, local Python dependencies and the pinned Java compiler/toolchain. Generated/cache dependencies stay in the workspace. The portable build uses `python tools/build_portable.py`; `tools/product_release.py` audits and packages the current distribution without original game or mod assets.

## Verification and documentation

```powershell
python tools/quality.py --no-coverage
python tools/test.py --pattern "test_final_flecks*.py"
python tools/rcm.py verify-originals
```

Windows link/process checks need the relevant OS permissions. Synthetic deployment tests isolate process queries from a real running game. Authoritative fresh counts are in `build/tests/test_report.json` and `quality_report.json`, with the surgical closure receipt in `research/embrace_closure/`.

- [Getting started](docs/GETTING_STARTED.en.md) / [Primeros pasos](docs/GETTING_STARTED.md)
- [Editor guide](docs/EDITOR_GUIDE.en.md) / [Guía del editor](docs/EDITOR_GUIDE.md)
- [Cinematic Director](docs/CINEMATIC_DIRECTOR.en.md) / [Director de escenas](docs/CINEMATIC_DIRECTOR.md)
- [Current product and limits](docs/FINAL_PRODUCT_REPORT.md)
- [Authoring parity and evidence](docs/EMBRACE_AUTHORING_PARITY.md)
- [Engine evidence](docs/ENGINE_NOTES.md) and [formats](docs/FORMAT_NOTES.md)
- [Tests](docs/TESTING.md) and [manual acceptance](docs/MANUAL_RUNTIME_CHECKLIST.en.md)

This unofficial fan project requires a legitimate installation of Redemption. It does not distribute original game assets, proprietary authoring tools or imported mod content.

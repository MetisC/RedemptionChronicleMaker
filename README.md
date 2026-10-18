# Redemption Chronicle Maker

**Redemption Chronicle Maker (RCM)** is a modern visual authoring tool for **Vampire: The Masquerade — Redemption**. It is designed to let you build new chronicles with the original game engine without using the old authoring tools and without having to hand-write the game’s runtime files.

RCM reuses the game’s existing levels, models, templates, scripting API and runtime, then gives you a modern workflow for placing actors and objects, writing conversations, building quests, wiring events, creating cinematics, travelling between scenes, authoring encounters and playtesting the result directly in Redemption.

> **Current version:** `1.0.0-rc6`
>
> **Status:** release candidate. The editor, build pipeline and automated/offline test suite are in good shape, but some native-game scenarios still require manual verification inside Redemption. Networking is experimental; the primary target is local single-player authoring/playtesting.

RCM is an **unofficial fan-made tool**. It is not affiliated with or endorsed by the owners of Vampire: The Masquerade or Vampire: The Masquerade — Redemption.

---

## What RCM is

RCM is a complete chronicle-authoring layer built around the original Redemption runtime.

The project uses a human-editable YAML document as the source of truth. The editor and CLI share the same backend, validators, catalogues and generators. On build, RCM converts that authored data into the Java/runtime formats expected by Redemption, compiles the generated classes against the real game API, validates the result, packages it and deploys it only inside RCM-managed folders.

The high-level pipeline is:

```text
Original Redemption installation (read-only)
                ↓
      catalogues / resources
                ↓
YAML → model → validation → Java + runtime formats
                ↓
              ECJ
                ↓
       readback / validation
                ↓
         chronicle package
                ↓
        RCM-managed deploy
```

RCM deliberately **does not edit level geometry**. The original level geometry is treated as read-only scenery. You author the story, actors, objects, triggers, conversations, quests, paths, audio, cameras, encounters and state on top of it.

That distinction is important: RCM is a chronicle/module editor, not a map modeller.

Original static props and framed doors can be targeted through **Campaign / Overview → Add… → Original object / create passage…**. Hide, restore, remove and door motion generate runtime actions; fixed NIL surfaces remain immutable. See [Editor guide](docs/EDITOR_GUIDE.en.md) and the pending ORG01–06 native checks.

Optional **Within The Darkness** content is imported from your own NOB through **Settings → Import mod content: Within The Darkness…**. The importer makes usable clans, disciplines, templates, models and the Penthouse level available locally, excluding the mod's menu skin and demo campaign. Without an import, RCM keeps its original content catalogue. Mod assets are not bundled with the public application or chronicle distribution ZIP; recipients need their own local import. See the [Editor guide](docs/EDITOR_GUIDE.en.md) for authoring and deployment.

---

## What you can create

RCM currently supports a broad range of Redemption authoring tasks:

- multi-scene chronicles using original Redemption locations;
- player entry points and named arrival positions;
- NPCs, enemies, props, items, weapons and armour;
- branching conversations with GOTO/RETURN flow;
- conversation cameras and cinematic sequences;
- notes, letters and interactive objects;
- flags, conditions, state changes and reusable event logic;
- quests, journal steps and XP rewards;
- inventory rewards, quest items and item checks;
- trigger volumes and trigger-enter/trigger-leave events;
- travel between scenes with explicit arrival points;
- waypoints, actor paths and patrol control;
- AI enable/disable controls and project-owned AI profiles;
- music, ambience and spatial one-shot sounds;
- authored combat encounters;
- **dynamic encounters**: ambushes, waves, continuous spawning, reinforcements and boss phases;
- health thresholds and generator state/count conditions;
- start/stop/pause/resume/reset control for dynamic encounters;
- resource browsing, original-template inspection and project-owned resource cloning;
- Story Graph visualisation;
- reference tracking, safe deletion, rename support and undo/redo;
- autosave/recovery, saved versions and protection against concurrent editing;
- build, deploy, runtime trace and playtest integration;
- editable project export and playable chronicle packages.

RCM also includes guided assistants for common authoring jobs so that ordinary work does not require touching YAML or Java.

---

## What RCM does **not** do

RCM intentionally avoids pretending to be a full replacement for a 3D modelling suite or for every internal tool the original developers had.

In particular:

- original level geometry is not editable;
- RCM does not ship the original game, original game assets or the old authoring tools;
- it does not automate playing the game or click through Redemption’s menus for you;
- arbitrary freeform camera XYZ/FOV authoring is not the normal workflow;
- there is no universal NCP writer;
- universal door editing and universal removal of arbitrary original static content are not guaranteed features;
- multiplayer/network behaviour is not the main certified target;
- some native-engine behaviours — especially save/load, re-entry, collision/pathfinding and very large dynamic encounters — still require manual testing in the actual game.

When RCM does not have enough evidence about an engine feature, the project prefers to fail safely or leave the feature out rather than invent behaviour.

---

# Requirements

For the packaged Windows build you need:

1. **Windows**.
2. A complete, working installation of **Vampire: The Masquerade — Redemption**.
3. Permission to read the game installation and create RCM-managed folders beside it.
4. Enough disk space for RCM’s private catalogues, extracted metadata, project files and builds.

The packaged release includes its own Python/Qt application runtime, ECJ compiler support and Java runtime. End users do **not** need to install Python, Qt or a JDK just to use the portable build.

RCM does not include `Vampire.exe`, `Codex.nob`, `Resource.nob`, the original levels, models, textures, `classes.zip` or other original copyrighted game data. Those are read from your own installation during setup.

---

# Installation — packaged Windows release

For normal use, prefer the packaged Windows release rather than the development workspace.

1. Extract the complete RCM release folder somewhere **outside the Redemption installation**.
2. Keep the application folder intact. Do not copy only `RedemptionChronicleMaker.exe`; the Qt libraries, JVM, notices and other bundled files are part of the application.
3. Run **`RedemptionChronicleMaker.exe`**.
4. On first launch, RCM will ask for **`Vampire.exe`** if it cannot locate the game automatically.
5. Select the executable from your complete Redemption installation.
6. RCM verifies the installation and builds the private catalogues it needs.
7. Your editable projects are stored separately from the application, by default under:

```text
Documents\Redemption Chronicle Maker
```

Replacing or updating the RCM program folder should therefore not overwrite your chronicles.

RCM does not scan entire drives during first run. If the game is not found, choose `Vampire.exe` explicitly.

---

# First-run initialization

The first run performs real setup work. RCM checks that the selected Redemption installation contains the executable, resources, script library and original chronicle data required for authoring. It then reads/indexes the installation and prepares derived catalogues for the editor.

The original installation remains read-only from the authoring side. RCM creates only its own managed deployment folders under the game’s `RCM` area when a chronicle is prepared for testing.

The project folder, language and other application preferences can be changed later in **Tools → Settings**. Changing the project folder or language requires a restart where indicated by the UI.

If setup is cancelled before a valid game installation is selected, RCM does not pretend that initialization succeeded.

For more detail, see [First run](docs/FIRST_RUN.en.md).

---

# Five-minute quick start

The fastest way to understand RCM is to use the included tutorial.

1. Launch RCM.
2. From the Welcome screen choose **Quick tutorial**.
3. Open **Story** and select Anezka.
4. Edit one line of dialogue in **Properties**.
5. Save.
6. Press **PLAYTEST IN REDEMPTION (F5)**.
7. RCM validates the project, rebuilds only if necessary, prepares the chronicle folder and launches Redemption.
8. In the game go to:

```text
Multiplayer → LAN → New Game
```

9. Select the RCM tutorial chronicle and play it.

RCM intentionally does not take control of Redemption’s menus. The editor prepares and launches the test; the in-game navigation remains yours.

If you make structural changes to a chronicle, start a **new game** for the next test. Close Redemption before updating/redeploying a playtest; RCM will not kill the game process for you.

See [Getting started](docs/GETTING_STARTED.en.md) for the compact version of this workflow.

---

# Creating a chronicle

A minimal new chronicle usually looks like this:

1. Choose **New chronicle** from Welcome.
2. Give the project a name and ID.
3. Choose an original Redemption scenario/level.
4. Place a player arrival using **Campaign → + Entry**.
5. Add an NPC.
6. Use **Assistant… → Talking NPC** to create a first conversation.
7. Add a trigger, quest, encounter or travel connection as needed.
8. Save and press **F5**.

A **scene** is your authored content. The selected Redemption scenario supplies the original level geometry/environment beneath it.

The main editor areas are:

### 3D Space

Use the viewport to place entries, NPCs, objects, waypoints and trigger areas on visible ground. Original geometry is selectable only as spatial reference and cannot be modified.

### Story / Resources

Edit actors, conversations, dialogue nodes and answers. Browse original and project-owned resources, filter by family/origin, inspect templates and save favourites.

### Campaign / Overview

Manage scenes, quests, travel, paths, encounters and cinematic sequences across the chronicle.

### Graph

Inspect conversation branching or the ordered actions associated with an event. Selecting graph cards returns you to the corresponding authoring data.

### Playtest / Debug

Inspect runtime trace output and navigate back toward the authored source. Trace information helps diagnose behaviour but does not replace visual verification inside the game.

See [Using the editor](docs/EDITOR_GUIDE.en.md) and [Author your adventure](docs/AUTHORING_GUIDE.en.md) for the detailed workflow.

---

# Assistants

RCM’s assistants are convenience layers over normal project entities — they do not create a separate hidden scripting system.

The authoring assistant covers common tasks such as:

- talking NPCs;
- NPCs that send the player somewhere;
- trigger actions;
- cinematic triggers;
- item pickup;
- quests;
- encounters;
- travel plus arrival;
- notes/letters;
- object conversations.

You can later reopen an assistant-created configuration. RCM reads the current authored entities, including changes already made in Properties, rather than maintaining a second copy of the data.

Cancel does not modify the project. Apply is undoable.

---

# Dynamic encounters

RC4 adds a higher-level dynamic combat system without replacing the existing authored encounter system.

Create one from:

- **Campaign → + Dynamic encounter…**;
- the assistants menu; or
- the 3D ground context menu with **Dynamic encounter here…**.

The wizard supports:

### Ambush

Spawn a bounded group once.

### Waves

Create successive groups. The next wave starts after the previous one has been cleared, with optional delays.

### Continuous generator

Spawn enemies over time while respecting a live-enemy cap, optional total limit and replacement behaviour.

### Reinforcements

Keep a group dormant until another event starts it.

### Boss phases

Use a generated or authored boss and trigger normal RCM actions when health crosses percentage or absolute-HP thresholds.

Dynamic encounters reuse the existing event/action system. They can be started, stopped, paused, resumed and reset from conversations, triggers, timers, quests, boss phases or other events.

Spawn positions can use authored waypoints or the engine’s near-player spawn behaviour. Enemy selection can be round-robin or weighted random where supported. Original template health/AI can be preserved, or health can be adjusted for the generated actor without modifying the original resource.

Boss thresholds are detected as a **crossing** from above the threshold to at-or-below it while the actor is still valid and alive. A lethal hit can therefore skip a phase; RCM does not claim a universal “before death” hook that the engine evidence does not support.

The runtime tracks owned GUIDs, roles, waves, counters, cooldowns and save state with bounded data structures. When restored ownership cannot be reconciled safely, the encounter fails closed instead of blindly spawning replacements and risking duplicates.

Open:

```text
chronicles/dynamic_lab/project.yaml
```

for a dedicated editable example.

Full details: [Dynamic encounters](docs/DYNAMIC_ENCOUNTERS.en.md).

---

# Playtest workflow

**F5 / PLAYTEST IN REDEMPTION** is the normal edit-test loop.

RCM will:

1. commit pending editor values;
2. save the project;
3. validate it;
4. stop if validation errors exist;
5. rebuild only when the current build is stale;
6. prepare the chronicle’s RCM-managed game folder;
7. launch Redemption using that chronicle folder.

Each chronicle is deployed into its own managed location beneath the game’s `RCM` directory. This avoids dumping authoring files into the original installation and allows RCM to track ownership and hashes.

The original game resources are not rewritten by the normal authoring workflow.

---

# Persistent character inventory compatibility

Redemption multiplayer characters can keep items between chronicle sessions. That means a saved character may still reference a project-defined item from another RCM chronicle before the new chronicle has even started.

RCM therefore maintains compatibility libraries inside managed launch folders so definitions required by persistent inventories remain available during startup. After an editor-started playtest ends, those managed libraries are refreshed.

RCM does **not** edit the saved character itself.

If an older managed launch folder fails before character selection because it is missing an owned item definition, close Redemption and use the workspace repair tool:

```powershell
python tools/repair_profile_libraries.py --game "C:\Path\To\Vampire The Masquerade - Redemption"
```

The repair tool only updates RCM-managed folders and keeps a backup of replaced data.

See [Troubleshooting](docs/TROUBLESHOOTING.en.md) for the current recovery guidance.

---

# Included examples

The repository/product currently carries four maintained examples:

### `chronicles/tutorial`

A small guided tutorial intended to teach the basic authoring/playtest loop.

### `chronicles/showcase`

A broader feature showcase containing optional laboratories for the major editor systems.

### `chronicles/mini_chronicle`

A compact but more complete adventure demonstrating multiple scenes and normal story flow.

### `chronicles/dynamic_lab`

A focused test chronicle for waves, reinforcements, boss thresholds, continuous spawning, pause/resume/stop and save/load behaviour.

The Welcome screen creates editable working copies so you do not have to modify the distributed masters directly.

---

# Project data and safety

RCM is deliberately conservative with user work and original game data.

Important protections include:

- projects live outside the replaceable application folder;
- atomic project saves;
- automatic recovery data;
- saved versions/backups;
- external-change detection;
- project locking to avoid concurrent editing of the same file;
- safe rename/reference updates;
- guarded deletion of referenced elements;
- validation before build/deploy;
- build fingerprints so stale builds are not silently deployed;
- deployment manifests and hashes;
- rollback on managed package/deployment failures where supported;
- original-game files kept outside RCM ownership.

No filesystem safety mechanism can make every possible crash or power-loss scenario mathematically atomic, so important projects should still be backed up normally.

---

# Packaging and sharing

RCM supports two package concepts:

### `.rcmproject`

An editable project export containing the YAML source and project-owned source assets.

### `.rcmpack`

A playable chronicle package containing the generated NOB/runtime classes and manifest required to install the chronicle into an RCM-managed game folder.

Packages do not include original Redemption geometry/models/resources.

Installed packages are tracked with manifests and hashes. Update/uninstall operations preserve unrelated files and stop when a managed file has been modified unexpectedly.

Chronicle packages may contain executable Java classes. RCM can inspect package metadata and requires explicit acceptance for custom code, but it is **not** a sandbox or malware scanner. Only install packages you trust.

Technical package details are documented in [PACKAGES.md](docs/PACKAGES.md).

---

# Advanced CLI

The GUI and CLI use the same backend.

The workspace-local CLI entry point is:

```powershell
python tools/rcm.py <command>
```

Useful commands include:

```powershell
python tools/rcm.py diagnostics
python tools/rcm.py verify-originals
python tools/rcm.py validate chronicles/mini_chronicle/project.yaml
python tools/rcm.py build chronicles/mini_chronicle/project.yaml
python tools/rcm.py deploy rcm_mini
python tools/rcm.py run rcm_mini
```

Package operations are also available:

```powershell
python tools/rcm.py package <chronicle-id> <destination>
python tools/rcm.py inspect-package <archive>
python tools/rcm.py install-package <archive> --accept-custom-code
python tools/rcm.py uninstall-package <chronicle-id>
python tools/rcm.py export-project <project.yaml> <destination>
python tools/rcm.py import-project <archive> <empty-directory>
```

Use `--game` when the workspace does not already know which Redemption installation to use.

The CLI itself does not automate gameplay.

---

# Running from the source workspace

The packaged application is the recommended path for ordinary users. The repository workspace is mainly for development, investigation and reproducible builds.

The current code targets **Python 3.12**.

## 1. Clone and enter the repository

```powershell
git clone https://github.com/MetisC/RedemptionChronicleMaker.git
cd RedemptionChronicleMaker
```

## 2. Bootstrap the backend/toolchain

Use the provided bootstrap script and **pass your game path explicitly**:

```powershell
powershell -ExecutionPolicy Bypass -File tools/bootstrap.ps1 -Game "C:\Games\Vampire The Masquerade - Redemption"
```

The bootstrap process prepares the local toolchain, verifies the expected ECJ compiler hash, installs the backend Python dependency into the workspace and scans the selected Redemption installation.

## 3. Install editor dependencies into the workspace

```powershell
python -m pip install --target cache/vendor -r requirements-editor.txt
```

For development/test tools:

```powershell
python -m pip install --target cache/devtools -r requirements-dev.txt
```

## 4. Start the editor

```powershell
python editor.py
```

The source entry point reports missing editor dependencies explicitly if PySide6, NumPy or Pillow are not available.

---

# Building the portable application

The portable Windows build uses PyInstaller plus a trimmed Java runtime generated with `jlink`.

Building it requires a JDK that provides `jlink`:

```powershell
python tools/build_portable.py --java-home "C:\Path\To\JDK"
```

The generated portable is an **onedir** application. Distribute the complete folder/ZIP, not the EXE alone.

The portable intentionally excludes original Redemption assets.

---

# Tests and quality checks

Latest recorded validation:

```text
482 PASS
0 FAIL
0 ERROR
0 SKIP
```

Common checks:

```powershell
python tools/quality.py --fast
python tools/quality.py --no-coverage
python tools/test.py --pattern test_dynamic_encounters.py
python tools/test.py --pattern test_dynamic_gui.py
python tools/audit_spawners.py
python tools/rcm.py verify-originals
```

The automated suite covers model/format validation, generated Java, save/restore logic through doubles, GUI behaviour, dynamic encounters, packaging and regression checks. Stress tests compile large synthetic dynamic-encounter configurations and inspect bytecode budgets.

These tests do **not** magically equal native Redemption verification. Generated/compiled/offline-tested and actually observed inside the real game are treated as separate states.

See [Testing](docs/TESTING.md) and [Manual runtime checklist](docs/MANUAL_RUNTIME_CHECKLIST.md).

---

# Current release status and known limitations

`1.0.0-rc6` is a **release candidate**, not final 1.0.

The current release includes the startup-inventory compatibility fix for shared/custom launch folders.

Known areas that still require manual/native confidence include:

- first-run behaviour on completely independent PCs/VMs;
- real physical DPI/GPU combinations beyond the local probes;
- some save/load and re-entry cases;
- dynamic encounter ownership restoration inside the native engine;
- collision/pathfinding behaviour for particular spawn points/templates;
- real network/multiplayer behaviour.

The project does not hide these gaps. Native-game acceptance cases are tracked separately from offline test results.

See [Known issues](docs/KNOWN_ISSUES.md), [Final product report](docs/FINAL_PRODUCT_REPORT.md) and [Manual runtime checklist](docs/MANUAL_RUNTIME_CHECKLIST.md).

---

# Documentation

User-facing English documentation:

- [Getting started](docs/GETTING_STARTED.en.md)
- [First run](docs/FIRST_RUN.en.md)
- [Editor guide](docs/EDITOR_GUIDE.en.md)
- [Authoring guide](docs/AUTHORING_GUIDE.en.md)
- [Tutorial](docs/TUTORIAL.en.md)
- [Showcase](docs/SHOWCASE.en.md)
- [Dynamic encounters](docs/DYNAMIC_ENCOUNTERS.en.md)
- [Shortcuts](docs/SHORTCUTS.en.md)
- [Troubleshooting](docs/TROUBLESHOOTING.en.md)

Technical/project documentation:

- [Architecture](docs/ARCHITECTURE.md)
- [Format notes](docs/FORMAT_NOTES.md)
- [Engine notes](docs/ENGINE_NOTES.md)
- [Scene model](docs/SCENE_MODEL.md)
- [NOT format](docs/NOT_FORMAT.md)
- [Packages](docs/PACKAGES.md)
- [Testing](docs/TESTING.md)
- [Contribution/quality criteria](docs/CONTRIBUTING.md)
- [Dependencies and notices](docs/DEPENDENCIES_LICENSES.md)

---

# Design principles

A few rules define the project:

1. **Use the original engine, not the original authoring workflow.**
2. **Do not modify original geometry.** Reuse it as the world the chronicle lives in.
3. **Keep ordinary authoring visual.** YAML/Java are escape hatches and implementation details, not the required day-to-day workflow.
4. **One source of truth.** Assistants, graph views, properties and the CLI all operate on the same project data.
5. **Fail safely.** Missing ownership, broken references and unsupported future formats should stop clearly rather than corrupting a chronicle.
6. **Do not invent engine behaviour.** Features should be based on original resources/API evidence or explicitly labelled as inferred/experimental.
7. **Keep the original installation clean.** RCM owns only its managed project/deployment area.
8. **Separate offline proof from native proof.** A successful generated build is not automatically claimed as a successful in-game test.

---

# Licensing and original game assets

RCM’s packaged dependencies carry their own third-party licences and notices. The portable distribution keeps those notices with the application. See [Dependencies and licences](docs/DEPENDENCIES_LICENSES.md).

The project currently does **not** declare a public licence for RCM’s own source code. Do not assume rights beyond what the repository explicitly grants.

No original Redemption executable, original authoring tool, original game archive, model, level or texture is meant to be redistributed as part of the RCM public application. A legitimate complete game installation remains a required dependency.

---

## Short version

If you only want to use RCM:

```text
1. Extract the full Windows release.
2. Run RedemptionChronicleMaker.exe.
3. Point it at Vampire.exe.
4. Open Quick tutorial or create a New chronicle.
5. Author visually.
6. Press F5.
7. In Redemption: Multiplayer → LAN → New Game.
8. Select your chronicle.
```

That is the intended workflow: **idea → author → F5 → play in Redemption**.

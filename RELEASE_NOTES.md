# Redemption Chronicle Maker 1.0.0-rc7

- Opening a chronicle now shows a wait cursor and “Opening chronicle…” before loading, including recent-project double-clicks. Repeated opens are blocked during loading; failures restore the cursor and controls. Feedback is translated into English/Spanish.

This release builds on RC5 with clickable original scenery, corrected arrival navigation, optional Within The Darkness content import and safer editing workflows. Original level geometry remains unchanged.

- Fixed a Showcase module-load crash caused by appending currency declarations from different base maps beyond Redemption's three-slot CASH table. Campaign builds now merge and bound those declarations; the output gate rejects overflowing NMF files. Five regression tests cover this case. The user confirmed corrected initial loading on 2026-10-18; later cinematic/save/network cases remain separate.

## Original scenery and click actions

- Identify original objects directly from the 3D viewport, open the object picker with the clicked object selected, and locate objects in the scene. Embedded scene brushes are included, making doors easier to identify.
- Attach native hover labels and click actions to original objects or selected fixed surfaces. Actions use the existing event system: travel, conversations, notes, flags, quests, cameras, cutscenes, rewards and reusable events. These interactions activate on click rather than on entering a nearby trigger.
- Hide, restore or remove supported original objects, and control supported doors through the original-object tools. Fixed geometry stays immutable; selectable overlays provide click interactions on its surfaces.
- New click events receive editable names such as `click_drippyCandle_4`. Existing event names are preserved.
- Right-clicking a fixed surface temporarily displays its interaction bounds while choosing an action. Cancelling clears the preview without changing the project.
- Fixed a regression that prevented bound objects from highlighting and receiving clicks. Runtime binding checks object identity and rejects ambiguous matches.
- Prevented self-scene travel links and added runtime guards against recursive events and repeated transitions.

## Arrival and movement

Corrected the initial movement after arriving in a scene, which could previously take an unnecessary detour until a second click. Generated entrance records now use the containing original sector and the engine's native party relocation mechanism to refresh navigation state. This does not modify the original geometry or replace the game's pathfinding system.

**Confirmed in game by the user:** the repaired scenery hover/click interactions and initial movement now work correctly in the tested chronicle.

## Optional Within The Darkness import

- Import a user-supplied `WTDarkness.nob` from the application settings. The source archive does not need to be installed in the game's root folder.
- Make supported clans, disciplines, actor templates, models and the Penthouse level available for authoring. Only usable content is offered; the mod's demo, menus and interface replacement are excluded.
- Keep imported resources local. They are not bundled with the public application or redistributed in chronicle distribution archives; recipients need their own local import when required.
- Installed content is shared across RCM launches, independently of the selected chronicle or current workspace import. The root RCM folder owns the pack; isolated native launch folders receive verified mirrors automatically. Launching without RCM leaves the base game unchanged.
- Without an import, the existing base-game workflow remains unchanged. Rabbit is not required to expose models already present in the base game.

## Safer editing and usability

- Unified **safe delete** across the editor, 3D viewport and campaign tools. Preview incoming references, navigate to them and choose validated cascade removal where supported. Associated technical data and empty events are removed when appropriate, unrelated content is preserved, and deletion remains undoable.
- Improved viewport navigation with UE4-style mouse shortcuts, corrected horizontal movement and smoother vertical camera rotation.
- Improved story graph and table contrast, stable tab placement, more compact controls, scrollable forms and full-text tooltips.
- Added resource filtering and catalogue-based inventory selection to reduce manual searching.
- English and Spanish interface selection persists between sessions.

## Compatibility and retained features

RC4 dynamic encounters remain available: ambushes, waves, continuous generators, reinforcements and boss phases use the existing event/action system. Existing authored encounters are preserved. Format 10 remains optional, and format 9 stays supported. The accepted tutorial **Una carta al amanecer** and the mini chronicle are preserved; the separate dynamic encounter lab remains available for testing.

Startup inventory compatibility is preserved: required custom template libraries are available before LAN character restoration. Deployment manages files inside the authorized RCM folder while preserving unrelated files and player profiles. Projects remain separate from the program folder.

## Validation and remaining checks

- Latest recorded automated run: **525 tests passed**, with no failures, errors or skipped tests. These cover offline integration, editor models, generated formats and build behaviour.
- An additional 140 widget regressions passed after compacting the property controls. Generated Java was compiled against the real Codex API with the required Java 45.3 class format. Packaged editor checks run in English and Spanish, with restricted PATH and moved folders; this is not independent-machine or native gameplay acceptance.
- Native acceptance includes the previously accepted tutorial and the user's latest confirmation of scenery click interactions and initial movement. This confirmation applies to the tested scenario and does not certify every level or runtime configuration.
- Broader native save/load ownership, re-entry, spawned-actor collision/navigation and networking still require the applicable manual checks. A lethal hit may skip a health threshold; no universal before-death interception is promised.

RCM does not distribute original Vampire: The Masquerade — Redemption assets or the original authoring tools. This remains a release candidate rather than final 1.0.

## Cinematic Director and native world authoring closure

- Capture/edit project camera paths from the viewport, with a conservative linear NCP writer founded on all 174 originals and the native reader/evaluator. One-point fixed shots, ordered keyframes, project packaging, fingerprints, references and cascade deletion; no invented FOV keys.
- Choreograph films with timed normal Actions and line-start dialogue Actions. Native shot/effect, LookAt/known motion, named conversation staging, positioned loop/Stop, small entity-attached dynamic light and demonstrated weather controls use real Codex APIs.
- New cue films cancel safely on load to avoid replaying side effects; old films keep their previous policy. No automatic project format conversion or new main tab.
- Optional Showcase Director lab and separate Arrival at the refuge example, available from Help. Accepted tutorial/mini remain preserved. Generated files, compilation, doubles and packaged UI checks are distinct from native acceptance. EMB01–24 document pending user checks; no new version number or final-1.0 claim.

## Final targeted authoring closure

- Temporary music and Restore previous music are ordinary Actions, available in events, click interactions, dialogue lines, film cues and boss phases. Investigation of the actual Codex bytecode shows a single Java snapshot, not a nested native stack. Nested pushes and unowned restores fail closed; ownership is transient across load, with explicit normal music available for recovery.
- Conversation properties now offer native party staging using one to four existing named Entry markers. RCM writes the evidenced 60-byte conversation records in generated NSD and calls the real TeleportPartyToConversation API. Existing automatic and RCM Entry staging remain supported. Named references, safe deletion, rename, undo and packaging are covered.
- All 174 original NCP files were rechecked. Repeated-position keys also repeat their path parameter, so no timed stationary rotation is invented. Authored stationary NCP rotation remains PARTIAL; one-point fixed holds and original paths remain available.
- Optional Showcase/refuge labs demonstrate the new music and party staging. Normal music is explicitly set when retrying or skipping the film. Compact dropdowns and full-text tooltips keep property forms usable at narrow widths.
- New manual cases are EMB-MUSIC-01..03, EMB-CONV-01..05 and EMB-NCP-01..05, in addition to the retained EMB01–24 and DYN01–12. New native behaviour remains MANUAL RUNTIME TEST REQUIRED. Version and formats remain rc7 and 9/10.


## Strict original authoring audit

- Scene environment controls for initial audio/volume, fog, view distance and
  compatible paired sky; original EAX retained because static-scene activation
  takes precedence. No geometry/lightmap edits.
- Template and local instance Foley, AI, motion sets, hover text and native
  container treasure classes, selected from actual original data.
- Advanced typed stock constructor binding with real metadata, entity links and
  native movement frames; native scripts retain callback/save ownership.
- Optional native interest group on waypoints, distinct from patrol routes.
- Selected data-only NOT/NOB library import with local dependency ownership;
  no menus, chronicles or external binary code, no assets inside public ZIPs.
- Separate Cargo at the refuge acceptance example; accepted tutorial unchanged.
- Replaced permissive parity claims with an eight-column strict audit. EAX,
  native regional context, sound/light boxes and stationary timed camera keys
  remain explicit limits. New native cases require user observation in game.
- Investigated original map illustrations/points/names/visibility: custom maps
  are feasible without Embrace or NIL editing; no map editor is advertised yet.

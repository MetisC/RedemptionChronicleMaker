# Changes · 1.0.0-rc7

- Opening a chronicle now shows a wait cursor and “Opening chronicle…” before loading, including recent-project double-clicks. Repeated opens are blocked during loading; failures restore the cursor and controls. Feedback is translated into English/Spanish.

- Fixed mixed-map Showcase metadata overflowing the native three-currency table before scene startup. One deduplicated, bounded CASH declaration is generated, and unsafe cumulative declarations fail output verification. Corrected initial loading confirmed by the user on 2026-10-18.

- Right-click original scenery to identify and use the pointed object. Inline NSD brush previews, exact triangle picking and Locate in 3D expose generic props such as Tenebrae's exit. Fixed NIL surfaces support native selectable brush overlays with hover labels and ordinary click actions.

- Optional Within The Darkness import from a user-supplied NOB: usable clans, disciplines, actors/models and reusable Penthouse geometry, excluding demo/menu reskin. Initial actor traits and event rewards use the real Codex API. Imported assets stay local, outside program/chronicle distribution ZIPs. Installed content now applies across managed RCM launches independently of the current workspace import: the root owns the pack and isolated native launch folders receive verified mirrors. Normal launches without RCM remain unchanged.

- Original static-object picker and passage helper: hide/restore/remove props, operate framed or pivot doors, and create click/travel events without editing base geometry. Native identity checks reject missing or ambiguous targets; door appearance, collision and original-script interaction remain manual checks.

- Unified entity deletion with reference navigation and a validated cascade preview. Fresh spawns can be deleted; linked uses can be removed together in one undo operation, without weakening conditions or deleting unrelated actions.

- Fixed startup inventory compatibility in shared/custom launch folders. After an editor playtest, saved item definitions are refreshed in managed folders so returning to another chronicle does not lose them. Saved characters are never edited.

- Dynamic encounter wizard: ambush, waves, continuous spawning, reinforcements and boss phases, in Campaign, assistants and the existing 3D ground menu.
- Original enemy filtering and confirmed template health, AI, flags, clan and scene provenance.
- Waypoint/near-player spawning, caps, bounded retries, pause/resume/stop/reset, existing event actions and health/counter/state conditions.
- Native GUID ownership records, bounded restore reconciliation, wave/batch cursors, thresholds and cooldown. Missing ownership fails closed instead of spawning duplicates.
- References, safe deletion, duplication, undo, graph and trace navigation include generators. English/Spanish UI.
- Opt-in format 10 with a backup; format 9 opens unchanged. Accepted tutorial source/runtime preserved. Separate Dynamic Encounter Lab and small optional Showcase station.
- Alias-free YAML writing now round-trips shared point lists through the existing safe loader.

First-run, safe saving, deployment, cache identity and language preferences remain. Native gameplay, independent-PC and real GPU/DPI checks remain manual. Not final 1.0.

Native click interactions: hover label plus arbitrary existing actions, including Event / Run. Self-scene travel/jump is rejected in validation and destination selectors. New click runtimes guard self travel, synchronous event recursion and repeated transition entry. The accepted tutorial runtime remains unchanged; the user confirmed hover/click and first movement in the tested chronicle; broader CLICK01–08 combinations remain manual.

Cinematic Director closure: own linear NCP capture/editor/writer, timed shared Actions and dialogue line Actions, native camera effects/staging, spatial loops with Stop, entity-attached lights and demonstrated weather. Optional Showcase lab plus refuge acceptance chronicle. Native rendering/audio/save/reentry checks remain EMB01–24; existing accepted content preserved. Version remains rc7.

Final targeted closure: temporary-music/restore Actions with evidenced single-snapshot ownership; native party conversation staging through existing named Entries and bounded generated NSD; references/rename/cascade/undo and real Codex 45.3 compilation. Retained safe stationary-NCP authoring restriction after analysing all 174 original paths. Optional labs updated, narrow property controls corrected. Fresh full gate: 525 tests, 0 failures/errors/skips; subsequent widget regression: 140, 0 failures/errors/skips. New native audio/formation/save/MP cases remain manual; no version or project-format increase.


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


## Optional chronicle combat difficulty

Chronicle properties now offer Easy, Normal, Hard and Nightmare in English and
Spanish. Normal is unchanged. Fresh RCM enemy health/maximum and native
Strength/Stamina use conservative factors (Easy .8/.9/.9, Hard1.2/1.1/1.1,
Nightmare1.5/1.2/1.2). Dynamic HP overrides are applied first. Enemy team/neutral
checks exclude allies, players and ordinary conversation NPCs. Existing GUIDs
and save/re-entry do not rescale; no new native save record is added. Changing
difficulty recommends a new game for uniform results. Native balance, equipment,
save/load and multiplayer observation remain DIFF manual checks.

Imported-library management now checks project and parent dependencies before
removing local copies. Shared deployments and saved inventories retain complete
verified data libraries, including transitive resources. Custom-script builds
verify actual Codex inheritance as well as constructor signatures. Instance
animation selectors refresh after motion-set changes; internal generated
inheritance records are hidden from ordinary browsing.

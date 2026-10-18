# Changes · 1.0.0-rc6

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

Native click interactions: hover label plus arbitrary existing actions, including Event / Run. Self-scene travel/jump is rejected in validation and destination selectors. New click runtimes guard self travel, synchronous event recursion and repeated transition entry. The accepted tutorial runtime remains unchanged; native CLICK01â€“08 checks are pending.

Cinematic Director closure: own linear NCP capture/editor/writer, timed shared Actions and dialogue line Actions, native camera effects/staging, spatial loops with Stop, entity-attached lights and demonstrated weather. Optional Showcase lab plus refuge acceptance chronicle. Native rendering/audio/save/reentry checks remain EMB01–24; existing accepted content preserved. Version remains rc6.

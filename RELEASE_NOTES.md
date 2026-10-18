# Redemption Chronicle Maker 1.0.0-rc6

This release builds on RC5 with clickable original scenery, corrected arrival navigation, optional Within The Darkness content import and safer editing workflows. Original level geometry remains unchanged.

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

- Latest recorded automated run: **482 tests passed**, with no failures, errors or skipped tests. These cover offline integration, editor models, generated formats and build behaviour.
- Generated Java was compiled against the real Codex API with the required Java 45.3 class format. Packaged editor checks passed in English and Spanish.
- Native acceptance includes the previously accepted tutorial and the user's latest confirmation of scenery click interactions and initial movement. This confirmation applies to the tested scenario and does not certify every level or runtime configuration.
- Broader native save/load ownership, re-entry, spawned-actor collision/navigation and networking still require the applicable manual checks. A lethal hit may skip a health threshold; no universal before-death interception is promised.

RCM does not distribute original Vampire: The Masquerade — Redemption assets or the original authoring tools. This remains a release candidate rather than final 1.0.

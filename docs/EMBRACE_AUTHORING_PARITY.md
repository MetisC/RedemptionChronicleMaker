# Embrace authoring parity · current closure matrix

This report separates implemented authoring from native acceptance. It does **not** claim 100% rendered/runtime parity or final 1.0. Baseline audit and primary evidence: [EMBRACE_AUTHORING_CLOSURE](../research/embrace_closure/EMBRACE_AUTHORING_CLOSURE.md), [NCP analysis](../research/embrace_closure/ncp_format.md), original calls/field catalogues beside them.

| Embrace capability | RCM equivalent | Status | Evidence | Runtime test |
|---|---|---|---|---|
| Brushes, CSG, level surfaces, UV, lightmaps, structural sectors/portals | Immutable reusable NIL | OUT OF SCOPE: GEOMETRY | Embrace manual; unchanged original files | Not applicable |
| Entities, transforms, templates, inventory, AI override | Typed authoring, own NOT/AI/Java, catalogues | COVERED DIFFERENTLY | model/project_resources, existing suites | Existing accepted tutorial; new models independently checked |
| Original hover/click and fixed-surface interactions | Native selectable NSD overlays, normal events/actions | COVERED DIFFERENTLY | click_interactions, original NSD and user confirmation | Latest user confirmed clicks; broad save/network checks remain |
| Door frames/pivots, hide/restore/remove | control_original / control_door | COVERED DIFFERENTLY | Original scripts and Codex methods | ORG / EMB02; not universal fixed-geometry animation |
| Playerstarts | Named entries/default entry, native NSD records and relocation | COVERED DIFFERENTLY | Native entrance reader and user-confirmed initial navigation | Re-entry/save/network matrix remains |
| Conversation starts | Named entry staging before conversation | COVERED DIFFERENTLY | UNIV_7_7 party staging; real entrance API | EMB04 / EMB18 |
| Interest spots | Existing waypoints and patrols | COVERED DIFFERENTLY | Manual 0–9; no additional Codex interest API/use found | No unproven idle behaviour claimed |
| Conversations, choices, flags, quests, notes, scenes, exits | Existing typed story/event system | COVERED DIFFERENTLY | Original formats, scripts and accepted tutorial | Existing acceptance remains scoped |
| Encounters, generators and boss phases | Existing encounters plus optional format-10 generators | COVERED DIFFERENTLY | Dynamic research and tests | DYN01–12 remain independent |
| Shots, subject/reference, camera focus | Existing presets, timelines and camera_shot Action | COVERED | CodexCamera SDK / original calls | EMB04–05 |
| Create camera paths | Own linear NCP writer, modeless viewport point capture/edit/reorder | NATIVE TEST REQUIRED | All 174 originals round-trip; native evaluator/128-key buffer | EMB09–11 |
| Original camera paths | Existing original PlayPath | COVERED | 71 original class references | EMB08; geometry-specific |
| Film choreography | Timed normal Actions, existing shot/prop/actor movement | NATIVE TEST REQUIRED | Shared event compiler; lifecycle doubles and real compilation | EMB05–07 / EMB15–17 |
| convreached choreography | Actions at line start plus existing motion/camera | NATIVE TEST REQUIRED | SDK/source example and original bytecode | EMB18 |
| Fade/flash/filter | Normal Actions; native fade and white effects, clear | NATIVE TEST REQUIRED | SDK; original fade/white flash calls; filter API | EMB12–13; arbitrary colour packing excluded |
| LookAt, gestures, stop/move actor | Shared Actions and actual NMS choices, existing patrols | COVERED DIFFERENTLY | CodexThing/Actor; original scripts | EMB06–07; model-specific |
| Music and ambient | Existing start/stop Actions | COVERED | SDK and original scripts | Existing acceptance plus EMB14 |
| Spatial sound objects/loops | Waypoint sound, named owned loop and Stop | NATIVE TEST REQUIRED | CodexSound SDK/constructors, save/recreate doubles | EMB14 / EMB19 |
| Soundbox intent | Existing enter/leave volumes + start/stop sound | COVERED DIFFERENTLY | RCM triggers and native sound API | EMB19; no soundbox brush writer |
| Runtime dynamic lights | Small entity-attached light Action, native style/color/radius/intensity | NATIVE TEST REQUIRED | Manual dynamic/editor-only distinction, actual JNI/API; own state/reapply | EMB20; no baked lighting claim |
| Weather | Original demonstrated weather names, saved selection | NATIVE TEST REQUIRED | Five original class references | EMB20; global engine effect, not new weather assets |
| Fog/EAX/ZClip/sky | Preserve original environment profiles | COVERED DIFFERENTLY | Native 176-byte tail reader; SCENE_MODEL | No invented offset controls |
| Codex Linker/script relationships | Events/Conditions/Actions, References, custom Java escape hatch | COVERED DIFFERENTLY | Existing callback pipeline and SDK | New cues compile through the same pipeline |
| WTD usable resources/Penthouse | Existing filtered local import and shared RCM runtime | COVERED DIFFERENTLY | Import policy, real pack and shared-content tests | WTD / EMB21; no mod assets in public package |
| Save/restore | Existing contracts plus opt-in director/audio/light state | NATIVE TEST REQUIRED | Ordered native Save/Restore calls and doubles | EMB16–17 / original save checklist; no migration claim |
| Packaging/debug | F5, own packages, diagnostics, bounded traces | COVERED DIFFERENTLY | Build/readback/portable tests | EMB22–24 |

## Scope conclusion

The important authoring gaps identified by the fresh audit now have implementations or established RCM abstractions. This is **authoring coverage**, not a declaration that the newly rendered scenes, spatial sounds, light, weather, every door, save/re-entry combination or networking have been observed working in Redemption. Those rows remain explicitly **NATIVE TEST REQUIRED** until the user completes the EMB cases. No additional release candidate number is created by this work.

Geometry creation/editing, CSG, UV/texturing, lightmap generation and structural sector/portal editing remain excluded by design. Unknown legacy binary tails, arbitrary camera FOV keys, unverified colour presets and universal door animation are not presented as completed features. Generic custom Java remains the deliberate escape hatch for specialist engine behaviour.

# Embrace authoring closure · audit of HEAD

Baseline: `b70149d` (the repository already identifies itself as 1.0.0-rc6; this work does not introduce another release number). Audit performed before implementing the extensions below. No original authoring application or game session was executed.

## Evidence categories

- **CONFIRMED IN MANUAL/SDK:** preserved Embrace manual, cutscene tutorial and Codex class documentation in `research/sdk/`.
- **CONFIRMED IN BYTECODE/API:** `research/API_SIGNATURES.txt`, actual Codex classfiles and the new `original_callsites.txt` disassembly. A referenced method is not evidence of its visual outcome.
- **CONFIRMED IN ORIGINAL SCRIPT:** executable instructions in the original classfiles, with class/method and bytecode offsets preserved in `original_callsites.txt`; SDK UNIV_7_7 source is identified separately as a documented example.
- **CONFIRMED IN ORIGINAL FILE:** 174 original NCPs, NSD/NIL/NOT/NMS research and the native executable reader. Original files remain unchanged.
- **ALREADY IMPLEMENTED IN RCM:** source paths below and existing regression suites, checked against HEAD rather than historical feature claims.
- **INFERRED:** mathematical interpretation requiring a native observation; labelled explicitly in the NCP report.
- **NOT FOUND:** no demonstrated call site in the 472-entry Codex archive scan. This does not prove an API is unusable.
- **NATIVE TEST REQUIRED:** all newly generated visual/audio behaviour. Offline tests, real compilation and packaging are separate gates.

## Capability matrix before changes

| Area | Original capability and evidence | HEAD equivalent | Status | Decision |
|---|---|---|---|---|
| A Geometry / level design | Brushes, CSG, structural sectors/portals, UV and lightmaps; Embrace manual | Immutable original NIL | OUT OF SCOPE: GEOMETRY | No implementation |
| B World authoring | Place/rotate template entities, override descriptions and scripts; manual Thing Properties | Actors/objects/transforms, own templates and Java; model/project_resources | COVERED DIFFERENTLY | Retain |
| B World authoring | Native selectable props and existing door frames/pivots; original NSD and door scripts | Original-object picker, exact picking, click overlay, control_original | COVERED DIFFERENTLY | Retain; latest click regression accepted by user |
| B World authoring | Playerstarts 0–15; manual and native entrance reader | Named entries/default_entry, own NSD entrances and native party relocation | COVERED DIFFERENTLY | No duplicate playerstart system; latest initial movement accepted by user |
| B World authoring | Conversation starts; manual, UNIV_7_7 and 107 original class references | No named conversation staging selector | PARTIAL | Add named staging through existing entries and native relocation, without another spatial collection |
| C Story / gameplay | Conversations, RETURN/GOTO, flags, quests, inventory, scene variants and exits | Existing authoring/runtime/campaign abstractions | COVERED DIFFERENTLY | Preserve accepted tutorial and inventory boot contract |
| C Story / gameplay | Ambushes, spawning, encounters | Existing encounters and optional format-10 generators | COVERED DIFFERENTLY | Preserve DYN01–12 manual gates |
| D Cinematics | SetupCutscene/SetShot; SDK and original scripts | Presets, subject/reference, shot timeline and lifecycle | COVERED | Extend, do not replace |
| D Cinematics | Original path camera playback; 71 class references | Existing camera_path/PlayPath | COVERED | Preserve |
| D Cinematics | Create path cameras; SDK debug commands, 174 NCPs, native reader/writer/evaluator | No own NCP writer | MISSING | Investigate all fields; implement only demonstrated subset |
| D Cinematics | AddFade, AddFlash, AddFilter, ClearAllEffects; SDK/API; 28/7/0/4 class references | Not available as ordinary Actions | MISSING | Add proven effects to shared Actions; colour packing requires native evidence before colour UI |
| D Cinematics | Coordinated camera, animation, motion, audio and events | Shot timeline plus one actor/prop route | PARTIAL | Timed cues invoking the existing Action compiler |
| D Cinematics | convreached choreography; SDK and original UNIV_7_7 | Per-line motions and automatic framing | PARTIAL | Add ordinary line actions without changing NCO RETURN/GOTO |
| E Audio / atmosphere | Music/ambient, one-shot located sound; SDK and original constructors | Existing start/stop music/ambient and positioned sound | COVERED | Retain |
| E Audio / atmosphere | Loop sound handles and Stop; SDK CodexSound and original scripts | No owned spatial loop | PARTIAL | Add bounded named loops with explicit stop and opt-in save lifecycle |
| E Audio / atmosphere | Soundboxes and regions; manual | Conditional RCM enter/leave volumes | COVERED DIFFERENTLY | Reuse trigger volumes, no brush authoring |
| E Audio / atmosphere | Weather; SetWeatherEffect used by 5 original classes | Original NSD environment profile only | PARTIAL | Offer only effects demonstrated by original scripts/catalogue |
| E Audio / atmosphere | EAX/fog/ZClip/sky; manual, native NSD reader | Preserved original environment profile; opaque fields not exposed | COVERED DIFFERENTLY | Do not invent byte sliders or alter accepted London environment |
| E Audio / atmosphere | Dynamic lights; manual separates editor-only from runtime; CodexThing API | Own templates/custom Java, no dedicated safe editor action | PARTIAL | Inspect allocation/setters and original resources; avoid baked lighting claims |
| F Actor staging | LookAtThing/LookAtPos, motion slots, StopActorAction, SendActorToPos | Facing dialogue, validated NMS motions, waypoints/patrols | PARTIAL | Expose missing look/gesture/stop operations in ordinary Actions |
| F Actor staging | Interestspots 0–9; manual | Named waypoints/patrols | COVERED DIFFERENTLY | No unique demonstrated narrative behaviour found; no parallel interestspot system |
| G Runtime / scripting | Codex Linker and callback relationships; manual | Typed Events/Conditions/Actions, references and custom Java | COVERED DIFFERENTLY | Reuse shared pipeline for cues and line actions |
| H Resources / mod content | NOT/model/AI/resource libraries | Catalogues, own templates/AI/Java/textures, packages, local WTD and Penthouse | COVERED DIFFERENTLY | Extend resource lifecycle for own camera paths; preserve local-only WTD |
| I Save / restore | Script-owned native save callbacks | Versioned save contract, entities, flags, patrols, interrupted films | NATIVE TEST REQUIRED | Preserve unchanged projects; opt-in records and signature for new state |
| J Debug / test | Console/dev camera/manual test | F5 pipeline, build/readback, trace, references, tests and explicit manual checklist | COVERED DIFFERENTLY | Add bounded cinematic traces and EMB cases; no automated gameplay |

## Justified implementation list

1. Evidence-backed NCP codec and project resource lifecycle, with visual capture/editing integrated into Sequences.
2. Shared camera-effect and actor-staging Actions; existing paths remain the movement abstraction.
3. Sequence timed Actions and conversation-line Actions, sharing validation and code generation.
4. Named conversation staging using existing entry markers; no duplicated start-point system.
5. Owned spatial loops and demonstrated weather controls, with explicit lifecycle and manual acceptance gates.
6. A single optional Showcase cinematic lab and a separate coherent acceptance chronicle.

This is an implementation decision list, not a claim of completed parity or native acceptance. Final status belongs in `docs/EMBRACE_AUTHORING_PARITY.md` after tests.

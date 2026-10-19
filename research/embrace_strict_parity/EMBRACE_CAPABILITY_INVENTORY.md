# Inventario original de capacidades

La cobertura RCM vigente está únicamente en docs/EMBRACE_AUTHORING_PARITY.md.
Este inventario conserva la descripción original que fundamenta la comparación.

| Capacidad original | Interfaz original | Datos/API nativos |
|---|---|---|
| Template placement and transforms [NON_GEOMETRY_MATERIAL] | Thing editor / placed templates | NSD tagged entity transforms; Native engine consumes NSD tagged entity transforms |
| Template inheritance [NON_GEOMETRY_MATERIAL] | Thing editor / Template Files | NOT parent tag 0; Native engine consumes NOT parent tag 0 |
| Script assignment and deletion [NON_GEOMETRY_MATERIAL] | Overrides tab | script tag 11; script-parameter blocks; Native engine consumes script tag 11; script-parameter blocks |
| Foley [NON_GEOMETRY_MATERIAL] | Overrides tab | NOT tag 6, NAG sound set; Native engine consumes NOT tag 6, NAG sound set |
| Motion set [NON_GEOMETRY_MATERIAL] | Key/value pairs | NOT tag 9, NMS; Native engine consumes NOT tag 9, NMS |
| AIClass [NON_GEOMETRY_MATERIAL] | Overrides tab | NOT tag 56, NAI; Native engine consumes NOT tag 56, NAI |
| DescriptionID [NON_GEOMETRY_MATERIAL] | Overrides tab | NOT tag 82, NLS; Native engine consumes NOT tag 82, NLS |
| TreasureClass [NON_GEOMETRY_MATERIAL] | Overrides tab | tag 92 uint32, GAME.NTT CLASS 0..255; Native engine consumes tag 92 uint32, GAME.NTT CLASS 0..255 |
| Per-instance keys [NON_GEOMETRY_MATERIAL] | Key/value grid applies to placed instance | NSD entity tag list; Native engine consumes NSD entity tag list |
| Layer selection per scene [NON_GEOMETRY_MATERIAL] | Scene Layers tab | NSD/NSC; Native engine consumes NSD/NSC |
| Music and volume [NON_GEOMETRY_MATERIAL] | Scene Sound tab | tail 0/68; activation 42c59e..5bd; Native engine consumes tail 0/68; activation 42c59e..5bd |
| Ambient and volume [NON_GEOMETRY_MATERIAL] | Scene Sound tab | tail 32/72; activation 42c5d9..5fb; Native engine consumes tail 32/72; activation 42c5d9..5fb |
| EAX [NON_GEOMETRY_MATERIAL] | Scene Sound tab | tail 76, scene+90; static-scene precedence in 42c6f9; Native engine consumes tail 76, scene+90; static-scene precedence in 42c6f9 |
| Fog mode/RGB/distances [NON_GEOMETRY_MATERIAL] | Scene Render tab | tail 80..100, loader and 42c4c4 renderer call; Native engine consumes tail 80..100, loader and 42c4c4 renderer call |
| ZClip [NON_GEOMETRY_MATERIAL] | Scene Render tab | tail 104, activation 42c53c..580; Native engine consumes tail 104, activation 42c53c..580 |
| Sky NOD/NAD [NON_GEOMETRY_MATERIAL] | Scene Sky tab | tail 112/144, original loader; Native engine consumes tail 112/144, original loader |
| Player starts [NON_GEOMETRY_MATERIAL] | Right-click playerstarts 0..15 | NSD native table; Native engine consumes NSD native table |
| Conversation starts [NON_GEOMETRY_MATERIAL] | Right-click convstarts 0..15 | NSD 60-byte records / TeleportPartyToConversation; Native engine consumes NSD 60-byte records / TeleportPartyToConversation |
| Interest spots [RUNTIME_RELEVANT] | Right-click interestspots 0..9 | Separate native table; NAI interestNum has nonzero uses; Native engine consumes Separate native table; NAI interestNum has nonzero uses |
| Actor movement paths [NON_GEOMETRY_MATERIAL] | Path corners / scripts | Codex actor movement; Native engine consumes Codex actor movement |
| Regions [NON_GEOMETRY_MATERIAL] | Region brushes / scripts | NSD regions; Native engine consumes NSD regions |
| Sound objects [NON_GEOMETRY_MATERIAL] | Thing Sound tab | Native sound data and CodexSound; Native engine consumes Native sound data and CodexSound |
| Soundboxes [RUNTIME_RELEVANT] | Thing Sound tab | NSD box/sound semantics require investigation; Native engine consumes NSD box/sound semantics require investigation |
| Runtime lights [NON_GEOMETRY_MATERIAL] | Light tab / Editor Only off | Native dynamic lights; Native engine consumes Native dynamic lights |
| Editor Only lights [GEOMETRY_ONLY] | Light tab / Editor Only on | Baked lightmaps; Level build / editor only |
| Lightboxes [UNKNOWN] | Right-click lightbox | Native mesh/light blocks must be followed; Native engine consumes Native mesh/light blocks must be followed |
| Door/exits/selectable scenery [NON_GEOMETRY_MATERIAL] | Quick Doors / thing scripts | Native movable existing brushes/frames/selectable flags; Native engine consumes Native movable existing brushes/frames/selectable flags |
| Codex Linker string/int/float [NON_GEOMETRY_MATERIAL] | Shift-C Value/Type/Description | Java constructor signature + variable NSD records; Native engine consumes Java constructor signature + variable NSD records |
| Codex Linker thing/actor links [NON_GEOMETRY_MATERIAL] | Shift-C select target template | Native reference relocation / constructor types; Native engine consumes Native reference relocation / constructor types |
| Custom Java scripts [NON_GEOMETRY_MATERIAL] | Script assignment / compiler | Real classfiles; Native engine consumes Real classfiles |
| Conversation/camera choreography [NON_GEOMETRY_MATERIAL] | Cutscene manual | Codex APIs / NCO; Native engine consumes Codex APIs / NCO |
| Fixed shot / SetShot / release [NON_GEOMETRY_MATERIAL] | Cutscene manual | CodexCamera; Native engine consumes CodexCamera |
| Camera paths/keyframes [NON_GEOMETRY_MATERIAL] | Camera editor / savepath | NCP evaluator, positive position span; Native engine consumes NCP evaluator, positive position span |
| Stationary camera turns [NON_GEOMETRY_OBSCURE] | Native path key insertion | Repeated parameter evidence; timing still unproven; Native engine consumes Repeated parameter evidence; timing still unproven |
| Fade/flash/filter [NON_GEOMETRY_MATERIAL] | Cutscene scripting | CodexCamera API; Native engine consumes CodexCamera API |
| LookAt / motions / walking [NON_GEOMETRY_MATERIAL] | Cutscene scripting | CodexThing/Actor / NMS; Native engine consumes CodexThing/Actor / NMS |
| Temporary music [NON_GEOMETRY_MATERIAL] | Original cutscene scripts | CodexSound single Java snapshot; Native engine consumes CodexSound single Java snapshot |
| External NOT libraries [NON_GEOMETRY_MATERIAL] | Template Files Add/Remove | NOT + dependency files; Native engine consumes NOT + dependency files |
| Models/motions/AI/foley resources [NON_GEOMETRY_MATERIAL] | File resource selectors | NOD/NAD/NMS/NAI/NAG; Native engine consumes NOD/NAD/NMS/NAI/NAG |
| External mods [NON_GEOMETRY_MATERIAL] | Template Files and resource archive loading | Local dependency closure; Native engine consumes Local dependency closure |
| Brushes/CSG/sectors/portals/UV [GEOMETRY_ONLY] | 2D brush editor / world build | Structural NIL/MAP; Level build / editor only |
| Lightmap baking [GEOMETRY_ONLY] | Build / Editor Only lights | Baked level data; Level build / editor only |
| Editor preferences/selection display [EDITOR_ONLY] | Preferences / Confirm on multiple selection | No runtime payload; Level build / editor only |

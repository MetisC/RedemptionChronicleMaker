# Native TreasureClass

CONFIRMED IN ORIGINAL FILES: property table 128 entries (40 bytes each), slot 92
is TREASURECLASS / integer. Original NOT inheritance contains 90 explicit uses.
GAME.NTT contains 160 CLASS entries, each in 0..255. The editor lists the actual
classes from that file, plus inherit and none (0). No private loot engine exists.

CONFIRMED IN EXECUTABLE: treasure_consumers.txt shows the native class lookup
and bounds checks. A class absent from the table has no drops; original class 0
is absent. container_guid_check.txt proves IsPropGuid only recognises type 2,
whereas containers are type 8. Generated container-enabled projects use the real
GetThingType/THING_TYPE_CONTAINER API to retain their handles.

CONFIRMED IN SDK: NTT.htm.txt, source recorded in NTT.source.json, describes
CLASS/CITEM and probability/treasure groups. Original probability rolls are
preserved. An individual empty roll is not evidence of a broken class.

IMPLEMENTED: own-template and placed-container controls; tag 92 uint32; valid
native class IDs only; instance changes become tiny inherited NOT definitions.
Inheritance omits tag 92. Explicit none writes 0. Not exposed on actors/props.
No native container script is replaced with a new loot system.

TESTS: test_strict_authoring covers type/range/catalogue/container restriction,
real Codex compilation and package readback. Optional strict_acceptance includes
class 230 and an inherited comparison barrel. EMB-TREASURE-01 remains MANUAL
RUNTIME TEST REQUIRED (break/open, repeated rolls, save/re-entry).

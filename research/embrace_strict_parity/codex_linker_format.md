# Native script binding and movement frames

CONFIRMED IN ORIGINAL FILES: real public constructor descriptors in Codex.nob
supply parameter order/types. 440 unambiguous Codex subclasses are catalogued after adding region/item links.
The baseline380 records and376 labels remain regression-checked. Literal
_params String[] initialisers are decoded as a bounded bytecode pattern, never
executed. Computed metadata falls back to typed parameter labels.

CONFIRMED IN EXECUTABLE: the FIRST entity variable block is movement frames:
count followed by 24-byte records, orientation XYZ then position XYZ. This order
is checked against tagged initial transforms (e.g. ANZK_14_1). The SECOND block
is CODEXPVALUE: u32 type, then variable payload. Reader 4b5060; relocation 4b5260
maps entity indices to actual GUIDs after placement. Types 1 int32, 2 float32,
3 thing index, 5 region index, 7 length+NUL string, 8 actor index and10 item index are authorable. Original 6 has
no payload; other original types retain their exact bytes but are not editable.
Null -1 is native, but not offered as a safe default for dereferencing scripts.

IMPLEMENTED: Actor/Object > Native script exposes stock/custom constructors and
typed controls. Links select actual same-scene entities. Frame 0 is the original
transform; additional frames select existing waypoints in order. Objects and
linked targets are placed in generated NSD before reference fixup. The runtime
adopts their handles and leaves original callbacks/save ownership with the
stock script. Incompatible RCM ownership (conversation, inventory, encounters,
click binding, additional creation) is rejected. No original Java is packaged.
Own Java parameters are declared in a normal advanced dialog and verified
against the compiled public constructor, JVM 45.3, rather than source regex.

REGRESSION: 64 original NSDs round-trip losslessly, including 19 parameter-only
files and 17 additional frame files; the older 28-file contract is separately
asserted. Test examples compile against actual Codex. The opt-in cargo example
binds ClassBobbing(thing,float,float,float) to a barrel with two native frames.

LIMITS: this is not a complete NSD reader for all original mesh/region layouts.
All stock constructors being catalogued does NOT mean all work on arbitrary
objects: region/quest/campaign-specific context may be required. Normal RCM volumes sample players; opt-in native regions now write box meshes
and sector links, leaving callbacks to original scripts. Arbitrary region
topology and CodexPlayer constructor binding are not silently inferred. Arbitrary external binary Java is not imported
by the data library tool. These remain PARTIAL authoring coverage, not 100%.
Native script save/re-entry and movement are MANUAL RUNTIME TEST REQUIRED.

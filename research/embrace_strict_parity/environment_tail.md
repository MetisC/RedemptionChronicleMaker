# NSD environment, fresh data flow

291 original tails are catalogued and hashed. The v8 reader 4a81c7..4a829f maps fields into the scene object; the activation block 42c4ae..42c718 demonstrates meanings, not just statistical similarity. environment_fields.json lists every offset, width, type, confidence and writable decision. Unknown offsets 64 and 108 remain byte-preserved.

Renderer registration and original rlDirect.dll were read, never executed. Function 1000d320 dispatches 0=disabled, 1=linear (D3D fog mode3, start/end), 2=exponential (mode1, density from parameter1), 3=EXP2 (outside the manual's requested set). RCM will expose 0/1/2 only. RGB is three floats in 0..255, not normalized 0..1; confirmed by activation conversion and original corpus. Distances remain engine units. ZClip=0 chooses native default10000 (0x461c4000); no meters or lightmap changes are claimed.

Audio nonempty names activate at native scene load with their volume. Empty native names do not stop a previously running track, so explicit Silence needs an ordinary native Stop call from the generated scene callback. Inheritance must remain byte-identical.

EAX is a separate finding: the field is proven, but activation prefers the original static scene at location+30 rather than the authored dynamic scene+34. Writing only our tail would often be ineffective. No misleading EAX control is exposed; a safe per-chronicle override still needs a demonstrated runtime setter or a separately owned static-scene mechanism. Copying an opaque profile is not editable EAX authoring.

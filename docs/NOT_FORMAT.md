# Inspector NOT propio

`python tools/not_inspector.py research/original/Resource.nob/misc/Templates/modernDay.not --template businessWoman --output build/diagnostics/businessWoman_inspected.json`

Resource Browser → plantilla → Inspeccionar muestra registro, propiedades conocidas y catálogo de herencia, solo lectura. No ejecuta NOT Editor.

## Confirmado en originales

Offset 0: NOT\x10. Offset 4: uint32 versión 1. Offset 8: uint32 cantidad. Desde 12: entradas de 36 bytes, nombre fijo de 32 más offset absoluto uint32. En cada registro: uint32 cantidad de tags, N tags de 36 bytes (uint32 ID + payload de 32), uint32 longitud de comentario y bytes de comentario. Tags desconocidos y el campo de nombre original se conservan para roundtrip. El parser rechaza registros/offsets truncados.

Global: 915; modernDay: 776; darkAges: 726; Multiplayer: 202 templates. Los cuatro se recodifican byte a byte. Multiplayer conserva 6786 bytes finales opacos, sin atribuirles significado. La regresión de lectura/escritura se ejecuta sobre los originales extraídos.

Tag 0 enlaza parent; catálogo previo resuelve propiedades heredadas y comunica si la cadena está completa. Campos conocidos: 1 orientation, 2 position, 3 sector, 4 model, 6 foley, 9 motions, 11 script, 16 thing type, 56 AI, 81 Cast ID, 82 Description ID, 92 TreasureClass uint32 y 114 actor flags. El inspector muestra interpretación, hex original y offset de cada tag; nombres de propiedades derivan de evidencia contrastada, no de una especificación oficial completa.

## Inferido / pendiente

No todas las propiedades ordenadas en el ejecutable han sido tipadas. Se conserva la evidencia, pero no se convierten bytes desconocidos a controles editables. La cola de Multiplayer y ciertos bloques auxiliares continúan opacos.

## Writer limitado

El writer genera hijos y propiedades contrastadas mediante el modelo de recursos propio; conserva tags desconocidos y bytes opacos al recodificar originales. No ofrece edición arbitraria de todas las propiedades del motor. El soporte de cada campo y sus límites se describe en FORMAT_NOTES.md.

## Strict authoring evidence update

Confirmed original-file/native evidence: NSD parameters are the SECOND entity
variable block (types 1/2/3/7/8 editable), movement frames are orientation XYZ then
position XYZ (24 bytes); 64 original files lossless. Native interest records are
72 bytes with a separate group selected by AI interestNum. TreasureClass is tag
92 uint32 and container-only in RCM. Optional environment patches touch proven
176-byte tail fields only; unknown bytes remain intact. EAX static precedence
prevents an effective dynamic override. Full evidence, safety limits and pending
native checks: research/embrace_strict_parity/codex_linker_format.md,
treasure_class.md, SAFETY_DECISIONS.md and docs/EMBRACE_AUTHORING_PARITY.md.
SDK-confirmed NTT/NSC documentation is separate from these original-file proofs.
Maps customisation remains an analysed route, not an implemented map editor.

# RCM 3D+ · Evidencia de escenografía nativa

Investigación y prototipo de brushes NSD como geometría decorativa añadida.
Escáneres: `scan_entities.py` (corpus completo) y `scan_templates.py` (plantillas NOT).
Corpus: `entity_corpus.json`, `template_dump.json` (291 escenas originales, 290 parseadas).

## Entidad brush NSD — layout confirmado por el corpus

Cada entidad NSD v8 serializa: tags → frames de movimiento → parámetros tipados →
presencia de brush → cuerpo brush → enlaces de región → bloque de luz.
El escritor acotado de RCM (`click_interactions.brush`) reproduce exactamente el
subconjunto observado: flags de cabecera `6`, sin bloque de luz, sin frames, planos
de colisión derivados de los bounds.

Corpus: 1.123 entidades con brush en escenas originales; todas las cabeceras usan
flags `6` y ninguna lleva bloque de luz coincidente. Ejemplo decodificado real
(`DOCK_LOT_1_1.nsd`, puerta): material `New_York\door1_NY`, 12 vértices, 12
triángulos, un grupo, bounds `[-8,-48,-80]..[8,48,80]`, seis planos, UV a escala de
mundo (~1 repetición / 64 u). El `spec` paramétrico replica esta convención de UV.

## Plantillas stock que definen el contrato de flags

| Plantilla | Tipo | collide | Flags relevantes | Uso RCM |
|---|---|---|---|---|
| `tracker_thing_null` | 2 (prop) | 0 | NOHIGHLIGHT | `mode: decor` — sólo visual |
| `tracker_thing_nohilite` | 2 | 3 (BBOX) | NOHIGHLIGHT, CAMERABLOCK | `mode: solid` — colisión experimental |
| `tracker_thing_blocker` | 2 | 3 | VISBLOCK+CAMERABLOCK+BLOCKSELECT+NOHIGHLIGHT, renderflags DONTRENDER | `mode: barrier` — barrera invisible experimental |
| `tracker_thing` | 2 | 3 | — | `mode: interactive` — clic vía `CaptureThing` |

`tracker_thing_blocker` aparece 13 veces en el corpus: es la evidencia nativa de
una entidad brush invisible que bloquea físicamente. `tracker_thing_null` aparece
13 veces con brushes sin colisión (decals/marcadores). Las regiones
(`trigger_region`, `cameraclip_region`) son tipo 3 con enlaces sectoriales; no son
props sólidos y no se reutilizan para geometría decorativa.

## API nativa relacionada (evidencia Codex)

- `SetCollideType`, `SetRenderFlags`, `SetThingFlags` existen en bytecode original.
- `CaptureThing` + `clicked` son el canal de interacción ya aceptado.
- `IsPropGuid` filtra el tipo 2; `GuidFromCastID`/`GetDescriptionID` resuelven la
  instancia NSD por identidad (cast id tag 81 / descripción tag 82).

## Estado de verificación

- DEMOSTRADO OFFLINE: emisión determinista del brush, readback binario
  (Scene.read → encode byte-idéntico), sector real desde planos NIL, compilación
  ECJ 45.3, binding por doubles (decor no captura; interactivo captura una vez).
- VERIFICADO EN JUEGO (usuario, 25/10/2026, scenery_lab): renderizado visual de
  las piezas, clic interactivo con acción (nota) y **bloqueo físico del jugador**
  — el panel flotante sobre el spawn bloqueaba el paso y el modo `solid` detiene
  al jugador (SCENERY01–04 y SCENERY07 observados).
- PENDIENTE NATIVO: bloqueo de NPC/AI (SCENERY08), persistencia guardar/cargar y
  reentrada (SCENERY05–06), ocultar/restaurar (SCENERY09), convivencia con
  enemigos/cámaras (SCENERY10) y comportamiento en red.

## Límites deliberados

- Sólo `shape: box` (paredes, paneles, plataformas, columnas, cajas, barreras).
  El subconjunto de seis planos de `Scene.encode` se conserva: no se emiten
  cascos convexos arbitrarios.
- Una pieza = una entidad. Sin CSG, sin sector/portal nuevo, sin lightmaps.
- La geometría paramétrica se guarda como `size`+`material`+`mode`, no como
  triángulos opacos; el brush se deriva en compilación.
- `mode: decor` nunca declara colisión. `solid`/`barrier` usan plantillas
  originales con `collide=3`, pero la colisión física queda EXPERIMENTAL hasta
  SCENERY07/08.

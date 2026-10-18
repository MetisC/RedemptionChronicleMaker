# Modelo de escena y perfiles de entorno

`level.source` selecciona la geometría original. `level.environment_scene` selecciona un NSD original **asociado a ese level** como perfil de entorno. Es opcional, admite nombres sin distinguir mayúsculas y no admite rutas libres ni una escena de otro level.

```yaml
level:
  source: EastLondon
  name: 'Londres: el regreso'
  environment_scene: EAST_28_1.nsd
```

Sin esa propiedad se conserva la selección automática histórica: primera escena asociada con un anchor estudiado. Los perfiles adicionales incluyen la estática de nombre común con el NIL. La GUI los ofrece en **Level base → Propiedades → Entorno original**. Se guarda en el mismo YAML de la escena, admite deshacer/rehacer y se elimina al elegir otra geometría para evitar referencias cruzadas. Un `level.sky` previo sigue siendo un override explícito sobre los dos campos finales del perfil.

El catálogo se deriva automáticamente en `scan`; el editor lo obtiene también de los catálogos existentes y copias originales, sin exigir un archivo de cache nuevo en workspaces antiguos. `cache/scene_profiles.json` es la salida legible de la investigación, no la fuente de verdad de los builds. Un archivo ausente, una versión NSD desconocida o un hash distinto bloquean validación/build; no se reemplaza silenciosamente por un entorno vacío.

El generador conserva los 176 bytes finales del NSD versión 8 y escribe los contadores globales propios, incluidas entradas nativas cuando se solicitan. El NSD contiene el controlador y las interacciones de brush propias; las entidades adicionales se crean desde Java. El anchor se conserva independientemente del perfil elegido. En el informe de build constan ruta/hash del NSD, hash del bloque, modelo/animación de cielo y existencia de override. El fingerprint incluye los NSD de entorno utilizados para detectar cambios entre build y deploy.

## Evidencia y límites del formato

El lector original del ejecutable original Vampire.exe, direcciones `0x4a81c7..0x4a82e5`, lee este tramo final en orden:

| Offset relativo al tail | Bytes | Confirmación |
|---|---:|---|
| 0 | 32 | Primer campo de cadena |
| 32 | 32 | Segundo campo de cadena |
| 64, 68, 72, 76, 80 | 4 cada uno | Cinco campos escalares |
| 84 | 12 | Bloque de tres componentes |
| 96, 100, 104, 108 | 4 cada uno | Cuatro campos escalares |
| 112 | 32 | Modelo de cielo, carga de NOD |
| 144 | 32 | Animación del cielo, carga de NAD |

La estructura de lectura y los dos campos de cielo están confirmados en el ejecutable original. El manual documenta opciones de música/ambient/EAX/fog/ZClip, pero **no confirma por sí solo qué offset binario corresponde a cada una**. Los 112 bytes iniciales se conservan opacos. No se escriben floats supuestamente de niebla ni volúmenes por conjetura.

NIL conserva luz global, iluminación ambiente, sectores, superficies y lightmaps. Por eso un perfil NSD no convierte una geometría nocturna en diurna con iluminación rehecha. Tampoco crea una superficie Sky si no existe. EastLondon conserva su fondo gris original; no se vuelven a añadir los cielos experimentales retirados.

NSL es una lista de autoría de Embrace y no la consume el juego. NSS es la selección de escenas del Narrador y requiere lógica `advance` en Java; no enlaza automáticamente ubicaciones con NSD. NSD es contenido runtime. Nuestra escena de campaña reúne geometría referenciada, entorno, entidades, eventos y narrativa; una secuencia de cámara sólo cambia el plano durante su ejecución.

El writer NSD admite entidades simples, overlays de brush propios y entradas nativas acotadas; no es un escritor universal. La reutilización del tail de un original complejo no supone que se pueda leer/escribir toda esa escena. Las entradas propias cubren playerstarts; la puesta en escena de conversación usa esas entradas mediante la API. Los bloques completos de convstarts, lightboxes, soundboxes y parámetros originales no tienen codec general; se usan abstracciones runtime cuando su intención está contrastada. La escena estática original puede aportar objetos base al motor. La acción optativa `control_original` identifica props de esa escena para ocultar/restaurar/retirar o mover puertas con frames; no hay borrado universal de geometría fija. Véase EDITOR_GUIDE.md y ORG01–06 en MANUAL_RUNTIME_CHECKLIST.md.

## Coreografía optativa sobre la escena

Los travellings propios recuerdan escena/level de creación y avisan si se usan en otro contexto. Un cue o una línea aporta CUÁNDO; las Actions existentes/nuevas aportan QUÉ. No hay otra escena geométrica ni sistema paralelo de eventos. Las entradas nombradas también sirven como puesta en escena antes del diálogo. Sonido en bucle se vincula a waypoint; luz dinámica a entidad propia; clima se cambia mediante nombres demostrados en scripts. Estas funciones requieren aceptación nativa independiente y no reinterpretan bytes opacos del entorno.

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

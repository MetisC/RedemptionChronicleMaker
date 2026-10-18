# Formatos: lectura, escritura y límites

## Fuente actual

`schema:2`, `project_format:9` habilita entries/waypoints/paths y acciones nuevas. Formato5 y schema1 conservan compatibilidad de generación. `prepare` introduce un perfil interno phase9; el editor guarda autoría, no geometría ni Java generado.

```yaml
entries:
  - id: safe
    name: Llegada segura
    transform: {position: [1016, -210, 0], orientation: [0, 0, 90]}
default_entry: safe
waypoints:
  - id: p0
    name: Inicio
    transform: {position: [850, -210, 0], orientation: [0, 0, 0]}
  - id: p1
    name: Regreso
    transform: {position: [850, -320, 0], orientation: [0, 0, 0]}
paths:
  - id: walk
    name: Paseo
    actor: guide
    points: [p0, p1]
    loop: true
    tolerance: 24
    speed: 90
```

Fragmento de escena: orientation es pitch/roll/yaw; marcadores absolutos. Validación de finitud, referencias,2..128 puntos y un recorrido por actor. Acciones `travel: {scene: archive, entry: safe}`, `start_patrol: walk`, `stop_patrol: guide`; exits por Cast ID; control_door diferencia frames/pivot. play_sound referencia WAV único y waypoint con volumen/radios. La GUI ofrece estos campos; identificar Cast IDs sigue siendo técnico si no existe catálogo fiable.

Chronicle Flags reservados para arrival, progreso once y checkpoint por acción, sin solapar los0..255 del autor. El límite nativo1024 se valida. Arrays de patrol cambian la firma de save; no se migran saves entre builds. NCP: 8+104*n en174 originales; lector sin pérdidas y escritor lineal propio contrastado con evaluador nativo, descrito al final de este documento. Se generan directamente NOT/NSD/NCO/NVO/NLS/NSC/NMF/NQD/WAV/NOB y Java45.3; no se escribe NIL.

classfile_limits lee constant pool y atributos Code reales, informa mayor método/pool. Header45.3 obligatorio, Code<=65535, pool<=65534. ECJ puede rechazar métodos enormes antes del readback; no hay partición automática general de un evento gigante.

Referencia reproducible: `research/binary_headers.json`, `research/not_roundtrips.json`, `research/template_tag_evidence.json` y `research/original/`. Los lectores/escritores runtime están en `src/rcm/formats.py`; lectores espaciales en `src/rcm/spatial/geometry.py` y `assets.py`. Las atribuciones de comportamiento se separan en `ENGINE_NOTES.md`.

## Contenedores NOB

Los seis NOB instalados tienen cabecera ZIP `50 4B 03 04` y directorio central estándar. La extracción utiliza ZIP directamente. Se conservan ruta de origen, tamaño y CRC32; los recursos técnicos extraídos también reciben SHA-256. Se rechazan rutas absolutas, `..` y separadores con drive.

El escritor genera ZIP STORED con timestamps fijos y orden estable, extensión `.nob`. La distribución incluye NOB en la raíz y clases sueltas en codex/. El selector descubre crónicas a través del índice NOB registrado bajo -user; los detalles están en USER_DIRECTORY.md.

## Formatos de texto

Los originales examinados usan líneas de tokens, comentarios y cadenas de resto de línea. Se genera Windows-1252 con CRLF. El YAML fuente es UTF-8; el validador rechaza texto no representable en Windows-1252, saltos de línea en campos de texto y delimitadores de comentarios.

| Formato | Evidencia estructural | Soporte actual |
|---|---|---|
| `.nsc` | `location ID NIL NSD/null NUI MAPLABEL FLAGS`, `exit A,index B,index [flags]`, ajustes | Lector de ubicaciones/settings/exits; escritor de campañas con varias ubicaciones |
| `.nmf` | `NLS`, `NVO`, `PLAYER`, `SPEAKER`, `CASH`, `NTX`, `NST`, `NSS` | Lee filas para seleccionar NLS/CASH; escribe metadatos propios |
| `.nss` | `Scene locationNumber sequenceIndex sceneName` | Lee asociaciones adicionales; no escribe secuencias |
| `.nco` | Conversation/Event/Line/AnswerReturn/AnswerGoto/Delay/Jump | Genera eventos/nodos, varias líneas, ANSWERGOTO y ANSWERRETURN; conserva el caso simple |
| `.nvo` | `lineID voiceResource text...` | Genera textos de todas las líneas/respuestas con voz silenciosa propia |
| `.nls` | `stringID text...` | Genera tabla propia `_R_<id>.nls`: nombre de crónica, actores y etiquetas corta/larga del NSD |
| `.npc` | Stats min/max/current, cash, experiencia, disciplinas e inventario | Copia e inventaría; no genera personajes jugadores |
| `.nai` | Attack/move/AI flags, distancias, wander y disciplinas | Genera perfiles propios a partir de una base, con propiedades editables acotadas |
| `.nqd` | `QUEST flags flags shortID longID icon reward`, otras filas según recurso | Genera entradas propias de journal; progreso y recompensa mediante Java, sin codec universal de quests |
| `.nbs` | `D template copies` o `R treasureClass copies`; 0 = infinito según comentarios originales | Copia e inventaría; no genera tiendas |

Las filas `.nss` se asocian por índice de la ubicación en NSC; esa correspondencia sigue siendo una inferencia. Las referencias estáticas NSC tienen archivo y línea explícitos. El catálogo de escenas incluye ambos tipos; no convierte una asociación NSS en prueba de carga.

## NOT: estructura reconstruida

Cuatro archivos examinados, versión DWORD 1. Todos los enteros de esta sección son little endian. Offsets contados desde el comienzo del archivo.

| Offset/tamaño | Contenido observado |
|---|---|
| 0 / 4 | `NOT\x10` |
| 4 / 4 | Versión, 1 en los cuatro originales |
| 8 / 4 | Número de entradas del índice |
| 12 / N × 36 | Índice: nombre de 32 bytes, seguido de offset absoluto uint32 |
| Offset de entrada / 4 | Número de tags |
| A continuación / tags × 36 | Identificador uint32 + payload de 32 bytes por tag |
| A continuación / 4 | Tamaño de comentario, incluyendo su NUL |
| A continuación / tamaño | Comentario con NUL final |

Los registros indexados son contiguos en esta instalación. `NotFile.read` valida cabecera, límites, offsets y terminadores. No interpreta ni normaliza payloads desconocidos. Conserva incluso los bytes posteriores al NUL del nombre, ya que los originales contienen datos residuales.

Se han verificado estas reproducciones exactas:

| Archivo | Entradas indexadas | Bytes adicionales no indexados | Roundtrip |
|---|---:|---:|---|
| `Global.not` | 915 | 0 | Idéntico |
| `darkAges.not` | 726 | 0 | Idéntico |
| `modernDay.not` | 776 | 0 | Idéntico |
| `Multiplayer.not` | 202 | 6.786 | Idéntico, conserva cola opaca |

La cola de Multiplayer contiene bytes que parecen registros adicionales, pero no se conocen sus condiciones de carga. No se añaden al catálogo ni se descartan. Los 2.619 registros indexados incluyen dos nombres repetidos entre archivos; el generador rechaza una referencia de plantilla ambigua.

Los tags usan varios tipos de payload: string C de hasta 31 bytes, uint32, float32 o vector de tres floats. El ancho de 32 bytes no implica que todo el payload sea significativo. Los nombres de 120 propiedades iniciales se extraen de cadenas ordenadas de `Vampire.exe`; su vinculación con IDs numéricos se contrasta con los valores de plantillas originales. No hay un header SDK para certificar toda la enumeración.

| Tag usado | Interpretación respaldada por comparación |
|---:|---|
| 0 | Based on / plantilla padre |
| 1 | Orientation: pitch, roll, yaw |
| 2 | Position: x, y, z |
| 3 | Sector |
| 4 | Modelo |
| 6 | Foley |
| 9 | Motion set |
| 11 | Clase script |
| 16 | Tipo de thing |
| 56 | AI |
| 81 | Cast ID |
| 82 | Description ID |
| 114 | Actor flags |

El escritor del prototipo crea una plantilla nueva con padre original y tags 11, 81 y 82 propios. No modifica `modernDay.not`, no duplica modelos y no requiere NOT Editor. El tutorial aceptado usa wrappers propios; campos de herencia o plantillas nuevas distintos de los probados requieren su verificación nativa específica.

## NSD: subconjunto reconstruido

Todos los 291 NSD examinados comienzan por `NSD\x10`, versión DWORD 8. El subconjunto aceptado por el codec tiene:

| Offset/tamaño | Contenido |
|---|---|
| 0 / 4 | Magic `NSD\x10` |
| 4 / 4 | Versión 8 |
| 8 / 32 | Primer identificador; normalmente termina en S |
| 40 / 32 | Segundo identificador; normalmente termina en L |
| 72 / 8 | Campos no interpretados, preservados al leer |
| 80 / 4 | Número de entidades |
| 84 / variable | Registros de entidades |
| Final / 192 por defecto | Cuatro contadores globales (16), tablas propias opcionales de entradas/conversación, y metadatos de entorno (176) |

Una entidad simple tiene `uint32 tagCount`, `tagCount × (uint32 tagID + payload32)` y **20 bytes de bloques variables vacíos**. Los primeros DWORD son cuenta de frames y parámetros; siguen presencia de brush, región e iluminación. Se admiten frames24 (orientación/posición), parámetros tipados y brushes generados; regiones/luces complejas siguen fuera del subconjunto.

64 de los 291 NSD originales se leen y reemiten exactamente (research/embrace_strict_parity/nsd_extended_roundtrips.json). Los28 del baseline anterior se comprueban por separado, sin cambiar sus hashes. El codec rechaza `EAST_28_4.nsd` y otras escenas complejas, en vez de reinterpretarlas incorrectamente.

La escena mínima de referencia tiene **480 bytes**, una única entidad `ghost` con tags 0, 1, 2, 3 y 11. Los parámetros/bloques variables quedan vacíos. El script propio se indica en el tag 11; no se escribe en el encabezado NSD.

El anchor del ghost se toma automáticamente de una entidad existente en una escena relacionada con el level. Para EastLondon son posición `[1184,1660,114]` y sector 19. Se conservan los últimos **176** bytes de metadatos y se anteponen los cuatro contadores globales, vacíos por defecto; las tablas propias optativas de entradas y conversación se escriben explícitamente con sus contadores. Copiar 192 bytes de una escena compleja podría arrastrar el final de un registro de entrada. No se copian sus actores, triggers, scripts o geometría de entidades.

El lector nativo NSD v8 lee al final dos nombres de 32 bytes para modelo y animación del cielo, offsets -64 y -32. Los recursos se resuelven desde el juego. Se conserva el entorno original completo; EastLondon mantiene ambos nombres vacíos y el fondo gris aceptado. Los campos de audio, volumen, niebla y ZClip están contrastados en la activación nativa; SCENE_MODEL.md da sus offsets. Los DWORD64 y108 se conservan opacos; EAX se hereda por prioridad estática.

`scene_entity_hints` busca secuencias de tags 0/1/2/3 en escenas complejas. Conserva offsets y marca `confidence: tag-pattern; not full scene parse`. Puede perder entidades o producir coincidencias; no sirve para editar/reemitir escenas complejas. El punto usado para Victoria se contrastó manualmente con el registro `otto`.

## NIL, modelos y geometría

Los 112 NIL tienen `NIL\x10` y DWORD siguiente 27. EastLondon contiene materiales, muchos datos numéricos y geometría; no se encontró en él una cadena de plantilla `businessWoman`, `Pedestrian`, `ghost` o `trigger_region`. Esa observación no demuestra que todo NIL esté libre de metadatos o entidades.

No existe escritor NIL ni modificación/copia de NIL en los paquetes. `Levels.nob` permanece externo como recurso original. El archivo `research/original/l1_east.nil` es una copia local de investigación, no un output de la crónica.

`.nod` y `.nad` son binarios: **no llevan necesariamente magic ASCII NOD/NAD**. Los ejemplos `.nod` comienzan por DWORD 7 seguido de valores variables; los `.nad` por DWORD 3 seguido de valores variables. Esos primeros valores no se denominan formalmente versión sin más evidencia. Se inventarían modelos, animaciones y recursos asociados, pero no se generan ni se editan mallas.

El lector resuelve las superficies/sectores NIL, la malla estática NOD y texturas NAM/TGA; siguen pendientes NIL global, NSD complejo, todos los tags NOT, cola no indexada, NAD, materiales avanzados, semántica temporal de NCP estacionarios y otros auxiliares. Que sean binarios no obliga a usar herramientas antiguas: se ampliarán nuestros codecs cuando una función concreta lo requiera.

## Java, WAV y reproducibilidad

ECJ 3.26.0 se ejecuta con `-1.3 -proc:none`, bootclasspath `cache/toolchain/classes.zip` y classpath de clases originales extraídas. El resultado se comprueba byte a byte en su cabecera: `CA FE BA BE 00 03 00 2D` = 45.3. No se rebajan clases Java modernas parcheando su número de versión.

El WAV propio es PCM mono, 16 bits, 22.050 Hz, cuatro segundos de silencio. La duración/visibilidad de subtítulos no se considera validada por el hecho de que el WAV sea correcto.

Los NOB/ZIP usan orden y timestamps constantes. `build_report.json` contiene hash y tamaño de cada archivo entregado; `--no-compile` produce un estado distinto y no publica un ZIP de distribución con clases antiguas. Los artefactos finales de un build anterior se retiran al iniciar una nueva construcción para evitar presentarlos como resultado de una compilación fallida.

## Conversaciones y textos fuente

El editor guarda UTF-8 en YAML; schema 1 se conserva por compatibilidad y las campañas actuales usan schema 2. El contenedor de intercambio .rcmproject incluye fuentes y recursos propios. Descripción/comentarios internos pueden tener varios párrafos y Unicode. Los textos exportados al motor siguen Windows-1252 y un solo parlamento por línea, sin delimitadores de comentarios; el editor permite añadir varias líneas a un nodo.

- Conversación simple: prompt/choices; permanece compatible.
- Conversación por nodos: speaker/entry/nodes con líneas y respuestas. No se mezclan las dos formas.
- GOTO genera `ANSWERGOTO: <claveNVO> ev_<node>`; RETURN genera `ANSWERRETURN: <claveNVO> <valor>`.
- La entrada se emite primero. Los IDs de texto derivan de la posición declarada del nodo y de su línea/respuesta, con límite conservador de 31 bytes. Los IDs de nodo se traducen en `ev_<id>`; no se confunden con callbacks Java.
- Los RETURN deben ser enteros positivos únicos dentro de la conversación. Las acciones de flags solo se asocian a respuestas RETURN; los eventos Java reciben ese resultado al terminar.
- Eventos/condiciones se traducen a Java, sin crear otro formato antiguo ni un bloque geométrico de trigger. Scene Start, Actor Clicked y Conversation Ended utilizan callbacks existentes.

El título de entrada corrige las claves del encabezado NSD mediante el NLS propio. `<prefix>S` y `<prefix>L` reciben `level.name`, o el nombre de crónica si falta. No se reescribe una tabla global original. La aceptación del tutorial no acredita todos los títulos de nuevas crónicas.

## Conservación y límites

La capa generada conserva la geometría referenciada y el entorno original. No se añade cielo experimental. Las plantillas hijas aportan identidad y script propios; los campos desconocidos se conservan.

No se ha resuelto completamente NIL global, NSD variable, todos los tags NOT, cola no indexada, NAD/skinning, materiales multipass, paths de cámara y auxiliares. Catálogo no significa escritor ni capacidad probada de instanciación. No se generan AI, quests, tiendas, inventarios o geometría por el mero hecho de haber inventariado sus archivos.

Los archivos `.autosave` son copias del mismo YAML; no se incluyen en la distribución. Las fuentes Java, modelo JSON e informes son material de build/diagnóstico, no otra fuente de autoría. Un ZIP final contiene solo el NOB y las clases, manteniendo una carpeta compacta por crónica.

## Lector NIL v27

Lectura de geometría, sin escritor. Little endian; NUL en nombres de 32 bytes. Evidencia: ejecutable original y 112 archivos, no una especificación SDK. Reader rechaza truncamientos, conteos/índices no válidos y coordenadas/UV no finitas.

| Orden | Estructura consumida |
|---|---|
| Cabecera | `NIL` + byte 0x10, uint32 27; 72 bytes opacos; 12 bytes de dimensiones |
| Materiales | uint32 cantidad, cantidad × nombre32 |
| Sectores | uint32 cantidad; registros siguientes por sector |
| Sector | 16 bytes (flags/centro); uint8 cantidad ×16; uint16 cantidad ×16; uint16 cantidad ×8 |
| Posiciones | uint16 cantidad, XYZ float32 ×12 |
| Corners | uint16 cantidad, registros ×24 |
| Superficies/grupos | uint32 número superficies; uint16 número grupos |
| Grupo | `<HiBIH>`: superficies uint16, material int32, capas uint8, flags uint32, corners uint16; capas ×6 bytes |
| Superficie | `<HBi>`: índice plano uint16, corners uint8, índice lightmap int32 |
| Portales | uint8 cantidad ×96 bytes, sin interpretar visibilidad |
| Cola por sector | uint16 cantidad ×72 bytes, conservada como salto de lectura |

Corner: índice XYZ uint16 en offset 0; UV difuso float32[2] en 8; UV lightmap en 16, no utilizado. Bytes intermedios no se usan como color/normal sin interpretación completa. Corners siguen el orden de superficies de cada grupo; su suma y la suma de superficies deben coincidir. Cada polígono se triangula en abanico: presupone convexidad original, todavía inferida.

La cola global posterior no se lee: BSP, lightmaps completos, salidas y otros bloques quedan pendientes. `source_end` registra el límite, no el tamaño total consumido. EastLondon: 3.096.883/5.586.623 bytes, 131 sectores, 45.927 triángulos y 109 materiales. Bounds XYZ [-5120,-4608,-80] a [4288,5824,1952]. 112 NIL pasan el lector; no significa que se haya validado visualmente cada mapa.

## Lector NOD v7

Little endian sin magic ASCII obligatorio. Lectura de malla de referencia; no escritor ni animación. Se contrastan las rutinas nativas y 1.476 NOD, todos con lectura completa y conteos válidos.

| Orden | Estructura |
|---|---|
| Inicio | uint32 versión 7, uint32 materiales, nombres32 |
| Conteos | `<HHIIHI>`: bones, nombres de shape, vértices, triángulos, grupos, flags |
| Bounds | 24 bytes |
| Bones | ×66: posición12, matriz48, jerarquía6; sin skinning |
| Shapes | nombres32 |
| Vértices | ×40: XYZ en 0, normal en 12, UV en 24; resto no usado |
| LOD | Si flags &1, uint16 por vértice |
| Triángulos | índices locales uint16[3], ×6 bytes |
| Grupos | ×28; material int32 en 0, triángulos uint16 en 16, vértices uint16 en 18 |

Cada grupo acumula su rango de vértices; los índices locales deben caber dentro de él. Se validan sumas y consumo hasta EOF. Vista de bind pose; no se aplican NAD, pesos ni transforms animados. Un modelo cargado no prueba que su plantilla pueda instanciarse sin otras dependencias.

## NAM/TGA y cache

NAM: texto Windows-1252 con `texture` y otras propiedades. Resolución relativa al directorio NAM. `pass 0` ofrece la primera textura de agua multipass. Material simple de NOD puede resolver TGA en `3d/Materials`; búsqueda NAM por basename solo cuando es inequívoca. TGA se decodifica mediante Pillow a RGBA. No se generan recursos originales nuevos de este tipo.

Cache NPZ sin pickle: vértices XYZUV float32 expandidos, material por triángulo, nombres, sectores y límite source_end. Clave SHA-256 del NIL + versión del codec. PNG con SHA de TGA guarda RGBA; JSON por level contiene resolución y warnings. Derivados regenerables, nunca parte de la crónica ni del paquete runtime.

## Triggers espaciales

Schema 1 sigue admitiendo fuentes anteriores. Se añade opcionalmente `triggers`; eventos `trigger_enter` referencian su ID. Posición representa centro del volumen, tamaño dimensiones completas y orientación conserva `[pitch,roll,yaw]`. Cajas solo admiten yaw; esfera orientación cero. La escala de actor/objeto no se exporta.

```yaml
triggers:
  - id: warehouse_entry
    name: Entrada
    shape: box
    transform:
      position: [128, 64, 50]
      orientation: [0, 0, 45]
    size: [160, 120, 100]
    once: true
  - id: courtyard
    name: Patio
    shape: sphere
    transform:
      position: [500, 0, 80]
      orientation: [0, 0, 0]
    radius: 80
    once: false

events:
  - id: ambush
    when: trigger_enter
    trigger: warehouse_entry
    conditions:
      - flag: alliance
        is_set: true
    actions:
      - spawn: guard
      - set_flag: entered
```

Fragmento, no proyecto completo: requiere actor guard, flags y demás campos. `size` y `radius` son exclusivos, positivos y finitos. No se permiten IDs/referencias inexistentes, transforms relativos de triggers ni spawn duplicado de una entidad entre inicio y trigger.

Volúmenes se traducen a Java, sin codec de región antigua ni cambios al NIL. Intervalo 0,15 s, servidor, entrada agregada de jugadores locales y condiciones AND. Guards/estado se prueban con doubles y compilan contra API original; ejecución nativa aún pendiente. Los contratos actuales se comprueban en tests/test_spatial.py y los harness Java.

## Campañas y journal

Se generan directamente NSC con varias ubicaciones, NMF compuesto y NQD de journal nativo, además de los codecs anteriores. El NQD usa exclusivamente la fila QUEST observada; se genera una entrada por paso. Se conserva geometry_in_package=false y el entorno original de cada escena. Schema 2 está descrito en ARCHITECTURE.md. Los NSD siguen siendo capas mínimas, no importación de las entidades originales.

Inspector NOT nuevo muestra offsets/tags/hex sin forzar un writer completo; NOT_FORMAT.md separa lo conocido de la cola opaca. Los formatos no comprendidos siguen sin escritor.
## Entorno y contenedores de proyecto

El modelo incluye `level.environment_scene`, validado como referencia NSD original asociada al level. No introduce otro formato binario: reutiliza el tail de 176 bytes NSD v8 y mantiene cuatro contadores globales vacíos. [SCENE_MODEL.md](SCENE_MODEL.md) detalla offsets confirmados y bytes opacos. Se corrige la interpretación NSS: la última columna es una clave NLS para el Narrador, no un nombre NSD. NSL no es necesario en el pipeline runtime. Los demás límites de codecs siguen vigentes.

La validación posterior al build relee NOT/NSD y comprueba referencias NSC/NMF/NCO/NLS/NVO/NQD, hashes y versión de clase 45.3. Conserva campos NOT desconocidos en round-trip. Estas comprobaciones no acreditan ejecución nativa ni comprensión completa de todos los comandos originales. La geometría NIL/NOD no se reescribe.

Los contenedores nuevos `.rcmproject` y `.rcmpack` son ZIP con manifest JSON, hashes SHA-256, metadatos y dependencias por versión. El primero contiene YAML/fuentes propias; el segundo NOB/clases compiladas. Rutas inseguras, duplicados por mayúsculas, geometría y formatos ejecutables ajenos se rechazan. Especificación operativa: [PACKAGES.md](PACKAGES.md).



## Cámaras e inventario en formato 9

Conversaciones admiten camera: native (no cámara propia) o un preset de camera_presets.PRESETS. Desde 0.9.9, si falta camera se usa ots_speaker_close; native es una elección explícita experimental. Secuencias admiten steps: lista ordenada de {at, actor, preset, angle?, transition?}; primer plano en 0, tiempos crecientes dentro de duration, actores/presets válidos y valores finitos. move_path referencia un recorrido local existente. camera_path referencia un NCP original o propio único; es excluyente con steps. path_speed: 0.01..100, tasa nativa, no segundos. Los NCP propios lineales se generan desde resources.camera_paths.

La timeline usa timer nativo de 150 ms; los tiempos se cuantizan a ticks. Desde 0.9.11, captura/restauración guarda una marca de película activa y el índice del actor movido por una cutscene, además de los records de patrol; restore cancela la película y detiene ese recorrido. service.py incluye cinema_record_v2 por escena en la firma del contrato de saves. Sin migración nativa entre contratos.

El inventario gráfico crea IDs distintos, cada uno con su plantilla de entidad generada, aunque hereden del mismo template original. Propiedad de creación única; props, objetos con spawn y objetos de otro inventario no se ofrecen como reutilizables.


## Journal en runtime formato 9

Se generan NQD y textos NLS directamente. start_quest carga sólo qNs0, advance_quest completa qNsI y carga qNs(I+1), complete_quest confirma flags/pasos y concede recompensa sin cargar el NQD padre. Las entradas completadas permanecen como historial. La ficha padre sigue generada por compatibilidad del paquete, pero no se carga en el journal de formato 9; por tanto no revela el recorrido completo al iniciar. Formatos históricos mantienen el flujo anterior. Esta es una política de nuestro runtime sobre entradas originales, no una gramática inventada de objetivos internos de NQD.


## Decorado móvil y llave física

En una timeline, cada plano puede indicar focus: ID de un objeto local; actor sigue siendo el interlocutor/segundo foco. prop_motion contiene object, at, duration y translation [x,y,z]. Requiere un objeto absoluto, tiempos finitos dentro de la película y traslación finita acotada. Se interpola el transform con SetPosition; no se genera geometría ni se inventan frames NSD. move_at retrasa el inicio de move_path hasta el instante indicado. Estos campos se editan desde Cámaras y participan en referencias, renombrado y protección de borrado.

NOT tag 20 se expone como item_type uint32. Las plantillas de misión originales usan 7; la inserción nativa lo consume sin dejarlo en la cuadrícula. La variante propia T_tutor_key hereda BoneKey y escribe 0 para que se conserve físicamente. Icono/modelo/otros campos se heredan sin reescribir los originales. El runtime moderno verifica inventario tras AddToActorInventory antes de considerar entregado el objeto. El soporte de inventario se verifica mediante los tests y las referencias del motor.

## Motion por nodo/línea y pose guardada

Sólo formato 9: `nodes[].motion` elige un slot del NMS real del speaker; `nodes[].lines[].motion` lo sustituye para esa línea. Ausencia conserva la herencia; ausencia en ambos usa la actuación del motor. La validación comprueba el slot en cada actor afectado. El callback usa el orden EVENT serializado (entrada primero) y LINE, con el quinto argumento como GUID del hablante. NCO/NVO mantienen su formato; el override se genera en Java con PlayMotionSetMode.

`cache/motions.json` v2 contiene constantes de Codex, NMS encontrados con procedencia, slots/NAD/flags y herencia de templates; su huella incluye Codex.class y catálogo de recursos. Una caché JSON corrupta se reconstruye. No hay editor NMS/NAD propio en esta revisión.

### NTX propio y final de animación

`show_note` genera `strings/R_<id>.ntx` y su referencia `NTX` en NMF. Gramática original contrastada con MP_CTD: `<TEXT id none 0>`, `<TITLE título>`, `<P 0xFFFFFFFF>`, texto, `</TEXT>`. Writer y reader propios del subconjunto sin voz, con validación de marcado, párrafos, IDs y codificación Windows-1252. No se usa NLS para sustituir las ventanas de texto. `object_clicked` admite un filtro `object`; `note_closed` recibe la continuación diferida de `textended(owner)`.

La documentación original confirma que el booleano de PlayMotionSetMode elige canal; el retorno es duración en msec. Los overrides explícitos tienen ahora stand en el canal base y recuperación tras el retorno temporal, cancelada al entrar en otra línea. No cambian NCO/NVO ni la actuación automática sin overrides. Ver ENGINE_NOTES.md.

El record `player_pose_record_v1` consta de SaveBoolean y seis SaveFloat: XYZ y orientación. Se escribe antes de los records de patrol/entidades. En escenas con cinematics, preceden SaveBoolean(cinema activo) y SaveInt(actor), contrato cinema_record_v2. El motor conserva flags por sus APIs originales. Esto es un contrato de serialización de nuestro script, no un escritor NSG/NSW completo. Nuevos records requieren partida nueva.

### Formato de proyecto 10 · encuentros dinámicos

scene.generators añade modo, waves/groups, rol/template/cantidad, waypoints, límites, intervalos, políticas, boss/phases y acciones normales. YAML sin aliases, compatible con loader seguro. Formato 9 se abre sin mutación; primer generador crea backup y conversión optativa con undo.

Se siguen generando NSC/NMF/NSD/NOT/NLS/NCO/NVO/NQD/NTX y Java/classes según contenido. NIL se referencia sin editar. dynamic_records_v1 añade SaveInt(1), estado/oleada/espera/cursors/batch/puntos/retries/counters, booleanos de seguridad/oleada/boss y float HP anterior; después slots GUID/entrada, counts por entrada/rol y done/pending por fase. Restore lee el mismo orden y rechaza propiedad/cursors inválidos. La firma incluye configuración dinámica: cambios estructurales requieren nueva partida. No es un writer completo del save nativo.

### Objetos originales · acción optativa en formatos 9/10

`control_original` contiene `level`, `template`, `position` XYZ y/o `cast_id`, y `operation`: `hide`, `restore`, `remove`, `frame` o `pivot`. El selector obtiene la identidad del NSD estático catalogado; no copia ni reescribe su bloque. Para movimiento requiere `frame` 0..255 y `parameter` positivo; `open` controla el signo de duración del pivote. La pertenencia al level y la plantilla original de tipo prop se validan antes de generar.

La generación añade Java y siete Chronicle Flags internos por identidad, deduplicados entre acciones. Conserva los bits originales de render, colisión, bloqueo visual y bloqueo de cámara, más estado oculto/retirado. Al restaurar sólo repone esos bits; al cargar/reentrar reaplica la visibilidad o retirada. No añade campos a los records Save/Restore. El movimiento de frames se delega al motor; su persistencia visual no está certificada. Sin acciones `control_original` no se inyecta este runtime.

### Importación local WTD

`content_packs/within_the_darkness/import.json` registra hashes de fuente/paquete, catálogo resuelto y geometría/NSD de Penthouse. `rcm_wtd_content.nob` contiene sólo la selección local: política de nombres suministrada por el usuario, excepción expresa NIL/NSD de Penthouse y NLS propio de su label. NCD/NDD/NDG se regeneran desde filas verificadas conservando las definiciones originales; sólo se añaden nombres sin colisión con Java/dependencias presentes. Se comprueba que cada implementación de disciplina hereda realmente de `Discipline` leyendo su classfile, sin ejecutarlo. NOT nuevas contienen únicamente registros seleccionados y herencia resuelta; no copian las colas no referenciadas del archivo fuente. Los NMS que colisionaban con originales se renombran y sólo las plantillas importadas apuntan a ellos.

En formato 9/10, `actors[].traits` admite `clan` por nombre NCD y `disciplines` como mapa nombre NDD → nivel 0..5. Usa SetActorClan y SetActorDisciplineLevel al crear un actor nuevo; no reinicializa un actor restaurado. Las acciones `set_actor_clan: {actor: Player, clan: salubri}` y `set_discipline: {actor: Player, discipline: Panacea, level: 1}` admiten Player o ID local. Requieren una importación válida, con validación y navegación de referencias normal.

`build_inputs_sha256` y contrato de saves incluyen la dependencia importada. El informe `imported_content` conserva ID/hash, sin meter el paquete en el ZIP de distribución; Deploy comprueba el hash y lo copia sólo a RCM. La compatibilidad de inventarios conserva el paquete completo cuando una plantilla de perfil lo necesita, evitando duplicar sus definiciones en `rcm_compat`. Sin importación/traits/acciones nuevas, el Java aceptado se genera idéntico.

Las AI importadas también se filtran por sus instrucciones `discipline`: cada nombre debe existir en la tabla NDD efectiva y cada nivel estar entre 0 y 5. Se excluyen las AI no resolubles y, por dependencia, sus plantillas; no se sustituyen por comportamientos inventados.

## Previsualización de objetos incrustados y selección 3D

`spatial/scene_mesh.py` reconoce de forma acotada un cuerpo de brush NSD: materiales de 32 bytes, vértices de 40 bytes, índices uint16 y grupos de 28 bytes. Exige cuentas/índices coherentes, floats finitos y bounds finales coincidentes. La búsqueda termina en el siguiente registro de entidad; no cruza hacia la malla de otro objeto. No es un lector completo del NSD variable ni un writer. Tenebrae: cuerpo en offset 6800, 78 vértices y 48 triángulos, material `London\CTdoor_L`, entidad `tracker_thing` en offset 6560.

Las previsualizaciones originales se transforman con yaw/pitch/roll y se seleccionan por triángulos, con oclusión NIL. La selección no cambia el YAML. Para superficies NIL, el asistente genera interacción nativa por clic con acciones normales; nunca `control_original` sobre caras fijas. Evidencia en `research/runtime_test/original_selection/tenebrae_evidence.json`.

## Interacciones nativas por clic

En formato 9/10, un objeto `tracker_thing` puede llevar `interaction: {materials, vertices, material_ids, sector}`. Los vértices expandidos contienen XYZUV locales (cinco floats), tres por triángulo; los IDs enlazan materiales de 32 bytes. Límites: 2048 triángulos, 64 materiales, coordenadas finitas y transform absoluto. El nombre del objeto genera el NLS del tag 82; Cast ID y script pasivo permiten `CaptureThing` en el controlador de escena. Son props cargados por nuestro NSD; no se simula un clic con un trigger ni se intenta recrearlos sin brush mediante CreateThing.

El codec NSD ahora acepta además el subconjunto propio: frames=0, parámetros=0, brush=1, cuerpo material/vértices/índices/grupos/bounds, seis planos axiales válidos, sectores de región=0, datos de luz=0. Cuentas y datos deben coincidir al releer. El escritor usa el patrón original flags=6, vértices de 40 bytes con normal/UV y floats finales 1/0, grupo de 28 bytes con word 4 y cuenta repetida. No es un escritor universal de NSD ni una edición del NIL. Los 20 bytes vacíos siguen idénticos para entidades anteriores.

`object_clicked` referencia el ID del objeto. Puede ejecutar cualquier acción normal; `run_event: ID` llama a otro evento local, y `when: manual` evita activación automática. El validador rechaza ciclos y cadenas mayores de 32; el runtime protege la reentrada síncrona. `travel` y `jump` no permiten el ID de su escena de origen. Otra escena puede usar el mismo NIL para otro layout. Los triggers de proximidad anteriores no se migran automáticamente.

El campo opcional `interaction.source` conserva el selector original (`level`, `template`, `position` y/o `cast_id`, sin operación). Comparte la búsqueda de identidad acotada de control_original. La capa sigue el transform y visibilidad del prop original; si no se identifica de forma única queda oculta y sin highlight. El proxy desactiva colisión física y se captura una sola vez por GUID. El clic nativo, movimiento/render y carga/restore de esta combinación siguen pendientes en CLICK01–08.

## Entradas NSD propias y nombres de eventos

Después de entidades y el contador de scripts globales (0), se escribe count uint32 y count×60 bytes: sector uint32, base 3×3 float32, posición XYZ float32, entrada uint32 e integrante uint32. Siguen la tabla de interestspots (72 bytes por registro), la de posiciones de conversación y el entorno de176 bytes; tablas vacías por defecto. Se validan matrices, tamaños y truncado. Base identidad; orientación autoral mediante SetOrientation. Los planos NIL cacheados permiten identificar el sector sin modificar geometría. Entrada 0: punto predeterminado. Escenas sin esta función conservan sus bytes.

IDs de eventos: 64 caracteres y mayúsculas tras el primer carácter minúsculo. Son strings internos, no nombres fijos NOD. Así click_drippyCandle_4 conserva la plantilla exacta sin alargar el ID compacto del objeto ni su plantilla nativa. La caja temporal de superficies usa la misma región conectada de material que la interacción; cancelar no crea datos.

## Director de escenas · extensión optativa 9/10

Sin conversión automática ni formato 11: `resources.camera_paths` contiene id/name, scene/level de creación y points con position/orientation. Datos inline viajan con Duplicate/export/import; prepare genera `paths/<id>.ncp` y su entrada PROJECT. Rechaza colisiones originales, valores no finitos y puntos consecutivos coincidentes. Los datos participan en fingerprints y References/Safe Delete.

NCP little endian: u32 count, float32 total, count × 26 float32. count 1..128 por buffer nativo. Registro: parámetro acumulado, inverso de tramo, base/lineal/cuadrática/cúbica XYZ, base/lineal/cuadrática/cúbica Euler. Se evalúa base + L*u + Q*u² + C*u³. Escritor propio: distancia acumulada, inverso y coeficientes lineales; Q/C=0. Un punto produce plano fijo; no hay FOV por keyframe. Los 174 originales conservan todos sus floats y bytes. Fuente: research/embrace_closure/ncp_format.md y desensamblado original, no conjetura sobre tamaños.

`sequences[].cues` contiene at/actions ordenados; máximo 64 cues, 32 acciones por cue y duración de secuencia hasta 120 s, límites propios de presupuesto de compilación/tick. `conversations[].nodes[].lines[].actions` usa las mismas Actions, máximo 32; se rechaza abrir otra interacción modal directa o indirectamente. Se bajan a eventos normales sólo en copia del compilador. NCO conserva GOTO/RETURN. `conversations[].staging` referencia una entrada local nombrada.

Contratos optativos: director_v1 incorpora coreografía/puesta en escena; películas con cues se cancelan al cargar para no repetir side effects. Se preserva la reanudación anterior de películas Player sin cues. spatial_loop_v1 guarda configuración y booleanos de fuentes ordenadas por ID, recreando handles no serializados. world_effects_v1 guarda índices de comandos de luz/clima ordenados canónicamente y reaplica una vez al GUID restaurado; un rechazo no genera reintento/log por tick. Sin estos campos no se añaden records nuevos al runtime antiguo. Cambiar contrato requiere partida nueva; no hay migración de saves.

NMF CASH: el lector nativo consume hasta tres nombres por línea y los añade a una tabla global de tres slots, sin comprobar capacidad. Varias líneas pueden sobrescribir su contador y causar un cierre durante la carga. El combinador de campañas conserva primeras apariciones únicas (sin distinguir mayúsculas), emite una sola línea con hasta tres monedas y registra las restantes en build_report.currency_profile.omitted_templates. La comprobación de salida rechaza más de tres consumos acumulados. No edita NMF originales. Evidencia: research/embrace_closure/METADATA_LOAD_FIX.md y native_metadata_cash.txt.

## Cierre quirúrgico: música y conversación nativa

`push_music: {resource: London_Hub, volume: 50}` y `pop_music: true` son Actions ordinarias, en formatos 9/10. Se valida una pista MP3 de música única y volumen entero 0..100. CodexSound.PushMusic(String,int) guarda nombre/volumen previos en un único par estático Java; PopMusic los vuelve a reproducir. No es una pila nativa. RCM limita la propiedad a una operación, comprueba que la instantánea siga siendo suya y no guarda/reconstruye una pila. Restore descarta propiedad transitoria sin Pop desconocido.

Se conserva `conversation.staging: entry_id`. La alternativa optativa es `staging: {mode: native, entries: [speaker_side, companion_side]}`: de una a cuatro entradas existentes, hasta 16 grupos distintos por escena. No hay índices nativos en la UX. La tabla convstart generada está en el cuarto count global, offset +12 del bloque global vacío, después de la tabla de entradas y una tabla de registros de 72 bytes que se mantiene vacía. Sus registros son `<I12fII>` (60 bytes): sector, matriz de rotación/traslación, grupo y selector de miembro. Se emiten selectores cero, como los 473 registros originales validados; el lookup usa sucesivos registros del grupo para la party. Rotación propia acotada al eje Z.

La escritura afecta sólo al NSD propio y exige cuatro counts vacíos de partida. Preserva los otros 176 bytes del entorno. Validación de tamaño, count máximo 64, grupos 0..15, selector cero, matriz ortonormal y floats finitos; roundtrip del subconjunto generado. Las tablas nativas son asignaciones dinámicas: 16 grupos es el límite de autoría adoptado del manual, no una afirmación de array fijo en el loader. No se escribe una tabla desconocida ni un NSD universal.

Los 22 pares NCP de XYZ coincidente encontrados en tres originales también tienen parámetro coincidente; ocho cambian Euler y catorce no. Sus coeficientes no demuestran hold o giro temporizado. El escritor lineal mantiene la restricción; el lector permite parámetros repetidos originales, rechaza negativos/decrecientes, inversos negativos y valores no finitos. Los 174 originales conservan bytes.

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

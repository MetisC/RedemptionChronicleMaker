# Motor: contratos y evidencia vigentes

La instalación original es la fuente técnica principal. Las clases y recursos utilizados están en research/original; research/API_SIGNATURES.txt y research/ALL_CODEX.bytecode.txt permiten contrastar firmas y llamadas. Las referencias documentales del SDK se conservan en research/sdk. No se ejecutan herramientas originales de autoría.

## CONFIRMADO EN ARCHIVOS ORIGINALES

Tenebrae: `London.nsc` conecta únicamente su salida 0 con WestLondon 3. Su NSD estático contiene `tracker_thing` + `ClickExit` en [105,-1122,-368], con brush `CTdoor_L` de 48 triángulos. Las otras dos puertas decorativas son 138 triángulos del NIL, agrupadas alrededor de X536 y X1056, Y184..208. No son dos entidades retirables. Evidencia: research/runtime_test/original_selection/tenebrae_evidence.json.

### Hover y clic nativos

`ClickExit.clicked(int target,int clicker,int capture)` llama a `TakeExit(exitNumber,clicker)`, sin muestreo de distancia. `beginscene` obtiene `GetDescriptionID`, fija `THING_FLAG_NOSTDELETE`, usa `THING_FLAG_NOHIGHLIGHT` para salidas inválidas y actualiza `SetDescriptionID` para el texto abierto/cerrado. El tag 82 del objeto contiene la clave NLS. `CaptureThing(int,int)` y `clicked` pertenecen a la API real.

El lector nativo de entidades NSD en `0x4a8560` consume tags, frames ×24, parámetros, presencia de brush, sectores de región y datos de luz. `0x4c3e50` lee materiales, cuentas de vértices/triángulos/grupos/flags, vértices ×40, índices ×6, grupos ×28, bounds ×24 y planos ×16. El brush original de Tenebrae usa flags 6, últimos floats de vértice 1/0 y grupos con cuenta de vértices repetida y word 4; se conserva este patrón en el escritor acotado. Los planos axiales confirman la convención normal·punto <= distancia. Evidencia: research/engine_evidence/nsd_entities_reader.txt, nsd_brush_reader.txt y research/runtime_test/click_interactions/.

### Crónicas, niveles y escenas

Los NOB son contenedores ZIP. Codex.nob contiene clases Java 45.3; classes.zip aporta la biblioteca de la JVM original. Las fuentes indexadas y sus hashes están en research/source_manifest.json.

NSC declara ubicaciones, geometry NIL, scene NSD, mapas, exits, script y metafile. NMF enumera recursos como NLS, NVO, SPEAKER, PLAYER, NTX, NST y NSS. Una crónica puede reutilizar un NIL en varias ubicaciones con escenas distintas:

```text
location EastLondon l1_east.nil EAST_28_1.nsd mapLondonEast.nui mapLondonEastMain 0x0060
```

NIL v27 contiene geometría, sectores, materiales y luz. NSD v8 describe contenido y entorno. La escena estática asociada al NIL puede aportar contenido base. Los últimos 176 bytes del NSD contienen entorno; los últimos 64 son dos nombres de 32 bytes para modelo y animación del cielo. Los demás campos se preservan opacos cuando su semántica no está confirmada. [SCENE_MODEL.md](SCENE_MODEL.md) recoge sus offsets.

LOCATION_FLAG_CLEARBUFFER vale 64; la referencia EastLondon conserva flags 0x0060. El generador conserva el entorno original, incluido el fondo gris aceptado por el usuario. No añade LondonNightSky ni Sky como supuesta reparación.

### Descubrimiento y vida de recursos

El ejecutable acepta -user y agrega codex, codex/system y codex.nob de esa ruta al classpath. El selector multijugador enumera NSC con el bit 0x2. El NOB se sitúa en la raíz de la carpeta de usuario para que el índice de recursos lo descubra.

Las tablas NLS cuyo nombre comienza por '_' se cargan al arrancar. Las bibliotecas NOT global/medieval/modernDay/multiplayer y las NOT con prefijo '_' se cargan antes de seleccionar una crónica. El NMF también admite referencias NOT explícitas.

Una plantilla propia que ya está en un inventario persistido debe existir al restaurar el perfil, antes de elegir una nueva crónica. El fallo LAN investigado ocurría al escribir a través de un puntero nulo durante esa restauración; las referencias de inventario precedían a la carga del NMF. La reparación mediante bibliotecas con prefijo '_' fue aceptada por el usuario. Evidencia original y aceptación: research/engine_evidence/lan. profile_compatibility conserva definiciones propias necesarias; no modifica el perfil.

### Instanciación y transforms

La API real contiene CreateThing(String,float[],float[]), SpawnThingNear(String,float,int), SetPosition(float[]), SetOrientation(float[]), GetPosition(), GetOrientation(), GuidFromCastID(String) y Remove(). Los scripts originales usan SpawnThingNear con 0.0f y flags 0; puede devolver GUID 0 si falla.

Los transforms utilizan tres floats para posición y tres para orientación. Nuestro modelo expone pitch/roll/yaw, con yaw sobre Z. El editor usa las coordenadas del motor y el raycasting de geometría original; aceptar una coordenada no demuestra que el pathfinder pueda llegar a ella.

SendActorToPos(float[],float), LookAtThing, StopActorAction y métodos de motion existen en las clases originales. StopActorMotion altera campos del controlador de animación; no debe usarse como sustituto general de una pausa de acción al iniciar diálogo.

### Conversaciones, notas y callbacks

`MON3_Main.convended` del Codex.nob instalado elimina la máscara 133 (INVUL=1, AIPAUSED=4, TALKTO=128) antes de AIOn cuando termina sin abortar. `ARC3_Erik` elimina NEUTRAL=262144 al reactivar al actor. Ver research/engine_evidence/dialogue_hostility.txt. Esto confirma las operaciones de flags originales; no acredita por sí solo nuestro preset ni el comportamiento de cada plantilla.

NCO/NVO contienen EVENT, LINE, ANSWERGOTO y ANSWERRETURN. ExecuteConversation lanza el diálogo; convreached y convended reciben los eventos/resultados usados por Java. La entrada se serializa primero. Los scripts originales encadenan conversaciones mediante timer desde convended, dejando terminar la limpieza del diálogo anterior.

SetupCutscene inicia el modo de cámara; Release y EndCutscene liberan controles. La limpieza nativa de conversación elimina recursos y termina retirando su puntero global. Nuestros callbacks difieren la continuación para respetar ese orden.

Los scripts SOC1_DataPrintout1 y CTD_Labyrinth llaman ExecuteText sobre objetos. ItemNodFragment recibe textended(owner). MP_CTD contiene NTX de prólogo; el escritor propio conserva su gramática para notas sin voz. [FORMAT_NOTES.md](FORMAT_NOTES.md) describe NTX y conversaciones con objetos.

### Estado, quests y secuencias

CodexSequence ofrece Get/Set/ClearChronicleFlag, Jump y ChangeScene. Existen Save/RestoreBoolean, Int y Float para records del script. El límite de Chronicle Flags es 1024 y MAX_QUESTS es 64. CodexQuest.Load y Complete se usan en scripts originales; las entradas de journal y pasos se generan directamente en NQD/NLS.

SetTimer agrega entradas incluso con el mismo ID; KillTimer retira las del script/ID. Duplicar timers puede adelantar el final de una película. Los scripts MP_LeavesThree y MP_CTD utilizan control de cutscene, AI, feedback, cámara y movimiento. La programación propia debe mantener ownership y liberar controles una sola vez.

Door usa MoveToFrame y PivotDoor usa RotatePivot. Existe IsExitValid/OpenExit/CloseExit. Mover un prop no reemplaza automáticamente los callbacks ni el estado interno de una puerta original. Ver research/engine_evidence/doors_and_actor_bytecode.txt.

Los 174 NCP cumplen 8+104*n, con n en el primer uint32. El patrón de tamaño aislado no demostraría un escritor; el análisis posterior del evaluador nativo asigna los 104 bytes a parámetros y polinomios de posición/Euler. El codec lineal y el roundtrip se documentan en research/embrace_closure/ncp_format.md. El barrido preliminar de tamaños sigue siendo evidencia de archivos, no la justificación del escritor.

### Control de objetos originales (optativo)

CodexWorld.GetFirstThing y CodexThing.NextInWorld permiten enumerar Things. GetTemplateName, GetLocationNum, GetPosition, GetFramePosition y GuidFromCastID permiten identificarlos. Door llama MoveToFrame(1,speed) y vuelve a 0; PivotDoor invierte el signo de duración al cerrar. El bytecode de Anezka coloca a Christof mediante GetFramePosition Ã¢â€ ’ SetPosition, confirmando coordenadas de mundo en esa API. BROT_31_1_Guard combina SetCollideType(0) con SetRenderFlags(2) para ocultar un objeto. Firmas reales: API_SIGNATURES.txt; extractos: research/engine_evidence/original_objects.txt y doors_and_actor_bytecode.txt.

### Clics y llegada: evidencia actual

El registro anterior confirma CLICK_BOUND para los tres overlays; el usuario confirmó que después dejaron de iluminarse. El binding activaba DISABLECOLLIDE. La revisión actual conserva las propiedades de selección del tracker original, limpia DISABLECOLLIDE/NOBLOCK/BLOCKSELECT/NOHIGHLIGHT y mantiene NOSTDELETE. Si se oculta/retira el original, el overlay se oculta y desactiva su colisión. Los doubles comprueban estas propiedades, sin acreditar el picking nativo.

El usuario confirmó que Stop/CancelActorAction no resolvió el rodeo. SetPosition cambia transform y sector; el teletransporte original además llama a 0x4b0950 → 0x44cc70(1), recalculando el polígono de suelo en 0x44ce56. La API es TeleportPartyToEntrance(playerGuid, entranceIndex): el wrapper 0x470ae0 resuelve el primer int como GUID. Evidencia: research/engine_evidence/native_arrivals.txt.

NSD v8 contiene entradas de 60 bytes: sector uint32, base 3×3 float32, posición 3×float32, entrada uint32 e integrante uint32 (0: fallback). El loader convierte el sector en puntero (0x4a7fc9). El punto original del Club Tenebrae [365,-976,-512] está en el sector 21; el punto propio [724.1906,-338.02884,-512] está en el 19. Planos NIL interiores: dot(normal,punto)>=distancia. Evidencia: nsd_points_reader.txt y tests/test_native_arrivals.py.

El generador escribe entradas en el NSD propio, con el punto predeterminado como entrada 0; el runtime usa el teletransporte nativo y SetOrientation. Se aplica a formato 10 y nuevas escenas con overlays, sin modificar el tutorial aceptado en formato 9 ni la geometría NIL. Falta confirmar selección/clic, primer recorrido, save/load y red dentro del juego. Evidencia offline: research/runtime_test/native_click_revision/.

### WTD importado por el usuario

El NOB entregado contiene tablas NCD/NDD/NDG y NOT/modelos/efectos; no contiene implementaciones Java propias. El filtro exige clases reales derivadas de Discipline y dependencias presentes, sin crear sustitutos. La lectura de Codex confirma SetActorClan(String) y SetActorDisciplineLevel(String,int); scripts originales llaman a este último. La selección actual ofrece 19 clanes adicionales, 9 disciplinas adicionales, 125 plantillas seleccionables y 28 modelos. Rabbit sólo referencia modelos que ya estaban en los archivos originales; no se añade soporte específico.

Penthouse sí es un NIL de 2.576.077 bytes con NSD estático de ocho props, cuyos scripts Door/DoubleDoor/DoorElevator están en Codex. Se reutiliza sin alterar geometría ni importar la crónica demo. Visor propio: 9.136 triángulos, cero avisos de materiales. Evidencia: research/mods/content_probe.json; fuente facilitada por el usuario y políticas de inclusión/exclusión en editor/assets/wtd_policy.json.

## CONFIRMADO EN SDK/DOCUMENTACIÓN

SetupCutscene(client,A,C) fija los focos. OTS_A mira desde detrás de A hacia C y OTS_C a la inversa. ANGULAR_B corresponde a Two Shot. SetShot recibe tipo, ángulo, distancia, lado y tiempo de interpolación; se usan constantes documentadas, no valores inventados. Cámara sobre el hombro es el valor predeterminado del editor.

PlayPath reproduce NCP originales o propios demostrados. CodexSound ofrece música/ambiente y fuentes situadas; el bucle propio tiene ownership/Stop/restore, pendiente de aceptación sonora nativa.

PlayMotionSetMode devuelve duración en milisegundos; su booleano selecciona canal, no repetición. TALK/LISTEN automáticos y overrides desde feedback están documentados. Nuestro catálogo lee los slots NMS reales, con herencia y procedencia.

NSS describe selección de escenas del Narrador y necesita handler Java advance; su última columna es una clave NLS, no un nombre NSD. NSL es una lista de autoría que no necesita consumir el runtime. NIL y NSD tienen responsabilidades distintas; cambiar NSD no recalcula lightmaps ni crea superficies de cielo.

## INFERIDO

El float de SendActorToPos se interpreta como velocidad por su uso en scripts; su escala exacta requiere observación. SetPosition tras Jump permite expresar una llegada, pero no prueba espacio libre ni navegación.

La ausencia de una pose base tras un gesto con AI pausada concuerda con la desaparición observada. La recuperación de idle se programa según la duración devuelta; compilación y doubles no prueban la apariencia de cada modelo.

La biblioteca ausente es la explicación del crash LAN mejor apoyada por volcados, datos de perfil, cargador y reparación aceptada. No se conservan como conclusiones las hipótesis descartadas sobre longitud arbitraria de textos o carpetas vacías.

Reaparición en RC4: el perfil actual conserva `R_rcm_showcase_s1_key`, pero el acceso del escritorio selecciona la carpeta compartida del tutorial/mini, donde esa plantilla faltaba. Se ha añadido allí la definición y su clase, conservando bytes del perfil y de los paquetes activos. La reparación anterior y el cargador respaldan esta explicación; no se ha obtenido un nuevo volcado ni confirmado todavía el nuevo arranque dentro del juego. Evidencia: research/runtime_test/profile_startup_repair.json y profile_originals_check.json. Deploy compartido/personalizado y cierre de una prueba desde el editor ahora conservan las bibliotecas de inventario. Lanzamientos externos con el editor cerrado no permiten actualizar automáticamente objetos adquiridos después: tools/repair_profile_libraries.py permite reparar sólo carpetas RCM administradas.

El selector propio reconoce patrones acotados de tags en el NSD estático asociado al NIL; no es un codec completo ni una prueba de que todos los candidatos estén presentes en runtime. La correlación posición NSD/frame 0 requiere prueba nativa para cada puerta. El generador verifica plantilla/ubicación y coincidencia única a ocho unidades; si no puede identificarlo, no actúa.

## IMPLEMENTADO Y COMPROBADO OFFLINE

Las respuestas RETURN pueden incluir `actions` propias, compiladas como eventos internos normales y ejecutadas por el resultado de conversación tras su limpieza nativa diferida. El flag de la respuesta se aplica primero; abortar no aplica ninguno de estos efectos. Las notas de estas acciones se incluyen en NTX. GOTO mantiene su contrato original; sus efectos se pueden colocar en la primera línea del nodo destino.

`flag_changed` compara GetChronicleFlag con el valor observado anteriormente; inicializa esa observación antes de los eventos de entrada y conserva la tabla `previous` en Save/Restore. No es un callback nativo nuevo: es muestreo del generador propio. El preset hostil de `actor_behavior` usa TEAM_ENEMY0=12 y elimina AIPAUSED, NEUTRAL y TALKTO; el neutral usa TEAM_PEDESTRIANS=10, pausa AI, marca NEUTRAL y recupera TALKTO si hay una conversación/clic de actor de nuestra crónica. Conserva los demás atributos, incluida invulnerabilidad. Firmas y constantes originales: research/API_SIGNATURES.txt, CodexActor.SetActorTeam/SetActorFlags/ClearActorFlags y CodexSequence.Get/Set/ClearChronicleFlag. La compilación contra Codex y doubles verifican orden, abortos, repetición, AI, flags y guardado; no certifican el combate ni la interfaz dentro de Redemption.

RCM añade props de brush seleccionable a su NSD propio, sobre la superficie original, con wrapper NOT y etiqueta NLS propia. No reescribe NIL ni NSD estático original. El evento es `object_clicked`, con las mismas acciones que los demás eventos. La capa recupera las superficies del objeto original o el componente conectado del material NIL señalado, conserva UV/material y separa las dos puertas de Tenebrae. El escritor limita triángulos/materiales, valida degenerados, índices, sectores y floats; sólo genera entidades sin frames/parámetros/luz y seis planos axiales. La compilación real y el readback no certifican hover ni pathfinding nativos.

Los enlaces a la propia escena se rechazan antes de construir. Los selectores la excluyen. Los nuevos runtimes de clic/llamada a evento añaden guardas de viaje y reentrada; las escenas sin esa función conservan el runtime aceptado. No se convierte ni elimina automáticamente un trigger antiguo de un proyecto de usuario.

## PENDIENTE DE VERIFICAR

El usuario confirmó los clics reparados y el primer desplazamiento en su prueba anterior. Nuevas combinaciones de cargas/reentrada/red siguen pendientes.


La aceptación nativa del tutorial corresponde a su recorrido concreto; no acredita cada actor, cámara, path, save/load, reentrada o caso de red. La nueva experiencia de primer arranque, F5 y Showcase sigue pendiente de los casos de [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md). La evidencia aceptada está en research/native_acceptance.

NCP propio lineal y sonido en bucle tienen implementación optativa; su aceptación nativa sigue pendiente. Geometría, codecs NSD/NOT universales y puertas universales no están implementados.

La nueva acción control_original compila contra Codex y tiene pruebas con doubles de identidad, ambigüedad, frames, flags, retirada y reentrada. ORG01–06 siguen pendientes en Redemption. No prueba colisión visual, portales, sincronización del script original ni persistencia de movimiento de puertas.

WTD01–07 siguen pendientes en el juego. Compilación 45.3 y catálogo resuelto no certifican la actuación de cada disciplina/AI ni los saves nativos con contenido adicional. No se presupone una licencia de redistribución a partir de la importación; los paquetes públicos no incluyen assets WTD.

CLICK01–08: confirmar hover/resaltado, selección frente al decorado original, alcance del clic, colisión de la capa, viaje único, diálogo/nota y save/load/reentrada/red en Redemption. Los planos de selección axiales son una aproximación de volumen al componente visible, no el BSP completo de cualquier brush original.

## Cierre de autoría: evidencia nueva

### CONFIRMADO EN ARCHIVO ORIGINAL

174 NCP de Resource.nob, sus hashes y floats: ncp_catalogue.json/ncp_field_analysis.json. El lector/escritor/evaluador nativo (431530/431600/430350) demuestran header de 8 bytes y registros de 104 bytes, buffer de 128, polinomios de posición/Euler; no incluyen FOV por punto. Base de cámara 4bb5b0: forward=(-sin(yaw)*cos(pitch), cos(yaw)*cos(pitch), sin(pitch)). No se modifica el archivo original.

### CONFIRMADO EN SDK / BYTECODE / SCRIPT ORIGINAL

PlayPath, AddFade, AddFlash, AddFilter, ClearAllEffects, LookAtThing/Pos, PlayMotionSetMode, StopActorAction, CodexSound y luces dinámicas contrastados con API/JNI. Auditoría de 472 entradas Codex y 141 clases relevantes en research/embrace_closure. Referencias de clases: PlayPath 71, AddFade 28, AddFlash 7, AddFilter 0; asignación de luz dinámica 0 (API/JNI sí). No confundir referencia de constant pool con ejecución observada. Los argumentos de clima originales son drizzle, lightRain, heavyRain y snow. Flash blanco original 16777215; no se inventan presets RGB. endscene usa tres ints.

### IMPLEMENTADO Y COMPROBADO OFFLINE

Lector NCP sin pérdidas y escritor lineal; captura/edit/reordenación visual, cues y acciones de línea por el compilador de eventos normal; sonido en bucle con ownership, luz/clima con estado optativo. Compilación real Codex 45.3 y doubles separados de tests Qt. Auditoría de paridad en docs/EMBRACE_AUTHORING_PARITY.md. El usuario ya confirmó el hover/clic y primer desplazamiento reparados en su prueba previa; no se vuelve a clasificar esa observación como hipótesis.

### INFERIDO / PENDIENTE DE VERIFICAR

La conversión de orientación de la cámara del visor se deriva de la base nativa; su encuadre visual debe confirmarse en EMB09–11. Escala/apariencia de luz, audio, weather, clipping y contratos reales de carga/reentrada nuevos permanecen en EMB01–24. No se reclama igualdad de smoothing del editor original ni WYSIWYG. No hay observación nativa de las funciones nuevas por el agente.

### CONFIRMADO EN ARCHIVOS ORIGINALES — cargador NMF CASH

El error de Windows al cargar el Taller (18/10/2026 11:21:32, 0xc0000005, Vampire.exe+0x97c16) coincide con la escritura del tercer token CASH. El ejecutable añade hasta tres referencias por línea a slots +0x1aeb8..+0x1aec0; su contador está en +0x1aec4. Varias líneas acumuladas pueden sobrescribirlo. El NMF combinado del Taller tenía cinco referencias consumidas. Evidencia y corrección: research/embrace_closure/METADATA_LOAD_FIX.md, native_metadata_cash.txt y metadata_cash_crash.json. La generación unifica/deduplica hasta tres y el gate rechaza el desbordamiento.

### CONFIRMADO POR EL USUARIO — carga inicial corregida

El usuario observó el cierre del paquete anterior. El paquete corregido está compilado y desplegado; el usuario confirmó su carga inicial: «Funciona bien y abre» (18/10/2026). No se ha ejecutado el juego automáticamente. La auditoría adicional se completó después de esta confirmación; sus funciones nuevas no están incluidas en esa aceptación.

### CONFIRMADO EN API / BYTECODE / ARCHIVOS — cierre quirúrgico

La nueva exploración del Codex original reconfirma 55 clases con referencias PushMusic, 53 PopMusic, 107 TeleportPartyToConversation y una TeleportPartyToEntrance. Push/Pop son wrappers Java con un solo snapshot público de pista/volumen; un segundo Push lo sobrescribe. No es una pila nativa anidada y no hay evidencia de persistencia. Las Actions de RCM conservan propiedad acotada y transitoria, sin guardar un stack inventado.

Entrada y conversación usan tablas NSD separadas y wrappers nativos distintos. Se validaron 99 tablas originales de conversación / 473 registros de 60 bytes; posición, matriz de orientación, sector, grupo y selector. El escritor sólo añade esta tabla demostrada a escenas propias. Los grupos 0..15 son el límite adoptado de autoría Embrace, no un array nativo fijo. Se reutilizan entradas nombradas existentes (una a cuatro por grupo); el runtime llama a TeleportPartyToConversation. Formación, colisión y diferencias en MP permanecen pendientes de observación.

Los 22 pares NCP de posición repetida también repiten parámetro; ocho cambian Euler. El modo anterior por distancia conserva su restricción. El evaluador nativo sí consume polinomios temporales propios: el nuevo modo escribe tramos positivos en segundos, con XYZ constante y Euler variable, sin ejecutar el builder por distancia. Roundtrip de los174originales intacto. Evidencia, decisiones y límites: research/embrace_closure/FINAL_FLECKS_AUDIT.md. Gate: 525 pruebas, 0/0/0; regresión posterior de widgets: 140, 0/0/0. Compilación real 45.3; audio/puesta en escena nuevos siguen MANUAL RUNTIME TEST REQUIRED.

## Strict authoring evidence update

Confirmed original-file/native evidence: NSD parameters are the SECOND entity
variable block (types 1/2/3/5/7/8/10 editable), movement frames are orientation XYZ then
position XYZ (24 bytes); 64 original files lossless. Native interest records are
72 bytes with a separate group selected by AI interestNum. TreasureClass is tag
92 uint32 and container-only in RCM. Optional environment patches touch proven
176-byte tail fields only; unknown bytes remain intact. EAX static precedence prevents a dynamic-tail override; the separately proven runtime roomtype command now provides an optional override after activation. Full evidence, safety limits and pending
native checks: research/embrace_strict_parity/codex_linker_format.md,
treasure_class.md, SAFETY_DECISIONS.md and docs/EMBRACE_AUTHORING_PARITY.md.
SDK-confirmed NTT/NSC documentation is separate from these original-file proofs.
Own maps are implemented through editor/maps.py and chronicle_maps.py. See AUTHORING_COMPLETION.md and research/authoring_completion/EVIDENCE.md.


## Cierre de autoría: mecanismos adicionales

CONFIRMADO EN ARCHIVOS ORIGINALES: región type3, malla local y tabla u32 count +
índices de sectores entre planos de colisión e iluminación.51regiones originales
inventariadas; parámetros type5=CodexRegion/type10=CodexItem contrastados con sus
constructores. El escritor genera cajas yaw-only y conserva la geometría NIL.
Catálogo de constructores unívocos440. Los seis enlaces Player estudiados usan
kind9 para compañeros colocados; todos sus scripts requieren el controlador
privado de campaña. No son un enlace genérico al PJ de LAN. Evidencia completa:
research/authoring_completion/final_original_evidence.json y EVIDENCE.md.

CONFIRMADO EN EJECUTABLE/API: roomtype→409150→49e400→AIL_set_3D_room_type,
rango0..25 y requisito de proveedor3D. CodexConsole.Execute(String) está presente.
NCP430350/430479..43069a evalúa parámetro temporal y polinomios XYZ/Euler
independientes; no llama al builder de distancias para reconstruir coeficientes.

IMPLEMENTADO/PRUEBA OFFLINE: mapas NUI/TGA/NLS/NSC, flags8/16; regiones enlazadas;
NCP temporal; objetivos dinámicos transitorios sobre dGuid, sin nuevos GUID ni
registros alias; zonas sobre volume() y handles existentes; audio asociado a GUID;
catálogo base NCD/NDD. Detalles/límites: AUTHORING_COMPLETION.md y matriz vigente.
Observación dentro del juego PENDIENTE: COMP01–06; no la certifica la compilación.

CONFIRMADO EN EJECUTABLE/SDK: bloque de luz4c44c0 ligado a vértices/grupos de
malla; no es una caja RGB/radio demostrada. SetShot recibe tiempo de transición
y el wrapper NCP fija la lente80f por separado; no hay setter Codex demostrado
de FOV por keyframe. Alternativas: zonas interactivas por flag y planos/recorridos.

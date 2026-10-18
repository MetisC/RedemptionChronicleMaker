# Motor: contratos y evidencia vigentes

La instalaciÃƒÂ³n original es la fuente tÃƒÂ©cnica principal. Las clases y recursos utilizados estÃƒÂ¡n en research/original; research/API_SIGNATURES.txt y research/ALL_CODEX.bytecode.txt permiten contrastar firmas y llamadas. Las referencias documentales del SDK se conservan en research/sdk. No se ejecutan herramientas originales de autorÃƒÂ­a.

## CONFIRMADO EN ARCHIVOS ORIGINALES

Tenebrae: `London.nsc` conecta ÃƒÂºnicamente su salida 0 con WestLondon 3. Su NSD estÃƒÂ¡tico contiene `tracker_thing` + `ClickExit` en [105,-1122,-368], con brush `CTdoor_L` de 48 triÃƒÂ¡ngulos. Las otras dos puertas decorativas son 138 triÃƒÂ¡ngulos del NIL, agrupadas alrededor de X536 y X1056, Y184..208. No son dos entidades retirables. Evidencia: research/runtime_test/original_selection/tenebrae_evidence.json.

### Hover y clic nativos

`ClickExit.clicked(int target,int clicker,int capture)` llama a `TakeExit(exitNumber,clicker)`, sin muestreo de distancia. `beginscene` obtiene `GetDescriptionID`, fija `THING_FLAG_NOSTDELETE`, usa `THING_FLAG_NOHIGHLIGHT` para salidas invÃƒÂ¡lidas y actualiza `SetDescriptionID` para el texto abierto/cerrado. El tag 82 del objeto contiene la clave NLS. `CaptureThing(int,int)` y `clicked` pertenecen a la API real.

El lector nativo de entidades NSD en `0x4a8560` consume tags, frames Ãƒâ€”24, parÃƒÂ¡metros, presencia de brush, sectores de regiÃƒÂ³n y datos de luz. `0x4c3e50` lee materiales, cuentas de vÃƒÂ©rtices/triÃƒÂ¡ngulos/grupos/flags, vÃƒÂ©rtices Ãƒâ€”40, ÃƒÂ­ndices Ãƒâ€”6, grupos Ãƒâ€”28, bounds Ãƒâ€”24 y planos Ãƒâ€”16. El brush original de Tenebrae usa flags 6, ÃƒÂºltimos floats de vÃƒÂ©rtice 1/0 y grupos con cuenta de vÃƒÂ©rtices repetida y word 4; se conserva este patrÃƒÂ³n en el escritor acotado. Los planos axiales confirman la convenciÃƒÂ³n normalÃ‚Â·punto <= distancia. Evidencia: research/engine_evidence/nsd_entities_reader.txt, nsd_brush_reader.txt y research/runtime_test/click_interactions/.

### CrÃƒÂ³nicas, niveles y escenas

Los NOB son contenedores ZIP. Codex.nob contiene clases Java 45.3; classes.zip aporta la biblioteca de la JVM original. Las fuentes indexadas y sus hashes estÃƒÂ¡n en research/source_manifest.json.

NSC declara ubicaciones, geometry NIL, scene NSD, mapas, exits, script y metafile. NMF enumera recursos como NLS, NVO, SPEAKER, PLAYER, NTX, NST y NSS. Una crÃƒÂ³nica puede reutilizar un NIL en varias ubicaciones con escenas distintas:

```text
location EastLondon l1_east.nil EAST_28_1.nsd mapLondonEast.nui mapLondonEastMain 0x0060
```

NIL v27 contiene geometrÃƒÂ­a, sectores, materiales y luz. NSD v8 describe contenido y entorno. La escena estÃƒÂ¡tica asociada al NIL puede aportar contenido base. Los ÃƒÂºltimos 176 bytes del NSD contienen entorno; los ÃƒÂºltimos 64 son dos nombres de 32 bytes para modelo y animaciÃƒÂ³n del cielo. Los demÃƒÂ¡s campos se preservan opacos cuando su semÃƒÂ¡ntica no estÃƒÂ¡ confirmada. [SCENE_MODEL.md](SCENE_MODEL.md) recoge sus offsets.

LOCATION_FLAG_CLEARBUFFER vale 64; la referencia EastLondon conserva flags 0x0060. El generador conserva el entorno original, incluido el fondo gris aceptado por el usuario. No aÃƒÂ±ade LondonNightSky ni Sky como supuesta reparaciÃƒÂ³n.

### Descubrimiento y vida de recursos

El ejecutable acepta -user y agrega codex, codex/system y codex.nob de esa ruta al classpath. El selector multijugador enumera NSC con el bit 0x2. El NOB se sitÃƒÂºa en la raÃƒÂ­z de la carpeta de usuario para que el ÃƒÂ­ndice de recursos lo descubra.

Las tablas NLS cuyo nombre comienza por '_' se cargan al arrancar. Las bibliotecas NOT global/medieval/modernDay/multiplayer y las NOT con prefijo '_' se cargan antes de seleccionar una crÃƒÂ³nica. El NMF tambiÃƒÂ©n admite referencias NOT explÃƒÂ­citas.

Una plantilla propia que ya estÃƒÂ¡ en un inventario persistido debe existir al restaurar el perfil, antes de elegir una nueva crÃƒÂ³nica. El fallo LAN investigado ocurrÃƒÂ­a al escribir a travÃƒÂ©s de un puntero nulo durante esa restauraciÃƒÂ³n; las referencias de inventario precedÃƒÂ­an a la carga del NMF. La reparaciÃƒÂ³n mediante bibliotecas con prefijo '_' fue aceptada por el usuario. Evidencia original y aceptaciÃƒÂ³n: research/engine_evidence/lan. profile_compatibility conserva definiciones propias necesarias; no modifica el perfil.

### InstanciaciÃƒÂ³n y transforms

La API real contiene CreateThing(String,float[],float[]), SpawnThingNear(String,float,int), SetPosition(float[]), SetOrientation(float[]), GetPosition(), GetOrientation(), GuidFromCastID(String) y Remove(). Los scripts originales usan SpawnThingNear con 0.0f y flags 0; puede devolver GUID 0 si falla.

Los transforms utilizan tres floats para posiciÃƒÂ³n y tres para orientaciÃƒÂ³n. Nuestro modelo expone pitch/roll/yaw, con yaw sobre Z. El editor usa las coordenadas del motor y el raycasting de geometrÃƒÂ­a original; aceptar una coordenada no demuestra que el pathfinder pueda llegar a ella.

SendActorToPos(float[],float), LookAtThing, StopActorAction y mÃƒÂ©todos de motion existen en las clases originales. StopActorMotion altera campos del controlador de animaciÃƒÂ³n; no debe usarse como sustituto general de una pausa de acciÃƒÂ³n al iniciar diÃƒÂ¡logo.

### Conversaciones, notas y callbacks

NCO/NVO contienen EVENT, LINE, ANSWERGOTO y ANSWERRETURN. ExecuteConversation lanza el diÃƒÂ¡logo; convreached y convended reciben los eventos/resultados usados por Java. La entrada se serializa primero. Los scripts originales encadenan conversaciones mediante timer desde convended, dejando terminar la limpieza del diÃƒÂ¡logo anterior.

SetupCutscene inicia el modo de cÃƒÂ¡mara; Release y EndCutscene liberan controles. La limpieza nativa de conversaciÃƒÂ³n elimina recursos y termina retirando su puntero global. Nuestros callbacks difieren la continuaciÃƒÂ³n para respetar ese orden.

Los scripts SOC1_DataPrintout1 y CTD_Labyrinth llaman ExecuteText sobre objetos. ItemNodFragment recibe textended(owner). MP_CTD contiene NTX de prÃƒÂ³logo; el escritor propio conserva su gramÃƒÂ¡tica para notas sin voz. [FORMAT_NOTES.md](FORMAT_NOTES.md) describe NTX y conversaciones con objetos.

### Estado, quests y secuencias

CodexSequence ofrece Get/Set/ClearChronicleFlag, Jump y ChangeScene. Existen Save/RestoreBoolean, Int y Float para records del script. El lÃƒÂ­mite de Chronicle Flags es 1024 y MAX_QUESTS es 64. CodexQuest.Load y Complete se usan en scripts originales; las entradas de journal y pasos se generan directamente en NQD/NLS.

SetTimer agrega entradas incluso con el mismo ID; KillTimer retira las del script/ID. Duplicar timers puede adelantar el final de una pelÃƒÂ­cula. Los scripts MP_LeavesThree y MP_CTD utilizan control de cutscene, AI, feedback, cÃƒÂ¡mara y movimiento. La programaciÃƒÂ³n propia debe mantener ownership y liberar controles una sola vez.

Door usa MoveToFrame y PivotDoor usa RotatePivot. Existe IsExitValid/OpenExit/CloseExit. Mover un prop no reemplaza automÃƒÂ¡ticamente los callbacks ni el estado interno de una puerta original. Ver research/engine_evidence/doors_and_actor_bytecode.txt.

Los 174 NCP examinados cumplen tamaÃƒÂ±o 8+104*n, con n en el primer uint32. El patrÃƒÂ³n no basta para implementar un writer: tangentes, orientaciÃƒÂ³n y padding siguen incompletos. Datos: research/engine_evidence/ncp_structure_scan.json.

### Control de objetos originales (optativo)

CodexWorld.GetFirstThing y CodexThing.NextInWorld permiten enumerar Things. GetTemplateName, GetLocationNum, GetPosition, GetFramePosition y GuidFromCastID permiten identificarlos. Door llama MoveToFrame(1,speed) y vuelve a 0; PivotDoor invierte el signo de duraciÃƒÂ³n al cerrar. El bytecode de Anezka coloca a Christof mediante GetFramePosition Ã¢â€ â€™ SetPosition, confirmando coordenadas de mundo en esa API. BROT_31_1_Guard combina SetCollideType(0) con SetRenderFlags(2) para ocultar un objeto. Firmas reales: API_SIGNATURES.txt; extractos: research/engine_evidence/original_objects.txt y doors_and_actor_bytecode.txt.

### Clics y llegada: evidencia actual

El registro anterior confirma CLICK_BOUND para los tres overlays; el usuario confirmó que después dejaron de iluminarse. El binding activaba DISABLECOLLIDE. La revisión actual conserva las propiedades de selección del tracker original, limpia DISABLECOLLIDE/NOBLOCK/BLOCKSELECT/NOHIGHLIGHT y mantiene NOSTDELETE. Si se oculta/retira el original, el overlay se oculta y desactiva su colisión. Los doubles comprueban estas propiedades, sin acreditar el picking nativo.

El usuario confirmó que Stop/CancelActorAction no resolvió el rodeo. SetPosition cambia transform y sector; el teletransporte original además llama a 0x4b0950 → 0x44cc70(1), recalculando el polígono de suelo en 0x44ce56. La API es TeleportPartyToEntrance(playerGuid, entranceIndex): el wrapper 0x470ae0 resuelve el primer int como GUID. Evidencia: research/engine_evidence/native_arrivals.txt.

NSD v8 contiene entradas de 60 bytes: sector uint32, base 3×3 float32, posición 3×float32, entrada uint32 e integrante uint32 (0: fallback). El loader convierte el sector en puntero (0x4a7fc9). El punto original del Club Tenebrae [365,-976,-512] está en el sector 21; el punto propio [724.1906,-338.02884,-512] está en el 19. Planos NIL interiores: dot(normal,punto)>=distancia. Evidencia: nsd_points_reader.txt y tests/test_native_arrivals.py.

El generador escribe entradas en el NSD propio, con el punto predeterminado como entrada 0; el runtime usa el teletransporte nativo y SetOrientation. Se aplica a formato 10 y nuevas escenas con overlays, sin modificar el tutorial aceptado en formato 9 ni la geometría NIL. Falta confirmar selección/clic, primer recorrido, save/load y red dentro del juego. Evidencia offline: research/runtime_test/native_click_revision/.

### WTD importado por el usuario

El NOB entregado contiene tablas NCD/NDD/NDG y NOT/modelos/efectos; no contiene implementaciones Java propias. El filtro exige clases reales derivadas de Discipline y dependencias presentes, sin crear sustitutos. La lectura de Codex confirma SetActorClan(String) y SetActorDisciplineLevel(String,int); scripts originales llaman a este ÃƒÂºltimo. La selecciÃƒÂ³n actual ofrece 19 clanes adicionales, 9 disciplinas adicionales, 125 plantillas seleccionables y 28 modelos. Rabbit sÃƒÂ³lo referencia modelos que ya estaban en los archivos originales; no se aÃƒÂ±ade soporte especÃƒÂ­fico.

Penthouse sÃƒÂ­ es un NIL de 2.576.077 bytes con NSD estÃƒÂ¡tico de ocho props, cuyos scripts Door/DoubleDoor/DoorElevator estÃƒÂ¡n en Codex. Se reutiliza sin alterar geometrÃƒÂ­a ni importar la crÃƒÂ³nica demo. Visor propio: 9.136 triÃƒÂ¡ngulos, cero avisos de materiales. Evidencia: research/mods/content_probe.json; fuente facilitada por el usuario y polÃƒÂ­ticas de inclusiÃƒÂ³n/exclusiÃƒÂ³n en editor/assets/wtd_policy.json.

## CONFIRMADO EN SDK/DOCUMENTACIÃƒâ€œN

SetupCutscene(client,A,C) fija los focos. OTS_A mira desde detrÃƒÂ¡s de A hacia C y OTS_C a la inversa. ANGULAR_B corresponde a Two Shot. SetShot recibe tipo, ÃƒÂ¡ngulo, distancia, lado y tiempo de interpolaciÃƒÂ³n; se usan constantes documentadas, no valores inventados. CÃƒÂ¡mara sobre el hombro es el valor predeterminado del editor.

PlayPath utiliza paths de cÃƒÂ¡mara precomputados. CodexSound admite mÃƒÂºsica, ambiente y sonido situado con radios, volumen, flags y posiciÃƒÂ³n/GUID. La acciÃƒÂ³n espacial propia no se anuncia como sistema persistente completo de audio en bucle.

PlayMotionSetMode devuelve duraciÃƒÂ³n en milisegundos; su booleano selecciona canal, no repeticiÃƒÂ³n. TALK/LISTEN automÃƒÂ¡ticos y overrides desde feedback estÃƒÂ¡n documentados. Nuestro catÃƒÂ¡logo lee los slots NMS reales, con herencia y procedencia.

NSS describe selecciÃƒÂ³n de escenas del Narrador y necesita handler Java advance; su ÃƒÂºltima columna es una clave NLS, no un nombre NSD. NSL es una lista de autorÃƒÂ­a que no necesita consumir el runtime. NIL y NSD tienen responsabilidades distintas; cambiar NSD no recalcula lightmaps ni crea superficies de cielo.

## INFERIDO

El float de SendActorToPos se interpreta como velocidad por su uso en scripts; su escala exacta requiere observaciÃƒÂ³n. SetPosition tras Jump permite expresar una llegada, pero no prueba espacio libre ni navegaciÃƒÂ³n.

La ausencia de una pose base tras un gesto con AI pausada concuerda con la desapariciÃƒÂ³n observada. La recuperaciÃƒÂ³n de idle se programa segÃƒÂºn la duraciÃƒÂ³n devuelta; compilaciÃƒÂ³n y doubles no prueban la apariencia de cada modelo.

La biblioteca ausente es la explicaciÃƒÂ³n del crash LAN mejor apoyada por volcados, datos de perfil, cargador y reparaciÃƒÂ³n aceptada. No se conservan como conclusiones las hipÃƒÂ³tesis descartadas sobre longitud arbitraria de textos o carpetas vacÃƒÂ­as.

ReapariciÃƒÂ³n en RC4: el perfil actual conserva `R_rcm_showcase_s1_key`, pero el acceso del escritorio selecciona la carpeta compartida del tutorial/mini, donde esa plantilla faltaba. Se ha aÃƒÂ±adido allÃƒÂ­ la definiciÃƒÂ³n y su clase, conservando bytes del perfil y de los paquetes activos. La reparaciÃƒÂ³n anterior y el cargador respaldan esta explicaciÃƒÂ³n; no se ha obtenido un nuevo volcado ni confirmado todavÃƒÂ­a el nuevo arranque dentro del juego. Evidencia: research/runtime_test/profile_startup_repair.json y profile_originals_check.json. Deploy compartido/personalizado y cierre de una prueba desde el editor ahora conservan las bibliotecas de inventario. Lanzamientos externos con el editor cerrado no permiten actualizar automÃƒÂ¡ticamente objetos adquiridos despuÃƒÂ©s: tools/repair_profile_libraries.py permite reparar sÃƒÂ³lo carpetas RCM administradas.

El selector propio reconoce patrones acotados de tags en el NSD estÃƒÂ¡tico asociado al NIL; no es un codec completo ni una prueba de que todos los candidatos estÃƒÂ©n presentes en runtime. La correlaciÃƒÂ³n posiciÃƒÂ³n NSD/frame 0 requiere prueba nativa para cada puerta. El generador verifica plantilla/ubicaciÃƒÂ³n y coincidencia ÃƒÂºnica a ocho unidades; si no puede identificarlo, no actÃƒÂºa.

## IMPLEMENTADO Y COMPROBADO OFFLINE

RCM aÃƒÂ±ade props de brush seleccionable a su NSD propio, sobre la superficie original, con wrapper NOT y etiqueta NLS propia. No reescribe NIL ni NSD estÃƒÂ¡tico original. El evento es `object_clicked`, con las mismas acciones que los demÃƒÂ¡s eventos. La capa recupera las superficies del objeto original o el componente conectado del material NIL seÃƒÂ±alado, conserva UV/material y separa las dos puertas de Tenebrae. El escritor limita triÃƒÂ¡ngulos/materiales, valida degenerados, ÃƒÂ­ndices, sectores y floats; sÃƒÂ³lo genera entidades sin frames/parÃƒÂ¡metros/luz y seis planos axiales. La compilaciÃƒÂ³n real y el readback no certifican hover ni pathfinding nativos.

Los enlaces a la propia escena se rechazan antes de construir. Los selectores la excluyen. Los nuevos runtimes de clic/llamada a evento aÃƒÂ±aden guardas de viaje y reentrada; las escenas sin esa funciÃƒÂ³n conservan el runtime aceptado. No se convierte ni elimina automÃƒÂ¡ticamente un trigger antiguo de un proyecto de usuario.

## PENDIENTE DE VERIFICAR

Confirmar manualmente los tres overlays de «Mi nueva crónica» y el primer recorrido mediante entradas NSD nativas. No se declara una corrección nativa confirmada por pruebas offline.


La aceptaciÃƒÂ³n nativa del tutorial corresponde a su recorrido concreto; no acredita cada actor, cÃƒÂ¡mara, path, save/load, reentrada o caso de red. La nueva experiencia de primer arranque, F5 y Showcase sigue pendiente de los casos de [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md). La evidencia aceptada estÃƒÂ¡ en research/native_acceptance.

NCP propio, ediciÃƒÂ³n geomÃƒÂ©trica, NSD complejo completo, todos los tags NOT, ÃƒÂ¡rbol AI completo, audio espacial persistente avanzado, puertas y eliminaciÃƒÂ³n universal de estÃƒÂ¡tica siguen limitados. Un build con clases 45.3 o un test con doubles no convierte estas capacidades en verificadas en Redemption.

La nueva acciÃƒÂ³n control_original compila contra Codex y tiene pruebas con doubles de identidad, ambigÃƒÂ¼edad, frames, flags, retirada y reentrada. ORG01Ã¢â‚¬â€œ06 siguen pendientes en Redemption. No prueba colisiÃƒÂ³n visual, portales, sincronizaciÃƒÂ³n del script original ni persistencia de movimiento de puertas.

WTD01Ã¢â‚¬â€œ07 siguen pendientes en el juego. CompilaciÃƒÂ³n 45.3 y catÃƒÂ¡logo resuelto no certifican la actuaciÃƒÂ³n de cada disciplina/AI ni los saves nativos con contenido adicional. No se presupone una licencia de redistribuciÃƒÂ³n a partir de la importaciÃƒÂ³n; los paquetes pÃƒÂºblicos no incluyen assets WTD.

CLICK01Ã¢â‚¬â€œ08: confirmar hover/resaltado, selecciÃƒÂ³n frente al decorado original, alcance del clic, colisiÃƒÂ³n de la capa, viaje ÃƒÂºnico, diÃƒÂ¡logo/nota y save/load/reentrada/red en Redemption. Los planos de selecciÃƒÂ³n axiales son una aproximaciÃƒÂ³n de volumen al componente visible, no el BSP completo de cualquier brush original.

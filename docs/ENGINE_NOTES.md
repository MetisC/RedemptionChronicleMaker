# Motor: contratos y evidencia vigentes

La instalación original es la fuente técnica principal. Las clases y recursos utilizados están en research/original; research/API_SIGNATURES.txt y research/ALL_CODEX.bytecode.txt permiten contrastar firmas y llamadas. Las referencias documentales del SDK se conservan en research/sdk. No se ejecutan herramientas originales de autoría.

## CONFIRMADO EN ARCHIVOS ORIGINALES

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

NCO/NVO contienen EVENT, LINE, ANSWERGOTO y ANSWERRETURN. ExecuteConversation lanza el diálogo; convreached y convended reciben los eventos/resultados usados por Java. La entrada se serializa primero. Los scripts originales encadenan conversaciones mediante timer desde convended, dejando terminar la limpieza del diálogo anterior.

SetupCutscene inicia el modo de cámara; Release y EndCutscene liberan controles. La limpieza nativa de conversación elimina recursos y termina retirando su puntero global. Nuestros callbacks difieren la continuación para respetar ese orden.

Los scripts SOC1_DataPrintout1 y CTD_Labyrinth llaman ExecuteText sobre objetos. ItemNodFragment recibe textended(owner). MP_CTD contiene NTX de prólogo; el escritor propio conserva su gramática para notas sin voz. [FORMAT_NOTES.md](FORMAT_NOTES.md) describe NTX y conversaciones con objetos.

### Estado, quests y secuencias

CodexSequence ofrece Get/Set/ClearChronicleFlag, Jump y ChangeScene. Existen Save/RestoreBoolean, Int y Float para records del script. El límite de Chronicle Flags es 1024 y MAX_QUESTS es 64. CodexQuest.Load y Complete se usan en scripts originales; las entradas de journal y pasos se generan directamente en NQD/NLS.

SetTimer agrega entradas incluso con el mismo ID; KillTimer retira las del script/ID. Duplicar timers puede adelantar el final de una película. Los scripts MP_LeavesThree y MP_CTD utilizan control de cutscene, AI, feedback, cámara y movimiento. La programación propia debe mantener ownership y liberar controles una sola vez.

Door usa MoveToFrame y PivotDoor usa RotatePivot. Existe IsExitValid/OpenExit/CloseExit. Mover un prop no reemplaza automáticamente los callbacks ni el estado interno de una puerta original. Ver research/engine_evidence/doors_and_actor_bytecode.txt.

Los 174 NCP examinados cumplen tamaño 8+104*n, con n en el primer uint32. El patrón no basta para implementar un writer: tangentes, orientación y padding siguen incompletos. Datos: research/engine_evidence/ncp_structure_scan.json.

## CONFIRMADO EN SDK/DOCUMENTACIÓN

SetupCutscene(client,A,C) fija los focos. OTS_A mira desde detrás de A hacia C y OTS_C a la inversa. ANGULAR_B corresponde a Two Shot. SetShot recibe tipo, ángulo, distancia, lado y tiempo de interpolación; se usan constantes documentadas, no valores inventados. Cámara sobre el hombro es el valor predeterminado del editor.

PlayPath utiliza paths de cámara precomputados. CodexSound admite música, ambiente y sonido situado con radios, volumen, flags y posición/GUID. La acción espacial propia no se anuncia como sistema persistente completo de audio en bucle.

PlayMotionSetMode devuelve duración en milisegundos; su booleano selecciona canal, no repetición. TALK/LISTEN automáticos y overrides desde feedback están documentados. Nuestro catálogo lee los slots NMS reales, con herencia y procedencia.

NSS describe selección de escenas del Narrador y necesita handler Java advance; su última columna es una clave NLS, no un nombre NSD. NSL es una lista de autoría que no necesita consumir el runtime. NIL y NSD tienen responsabilidades distintas; cambiar NSD no recalcula lightmaps ni crea superficies de cielo.

## INFERIDO

El float de SendActorToPos se interpreta como velocidad por su uso en scripts; su escala exacta requiere observación. SetPosition tras Jump permite expresar una llegada, pero no prueba espacio libre ni navegación.

La ausencia de una pose base tras un gesto con AI pausada concuerda con la desaparición observada. La recuperación de idle se programa según la duración devuelta; compilación y doubles no prueban la apariencia de cada modelo.

La biblioteca ausente es la explicación del crash LAN mejor apoyada por volcados, datos de perfil, cargador y reparación aceptada. No se conservan como conclusiones las hipótesis descartadas sobre longitud arbitraria de textos o carpetas vacías.

## PENDIENTE DE VERIFICAR

La aceptación nativa del tutorial corresponde a su recorrido concreto; no acredita cada actor, cámara, path, save/load, reentrada o caso de red. La nueva experiencia de primer arranque, F5 y Showcase sigue pendiente de los casos de [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md). La evidencia aceptada está en research/native_acceptance.

NCP propio, edición geométrica, NSD complejo completo, todos los tags NOT, árbol AI completo, audio espacial persistente avanzado, puertas y eliminación universal de estática siguen limitados. Un build con clases 45.3 o un test con doubles no convierte estas capacidades en verificadas en Redemption.

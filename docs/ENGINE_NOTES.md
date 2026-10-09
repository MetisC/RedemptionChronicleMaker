# Notas del motor y evidencia

## Fase 9: evidencia nueva, sin ensayo nativo de 0.9.0

### CONFIRMADO EN ARCHIVOS ORIGINALES

`research/phase9/api_signatures.txt` conserva SendActorToPos(float[],float), StopActorMotion, SetPosition/SetOrientation, HasFrames/GetNumFrames, MoveToFrame/RotatePivot, IsExitValid/OpenExit/CloseExit, SetShot y constructores situados de CodexSound. Todas las ramas nuevas compilan contra esas clases a45.3. `doors_and_actor_bytecode.txt`: Door abre con MoveToFrame(1,speed) y cierra con frame0; PivotDoor usa RotatePivot(frame,+/-duration). Nuestro movimiento no sustituye sus callbacks ni actualiza su bOpen automáticamente.

174 NCP originales cumplen tamaño `8+104*n`, con n en el primer uint32 little-endian. Evidencia: `research/phase9/ncp_structure_scan.json`. Campos/tangentes/padding/orientación sin contrato completo; no se genera NCP por extrapolar ese patrón.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

`research/phase7/embrace/cutscene.htm.txt`, `CodexCamera.htm.txt` y `CodexSound.htm.txt`: SetupCutscene(client,A,C) define focos. Two Shot es ANGULAR_B; OTS_A mira desde detrás de A hacia C, OTS_C a la inversa; POV_A muestra A desde C, POV_C muestra C desde A. PROFILE_A/C tienen soporte incierto según el propio manual y no se usan como Two Shot. SetShot recibe enums shot/angle/distance/side/lerpTime. CodexSound situado recibe name,minDist,maxDist,volume,pan,flags,position/thingGuid; nuestra acción usa pan0/flags0, sin loop. Ejemplos originales de movimiento usan90 y210 como segundo argumento.

### INFERIDO

El float de SendActorToPos parece ser velocidad; se expone como parámetro de movimiento,90 por defecto. Su escala exacta queda por comprobar. Aplicar SetPosition tras Jump puede proporcionar una llegada lógica; aceptar XYZ no demuestra espacio libre para la cápsula del jugador.

### PENDIENTE DE VERIFICAR

Llegadas/collision, navegación/patrullas, cámara con dos focos, sonido audible, GUIDs/checkpoints después de save/load, puertas/exits y scripts base, herencia NOT/AI. El usuario aplazó las pruebas de juego. Static ALL/NONE/SELECTIVE, NCP desde vista, loop espacial persistente y árbol AI siguen abiertos. No se ha ejecutado ninguna herramienta original de autoría.

Investigación: 7–8 de octubre de 2026. Fuente principal: instalación GOG indicada por el usuario. Las copias locales están en `research/original/`; los archivos originales solo se abren para lectura. No se ha ejecutado ningún programa de autoría original. La autorización histórica de despliegue en RCM se utilizó en Fase 1. La entrega inicial de Fase 2 respetó solo lectura. La autorización posterior permite preparar pruebas únicamente en RCM; los originales fuera de ella permanecen intactos.

La existencia de una firma Java demuestra que la API se distribuye con esta versión. El bytecode muestra cómo la usan scripts originales. Ninguno de esos dos hechos prueba que nuestro paquete ya funcione en el motor nativo.

## OBSERVADO POR EL USUARIO EN EL JUEGO

El usuario confirmó en la revisión 3: nombre correcto, mapa cargado, halo desaparecido, Victoria visible junto al jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara de diálogo se percibe algo baja. Save/load y replicación en red no se han probado.

El registro nativo preservado en research/runtime_test/native_revision3_accepted.log contiene construcción del controlador, beginscene y SpawnThingNear GUID=1073741889 junto al jugador 1073741825. No es el log del harness. En ese ensayo inicial se comentó un fondo azul cerca del muelle; después se compararon las referencias originales y el usuario aceptó su aspecto gris, sin cielo adicional.

## CONFIRMADO EN ARCHIVOS ORIGINALES

### Inventario y puntos de entrada

### Hallazgos del ensayo: menú, proximidad y fondo

Confirmado por análisis estático de archivos originales, no por ejecución de la revisión:

- `Codex.LOCATION_FLAG_CLEARBUFFER = 64` en las clases originales. EastLondon en `London.nsc` tiene `0x0060`; nuestro NSC anterior usaba solo `0x0020`, omitiendo ese bit. El generador conserva ahora CLEARBUFFER de la referencia original, dando `0x60` para este demo. Esto acredita una omisión concreta; el usuario confirmó que el halo desapareció al probar la revisión 3, sin que esto pruebe una causa única.
- El cargador de plantillas carga `global`, `medieval`, `modernDay` y `multiplayer` y solo autoenumera NOT con primer carácter `_` (`0x4dce68`). Nuestro `R_east_demo.not` no pertenecía a esas categorías y no tenía referencia explícita. El parser NMF admite `NOT <nombre>` y llama al cargador `0x4dcf20` (`0x4979cd–0x4979fe`). La revisión añade `NOT R_east_demo.not` al NMF. Otro contrato posible es el listado de bibliotecas NOT del encabezado NSD (`0x4a7f04–0x4a7f7a`), no implementado aquí. No se modifica ni reemplaza una biblioteca original.
- El Java de revisión 3 crea un registro de texto al construirse y anota beginscene, jugador/ubicación, GUID de spawn, errores y fin de reintentos. Usa Java 1.1 `FileOutputStream`/`PrintStream`, compilado contra `classes.zip` original. Ruta relativa fija `RCM/<id>/runtime_trace.log`, con el directorio de trabajo en la raíz del juego. Los tests escriben una copia separada dentro de `build/tests/`; ese log no es evidencia nativa.

- Después de registrar `-user`, `Vampire.exe 0x4284b5` enumera `strings`/`nls`, comprueba el primer carácter `_` en `0x4284db` y carga esas tablas en `0x4284e1`. Nuestro NLS ahora se llama `_R_east_demo.nls`. El NMF también lo referencia. La tabla global `chronicles.nls` deja de copiarse.
- El lector NSD v8 (`0x4a7de0`) termina leyendo dos nombres de 32 bytes: modelo (`0x4a82a2`, llamada a `0x4c4f50`) y animación (`0x4a82db`, llamada a `0x4c7cf0`). Son los últimos 64 bytes. Escenas originales de Viena usan `viennasky` sin extensión. `Resource.nob` contiene `3d/Models/LondonNightSky.nod` y `3d/Anims/LondonNightSky.nad`; la revisión 3 referenciaba ambos. La revisión 4 utiliza Sky. Los NSD londinenses examinados tenían esos campos vacíos: no se afirma que copiemos su configuración de fondo.
- `CodexThing.SpawnThingNear(String,float,int)` está en la API real y se usa con `0.0f, 0` en bytecode original de summons. El JNI `0x473b70` crea la plantilla y llama a `0x4b0d00` para situarla cerca del propietario; devuelve 0 si falla. El tercer argumento es flags, no número de intentos. Usamos esos mismos argumentos sobre el jugador y después `SetOrientation(float[])`.
- `StingerSound` tiene los callbacks `beginscene(int,int)` y `timer(int,float,float,float,float)` y vuelve a programar `SetTimer` desde el timer. Es evidencia de ese patrón para un script de entidad. Nuestra espera usa `SetTimer(0.5f,9001)` y `KillTimer(9001)`; todas las firmas compilan contra Codex original.

Ventanas reproducibles: `tools/research_scene_runtime.py` → `research/user_directory/scene_runtime.txt`. Detalles auxiliares en `localisation_order.txt`, `scene_loading.txt` y `spawn_near.txt`.

Los seis `.nob` son ZIP y se leen con `zipfile`. `Codex.nob` tiene 465 clases: todas tienen versión **45.3**. También contiene ejecutables de compilación/documentación antiguos, un DLL y un proyecto de Visual Studio; no se ejecutaron y no son dependencias del proyecto. `classes.zip` contiene la biblioteca de la JVM, incluyendo `java/lang/Object.class` 45.3.

`research/source_manifest.json` registra hashes de los seis contenedores, los archivos de `Chronicles`, `classes.zip`, `Vampire.exe` y manuales/readmes: 43 fuentes. `research/discovery_summary.json`, `research/binary_headers.json` y los catálogos contienen el inventario reproducible.

Investigación adicional del 8 de octubre: el ejecutable reconoce `-user`/`/user`, registra esa ruta para recursos y la incorpora al classpath como `<user>\codex`, `<user>\codex\system` y `<user>\codex.nob`. El usuario ha confirmado la aparición de la crónica y carga del mapa por esa vía. Evidencia estática en `USER_DIRECTORY.md` y `research/user_directory/`; la lógica simple de Fase 1 fue posteriormente confirmada por el usuario; las ampliaciones de Fase 2 requieren otra prueba nativa.

La rutina del selector multijugador (`0x412a29`) enumera `chronicles`/`nsc` y filtra el bit `0x2`. En el enumerador (`0x4cae60`), el prefijo de usuario se calcula pero no se pasa a la búsqueda física de archivos sueltos (`0x4caee8`); los índices NOB sí se recorren (`0x4cafc8`). La distribución corregida incluye el NOB en la raíz de la carpeta seleccionada por `-user`.

### 1. Estructura de una crónica

`Chronicles/London.nsc` contiene filas `location`, enlaces `exit`, `script`, `metafile`, `portal` y `flags`. `MP_CurseDarkness.nsc` añade `reviveloc`. Cada `location` tiene identificador, `.nil`, `.nsd` o `null`, `.nui`, etiqueta del mapa y flags. Los `.nmf` enumeran recursos como `NLS`, `NVO`, `SPEAKER`, `PLAYER`, `CASH`, `NTX`, `NST` y `NSS`.

No se identifica level con crónica: una ubicación del `.nsc` selecciona geometría y escena por separado. Los nombres de ubicación pueden ser aliases de un mismo `.nil`.

### 2–4. Referencias de level, escenas y relación NIL/NSD

`London.nsc` declara:

```text
location EastLondon l1_east.nil EAST_28_1.nsd mapLondonEast.nui mapLondonEastMain 0x0060
```

`MP_London_Null.nsc` declara la misma ubicación y geometría con `null` en la columna de escena. Hay 112 `.nil` con cabecera `NIL\x10`, DWORD siguiente 27; 291 `.nsd` con `NSD\x10`, DWORD siguiente 8. No son el mismo formato ni el mismo recurso.

`SET4_29_2_Main` llama `CodexSequence.ChangeScene("EastLondon", "EAST_32_1.nsd")`. `WAR3_Main` cambia escenas de dos ubicaciones tras conversaciones. `mp_lot.nss` y `MP_CTD.nss` tienen filas `Scene <ubicación numérica> <índice> <nombre de escena>`.

### 5–9. Contenido, creación y transforms

La API contiene exactamente:

```java
new CodexWorld(Codex.WORLD_CURRENT);
int CreateThing(String template, float[] position, float[] orientation);
boolean CodexThing.SetPosition(float[] position);
boolean CodexThing.SetOrientation(float[] orientation);
float[] CodexThing.GetPosition();
float[] CodexThing.GetOrientation();
```

`WORLD_CURRENT = 12345678`; no equivale al índice de ubicación. `VEC_X/Y/Z = 0/1/2`; `VEC_PITCH/ROLL/YAW = 0/1/2`. Los wrappers de tres floats conservan ese orden y crean un array de tres elementos. Las entidades `.nsd` incluyen posición y orientación como tres floats little endian en tags separados.

`ClassSkeletonWraith.awaken` crea `Szlachta` mediante `CodexWorld.CreateThing`. Otros scripts usan `CodexThing.SpawnThing`, `SpawnThingNear` y `Codex.Spawn`; `CTD_LeComte.convended` crea un objeto `monacleclarity` desde un punto existente. `CodexWorld.CreateTreasure` y `CodexThing.SpawnTreasure` existen para tablas de tesoro.

En `EAST_28_1.nsd`, offset 9078, `otto` tiene posición `[1016,-54,0]`, orientación `[0,0,180]`, sector 108. Es un ejemplo de coordenadas originales; no demuestra proximidad a la entrada multijugador. La revisión del demo utiliza `near_player`, conservando el modo absoluto para autoría por coordenadas. El primer `ghost`, offset 84, está en `[1184,1660,114]`, sector 19: se usa como anchor del controlador. Los hints conservan ambos offsets.

`businessWoman` existe en `modernDay.not`, hereda `_civilians_MD` y referencia `businesswoman.nod`, `npcNyc3.nag` y `gothGirl.nms`. Su AI heredada es `ped.nai`; el script heredado es `Pedestrian`. Nuestro `.not` deriva una plantilla nueva y sustituye ese script por una clase propia pasiva, evitando heredar lógica narrativa o de peatón.

La API expone `SetModel`, flags de render/collision, escala, velocidad, attachments, frames, partículas, luces y efectos. Esos métodos manipulan entidades; no son un editor de la geometría NIL. `AddToActorInventory(int)` y las acciones de pickup/equip disponibles en las clases reales permiten gestionar objetos ya creados. No se generan inventarios en el esquema 1.

### 10. Entradas, salidas y desplazamiento

Los `.nsc` conectan índices, por ejemplo `exit WestLondon,2 EastLondon,0`. Los comentarios de `MP_RaveClub.nsc` documentan `CLOSED=0x1` y `ONEWAY=0x100` para filas de exit.

`CodexSequence` contiene `OpenExit(String,int)`, `CloseExit(String,int)`, `IsExitValid`, `IsExitClosed`, `ChangeExit(String,int,String,int)`, `TakeExit(int,int)`, `Jump(String,int)`, `PlayerJump(String,int,int)`, `SetPortalLocation(int,int)`, `SetReviveLocation(int,int)`, `CreateTeleporter(int,String,String,int,int)` y `ActivateTeleporter(int,int)`. `CodexPlayer.TeleportPartyToEntrance(int,int)` también existe. No hay que inventar métodos `LoadLevel`, `SetDoorDestination` o `SpawnNPC`.

`ClickExit` y derivados consumen parámetros de destino y llaman las funciones reales. Las puertas móviles pueden ser props con frames: existen `AllocateFrames`, `SetFramePosition`, `SetFrameOrientation`, `MoveToFrame` y `RotatePivot`. Una puerta que sea pared de la geometría no se transforma automáticamente en prop.

### 11–12. Triggers y callbacks

Callbacks encontrados tanto en scripts como en cadenas de registro de `Vampire.exe`:

| Callback real | Firma encontrada | Ejemplo |
|---|---|---|
| Inicio de escena | `beginscene(int,int)` | `EAST_28_4_Main`, `Pedestrian` |
| Creación | `created(int)` | `ClassSpiderSac` |
| Clic | `clicked(int,int,int)` | `EAST_Otto`, `CTD_LeComte` |
| Entrada/salida | `entered(int,int,int)`, `exited(int,int,int)` | scripts de regiones |
| Timer | `timer(int,float,float,float,float)` | `ClassSpiderSac`, escenas |
| Trigger explícito | `triggered(int,int,int,float,float,float,float,int)` | `triggerMult`, `ClassBreakable` |
| Conversación | `convreached(int,int,int,int,int)`, `convended(int,boolean,int)` | `WAR3_Main`, escenas |
| Persistencia | `save(int)`, `restore(int)`, `restored(int)` | múltiples clases |

`CaptureThing(guid[,captureID])` registra un receptor. Su wrapper pasa el GUID del script, el GUID de entidad y el capture ID al método nativo. `GetClassThing()` devuelve el thing asociado al script. Los scripts originales capturan actores y regiones en constructores, o reciben referencias por parámetros de escena.

`CodexThing.Trigger(int,int,float,float,float,float)` y `SetTimer` existen. `CodexRegion` expone flags; `CodexCollision` ofrece consultas de esfera, posición, segmentos y geometría. Las regiones de algunas escenas tienen bloques binarios variables; la firma de un callback no basta para conocer la construcción de todos esos volúmenes.

### 13–15. Conversaciones, respuestas y resultado Java

Los 310 `.nco` son texto. Se observan `CONVERSATION:`, `EVENT:`, `LINE:`, `ANSWERGOTO:`, `ANSWERRETURN:`, `DELAY:` y `JUMP:`. Una `LINE` referencia un ID de texto/voz y un Cast ID. Los textos pertenecen al `.nvo`: ID de línea, nombre del recurso de voz, texto. `.nls` es una tabla de ID y resto de línea para textos generales.

`36_1_BigAl.nco` tiene dos `ANSWERRETURN` con valores 1 y 2. `WAR3_Main.convended(int,boolean,int)` compara el **tercer parámetro** con 1 y elige otra conversación según la respuesta. `FLS3_LibussaHelp` hace lo mismo y modifica una puerta.

`Codex.ExecuteConversation(int,int,String,String[,int])` existe; los originales pasan ID de conversación y nombre de archivo. `CONV_XFLAG_WANTFEEDBACK = 4`, `CONV_XFLAG_ALLOWABORT = 8`. `convreached` se usa para elegir tomas de cámara por evento/línea.

El generador crea dos conversaciones propias. Cada una tiene dos respuestas con resultados explícitos. Los NCO, NVO y Cast IDs se validan entre sí. Se genera un WAV PCM silencioso propio para que el recurso de voz referenciado exista.

### 16–17. Chronicle Flags y persistencia

`CodexSequence.GetChronicleFlag(int)`, `SetChronicleFlag`, `ClearChronicleFlag`, `ToggleChronicleFlag` y `ClearAllChronicleFlags` están presentes. `EAST_28_4_Main.beginscene` comprueba flags y condiciona lógica de escena. Los flags son índices booleanos; no son strings ni el bitmask `flags` del archivo NSC.

`SaveInt`, `RestoreInt`, `SaveFloat`, `RestoreFloat`, `SaveBoolean`, `RestoreBoolean`, `SaveString`, `RestoreString` y `SaveGame` existen. Los scripts originales guardan campos en `save` y los restauran en el mismo orden en `restore`. La API incluye flags de entidad `SAVENEVER=1`, `SAVESUSPEND=2`, `SAVESETMODIFIED=4`, `SAVEALWAYS=8`.

Nuestro controlador guarda GUIDs y vuelve a capturar entidades existentes. No almacena el flag en una variable Java: usa el estado de la crónica. La conservación real de flags/GUIDs y el orden de callbacks del motor necesitan una prueba de save/load.

### 18. Quests

Los 45 `.nqd` examinados son texto. Ejemplo: `QUEST 0 0 Q_INFILTRATESETITE_S Q_INFILTRATESETITE_L QuestCheck.tga 5000`. El recurso referencia descripciones cortas/largas e icono. `CodexQuest.Load(String)` devuelve un entero usado en `new CodexQuest(id)`. Hay funciones para completar, pasos, flags de ítems y descripción. `MP_CTDChronicle.Step` carga quests, completa otras y modifica exits/flags. No se necesita un editor de quests para escribir este texto; el generador de quests queda fuera del esquema 1.

### 19. Cámaras

`CodexCamera.SetupCutscene(int,int,int)`, `SetShot(int,int,int,int,int,float)`, `Release(int)`, `SetupOneShot`, `ShotType`, `ShotAngle`, fades, flashes, filtros y `PlayPath(int,int,String,float)` aparecen en las clases reales. `EAST_28_4_Main.convreached` usa SetupCutscene y SetShot; `EAST_Otto` usa un `.ncp`.

El prototipo genera SetupCutscene/Release desde los callbacks de conversación. No genera paths `.ncp` ni un lenguaje de cámaras.

### 20. Audio

`CodexSound.StartMusic(String,int)`, `StopMusic`, `PushMusic`, `PopMusic`, `StartAmbient`, `StopAmbient`, controles de volumen, `PlayVoice(int,String,int)` y constructores para sonidos asociados a GUID o posición son reales. `EAST_28_4_Main` usa PushMusic/PopMusic. Los finales de los `.nsd` contienen nombres de música/ambiente.

El catálogo distingue 56 archivos de `Sounds/Music`, 48 de `Sounds/StereoAmbient` y recursos de voz, además de los WAV de los NOB. Las extensiones por sí solas no determinan su papel. El prototipo conserva el bloque de entorno de la escena de referencia, y genera silencio para el diálogo; no ofrece todavía acciones YAML de audio.

### 21–22. AI, actores y recursos instanciables

Los `.nai` contienen campos textuales de ataque, movimiento, distancias, wander, mind flags y disciplinas. `.npc` es una definición de jugador con stats, cash, experiencia, disciplinas e ítems; no es la plantilla genérica de un NPC. Las plantillas viven en `.not` y enlazan modelos, AI, motionsets, foley, scripts y otras propiedades.

`CodexActor` expone flags, equipo, salud, stats, velocidades, AI target/mode, acciones y efectos. El prototipo pausa la AI del NPC, le asigna equipo de peatones y habilita TALKTO, NEUTRAL y NOFEED. No pausa la AI global del mundo.

Los `.not` indexan actores, props, ítems, armas, armaduras, jugadores, proyectiles, contenedores y regiones. Eso proporciona candidatos a CreateThing. Un `.nod` aislado no reemplaza una plantilla ni asegura que todas las propiedades requeridas existan. La instanciación de cada familia y plantillas con scripts/constructores particulares no se considera automáticamente probada.

### 23. Generación directa alcanzada

Se generan `.nsc`, `.nmf`, `.nco`, `.nvo`, `.nls`, `.not`, un subconjunto `.nsd`, Java, `.class` 45.3, WAV y ZIP `.nob`. Los cuatro NOT originales se leen/reemiten byte a byte; 24 NSD originales también. No se genera el modelo `.nod` ni la geometría `.nil`.

### 24–25. Dependencias geométricas y uso del runtime

Los originales separan referencias NIL/NSD y muestran creación de contenido y cambios de escena desde Java. Existe base técnica para entidades, conversaciones, flags, quests, cámaras, audio, inventario, teletransportes y cambios de conexiones sobre un level existente.

La topología física, paredes/suelos, sectores, portales geométricos y visibilidad pertenecen a datos geométricos; no hay evidencia de un editor Java completo para ellos. Algunas regiones/props de NSD tienen datos geométricos propios, independientes de la malla NIL. El primer prototipo evita esos bloques.

## CONFIRMADO EN SDK/DOCUMENTACIÓN

No se ha localizado ni utilizado un SDK completo, fuentes `Codex*.java` o manual oficial de formatos en los archivos examinados. `Codex.dsp` y `__DocCodex.bat` hacen referencia a fuentes que no están en `Codex.nob`; no se atribuye a un SDK una función descubierta solo en bytecode.

La documentación primaria de Eclipse describe el compilador batch, classpath y bootclasspath: [Using the batch compiler](https://help.eclipse.org/latest/topic/org.eclipse.jdt.doc.user/tasks/task-using_batch_compiler.htm). La disponibilidad de ECJ 3.26.0 está publicada en [Maven Central](https://repo1.maven.org/maven2/org/eclipse/jdt/ecj/3.26.0/). El modo `-1.3` y la emisión 45.3 se comprobaron con el compilador descargado, y el resultado contra las clases originales está en `build/east_demo/compiler.log` y en las cabeceras generadas. Esta documentación acredita el compilador, no la semántica del motor.

## INFERIDO

- La colocación absoluta puede usar la API real CreateThing; aún falta comprobar collision y suelo en coordenadas arbitrarias. La creación junto al jugador y nuestra narrativa sobre el NIL reutilizado ya tienen confirmación del usuario.
- Los ángulos parecen ser grados: orientaciones originales 90, 180, 225 y 270, y yaw en componente 2. No se encontró una especificación oficial de unidades o sentido positivo. El YAML usa valores equivalentes a los archivos originales.
- El booleano de `convended` parece indicar aborto; `MON3_Main` evita un cambio cuando es true. El controlador lo trata como `aborted`. Hay que verificarlo en el motor.
- En el subconjunto simple, los últimos 192 bytes contienen 16 bytes de contadores globales vacíos y 176 de metadatos. El lector nativo confirma los dos campos finales de modelo/animación de fondo. Se copian los otros 112 bytes de metadatos; iluminación/niebla completas siguen pendientes.
- Las asociaciones adicionales desde NSS usan el orden de `location` para interpretar índices numéricos. Es razonable por los ejemplos, pero no está respaldado por un header del SDK.
- Las cadenas ordenadas de propiedades de `Vampire.exe`, contrastadas con valores de NOT originales, identifican tags como 0 parent, 1 orientation, 2 position, 3 sector, 11 script, 81 Cast ID y 82 Description ID. La asignación completa de todos los tags no se considera resuelta.
- La posición de Otto es un punto con evidencia de uso por un actor, no una garantía de collision para otro tamaño de actor.

## PENDIENTE DE VERIFICAR

1. Traducciones del título de entrada de la escena en el paquete reconstruido de Fase 2. El fondo gris original fue confirmado por el usuario; ya no se añade Sky.
2. Colocación absoluta, collision, ajuste al suelo, navegación y sentido/unidades angulares. La aparición próxima al jugador sí fue observada.
3. Save/load de Chronicle Flags y entidades; orden save/restore/restored/beginscene y ausencia de duplicados. Recordar elecciones en otra conversación no prueba cargar un save.
4. Aborto de diálogo y recuperación de interacción; cámara baja observada por el usuario.
5. Red: replicación de GUIDs, sincronización de decisiones y callbacks solo en servidor. El harness solo comprueba nuestra condición de cliente.
6. Triggers arbitrarios y todos los bloques variables de NSD; inventarios, quests, cámaras avanzadas, audio y entradas/salidas: API investigada, sin generador completo ni prueba nativa.
7. Todos los campos NIL y tags NOT; datos no indexados al final de Multiplayer.not.

El menú, nombre, mapa, carga de nuestro NSD/clases/NOT, creación de Victoria, interacción y decisiones tienen evidencia nativa del usuario. El agente no ha ejecutado el juego. El despliegue histórico de Fase 1 se limitó a RCM y no utilizó herramientas originales de autoría; el despliegue posterior de Fase 2 se documenta al final bajo su nueva autorización.

## Actualización de Fase 2 — 8 de octubre de 2026

### CONFIRMADO EN ARCHIVOS ORIGINALES

- `Resource.nob/conversations/12_1_Bill.nco` contiene `EVENT: ev_0`, `ANSWERGOTO ... ev_1`, `ANSWERRETURN ... 2` y `EVENT: ev_1`. Los destinos de GOTO son eventos del mismo NCO; el generador nuevo utiliza esos comandos, sin invocar un editor de conversación.
- La cabecera de `EAST_28_1.nsd` contiene `EAST_28_1S` en bytes 8..39 y `EAST_28_1L` en 40..71. `Local_Eng.nob/strings/london.nls` traduce esas mismas claves como `East London` y `Scene 28.1 - East London`. Son referencias localizables; no constituyen el nombre del script, almacenado en tag 11.
- Las clases reales ya documentadas ofrecen beginscene, clicked, convreached, convended, Get/Set/ClearChronicleFlag y ExecuteConversation. Las condiciones/eventos nuevos solo componen esas firmas existentes. Todas las clases producidas compilan contra el Codex original, con versión 45.3.
- EastLondon original no referencia Sky/LondonNightSky en los campos finales de su entorno. La demo conserva los 176 bytes originales, con CLEARBUFFER. Investigación de modelos y experimento descartado: `research/sky/FINDINGS.md`; no se necesita otra reparación del muelle.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

No aparece un nuevo SDK del juego ni especificación oficial completa de NCO/NSD. La autoría nueva se apoya en originales y bytecode, no en métodos supuestos.

La documentación oficial de [Qt for Python](https://doc.qt.io/qtforpython-6/gettingstarted.html) respalda PySide6 y la organización de la aplicación Qt. Esta documentación concierne al editor, no al comportamiento de Redemption. El guardado propio usa las primitivas de archivos de Python; no depende de un frontend antiguo.

### INFERIDO

Añadir al NLS propio las claves S/L generadas debe resolver el identificador que aparecía al entrar. La relación clave/traducción está confirmada en originales; el efecto visual de la corrección aún debe observarse en el paquete nuevo.

Los nodos se emiten con la entrada primero, como los ejemplos originales. La compilación y los cruces NCO/NVO/Cast ID no equivalen a ejecutar ANSWERGOTO en esta crónica. La selección del actor real recibido en convreached para líneas de otros speakers conserva el fallback al actor principal, pero requiere una prueba nativa con varios hablantes.

### PENDIENTE DE VERIFICAR

Bifurcaciones/GOTO nuevas, múltiples líneas/hablantes, coordenadas absolutas y su collision, eventos condicionados, título de entrada, abortos, persistencia tras save/load y red. El ensayo GUI y los 33 escenarios Java con doubles no prueban esos contratos nativos.

### PROBADO LOCALMENTE, SEPARADO DE EVIDENCIA NATIVA

64 tests pasan; 26 son la cobertura original. La crónica `editor_demo` fue creada y construida mediante controles reales del editor (QtTest), sin editar manualmente su YAML. GUI y CLI generan un ZIP idéntico por SHA-256. De los 11 archivos runtime de `east_demo`, solo cambia la tabla propia NLS con las etiquetas S/L; las clases y el NSD coinciden con el checkpoint.

Evidencia: `build/editor/acceptance/report.json`, capturas en ese directorio, `build/editor/phase2_verification.json`, `build/tests/test_report.json` y los dos harness logs. Se han vuelto a comparar las 43 fuentes originales y sus hashes coinciden. El agente no ha ejecutado Redemption. Tras la entrega inicial se actualizaron paquetes solo en RCM mediante la nueva autorización del usuario; este posteriormente confirmó la crónica funcionando.

### OBSERVADO POR EL USUARIO EN EL JUEGO — HISTÓRICO

Fase 1: aparición de la crónica y nombre correcto, geometría cargada, Victoria cerca del inicio, diálogo a pantalla completa, elecciones recordadas al volver a hablar y desaparición del halo. El fondo gris coincide con las referencias originales y el usuario lo considera adecuado. La cámara se percibe algo baja. Estos resultados no se atribuyen al paquete de aceptación de Fase 2.

## Aceptación nativa posterior de Fase 2

**OBSERVADO POR EL USUARIO:** la variante `editor_playtest` desplegada recibe la confirmación «Va perfecto». El usuario aclara que aún no ha probado el editor. Es aceptación general de la crónica, sin inventar un desglose de comprobaciones de persistencia, aborto o red.

**REGISTRO NATIVO:** `research/runtime_test/native_phase2_accepted.log` es copia del log generado por el juego en RCM/editor_playtest; contiene constructor, beginscene servidor/local y SpawnThingNear GUID=1073741889. Procedencia, hash y declaración del usuario: `phase2_native_acceptance.json`. No se mezcla con los logs del motor simulado.

**PROBADO LOCALMENTE:** revisión del editor para confirmar IDs pendientes al guardar/validar/build y refrescar inmediatamente filas de flags/destinos/condiciones. 64 tests y aceptación GUI completa pasan. El generador y los recursos nativos desplegados permanecen sin cambios.

**PENDIENTE:** ensayo personal del editor por el usuario, save/load, abortos y red, coordenadas absolutas y diálogos con varios hablantes. La aceptación general no prueba exhaustivamente todas esas capacidades.

## Actualización de Fase 3 — 8 de octubre de 2026

### CONFIRMADO EN ARCHIVOS ORIGINALES

- NIL v27: el lector nativo `Vampire.exe 0x4a9170`, contrastado con `0x4b2e80/0x4b3440`, consume encabezado, nombres de materiales, sectores, tablas XYZ, corners con UV, grupos/superficies, portales y cola por sector. Ventanas de instrucciones conservadas en `research/viewport/native_nil_reader.txt`. Nuestro lector no interpreta la cola global restante.
- EastLondon `Levels.nob/levels/l1_east.nil`: 131 sectores, 45.927 triángulos expandidos y 109 nombres de material; bounds [-5120,-4608,-80] a [4288,5824,1952]. El bloque leído termina en 3.096.883 de 5.586.623 bytes.
- Los nombres enlazan NAM con campos `texture`; agua usa `pass 0`. Bitmaps TGA y UV se leen directamente. Los NOD enlazan nombres de materiales que también resuelven `3d/Materials/<nombre>.tga`.
- NOD versión 7: rutinas `0x4c35d0/0x4c3ba0`; bones de 66 bytes, vértices de 40, índices por grupo de 6 y grupos de material de 28. `research/viewport/native_nod_reader.txt` y el lector documentan offsets. No se atribuye a este lector animación ni skinning.
- CodexThing.GetPosition, CodexPlayer.GetCurrentPlayer/GetNumMPPlayers/GetMPPlayer, SetTimer/KillTimer y SaveInt/RestoreInt son firmas originales. Los triggers propios componen esas APIs; compilan a 45.3 sin una función inventada de región.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

No se ha encontrado un SDK nuevo del juego ni una especificación oficial NIL/NOD. Los offsets proceden del ejecutable y los recursos originales.

Documentación oficial de [QOpenGLWidget](https://doc.qt.io/qt-6/qopenglwidget.html) y [ejemplo Qt OpenGL](https://doc.qt.io/qtforpython-6/examples/example_opengl_hellogl2.html) respaldan el contexto, shaders/buffers y la integración elegida. Esto acredita la biblioteca del editor, no un contrato nativo del juego.

### INFERIDO

- La triangulación en abanico presupone superficies convexas originales. Conteos e índices coinciden en los 112 NIL, pero no se demuestra aquí convexidad de cada polígono ni su equivalencia de colisión.
- Yaw usa una rotación matemática positiva en XY para dibujo/volúmenes. Orden de componentes confirmado; grados y sentido positivo siguen pendientes de contraste de nuestro actor absoluto en el motor.
- Las referencias NSD obtenidas por patrón son ayudas de inspección; pueden omitir elementos o producir coincidencias. No representan una lectura completa de puertas, regiones o spawn points.
- Un raycast sobre geometría visible proporciona un punto de autoría; no demuestra que el actor pueda caminar o caber allí en el runtime.

### PENDIENTE DE VERIFICAR

Triggers Java dentro de Redemption: entrada/salida, cajas rotadas, esfera, varios jugadores, condiciones, spawn diferido, retorno tras diálogo, once y restore. Posiciones absolutas, apoyo/collision y sentido de yaw. Save/load, abortos y replicación de las fases anteriores siguen pendientes de pruebas detalladas.

NIL global/BSP/lightmaps, NSD variable completo, NAD/skinning, multipass/transparencias equivalentes al renderer original y varias familias de formatos continúan fuera del codec implementado.

### PROBADO LOCALMENTE, SEPARADO DE EVIDENCIA NATIVA

84 tests pasan. Lectura estructural de 112/112 NIL y 1.476/1.476 NOD: `nil_scan.json`/`nod_scan.json`. Ventana Qt real: EastLondon, 109 materiales sin fallback, modelo Victoria, creación con clic, gizmos, triggers, relaciones, save/reopen y build; informe y capturas en `build/viewport/acceptance/`. Muestreo de navegación alrededor de 62 llamadas paintGL/s en esta máquina, no medida de presentación/GPU finalizada. Cache corrupto regenera sin alterar originales.

El harness adicional comprueba 11 escenarios de triggers con doubles; la compilación usa Codex real. La distribución de Fase 2 reconstruida sigue con SHA-256 `90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab`. Las 43 fuentes originales coinciden por hash. Preparar RCM no significa ejecutar el juego: no existe aceptación nativa nueva de Fase 3.

## Fase 4 — evidencia nueva

### CONFIRMADO EN ARCHIVOS ORIGINALES

CodexQuest.Load(String), Complete y wrappers de flags; CodexPlayer.AwardPlayerExperience; CodexActor.AddToActorInventory/GetActorFirstInventoryItem; CodexItem.GetNextInventoryItem/RemoveItemFromInventory; CodexThing.Remove/GetTemplateName/GetLocationNum; CodexSequence.Jump(String,int), Get/Set/ClearChronicleFlag y Save/RestoreBoolean/Int; CodexCamera.SetupCutscene/ShotType/ShotAngle/Release; CodexSound.StartMusic/StartAmbient/StopMusic/StopAmbient. Firmas y bytecode: research/phase4/api_and_original_bytecode.txt. MP_CTDChronicle reutiliza Load para cargar/completar quests. NUM_CHRONICLE_FLAGS=1024, MAX_QUESTS=64.

NQD originales usan QUEST y claves cortas/largas NLS, icono y recompensa numérica; existen recompensas cero. No se ha identificado aquí una gramática fiable de múltiples objetivos internos. NAI: 136 perfiles y referencias de templates inventariadas. NOT: cuatro bibliotecas comparadas con recodificación exacta; cada propiedad inspeccionada conserva su offset y bytes.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

No se ha encontrado una especificación adicional de NQD/NAI ni se atribuye la investigación propia a un SDK inexistente.

### INFERIDO

Alias nuevos de location deberían resolver Jump con la geometría original y entrada 0. NPC/enemigos heredan NAI, con team/pausa configurados. Los pasos NQD separados deberían aparecer en el journal conforme se cargan/completan. Compilar métodos/formatos observados no prueba estos resultados visuales.

### PENDIENTE DE VERIFICAR

Campaña completa de dos mapas: entradas, regreso, journal, recogida/entrega real del libro, combate/AI, muerte/corpse lifecycle, música, cámara y save/load. Los nuevos eventos de pickup/muerte/encounter son muestreo propio sobre APIs, no callbacks nativos inventados. Polling puede perder transiciones rápidas o cadáveres eliminados entre muestras; se evita declarar muerto un GUID inválido. Red completa sigue fuera de esta fase.

### PROBADO LOCALMENTE

Pruebas, aceptación Qt real, compilación 45.3, manifests y reporte: docs/PHASE4_REPORT.md. La evidencia histórica del usuario para Fases 1/2 permanece distinta; no confirma la nueva campaña.
# Estado de evidencia de Fase 6

**Confirmado en archivos originales:** las firmas de callbacks de guardado/restauración y la API usada por los generadores se contrastan con clases reales de Codex. Los catálogos incluyen recursos NOB y recursos sueltos (`archive: null`). Compilar contra esas clases no confirma por sí solo la semántica de ejecución.

**Confirmado mediante pruebas propias:** parsers, validadores, generación, compilación Java 45.3 y callbacks simulados tienen reportes en `build/tests/`. No pertenecen a la categoría «confirmado dentro del juego».

**Pendiente de verificar dentro de Redemption:** corrección actual de conversación rechazada/abortada, cámara y UI, callbacks save/load, NOT propio con AI, inventario, transiciones y repetición de escenas. El usuario aceptó la demo anterior y comunicó una regresión posterior; no se extiende aquella aceptación a esta versión. Véanse [RUNTIME_TEST_MATRIX.md](RUNTIME_TEST_MATRIX.md) y [RELEASE_BLOCKERS.md](RELEASE_BLOCKERS.md).

# Evidencia de Fase 7

### CONFIRMADO EN ARCHIVOS ORIGINALES

El lector NSD versión 8 del ejecutable copiado lee 176 bytes finales después de los bloques variables; los últimos 64 son referencias de modelo/animación de cielo. El orden/tamaños están en [SCENE_MODEL.md](SCENE_MODEL.md) y `research/user_directory/scene_runtime.txt`. El hash completo del original se verifica antes de reutilizar el tail. Los scripts originales documentan 45 llamadas literales consecutivas a `CodexSequence.ChangeScene(location, scene)`; evidencia con líneas en `research/phase7/codex_scene_links.json`.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

Se recuperaron copias archivadas del manual original de Embrace, NIL/NSC/NSL/NSS/NMF y API de cámara/secuencia/audio. Fuentes y hashes en `research/phase7/embrace/`. NIL describe geometría e iluminación; la estática NSD del mismo nombre se carga automáticamente. Las escenas adicionales tienen ajustes propios de sonido/render/cielo. NSL sólo sirve al editor. NSS describe entradas del panel Storyteller, con clave NLS y handler advance; sus índices no son posiciones de locations NSC. Sky depende también de superficies de geometría marcadas para ello. El manual distingue luces dinámicas de luces usadas sólo para lightmaps.

### INFERIDO

Los campos opacos del tail deben contener parte de las opciones Sound/Render documentadas; no se asignan nombres ni se editan por conjetura. No todos los cambios de iluminación o cielo pueden conseguirse con un NSD sobre geometría existente. Los scripts pueden aportar asociaciones de escenas adicionales, pero la extracción literal no cubre cálculos o selección dinámica.

### PENDIENTE DE VERIFICAR

La demo de tres escenas, recuperación de cursor/cámara, save/load, NOT/AI, inventario, reentrada y red en la versión 0.7.0. También entrada distinta de 0, sustitución de estática base, paths/regiones/audio espacial/luces propias y offsets individuales de entorno. No se ha obtenido ni ejecutado Embrace.exe; el contraste de sus funciones procede de su manual original.



## Ronda 0 — cámaras y layouts (0.9.2)

### CONFIRMADO EN ARCHIVOS ORIGINALES

API_SIGNATURES.txt contiene SetupCutscene, SetShot, Release, PlayPath y GetGUID. La plantilla Rat de Global.not usa Rat.nod/enemyGhoulRat.nai; scene_hints registra rat en SIM1_5_1 (detección de tags, no parse completo de esa escena). Rat se reutiliza sin modificar sus bytes originales.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

CodexCamera.htm documenta PlayPath(clientGuid, scriptGuid, pathName, speed) para paths precomputados y SetShot con lerpTime. Se usan esos métodos, sin API inventada.

### INFERIDO

Una única rata básica debería resultar más fácil que cuatro brujahFled_MD; no es una medición nativa de dificultad. Dejar el callback de diálogo sin SetupCutscene conserva la selección automática que haga el motor durante ExecuteConversation (sin NOAUTOBEGIN).

### PENDIENTE DE VERIFICAR

Diálogo automático vs presets, timeline, movimiento y restore de cutscene, PlayPath EASTOttoVan sobre EastLondon, multiplicidad de inventario y nuevo recorrido completo. Pruebas manuales aplazadas. No se ha creado un writer NCP ni puertas físicas completas.


## Ronda 0 — journal y cierre de diálogo (0.9.5)

### CONFIRMADO EN ARCHIVOS ORIGINALES

SetupCutscene llama a BeginCutscene interno (0x431e10 → 0x42f580). Release y EndCutscene convergen en 0x42f6d0, que devuelve cámara y controles. La limpieza nativa de conversación 0x458e40 retira recursos y al final borra su puntero global. Evidencia sobre la copia original, sin ejecutarla: research/round0/dialogue_journal_fix/native_methods.txt, native_lifecycle.txt y native_end_order.txt. Firmas: API_SIGNATURES.txt.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

CodexCamera.htm.txt describe entrar en modo cutscene y liberar controles. UNIV_7_7 en cutscene.htm.txt encadena conversaciones desde convended mediante SetTimer; no inicia la siguiente directamente. Se conserva este orden en formato 9.

### INFERIDO

Omitir SetupCutscene en cámara native conserva controles de juego: concuerda con el movimiento observado. La inferencia de 0.9.2 sobre omitir completamente SetupCutscene queda invalidada por la prueba del usuario. Reabrir diálogo dentro de convended puede interferir con la limpieza de su predecesor. Que compilen Release y el timer no prueba por sí solo que vuelva el cursor real.

### PENDIENTE DE VERIFICAR

Usuario confirma en 0.9.4 PNJ, journal y diálogo; falla caminar durante diálogo, Ayuda/Volver y recuperación de HUD/cursor. Se corrige en 0.9.5 con entrada en cutscene automática y cierre/acciones diferidos. Los pasos NQD se cargan sin duplicar la ficha general; aceptar completa la guía inicial y revela la lección. Las regresiones Java modelan callback, limpieza posterior, abortos, fallos, dobles cierres, resultados sin duplicación y restore. Falta confirmar visualmente la revisión nueva dentro de Redemption con partida nueva. PATH_FAILED route=0 sigue siendo evidencia de recorrido pendiente, no aceptación nativa.

## Ronda 0 — cutscene y layout visible (0.9.6)

### CONFIRMADO EN ARCHIVOS ORIGINALES

Los scripts compilados de `MP_LeavesThree` usan `BeginCutscene`/`EndCutscene` junto con `AIOff`/`AIOn` para secuencias con movimiento y cámara. Su documentación enumera los planos y distancias disponibles. La evidencia copiada está en `research/phase7/embrace/cutscene.htm.txt` y `research/round0/cutscene_layout_fix/MP_LeavesThree_bytecode.txt`.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

La API declara `Codex.BeginCutscene(int,int)`, `Codex.EndCutscene(int,int)`, `Codex.AIOff()` y `Codex.AIOn()`. Los presets nuevos del editor sólo emiten las constantes documentadas `CAM_SHOT_*`, `CAM_ANGLE_*` y `CAM_DIST_*`.

### INFERIDO

La causa más probable de que mover el ratón sacara al usuario de una cutscene era iniciar sólo la cámara sin reclamar el modo de cutscene. La timeline propia reclama ahora ese modo y lo libera por duración. La orden de movimiento acepta el primer waypoint si el actor ya está dentro de su tolerancia; así no confunde una posición inicial válida con un fallo del pathfinder.

### PENDIENTE DE VERIFICAR

La revisión 0.9.6 necesita una partida nueva para confirmar visualmente el bloqueo del ratón/HUD, los tres planos de `walk_scene`, el fin limpio de la secuencia y el mensaje de llegada al layout `combat`. El travelling NCP original continúa siendo experimental.
### Investigación de crash LAN — diagnóstico mediante volcados (09/10/2026)

#### CONFIRMADO EN ARCHIVOS ORIGINALES

Cuatro volcados de Windows de Vampire.exe fallan en la misma dirección
`0x004a7a40`, con EAX=0: `mov [eax+0x224],edi`. El motor intenta escribir
en un objeto nulo durante la restauración del inventario/equipamiento de un
actor. La pila contiene `0x0048a415`, retorno del cargador de perfil de jugador.
La copia desensamblada del ejecutable tiene el mismo SHA256 que la instalada.

El perfil `Crypt/npf000000.npf`, leído y copiado al workspace sin modificarlo,
contiene `r_rcm_tutor_s0_reward` como plantilla de un objeto en el offset 908.
El cargador base de objetos busca la plantilla antes de continuar leyendo el
registro (`0x4a540d`); si falta, retorna fallo antes de consumirlo completo.
El cargador de inventario no verifica el retorno nulo en la instrucción del crash.

Al arrancar, el motor carga global/medieval/modernDay/multiplayer y las NOT
cuyo nombre comienza por `_` (`0x4dce68`). Antes de la reparación, las cuatro
NOT propias de la demo no tenían ese prefijo: se cargaban únicamente desde
el NMF de la crónica. El cargador de NOT conserva una tabla por nombre de
biblioteca y evita cargarla dos veces (`0x4dcf7e–0x4dcf88`).

Evidencia: `research/runtime_test/lan_crash/`: dump_analysis.json,
executable_identity.json, desensamblados y startup_repair.json.

#### CONFIRMADO EN SDK/DOCUMENTACIÓN

No se añade una API Java ni se atribuye esta reparación al SDK. La evidencia
es el ejecutable real y los datos del personaje; las herramientas originales
de autoría no se ejecutan.

#### INFERIDO

La plantilla de recompensa ausente al restaurar el personaje es la causa
que mejor explica los cuatro crashes: la lectura falla a mitad de un objeto,
se desajusta la lectura posterior y el motor no comprueba el puntero nulo.
Esto explica que ni revertir Java/recursos ni retirar carpetas vacías lo
solucionara: el objeto ya estaba persistido en el perfil del jugador.
El usuario confirmó posteriormente «Funciona», tras la reparación instalada.
La aceptación se conserva en research/runtime_test/lan_crash/native_acceptance.json.

Se retira la hipótesis de un límite de 640 bytes en NLS/NVO, y su validación
arbitraria: no había evidencia de ese límite en el motor. Tampoco se conserva
la hipótesis de las carpetas vacías como causa. El historial de aislamiento
queda marcado como superado por este análisis.

#### PENDIENTE DE VERIFICAR

La reparación instalada cambia sólo los nombres de las cuatro NOT propias
para permitir su carga inicial y las líneas NOT de los NMF que las referencian.
Conserva cada byte de las plantillas y del resto de recursos, y todas las clases
Java previas. El perfil del jugador permanece idéntico. Está respaldada antes
de reemplazarse dentro de RCM. El generador y el validador de salida incorporan
el contrato de carga inicial para futuras crónicas.

El usuario ha confirmado la recuperación del acceso LAN. Inventario, guardado
y reapertura siguen requiriendo verificación específica. Eliminar una
crónica con objetos propios persistidos puede volver a dejar referencias sin
resolver: ese ciclo de desinstalación necesita conservar sus bibliotecas o un
procedimiento de migración del personaje expresamente autorizado.


## Tutorial guiado, interlocutores y secuencias — 09/10/2026

### CONFIRMADO EN ARCHIVOS ORIGINALES

MP_LeavesThree gira personajes con `LookAtThing` y usa `SetupCutscene` con
tercer argumento 0; ver research/round0/cutscene_layout_fix/MP_LeavesThree_bytecode.txt.
La clase original usa tanto `Jump` como `ChangeScene`. La API extraída contiene
LookAtThing, StopActorMotion, PlayActorMotionSetMode y MOTION_IDLE=49.

### CONFIRMADO EN SDK/DOCUMENTACIÓN

research/phase7/embrace/cutscene.htm.txt documenta actores, línea de acción y
SetShot. Los scripts del SDK muestran LookAtThing, SendActorToPos, AIOff,
liberación diferida de cámara y selección del NSD con ChangeScene.
Se estudian como evidencia; no se ejecutan herramientas originales de autoría.

### INFERIDO

Usar al jugador también como tercer actor de la cámara automática explica el
encuadre central extraño. El giro recíproco y el tercer argumento 0 reproducen
patrones originales, sin garantizar que todos los diálogos originales giren
siempre a ambos actores. Dejar el actor en idle al terminar el recorrido debería
eliminar la pose estática observada; su apariencia aún requiere ensayo nativo.

### PENDIENTE DE VERIFICAR

La revisión 0.9.8 está compilada contra Codex. Los recorridos completos y de
omisión se verifican con doubles, incluidos clics durante la película, avance
del paseo, selección de NSD y journal secuencial. Falta observar en Redemption
el encuadre automático/primer plano, animación final, bloqueo de movimiento de
cámara durante la película, desaparición del barril y aparición de la rata.
Detalles, instrucciones y límites: docs/GUIDED_TUTORIAL_FIX.md.


## Conversación y animación — revisión 0.9.9

El usuario informó que los dos interlocutores entraban en pose en T tras la
revisión 0.9.8. La llamada StopActorMotion añadida al giro se retira: la tabla
nativa y el desensamblado confirman que borra campos del controlador de motion.
Se usa StopActorAction antes de iniciar el diálogo, como en un ejemplo original
del SDK, y se conserva la animación al cambiar de línea. La cámara predeterminada
pasa a sobre el hombro; Vera enseña los trece encuadres al pulsar Siguiente.
La evidencia original, la inferencia causal y la comprobación visual pendiente
se separan en docs/DIALOGUE_MOTION_CAMERA_FIX.md. No se declara ya verificado
nativamente el retorno a reposo que se propuso en 0.9.8.


## Revisión 0.9.10 — MP_CTD, cola de timers y llave física

### CONFIRMADO EN ARCHIVOS ORIGINALES

SetTimer añade entradas incluso con el mismo ID; KillTimer retira las del script/ID. BoneKey hereda tipo 7 y la inserción nativa consume ese tipo en vez de conservarlo en la cuadrícula. CTD_Oubliette_Main y CTD_LeComte controlan cámaras y movimiento desde feedback; CTD_ChamberSkulls abre una puerta con RotatePivot y flags. Evidencia detallada: CTD_CINEMA_INVENTORY_FIX.md y research/round0/ctd_cinema_fix/.

### OBSERVADO POR EL USUARIO

La 0.9.9 mejora los encuadres y las animaciones de los interlocutores; queda una pose rara de Otto. La película finaliza antes de lo esperado, la llave no se ve en inventario y el laboratorio es inaccesible. La 0.9.10 corrige esas causas y cambia Otto por Anezka; aún no ha recibido una comprobación visual.

### INFERIDO Y PENDIENTE

La cola duplicada explica el final prematuro y el tipo 7 la desaparición de la llave. Se simula ahora la cola real y se verifica la presencia del objeto tras insertarlo. La apariencia, colisión, guardado y comportamiento visual nuevos necesitan ensayo nativo.

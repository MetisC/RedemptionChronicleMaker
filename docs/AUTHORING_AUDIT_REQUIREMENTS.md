REDEMPTION CHRONICLE MAKER
AUDITORÍA COMPLEMENTARIA DE MADUREZ Y HUECOS REALES DE AUTORÍA

Este prompt NO sustituye tu roadmap actual ni invalida el trabajo que ya estés realizando.

Debes SUMAR esta auditoría a tus objetivos actuales.

Primero inspecciona el estado ACTUAL del proyecto y determina cuáles de las preocupaciones descritas aquí:

- ya están completamente resueltas;
- están parcialmente resueltas;
- siguen pendientes;
- han quedado obsoletas por cambios posteriores;
- requieren prueba real dentro de Vampire: The Masquerade — Redemption.

NO reimplementes algo que ya funcione correctamente.

NO des por válida una preocupación de este prompt si el código actual demuestra que ya ha sido resuelta.

El objetivo es cerrar huecos reales para convertir Redemption Chronicle Maker en un auténtico:

AURORA TOOLSET PARA VAMPIRE: THE MASQUERADE — REDEMPTION

Es decir:

una herramienta con la que un diseñador pueda crear una crónica COMPLETA de forma cómoda utilizando escenarios existentes, sin herramientas originales de autoría y sin tener que conocer formatos internos, Java o detalles arcanos del motor.

============================================================
PRINCIPIO CENTRAL
============================================================

NO queremos editar geometría.

NO queremos crear un mini Blender.

NO queremos sustituir el renderer ni crear levels desde cero.

La geometría original actúa como escenario base.

Queremos poder controlar de manera moderna TODO lo necesario para construir aventuras completas sobre esa geometría:

- actores;
- NPC;
- enemigos;
- objetos;
- props;
- puertas;
- entradas;
- salidas;
- transiciones;
- triggers;
- regions;
- waypoints;
- paths;
- conversaciones;
- quests;
- eventos;
- condiciones;
- flags;
- inventario;
- encuentros;
- IA;
- cámaras;
- secuencias;
- música;
- sonidos;
- estado persistente;
- templates;
- build;
- deploy;
- playtest;
- debugging.

============================================================
1. AUDITORÍA PREVIA OBLIGATORIA
============================================================

Antes de cambiar código:

1. Leer el estado actual completo del proyecto.
2. Leer los informes de todas las fases disponibles.
3. Leer:
   - FEATURE_MATRIX
   - FEATURE_GAPS
   - KNOWN_ISSUES
   - RELEASE_BLOCKERS
   - RUNTIME_TEST_MATRIX
   - ENGINE_NOTES
   - FORMAT_NOTES
4. Ejecutar tests.
5. Ejecutar Golden/System Test projects.
6. Identificar qué puntos de esta auditoría siguen siendo reales.

Crear o actualizar:

docs/AUTHORING_GAP_AUDIT.md

con:

RESOLVED
PARTIAL
OPEN
RUNTIME VERIFICATION REQUIRED
NOT RELEVANT ANYMORE

============================================================
2. DISTINGUIR SIEMPRE TRES NIVELES DE ÉXITO
============================================================

Nunca mezclar:

GENERATED
COMPILED
RUNTIME VERIFIED

Una función que:

- genera archivos;
- compila Java;
- produce un build;

NO debe considerarse automáticamente compatible con Redemption.

La compatibilidad real la decide el runtime.

Mantener esta distinción en documentación, tests y Feature Matrix.

============================================================
3. PRIORIDAD ABSOLUTA: RUNTIME REAL
============================================================

La principal preocupación ya no debe ser únicamente:

"¿El código Python funciona?"

sino:

"¿Redemption hace realmente lo que esperamos?"

Crear o ampliar una suite de pruebas reales dentro del juego.

Debe cubrir especialmente:

- conversaciones;
- cámaras;
- decisiones;
- Chronicle Flags;
- quests;
- items;
- actores;
- custom templates;
- AI;
- transitions;
- triggers;
- encuentros;
- save/load;
- reentrada en levels;
- ejecución repetida de eventos.

============================================================
4. DIÁLOGO / CÁMARA / UI
============================================================

Verificar específicamente cualquier problema conocido relacionado con:

- aceptar diálogo;
- rechazar diálogo;
- abortar diálogo;
- terminar conversación;
- volver a hablar;
- cursores;
- recuperación de UI;
- cámara;
- Release Camera;
- control del jugador.

Crear una matriz de casos.

Ejemplo:

START CONVERSATION
→ choose answer
→ end normally
→ player regains control
→ cursor/UI correct
→ camera restored

ABORT
→ same guarantees

REPEAT CONVERSATION
→ no stale state

Si existen bugs conocidos corregidos sólo offline:

probarlos dentro de Redemption.

============================================================
5. SAVE / LOAD / PERSISTENCIA
============================================================

Ésta es una prioridad CRÍTICA.

Crear pruebas reales:

PLAY
→ alter state
→ SAVE GAME
→ EXIT
→ START GAME
→ LOAD
→ VERIFY

Comprobar al menos:

- Chronicle Flags;
- quest state;
- quest step;
- conversation consequences;
- items;
- inventory;
- rewards;
- encounters completed;
- actors when relevant;
- dynamic GUID/state mapping;
- scene/world state.

============================================================
6. IDEMPOTENCIA
============================================================

Una crónica real debe sobrevivir a:

- cargar partida;
- entrar/salir de level;
- volver a entrar;
- hablar dos veces;
- cargar varias veces.

Verificar que no ocurre:

- NPC duplicado;
- item duplicado;
- recompensa duplicada;
- XP duplicada;
- encounter repetido cuando no corresponde;
- quest reiniciada;
- trigger once ejecutado de nuevo;
- conversación inicial relanzada incorrectamente.

Introducir helpers/patrones seguros cuando sea útil.

============================================================
7. REENTRADA DE LEVELS
============================================================

Crear pruebas específicas:

Level A
→ Level B
→ Level A
→ Level B
→ Level A

Verificar:

- actores;
- flags;
- objetos;
- quests;
- exits;
- encuentros;
- triggers;
- música;
- estado.

Una campaña no puede asumir que un level sólo se visita una vez.

============================================================
8. PLAYER START / ENTRADAS
============================================================

Investigar exhaustivamente cómo determina Redemption:

- posición inicial;
- orientación inicial;
- entrada al cambiar de location;
- entradas múltiples a una misma location;
- revive location;
- portal location;
- exits originales.

Queremos una herramienta moderna que permita definir visualmente:

ENTRY POINT:
EastStreet

posición
orientación

ENTRY POINT:
SewerEntrance

posición
orientación

y después:

Exit A
→ WestLondon.EastStreet

Exit B
→ WestLondon.SewerEntrance

Esto NO es edición de geometría.

Es authoring de crónica y debe considerarse función importante para 1.0 si el runtime lo permite.

============================================================
9. ENTRY POINTS VISUALES
============================================================

Si técnicamente es posible:

representar entry points en viewport.

Debe poder:

- crear;
- mover;
- rotar;
- renombrar;
- seleccionar como destino de transición.

No exigir coordenadas manuales.

============================================================
10. PUERTAS / EXITS
============================================================

Auditar seriamente soporte de puertas y exits.

Investigar recursos y API reales relacionados con:

- Door;
- PivotDoor;
- Quick Doors;
- exits;
- portals;
- activation;
- open;
- close;
- lock;
- unlock;
- interaction.

Queremos poder utilizar puertas EXISTENTES sin modificar geometría.

============================================================
11. DOOR AUTHORING
============================================================

Objetivo de UX cuando el motor lo permita:

Seleccionar puerta existente.

Properties:

ID
Initial State
Locked
Required Item
Required Flag
On Open
On Close
On Use
Destination

Actions:

Open Door
Close Door
Lock Door
Unlock Door

No inventar propiedades que el motor no soporte.

============================================================
12. EXITS / TRANSITIONS
============================================================

Un diseñador debe poder conectar locations visualmente sin conocer:

ChangeScene
TakeExit
Jump
PlayerJump
portal internals

La GUI debe convertir conceptos humanos:

FROM:
EastLondon.WarehouseDoor

TO:
Warehouse.FrontDoor

en las operaciones reales necesarias.

============================================================
13. STATIC SCENE CONTENT
============================================================

Investigar una cuestión crítica:

Cuando reutilizamos un level original:

¿qué parte del contenido original viene ligada a:

- geometría;
- .NIL;
- static scene;
- .NSD;
- otro recurso?

Queremos entender hasta qué punto podemos reutilizar:

GEOMETRY ONLY

frente a:

GEOMETRY + ORIGINAL STATIC CONTENT

============================================================
14. CONTROL DE CONTENIDO ORIGINAL
============================================================

Objetivo deseable:

Scene Profile:

Original Geometry:
YES

Original Static Entities:
ALL / NONE / SELECTIVE

Chronicle Entities:
YES

No implementar una opción ficticia.

Primero demostrar qué controla realmente cada formato/runtime.

Si eliminar static entities concretas requiere generar una scene propia:

investigar y documentar esa vía.

============================================================
15. DIFERENCIAR GEOMETRÍA Y DECORACIÓN
============================================================

No considerar automáticamente "original" todo lo visible.

Clasificar cuando sea posible:

IMMUTABLE GEOMETRY

versus:

STATIC ENTITY / PROP

versus:

DYNAMIC ACTOR

versus:

SCENE CONFIGURATION

Esto puede permitir reutilizar un mismo escenario para épocas/contextos completamente diferentes.

============================================================
16. PATHS / WAYPOINTS
============================================================

Esto es una capacidad importante para un Aurora Toolset.

Investigar:

- path corners;
- waypoints;
- SendActorToPos;
- arrived();
- movement callbacks;
- original patrol scripts;
- interest spots;
- navigation helpers.

Objetivo:

Add Waypoint
→ click en viewport

Crear:

PatrolPath

Waypoint01
→ Waypoint02
→ Waypoint03

Assign to Actor:
Guard01

============================================================
17. PATH UX
============================================================

Implementar sólo si existe una traducción fiable al runtime.

La edición debería permitir:

- crear waypoint;
- moverlo;
- insertar;
- borrar;
- reordenar;
- loop;
- reverse;
- visualizar paths.

No crear navmesh ni sistema de pathfinding nuevo.

============================================================
18. MOVIMIENTO SCRIPTADO
============================================================

Autoría fácil para:

Move Actor To
Follow Actor
Guard Position
Patrol
Flee To
Walk To

cuando puedan generarse mediante API real.

============================================================
19. IA: EVITAR SOBREINGENIERÍA
============================================================

No necesitamos un Behavior Tree editor gigantesco.

Priorizar presets útiles de diseño:

Civilian
Passive NPC
Guard
Patrol Guard
Aggressive Melee
Aggressive Ranged
Follower
Scripted NPC

Cada preset debe mapearse a comportamiento real del motor.

============================================================
20. AI ADVANCED
============================================================

Usuarios avanzados pueden editar propiedades reales de .nai.

Pero la experiencia normal debe hablar lenguaje humano.

Ejemplo:

Detection Range
Chase Distance
Preferred Attack
Wander

No:

byte field 14
flags 0x20

salvo modo Advanced.

============================================================
21. SONIDO ESPACIAL
============================================================

Investigar si Redemption permite sonidos colocados espacialmente.

Si existe:

- position;
- radius;
- falloff;
- looping;
- ambient source;

añadir representación en viewport.

Ejemplo:

Add Ambient Sound
→ click
→ radius sphere

============================================================
22. ENVIRONMENT AUTHORING
============================================================

Auditar capacidades realmente útiles:

- weather;
- ambient audio;
- music;
- fog si está controlable;
- environment profile;
- scene audio.

Separar:

runtime-controllable

de:

geometry/lightmap-dependent.

No intentar reproducir renderer.

============================================================
23. CÁMARAS Y DIÁLOGOS
============================================================

La cámara debe evolucionar hacia una herramienta narrativa cómoda.

No necesitamos Premiere.

Sí queremos poder configurar:

Speaker Close
Listener Close
OTS Speaker
OTS Listener
Two Shot
Medium
Full

mediante presets que generan valores reales de CodexCamera.

============================================================
24. CREATE CAMERA FROM VIEW
============================================================

Muy importante para UX.

Flujo:

navego el viewport
→ encuentro encuadre
→ Create Camera From View

y también:

Align View To Camera

Esto convierte la cámara en una herramienta usable.

============================================================
25. CONVERSATION PRESENTATION
============================================================

Cuando sea posible:

Conversation Line:

Speaker
Text
Camera
Motion
Optional Event

No obligar a configurar presentación manualmente para cada línea.

Debe existir Auto Camera razonable.

============================================================
26. STATIC / ORIGINAL ENTITY INSPECTOR
============================================================

Cuando seleccionemos un elemento original:

mostrar:

resource/template
source scene
type
references known
editable: NO/limited

Si puede sustituirse u ocultarse mediante scene override:

mostrar esa opción.

============================================================
27. CUSTOM `.NOT` RUNTIME VERIFICATION
============================================================

El soporte `.NOT` NO está terminado porque:

read/write/roundtrip funciona.

Debe existir prueba real:

Clone original template
→ new project template
→ change obvious supported property
→ build
→ deploy
→ spawn
→ run Redemption

Verificar:

- game does not crash;
- template is found;
- model correct;
- actor exists;
- properties expected;
- script/AI works.

============================================================
28. `.NOT` FAILURE SAFETY
============================================================

Si un custom template es inválido:

Build debería detectarlo cuando sea posible.

No sobrescribir originales.

No publicar automáticamente writer como stable si únicamente funciona en fixtures.

============================================================
29. PORTABLE / CLEAN MACHINE
============================================================

Una prueba importante para 1.0:

copiar aplicación portable a entorno limpio.

Sin:

- Python instalado;
- repo;
- herramientas de desarrollo;
- SDK original.

Sólo:

RCM
+
instalación normal de Redemption.

Debe:

- arrancar;
- detectar/seleccionar juego;
- generar cache;
- abrir proyecto;
- build;
- deploy.

============================================================
30. DEPENDENCIA DEL SDK
============================================================

Auditar si todavía necesitamos alguna herramienta antigua del SDK en runtime/build.

Objetivo:

ninguna herramienta de autoría antigua.

Si todavía dependemos de un compilador Java original u otro componente técnico:

determinar:

- por qué;
- licencia/distribución;
- si podemos sustituirlo modernamente;
- si se puede empaquetar legal/técnicamente.

Diferenciar:

TOOLCHAIN TECHNICAL DEPENDENCY

de:

AUTHORING TOOL DEPENDENCY.

La prohibición absoluta se refiere al workflow de autoría.

============================================================
31. JAVA COMPILATION
============================================================

Verificar que el pipeline moderno produce siempre bytecode compatible.

Añadir test que inspeccione:

major/minor version.

Esperado:

Java 1.1 compatible / bytecode 45.x según lo confirmado.

============================================================
32. LARGE CHRONICLE JAVA LIMITS
============================================================

Investigar límites reales del Java antiguo:

- method size;
- constant pool;
- class size;
- generated switch/if chains.

Generar stress projects.

Si una crónica grande puede superar límites:

dividir código generado automáticamente en múltiples classes/scripts.

============================================================
33. REPEATED BUILD / DEPLOY
============================================================

Probar:

Build
Deploy
Run

editar

Build
Deploy
Run

repetido muchas veces.

No dejar:

- stale files;
- obsolete classes;
- duplicated resources;
- old package remnants.

============================================================
34. CLEAN DEPLOY
============================================================

Deploy debe conocer exactamente qué archivos pertenecen al proyecto.

Cuando un recurso deja de existir:

debe poder retirar su versión anterior si RCM fue quien la desplegó.

No borrar assets ajenos.

============================================================
35. RUNTIME EVENT TRACE
============================================================

Si existe instrumentación:

hacerla realmente útil.

Ejemplo:

SceneStart EastLondon
Spawn Victoria
Trigger Warehouse entered
Quest MissingGhoul 1 → 2
SetFlag warehouse_started
Conversation victoria_intro return=2
OpenExit warehouse_exit

Esto es oro para debugging.

============================================================
36. TRACE MAPPING
============================================================

Cada entrada debe poder relacionarse con:

entity ID
event ID
action index
quest step

cuando exista información.

============================================================
37. SAVE/LOAD DEBUG TRACE
============================================================

Registrar cuando sea posible:

SAVE STATE
RESTORE STATE

Flags restored:
...

Quest states:
...

Script-local state:
...

Esto ayudará a investigar persistencia.

============================================================
38. SYSTEM TEST CHRONICLE
============================================================

Ampliar RCM_SystemTest para cubrir explícitamente estos huecos.

Debe incluir estaciones/pruebas:

ENTRY POINT
DOOR
EXIT
PATH
SAVE/LOAD
REENTRY
STATIC CONTENT
CUSTOM TEMPLATE
DIALOG ABORT
CAMERA
SPATIAL AUDIO
AI PRESET

cuando cada capacidad exista.

============================================================
39. GOLDEN CHRONICLE
============================================================

GoldenChronicle debe comportarse como una pequeña aventura real, no únicamente una batería técnica.

Debe servir para comprobar interacción entre sistemas.

============================================================
40. MANUAL RUNTIME CHECKLIST
============================================================

Actualizar RUNTIME_TEST_MATRIX con casos explícitos:

Dialog normal
Dialog abort
Dialog repeat
Save/load flags
Save/load quests
Save/load inventory
Save/load encounters
Level reentry
Entry A
Entry B
Door locked
Door unlocked
Path
Custom actor template
Camera restore
Music restore
Trigger once
Trigger repeatable

============================================================
41. PRIORIDADES
============================================================

Si hay demasiado trabajo, utilizar este orden:

P0

1. Dialog/camera/UI runtime correctness.
2. Save/load persistence.
3. Reentry/idempotence.
4. Custom `.NOT` runtime verification.

P1

5. Player starts / entry points.
6. Doors / exits / transitions.
7. Static scene content control.
8. Paths / waypoints.
9. Portable clean-machine test.

P2

10. Spatial audio.
11. Environment authoring.
12. Camera authoring improvements.
13. AI presets.

P3

14. Multiplayer authoring parity.
15. Secondary polish.

============================================================
42. MULTIPLAYER
============================================================

Multiplayer sigue siendo valioso, pero NO debe bloquear una primera versión sólida orientada a crear crónicas.

No priorizar multiplayer por encima de:

- persistence;
- player starts;
- doors;
- transitions;
- paths;
- runtime stability.

Si ya está implementado correctamente, conservarlo y probarlo.

============================================================
43. AURORA AUTHORING CHECKLIST
============================================================

Crear:

docs/AURORA_PARITY_CHECKLIST.md

No se refiere a feature parity exacta con Neverwinter Nights.

Se refiere a la EXPERIENCIA DE AUTORÍA.

Preguntas:

¿Puedo crear una campaña?

¿Puedo añadir múltiples areas?

¿Puedo elegir cómo entra el jugador?

¿Puedo conectar areas?

¿Puedo colocar NPC?

¿Puedo colocar enemigos?

¿Puedo hacer patrullas?

¿Puedo hacer puertas?

¿Puedo hacer triggers?

¿Puedo crear quests?

¿Puedo crear conversaciones?

¿Puedo condicionar conversaciones?

¿Puedo dar objetos?

¿Puedo hacer comerciantes si Redemption lo soporta?

¿Puedo hacer encuentros?

¿Puedo controlar música/ambiente?

¿Puedo crear cinemáticas?

¿Puedo guardar/cargar correctamente?

¿Puedo volver a un area?

¿Puedo depurar?

¿Puedo Build + Play?

Cada respuesta debe ser:

YES
PARTIAL
NO
NOT SUPPORTED BY ENGINE

============================================================
44. DIFERENCIAR LIMITACIÓN DEL EDITOR Y DEL MOTOR
============================================================

Muy importante.

Cuando algo no pueda hacerse:

determinar si es:

RCM LIMITATION

o:

REDEMPTION ENGINE LIMITATION.

Documentarlo.

No perseguir durante semanas una función que el motor sencillamente no puede hacer.

============================================================
45. ENGINE CAPABILITY AUDIT
============================================================

Volver a revisar Codex.nob y scripts originales buscando capacidades de AUTHORING todavía no expuestas.

No buscamos cualquier función.

Buscamos funciones útiles para construir aventuras.

Clasificar descubrimientos:

CRITICAL AUTHORING
USEFUL AUTHORING
ADVANCED
IRRELEVANT

============================================================
46. CAPABILITY → EDITOR MAPPING
============================================================

Para cada capacidad útil:

ENGINE CAPABILITY
↓
CURRENT RCM SUPPORT
↓
GUI SUPPORT
↓
VALIDATION
↓
BUILD
↓
RUNTIME TEST

Esto debe permitir descubrir huecos reales.

============================================================
47. NO FEATURE BINGO
============================================================

No añadir una función únicamente porque Codex exponga un método.

Pregunta siempre:

"¿Ayuda a construir una crónica?"

Si no:

no es prioridad.

============================================================
48. UX FINAL DE AUTHORING
============================================================

La experiencia objetivo debe ser:

NEW CHRONICLE

ADD AREA
→ East London

SET PLAYER ENTRY
→ click

ADD NPC
→ choose template
→ click

ADD CONVERSATION
→ graph/tree

ADD QUEST

ADD DOOR TRANSITION

ADD TRIGGER
→ draw volume

ADD ENCOUNTER

ADD PATH
→ clicks

ADD CAMERA

VALIDATE

BUILD

PLAY

No:

edit YAML
edit Java
remember coordinates
remember resource IDs
call SDK tool

============================================================
49. YAML COMO ESCAPE HATCH
============================================================

El formato textual continúa siendo importante.

Pero no debe ser requisito para uso normal.

Un diseñador debe poder crear toda la Golden Chronicle desde GUI.

============================================================
50. ADVANCED MODE
============================================================

Mantener acceso para usuarios técnicos:

- internal IDs;
- raw resources;
- generated files;
- custom Java;
- raw template properties.

Pero separar claramente del flujo normal.

============================================================
51. PRUEBA "USUARIO DE 2000"
============================================================

Realizar un test manual conceptual:

imagina un usuario que jugó Redemption hace décadas pero no conoce su SDK.

Debe poder entender:

Area
NPC
Conversation
Quest
Trigger
Door
Encounter
Path
Build
Play

sin conocer:

NIL
NSD
NCO
NMF
NQD
NOT
NOB
CodexActor

============================================================
52. DOCUMENTACIÓN ORIENTADA AL DISEÑADOR
============================================================

EDITOR_GUIDE debe hablar lenguaje de aventuras.

Ejemplo:

"To create a locked door..."

No:

"Call CodexSequence.CloseExit..."

La documentación técnica seguirá existiendo separadamente.

============================================================
53. PRUEBA DE CRÓNICA REAL
============================================================

Crear una crónica de aceptación que parezca una aventura real.

Mínimo:

3 areas reutilizadas;
varias entradas;
al menos una puerta;
6+ NPC;
4+ enemigos;
2 paths/patrols cuando estén soportados;
2 quests;
1 quest branching;
varias conversaciones;
1 conversación condicionada;
1 encounter;
1 quest item;
1 recompensa;
1 secuencia;
música;
audio;
triggers;
save/load;
reentry;
final.

============================================================
54. JUGARLA ENTERA
============================================================

Cuando sea posible:

jugar la crónica desde principio hasta final.

No limitar playtest a:

"carga el mapa".

Hacer:

START
→ PLAY
→ SAVE
→ EXIT
→ LOAD
→ CONTINUE
→ FINISH

Registrar problemas.

============================================================
55. NO HACER
============================================================

NO:

- edición de geometría;
- brush editor;
- BSP editor;
- mesh editor;
- level builder;
- mini Blender;
- motor gráfico nuevo;
- remake;
- feature creep ajeno a creación de crónicas.

============================================================
56. DEFINICIÓN DEL PRODUCTO
============================================================

Redemption Chronicle Maker no pretende sustituir cada herramienta técnica que existió alrededor del motor NOD.

Pretende sustituir COMPLETAMENTE el workflow que un diseñador necesita para crear una crónica.

La geometría ya existe.

El diseñador construye la aventura encima.

============================================================
57. CRITERIO DE MADUREZ
============================================================

No considerar el proyecto "Aurora vampírico" únicamente porque tenga muchos paneles.

Debe permitir realmente:

AUTHOR
VALIDATE
BUILD
PLAY
SAVE
LOAD
ITERATE

una crónica completa.

============================================================
58. REPORTE
============================================================

Crear o actualizar:

docs/AUTHORING_GAP_AUDIT.md

docs/AURORA_PARITY_CHECKLIST.md

docs/RUNTIME_TEST_MATRIX.md

docs/RELEASE_BLOCKERS.md

y añadir un informe específico:

docs/AUTHORING_MATURITY_REPORT.md

con:

CURRENT STATE

RESOLVED CONCERNS

OPEN CONCERNS

RUNTIME VERIFIED

RUNTIME NOT VERIFIED

PLAYER ENTRY STATUS

DOORS/EXITS STATUS

PATHS STATUS

STATIC SCENE STATUS

SAVE/LOAD STATUS

.NOT RUNTIME STATUS

PORTABLE STATUS

AI STATUS

CAMERA STATUS

AUTHORING PARITY STATUS

BLOCKERS FOR 1.0

RECOMMENDED PRIORITIES

============================================================
59. REGLA FINAL
============================================================

No reescribas sistemas ya correctos para satisfacer literalmente este prompt.

Este prompt es una AUDITORÍA DE RIESGOS Y HUECOS.

Primero comprobar.

Después corregir.

Después testear.

Después verificar dentro de Redemption cuando sea necesario.

El objetivo final no es tener la mayor cantidad posible de funciones.

Es conseguir que alguien pueda sentarse delante de Redemption Chronicle Maker y crear una crónica completa como esperaba poder hacer con un toolset moderno:

areas
+
NPC
+
conversations
+
quests
+
doors
+
triggers
+
paths
+
encounters
+
cinematics
+
state
+
build
+
play

sin utilizar ninguna herramienta de autoría antigua.

Ese es el listón.

AURORA TOOLSET, PERO PARA VAMPIRE: THE MASQUERADE — REDEMPTION.
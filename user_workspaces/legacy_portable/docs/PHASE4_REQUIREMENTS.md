REDEMPTION CHRONICLE MAKER — FASE 4
AUTHORING COMPLETO DE CRÓNICAS: QUESTS, ESCENAS, OBJETOS, IA, CÁMARAS, AUDIO Y LÓGICA AVANZADA

La Fase 3 está terminada.

Ahora comienza la Fase 4.

Hasta este momento Redemption Chronicle Maker dispone de:

- backend propio de generación;
- proyectos modernos;
- build reproducible;
- editor gráfico;
- selección de levels originales;
- actores;
- conversaciones;
- eventos;
- Chronicle Flags;
- Resource Browser;
- viewport 3D;
- navegación moderna;
- geometría/texturas cuando están soportadas;
- colocación visual;
- triggers;
- relaciones;
- Find References;
- World Outliner.

La Fase 4 debe convertir todo esto en una herramienta capaz de crear una CRÓNICA REAL, no solamente una demo técnica o una escena aislada.

============================================================
OBJETIVO PRINCIPAL
============================================================

Al terminar esta fase debe ser posible crear una pequeña campaña jugable de Vampire: The Masquerade — Redemption sin utilizar ninguna herramienta antigua.

Debe poder construirse visualmente una experiencia con:

- varios levels;
- escenas;
- NPC;
- enemigos;
- conversaciones;
- decisiones;
- quests;
- objetos;
- inventario;
- recompensas;
- encuentros;
- triggers;
- cambios de escena;
- cámaras;
- secuencias;
- música;
- sonidos;
- condiciones;
- estados persistentes;
- consecuencias;
- IA configurable dentro de lo que realmente soporte el motor.

Todo generado directamente por Redemption Chronicle Maker.

NO utilizar:

- Embrace;
- NOT Editor;
- editores originales;
- herramientas de quest antiguas;
- herramientas de conversación antiguas;
- herramientas de Storyteller;
- workflows heredados.

============================================================
REGLA Nº 1 — NO ROMPER FASES ANTERIORES
============================================================

Antes de desarrollar:

1. Leer toda la documentación existente.
2. Leer PHASE1_REPORT, PHASE2_REPORT y PHASE3_REPORT si existen.
3. Ejecutar todos los tests.
4. Abrir los proyectos de prueba existentes.
5. Verificar el viewport.
6. Realizar Build de las crónicas anteriores.
7. Crear un checkpoint de trabajo si el repositorio utiliza Git.

La Fase 4 debe AMPLIAR la aplicación.

NO reescribir innecesariamente:

- modelo interno;
- YAML;
- build;
- GUI;
- viewport;
- parser;
- cache;
- Resource Browser.

============================================================
1. CRÓNICAS MULTI-LEVEL
============================================================

Hasta ahora un level podía actuar como escenario principal.

Fase 4 debe soportar con comodidad crónicas que utilicen múltiples levels.

Ejemplo:

Chronicle

    EastLondon
        Club
        Alley

    WestLondon
        Haven

    Warehouse
        MainFloor

El editor debe permitir gestionar las localizaciones utilizadas por la crónica.

Debe quedar claro:

- qué levels forman parte del proyecto;
- qué scenes/versiones se utilizan;
- cómo se conectan;
- cuál es la entrada inicial;
- qué exits/transiciones existen.

============================================================
2. CHRONICLE FLOW
============================================================

Crear una vista de alto nivel del flujo de la crónica.

NO es necesario hacer un graph editor gigantesco si una solución sencilla funciona mejor.

Debe permitir comprender:

EastLondon
   |
   +---- ClubExit ----> WestLondon
   |
   +---- SewerExit ---> Warehouse

y condiciones como:

WarehouseExit

IF:
    warehouse_unlocked

GO TO:
    Warehouse

El diseñador debe poder comprender fácilmente cómo se recorren los levels.

============================================================
3. SCENE TRANSITIONS
============================================================

Implementar edición visual de transiciones conocidas y confirmadas por el motor.

Debe soportar, cuando el backend/API real lo permita:

- Open Exit;
- Close Exit;
- Change Scene;
- Take Exit;
- Jump;
- Player Jump;
- teleport;
- portal/location changes.

NO inventar llamadas.

Cada transición debe utilizar API o formato confirmado.

En viewport, cuando una transición tenga posición espacial, mostrarla.

============================================================
4. QUEST EDITOR REAL
============================================================

Crear un Quest Editor moderno.

No quiero editar .nqd manualmente.

Debe permitir:

+ New Quest

Campos mínimos:

- ID;
- título;
- descripción;
- icono cuando esté soportado;
- estado;
- pasos/objetivos;
- condiciones de avance;
- condiciones de finalización.

Ejemplo:

QUEST:
The Missing Ghoul

STEP 1:
Talk to Victoria

STEP 2:
Find the warehouse

STEP 3:
Recover the ledger

STEP 4:
Return to Victoria

============================================================
5. QUEST STEPS
============================================================

Cada quest debe poder tener pasos.

Ejemplo:

Step 1
STATUS:
Active

COMPLETE WHEN:
Conversation victoria_intro returns 1

NEXT:
Step 2

Otro ejemplo:

Step 2

COMPLETE WHEN:
Player enters WarehouseTrigger

NEXT:
Step 3

Utilizar el sistema real de CodexQuest cuando corresponda.

No crear un sistema completamente desconectado del runtime si el motor ya proporciona uno adecuado.

============================================================
6. QUEST JOURNAL
============================================================

Investiga exactamente cómo Redemption presenta quests y textos al jugador.

Generar correctamente:

- nombre;
- descripción;
- estados;
- objetivos;
- progresión.

La herramienta debe ocultar formatos internos al diseñador.

============================================================
7. QUEST RELATIONSHIPS
============================================================

Integrar quests con Find References.

Al seleccionar:

QuestMissingGhoul

mostrar:

USES:
Victoria
WarehouseTrigger
LedgerItem
ReturnToVictoriaEvent

USED BY:
MainChronicleFlow
VictoriaConversation

Al seleccionar Victoria:

QUESTS:
The Missing Ghoul

============================================================
8. ITEM / OBJECT EDITOR
============================================================

Añadir soporte serio para objetos reutilizando recursos reales.

Debe ser posible:

Resource Browser
→ Items / Objects
→ elegir
→ colocar en viewport

Tipos potenciales según soporte confirmado:

- quest items;
- armas;
- consumibles;
- llaves;
- documentos;
- props;
- otros objetos interactivos.

No mezclar categorías si el motor las trata de manera diferente.

============================================================
9. ITEM PROPERTIES
============================================================

Mostrar únicamente propiedades que podamos generar correctamente.

Ejemplo:

ID
Template
Position
Orientation
Respawn
Quest Item
Pickup Event
Owner
Initial Container

No inventar propiedades de gameplay no soportadas.

============================================================
10. INVENTARIO DE ACTORES
============================================================

Permitir editar inventario inicial cuando el runtime/formato real lo permita.

Actor:

Victoria

Inventory:
    Pistol
    Blood Pack
    Warehouse Key

Debe poder añadirse desde Resource Browser.

Mostrar:

- equipped;
- carried;
- belt/slot;

sólo cuando dichos conceptos estén confirmados por los formatos originales.

============================================================
11. GIVE / TAKE ITEM ACTIONS
============================================================

Añadir acciones confirmadas para:

- dar objeto;
- quitar objeto;
- crear objeto;
- destruir/eliminar objeto;
- añadir a inventario;
- entregar recompensa.

Integrarlas con Event Editor y Conversation Editor.

Ejemplo:

ANSWER:
"Thank you."

DO:
Give Player WarehouseKey
Set Flag victoria_helped

============================================================
12. PICKUP EVENTS
============================================================

Los objetos interactivos deben poder disparar eventos.

Ejemplo:

Ledger

WHEN:
Picked Up

DO:
Set Flag ledger_found
Advance Quest MissingGhoul → Step 3
Start Conversation optional_reaction

============================================================
13. ENCOUNTER EDITOR
============================================================

Crear una capa de autoría para encuentros.

NO crear un sistema RPG nuevo.

Es una herramienta para agrupar elementos existentes.

Ejemplo:

Encounter:
Warehouse Ambush

Actors:
    Sabbat01
    Sabbat02
    Sabbat03

Spawn When:
Player enters WarehouseAmbush

Conditions:
warehouse_cleared == false

On Complete:
Set warehouse_cleared
Open warehouse_exit
Advance Quest

Debe compilarse al sistema existente de eventos/spawns.

============================================================
14. ACTOR GROUPS
============================================================

Permitir crear grupos lógicos:

WarehouseGuards

contiene:

Guard01
Guard02
Guard03

Esto facilita:

- Spawn Group;
- Remove Group;
- Highlight Group;
- Find References.

No tiene que existir como concepto en Redemption si se compila correctamente a operaciones individuales.

Es una abstracción del editor.

============================================================
15. ACTOR SPAWN PRESETS
============================================================

Permitir configurar patrones comunes:

- spawn immediately;
- spawn on scene start;
- spawn when trigger activates;
- spawn after conversation;
- spawn after flag;
- spawn after quest step.

Sin exigir escribir eventos repetitivos manualmente.

Internamente debe continuar generando el modelo normal de eventos.

============================================================
16. IA — INVESTIGACIÓN REAL
============================================================

Investigar profundamente:

- .nai;
- propiedades AI;
- scripts originales;
- CodexActor;
- modos;
- targets;
- equipos;
- chase;
- wander;
- combat behavior;
- movement;
- disciplines.

Separar claramente:

CONFIRMADO
INFERIDO
NO SOPORTADO

============================================================
17. AI PROFILE BROWSER
============================================================

Si los .nai originales pueden catalogarse:

crear:

Resource Browser
→ AI Profiles

Mostrar:

- identificador;
- parámetros importantes;
- recursos/actores originales que lo utilizan cuando pueda conocerse.

Permitir asignarlos sólo cuando técnicamente sea correcto hacerlo.

============================================================
18. AI CONFIGURATION
============================================================

No hacer todavía un megaeditor de IA si el formato no está suficientemente comprendido.

Sí permitir configurar elementos seguros:

- team;
- hostile/friendly;
- initial target;
- scripted movement;
- attack target;
- follow;
- move to;
- guard location;
- behavior profile cuando sea soportado.

============================================================
19. WAYPOINTS / PATHS
============================================================

Investigar cómo Redemption maneja:

- paths;
- waypoints;
- actor movement;
- arrival callbacks.

Si los datos necesarios pueden generarse sin alterar geometría:

añadir edición visual.

Flujo:

Add Waypoint
→ click
→ waypoint aparece

Path:
GuardPatrol

Waypoint01
→ Waypoint02
→ Waypoint03

Actor:
Guard01

Behavior:
Patrol GuardPatrol

Sólo implementar si puede traducirse limpiamente al runtime real.

============================================================
20. CAMERAS
============================================================

Añadir representación visual de cámaras.

Viewport:

Add Camera

Mostrar:

- posición;
- orientación;
- FOV/shot properties cuando corresponda.

Permitir ver aproximadamente lo que verá la cámara.

============================================================
21. CAMERA PREVIEW
============================================================

Al seleccionar una cámara:

Preview Camera

Mostrar una pequeña preview o cambiar temporalmente el viewport a dicha cámara.

No necesita reproducir exactamente el renderer del juego.

Sí debe permitir componer planos.

============================================================
22. CUTSCENE / SEQUENCE EDITOR
============================================================

Crear un editor sencillo para secuencias narrativas.

No hacer un editor cinematográfico gigantesco.

Modelo conceptual:

Sequence:
VictoriaIntroduction

1. Lock Player
2. Camera Shot VictoriaClose
3. Victoria animation gesture
4. Dialogue line
5. Camera Shot Player
6. Victoria moves to Door
7. Open Exit
8. Release Camera

Debe utilizar API real:

CodexCamera
CodexSequence
actor motions
timers
callbacks

cuando corresponda.

============================================================
23. SEQUENCE TIMELINE
============================================================

Si resulta razonable, utilizar una pequeña timeline/lista ordenada.

Ejemplo:

0.0 Camera VictoriaClose
0.5 Victoria gesture
1.2 Start conversation
4.8 Camera PlayerMedium
6.2 Open WarehouseDoor

No construir un Adobe Premiere.

Basta con una herramienta de secuencia clara.

============================================================
24. CONVERSATION + CAMERA
============================================================

Mejorar Conversation Editor para permitir asociar presentación.

Por línea/nodo cuando sea viable:

Speaker
Text
Camera Shot
Gesture/Animation
Optional Event

Ejemplo:

Victoria:
"No deberías haber venido."

CAMERA:
Victoria_Closeup

MOTION:
Gesture02

No obligar a configurar cámara para cada línea.

Debe existir comportamiento automático razonable.

============================================================
25. AUTO CAMERA
============================================================

Crear opcionalmente presets sencillos usando capacidades conocidas:

- speaker close;
- listener close;
- two shot;
- over shoulder;
- medium;
- full.

El editor puede generar los parámetros correspondientes.

No inventar nuevas cámaras si CodexCamera no lo soporta.

============================================================
26. ACTOR ANIMATIONS / MOTIONS
============================================================

Catalogar las animaciones/motion sets utilizables cuando sea posible.

Resource Browser:

Animations / Motions

Permitir búsqueda.

No prometer preview perfecta si todavía no podemos decodificar toda animación.

Sí permitir seleccionar movimientos conocidos por nombre cuando scripts originales demuestren su uso.

============================================================
27. AUDIO
============================================================

Crear soporte de autoría para:

- música;
- ambiente;
- efectos de sonido;
- voz cuando corresponda.

Resource Browser:
Audio

Categorías:

Music
Ambient
Sound
Voice

Sólo cuando puedan identificarse correctamente.

============================================================
28. MUSIC EVENTS
============================================================

Permitir:

Start Music
Push Music
Pop Music
Stop/Change Music

según API real.

Ejemplo:

WHEN:
WarehouseAmbush starts

DO:
Push Music combat_track

WHEN:
WarehouseAmbush ends

DO:
Pop Music

============================================================
29. AMBIENT AUDIO
============================================================

Permitir asociar ambiente a scenes cuando sea soportado.

Ejemplo:

EastLondon:
Rain ambience
Street ambience

Warehouse:
Industrial ambience

============================================================
30. WEATHER / ENVIRONMENT
============================================================

Exponer acciones confirmadas como:

SetWeatherEffect

si están correctamente documentadas y utilizadas por el juego.

No crear un sistema climático inventado.

============================================================
31. EVENT EDITOR AVANZADO
============================================================

Ampliar Event Editor sin convertirlo en un monstruo.

TRIGGERS / WHEN:

- Scene Start
- Scene End
- Player Enters Trigger
- Player Leaves Trigger
- Actor Clicked
- Actor Killed
- Actor Arrived
- Item Picked Up
- Conversation Ended
- Conversation Reached
- Quest Step Completed
- Timer

Sólo aquellos respaldados por callbacks reales.

============================================================
32. CONDITIONS AVANZADAS
============================================================

Añadir condiciones útiles basadas en datos reales:

- Chronicle Flag set/not set;
- Quest state;
- Quest step;
- Actor exists/alive cuando sea comprobable;
- Item owned cuando exista API segura;
- conversation result/state;
- otros estados confirmados.

Permitir:

ALL
ANY
NOT

sin crear lenguaje de programación innecesario.

============================================================
33. ACTION LIBRARY
============================================================

Crear una biblioteca central de acciones.

Categorías conceptuales:

ACTOR
    Spawn Actor
    Remove Actor
    Move Actor
    Attack
    Change Team
    Give Item

STORY
    Start Conversation
    Set Flag
    Clear Flag
    Advance Quest
    Complete Quest

WORLD
    Open Exit
    Close Exit
    Change Scene
    Teleport
    Weather

CAMERA
    Setup Cutscene
    Set Shot
    Release Camera

AUDIO
    Start Music
    Play Sound
    Ambient

La lista debe derivarse exclusivamente de funcionalidad soportada.

============================================================
34. ACTION PARAMETERS
============================================================

Cada acción debe presentar parámetros comprensibles.

Ejemplo:

Spawn Actor

Actor:
[Victoria ▼]

NO:

GUID:
[________]

El editor debe resolver IDs internos y generar código adecuado.

============================================================
35. ACTION TARGET PICKER
============================================================

Cuando una acción afecte a una entidad espacial:

permitir elegirla:

- desde lista;
- desde Outliner;
- cuando sea posible, directamente seleccionándola en viewport.

Ejemplo:

Action:
Open Exit

Target:
[Pick from Viewport]

============================================================
36. RELATIONSHIPS — AMPLIACIÓN
============================================================

Ampliar Find References para nuevos sistemas:

- quests;
- items;
- sequences;
- cameras;
- AI;
- audio;
- encounters;
- transitions.

El objetivo continúa siendo que cualquier elemento importante pueda responder:

WHO USES ME?

WHAT DO I USE?

============================================================
37. VALIDACIÓN SEMÁNTICA
============================================================

No limitar validación a "existe el ID".

Detectar problemas como:

- quest sin forma de avanzar;
- conversación referencia actor inexistente;
- item necesario nunca se crea;
- trigger afecta actor de otro level incompatible;
- exit apunta a level no incluido;
- sequence referencia cámara inexistente;
- encounter vacío;
- quest step apunta a evento inexistente;
- actor no tiene mecanismo de spawn;
- referencias circulares problemáticas cuando puedan determinarse.

Clasificar:

ERROR
WARNING
INFO

============================================================
38. DEAD CONTENT DETECTION
============================================================

Cuando sea razonable, detectar contenido aparentemente no utilizado:

- actor nunca spawned;
- conversación nunca lanzada;
- quest nunca iniciada;
- trigger sin acciones;
- flag nunca leído;
- flag nunca escrito;
- item no referenciado.

No tratar todos estos casos como ERROR.

Muchos serán WARNING.

============================================================
39. GLOBAL SEARCH
============================================================

Crear búsqueda global.

Ctrl+Shift+F o equivalente.

Buscar:

- IDs;
- nombres;
- textos de conversación;
- quest titles;
- flags;
- actores;
- items;
- events.

Los resultados deben permitir navegación directa.

============================================================
40. RENAME SEGURO
============================================================

Cuando sea posible:

Rename Actor ID

debe actualizar referencias automáticamente.

Lo mismo para:

- conversations;
- events;
- quests;
- items;
- flags;
- sequences.

Antes de renombrar:

mostrar número de referencias si resulta sencillo.

Evitar referencias rotas.

============================================================
41. UNDO / REDO
============================================================

Implementar Undo/Redo de forma seria para operaciones de autoría.

Ctrl+Z
Ctrl+Y / Ctrl+Shift+Z

Prioridad:

- mover entidad;
- crear/borrar entidad;
- cambiar property;
- editar conversación;
- editar evento;
- añadir/borrar quest step;
- editar trigger.

No hace falta cubrir absolutamente todo de inmediato, pero la arquitectura debe quedar establecida.

============================================================
42. COPY / PASTE / DUPLICATE
============================================================

Permitir duplicar:

- actors;
- triggers;
- objects;
- events;
- conversations cuando sea coherente.

Ejemplo:

Guard01
Duplicate
→ Guard02

Generar ID nuevo seguro.

============================================================
43. PREFABS / TEMPLATES DEL EDITOR
============================================================

Crear concepto propio de "prefab" sólo a nivel del editor.

NO confundir con .NOT.

Ejemplo:

Sabbat Ambush

incluye:

3 actores
1 trigger
1 encounter
1 music event

El usuario puede reutilizarlo.

Internamente se expande a entidades normales.

No necesita implementarse si amenaza objetivos principales; puede quedar preparado arquitectónicamente.

============================================================
44. `.NOT` — INVESTIGACIÓN PROFUNDA
============================================================

En esta fase quiero avanzar seriamente la investigación de `.NOT`.

NO utilizar NOT Editor.

Investigar directamente:

- cabecera;
- estructura;
- records;
- strings;
- template entries;
- propiedades;
- herencia si existe;
- referencias;
- diferencias entre Global.not, modernDay.not, darkAges.not, Multiplayer.not.

Comparar múltiples templates conocidos.

Documentar offsets/estructuras cuando puedan confirmarse.

============================================================
45. `.NOT` READER
============================================================

Objetivo deseable:

crear al menos un lector moderno propio capaz de enumerar templates y propiedades conocidas de `.NOT`.

Si es viable:

tools/not_inspector.py

o módulo equivalente.

El reader debe ser:

- read-only inicialmente;
- robusto;
- documentado;
- con tests.

============================================================
46. `.NOT` WRITER — NO FORZAR
============================================================

NO implementar un writer completo si todavía no comprendemos suficientemente el formato.

La prioridad es CORRECCIÓN.

Si durante investigación se demuestra que podemos generar una modificación segura:

hacer prototipo aislado y tests.

No hacer depender Fase 4 de ello.

============================================================
47. TEMPLATE INSPECTOR
============================================================

Si `.NOT` reader alcanza suficiente madurez:

Resource Browser → Actor Template → Inspect

mostrar propiedades conocidas.

Esto facilitará enormemente futuras fases.

============================================================
48. RESOURCE PREVIEWS
============================================================

Mejorar progresivamente Resource Browser.

Cuando sea posible:

Actors / models:
preview 3D

Textures:
preview 2D

Items:
modelo/icono

Audio:
play preview

No retrasar funcionalidad principal buscando previews perfectas.

============================================================
49. PROJECT DASHBOARD
============================================================

Añadir una vista resumen útil.

Ejemplo:

Chronicle: Blood in London

Levels: 4
Actors: 27
Conversations: 14
Quests: 6
Events: 43
Triggers: 18
Items: 12
Warnings: 3
Errors: 0

Esto ayuda a gestionar proyectos grandes.

============================================================
50. BUILD PROFILE
============================================================

Permitir distinguir:

Development Build
Release Build

Development puede incluir:

- logs;
- nombres útiles;
- información adicional de depuración cuando sea viable.

Release debe producir sólo lo necesario.

No complicar si el runtime no permite diferencias reales.

============================================================
51. DEPLOY / TEST
============================================================

Fase 4 debe investigar un workflow moderno de prueba.

Idealmente:

BUILD
→ DEPLOY
→ RUN GAME

Sin modificar arbitrariamente originales.

Crear un sistema controlado para copiar nuestra crónica compilada donde Redemption espera mods/crónicas.

Debe existir:

Deploy Chronicle

y cuando sea razonablemente seguro:

Run Redemption

============================================================
52. CONFIGURACIÓN DEL JUEGO
============================================================

La ruta de la instalación puede configurarse en Settings.

Ejemplo:

Game Installation:
H:\GOG\Vampire The Masquerade - Redemption

No hardcodear esa ruta como requisito general del programa.

La instalación detectada/seleccionada debe validarse.

============================================================
53. TEST IN GAME
============================================================

Si podemos automatizar el arranque:

Test Chronicle

Debe:

1. build;
2. validar;
3. deploy;
4. arrancar Redemption.

No intentar automatizar clicks internos del juego si no existe forma fiable.

============================================================
54. DEVELOPMENT CONSOLE / LOG
============================================================

Investigar modos de log/debug del juego.

Si existe una consola, log o salida útil:

integrarla como ayuda de desarrollo cuando sea práctico.

NO desarrollar hooking/inyección complicada en esta fase.

============================================================
55. ERROR MAPPING
============================================================

Cuando la compilación Java o build falle:

mapear el error a elementos del editor cuando sea posible.

Ejemplo:

NO:
GeneratedChronicle.java line 842

SÍ:
Event "WarehouseAmbush" → Action 3 produced invalid Java.

Mantener log técnico disponible para diagnóstico.

============================================================
56. GENERATED CODE INSPECTOR
============================================================

Añadir opcionalmente una vista avanzada:

Generated Files

para usuarios técnicos.

Mostrar:

- Java;
- .nsc;
- .nco;
- otros generados.

Read-only desde GUI por defecto.

Esto es útil para depuración y transparencia.

El usuario normal no necesita verlo.

============================================================
57. CAMPAIGN INTEGRITY CHECK
============================================================

Crear:

Tools → Check Chronicle Integrity

Debe revisar todo el proyecto y producir un informe.

Ejemplo:

0 Errors
4 Warnings
12 Info

Warnings:
- Actor "Guard04" is never spawned.
- Flag "victoria_angry" is never read.
- Quest "MissingGhoul" has no completion action.

============================================================
58. AUTOSAVE / RECOVERY
============================================================

Fortalecer recuperación.

Debe soportar:

- autosave;
- backup;
- recuperación después de cierre inesperado;
- escritura atómica.

No perder horas de diseño porque la aplicación se cierre.

============================================================
59. RENDIMIENTO DE PROYECTOS GRANDES
============================================================

Preparar aplicación para crónicas considerablemente mayores.

Evitar:

- recorrer todo el proyecto en cada click;
- reconstruir graphs constantemente;
- recargar Resources.nob repetidamente;
- recalcular geometría por cambios narrativos.

Utilizar índices/cache adecuados.

============================================================
60. EXPERIENCIA DE USO
============================================================

El programa debe continuar alejándose de una herramienta técnica.

Crear una quest debe sentirse como:

New Quest
→ escribir nombre
→ añadir steps
→ elegir condiciones
→ listo

No como:

crear .nqd
→ generar constante
→ añadir callback
→ editar Java

Lo mismo con todos los sistemas.

============================================================
61. NO CREAR SUBSISTEMAS DE GAMEPLAY NUEVOS
============================================================

Redemption Chronicle Maker es una herramienta de autoría.

No estamos rehaciendo Vampire Redemption.

No inventar:

- nuevo sistema de combate;
- nuevo sistema de quests ajeno al motor;
- nueva IA completa;
- nuevas estadísticas;
- sistemas propios de RPG.

La herramienta debe facilitar lo que el motor ya permite.

============================================================
62. NO EDITAR GEOMETRÍA
============================================================

La geometría continúa fuera de alcance.

NO:

- mover paredes;
- añadir habitaciones;
- modificar meshes del level;
- cambiar BSP;
- editar brushes;
- crear level desde cero.

Los levels originales son escenarios base.

Todo lo demás se construye encima.

============================================================
63. EXPERIENCIA OBJETIVO
============================================================

Al terminar Fase 4 quiero poder hacer algo así:

NEW CHRONICLE

Add Level:
East London

Add Actor:
Victoria

Place Actor visually

Create Conversation:
Victoria Intro

Create Quest:
The Missing Ghoul

Add Item:
Warehouse Ledger

Place Item visually

Create Trigger:
Warehouse Entrance

Create Encounter:
3 Sabbat

Trigger:
Player enters

Actions:
Spawn Sabbat
Start Combat Music
Close Exit

On enemies dead:
Open Exit
Advance Quest

Create Camera Sequence

Return to Victoria

Conversation result:
Complete Quest

Reward:
Item / XP / state

Build

Deploy

Run

TODO sin utilizar ninguna herramienta original.

============================================================
64. PRUEBA DE ACEPTACIÓN
============================================================

Crear una nueva crónica de demostración utilizando exclusivamente Redemption Chronicle Maker.

Debe contener como mínimo:

- 2 levels originales;
- 1 transición entre ellos;
- 4 NPC;
- 3 enemigos;
- 1 NPC importante con varias conversaciones;
- 1 conversación ramificada;
- 1 conversación que dependa de estado anterior;
- 1 quest con mínimo 3 pasos;
- 1 quest item;
- 1 trigger espacial;
- 1 encounter;
- 1 cambio de música;
- 1 Chronicle Flag con consecuencia posterior;
- 1 cámara/secuencia si el API confirmado permite implementarla;
- 1 condición basada en quest o flag;
- 1 recompensa;
- final de quest.

Todo creado mediante GUI.

No editar manualmente archivos generados salvo para diagnóstico.

============================================================
65. PRUEBA DENTRO DEL JUEGO
============================================================

Cuando sea posible:

hacer Build.

Deploy.

Ejecutar Vampire Redemption.

Probar manualmente la crónica.

Verificar especialmente:

- carga;
- transitions;
- actores;
- conversación;
- branch;
- quest;
- trigger;
- encounter;
- item;
- persistencia;
- final.

Documentar cualquier diferencia entre comportamiento esperado y real.

============================================================
66. TESTS AUTOMÁTICOS
============================================================

Mantener todos los tests existentes.

Añadir tests para:

- quests;
- quest steps;
- items;
- inventory;
- encounters;
- transitions;
- sequences;
- actions;
- conditions;
- global rename;
- Find References ampliado;
- integrity checker;
- .NOT reader si se implementa;
- deployment;
- generated output.

============================================================
67. DOCUMENTACIÓN
============================================================

Actualizar:

README.md
docs/ARCHITECTURE.md
docs/ENGINE_NOTES.md
docs/FORMAT_NOTES.md
docs/ROADMAP.md
docs/EDITOR_GUIDE.md
docs/VIEWPORT.md

Crear:

docs/QUESTS.md
docs/ITEMS.md
docs/SEQUENCES.md
docs/AI.md
docs/NOT_FORMAT.md
docs/DEPLOYMENT.md

cuando dichas áreas se implementen/investiguen.

============================================================
68. HELP CONTEXTUAL
============================================================

Cuando sea sencillo:

añadir tooltips o ayuda breve.

Ejemplo:

Chronicle Flag:
Persistent boolean state stored by the chronicle.

No llenar la interfaz de documentación.

El objetivo es reducir la necesidad de consultar manual externo constantemente.

============================================================
69. NO HACER EN FASE 4
============================================================

NO hacer todavía:

- edición de geometría;
- creación de levels completos;
- editor de meshes;
- editor completo de materiales;
- editor completo de texturas;
- creación de modelos;
- animación 3D completa;
- writer `.NOT` completo si no está comprendido;
- sistema de plugins público;
- marketplace;
- integración online;
- multiplayer tooling completo;
- conversión del motor;
- remake del juego.

============================================================
70. PRIORIDADES
============================================================

Si el alcance resulta demasiado grande, priorizar exactamente así:

1. Multi-level chronicles.
2. Quest Editor.
3. Items / quest items.
4. Event/condition/action expansion.
5. Encounters.
6. Scene transitions.
7. Camera/cutscene basics.
8. Audio.
9. AI useful subset.
10. Deploy/Test workflow.
11. `.NOT` reader research.
12. polish adicional.

NO sacrificar estabilidad para implementar todos los puntos superficialmente.

============================================================
71. FILOSOFÍA DE IMPLEMENTACIÓN
============================================================

Prefiero:

5 sistemas completos y fiables

a:

20 sistemas medio rotos.

Cada nueva función debe recorrer el pipeline completo:

MODEL
↓
GUI
↓
VALIDATION
↓
SERIALIZATION
↓
GENERATOR
↓
BUILD
↓
RUNTIME

No crear botones que todavía no generen algo válido.

============================================================
72. REVISIÓN FINAL
============================================================

Antes de terminar:

- ejecutar todos los tests;
- comprobar proyectos de fases anteriores;
- comprobar viewport;
- comprobar builds anteriores;
- ejecutar Integrity Check;
- crear demo Fase 4;
- Build demo;
- Deploy demo cuando sea posible;
- probar en Redemption cuando sea posible;
- revisar warnings;
- revisar logs;
- revisar documentación;
- eliminar código muerto evidente;
- comprobar que CLI sigue funcionando.

============================================================
73. REPORTE
============================================================

Crear:

docs/PHASE4_REPORT.md

con:

IMPLEMENTADO

QUEST SYSTEM

ITEM SYSTEM

ENCOUNTERS

TRANSITIONS

CAMERAS / SEQUENCES

AUDIO

AI

EVENTS / CONDITIONS / ACTIONS

RESOURCE BROWSER

.NOT RESEARCH

DEPLOYMENT

PROBADO AUTOMÁTICAMENTE

PROBADO DENTRO DE REDEMPTION

NO PROBADO

BUGS CONOCIDOS

LIMITACIONES

DEUDA TÉCNICA

CAMBIOS DE ARQUITECTURA

PROPUESTA PARA FASE 5

============================================================
74. CRITERIO REAL DE ÉXITO
============================================================

La Fase 4 NO está terminada porque existan más paneles.

Está terminada cuando Redemption Chronicle Maker puede utilizarse realmente para construir una pequeña aventura completa.

Debemos haber pasado de:

"puedo colocar NPC y crear conversaciones"

a:

"puedo crear una CRÓNICA jugable."

La experiencia objetivo es:

LEVELS
↓
ACTORS
↓
CONVERSATIONS
↓
QUESTS
↓
ITEMS
↓
TRIGGERS
↓
ENCOUNTERS
↓
CAMERAS / AUDIO
↓
CONSEQUENCES
↓
BUILD
↓
DEPLOY
↓
PLAY

Todo mediante una herramienta moderna.

Todo directamente contra los formatos/runtime de Vampire: The Masquerade — Redemption.

Sin herramientas de autoría originales.

============================================================
75. REGLA FINAL
============================================================

NO empezar Fase 5.

Al terminar, detenerse.

Dejar todo implementado, probado, documentado y persistido en el proyecto.

No considerar una función terminada si sólo existe visualmente en la GUI pero todavía no llega correctamente hasta el build/runtime.

Redemption Chronicle Maker debe continuar acercándose al objetivo original:

EL EDITOR DE CRÓNICAS QUE VAMPIRE: THE MASQUERADE — REDEMPTION DEBERÍA HABER TENIDO.
REDEMPTION CHRONICLE MAKER — FASE 5
INDEPENDENCIA TOTAL DE LAS HERRAMIENTAS ORIGINALES, TEMPLATES PROPIOS, DEBUGGING, PLAYTEST Y PRIMERA VERSIÓN REALMENTE DISTRIBUIBLE

La Fase 4 está terminada.

Ahora comienza la Fase 5.

Hasta este momento Redemption Chronicle Maker ya debe permitir crear una pequeña crónica completa utilizando:

- levels originales;
- viewport 3D moderno;
- navegación;
- colocación visual;
- actores;
- conversaciones;
- eventos;
- Chronicle Flags;
- quests;
- items;
- triggers;
- encounters;
- transiciones;
- cámaras/secuencias;
- audio;
- IA dentro de lo soportado;
- Build;
- Deploy;
- ejecución/prueba del juego cuando sea posible.

La Fase 5 debe atacar ahora los obstáculos que todavía nos mantienen atados conceptualmente a recursos/templates preexistentes y convertir Redemption Chronicle Maker en una herramienta madura, depurable y distribuible.

============================================================
OBJETIVO PRINCIPAL
============================================================

El objetivo de Fase 5 es pasar de:

"puedo crear crónicas completas utilizando los recursos que ya existen"

a:

"puedo crear contenido nuevo y mantener proyectos grandes sin depender de ninguna herramienta original del SDK."

Las prioridades de esta fase son:

1. Comprender y escribir .NOT de forma segura.
2. Crear templates propios de actores/objetos.
3. Crear un editor moderno de templates.
4. Mejorar IA y comportamiento.
5. Mejorar secuencias/cinemáticas.
6. Crear herramientas serias de debugging.
7. Facilitar muchísimo el playtesting.
8. Mejorar importación, exportación y packaging.
9. Convertir la aplicación en un programa Windows distribuible.
10. Mantener compatibilidad absoluta con todo lo construido.

NO editar geometría todavía.

============================================================
REGLA Nº 1 — REGRESIÓN CERO
============================================================

Antes de comenzar:

- leer toda la documentación existente;
- leer PHASE1_REPORT;
- leer PHASE2_REPORT;
- leer PHASE3_REPORT;
- leer PHASE4_REPORT;
- ejecutar todos los tests;
- comprobar crónicas de fases anteriores;
- comprobar Build;
- comprobar Deploy;
- comprobar viewport;
- comprobar carga/guardado;
- comprobar Resource Browser.

Crear un checkpoint antes de cambios estructurales importantes.

Fase 5 debe ampliar el proyecto.

NO reescribir componentes estables por gusto.

============================================================
1. `.NOT` — OBJETIVO PRINCIPAL
============================================================

La investigación de `.NOT` realizada anteriormente debe convertirse ahora en soporte real.

El objetivo es disponer de:

NOT Reader
+
NOT Writer

propios.

NO utilizar NOT Editor.

NO llamar externamente a NOT Editor.

NO automatizar NOT Editor.

Queremos generar directamente el formato que consume Redemption.

============================================================
2. INVESTIGACIÓN FORENSE DE `.NOT`
============================================================

Antes de escribir:

analizar exhaustivamente:

Global.not
modernDay.not
darkAges.not
Multiplayer.not

y cualquier otro `.NOT` disponible.

Comparar:

- cabeceras;
- tablas;
- offsets;
- strings;
- records;
- alignment;
- tipos de datos;
- templates;
- propiedades;
- defaults;
- referencias;
- inheritance si existe;
- parent/template relations;
- modelos;
- scripts;
- AI;
- flags;
- actor data;
- item data;
- object data.

Utilizar múltiples templates conocidos como casos de estudio.

============================================================
3. ESPECIFICACIÓN DEL FORMATO `.NOT`
============================================================

Actualizar:

docs/NOT_FORMAT.md

con una especificación técnica progresiva.

Separar:

CONFIRMADO

PROBABLE

DESCONOCIDO

No inventar campos.

Cuando se conozca:

documentar tamaño,
tipo,
endianness,
offset,
significado,
relaciones.

============================================================
4. NOT READER COMPLETO
============================================================

Crear un parser robusto.

Debe poder:

- abrir `.NOT`;
- enumerar templates;
- leer nombres;
- leer propiedades conocidas;
- preservar propiedades desconocidas;
- identificar tipo de template cuando sea posible;
- seguir referencias;
- detectar corrupción básica.

Muy importante:

NO descartar datos desconocidos.

Si un record contiene campos todavía no comprendidos, conservarlos en representación raw para permitir round-trip.

============================================================
5. ROUND-TRIP `.NOT`
============================================================

Prueba fundamental:

READ original.not
→ WRITE copy.not

y comprobar que:

- la estructura es válida;
- los templates continúan presentes;
- las propiedades conocidas coinciden;
- los datos desconocidos se conservan cuando sea posible.

No exigir byte-identical si existen offsets o normalización inevitable.

Sí exigir equivalencia funcional.

============================================================
6. NOT WRITER
============================================================

Implementar escritura únicamente cuando exista suficiente certeza.

El writer debe soportar inicialmente:

- copiar template;
- modificar propiedades conocidas;
- añadir template derivado;
- renombrar template;
- cambiar campos soportados.

NO intentar soportar todo el formato simultáneamente.

============================================================
7. TEMPLATE EDITOR
============================================================

Crear en GUI:

Templates

con categorías conocidas.

Por ejemplo:

Actors
Items
Objects
Weapons
Props
Other

sólo cuando puedan identificarse con seguridad.

============================================================
8. CREAR TEMPLATE NUEVO
============================================================

Flujo objetivo:

Templates
→ New Actor Template
→ Base Template
→ Edit Properties
→ Save

Ejemplo:

Base:
businessWoman

New Template:
VictoriaVentrue

Model:
...

Clan:
Ventrue

AI:
...

Script:
...

Flags:
...

El sistema puede utilizar inicialmente herencia/copia de template existente para reducir riesgo.

============================================================
9. TEMPLATE INHERITANCE
============================================================

Si el formato soporta herencia o dependencia de template:

exponerla correctamente.

Si NO existe conceptualmente como tal:

NO inventarla en el formato.

El editor puede tener internamente:

"Clone From"

aunque al guardar produzca una entrada completa.

============================================================
10. ACTOR TEMPLATE EDITOR
============================================================

Cuando esté confirmado, permitir editar propiedades como:

- name/id;
- model;
- actor flags;
- clan;
- team;
- AI;
- script;
- cast ID;
- health;
- stats;
- disciplines;
- talkable;
- inventory defaults;
- otros campos confirmados.

No mostrar campos cuyo significado no esté suficientemente comprendido.

============================================================
11. ITEM TEMPLATE EDITOR
============================================================

Cuando el parser permita distinguir items:

permitir crear/modificar:

- template ID;
- model;
- icon;
- type;
- inventory behavior;
- script;
- stack/value;
- flags;
- equip data;

únicamente para campos confirmados.

============================================================
12. TEMPLATE VALIDATION
============================================================

Detectar:

- IDs duplicados;
- parent/base inexistente;
- modelo inexistente;
- AI inexistente;
- script inexistente;
- recursos rotos;
- valores fuera de rango;
- propiedades incompatibles conocidas.

============================================================
13. CUSTOM RESOURCE CATALOG
============================================================

Resource Browser debe separar:

ORIGINAL GAME

PROJECT RESOURCES

Por ejemplo:

Actors
    Original
    Project

Items
    Original
    Project

Models
    Original
    Project

El usuario debe distinguir claramente recursos propios y originales.

============================================================
14. PROJECT RESOURCE OVERRIDES
============================================================

Diseñar una estrategia limpia para recursos de proyecto.

NO modificar recursos originales.

El proyecto debe poder incluir overrides/copias propias cuando el motor lo permita.

Documentar claramente precedencia de recursos.

============================================================
15. MODELS
============================================================

Investigar con más profundidad los formatos de modelos originales.

Objetivos:

- visualizar más modelos;
- asociar correctamente modelos a templates;
- mostrar preview;
- identificar texturas asociadas;
- identificar skeleton/animation sets cuando sea posible.

NO crear todavía un modelador 3D.

============================================================
16. MODEL PREVIEW
============================================================

Resource Browser:

Model
→ Preview

Debe permitir:

- rotar;
- zoom;
- inspeccionar;
- ver textura;
- ver bounding box.

Si existen animaciones fáciles de asociar:

permitir preview opcional.

============================================================
17. ACTOR PREVIEW
============================================================

Un Actor Template debe poder previsualizarse combinando:

- model;
- material/textures;
- escala;
- orientación;
- propiedades básicas conocidas.

El preview NO necesita simular IA.

============================================================
18. TEXTURE BROWSER
============================================================

Mejorar catálogo de texturas.

Debe permitir:

- búsqueda;
- preview;
- dimensiones;
- alpha;
- resource path;
- referencias conocidas.

Esto ayudará tanto a modelos como objetos.

============================================================
19. CUSTOM TEXTURES
============================================================

Investigar qué formato espera el juego.

Cuando sea razonablemente viable:

permitir importar:

PNG/TGA/etc.

y convertir automáticamente al formato necesario.

NO obligar al usuario a utilizar convertidores antiguos.

============================================================
20. RESOURCE CONVERSION PIPELINE
============================================================

Principio:

MODERN SOURCE
→ OUR CONVERTER
→ REDEMPTION RESOURCE

No:

MODERN SOURCE
→ OLD SDK TOOL
→ REDEMPTION RESOURCE

Si algún formato todavía requiere tooling antiguo porque no está comprendido:

documentarlo como limitación.

NO esconder esa dependencia.

============================================================
21. AI EDITOR
============================================================

La investigación de `.nai` debe evolucionar a un editor moderno útil.

Resource Browser / AI Profiles:

- New;
- Clone;
- Edit;
- Delete project AI profile.

============================================================
22. AI PROFILE PROPERTIES
============================================================

Exponer campos confirmados como:

attack type;
attack rate;
movement;
chase distance;
search distance;
wander;
discipline usage;
flags;
otros campos confirmados.

Utilizar nombres amigables.

Mostrar nombre interno/valor técnico en modo avanzado.

============================================================
23. AI PRESETS
============================================================

Crear presets de autoría que generen perfiles reales.

Ejemplos conceptuales:

Passive Civilian
Guard
Aggressive Melee
Ranged Enemy
Patrol Guard
Follower

No inventar nuevas reglas.

Cada preset debe simplemente establecer propiedades reales del motor.

============================================================
24. SCRIPTED AI BEHAVIOR
============================================================

Integrar comportamiento scriptado con Event Editor.

Ejemplos:

Move Actor
Follow Actor
Attack Actor
Guard Position
Flee
Change Team
Set Target
Clear Target

sólo cuando API real lo soporte.

============================================================
25. PATH EDITOR MEJORADO
============================================================

Si Fase 4 implementó waypoints:

mejorarlo.

Viewport:

Path Tool

click
→ waypoint 1
click
→ waypoint 2
click
→ waypoint 3

Mostrar línea entre ellos.

Permitir:

- reorder;
- insert;
- delete;
- loop;
- reverse.

Sólo si puede traducirse correctamente a funciones reales.

============================================================
26. VISUAL SCRIPTING — MUY CONTROLADO
============================================================

El Event Editor puede evolucionar a una vista visual opcional.

NO crear un lenguaje nuevo gigante.

Debe representar exactamente:

TRIGGER
→ CONDITIONS
→ ACTIONS

Ejemplo:

[Player enters trigger]
        |
[flag warehouse_done == false]
        |
[Spawn Guards]
        |
[Close Exit]
        |
[Music Combat]

Debe ser otra representación del MISMO modelo de Fase 4.

No crear dos sistemas distintos.

============================================================
27. GRAPH VIEW
============================================================

Graph View debe ser opcional.

Tree/List Editor sigue existiendo.

Ambos editan los mismos datos.

Esto es importante para:

- usuarios que prefieran lista;
- debugging;
- proyectos grandes.

============================================================
28. CONVERSATION GRAPH
============================================================

Ahora sí puede añadirse un editor gráfico de conversaciones.

Cada nodo:

- speaker;
- lines;
- answers;
- goto;
- return;
- events/camera hooks.

Debe coexistir con la vista árbol existente.

============================================================
29. CONVERSATION GRAPH VALIDATION
============================================================

Visualizar:

- nodos inaccesibles;
- ramas muertas;
- destinos inexistentes;
- ciclos;
- returns;
- entry node.

Los ciclos no son necesariamente error.

Marcarlos informativamente.

============================================================
30. CINEMATIC TIMELINE
============================================================

Mejorar el Sequence Editor.

Crear timeline suficientemente cómoda para:

- camera shots;
- actor movement;
- animation;
- dialogue;
- audio;
- waits;
- events.

No intentar competir con software de edición cinematográfica.

============================================================
31. SCRUB / PREVIEW DE SECUENCIAS
============================================================

Cuando sea posible:

permitir preview aproximada dentro del viewport.

Ejemplo:

camera changes,
actor markers move,
timing indicators.

No afirmar que el preview reproduce exactamente runtime si no es así.

============================================================
32. CAMERA FRUSTUM
============================================================

Mostrar visualmente:

- posición;
- dirección;
- frustum aproximado;
- target cuando exista.

Esto debe hacer composición de escenas mucho más cómoda.

============================================================
33. CINEMATIC CAMERA CONTROLS
============================================================

Permitir:

Align Camera to View

y:

Align View to Camera

Flujo:

navego viewport
→ encuentro encuadre
→ "Create Camera From View"

Esto es importantísimo para usabilidad.

============================================================
34. DEBUG MODE DEL EDITOR
============================================================

Crear un modo:

PLAYTEST / DEBUG

orientado a probar crónicas.

No es necesario ejecutar el motor dentro del editor.

Debe centralizar:

- build;
- deploy;
- run;
- logs;
- state;
- validation;
- quick navigation.

============================================================
35. DEBUG SYMBOLS / MAPPING
============================================================

Generar metadata que relacione código generado con entidades del proyecto.

Ejemplo:

GeneratedChronicle.java line 911

→ Event:
WarehouseAmbush

→ Action:
Spawn Guard02

Así los errores técnicos pueden traducirse a elementos de autoría.

============================================================
36. RUNTIME LOG PARSING
============================================================

Investigar logs reales de Redemption.

Si el juego produce:

- console output;
- log files;
- script errors;

crear parser.

Mostrar en editor:

RUNTIME ERROR

Conversation victoria_intro failed
Actor Victoria not found

cuando pueda inferirse con fiabilidad.

============================================================
37. DEBUG BUILD
============================================================

Crear build de desarrollo con instrumentación propia cuando sea viable.

Ejemplo:

registrar:

- scene start;
- actor spawn;
- event fired;
- conversation start/end;
- quest progression;
- flag changes.

Sólo si puede hacerse sin romper comportamiento.

============================================================
38. EVENT TRACE
============================================================

Crear un Event Trace para debug.

Ejemplo:

12:04:02 SceneStart EastLondon
12:04:02 Spawn Victoria
12:04:09 Click Victoria
12:04:09 Conversation victoria_intro
12:04:21 Return 2
12:04:21 Set victoria_angry = true

Esto sería enormemente útil.

============================================================
39. FLAG WATCH
============================================================

Permitir definir watches de debug.

Ejemplo:

WATCH:
victoria_met
victoria_angry
warehouse_open

Mostrar cambios detectados cuando exista instrumentación suficiente.

============================================================
40. QUEST WATCH
============================================================

Lo mismo para quests:

MissingGhoul
Step: 2 → 3
Status: Active

============================================================
41. SPAWN WATCH
============================================================

Debug:

Actors alive/spawned

Victoria
Guard01
Guard02

si la instrumentación real permite conocerlo.

============================================================
42. PLAYTEST BOOKMARKS
============================================================

Crear bookmarks de autoría.

Ejemplo:

Test:
Warehouse Ambush

Expected:
Level = Warehouse
Quest = MissingGhoul Step 2
Flags:
warehouse_open = false

No es necesario alterar el savegame del juego si no sabemos hacerlo de forma segura.

Puede inicialmente ser checklist/instrucción de prueba.

============================================================
43. QUICK TEST ENTRY POINTS
============================================================

Investigar si el runtime permite arrancar crónica/level de forma más directa.

Si existe forma confirmada:

añadir:

Test From Level

Test From Chronicle Start

NO desarrollar hacks frágiles si no existe soporte.

============================================================
44. SAVEGAME RESEARCH
============================================================

Investigar formato de saves únicamente para determinar si puede facilitar playtest.

NO editar saves hasta comprenderlos suficientemente.

Objetivo futuro posible:

crear estados de prueba.

En esta fase:

reader/investigación si es razonable.

============================================================
45. PROJECT VALIDATOR 2.0
============================================================

Ampliar Integrity Check.

Analizar:

- templates;
- resources;
- quests;
- events;
- conversations;
- scenes;
- transitions;
- AI;
- paths;
- cameras;
- sequences;
- custom assets.

============================================================
46. STORY FLOW ANALYSIS
============================================================

Crear análisis estático del flujo narrativo.

Ejemplo:

Chronicle Start
→ Victoria Intro
→ Quest MissingGhoul
→ Warehouse
→ Return Victoria

Mostrar posibles ramas.

No pretender resolver todas las condiciones dinámicas.

Sí detectar rutas obviamente imposibles.

============================================================
47. UNREACHABLE CONTENT
============================================================

Detectar contenido potencialmente inalcanzable:

- conversation node unreachable;
- level never entered;
- quest never started;
- encounter never triggered;
- actor never spawned;
- sequence never called.

Usar WARNING, no necesariamente ERROR.

============================================================
48. REFERENCE GRAPH
============================================================

Crear una vista global opcional:

REFERENCE GRAPH

para investigar dependencias.

No debe ser la interfaz principal.

Debe servir para:

- debugging;
- comprensión;
- refactors.

============================================================
49. SAFE DELETE
============================================================

Antes de borrar:

Victoria

mostrar:

Referenced by 8 elements.

Options:

Cancel
Delete and remove references
Delete anyway (advanced)

Evitar proyectos rotos.

============================================================
50. RENAME REFACTORING
============================================================

Mejorar rename seguro.

Renombrar:

Actor
Conversation
Quest
Flag
Event
Template
Sequence

debe actualizar referencias.

============================================================
51. PROJECT MIGRATIONS
============================================================

Como el modelo está creciendo, crear sistema de versión.

Ejemplo:

project_format: 5

Al abrir proyecto antiguo:

Upgrade Project

Mantener backup previo.

No romper silenciosamente proyectos de fases anteriores.

============================================================
52. BACKUPS
============================================================

Implementar snapshots automáticos razonables.

Ejemplo:

.backups/

Mantener varias versiones recientes.

No almacenar infinitamente.

============================================================
53. CRASH RECOVERY
============================================================

La aplicación debe sobrevivir a cierres inesperados.

Al iniciar:

Recovered autosave found.

Recover?
Discard?

============================================================
54. IMPORT PROJECT
============================================================

Permitir importar proyecto empaquetado.

Por ejemplo:

.rcmproject

o ZIP estructurado.

============================================================
55. EXPORT PROJECT
============================================================

Exportar proyecto completo:

- YAML/data;
- conversations;
- templates;
- custom resources;
- documentation opcional.

NO incluir recursos originales de Redemption innecesariamente.

============================================================
56. PORTABLE PROJECT
============================================================

La exportación debe identificar claramente:

Original Game Dependency

versus:

Project-owned Resources

Esto será importante para compartir crónicas legalmente y evitar duplicar material del juego.

============================================================
57. CHRONICLE PACKAGE
============================================================

Crear un formato de distribución de crónicas.

Ejemplo conceptual:

MyChronicle.rcmpack

Debe contener únicamente lo necesario para instalar la crónica.

============================================================
58. PACKAGE MANIFEST
============================================================

Cada paquete debe incluir:

- ID;
- name;
- author;
- version;
- description;
- required game version;
- required Chronicle Maker/runtime version si aplica;
- resources;
- dependencies.

============================================================
59. INSTALL CHRONICLE
============================================================

Crear:

Install Chronicle Package

Debe:

- validar;
- comprobar conflictos;
- mostrar archivos que instalará;
- instalar;
- registrar instalación.

============================================================
60. UNINSTALL CHRONICLE
============================================================

La herramienta debe poder retirar únicamente los archivos que ella instaló.

No borrar recursos ajenos.

============================================================
61. PACKAGE CONFLICT DETECTION
============================================================

Detectar:

- mismo ID;
- mismo resource;
- mismo template;
- override incompatible.

Avisar claramente.

============================================================
62. PROJECT VERSIONING
============================================================

Añadir campos:

Version
Author
Description

y quizá:

Changelog

Esto prepara distribución real.

============================================================
63. EXPORT RELEASE BUILD
============================================================

Añadir:

Build Release Package

Diferente de:

Development Build.

Release debe:

- limpiar debug instrumentation;
- validar;
- generar archivos necesarios;
- empaquetar;
- producir manifest.

============================================================
64. APPLICATION PACKAGING
============================================================

Ahora sí:

crear ejecutable Windows.

Objetivo:

RedemptionChronicleMaker.exe

No obligar al usuario a instalar Python.

Usar solución madura compatible con PySide6.

Por ejemplo PyInstaller/Nuitka si resulta apropiado.

Documentar decisión.

============================================================
65. PORTABLE BUILD
============================================================

Preferencia inicial:

versión portable.

Ejemplo:

RedemptionChronicleMaker/
    RedemptionChronicleMaker.exe
    ...

Sin instalador obligatorio.

Más adelante podrá existir instalador.

============================================================
66. SETTINGS
============================================================

Crear panel Settings limpio.

Configuraciones:

- Game Path;
- cache location;
- autosave interval;
- viewport controls;
- editor preferences;
- debug options.

No exponer cien opciones técnicas sin necesidad.

============================================================
67. FIRST RUN
============================================================

Primer arranque:

1. Welcome.
2. Detect/select Redemption installation.
3. Validate installation.
4. Build resource cache.
5. Ready.

No exigir configuración manual absurda.

============================================================
68. RESOURCE CACHE REBUILD
============================================================

Settings / Tools:

Rebuild Resource Cache

con progreso.

============================================================
69. DIAGNOSTICS
============================================================

Crear:

Help → Diagnostics

Debe mostrar:

Application version
Project format
Game path
Game detected
Resource cache status
Renderer
Python/runtime bundled version
Graphics API
etc.

Útil para soporte.

============================================================
70. EXPORT DIAGNOSTIC REPORT
============================================================

Permitir generar reporte técnico para bugs.

NO incluir información privada innecesaria.

============================================================
71. ERROR REPORTING
============================================================

Cuando la aplicación falle:

mostrar error amigable.

Guardar log.

No desaparecer sin explicación.

============================================================
72. UI POLISH
============================================================

Realizar una pasada seria de usabilidad.

Revisar:

- tamaños;
- iconos;
- paddings;
- paneles;
- tabs;
- menus;
- context menus;
- shortcuts;
- tooltips;
- focus;
- keyboard navigation.

No rediseñar toda la aplicación por estética.

============================================================
73. DARK / LIGHT
============================================================

Si resulta sencillo mediante Qt:

permitir tema claro/oscuro o seguir sistema.

NO gastar demasiado tiempo aquí.

============================================================
74. COMMAND PALETTE
============================================================

Opcional pero útil:

Ctrl+Shift+P

Buscar acciones:

Add Actor
Build
Validate
Find References
Open Quest
etc.

Sólo si no distrae de prioridades.

============================================================
75. RECENT PROJECTS
============================================================

Añadir lista de proyectos recientes.

============================================================
76. DOCUMENTATION BROWSER
============================================================

Help puede abrir:

EDITOR_GUIDE
shortcuts
troubleshooting.

No hace falta navegador HTML complejo.

============================================================
77. SAMPLE PROJECTS
============================================================

Incluir varios proyectos propios pequeños que NO distribuyan assets originales.

Ejemplos:

Hello Vampire
Conversation Demo
Quest Demo
Encounter Demo

Dependiendo de recursos presentes en instalación del usuario.

============================================================
78. TEMPLATE WIZARDS
============================================================

Crear wizards únicamente donde reduzcan muchísimo fricción.

Ejemplo:

New NPC

1. Choose Base Template
2. Choose Model
3. Choose AI
4. Name
5. Place in Level

No crear asistentes para todo.

============================================================
79. COPY ORIGINAL TEMPLATE TO PROJECT
============================================================

Flujo muy importante:

Original Template:
businessWoman

Right click:
Clone to Project

New ID:
VictoriaVentrue

Ahora editable sin afectar original.

============================================================
80. PROJECT TEMPLATE LIBRARY
============================================================

Templates personalizados deben guardarse en el proyecto.

No escribir jamás en `.NOT` original.

Build genera los recursos/overrides necesarios.

============================================================
81. CUSTOM ACTOR TEST
============================================================

Prueba de aceptación específica:

1. Clonar actor template original.
2. Cambiar ID.
3. Cambiar propiedades soportadas.
4. Asignar script/AI propios.
5. Colocarlo en level.
6. Build.
7. Deploy.
8. Ejecutar Redemption.
9. Confirmar que aparece y funciona.

Ésta es una prueba crítica de Fase 5.

============================================================
82. CUSTOM ITEM TEST
============================================================

Cuando esté soportado:

1. Clone item template.
2. Modify supported fields.
3. Place in scene.
4. Pick up.
5. Verify behavior.

============================================================
83. ROUND-TRIP TESTS
============================================================

Para `.NOT`:

crear corpus de tests.

Comparar:

read → write → read

y asegurar equivalencia estructural.

No probar sólo un archivo.

============================================================
84. FUZZ / CORRUPTION SAFETY
============================================================

El parser `.NOT` nunca debe causar pérdidas sobre originales.

Debe detectar archivos truncados/malformados y fallar limpiamente.

============================================================
85. NO MODIFICAR ARCHIVOS ORIGINALES
============================================================

Todo override/template custom debe generarse dentro del Build/proyecto.

Nunca modificar:

Global.not
modernDay.not
darkAges.not
Multiplayer.not

originales.

============================================================
86. DEPENDENCY MANAGER
============================================================

Preparar soporte básico para dependencias entre proyectos/packages.

Ejemplo:

Requires:
Community Resource Pack >= 1.2

No desarrollar repositorio online.

Sólo modelo/validation local.

============================================================
87. SCRIPT ESCAPE HATCH
============================================================

Usuarios avanzados pueden necesitar código.

Permitir opcionalmente:

Custom Script Hook

pero:

- claramente marcado Advanced;
- no requerido para uso normal;
- integrado con build;
- validado/compilado;
- no sustituye herramientas visuales.

============================================================
88. GENERATED JAVA OWNERSHIP
============================================================

Distinguir:

generated Java

de:

user custom Java

para que Build nunca sobrescriba código manual.

============================================================
89. ADVANCED MODE
============================================================

Considerar un modo avanzado que muestre:

- internal IDs;
- raw resource names;
- generated API mapping;
- Codex methods;
- raw template fields.

Modo normal debe seguir siendo amigable.

============================================================
90. RAW TEMPLATE INSPECTOR
============================================================

Para ingeniería inversa:

mostrar propiedades desconocidas en modo técnico:

Offset
Type guess
Raw bytes
String refs

Esto ayudará en fases futuras.

============================================================
91. FORMAT RESEARCH TOOLS
============================================================

Mantener tooling separado para:

- binary diff;
- structure dump;
- string extraction;
- template comparison;
- hexdump annotations.

Estas herramientas pueden vivir en:

tools/research/

============================================================
92. NO EDITAR GEOMETRÍA
============================================================

Todavía NO:

- crear levels;
- modificar brushes;
- modificar BSP;
- cambiar arquitectura;
- mover paredes;
- modificar geometría original.

Esto pertenece a una posible fase futura independiente.

============================================================
93. CRITERIO DE USABILIDAD
============================================================

Al final de Fase 5, un usuario debería poder:

- instalar/abrir Chronicle Maker;
- detectar su juego;
- crear proyecto;
- elegir level;
- clonar un actor original;
- convertirlo en template propio;
- colocar actor;
- crear conversación;
- crear quest;
- crear encounter;
- crear secuencia;
- Build;
- Playtest;
- Debug;
- Export;
- compartir package.

Sin saber:

Java
.nco
.nsc
.nmf
.nqd
.nai
.not
.nob

salvo que quiera entrar en modo avanzado.

============================================================
94. PRUEBA DE ACEPTACIÓN COMPLETA
============================================================

Crear una nueva crónica de demostración exclusivamente desde Redemption Chronicle Maker.

Debe incluir:

- mínimo 2 levels;
- mínimo 5 NPC;
- al menos 1 ACTOR TEMPLATE PERSONALIZADO generado por nuestro `.NOT` writer;
- al menos 1 AI profile propio si está soportado;
- mínimo 2 quests;
- al menos 1 item relevante;
- conversación con varias ramas;
- conversación condicionada por estado;
- encounter;
- cámara/secuencia;
- audio;
- transición;
- trigger;
- relaciones;
- custom template;
- debug trace;
- build;
- deploy;
- playtest.

============================================================
95. PRUEBA REAL EN REDEMPTION
============================================================

Muy importante.

El soporte `.NOT` NO se considera terminado por pasar tests internos.

Debe probarse dentro de Redemption.

Verificar:

- juego arranca;
- crónica carga;
- custom template existe;
- actor puede instanciarse;
- modelo correcto;
- comportamiento correcto;
- conversación;
- AI;
- inventario cuando aplique;
- guardado/carga no rompe.

============================================================
96. FALLBACK
============================================================

Si `.NOT` writer no alcanza suficiente fiabilidad durante Fase 5:

NO fingir éxito.

Entregar:

- reader sólido;
- documentación completa;
- writer experimental aislado;
- resultados de pruebas;
- fallos concretos.

Pero continuar el resto de Fase 5.

La prioridad absoluta es no producir archivos capaces de corromper proyectos o builds silenciosamente.

============================================================
97. TEST SUITE
============================================================

Mantener todo lo anterior.

Añadir tests para:

- NOT reader;
- NOT writer;
- roundtrip;
- templates;
- custom resources;
- AI profiles;
- graph editor model;
- debug mapping;
- package manifest;
- install/uninstall package;
- project migration;
- backups;
- release build.

============================================================
98. DOCUMENTACIÓN
============================================================

Actualizar todo lo existente.

Crear cuando corresponda:

docs/NOT_WRITER.md
docs/TEMPLATES.md
docs/CUSTOM_RESOURCES.md
docs/DEBUGGING.md
docs/PACKAGES.md
docs/RELEASE_BUILD.md
docs/PROJECT_FORMAT.md

============================================================
99. PHASE 5 REPORT
============================================================

Crear:

docs/PHASE5_REPORT.md

Debe contener:

IMPLEMENTADO

.NOT READER

.NOT WRITER

CUSTOM ACTOR TEMPLATES

CUSTOM ITEMS

CUSTOM AI

RESOURCE PIPELINE

CONVERSATION GRAPH

VISUAL SCRIPTING

CINEMATICS

DEBUGGING

PLAYTEST

PACKAGING

APPLICATION BUILD

PROBADO AUTOMÁTICAMENTE

PROBADO EN REDEMPTION

NO PROBADO

LIMITACIONES

BUGS CONOCIDOS

FORMATOS PENDIENTES

DEUDA TÉCNICA

PROPUESTA PARA FASE 6

============================================================
100. PRIORIDADES EN CASO DE FALTA DE TIEMPO
============================================================

Priorizar exactamente:

1. Regression safety.
2. `.NOT` reader.
3. `.NOT` writer seguro.
4. Custom Actor Templates.
5. Test real en Redemption.
6. Debugging / Event Trace.
7. AI editor.
8. Conversation Graph.
9. Cinematic improvements.
10. Packaging de crónicas.
11. Executable Windows.
12. Polish.

NO entregar veinte features superficiales dejando `.NOT` a medias si el objetivo principal todavía no está resuelto.

============================================================
101. FILOSOFÍA DE CALIDAD
============================================================

Cada feature importante debe recorrer:

MODEL
↓
GUI
↓
VALIDATION
↓
SERIALIZATION
↓
BUILD
↓
RUNTIME
↓
TEST

No considerar una función terminada porque exista un control visual.

============================================================
102. QUÉ NO HACER
============================================================

NO:

- editar geometría;
- crear un level editor completo;
- desarrollar un motor 3D nuevo;
- remake del juego;
- reemplazar el runtime;
- hooking complejo;
- inyección de DLL;
- tocar ejecutable;
- parchear binarios innecesariamente;
- desarrollar marketplace;
- integración cloud;
- sistema online;
- multiplayer editor completo.

============================================================
103. RESULTADO ESPERADO
============================================================

Después de esta fase Redemption Chronicle Maker debe haber evolucionado de:

"editor moderno de crónicas basado en recursos existentes"

a:

"ENTORNO MODERNO DE AUTORÍA PARA REDEMPTION"

capaz de:

CREAR
EDITAR
VISUALIZAR
VALIDAR
COMPILAR
DEPURAR
PROBAR
EMPAQUETAR
COMPARTIR

crónicas completas.

Y, de forma especialmente importante:

crear TEMPLATES PROPIOS sin NOT Editor.

============================================================
104. REVISIÓN FINAL
============================================================

Antes de terminar:

- ejecutar TODOS los tests;
- abrir proyectos antiguos;
- migrarlos si procede;
- comprobar viewport;
- comprobar Resource Browser;
- comprobar custom templates;
- comprobar Build;
- comprobar Deploy;
- comprobar Playtest;
- comprobar debug mapping;
- comprobar Release Package;
- comprobar portable application;
- comprobar documentación.

============================================================
105. REGLA FINAL
============================================================

NO empezar Fase 6.

Al terminar detenerse.

No declarar `.NOT` writer estable sin prueba real dentro del juego.

No sacrificar proyectos existentes.

No introducir dependencia de herramientas originales.

Redemption Chronicle Maker debe continuar cumpliendo la promesa central:

NINGUNA HERRAMIENTA DE AUTORÍA DE HACE 25 AÑOS.

ÚNICAMENTE EL JUEGO COMO RUNTIME Y FUENTE DE RECURSOS.

Todo lo demás debe poder hacerse desde una herramienta moderna construida por nosotros.

El objetivo no es recrear Embrace.

El objetivo es construir el entorno de creación que Vampire: The Masquerade — Redemption debería haber tenido desde el principio.
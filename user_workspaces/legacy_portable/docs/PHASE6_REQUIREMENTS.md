REDEMPTION CHRONICLE MAKER — FASE 6
ESTABILIZACIÓN, AUDITORÍA EXHAUSTIVA, COBERTURA DE HUECOS Y TEST SUITE DE NIVEL BETA

La Fase 5 está terminada.

Ahora comienza la Fase 6.

Esta fase NO debe centrarse principalmente en añadir grandes subsistemas nuevos.

El objetivo es convertir todo lo construido hasta ahora en una BASE FIABLE, COHERENTE Y COMPROBADA.

Redemption Chronicle Maker ya debe disponer, en distinto grado, de:

- backend de generación;
- proyectos modernos;
- GUI;
- viewport 3D;
- levels originales;
- actores;
- templates;
- conversaciones;
- quests;
- eventos;
- conditions/actions;
- Chronicle Flags;
- items;
- encounters;
- triggers;
- secuencias/cámaras;
- audio;
- IA;
- build;
- deploy;
- playtest;
- debugging;
- Resource Browser;
- Find References;
- validación;
- packaging;
- soporte propio de .NOT cuando haya quedado validado;
- ejecutable/distribución cuando proceda.

La Fase 6 debe comprobar de forma sistemática que TODO ESO FUNCIONA DE VERDAD.

============================================================
OBJETIVO PRINCIPAL
============================================================

Esta fase tiene cinco objetivos absolutos:

1. AUDITAR todo el código existente.
2. ENCONTRAR huecos, stubs, falsas implementaciones y paths no terminados.
3. COMPLETAR las funciones necesarias para crear crónicas completas.
4. CREAR tests exhaustivos y fiables.
5. CONSEGUIR que una regresión futura sea detectada automáticamente.

La prioridad no es el número de features.

La prioridad es CONFIANZA.

Al terminar Fase 6 quiero poder preguntarme:

"¿Puedo tocar una parte del proyecto sin romper silenciosamente otras diez?"

y que la respuesta razonable sea:

"SÍ, los tests deberían detectarlo."

============================================================
1. NO DAR NADA POR FUNCIONAL
============================================================

No asumir que algo funciona porque:

- existe un botón;
- existe una clase;
- existe un método;
- existe código generado;
- existe documentación;
- pasó una prueba manual antigua.

Revisar cada subsystem desde:

MODEL
→ GUI
→ SERIALIZATION
→ VALIDATION
→ GENERATOR
→ BUILD
→ DEPLOY
→ RUNTIME

Una feature que sólo funciona hasta mitad del pipeline NO está terminada.

============================================================
2. INVENTARIO COMPLETO DE FEATURES
============================================================

Crear:

docs/FEATURE_MATRIX.md

Debe enumerar sistemáticamente todas las funciones existentes.

Ejemplo:

FEATURE
Actor creation

MODEL:
PASS

GUI:
PASS

SAVE/LOAD:
PASS

VALIDATION:
PASS

GENERATOR:
PASS

BUILD:
PASS

RUNTIME TEST:
PASS


Otro ejemplo:

Custom Item Template

MODEL:
PASS

GUI:
PASS

SAVE/LOAD:
PASS

VALIDATION:
PASS

GENERATOR:
PARTIAL

RUNTIME TEST:
NOT TESTED

Cada feature debe tener estado explícito:

PASS
PARTIAL
FAIL
NOT IMPLEMENTED
NOT TESTED
NOT APPLICABLE

No esconder huecos.

============================================================
3. BUSCAR IMPLEMENTACIONES FALSAS
============================================================

Buscar en todo el proyecto:

TODO
FIXME
HACK
XXX
pass
NotImplemented
raise NotImplementedError
placeholder
mock
dummy
temporary
stub
future
unsupported
experimental

Analizar cada aparición.

Clasificar:

- legítima;
- deuda técnica;
- implementación incompleta;
- funcionalidad falsa;
- código muerto.

No borrar ciegamente.

============================================================
4. DETECTAR GUI SIN BACKEND
============================================================

Buscar controles visuales que:

- no modifican modelo;
- no guardan;
- no generan output;
- llaman a funciones vacías;
- muestran datos estáticos;
- sólo funcionan durante la sesión;
- desaparecen al recargar proyecto.

Crear tests o arreglarlos.

============================================================
5. DETECTAR BACKEND SIN GUI
============================================================

Buscar capacidades útiles del backend que existan pero no estén expuestas adecuadamente.

Sólo cubrirlas si son necesarias para crear una crónica completa.

NO convertir esta auditoría en una excusa para añadir cien features secundarias.

============================================================
6. AUDITAR MODELO INTERNO
============================================================

Revisar todos los modelos:

- Chronicle;
- Level;
- Actor;
- Template;
- Conversation;
- Conversation Node;
- Quest;
- Quest Step;
- Event;
- Condition;
- Action;
- Flag;
- Trigger;
- Item;
- Encounter;
- Sequence;
- Camera;
- Audio;
- AI;
- Path;
- Resource;
- Package;
- otros existentes.

Comprobar:

- defaults;
- IDs;
- references;
- optional fields;
- invalid states;
- copy;
- delete;
- rename;
- serialization.

============================================================
7. TESTS DE SERIALIZACIÓN
============================================================

Cada modelo persistente debe tener:

CREATE
→ SAVE
→ LOAD
→ COMPARE

El resultado debe conservar semánticamente el proyecto.

Añadir round-trip tests.

No confiar únicamente en tests unitarios de campos individuales.

============================================================
8. PROJECT FORMAT MIGRATIONS
============================================================

Probar proyectos de versiones anteriores.

Crear fixtures reales o simplificados de:

Phase 1
Phase 2
Phase 3
Phase 4
Phase 5

Abrirlos con versión actual.

Verificar:

- migración;
- backup;
- contenido;
- references;
- build.

============================================================
9. TESTS DE REFERENCIAS
============================================================

Crear cobertura fuerte para referencias.

Ejemplos:

Actor → Conversation
Conversation → Actor
Quest → Event
Event → Actor
Event → Flag
Trigger → Event
Encounter → Actors
Sequence → Camera
Item → Quest
Transition → Level

Comprobar:

- references válidas;
- references rotas;
- rename;
- delete;
- duplicate;
- copy/paste.

============================================================
10. SAFE RENAME
============================================================

Testear exhaustivamente rename.

Ejemplo:

Victoria
→ VictoriaVentrue

Debe actualizar TODAS las referencias conocidas.

Después:

Validate
→ 0 broken references

Añadir tests para cada tipo renombrable.

============================================================
11. SAFE DELETE
============================================================

Probar borrar una entidad con:

0 references
1 reference
muchas references

Verificar:

- warning;
- cancel;
- delete;
- cleanup;
- validation posterior.

============================================================
12. COPY / DUPLICATE
============================================================

Testear duplicación de:

- actor;
- trigger;
- event;
- quest;
- conversation;
- sequence;
- item;
- templates si está soportado.

Los IDs nuevos deben ser válidos y no colisionar.

============================================================
13. UNDO / REDO
============================================================

Auditar operaciones principales.

Testear:

change property
undo
redo

move actor
undo
redo

create actor
undo
redo

delete actor
undo
redo

conversation edit
undo
redo

quest edit
undo
redo

No aceptar corrupción del modelo después de chains largos.

============================================================
14. AUTOSAVE
============================================================

Testear:

- autosave normal;
- cierre inesperado;
- recovery;
- discard recovery;
- save tras recovery;
- autosave de proyecto inválido.

Nunca sobrescribir silenciosamente un proyecto válido con datos corruptos.

============================================================
15. BACKUPS
============================================================

Comprobar:

- creación;
- rotación;
- recuperación;
- límites;
- nombres;
- timestamps.

============================================================
16. RESOURCE INDEX
============================================================

Auditar completamente el catálogo de recursos.

Comprobar:

- duplicados;
- paths;
- case sensitivity;
- nombres raros;
- resources faltantes;
- colisiones;
- cache invalidation.

============================================================
17. RESOURCE CACHE
============================================================

Tests:

empty cache
build cache
load cache
corrupt cache
delete cache
rebuild cache
game resources changed

La aplicación debe recuperarse de cache corrupta.

============================================================
18. LEVEL CATALOG
============================================================

Validar todos los levels detectados.

Para cada level catalogado, comprobar al menos:

- referencia existe;
- metadata parseable;
- scene links;
- geometry availability;
- texture references básicas.

Crear informe.

============================================================
19. VIEWPORT STABILITY
============================================================

Realizar stress tests razonables del viewport.

Probar:

- cargar level;
- cambiar level repetidamente;
- abrir/cerrar proyecto;
- crear muchas entidades;
- seleccionar rápidamente;
- mover objetos;
- triggers;
- gizmos;
- hide/show layers.

Buscar:

- leaks;
- crashes;
- stale references;
- duplicated entities;
- desync GUI/model.

============================================================
20. VIEWPORT SAVE CONSISTENCY
============================================================

Colocar actor visualmente.

Guardar.

Cerrar.

Abrir.

Debe aparecer exactamente en la misma posición/orientación.

Testear lo mismo con:

- triggers;
- objects;
- cameras;
- waypoints;
- otros elementos espaciales.

============================================================
21. COORDINATE PRECISION
============================================================

Comprobar pérdida de precisión.

Especialmente:

X
Y
Z
rotation
trigger dimensions
camera transform

No acumular drift después de múltiples save/load.

============================================================
22. PICKING
============================================================

Auditar picking.

Probar:

- actors;
- triggers;
- objects;
- overlapping entities;
- hidden layers;
- original entities;
- editable entities.

No seleccionar elementos ocultos cuando no corresponda.

============================================================
23. RELATIONSHIPS
============================================================

Testear:

Find References

para TODOS los tipos importantes.

Debe devolver:

- referencias entrantes;
- referencias salientes.

Comparar contra modelo real.

============================================================
24. RELATIONSHIP CACHE / INDEX
============================================================

Si existe índice de references:

crear tests para invalidarlo/actualizarlo después de:

- add;
- remove;
- rename;
- duplicate;
- load;
- migration.

============================================================
25. CONVERSATION ENGINE
============================================================

Crear suite completa de conversaciones.

Casos:

simple line
multiple lines
two answers
GOTO
RETURN
nested branches
cycles
multiple returns
unreachable node
missing node
missing speaker
empty text
special characters
Unicode
long text

============================================================
26. CONVERSATION ROUND-TRIP
============================================================

GUI/model
→ generated .nco
→ parser/inspection cuando sea posible

Comprobar estructura.

============================================================
27. CONVERSATION GRAPH VS TREE
============================================================

Si existen ambas vistas:

editar en Tree
→ Graph refleja cambios

editar en Graph
→ Tree refleja cambios

Guardar/cargar
→ ambas siguen coincidiendo.

============================================================
28. QUEST TEST SUITE
============================================================

Casos:

single-step quest
multi-step quest
branching when supported
completion
quest item
conversation advancement
trigger advancement
actor death advancement
flag-based progression

============================================================
29. QUEST DEAD-END ANALYSIS
============================================================

Crear tests para Integrity Check.

Detectar:

- quest nunca iniciable;
- step sin completion path;
- next step inexistente;
- quest nunca completable.

No generar falsos positivos obvios en casos dinámicos válidos.

============================================================
30. FLAGS
============================================================

Testear:

set
clear
toggle
read
conditions
duplicate ID
duplicate alias
rename alias
delete referenced flag

============================================================
31. EVENT ENGINE
============================================================

Crear tests para cada evento soportado.

Ejemplos:

Scene Start
Scene End
Actor Clicked
Actor Killed
Actor Arrived
Player Enter Trigger
Player Exit Trigger
Item Pickup
Conversation End
Conversation Reached
Timer
Quest step events

============================================================
32. CONDITIONS
============================================================

Testear:

TRUE
FALSE
ALL
ANY
NOT

nested conditions si están soportadas.

Casos límite:

0 conditions
1 condition
invalid ref
contradictory conditions.

============================================================
33. ACTIONS
============================================================

Crear test individual para cada acción soportada.

Ejemplo:

Spawn Actor
Remove Actor
Start Conversation
Set Flag
Clear Flag
Advance Quest
Complete Quest
Give Item
Open Exit
Close Exit
Change Scene
Teleport
Play Sound
Music
Camera actions
AI target
etc.

Cada acción debe demostrar que:

model
→ generator

produce salida esperada.

============================================================
34. ACTION PARAMETER VALIDATION
============================================================

Ejemplos:

Spawn Actor without actor
Start Conversation missing conversation
Open Exit missing target
Give Item missing item

Deben producir errores claros.

============================================================
35. ENCOUNTERS
============================================================

Testear:

empty encounter
single actor
multiple actors
spawn
completion
open exit
quest advancement
music hooks
repeatable/nonrepeatable si existe.

============================================================
36. ITEMS
============================================================

Testear:

spawn item
pickup
inventory assignment
give
remove
quest item
item references
template validation.

============================================================
37. INVENTORY
============================================================

Testear inventario de actor:

empty
single item
multiple items
equipped
invalid item
duplicate item
unsupported slot.

============================================================
38. TEMPLATES
============================================================

Crear tests para:

clone template
modify template
save project
build
references
duplicate ID
invalid model
invalid AI
invalid script.

============================================================
39. `.NOT` READER
============================================================

Crear corpus de test real.

Incluir todos los `.NOT` originales disponibles.

Para cada uno:

parse
→ no crash

Enumerar templates.

Comparar counts conocidos.

============================================================
40. `.NOT` WRITER
============================================================

Si existe writer estable:

crear round-trip tests extensos.

read
→ write
→ read

Comparar:

- template IDs;
- propiedades conocidas;
- unknown raw fields;
- references.

============================================================
41. `.NOT` RUNTIME TESTS
============================================================

No confiar sólo en round-trip.

Crear templates personalizados de prueba.

Build.

Deploy.

Ejecutar Redemption.

Confirmar:

- juego arranca;
- template carga;
- actor aparece;
- actor funciona.

Documentar cada caso probado.

============================================================
42. AI
============================================================

Crear tests de parser/generator de `.nai` o sistema equivalente.

Casos:

original profile
cloned profile
modified profile
invalid value
unknown field
round-trip.

============================================================
43. PATHS / WAYPOINTS
============================================================

Testear:

single waypoint
multiple
loop
insert
delete
reorder
actor assignment
save/load.

============================================================
44. CAMERAS
============================================================

Testear:

creation
position
rotation
properties
sequence reference
delete referenced camera
save/load.

============================================================
45. SEQUENCES
============================================================

Testear:

camera
wait
actor movement
animation
conversation
audio
event
exit

y combinaciones.

============================================================
46. SEQUENCE ORDER
============================================================

Comprobar que acciones mantienen orden y timing correcto en output generado.

============================================================
47. AUDIO
============================================================

Testear:

resource lookup
missing audio
music actions
ambient
sound effect
voice references.

============================================================
48. MULTI-LEVEL
============================================================

Crear tests con:

2 levels
3 levels
repeated level references
invalid level
transition loops
missing destination.

============================================================
49. TRANSITIONS
============================================================

Testear cada mecanismo soportado:

Open Exit
Close Exit
Change Scene
Jump
Portal
Teleport

según implementación real.

============================================================
50. BUILD PIPELINE
============================================================

Crear suite específica de build.

Casos:

valid minimal project
valid complex project
invalid project
missing resources
Java compile error
generator error
package error
permission/path error
partial build.

El build debe fallar limpiamente.

============================================================
51. BUILD DETERMINISM
============================================================

Mismo proyecto
→ dos builds

Comparar output.

Debe ser idéntico o semánticamente equivalente salvo timestamps conocidos.

============================================================
52. GENERATED JAVA
============================================================

Crear tests para:

- syntax;
- imports;
- class names;
- escaping;
- large chronicles;
- multiple events;
- method size;
- IDs.

============================================================
53. JAVA COMPILATION
============================================================

Automatizar compilación de fixtures.

Todos los ejemplos válidos deben compilar.

Los inválidos deben producir error esperado.

============================================================
54. GENERATED FORMAT VALIDATION
============================================================

Para cada formato generado:

.nsc
.nmf
.nco
.nqd
.nai
.not
otros

crear validadores/parsers propios cuando sea razonable.

El generador no debe limitarse a escribir texto.

Debe poder verificar su propia salida.

============================================================
55. PACKAGE TESTS
============================================================

Testear:

create package
inspect manifest
install
conflict
upgrade
uninstall
reinstall.

============================================================
56. INSTALL / UNINSTALL SAFETY
============================================================

Crear sandbox/directorio falso de juego para tests.

Nunca depender del juego real para comprobar operaciones de filesystem.

Verificar que uninstall:

sólo elimina archivos propiedad del paquete.

============================================================
57. PROJECT EXPORT / IMPORT
============================================================

Testear:

export
delete original
import
build

Debe conservar proyecto.

============================================================
58. CUSTOM RESOURCES
============================================================

Testear packaging de recursos propios.

Comprobar que no se incluyan accidentalmente recursos originales innecesarios.

============================================================
59. APP PACKAGING
============================================================

Construir executable/portable actual.

Probar en entorno limpio cuando sea posible.

Debe detectar dependencias faltantes.

============================================================
60. FIRST RUN
============================================================

Testear:

no settings
game detected
game not found
cache absent
cache corrupt
existing cache.

============================================================
61. SETTINGS
============================================================

Testear persistencia de:

game path
viewport prefs
autosave
debug options.

Settings inválidos no deben impedir arrancar la aplicación.

============================================================
62. CRASH STARTUP SAFETY
============================================================

Muy importante:

La aplicación NO debe quedar inutilizable por una configuración gráfica corrupta.

Si viewport/render settings provocan crash:

implementar estrategia segura:

- safe defaults;
- reset settings;
- fallback renderer cuando sea razonable.

Crear:

Reset Application Settings

accesible cuando sea posible.

============================================================
63. LARGE PROJECT FIXTURE
============================================================

Crear automáticamente un proyecto sintético grande.

Por ejemplo:

5 levels
100 actors
50 conversations
20 quests
100 events
50 triggers
30 items
varias sequences

No tiene que ser narrativamente bonito.

Debe servir para stress test.

============================================================
64. LARGE PROJECT PERFORMANCE
============================================================

Medir:

load time
save time
validation
Find References
global search
build
viewport interaction.

Detectar operaciones O(n²) absurdas.

============================================================
65. MEMORY / RESOURCE LEAKS
============================================================

Investigar especialmente:

- level switching;
- textures;
- viewport;
- project reload;
- caches.

No exigir tooling extremadamente complejo, pero corregir leaks obvios.

============================================================
66. FUZZ TESTING DE PARSERS
============================================================

Aplicar fuzz ligero/controlled mutations a formatos críticos.

Especialmente:

.NOT
YAML/project
resource metadata
conversation inputs

El parser debe fallar limpiamente.

============================================================
67. PROPERTY-BASED TESTING
============================================================

Cuando sea útil, usar property-based tests.

Ejemplo:

random valid IDs
random positions
random simple conversation graphs
random flags

serialize
→ deserialize

debe preservar modelo.

============================================================
68. BAD INPUT TESTING
============================================================

Probar:

invalid Unicode
very long names
illegal IDs
empty IDs
duplicate IDs
negative values
NaN
infinite floats
huge positions
invalid paths.

============================================================
69. PATH HANDLING
============================================================

Testear rutas Windows:

spaces
Unicode
deep paths
different drives
read-only paths
missing paths.

============================================================
70. ERROR UX
============================================================

Auditar todos los errores importantes.

No mostrar normalmente:

Traceback
KeyError
IndexError

Mostrar:

qué ocurrió
qué elemento está afectado
cómo solucionarlo cuando sea posible.

============================================================
71. LOGGING
============================================================

Revisar logs.

Debe existir separación razonable:

INFO
WARNING
ERROR
DEBUG

No llenar disco indefinidamente.

============================================================
72. DIAGNOSTIC REPORT
============================================================

Probar que Diagnostics puede generarse incluso si:

- project fails;
- cache fails;
- game path invalid;
- viewport unavailable.

============================================================
73. DEAD CODE
============================================================

Buscar código no utilizado.

Eliminar sólo después de comprobar references/tests.

============================================================
74. DUPLICATED LOGIC
============================================================

Buscar implementaciones duplicadas entre:

CLI
GUI
Build
Validators
Viewport

Unificar cuando sea seguro.

============================================================
75. EXCEPTION HANDLING
============================================================

Buscar:

except Exception:
    pass

o equivalentes.

Revisar uno por uno.

No ocultar errores silenciosamente.

============================================================
76. TYPE CHECKING
============================================================

Si el proyecto utiliza type hints:

ampliarlos en áreas críticas.

Ejecutar checker apropiado si encaja con el proyecto.

No dedicar la fase entera a satisfacer typing cosmético.

============================================================
77. LINT / STATIC ANALYSIS
============================================================

Configurar herramientas razonables.

Por ejemplo:

ruff
mypy/pyright si procede

Pero:

NO reformatear medio proyecto innecesariamente.

============================================================
78. SECURITY BÁSICA
============================================================

Aunque sea aplicación local, revisar:

- path traversal en packages;
- ZIP extraction;
- overwrites;
- arbitrary file delete;
- package install paths.

Un `.rcmpack` malicioso no debe poder escribir fuera del destino permitido.

============================================================
79. PACKAGE TRUST
============================================================

No ejecutar automáticamente scripts arbitrarios importados sin advertencia.

Si existe custom Java:

marcar package con código custom.

Informar antes de instalar/build.

============================================================
80. TEST DATA SEPARATION
============================================================

Tests no deben depender innecesariamente de la instalación real.

Crear fixtures pequeños.

Los integration tests que necesiten Redemption deben marcarse separadamente.

============================================================
81. TEST CATEGORIES
============================================================

Organizar tests:

UNIT
INTEGRATION
FORMAT
GUI-MODEL
BUILD
PACKAGE
RUNTIME
PERFORMANCE

Debe poder ejecutarse:

fast tests

sin necesitar el juego.

============================================================
82. TEST COMMANDS
============================================================

Documentar comandos.

Ejemplo conceptual:

pytest

pytest -m unit

pytest -m integration

pytest -m runtime

Ajustar a arquitectura real.

============================================================
83. TEST REPORT
============================================================

Generar reporte legible.

No necesito perseguir 100% de cobertura artificial.

Sí necesito saber qué partes críticas carecen de tests.

============================================================
84. CODE COVERAGE
============================================================

Medir cobertura.

Identificar módulos críticos con poca cobertura.

Priorizar:

model
serialization
validation
generators
formats
build
references
packages.

No obsesionarse con widgets triviales.

============================================================
85. COVERAGE TARGET
============================================================

No exigir porcentaje arbitrario global.

Sí establecer objetivo fuerte para lógica crítica.

Como guía:

core/backend:
muy alta cobertura.

GUI visual:
cobertura razonable mediante model/controller tests.

============================================================
86. RUNTIME TEST MATRIX
============================================================

Crear:

docs/RUNTIME_TEST_MATRIX.md

Debe listar pruebas que requieren Redemption real.

Ejemplo:

Minimal Chronicle        PASS
Actor Spawn              PASS
Conversation Branch      PASS
Quest Advance            PASS
Custom NOT Actor         PASS
Item Pickup              PASS
Scene Transition         PASS
Camera Sequence          PASS
AI Profile               PASS
Save/Load                NOT TESTED

============================================================
87. MANUAL PLAYTEST SCRIPT
============================================================

Crear una crónica específica para probar sistemas.

Nombre sugerido:

RCM_SystemTest

No debe ser una aventura bonita.

Debe contener zonas/pruebas claramente separadas.

Ejemplo:

NPC TEST
CONVERSATION TEST
QUEST TEST
ITEM TEST
TRIGGER TEST
AI TEST
CAMERA TEST
TRANSITION TEST

============================================================
88. SYSTEM TEST CHRONICLE
============================================================

Esta crónica debe ser generada por Chronicle Maker.

No editar archivos generados manualmente salvo diagnóstico.

Debe convertirse en regression fixture oficial.

============================================================
89. IN-GAME TEST CHECKLIST
============================================================

Crear checklist.

Ejemplo:

[ ] Chronicle appears
[ ] Level loads
[ ] Actor spawns
[ ] Actor clickable
[ ] Conversation starts
[ ] Answer 1 works
[ ] Answer 2 works
[ ] Flag changes
[ ] Quest advances
[ ] Item pickup works
[...]

============================================================
90. SAVE/LOAD EN REDEMPTION
============================================================

Probar especialmente:

save game
exit
reload
continue

Verificar:

- flags;
- quests;
- actors cuando corresponda;
- state.

Los problemas de persistencia son críticos.

============================================================
91. REPEATED PLAYTEST
============================================================

Probar crónica varias veces desde cero.

Detectar estados residuales o resources que no se limpian.

============================================================
92. BUILD → DEPLOY → PLAY LOOP
============================================================

Optimizar sólo si resulta necesario.

Debe ser suficientemente cómodo para iterar:

Edit
→ Build
→ Deploy
→ Run

No añadir features nuevas gigantescas.

============================================================
93. DOCUMENTAR BUGS REALES
============================================================

Crear:

docs/KNOWN_ISSUES.md

Cada issue:

ID
Description
Severity
Reproduction
Status
Workaround
Fixed version

============================================================
94. BUG SEVERITY
============================================================

Clasificar:

BLOCKER
CRITICAL
MAJOR
MINOR
COSMETIC

Priorizar:

BLOCKER
CRITICAL
MAJOR

antes del polish.

============================================================
95. REGRESSION TEST POR BUG
============================================================

Regla importante:

Cuando se arregle un bug reproducible importante:

añadir test que falle antes del fix y pase después.

Evitar arreglos que puedan reaparecer silenciosamente.

============================================================
96. GUI WORKFLOW TESTING
============================================================

Recorrer manualmente flujos completos:

NEW PROJECT
→ LEVEL
→ ACTOR
→ CONVERSATION
→ QUEST
→ EVENT
→ BUILD

y otros flujos principales.

Buscar:

- controles confusos;
- estados imposibles;
- botones inactivos;
- selección perdida;
- datos que no guardan.

============================================================
97. KEYBOARD / SHORTCUTS
============================================================

Comprobar que shortcuts no colisionan.

Ctrl+S
Ctrl+Z
Ctrl+Y
Delete
F5
etc.

============================================================
98. SELECTION STATE
============================================================

Comprobar coordinación:

Viewport
Outliner
Properties
References
Graph
Conversation
Quest

La selección no debe quedarse desincronizada.

============================================================
99. UNSAVED CHANGES
============================================================

Testear:

close app
open new
open other project
exit
crash recovery

No perder trabajo.

============================================================
100. ERROR IN ONE PANEL
============================================================

Un error al cargar un preview o recurso no debe derribar toda la aplicación.

Aislar fallos cuando sea razonable.

============================================================
101. MISSING ORIGINAL RESOURCE
============================================================

Simular recurso original faltante.

La aplicación debe indicar cuál falta y continuar cuando sea posible.

============================================================
102. CUSTOM RESOURCE OVERRIDES
============================================================

Testear prioridad correcta entre:

original
project override
generated resource

No crear colisiones silenciosas.

============================================================
103. CASE SENSITIVITY
============================================================

Investigar comportamiento real del runtime.

Validar nombres de recursos en consecuencia.

Windows puede esconder bugs de case que después compliquen tooling.

============================================================
104. SPECIAL CHARACTERS
============================================================

Probar nombres/textos con:

acentos
ñ
apóstrofes
comillas
símbolos

Especialmente conversaciones y strings.

============================================================
105. LONG DIALOGUES
============================================================

Crear conversaciones grandes para detectar:

- límites;
- Java method size;
- generated file issues;
- UI degradation.

============================================================
106. LARGE GENERATED JAVA
============================================================

Investigar si crónicas grandes pueden superar límites de Java antiguo.

Si existe riesgo:

dividir generación de forma segura.

No esperar a que un proyecto real reviente.

============================================================
107. JAVA 1.1 COMPATIBILITY
============================================================

Auditar generated Java.

No utilizar accidentalmente sintaxis/API moderna incompatible con runtime original.

Añadir tests específicos.

============================================================
108. GENERATED IDENTIFIERS
============================================================

IDs del usuario pueden no ser Java-valid.

Crear saneamiento consistente.

Ejemplo:

"Victoria Intro"

no debe romper class/method generation.

Mantener mapping reversible.

============================================================
109. STRING ESCAPING
============================================================

Testear:

quotes
backslash
newline
Unicode
long strings

en output Java y formatos NOD.

============================================================
110. BUILD CLEAN
============================================================

Añadir:

Clean Build

y probar que elimina únicamente output generado.

No borrar fuentes.

============================================================
111. BUILD AFTER FAILURE
============================================================

Probar:

build fails
fix project
build again

No dejar artifacts corruptos contaminando siguiente build.

============================================================
112. ATOMIC BUILD
============================================================

Cuando sea práctico:

generar en staging/temp

y mover resultado final sólo después de éxito.

Evitar build medio generado.

============================================================
113. DEPLOY AFTER FAILURE
============================================================

Nunca desplegar automáticamente un build que falló validación/compilación.

============================================================
114. VERSION COMPATIBILITY
============================================================

Comprobar:

project format version
application version
package version

Mensajes claros ante incompatibilidad.

============================================================
115. APPLICATION STARTUP
============================================================

Medir startup.

No reconstruir caches grandes siempre.

============================================================
116. PROJECT LOAD
============================================================

No bloquear absurdamente con proyectos grandes.

Mostrar progress cuando haga falta.

============================================================
117. THREADING
============================================================

Revisar operaciones pesadas.

No tocar widgets Qt desde threads incorrectos.

Buscar race conditions básicas.

============================================================
118. CANCELLATION
============================================================

Para tareas largas cuando sea razonable:

cache rebuild
resource scan

permitir cancelación segura.

No es imprescindible para builds muy rápidos.

============================================================
119. DOCUMENTATION AUDIT
============================================================

Revisar toda documentación.

Eliminar afirmaciones obsoletas.

Actualizar screenshots/textos cuando proceda.

============================================================
120. EDITOR GUIDE
============================================================

EDITOR_GUIDE debe permitir a alguien sin conocimiento interno crear una crónica sencilla.

No explicar Java salvo en Advanced.

============================================================
121. TROUBLESHOOTING
============================================================

Crear/actualizar:

docs/TROUBLESHOOTING.md

Casos:

game not detected
build fails
Java compile fails
missing resource
viewport unavailable
package conflict
custom template fails.

============================================================
122. TESTING GUIDE
============================================================

Crear:

docs/TESTING.md

Explicar:

- estructura;
- cómo ejecutar;
- markers;
- fixtures;
- runtime tests;
- cómo añadir regression test.

============================================================
123. CONTRIBUTOR QUALITY BAR
============================================================

Crear instrucciones breves para futuras modificaciones:

Nueva feature no se acepta sin:

- modelo;
- validación;
- serialization;
- generator;
- tests.

============================================================
124. FEATURE GAPS
============================================================

Después de auditoría, crear lista de huecos REALES.

Clasificar:

REQUIRED FOR FULL CHRONICLE AUTHORING

USEFUL

OPTIONAL

NO IMPLEMENTAR

============================================================
125. CUBRIR HUECOS CRÍTICOS
============================================================

Completar durante Fase 6 cualquier hueco que impida crear una crónica completa.

Ejemplos posibles:

- una acción existe pero no genera;
- quest no persiste;
- items no funcionan en build;
- transition sólo está en GUI;
- actor template no llega al package.

No esperar a Fase 7 para arreglar funcionalidades básicas rotas.

============================================================
126. NO EXPANSIÓN DESCONTROLADA
============================================================

NO añadir grandes features nuevas sólo porque aparezcan durante auditoría.

Preguntar:

"¿Es necesario para que una crónica completa funcione?"

Si NO:

documentar para Fase 7 o backlog.

============================================================
127. DEFINICIÓN DE "CRÓNICA COMPLETA"
============================================================

Para esta auditoría, debe ser posible construir:

- múltiples levels;
- NPC;
- enemigos;
- conversaciones ramificadas;
- condiciones;
- quests;
- items;
- inventario/recompensas cuando estén soportados;
- triggers;
- encounters;
- transitions;
- flags;
- AI;
- audio;
- cámaras/sequences;
- custom templates;
- build;
- deploy;
- playtest;
- package.

============================================================
128. GOLDEN TEST PROJECT
============================================================

Crear una crónica más representativa que SystemTest.

Nombre sugerido:

RCM_GoldenChronicle

Debe utilizar casi todos los sistemas principales juntos.

============================================================
129. GOLDEN BUILD
============================================================

Guardar expectativas del build.

No necesariamente bytes completos si cambian detalles.

Comparar estructura/semántica.

============================================================
130. END-TO-END AUTOMATED TEST
============================================================

Debe existir al menos un test grande:

create/load project
→ validate
→ generate
→ compile
→ package

sin interacción manual.

============================================================
131. END-TO-END GUI MODEL TEST
============================================================

Simular mediante APIs/controladores principales:

create actor
create conversation
create quest
save
reload
build.

No hace falta robotizar clicks pixel a pixel.

============================================================
132. RUNTIME TEST LIMIT
============================================================

Los tests automáticos NO deben afirmar que algo funciona dentro del juego si no han ejecutado realmente Redemption.

Mantener separación:

AUTOMATED
GENERATED
RUNTIME VERIFIED

============================================================
133. PERFORMANCE BASELINE
============================================================

Crear:

docs/PERFORMANCE.md

Registrar tiempos aproximados de:

startup
project load
validation
build
large project load
cache generation.

Esto permitirá detectar regresiones futuras.

============================================================
134. TEST FAILURE QUALITY
============================================================

Los tests deben fallar con mensajes comprensibles.

No crear suites tan opacas que nadie sepa qué sistema rompió.

============================================================
135. FLAKY TESTS
============================================================

Evitar dependencia de:

timing exacto
orden filesystem arbitrario
paths locales
red
estado global.

Un test flaky es deuda.

============================================================
136. TEMP FILE CLEANUP
============================================================

Tests/build deben limpiar temporales incluso tras fallo cuando sea posible.

============================================================
137. CI-READY
============================================================

Dejar suite preparada para futura CI.

No hace falta configurar hosting remoto si no existe.

Sí hacer que los tests puedan ejecutarse por comando único.

============================================================
138. RELEASE BLOCKERS
============================================================

Crear:

docs/RELEASE_BLOCKERS.md

Al final de fase debe idealmente quedar:

0 BLOCKERS

0 CRITICAL

o documentar claramente los restantes.

============================================================
139. BETA READINESS
============================================================

Evaluar si la aplicación está preparada para:

PRIVATE BETA

NO asumir que sí.

Crear criterios objetivos.

============================================================
140. BETA CHECKLIST
============================================================

Ejemplo:

[ ] Starts on clean machine
[ ] Detects game
[ ] Creates project
[ ] Opens level
[ ] Places actor
[ ] Conversation builds
[ ] Quest builds
[ ] Custom template works
[ ] Deploy works
[ ] Package install works
[ ] Recovery works
[ ] No critical known crash

============================================================
141. MANUAL "IDIOT TEST"
============================================================

Realizar un flujo fingiendo no conocer el proyecto.

No utilizar terminal salvo funciones advanced.

Intentar crear crónica sólo desde GUI.

Anotar cualquier punto donde haga falta conocimiento oculto.

============================================================
142. REDUCIR FRICCIÓN
============================================================

Si una acción básica requiere demasiados pasos:

simplificarla.

Ejemplo:

No exigir crear manualmente evento + flag + callback para una interacción común si puede existir un wizard/preset que genere esos elementos correctamente.

============================================================
143. NO OCULTAR COMPLEJIDAD IRRECUPERABLE
============================================================

Los presets deben generar datos editables normales.

No crear magia cerrada imposible de modificar después.

============================================================
144. CLEAN PROJECT STRUCTURE
============================================================

Revisar estructura del repositorio.

Evitar:

- root lleno de archivos temporales;
- copias viejas;
- scripts abandonados;
- generated outputs versionados sin motivo.

============================================================
145. DEPENDENCY AUDIT
============================================================

Revisar dependencias Python.

Eliminar las no utilizadas.

Fijar versiones razonables cuando sea importante.

============================================================
146. LICENSE INVENTORY
============================================================

Crear lista de dependencias externas y licencias.

Importante de cara a distribución.

NO distribuir assets propietarios del juego.

============================================================
147. ORIGINAL GAME ASSETS
============================================================

Auditar package/app.

Verificar que no contiene accidentalmente:

- modelos originales;
- texturas originales;
- audio original;
- archivos NOB completos;
- otros assets propietarios.

La aplicación debe leerlos desde la instalación del usuario.

============================================================
148. CLEAN MACHINE TEST
============================================================

Cuando sea posible:

probar build portable en un entorno limpio o lo más equivalente posible.

Sin Python instalado.

Verificar startup y selección del juego.

============================================================
149. FINAL INTEGRITY RUN
============================================================

Antes de terminar Fase 6:

ejecutar:

- full test suite;
- static checks;
- feature matrix;
- golden project;
- system test project;
- build;
- package;
- migrations;
- cache rebuild.

============================================================
150. RUNTIME PLAYTEST FINAL
============================================================

Ejecutar Redemption con RCM_SystemTest y/o GoldenChronicle.

Recorrer checklist.

Actualizar RUNTIME_TEST_MATRIX.

============================================================
151. PHASE 6 REPORT
============================================================

Crear:

docs/PHASE6_REPORT.md

Debe contener:

SUMMARY

FEATURE MATRIX SUMMARY

TEST SUITE

TEST COUNTS

COVERAGE

RUNTIME TESTS

BUGS FOUND

BUGS FIXED

REGRESSIONS FOUND

FEATURE GAPS FOUND

FEATURE GAPS FIXED

KNOWN ISSUES

BLOCKERS

CRITICAL ISSUES

PERFORMANCE

PROJECT MIGRATIONS

.NOT STATUS

VIEWPORT STATUS

BUILD STATUS

DEPLOY STATUS

PACKAGE STATUS

BETA READINESS

RECOMMENDATIONS FOR PHASE 7

============================================================
152. CRITERIO DE ÉXITO
============================================================

La Fase 6 NO está terminada porque:

"todos los tests existentes pasan."

Los tests existentes también pueden ser insuficientes.

Está terminada cuando:

- hemos auditado sistemáticamente el proyecto;
- conocemos sus huecos;
- hemos cubierto los huecos críticos;
- las funciones principales tienen tests;
- existe testing end-to-end;
- existe testing de formatos;
- existe testing de regresión;
- existe testing runtime documentado;
- los proyectos antiguos siguen funcionando;
- los errores importantes son comprensibles;
- podemos hacer una crónica completa sin encontrarnos botones falsos o caminos muertos.

============================================================
153. FILOSOFÍA DE TESTING
============================================================

No perseguir un 100% de coverage vacío.

Un test útil demuestra COMPORTAMIENTO.

Prioridad absoluta:

1. Datos no se pierden.
2. References no se rompen.
3. Generated output es válido.
4. Build es fiable.
5. Runtime recibe lo esperado.
6. Proyectos antiguos sobreviven.
7. Una feature rota no pasa desapercibida.

============================================================
154. FILOSOFÍA DE BUGFIX
============================================================

No parchear síntomas cuando exista un problema estructural claro.

Pero tampoco reescribir sistemas enteros innecesariamente.

Fix pequeño cuando basta.

Refactor sólo cuando reduce realmente riesgo.

============================================================
155. NO HACER
============================================================

NO:

- editar geometría;
- construir un mini Blender;
- hacer level creation;
- rehacer renderer;
- crear marketplace;
- añadir cloud;
- añadir multiplayer tooling enorme;
- crear features espectáculo mientras haya sistemas básicos sin tests;
- empezar Fase 7.

============================================================
156. RESULTADO ESPERADO
============================================================

Después de Fase 6 quiero poder considerar Redemption Chronicle Maker una BETA TÉCNICAMENTE SERIA.

No perfecta.

No acabada.

Pero sí:

ESTABLE
TESTEADA
RECUPERABLE
VALIDADA
MANTENIBLE
DEPURABLE

Y, sobre todo:

que podamos seguir desarrollándola sin vivir con miedo a romper cinco fases anteriores.

============================================================
157. REGLA FINAL
============================================================

NO iniciar Fase 7.

Primero convertir todo el código existente en una base fiable.

Buscar activamente fallos.

Romper deliberadamente entradas.

Probar casos límite.

Crear regression tests.

No esconder errores.

No afirmar runtime compatibility sin prueba runtime.

No considerar una feature terminada sólo porque exista código para ella.

Al final de esta fase Redemption Chronicle Maker debe estar preparado para la última gran etapa funcional:

cerrar todos los huecos de autoría necesarios para convertirse realmente en un AURORA TOOLSET VAMPÍRICO.

Pero ESA será la Fase 7.

Fase 6 es la fase donde demostramos que todo lo construido hasta ahora se sostiene.
REDEMPTION CHRONICLE MAKER — FASE 3
EDITOR ESPACIAL 3D MODERNO

La Fase 2 está terminada y funciona.

Ahora comienza la Fase 3.

El objetivo de esta fase NO es crear simplemente un visor de levels.

Debe construirse un EDITOR ESPACIAL MODERNO E INTERACTIVO sobre los levels existentes de Vampire: The Masquerade — Redemption.

La geometría original continúa siendo inmutable en esta fase, pero todo el contenido de nuestra crónica debe poder editarse intuitivamente sobre ella.

La experiencia objetivo debe aproximarse conceptualmente a editores actuales como Unity, Unreal, Godot o Neverwinter Nights Toolset, adaptada a las necesidades concretas de Redemption.

============================================================
PRINCIPIO FUNDAMENTAL
============================================================

El usuario no debe necesitar conocer coordenadas manualmente para trabajar normalmente.

Debe poder:

Abrir level
→ navegar por él
→ seleccionar superficie/punto
→ colocar entidad
→ moverla
→ rotarla
→ seleccionarla
→ editarla
→ entender inmediatamente sus relaciones con el resto de la crónica

Las coordenadas numéricas deben continuar disponibles en Properties para precisión, pero dejar de ser el método principal de colocación.

IMPORTANTE:

NO utilizar ninguna herramienta antigua de autoría de Redemption.

NO Embrace.
NO NOT Editor.
NO herramientas visuales originales.
NO workflows heredados.

La herramienta debe operar directamente sobre nuestros datos, recursos originales y formatos/runtime de Redemption.

============================================================
1. VISUALIZACIÓN REAL DEL LEVEL
============================================================

Investiga los formatos originales necesarios para reconstruir visualmente un level.

El objetivo prioritario es representar:

- geometría;
- materiales;
- texturas;
- orientación;
- escala;
- estructura espacial.

No quiero inicialmente una reconstrucción artística perfecta del renderer original.

Sí quiero que el level sea claramente reconocible y útil para trabajar.

La vista 3D debe servir para crear escenas, no únicamente para demostrar que podemos leer polígonos.

============================================================
2. TEXTURAS
============================================================

Haz un esfuerzo serio por cargar y mostrar las texturas originales.

Investiga:

- referencias de materiales;
- formato de las texturas;
- coordenadas UV;
- rutas de recursos;
- resolución de recursos;
- transparencias cuando sean importantes;
- materiales especiales relevantes.

Cuando una textura no pueda cargarse:

- no bloquear el editor;
- utilizar un material fallback claramente reconocible;
- registrar qué recurso falta.

No conformarse deliberadamente con un mundo gris de polígonos si los datos necesarios para mostrar las texturas están disponibles.

No considerar completa esta parte simplemente porque la geometría pueda renderizarse.

============================================================
3. NAVEGACIÓN MODERNA
============================================================

La navegación 3D debe ser cómoda según estándares actuales.

Como mínimo:

CÁMARA LIBRE

WASD = movimiento
Ratón = mirar
Rueda = variar velocidad o zoom cuando corresponda

Añadir movimiento vertical cuando sea apropiado.

Permitir velocidades razonables para:

- interiores pequeños;
- calles;
- levels grandes.

FOCUS SELECTION

Implementar una acción tipo:

F = enfocar selección

o equivalente.

Selecciono Victoria → la cámara se centra sobre Victoria.

ORBIT

Cuando resulte conveniente, permitir orbitar alrededor de la selección.

PERSPECTIVE

Vista perspectiva normal de editor.

Una vista ortográfica puede añadirse si es sencilla, pero NO tiene prioridad sobre una buena navegación 3D.

GROUND AWARENESS

Evitar que navegar por el mapa sea una lucha constante.

Investiga mecanismos sencillos para:

- mantener altura razonable;
- desplazarse sobre suelo;
- disponer de fly mode cuando sea necesario.

La navegación debe sentirse moderna y predecible.

NO quiero una cámara debug incómoda ni controles heredados de herramientas antiguas.

============================================================
4. SELECCIÓN DIRECTA
============================================================

Debe existir picking con el ratón.

El usuario debe poder hacer click directamente sobre:

- actor;
- prop de nuestra crónica;
- trigger;
- spawn;
- salida;
- waypoint;
- entidad editable.

La selección debe quedar visualmente resaltada.

Puede utilizar:

- outline;
- bounding box;
- highlight;
- gizmo;
- combinación de estos métodos.

No depender exclusivamente del árbol lateral para seleccionar entidades.

============================================================
5. COLOCACIÓN INTUITIVA
============================================================

Debe poder elegirse:

Add Actor

y posteriormente hacer click en una superficie válida del level.

El editor calcula automáticamente:

X
Y
Z

y crea la entidad allí.

Lo mismo debe diseñarse, cuando resulte apropiado, para:

- NPC;
- enemigos;
- objetos;
- spawn points;
- triggers;
- otros elementos espaciales.

Utiliza raycasting/intersección contra la geometría mostrada.

El flujo objetivo debe ser:

Add Actor
→ elegir template
→ click en el suelo
→ aparece
→ girarlo
→ terminado

NO:

buscar coordenadas
→ copiarlas
→ pegarlas
→ corregir altura
→ calcular orientación

============================================================
6. TRANSFORM GIZMOS
============================================================

Implementar gizmos modernos para:

MOVE

Mover la entidad por ejes.

ROTATE

Especialmente importante para la rotación horizontal de actores.

SCALE

Sólo cuando tenga sentido para ese tipo de entidad.

No permitir operaciones sin significado únicamente porque el gizmo pueda hacerlas.

El panel Properties debe actualizar inmediatamente:

X
Y
Z
Orientation

y viceversa.

============================================================
7. SNAP
============================================================

Añadir ayudas razonables:

- snap a superficie;
- snap al suelo;
- rotación incremental opcional;
- grid snap opcional.

No obligar a utilizar snap.

============================================================
8. REPRESENTACIÓN DE ENTIDADES
============================================================

Las entidades de nuestra crónica deben distinguirse claramente.

Si podemos cargar sus modelos originales correctamente:

MOSTRAR LOS MODELOS.

Si todavía no podemos:

utilizar representaciones claras.

Por ejemplo:

Actor        → humanoide / icono
Trigger      → volumen translúcido
Spawn        → marcador
Exit         → puerta / flecha
Waypoint     → punto
Camera       → icono de cámara

El objetivo es que mirando el level pueda comprenderse la construcción de la escena.

============================================================
9. TRIGGERS VISUALES
============================================================

Los triggers NO deben ser meros registros en una lista.

Representarlos espacialmente.

Cuando el motor utilice regiones/volúmenes compatibles, mostrarlos como:

- caja;
- esfera;
- volumen correspondiente.

Debe poder:

- seleccionar;
- mover;
- redimensionar;
- editar propiedades.

cuando nuestro modelo permita dichas operaciones.

============================================================
10. RELACIONES VISUALES
============================================================

Éste es un requisito fundamental.

Al seleccionar una entidad, el editor debe poder indicar qué elementos de la crónica están relacionados con ella.

Ejemplo:

Seleccionamos:

Victoria

y el editor muestra:

USED BY

Spawn event:
    EastLondon.scene_start

Conversations:
    victoria_intro
    victoria_angry

Events:
    victoria_killed

Quest:
    missing_ghoul

Flags:
    victoria_met
    victoria_angry

Y también:

AFFECTS

Conversation victoria_intro
Flag victoria_met
Actor thug_01
Exit WarehouseDoor

No es necesario que todas estas categorías existan desde el primer momento.

Debe construirse a partir de las relaciones realmente soportadas por nuestro modelo.

============================================================
11. RELATIONSHIP LINKS
============================================================

Cuando dos elementos tengan una relación espacial o lógica importante, proporcionar alguna forma clara de visualizarla.

Ejemplo:

Trigger A
   |
   +---- activates ----> Victoria

o:

Trigger A
   +---- spawn --------> Thug01
   +---- spawn --------> Thug02
   +---- set flag -----> ambush_started

No quiero convertir permanentemente la vista 3D en un plato de espaguetis.

Por tanto los links deben poder:

Show Relationships
Hide Relationships

o aparecer únicamente al seleccionar una entidad.

============================================================
12. SELECCIÓN DE TRIGGER
============================================================

Al seleccionar un trigger, quiero poder comprender inmediatamente:

QUÉ LO ACTIVA

Ejemplo:

Player enters

CONDICIONES

warehouse_complete == false

QUÉ HACE

Spawn thug01
Spawn thug02
Close warehouse_exit
Set ambush_started

A QUÉ AFECTA

Los actores o elementos correspondientes deben resaltarse en el viewport cuando resulte posible.

============================================================
13. SELECCIÓN DE ACTOR
============================================================

Al seleccionar un actor:

Mostrar:

SPATIAL

Position
Orientation
Level

IDENTITY

ID
Template
Name

STORY

Conversations
Events
Quest references
Flags

SPAWN

How is this actor created?
When?
Under what condition?

DEPENDENCIES

Who references this actor?

Esta última pregunta es especialmente importante.

============================================================
14. FIND REFERENCES
============================================================

Implementar conceptualmente:

Find References

para cualquier entidad importante.

Ejemplo:

Botón derecho:

Victoria
    Find References

Resultado:

SceneStartEvent
victoria_intro
victoria_killed
QuestMissingGhoul

Doble click → navegar al elemento.

Esto evitará una enorme cantidad de errores cuando las crónicas crezcan.

============================================================
15. WORLD OUTLINER
============================================================

Añadir un árbol de escena moderno.

Ejemplo:

EastLondon

    Actors
        Victoria
        Guard01
        Guard02

    Triggers
        WarehouseEntrance
        AlleyAmbush

    Objects
        Evidence01

    Spawns
        SabbatSpawn

    Exits
        WarehouseExit

Seleccionar en Outliner = seleccionar en viewport.

Seleccionar en viewport = seleccionar en Outliner.

============================================================
16. VISIBILIDAD
============================================================

El Outliner debe permitir ocultar categorías o entidades en el viewport.

Por ejemplo:

[x] Actors
[x] Objects
[ ] Triggers
[ ] Waypoints
[x] Exits

Esto será especialmente útil cuando un level tenga muchas cosas.

============================================================
17. DISTINGUIR ORIGINAL Y NUESTRA CRÓNICA
============================================================

Muy importante.

Debe quedar visualmente claro qué pertenece a:

ORIGINAL LEVEL

y qué pertenece a:

OUR CHRONICLE

Los elementos originales que sean únicamente referencia deberían ser:

- seleccionables cuando resulte útil;
- inspeccionables;
- NO modificables accidentalmente.

Los elementos creados por nosotros sí serán editables.

============================================================
18. INSPECCIÓN DEL LEVEL ORIGINAL
============================================================

Cuando técnicamente resulte posible, extraer y mostrar elementos originales útiles como referencia:

- puertas;
- exits;
- regiones;
- entidades;
- spawn points;
- lights;
- objetos;
- actores;
- cámaras;
- otros elementos contenidos en escena.

No es necesario soportarlos todos inmediatamente.

Pero diseñar la arquitectura para distinguir:

READ ONLY ORIGINAL ENTITY

de:

EDITABLE CHRONICLE ENTITY

============================================================
19. RECURSOS ORIGINALES EN EL VIEWPORT
============================================================

Cuando sea viable, intentar utilizar:

- modelos originales;
- materiales originales;
- texturas originales;
- props originales.

No duplicar recursos innecesariamente.

Crear sistemas de cache donde tenga sentido.

El usuario debe poder seleccionar un recurso desde Resource Browser y colocarlo visualmente.

============================================================
20. RENDIMIENTO
============================================================

Los levels son antiguos y deberían ser manejables en hardware moderno.

Aun así:

- no reconstruir constantemente toda la escena;
- cachear geometría;
- cachear texturas;
- utilizar GPU;
- no ejecutar parsers pesados cada frame;
- separar carga de datos y render.

La navegación debe mantenerse fluida.

Objetivo razonable:

60 FPS en levels normales en hardware moderno cuando la arquitectura utilizada lo permita.

No sacrificar corrección del parser sólo para perseguir esa cifra.

============================================================
21. TECNOLOGÍA DEL VIEWPORT
============================================================

Investiga qué solución encaja mejor con nuestra aplicación PySide6 existente.

Opciones razonables incluyen:

- OpenGL moderno;
- moderngl;
- Qt OpenGL;
- otra biblioteca Python madura y mantenible.

Elige según:

- integración con PySide6;
- picking;
- texturas;
- geometría;
- gizmos;
- rendimiento;
- mantenimiento futuro.

NO introducir un motor de videojuegos gigantesco únicamente para mostrar el viewport salvo que exista una justificación realmente fuerte.

Documenta la decisión técnica.

============================================================
22. NO HACER UN RENDERER PERFECTO
============================================================

No perder tiempo intentando reproducir exactamente:

- iluminación de Redemption;
- shaders;
- niebla original;
- efectos gráficos;
- partículas;
- postprocesado.

El objetivo es:

AUTHORING VIEWPORT.

Debe ser:

- claro;
- reconocible;
- texturizado;
- navegable;
- preciso espacialmente.

No tiene que confundirse con el juego ejecutándose.

============================================================
23. USABILIDAD COMO CRITERIO PRINCIPAL
============================================================

La usabilidad es tan importante como la compatibilidad técnica.

No considerar terminada la Fase 3 si únicamente existe:

- wireframe;
- mundo gris cuando las texturas están disponibles;
- cámara incómoda;
- picking deficiente;
- colocación mediante coordenadas manuales;
- viewport que sólo sirve de demostración.

La pregunta de aceptación es:

¿APETECE CONSTRUIR UNA ESCENA AQUÍ?

Si la respuesta es no, esta fase todavía no está terminada.

============================================================
24. PROPERTIES PANEL
============================================================

La selección en viewport debe sincronizarse con el panel de Properties existente.

Actor seleccionado:

ID
Template
Name
Level
X
Y
Z
Orientation
Spawn
Conversation
Flags
References

Trigger seleccionado:

ID
Shape
Position
Size
Activation
Conditions
Actions
Affected entities
References

Los cambios visuales y numéricos deben sincronizarse inmediatamente.

============================================================
25. DEPENDENCY / RELATIONSHIP INSPECTOR
============================================================

Crear una forma clara de consultar las dependencias narrativas y lógicas.

Ejemplo:

Victoria

REFERENCED BY:
- SpawnVictoriaEvent
- victoria_intro
- victoria_killed
- missing_ghoul

REFERENCES:
- victoria_met
- warehouse_guard
- warehouse_exit

Debe ser posible navegar mediante doble click o acción equivalente.

============================================================
26. HIGHLIGHT DE ELEMENTOS AFECTADOS
============================================================

Cuando seleccionemos un evento, trigger o actor con relaciones:

permitir destacar en el viewport los elementos relacionados.

Ejemplo:

Seleccionamos AlleyAmbush Trigger.

El viewport resalta:

- thug01 spawn;
- thug02 spawn;
- warehouse_exit.

Debe ser fácil desactivar el resaltado.

============================================================
27. EVENTOS ESPACIALES
============================================================

Conectar el Event Editor de Fase 2 con el viewport.

Por ejemplo:

Selecciono un trigger en 3D.

Properties:

WHEN:
Player enters

IF:
warehouse_complete == false

DO:
Spawn thug01
Spawn thug02
Set ambush_started

No crear sistemas duplicados.

Debe seguir existiendo un único modelo interno compartido por:

- GUI;
- viewport;
- CLI;
- build.

============================================================
28. CREACIÓN DE TRIGGERS
============================================================

Permitir crear triggers desde el viewport.

Flujo conceptual:

Add Trigger
→ click en posición
→ aparece volumen
→ ajustar tamaño con gizmo
→ configurar condición
→ configurar acciones

Los datos resultantes deben usar el mismo modelo de eventos existente.

============================================================
29. CREACIÓN DE ACTORES
============================================================

Flujo conceptual:

Resource Browser
→ Actors
→ buscar template
→ seleccionar
→ click en level
→ actor creado
→ ajustar orientación
→ configurar propiedades

No pedir coordenadas manuales salvo que el usuario quiera precisión.

============================================================
30. CREACIÓN DE OBJETOS
============================================================

Cuando el backend y catálogo existente lo permitan:

Resource Browser
→ Objects
→ seleccionar recurso
→ click en level
→ colocar
→ mover
→ rotar

No añadir objetos cuyo formato o spawn todavía no esté bien confirmado.

============================================================
31. EDICIÓN NO DESTRUCTIVA
============================================================

La geometría original continúa siendo de sólo lectura.

No permitir:

- mover paredes;
- borrar geometría;
- editar brushes;
- cambiar topology;
- modificar level original.

Nuestra herramienta crea una capa lógica/narrativa sobre el level.

============================================================
32. CAPAS DEL VIEWPORT
============================================================

Diseñar conceptualmente capas como:

Original Geometry
Original Entities
Chronicle Actors
Chronicle Objects
Triggers
Spawns
Exits
Cameras
Helpers

Permitir mostrar/ocultar capas cuando sea útil.

============================================================
33. CARGA DEL LEVEL
============================================================

La carga debe mostrar progreso razonable cuando sea necesario.

Ejemplo:

Reading level...
Parsing geometry...
Loading materials...
Loading textures...
Building scene...
Ready.

No congelar aparentemente la aplicación durante largos periodos sin feedback si puede evitarse.

============================================================
34. CACHE
============================================================

Crear cache regenerable para datos costosos.

Por ejemplo:

cache/levels/
cache/textures/
cache/geometry/

No alterar recursos originales.

El cache debe poder borrarse y regenerarse.

============================================================
35. ERRORES DE RECURSOS
============================================================

Si un level tiene:

- textura no encontrada;
- material desconocido;
- referencia rota;
- formato no soportado;

el editor debe:

- continuar cargando cuando sea posible;
- mostrar fallback;
- registrar warning;
- indicar claramente el recurso problemático.

NO cerrar la aplicación porque falte una textura.

============================================================
36. TESTS
============================================================

Preservar todos los tests anteriores.

Añadir tests, cuando sea razonable, para:

- parsing de geometría;
- resolución de recursos;
- materiales;
- coordenadas;
- transformaciones;
- serialización de posiciones;
- relaciones entre entidades;
- Find References;
- cache;
- raycast/picking en componentes que puedan probarse sin GUI real.

Priorizar tests de parser/modelo sobre tests frágiles de interacción gráfica.

============================================================
37. DOCUMENTACIÓN
============================================================

Actualizar:

README.md
docs/ARCHITECTURE.md
docs/ENGINE_NOTES.md
docs/FORMAT_NOTES.md
docs/ROADMAP.md
docs/EDITOR_GUIDE.md

Crear además:

docs/VIEWPORT.md

que documente:

- cómo se carga un level;
- formatos utilizados;
- renderer;
- materiales;
- texturas;
- navegación;
- picking;
- gizmos;
- raycasting;
- cache;
- limitaciones actuales.

============================================================
38. COMPATIBILIDAD CON FASE 2
============================================================

MUY IMPORTANTE:

No romper:

- proyectos existentes;
- YAML existente;
- CLI;
- build;
- conversaciones;
- eventos;
- actores;
- flags;
- Resource Browser.

La Fase 3 debe ampliar el editor, no sustituir la base funcional.

============================================================
39. PRUEBA DE REGRESIÓN
============================================================

Antes de considerar terminada la fase:

- ejecutar tests;
- cargar proyecto de Fase 2;
- abrirlo en editor;
- hacer Build;
- comprobar que genera correctamente;
- comprobar que el nuevo viewport no altera datos sin que el usuario lo solicite.

============================================================
40. PRUEBA DE ACEPTACIÓN COMPLETA
============================================================

Fase 3 será considerada satisfactoria si podemos:

1. Abrir Redemption Chronicle Maker.
2. Abrir una crónica existente.
3. Seleccionar East London u otro level.
4. Ver su geometría.
5. Ver una proporción útil de sus texturas.
6. Navegar cómodamente por él.
7. Usar WASD/ratón de manera natural.
8. Enfocar una selección.
9. Seleccionar entidades haciendo click.
10. Crear un actor desde Resource Browser.
11. Colocarlo haciendo click sobre el suelo.
12. Moverlo.
13. Girarlo.
14. Guardarlo.
15. Volver a abrir el proyecto y encontrarlo correctamente.
16. Seleccionarlo y ver sus Properties.
17. Ver qué eventos lo crean o utilizan.
18. Ver qué conversaciones lo referencian.
19. Utilizar Find References.
20. Crear un trigger espacial.
21. Ver claramente su volumen.
22. Moverlo.
23. Redimensionarlo.
24. Asociarle condiciones.
25. Asociarle acciones.
26. Seleccionarlo.
27. Ver qué elementos afecta.
28. Resaltar dichos elementos en viewport.
29. Ocultar/mostrar categorías desde Outliner.
30. Distinguir visualmente elementos originales de elementos de crónica.
31. Validar proyecto.
32. Hacer Build.
33. Mantener funcionando la crónica generada por Fase 2.

============================================================
41. NO HACER TODAVÍA
============================================================

NO implementar todavía:

- edición de geometría;
- clon de Embrace;
- modelado 3D;
- modificación de meshes;
- creación de levels desde cero;
- editor completo de materiales;
- sistema completo de iluminación;
- sistema completo de partículas;
- editor completo de animaciones;
- editor completo de AI;
- NOT Editor completo salvo que aparezca una necesidad estricta y pequeña;
- marketplace;
- plugins;
- launcher complejo;
- distribución pública final.

============================================================
42. NO DESVIARSE
============================================================

No intentes impresionar añadiendo funciones laterales que no sean esenciales.

Prioridades:

1. Level visible.
2. Texturas.
3. Navegación cómoda.
4. Picking.
5. Colocación intuitiva.
6. Gizmos.
7. Triggers visuales.
8. Relaciones y referencias.
9. Estabilidad.
10. Build intacto.

============================================================
43. CRITERIO DE ÉXITO REAL
============================================================

Fase 3 NO está terminada porque podamos renderizar triángulos.

Está terminada cuando el viewport se convierte en la forma natural de construir una escena.

El objetivo final de uso debe sentirse así:

OPEN LEVEL
↓
NAVIGATE
↓
ADD ACTOR
↓
CLICK TO PLACE
↓
ROTATE
↓
ADD TRIGGER
↓
CONFIGURE ACTIONS
↓
SELECT ACTOR
↓
SEE REFERENCES
↓
VALIDATE
↓
BUILD

Y NO así:

OPEN LEVEL
↓
LOOK AT WIREFRAME
↓
WRITE COORDINATES MANUALLY
↓
RETURN TO OLD WORKFLOW

============================================================
44. REPORTE FINAL
============================================================

Al terminar crear:

docs/PHASE3_REPORT.md

con secciones:

IMPLEMENTADO

PARSING DE LEVELS

GEOMETRÍA

TEXTURAS

NAVEGACIÓN

PICKING

GIZMOS

COLOCACIÓN

TRIGGERS

RELACIONES

FIND REFERENCES

PROBADO

PROBADO DENTRO DE REDEMPTION

NO PROBADO

LIMITACIONES

FORMATOS TODAVÍA NO COMPRENDIDOS

PROBLEMAS DE RENDIMIENTO

DEUDA TÉCNICA

PROPUESTA PARA FASE 4

============================================================
45. REGLA FINAL
============================================================

No empezar Fase 4.

No considerar terminada Fase 3 únicamente porque exista un viewport técnico.

Debe ser un editor espacial moderno, cómodo y realmente utilizable.

La geometría original es la base.

Nuestra crónica se construye visualmente encima.

El objetivo es acercarnos progresivamente a un editor del nivel de comodidad que un usuario esperaría de una herramienta moderna de creación de campañas, pero utilizando directamente el runtime y recursos de Vampire: The Masquerade — Redemption.
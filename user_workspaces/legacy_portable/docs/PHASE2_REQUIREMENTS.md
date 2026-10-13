# REDEMPTION CHRONICLE MAKER — FASE 2

La Fase 1 está terminada y **funciona**.

El pipeline construido en la Fase 1 es capaz de generar una crónica válida de **Vampire: The Masquerade — Redemption** y ha sido probado satisfactoriamente.

Ahora comienza la **Fase 2**.

El objetivo de esta fase NO es rehacer la arquitectura ni ampliar indiscriminadamente el soporte del motor.

El objetivo es convertir el núcleo funcional de Fase 1 en el **primer editor moderno realmente utilizable para crear una crónica**.

---

# REGLA Nº 1: NO ROMPER LO QUE FUNCIONA

Antes de modificar nada:

1. Inspecciona todo el proyecto existente en la carpeta de trabajo.
2. Lee:
   - README.md
   - docs/ENGINE_NOTES.md
   - docs/FORMAT_NOTES.md
   - docs/ARCHITECTURE.md
   - docs/ROADMAP.md
   - tests existentes
   - código de Fase 1
   - ejemplo funcional generado
3. Ejecuta los tests actuales.
4. Comprueba que el build funcional de Fase 1 sigue generándose correctamente.
5. Comprende la arquitectura existente antes de cambiarla.

La Fase 1 es ahora la **base estable del proyecto**.

NO la sustituyas por una arquitectura nueva porque consideres otra más elegante.

Refactoriza únicamente cuando exista una razón concreta y los tests garanticen que no rompemos compatibilidad.

Si Git está disponible y el proyecto ya lo utiliza, crea un checkpoint/commit antes de realizar cambios importantes.

---

# PRINCIPIO FUNDAMENTAL DEL PROYECTO

Redemption Chronicle Maker debe permitir crear crónicas para Vampire: Redemption:

**SIN utilizar ninguna herramienta de autoría original.**

NO:

- Embrace;
- NOT Editor;
- Conversation Editor antiguo;
- Quest Editor antiguo;
- herramientas visuales del SDK;
- workflows manuales antiguos.

El juego original es:

1. runtime;
2. biblioteca de recursos;
3. fuente técnica para estudiar formatos.

Nuestra herramienta debe hablar directamente con los formatos y API que consume Redemption.

---

# INSTALACIÓN ORIGINAL

La instalación de referencia continúa situada en:

```text
H:\GOG\Vampire The Masquerade - Redemption
```

Es SOLO LECTURA.

Puedes inspeccionar libremente cualquier recurso que necesites.

NO modificarla.

NO escribir dentro de ella.

NO utilizar sus herramientas de autoría.

Si necesitas manipular algo, cópialo al workspace.

---

# OBJETIVO DE FASE 2

Construir el primer **Redemption Chronicle Maker Desktop Editor**.

Debe ser una aplicación de escritorio moderna que permita realizar visualmente una crónica pequeña utilizando el backend ya funcional.

Al terminar esta fase debe ser posible hacer, sin editar YAML manualmente:

```text
Crear proyecto
      ↓
Elegir un level existente
      ↓
Añadir un NPC
      ↓
Configurar sus propiedades
      ↓
Crear una conversación ramificada
      ↓
Crear uno o varios eventos sencillos
      ↓
Validar
      ↓
Build
      ↓
Obtener una crónica válida
```

Éste es el criterio principal de éxito.

---

# TECNOLOGÍA DE GUI

Utiliza:

```text
Python + PySide6
```

salvo que exista una razón técnica muy seria derivada de la arquitectura actual para no hacerlo.

NO usar:

- Electron;
- navegador embebido como arquitectura principal;
- servidor web local como interfaz;
- tecnologías innecesariamente pesadas.

Queremos una aplicación Windows convencional.

---

# FILOSOFÍA DE INTERFAZ

La interfaz NO debe exponer al usuario detalles arcanos del motor salvo cuando sea realmente necesario.

El creador NO debería necesitar conocer:

```text
.nsc
.nmf
.nco
.nvo
.nls
.class
.nob
CodexActor
CaptureThing
ANSWERRETURN
```

Esos son detalles del backend.

La experiencia debe parecerse más a un pequeño editor moderno de campañas.

---

# ESTRUCTURA CONCEPTUAL DE LA APLICACIÓN

La ventana principal debería aproximarse a:

```text
┌───────────────────────────────────────────────────────────────┐
│ Redemption Chronicle Maker                                  │
├────────────────┬──────────────────────────────┬───────────────┤
│ PROJECT        │                              │ PROPERTIES    │
│                │                              │               │
│ Chronicle      │       EDITOR CENTRAL         │ objeto        │
│ Levels         │                              │ seleccionado  │
│ Actors         │                              │               │
│ Conversations  │                              │               │
│ Events         │                              │               │
│ Quests*        │                              │               │
├────────────────┴──────────────────────────────┴───────────────┤
│ Problems / Build / Log                                       │
└───────────────────────────────────────────────────────────────┘
```

No hace falta copiar literalmente este layout.

Diseña una UI limpia y funcional.

---

# IMPORTANTE: NO VISOR 3D TODAVÍA

En Fase 2:

**NO desarrollar todavía un renderer 3D del level.**

Eso será una fase posterior.

Las posiciones podrán editarse inicialmente mediante:

```text
X
Y
Z
rotación/orientación
```

La arquitectura debe permitir añadir posteriormente un visor 3D sin tener que rehacer el modelo de datos.

---

# 1. GESTOR DE PROYECTOS

La aplicación debe permitir:

### Crear nueva crónica

Campos iniciales:

- ID interno;
- nombre;
- descripción opcional;
- directorio de proyecto.

### Abrir crónica

Abrir proyectos creados anteriormente.

### Guardar

Guardar modificaciones en nuestro formato fuente.

### Guardar como

Cuando resulte razonable.

### Estado modificado

Mostrar claramente cuando hay cambios sin guardar.

---

# 2. FORMATO FUENTE

Mantén el formato fuente moderno creado en Fase 1.

Si actualmente se utiliza YAML:

**seguir utilizando YAML.**

La GUI debe editar ese modelo.

NO crear un segundo formato exclusivo de la interfaz.

Debe existir una única fuente de verdad:

```text
project.yaml
+
archivos auxiliares del proyecto
```

La aplicación visual simplemente modifica esos datos.

Debe seguir siendo posible utilizar el build desde línea de comandos.

La GUI NO debe convertirse en requisito para compilar.

---

# 3. CATÁLOGO DE LEVELS

Utiliza el catálogo generado a partir del juego original en Fase 1 o amplíalo si resulta necesario.

El usuario debe poder abrir:

```text
Level
    Choose Base Level...
```

y obtener una lista de levels/localizaciones reales disponibles.

Mostrar como mínimo:

- nombre;
- identificador;
- archivo `.nil`;
- escenas asociadas conocidas;
- crónica original de procedencia cuando pueda determinarse.

Añade buscador/filtro.

El catálogo debe provenir de la instalación real.

NO mantener una lista inventada manualmente.

---

# 4. ACTOR / NPC EDITOR

Éste es uno de los objetivos principales de Fase 2.

Debe existir:

```text
Actors
   + Add Actor
```

Al crear un actor:

### Identidad

- ID interno;
- nombre visible cuando el motor permita establecerlo;
- comentario/descripción interna para el diseñador.

### Template

Selector de plantillas reales conocidas.

Ejemplo conceptual:

```text
businessWoman
gothGirl1
Mugger
...
```

El selector debe alimentarse del catálogo real extraído del juego.

Debe existir búsqueda.

### Level

Seleccionar dónde aparece.

### Transform

```text
X
Y
Z
Orientation
```

Utiliza exactamente el sistema de coordenadas/orientación que haya quedado confirmado en Fase 1.

### Spawn

Configurar al menos:

```text
Spawn on scene start
```

y las condiciones básicas que ya soporte nuestro backend.

### Estado

Cuando el backend de Fase 1 ya lo permita, exponer propiedades confirmadas como:

- clan;
- team;
- health;
- flags;
- talkable;
- etc.

NO añadas propiedades simplemente porque CodexActor tenga un método.

Sólo introduce en GUI aquellas que podamos generar de manera fiable.

---

# 5. RESOURCE BROWSER

Crear un navegador sencillo de recursos reutilizables.

Inicialmente centrado en:

- actor templates;
- levels;
- escenas;
- modelos si ya están catalogados;
- AI disponibles si existe información fiable;
- items si ya pueden identificarse.

Debe permitir:

```text
buscar
filtrar
seleccionar
```

No necesitamos todavía previsualización 3D.

Cuando un recurso proceda del juego original, mostrar su identificador exacto.

---

# 6. CONVERSATION EDITOR

Ésta es otra pieza central.

Quiero poder crear conversaciones SIN editar `.nco`.

Debe existir:

```text
Conversations
   + New Conversation
```

La primera versión NO necesita un enorme graph editor estilo Unreal.

Prefiero una interfaz sólida y sencilla.

Puede utilizar:

```text
árbol jerárquico
+
panel de propiedades
```

si eso reduce complejidad y errores.

---

# MODELO DE CONVERSACIÓN

Debe permitir representar al menos:

```text
Conversation
    Event / Node
        Line
        Line
        Answer
            → otro Node
        Answer
            → Return Value
```

Elementos necesarios:

### Speaker

Elegir actor/personaje.

### Text

Texto de la línea.

### Answers

Añadir múltiples respuestas.

Cada respuesta puede:

```text
GOTO otro nodo
```

o:

```text
RETURN valor
```

exactamente de acuerdo con el funcionamiento real de `.nco`.

---

# INTERFAZ DE CONVERSACIÓN

Ejemplo conceptual:

```text
Victoria Intro
│
├── Opening
│    Victoria:
│    "No deberías estar aquí."
│
│    Player answers:
│
│    ├── "¿Quién eres?"
│    │       → WhoAreYou
│    │
│    ├── "Apártate."
│    │       → Threat
│    │
│    └── "Me voy."
│            → RETURN 3
│
├── WhoAreYou
│    ...
│
└── Threat
     ...
```

Debe ser posible:

- crear nodo;
- borrar nodo;
- renombrar nodo;
- añadir línea;
- borrar línea;
- añadir respuesta;
- elegir destino;
- elegir RETURN;
- reordenar líneas cuando sea razonable.

---

# VALIDACIÓN DE CONVERSACIONES

Detectar automáticamente:

- IDs duplicados;
- destinos inexistentes;
- nodos huérfanos cuando sea relevante;
- actores inexistentes;
- conversaciones sin entrada;
- RETURN inválidos;
- referencias rotas.

Mostrar errores en Problems.

---

# 7. EVENT EDITOR

No quiero todavía un sistema de scripting visual gigantesco.

Quiero un **primer Event Editor sencillo**.

Conceptualmente:

```text
WHEN
    Scene Starts

IF
    Chronicle Flag X == false

DO
    Spawn Actor Victoria
```

Debe reutilizar exclusivamente acciones que nuestro backend ya pueda generar.

---

# EVENTOS INICIALES

Implementar sólo aquellos necesarios y bien confirmados.

Prioridad:

```text
Scene Start
Actor Clicked
Conversation Ended
Actor Killed
Timer
```

No hace falta implementar todos si algunos requieren cambios excesivos.

---

# CONDITIONS

Inicialmente basta con:

```text
Chronicle Flag is set
Chronicle Flag is not set
```

y otras condiciones que el backend ya tenga sólidamente implementadas.

---

# ACTIONS

Como mínimo intenta soportar las que necesitamos para reproducir la crónica de Fase 1:

```text
Spawn Actor
Start Conversation
Set Chronicle Flag
Clear Chronicle Flag
```

Añade otras únicamente si están bien confirmadas y son sencillas:

```text
Remove Actor
Open Exit
Close Exit
Change Scene
```

pero NO conviertas Fase 2 en un intento de implementar toda la API Codex.

---

# 8. CHRONICLE FLAGS

Crear un pequeño editor de flags.

Ejemplo:

```text
1000  victoria_met
1001  victoria_angry
1002  warehouse_complete
```

La GUI debe permitir:

- añadir;
- borrar;
- renombrar alias;
- asignar ID;
- detectar IDs duplicados.

Internamente deben generar exactamente los valores que espera el backend.

---

# 9. PROPERTIES PANEL

La selección de cualquier elemento debe mostrar sus propiedades editables.

Por ejemplo:

### Actor seleccionado

```text
ID
Template
Level
X
Y
Z
Orientation
Conversation
Spawn condition
```

### Conversation seleccionada

```text
ID
Entry node
Actor
```

### Event seleccionado

```text
Trigger
Conditions
Actions
```

Evitar ventanas modales innecesarias.

---

# 10. PROBLEMS PANEL

Necesito una zona similar a la de un IDE:

```text
Problems
```

que muestre:

```text
ERROR
WARNING
INFO
```

Ejemplos:

```text
ERROR Actor "victoria" references unknown template "foo".

ERROR Conversation "victoria_intro" points to missing node "Threat2".

WARNING Actor "victoria" has position 0,0,0.

ERROR Chronicle flag 1001 is duplicated.
```

Doble click debería llevar al elemento correspondiente cuando sea razonablemente fácil.

---

# 11. BUILD DESDE LA GUI

Debe existir un botón evidente:

```text
BUILD CHRONICLE
```

La GUI debe llamar al MISMO backend de build que utiliza CLI.

NO mantener dos implementaciones.

El resultado debe aparecer en:

```text
build/
```

como hasta ahora.

Mostrar:

```text
Build successful
```

o errores detallados.

---

# 12. VALIDATE

Añadir:

```text
Validate Project
```

sin necesidad de generar build.

Debe ejecutar exactamente los validadores del backend.

---

# 13. BUILD LOG

Mostrar de forma legible:

```text
Parsing project...
Validating...
Generating chronicle...
Generating conversation...
Generating Java...
Compiling Java...
Packaging...
Build succeeded.
```

No inundar al usuario con trazas internas salvo que active una vista detallada.

---

# 14. PRESERVAR CLI

MUY IMPORTANTE:

Todo lo que hagamos desde GUI debe continuar pudiendo hacerse mediante:

```text
python build.py ...
```

La arquitectura deseada es:

```text
                 ┌──── CLI
PROJECT MODEL ───┤
                 └──── GUI

                       ↓

                    BACKEND

                       ↓

                     BUILD
```

NO:

```text
CLI backend
+
GUI backend diferente
```

---

# 15. AUTOSAVE / RECOVERY

Implementar de forma prudente un sistema básico de protección contra pérdida de trabajo.

Como mínimo:

- detectar proyecto modificado;
- preguntar antes de cerrar con cambios;
- guardar de forma atómica cuando sea posible.

Si resulta sencillo:

```text
.project.autosave
```

o mecanismo equivalente.

No sobrecomplicar.

---

# 16. COPIAS Y DATOS ORIGINALES

Nunca escribir automáticamente dentro de:

```text
H:\GOG\Vampire The Masquerade - Redemption
```

durante esta fase.

Todos los builds siguen yendo a nuestro `build/`.

La instalación permanece como fuente read-only.

---

# 17. DOCUMENTACIÓN

Actualizar:

```text
README.md
docs/ARCHITECTURE.md
docs/ENGINE_NOTES.md
docs/FORMAT_NOTES.md
docs/ROADMAP.md
```

Crear además:

```text
docs/EDITOR_GUIDE.md
```

explicando cómo:

```text
crear proyecto
elegir level
añadir NPC
crear conversación
crear evento
validar
hacer build
```

---

# 18. TESTS

NO reducir cobertura existente.

Añadir tests para:

- round-trip modelo ↔ YAML cuando corresponda;
- creación de proyectos;
- edición de actores;
- conversaciones ramificadas;
- referencias rotas;
- flags duplicados;
- serialización;
- build lanzado desde API;
- mismo resultado desde CLI y backend llamado por GUI cuando pueda verificarse.

No hace falta automatizar cada widget individual.

Priorizar backend/modelo.

---

# 19. ERRORES

La GUI jamás debe morir porque haya un proyecto inválido.

Capturar errores y mostrarlos amigablemente.

Por ejemplo:

NO:

```text
Traceback...
KeyError...
```

como experiencia normal.

SÍ:

```text
Conversation "victoria_intro" references actor "victora",
but that actor does not exist.
```

Los tracebacks pueden registrarse en modo diagnóstico.

---

# 20. NO HACER EN FASE 2

NO desarrollar todavía:

- visor 3D;
- renderer de `.nil`;
- edición de geometría;
- clon de Embrace;
- `.NOT` Editor completo;
- editor de modelos;
- texturas;
- animaciones;
- nuevas disciplinas;
- editor completo de AI;
- quest editor complejo;
- herramienta de sonido;
- instalador final;
- updater;
- marketplace;
- Steam/GOG integration;
- sistema de plugins;
- scripting visual completo;
- árbol gigantesco con toda la API Codex.

No desviarse.

---

# IMPORTANTE SOBRE `.NOT`

El objetivo a largo plazo continúa siendo NO depender de NOT Editor.

Pero si la Fase 1 ya puede reutilizar plantillas existentes para generar actores, utiliza ese mecanismo.

NO intentes resolver completamente `.NOT` durante Fase 2.

Documenta cualquier descubrimiento relevante y déjalo para una fase posterior.

---

# IMPORTANTE SOBRE COORDENADAS

En Fase 2 aceptamos temporalmente introducir:

```text
X
Y
Z
Orientation
```

manualmente.

Pero prepara el modelo de datos pensando en que una fase posterior tendrá:

**visor 3D del level + colocación mediante ratón.**

No codifiques la posición de forma que después resulte difícil conectarla a dicho visor.

---

# PRUEBA DE ACEPTACIÓN DE FASE 2

Al terminar, crea mediante LA PROPIA GUI una crónica nueva de prueba.

No editar manualmente el YAML salvo para depuración.

La prueba debe:

1. Crear un proyecto.
2. Seleccionar un level original.
3. Crear un actor.
4. Elegir una template original mediante Resource Browser.
5. Establecer posición y orientación.
6. Crear una conversación.
7. Crear al menos una bifurcación.
8. Tener al menos dos respuestas del jugador.
9. Una respuesta debe cambiar un Chronicle Flag.
10. Ese flag debe producir posteriormente una diferencia de comportamiento.
11. Validar desde GUI.
12. Hacer Build desde GUI.
13. Obtener el mismo pipeline funcional de Fase 1.

Si puede probarse dentro de Vampire: Redemption desde el entorno disponible, hazlo.

Si no puede ejecutarse el juego automáticamente, indícalo claramente y deja el build preparado para prueba manual.

---

# CALIDAD DE UI

No quiero una interfaz de demo deliberadamente fea simplemente porque sea una Fase 2.

Tampoco quiero perder tiempo haciendo diseño artístico.

Debe ser:

- limpia;
- consistente;
- legible;
- usable;
- Windows-friendly;
- con tamaños de controles razonables;
- sin texto diminuto;
- sin paneles absurdamente comprimidos.

Utiliza widgets estándar de Qt.

No inventes un sistema visual extravagante.

---

# ATAJOS ÚTILES

Cuando sean fáciles de implementar:

```text
Ctrl+N  New
Ctrl+O  Open
Ctrl+S  Save
Ctrl+Shift+S Save As
F5      Build
```

No son obligatorios si interfieren con trabajo más importante.

---

# PRIMER LANZAMIENTO

Quiero poder ejecutar algo sencillo parecido a:

```text
python editor.py
```

o:

```text
python -m redemption_editor
```

Documenta el comando exacto.

Más adelante construiremos un `.exe`.

NO necesitamos empaquetar ejecutable todavía.

---

# ARQUITECTURA FUTURA

Aunque NO debes implementarlo ahora, evita decisiones que bloqueen posteriormente:

### Fase futura

```text
3D Level Viewer
```

que permita:

- cargar geometría existente;
- navegar por ella;
- seleccionar punto;
- colocar actor;
- mover actor;
- orientar actor;
- visualizar triggers;
- visualizar props.

El editor actual debe poder recibir dichas posiciones sin cambios radicales en el modelo.

---

# CRITERIO DE ÉXITO REAL

Fase 2 NO está terminada porque aparezca una ventana.

Está terminada cuando podemos utilizar nuestra propia aplicación para crear una crónica pequeña **sin editar formatos internos de Redemption y sin utilizar herramientas antiguas**.

El flujo debe ser:

```text
NEW PROJECT
       ↓
CHOOSE LEVEL
       ↓
ADD ACTOR
       ↓
CREATE CONVERSATION
       ↓
CREATE EVENT
       ↓
VALIDATE
       ↓
BUILD
       ↓
REDEMPTION CHRONICLE
```

---

# REVISIÓN FINAL OBLIGATORIA

Antes de considerar terminada la Fase 2:

1. Ejecuta todos los tests.
2. Ejecuta nuevamente el build de la crónica de Fase 1.
3. Confirma que sigue funcionando.
4. Crea la nueva crónica de aceptación mediante GUI.
5. Valídala.
6. Haz Build.
7. Revisa errores y warnings.
8. Revisa documentación.
9. Elimina código muerto evidente.
10. No dejes archivos temporales absurdos en la raíz.

Después escribe un resumen en:

```text
docs/PHASE2_REPORT.md
```

con:

### IMPLEMENTADO

### PROBADO

### PROBADO DENTRO DE REDEMPTION

### NO PROBADO DENTRO DEL JUEGO

### LIMITACIONES ACTUALES

### DEUDA TÉCNICA

### PROPUESTA PARA FASE 3

---

# MUY IMPORTANTE

No empieces Fase 3.

No intentes sorprender al usuario añadiendo veinte subsistemas que no ha pedido.

Quiero **una Fase 2 pequeña en superficie pero completa verticalmente**.

Prefiero:

```text
1 NPC
+
1 conversación buena
+
1 sistema de eventos bueno
+
1 Build fiable
```

a:

```text
40 paneles a medio implementar.
```

La prioridad absoluta es convertir el pipeline probado de Fase 1 en **el primer editor de crónicas realmente usable**.

Todo el trabajo debe quedar persistido en la carpeta seleccionada.
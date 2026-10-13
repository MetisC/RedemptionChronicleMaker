PROYECTO:
REDEMPTION CHRONICLE MAKER

VERSIÓN OBJETIVO:
1.0.0-rc4

NOMBRE DE ESTA PASADA:

DYNAMIC ENCOUNTERS
ENEMY DIRECTOR
GENERADORES / OLEADAS / REFUERZOS / JEFES POR FASES

======================================================================
0. MISIÓN
======================================================================

QUIERO AÑADIR A REDEMPTION CHRONICLE MAKER UN SISTEMA DE AUTORÍA
EXTREMADAMENTE POTENTE PERO EXTREMADAMENTE FÁCIL PARA CREAR COMBATES
DINÁMICOS.

EJEMPLOS DE LO QUE QUIERO PODER CREAR SIN ESCRIBIR JAVA:

- entro en una zona y aparecen 4 enemigos;
- al morir aparecen otros 6;
- tres oleadas sucesivas;
- enemigos que continúan apareciendo cada 10 segundos;
- mantener siempre entre 3 y 6 enemigos vivos;
- un generador infinito hasta destruir/cerrar algo;
- una emboscada;
- refuerzos que llegan después de 30 segundos;
- refuerzos cuando sólo queda un enemigo vivo;
- una sala que se llena progresivamente;
- un jefe que al 50% de vida invoca enemigos;
- al 25% de vida cambia de fase;
- antes de morir dispara una cinemática o conversación;
- al morir el jefe se detienen todos los generadores;
- al terminar una oleada se abre una puerta;
- al completar todas se avanza una quest;
- enemigos aleatorios elegidos de un pool;
- distintos puntos de aparición;
- spawns alternos;
- spawn cerca del jugador;
- un prop/portal que visualmente representa el generador;
- activar/desactivar/pausar/reanudar un generador mediante eventos;
- generadores reutilizables;
- generadores de una sola ejecución;
- encounters que reinician al volver;
- encounters cuyo estado queda completado para siempre;
- save/load a mitad de combate sin duplicar enemigos ni recompensas.

PERO LA UX NO PUEDE PARECER UN EDITOR DE PROGRAMACIÓN.

EL USUARIO NORMAL DEBE PODER HACER ALGO COMO:

    + Encuentro dinámico…

    Tipo:
        Emboscada
        Oleadas
        Generador continuo
        Refuerzos
        Jefe por fases

    Enemigos:
        [Rata] x 4
        [Ghoul] x 2

    Aparecen en:
        Punto A
        Punto B
        Punto C

    Empieza cuando:
        El jugador entra en Zona 1

    Termina cuando:
        No queda ningún enemigo

    Al terminar:
        Completar misión

    [CREAR]

Y ESO DEBE FUNCIONAR.

Toda la potencia adicional vive en:

    Opciones avanzadas

NO delante del usuario.

======================================================================
1. ESTA PASADA TIENE DOS PARTES OBLIGATORIAS
======================================================================

PARTE A:

INVESTIGACIÓN PROFUNDA DEL MOTOR ORIGINAL.

PARTE B:

IMPLEMENTACIÓN EN RCM BASADA EN LO DESCUBIERTO.

NO QUIERO:

investigar
→ hacer informe
→ detenerse.

QUIERO:

INVESTIGAR
→ TOMAR DECISIONES
→ IMPLEMENTAR
→ TESTEAR
→ ENTREGAR.

EN EL MISMO PASE.

Sólo detenerse antes de implementar si existe una imposibilidad técnica REAL que
haga peligroso continuar.

Si una capacidad concreta no puede demostrarse:

NO INVENTARLA.

Implementar el subconjunto comprobado y documentar la limitación.

======================================================================
2. REGLA FUNDAMENTAL
======================================================================

NO DISEÑES TODAVÍA EL SISTEMA RUNTIME.

PRIMERO INVESTIGA CÓMO LO HACE REDEMPTION.

La prioridad es:

1. mecanismos originales del juego;
2. patrones originales de scripts;
3. API Codex real;
4. contratos ya comprobados por RCM;
5. sólo entonces código propio.

NO reinventar una solución si Nihilistic ya dejó una.

======================================================================
3. INVESTIGACIÓN OBLIGATORIA DEL MOTOR ORIGINAL
======================================================================

Analiza exhaustivamente:

research/API_SIGNATURES.txt
research/ALL_CODEX.bytecode.txt
research/engine_evidence/
research/sdk/
research/original/ cuando esté disponible
source_manifest
catálogos originales
NOT
NSD
NSS
NCO
scripts/classes originales
documentación SDK

y cualquier evidencia relevante existente.

======================================================================
3.1 — BUSCAR GENERADORES ORIGINALES
======================================================================

Buscar por nombres, strings, bytecode y referencias:

Generator
Spawner
Spawn
SpawnThing
SpawnThingNear
CreateThing
Respawn
ReSpawn
Summon
Summoned
Reinforcement
Wave
Encounter
Monster
Enemy
CreateActor
Generate
Portal
Emitter

NO limitarse a búsqueda literal.

Buscar TODOS los call sites de:

SpawnThing
SpawnThingNear
CreateThing
PreloadTemplate

Registrar:

clase;
método;
contexto;
template;
timer;
condiciones;
qué hace con el GUID;
cómo comprueba muerte;
cómo elimina;
cómo vuelve a generar.

======================================================================
3.2 — INVESTIGAR EL "ORIGINAL GENERATOR SCRIPT"
======================================================================

Existe referencia externa a un:

    original generator script

del juego.

NO aceptar esa referencia como hecho suficiente.

Intentar localizar EXACTAMENTE:

- nombre de clase;
- recurso;
- plantilla;
- script;
- bytecode;
- mapas que lo utilizan;
- propósito;
- variables;
- timers;
- spawn limit;
- respawn;
- cleanup;
- condiciones;
- comportamiento tras save/load.

Si existe:

documentarlo y aprovechar su diseño cuando sea útil.

Si NO se localiza:

documentar:

    NOT FOUND AFTER EXHAUSTIVE SEARCH

y continuar usando APIs demostradas.

NO detener implementación por esto.

======================================================================
3.3 — SPAWN NATIVO
======================================================================

Investigar las diferencias REALES entre:

    CodexWorld.CreateThing
    CodexThing.SpawnThing
    CodexThing.SpawnThingNear

Determinar:

- requisitos;
- template loading;
- coordenadas;
- orientación;
- localidad;
- navegación;
- distancia;
- flags;
- owner;
- save behavior;
- multiplayer behavior conocido;
- resultado cuando falla;
- GUID 0;
- colisión;
- aparición dentro de geometría;
- diferencias entre actor/item/prop.

Investigar también:

    PreloadTemplate

y cualquier factory original relacionada.

======================================================================
3.4 — MUERTE / VIDA / DAÑO
======================================================================

Investigar:

GetActorHealth
GetActorMaxHealth
SetActorHealth
SetActorMaxHealth

y cualquier otro método relacionado.

Buscar callbacks originales de:

damage
hurt
hit
health
killed
death

IMPORTANTE:

NO asumir que existe callback de daño.

Si no existe callback fiable:

implementar vida por MUESTREO CONTROLADO.

Documentarlo claramente.

======================================================================
3.5 — HEALTH THRESHOLD
======================================================================

Queremos soportar:

    "cuando este actor baja del 50%"

    "cuando baja del 25%"

    "cuando le quedan 20 HP"

Investigar la forma más fiable.

Semántica recomendada:

DISPARAR AL CRUZAR EL UMBRAL:

    anterior > threshold
    actual <= threshold

NO:

disparar 300 veces mientras siga debajo.

Debe soportar:

    once

por defecto.

Si el actor puede pasar directamente de 60% a muerto entre dos muestras:

investigar qué comportamiento podemos garantizar.

NO afirmar que podemos ejecutar literalmente "antes de morir" si el motor no ofrece
un callback de daño previo.

En ese caso:

documentar la semántica real:

    "al detectar que la vida ha cruzado el umbral mientras el actor sigue válido"

y diseñar las fases de jefe alrededor de esa realidad.

======================================================================
3.6 — FLAGS INTERESANTES
======================================================================

Investigar específicamente:

THING_AF_SUMMONED
THING_FLAG_EMITTER
THING_FLAG_PROXIMITYTRIGGER

y cualquier flag relacionado con:

spawn;
AI;
save;
corpse;
visibility;
invulnerability.

NO utilizar ninguno basándose sólo en su nombre.

Necesita evidencia original o prueba controlada.

======================================================================
3.7 — TIMERS
======================================================================

Sabemos que SetTimer puede acumular entradas y KillTimer importa.

Investigar patrones originales para:

- loops;
- respawn;
- waves;
- polling;
- retry;
- delayed spawn.

Evitar crear tormentas de timers.

Preferir UN LOOP DE CONTROL central por escena cuando tenga sentido.

======================================================================
3.8 — SAVE / RESTORE
======================================================================

Investigar:

SaveBoolean
RestoreBoolean
SaveInt
RestoreInt
SaveFloat
RestoreFloat

y patrones originales.

Determinar cómo persistir:

- generador iniciado;
- pausado;
- completado;
- wave actual;
- total generado;
- kills;
- thresholds de jefe ya disparados;
- cooldown;
- estado de repetición.

NO gastar Chronicle Flags innecesariamente si los records nativos son más apropiados.

======================================================================
3.9 — RANDOM
======================================================================

Investigar qué usan los scripts originales para azar.

NO asumir java.util.Random si la JVM/biblioteca del juego no lo soporta de forma
contrastada.

Buscar:

Random
Rand
random

Si existe patrón original:

usar ese.

Si no:

implementar sólo selección determinista / round-robin inicialmente.

NO introducir azar roto.

======================================================================
4. INFORME DE INVESTIGACIÓN
======================================================================

Crear:

research/dynamic_encounters/ENGINE_SPAWNER_AUDIT.md

y:

research/dynamic_encounters/spawn_calls.json

El informe debe clasificar cada descubrimiento:

CONFIRMADO EN ORIGINAL
CONFIRMADO EN SDK
CONFIRMADO POR RCM
INFERIDO
NO ENCONTRADO
REQUIERE PRUEBA NATIVA

No debe detener la implementación.

Debe servir como fundamento de ella.

======================================================================
5. FILOSOFÍA DE PRODUCTO
======================================================================

LA FEATURE NO SE LLAMA PRINCIPALMENTE:

SpawnerFactoryDefinitionEditor

La interfaz humana debe hablar de:

    Encuentro dinámico

Dentro, cuando sea útil:

    Generador

La intención manda.

El usuario quiere:

    "quiero enemigos aquí"

NO:

    "quiero configurar un poll loop que instancia templates".

======================================================================
6. NO ROMPER ENCOUNTERS EXISTENTES
======================================================================

El sistema actual de encuentros sigue siendo válido.

Actualmente:

encounter
=
grupo de actores authored

spawn_encounter
=
crear ese grupo

encounter_complete
=
todos sus miembros muertos

CONSERVARLO.

NO reescribir encounters existentes.

El sistema dinámico se añade ENCIMA.

======================================================================
7. POR QUÉ NECESITAMOS UN NUEVO CONCEPTO RUNTIME
======================================================================

Los encounters actuales referencian actores concretos del proyecto.

Eso NO sirve bien para:

- crear 100 ratas sucesivamente;
- reutilizar la misma template infinitamente;
- generar actores que no existen como entidades authored;
- seleccionar aleatoriamente;
- respawn;
- mantener N vivos;
- waves arbitrarias.

Por tanto crear una entidad authoring específica:

    DYNAMIC ENCOUNTER / GENERATOR

Puede almacenarse internamente como:

    generators

si es la solución más limpia.

NO crear cientos de actores ficticios en project.yaml.

======================================================================
8. FORMATO DE PROYECTO
======================================================================

ESTO ES UNA FEATURE DE FORMATO NUEVA.

Usar:

    project_format: 10

si realmente necesita nuevos datos persistentes, como parece.

CURRENT_PROJECT_FORMAT:

    10

PERO:

NO modificar automáticamente todos los proyectos 9.

Reglas:

- format 9 sigue abriendo;
- format 9 sigue funcionando;
- tutorial actual puede seguir en 9;
- al utilizar por primera vez Encuentro dinámico:
      hacer backup;
      actualizar a 10;
      informar de forma discreta;
- nuevos proyectos pueden nacer directamente como 10.

RCM antiguo ya rechazará format 10 mediante el gate existente.

NO crear framework gigante de migración.

======================================================================
9. ENTIDAD DE AUTORÍA
======================================================================

Diseñar una estructura clara.

EJEMPLO CONCEPTUAL, NO CONTRATO OBLIGATORIO:

generators:
  - id: crypt_attack
    name: Emboscada de la cripta

    mode: waves

    spawn_points:
      - spawn_a
      - spawn_b
      - spawn_c

    waves:
      - groups:
          - id: ghouls
            template: GhoulMale
            count: 4

      - delay: 3
        groups:
          - id: rats
            template: Rat
            count: 6

    limits:
      max_alive: 8

    persistence:
      once: true

No copiar este schema ciegamente.

Primero diseñarlo con:

- validación clara;
- referencias seguras;
- diff legible;
- compatibilidad;
- serialización sencilla.

======================================================================
10. UI PRINCIPAL: ULTRA SIMPLE
======================================================================

NO nueva pestaña.

NO nuevo gran editor.

Dentro de:

    Campaña / Vista global

Añadir:

    + Encuentro dinámico…

También puede aparecer en:

    Asistentes de crónica…

======================================================================
11. ASISTENTE
======================================================================

PRIMERA PÁGINA:

¿QUÉ QUIERES CREAR?

    Emboscada
    Oleadas
    Generador continuo
    Refuerzos
    Jefe por fases

Cada opción con UNA FRASE.

EMBOSCADA

    Aparece un grupo cuando ocurre algo.

OLEADAS

    Un grupo tras otro hasta completar el combate.

GENERADOR CONTINUO

    Sigue creando enemigos respetando un límite.

REFUERZOS

    Añade enemigos cuando se cumple una condición.

JEFE POR FASES

    Reacciona a la vida del jefe y puede lanzar refuerzos, eventos y cinemáticas.

======================================================================
12. PÁGINA ENEMIGOS
======================================================================

QUIERO UN SELECTOR DE ENEMIGOS BUENO DE VERDAD.

NO:

campo de texto con template ID.

Usar Resource Browser / catálogo.

Mostrar:

    nombre
    modelo si puede previsualizarse
    template
    procedencia
    tipo
    AI
    información original confirmada

Filtro destacado:

    Enemigos usados por Redemption

Además:

    Todos los actores
    Juego original
    Recursos propios

======================================================================
13. CATÁLOGO DE ENEMIGOS ORIGINAL
======================================================================

Investigar los templates originales para poder distinguir de forma fiable:

- actores utilizados como enemigos;
- actores neutrales;
- NPC;
- animales;
- monstruos;
- vampiros;
- humanos;
- etc.

Buscar evidencia en:

NOT;
team;
actor type;
AI;
flags;
escenas originales;
scripts originales.

NO CLASIFICAR POR NOMBRE si se puede evitar.

NO inventar:

"dificultad 7/10"

sin fundamento.

Sí mostrar metadata REAL cuando exista:

    actor type
    clan
    team
    AI
    health
    flags
    campaign usage
    source

si los tags correspondientes están contrastados.

======================================================================
14. ENEMY ENTRY
======================================================================

Cada entrada básica debe poder ser:

    Ghoul
    Cantidad: 4

Opciones avanzadas por tipo:

    peso de selección
    cantidad
    retardo
    punto(s) permitido(s)
    límite simultáneo
    health multiplier
    health inicial
    team override
    AI initial state

PERO:

sólo exponer overrides cuya API esté confirmada.

DEFAULT:

    usar el template ORIGINAL tal cual.

Eso es fundamental.

======================================================================
15. VIDA / DIFICULTAD
======================================================================

Como Get/Set health/max health existen:

permitir opcionalmente:

    Vida:
        Original
        x0.5
        x1
        x1.5
        x2
        Personalizada

Implementar el multiplicador SOBRE la vida real del actor generado.

NO modificar el template original.

NO inventar otra estadística "difficulty".

Puede ser útil para:

    élite
    miniboss
    boss

pero esas palabras son presentación, no nueva mecánica.

======================================================================
16. SPAWN POINTS
======================================================================

DEFAULT SEGURO:

usar WAYPOINTS ya existentes.

El usuario puede:

    Añadir punto de aparición

y colocarlo en Espacio 3D.

NO necesitamos otra geometría.

Un generator referencia:

    uno
    o varios waypoints.

======================================================================
17. DISTRIBUCIÓN ENTRE PUNTOS
======================================================================

Soportar, si técnicamente seguro:

    Secuencial
    Rotatorio
    Aleatorio

Opciones avanzadas:

    no repetir último punto
    punto específico por grupo

NO crear coordenadas random arbitrarias dentro de un volumen salvo que la
investigación demuestre una colocación segura.

Un waypoint authored es mucho más fiable.

======================================================================
18. SPAWN CERCA DEL JUGADOR
======================================================================

Si SpawnThingNear demuestra ser suficientemente fiable:

ofrecer:

    Cerca del jugador

como método.

Debe quedar claro que:

    el motor decide el punto cercano.

NO mezclarlo con posición authored exacta.

======================================================================
19. PORTALES / GENERADORES VISIBLES
======================================================================

Quiero poder hacer:

    portal
    nido
    puerta
    máquina
    agujero
    sarcófago

del que "salen" enemigos.

PERO NO INVENTAR UNA ENTIDAD GRÁFICA ESPECIAL.

Usar:

    prop normal

opcionalmente vinculado como:

    Representación visual

El generador runtime sigue siendo lógico.

Opciones:

    prop visible
    sonido al generar
    animación/sequence al empezar
    sonido por spawn

utilizando sistemas YA EXISTENTES.

Si existe un emitter original adecuado y está bien comprendido:

puede usarse.

Si no:

NO fabricar un sistema de partículas nuevo.

======================================================================
20. MODOS DE GENERADOR
======================================================================

==================================================
20.1 — EMBOSCADA
==================================================

Cuando se activa:

spawn del grupo.

Opciones:

    todos a la vez
    escalonados cada X segundos

Completa:

    cuando todos mueren

DEFAULT:

    una sola vez.

==================================================
20.2 — OLEADAS
==================================================

Wave 1
Wave 2
Wave 3
...

Cada wave:

    tipos
    cantidades
    puntos
    delay inicial

Transición configurable:

    cuando mueren todos
    después de X segundos
    manual/condición avanzada

DEFAULT:

    siguiente cuando wave anterior está limpia.

==================================================
20.3 — GENERADOR CONTINUO
==================================================

Parámetros sencillos:

    Crear uno cada: X segundos
    Máximo vivos: N

Opciones:

    máximo total
    pool de enemigos
    pesos
    spawn points

Ejemplo:

    cada 5 segundos
    máximo 6 vivos
    infinito

NO debe producir más de max_alive.

==================================================
20.4 — MANTENER PRESIÓN
==================================================

Modo opcional:

    Objetivo de enemigos vivos: N

Ejemplo:

    objetivo 4
    máximo 6

Si bajan de 4:

genera reemplazos.

Perfecto para arena / asedio.

==================================================
20.5 — REFUERZOS
==================================================

No empieza inmediatamente.

Se dispara por:

    timer
    condición
    muerte
    salud
    flag
    quest
    evento normal.

Ejemplo:

    cuando quedan 2 guardias
    llegan 4 más.

==================================================
20.6 — JEFE POR FASES
==================================================

Seleccionar:

    actor authored

O:

    actor único generado por el propio generator.

Configurar:

    al 75%
    al 50%
    al 25%

Cada threshold puede ejecutar ACCIONES NORMALES DE RCM.

Ejemplo:

50%:

    reproducir sequence
    spawn wave
    set flag

25%:

    spawn 6 ratas
    start music

0/death:

    complete quest
    stop generator
    open exit

======================================================================
21. HEALTH THRESHOLDS
======================================================================

Añadir soporte GENERAL para vida.

Idealmente mediante condición:

    actor_health

Ejemplo conceptual:

actor_health:
    actor: boss
    comparison: <=
    percent: 50

o:

    value: 100

Soportar:

    porcentaje
    HP absolutos

COMPARADORES razonables:

    <
    <=
    >
    >=

PERO EN UI BÁSICA:

    "Cuando la vida baje al 50%"

======================================================================
22. STATE_CHANGED
======================================================================

Aprovechar el sistema existente cuando sea posible.

Un evento:

    state_changed

con:

    actor_health <= 50%

puede disparar las acciones.

No crear otro motor de eventos paralelo si no hace falta.

Para actores dinámicos generados:

el generator debe exponer una forma estable de referirse al actor/rol.

======================================================================
23. ROLES / SLOTS
======================================================================

Para generadores complejos usar IDs humanos internos.

Ejemplo:

    boss
    guards
    reinforcements

Una entrada:

    role: boss
    template: TremereLord
    count: 1

permite:

    boss health 50%
    boss killed

NO hacer que el autor tenga que manejar GUID runtime.

GUID es detalle interno.

======================================================================
24. EVENTOS DEL GENERADOR
======================================================================

Integrar con Event Editor.

Añadir, si encaja arquitectónicamente:

    generator_started
    wave_started
    wave_complete
    generator_complete
    generator_stopped

NO añadir veinte callbacks innecesarios.

Para casos derivados usar condiciones.

======================================================================
25. ACCIONES DEL GENERADOR
======================================================================

Añadir al ACTION catalog:

    start_generator
    stop_generator
    pause_generator
    resume_generator

Considerar:

    reset_generator

como AVANZADO únicamente.

Estas acciones permiten:

    conversación -> empieza combate
    boss 50% -> empieza refuerzos
    quest complete -> detiene portal
    trigger_leave -> pausa generador

======================================================================
26. CUÁNDO EMPIEZA
======================================================================

El asistente debe ofrecer:

    Al entrar en escena
    Al entrar en una zona
    Al hacer clic en objeto
    Al terminar conversación
    Al morir actor
    Al terminar encuentro
    Después de X segundos
    Cuando se cumple una condición
    Manualmente desde otro evento

Eso debe mapear al Event System existente.

NO crear "start condition engine" duplicado.

======================================================================
27. CUÁNDO SE DETIENE
======================================================================

Opciones básicas:

    Cuando termina
    Nunca / hasta que otro evento lo detenga
    Cuando el jugador sale de una zona

Opciones avanzadas:

    flag
    quest
    timer
    generados totales
    kills
    condición.

======================================================================
28. COMPLETION
======================================================================

Un generator finite se considera COMPLETE cuando:

    no quedan waves por generar
    Y
    no quedan enemigos generados vivos

salvo configuración diferente.

NO considerar completado sólo porque se generó la última wave.

======================================================================
29. CONTADORES
======================================================================

Mantener internamente:

    wave actual
    total generado
    vivos
    muertos
    total por role

Exponer condiciones útiles:

    enemigos vivos <= N
    muertos >= N
    wave == N
    generator complete

NO obligar al usuario normal a usar esas condiciones.

======================================================================
30. SPAWN FAILURE
======================================================================

EL MOTOR PUEDE RECHAZAR UN SPAWN.

NO entrar en loop infinito.

Implementar política:

    intento
    retry limitado
    siguiente spawn point
    trace

Después de N fallos:

    generator error/stall

NO bloquear el juego.

Trace:

GENERATOR_SPAWN_FAILED
generator=
template=
point=
attempt=

======================================================================
31. OWNERSHIP
======================================================================

Cada GUID generado pertenece a:

    generator
    role
    wave

RCM debe saber:

    este enemigo es mío.

NUNCA retirar:

    NPC original
    enemigo estático
    actor de otro generator

al detener/limpiar.

======================================================================
32. CLEANUP
======================================================================

Opciones:

DEFAULT:

    muertos se dejan al comportamiento normal del juego.

Al detener:

    no eliminar enemigos vivos automáticamente

salvo opción:

    Retirar enemigos generados al detener

AVANZADO.

Si Remove sobre cadáveres/actores vivos tiene problemas:

NO ofrecer hasta confirmarlo.

======================================================================
33. REPEAT / RESPAWN
======================================================================

Ofrecer presets claros:

    Una vez
    Cada vez que vuelves a la escena
    Tras cooldown
    Continuo

Persistencia exacta debe estar documentada.

DEFAULT STORY:

    Una vez.

DEFAULT SPAWNER:

    Continuo mientras activo.

======================================================================
34. SAVE / LOAD ES BLOQUEADOR
======================================================================

ESTA FEATURE NO ES VÁLIDA SI DUPLICA ENEMIGOS TRAS CARGAR.

Diseñar desde el principio:

SAVE a mitad de wave.

LOAD.

Debe restaurar correctamente:

    started
    paused
    wave
    counters
    thresholds
    completion

Y reconciliar actores generados existentes.

NO spawn duplicado.

NO reward duplicada.

NO volver a disparar threshold 50%.

======================================================================
35. REENTRY
======================================================================

Salir de escena y volver.

Comportamiento según política:

ONCE:

    si completado:
        sigue completado.

RESET ON REENTRY:

    vuelve al estado inicial.

RESUME:

    continúa estado persistido.

No dejar generators zombies funcionando en otra escena.

======================================================================
36. BOSS PHASE SAFETY
======================================================================

Threshold:

50%

debe disparar exactamente una vez.

Incluso con:

save
load
salir
volver

No repetir:

cinemática
XP
wave
reward

salvo que expresamente sea repeatable.

======================================================================
37. ACCIONES EN THRESHOLD
======================================================================

NO crear una lista nueva de acciones.

Usar TODAS las ACTIONS actuales de RCM.

Por ejemplo:

    spawn encounter
    start generator
    stop generator
    set flag
    advance quest
    start conversation
    play sequence
    start music
    play sound
    open exit
    etc.

Así la feature se integra con TODO RCM.

======================================================================
38. RANDOM ENEMY POOLS
======================================================================

Si la investigación confirma un RNG seguro:

permitir:

POOL:

    Ghoul        peso 5
    Rat          peso 3
    Nosferatu    peso 1

Modo:

    Elegir uno por spawn.

Basic UI puede mostrar:

    Aleatorio entre estos enemigos.

Advanced:

    pesos.

Si RNG no está confirmado:

round-robin.

NO bloquear toda la feature por Random.

======================================================================
39. LIMITES DE SEGURIDAD
======================================================================

Definir límites razonables.

NO quiero:

un error de usuario
→ 9000 actores
→ Vampire.exe explota.

Ejemplos de validaciones:

    max_alive >= 1
    interval >= mínimo seguro
    counts acotados
    waves acotadas

Investigar límites prácticos antes de decidir valores.

Advanced puede permitir valores mayores con warning.

======================================================================
40. RENDIMIENTO
======================================================================

RCM genera Java 45.3.

Evitar:

- un método Java monstruoso;
- cientos de timers independientes;
- arrays sin límite;
- memoria creciente infinitamente;
- guardar todos los GUID históricos.

Para generators continuos:

guardar sólo:

    activos
    counters
    estado necesario.

Un enemigo muerto que ya no es relevante debe salir del tracking activo.

======================================================================
41. CONTROL LOOP
======================================================================

Preferir, si encaja con runtime actual:

UN POLL LOOP DE ESCENA

que controle:

    events sampled
    paths
    generators
    health thresholds

antes que:

    timer por enemigo
    timer por wave
    timer por generator
    timer por threshold.

NO crear una bomba de SetTimer.

======================================================================
42. TRACE
======================================================================

Añadir trazas útiles:

GENERATOR_START
GENERATOR_STOP
GENERATOR_PAUSE
GENERATOR_RESUME

GENERATOR_SPAWN
generator=
wave=
role=
template=
guid=
point=

GENERATOR_KILL
generator=
role=
guid=

GENERATOR_THRESHOLD
generator=
role=
percent=

GENERATOR_WAVE_START
GENERATOR_WAVE_COMPLETE

GENERATOR_COMPLETE

GENERATOR_SPAWN_FAILED

Esto debe integrarse con:

    Prueba / Depuración

y navegación al generator correspondiente.

======================================================================
43. STORY GRAPH
======================================================================

Representar generators SIN hacer el gráfico ilegible.

Mostrar:

Trigger/Event
   ↓
Generator
   ↓
Wave / Complete
   ↓
acciones importantes

No representar cada enemigo generado runtime.

======================================================================
44. REFERENCES
======================================================================

Buscar referencias debe entender:

generator
spawn points
enemy templates
trigger
events
actions
boss actor
waves

Safe Delete debe impedir:

borrar waypoint usado como spawn point;
borrar actor usado como boss;
borrar generator referenciado por start_generator.

======================================================================
45. DUPLICAR
======================================================================

Duplicar generator:

nuevo ID.

Mantener:

templates;
config;
spawn points;

pero revisar callbacks/referencias para no crear dos generadores enlazados
accidentalmente a los mismos eventos si eso no es seguro.

======================================================================
46. PROPERTIES
======================================================================

Seleccionar generator muestra:

Nombre
Tipo
Estado de activación
Enemigos
Puntos
Completion

Luego:

    ▸ Opciones avanzadas

Dentro:

limits
persistence
timing
random
cleanup
etc.

NO mostrar 42 campos permanentemente.

======================================================================
47. VISTA 3D
======================================================================

Cuando generator está seleccionado:

resaltar:

    spawn points
    trigger de activación
    prop visual vinculado

Con líneas discretas.

NO representar todos los posibles enemigos.

Opcionalmente iconos:

    1
    2
    3

sobre spawn points.

======================================================================
48. QUICK CREATION FROM 3D
======================================================================

QoL MUY IMPORTANTE:

desde Espacio 3D:

click derecho / Añadir

    Encuentro dinámico aquí…

Puede:

1. crear waypoint en el punto;
2. abrir el wizard;
3. usar ese waypoint como primer spawn point.

Eso hace la creación MUY rápida.

======================================================================
49. RECIPES
======================================================================

Añadir recetas de intención humana.

BUENAS:

    Emboscada aquí
    Tres oleadas
    Portal continuo
    Refuerzos
    Jefe por fases

NO:

    Crear polling health conditional generator event.

El usuario piensa en escenas, no en arquitectura.

======================================================================
50. PRESETS
======================================================================

Preset:

EMBOSCADA SIMPLE

    3 enemigos
    spawn todos
    once
    complete all dead

OLEADAS

    3 waves
    siguiente al limpiar
    2 s entre waves

GENERADOR

    1 cada 5 s
    máximo 5 vivos
    hasta stop

REFUERZOS

    manual start
    group once

JEFE

    50%
    25%
    death

El usuario modifica después.

======================================================================
51. CREACIÓN DE JEFE POR FASES
======================================================================

Wizard:

Selecciona jefe:

    [actor existente]
    o
    [generar jefe]

Añadir fase:

    Vida: 50%

    Acciones:
        [ + Añadir ]

Ejemplo visual:

100%
  │
50% ──▶ Oleada de refuerzos
  │
25% ──▶ Música + cinemática
  │
0%  ──▶ Abrir salida + completar misión

MUY intuitivo.

======================================================================
52. "ANTES DE MATARLO"
======================================================================

Este caso es IMPORTANTE.

Si el usuario quiere:

"cuando está casi muerto haz algo"

ofrecer:

    Al bajar al X%

NO llamarlo:

    Before death

salvo que el motor permita una garantía real.

Tooltip:

    "Se activa al detectar que la vida cruza este porcentaje."

Si polling significa que un golpe mortal puede saltarse la fase:

INVESTIGAR mecanismos seguros.

Posible opción avanzada SÓLO SI ESTÁ BIEN SOPORTADA:

    Proteger cambio de fase

por ejemplo impedir muerte en ese tramo.

PERO NO IMPLEMENTAR INVULNERABILIDAD AUTOMÁTICA sin entender perfectamente
su semántica.

======================================================================
53. ENEMIGOS ORIGINALES
======================================================================

QUIERO PODER USAR FACILÍSIMAMENTE LOS ENEMIGOS QUE YA EXISTEN EN REDEMPTION.

Crear una vista/filtro:

    Enemigos de la campaña original

Agrupar, si puede inferirse de forma fiable:

    Medieval
    Moderna
    Humanos
    Vampiros
    Monstruos
    Animales
    etc.

Si no puede inferirse un grupo:

NO inventarlo.

Mostrar:

    Otros / Sin clasificar.

======================================================================
54. ENEMY DETAILS
======================================================================

Cuando selecciono un template:

mostrar sólo datos confirmados.

Por ejemplo, si disponibles:

    Template
    Modelo
    Tipo
    Clan
    Team
    AI
    Vida
    Script
    Fuente original
    Usado en...

Esto convierte el catálogo en algo realmente útil para crear crónicas.

======================================================================
55. PREVIEW
======================================================================

Si ya podemos mostrar el modelo mediante la infraestructura del viewport:

permitir botón:

    Ver modelo

o preview existente.

NO crear un renderer nuevo.

======================================================================
56. INTEGRITY
======================================================================

Warnings:

Generator sin spawn points.

Generator sin start.

Wave vacía.

Boss threshold duplicado.

Threshold 50 y 50.

Generator infinito sin max_alive.

Start y stop imposibles.

Template no disponible.

Spawn point eliminado.

Completion action que nunca puede ocurrir.

Generator sin ninguna vía de activación.

Generator finite sin completion detectable.

======================================================================
57. BUILD
======================================================================

La generación Java debe:

- seguir compilando contra Codex real;
- producir bytecode 45.3;
- no requerir librerías externas;
- no requerir JRE moderno runtime;
- no cambiar originales.

======================================================================
58. STRESS TEST
======================================================================

Crear fixtures extremos.

Ejemplo:

20 generators
10 waves cada uno
varios templates
thresholds
events
actions

Compilar.

Comprobar:

- límites de método;
- tamaño class;
- tiempos;
- memoria Python;
- validación;
- Story Graph.

Si se acerca al límite Java:

particionar funciones.

======================================================================
59. TEST UNITARIOS
======================================================================

Obligatorios:

FORMAT

format9 abre.
format10 abre.
RC3 viejo rechazaría 10 conceptualmente.
generator validation.

SPAWN

one shot.
multi spawn.
multiple points.
max alive.
max total.
failed spawn.
retry.
stop.
pause.
resume.

WAVES

next on clear.
delay.
overlap si soportado.
complete.
empty invalid.

CONTINUOUS

interval.
cap.
replacement.
stop condition.

HEALTH

static actor 50%.
generated boss 50%.
crossing only.
not repeated.
absolute HP.
save restore threshold.

KILLS

alive count.
kill count.
wave completion.

SAVE LOAD

mid-wave.
mid-generator.
boss after threshold.
generator completed.
no duplicate rewards.

REENTRY

once.
reset.
resume.

REFERENCES

waypoint.
boss.
generator actions.
safe delete.

EDITOR

wizard.
presets.
advanced collapsed.
resource selector.
duplicate.
undo.
redo.

I18N

ES/EN.

======================================================================
60. RUNTIME DOUBLES
======================================================================

Extender doubles para modelar:

spawn GUIDs;
health;
max health;
alive/dead;
Remove;
team si se usa;
timers;
save/restore;
scene transition.

Simular:

boss recibe daño.

60 → 49.

Debe disparar threshold 50 una vez.

Luego:

49 → 20

threshold 25 una vez.

======================================================================
61. EJEMPLO DE REGRESIÓN
======================================================================

Crear fixture:

DYNAMIC ENCOUNTER LAB

Escena:

trigger entrada.

Wave 1:
    3 ratas.

Wave 2:
    2 enemigos.

Boss:
    1 enemigo.

Boss 50%:
    spawn 2 adds.

Boss 25%:
    play sound.

Boss muerto:
    complete quest.

Guardar/cargar entre estados.

======================================================================
62. SHOWCASE
======================================================================

NO TOCAR EL RECORRIDO PRINCIPAL.

Añadir al LABORATORIO OPCIONAL una estación:

    Encuentros dinámicos

Pequeña.

Ejemplo:

Guía:
    "Probar generador"

→ 2 enemigos.

Después:

    miniboss

al 50%:

→ aparece un refuerzo.

NO convertir Showcase en Doom.

Añadir enlaces editoriales.

======================================================================
63. TUTORIAL RÁPIDO
======================================================================

NO MODIFICAR.

"Una carta al amanecer" sigue intacto.

Dynamic Encounters es avanzado respecto al primer tutorial.

======================================================================
64. DOCUMENTACIÓN
======================================================================

Crear:

docs/DYNAMIC_ENCOUNTERS.md
docs/DYNAMIC_ENCOUNTERS.en.md

Debe explicar primero:

EMBOSCADA EN 30 SEGUNDOS.

Ejemplo:

1. + Encuentro dinámico.
2. Emboscada.
3. Selecciona 3 ratas.
4. Selecciona zona.
5. F5.

Después:

Oleadas.
Generador.
Boss.

Sólo al final:

detalles avanzados.

======================================================================
65. TOOLTIP / AYUDA
======================================================================

Cada modo:

EMBOSCADA
"Un grupo aparece una vez."

OLEADAS
"Varios grupos aparecen uno tras otro."

GENERADOR
"Crea nuevos enemigos mientras esté activo."

REFUERZOS
"Un grupo aparece cuando otro evento lo solicita."

JEFE POR FASES
"Ejecuta acciones al bajar la vida del jefe."

Eso es suficiente.

======================================================================
66. MANUAL RUNTIME CHECKLIST
======================================================================

YO HAGO LA PRUEBA DENTRO DE REDEMPTION.

NO AUTOMATIZAR GAMEPLAY.

Checklist corto:

DYN01
Trigger → aparecen 3 enemigos.

DYN02
Al matarlos → aparece wave 2.

DYN03
Generator continuo respeta max_alive.

DYN04
Stop generator deja de generar.

DYN05
Boss 50% dispara UNA vez.

DYN06
Boss 25% dispara UNA vez.

DYN07
Boss death completa encounter/quest.

DYN08
Save/load a mitad de wave sin duplicados.

DYN09
Save/load después de threshold sin repetirlo.

DYN10
Salir y volver respeta política de persistencia.

DYN11
F5 tras editar count/template actualiza.

DYN12
Spawn failure no cuelga el juego.

======================================================================
67. NO DECLARAR MÁS DE LO PROBADO
======================================================================

Estados:

OFFLINE VERIFIED
COMPILED
DEPLOYED
MANUAL RUNTIME TEST REQUIRED
RUNTIME VERIFIED
RUNTIME FAILED

NO decir:

"health thresholds funcionan en Redemption"

sólo porque pasan doubles.

======================================================================
68. NO HACER
======================================================================

NO:

editor de geometría.

NO:

nuevo navmesh.

NO:

sistema de partículas propio.

NO:

nuevo lenguaje de scripting.

NO:

Behaviour Tree editor.

NO:

sistema de loot nuevo.

NO:

sistema de stats nuevo.

NO:

difficulty system inventado.

NO:

multiplayer director sofisticado.

NO:

procedural dungeon system.

NO:

AI director tipo Left 4 Dead.

NO:

otra pestaña principal.

NO:

reescribir Event System.

NO:

reescribir Encounter System actual.

======================================================================
69. PRINCIPIO DE ARQUITECTURA
======================================================================

DYNAMIC ENCOUNTER DEBE SER UNA CAPA DE AUTORÍA SOBRE CAPACIDADES REALES.

NO OTRO MOTOR DENTRO DE RCM.

Debe reutilizar:

Resource Browser
Waypoints
Triggers
Conditions
Actions
Events
Quest
Flags
Sequences
Audio
Story Graph
References
Debug Trace

TODA LA POTENCIA DE RCM YA EXISTENTE.

======================================================================
70. PRINCIPIO DE UX
======================================================================

EL 90% DE USUARIOS DEBE PODER IGNORAR:

max_total
weights
persistence mode
cleanup
spawn retry
health sampling
GUID tracking

Y aun así crear:

    una emboscada
    tres oleadas
    un generador
    un boss.

La potencia avanzada está ahí.

NO delante.

======================================================================
71. CRITERIO DE ÉXITO
======================================================================

QUIERO PODER HACER ESTO:

click derecho en una calle.

"Encuentro dinámico aquí…"

"Oleadas"

Wave 1:
    4 ratas

Wave 2:
    3 ghouls

Wave 3:
    1 vampiro

Empieza:
    al entrar en esta zona

Al terminar:
    avanzar quest

[CREAR]

F5.

Y FUNCIONA.

Y TAMBIÉN PODER HACER:

Boss:
    Tremere

50%:
    empieza portal izquierdo

25%:
    empieza portal derecho
    música
    sequence

Muerto:
    parar portales
    abrir puerta
    completar misión

SIN ESCRIBIR JAVA.

======================================================================
72. INVESTIGACIÓN + IMPLEMENTACIÓN
======================================================================

NO ME DEVUELVAS ÚNICAMENTE:

"he descubierto que..."

Después del audit:

IMPLEMENTA.

Si el original generator resulta fantástico:

APROVÉCHALO.

Si es demasiado limitado:

usa el mecanismo nativo apropiado.

Si no existe:

construye la capa RCM con:

CreateThing / SpawnThingNear / timers / health / state

de forma contrastada.

======================================================================
73. INFORME FINAL
======================================================================

Entregar:

1. RESULTADOS DE INVESTIGACIÓN DEL MOTOR.

Exactamente qué mecanismos originales existen.

2. ORIGINAL GENERATOR SCRIPT.

Encontrado/no encontrado y evidencia.

3. ARQUITECTURA IMPLEMENTADA.

4. UX FINAL.

5. MODOS SOPORTADOS.

6. HEALTH THRESHOLDS.

Semántica exacta.

7. SAVE/LOAD.

Cómo evita duplicados.

8. LIMITACIONES.

Especialmente cualquier limitación de "antes de morir".

9. TESTS.

PASS/FAIL/SKIP.

10. EXAMPLES / SHOWCASE.

11. MANUAL RUNTIME CHECKLIST.

12. BUILD RC4.

13. USER RELEASE RC4.

14. WORKSPACE ARCHIVE.

======================================================================
74. VEREDICTO FINAL
======================================================================

Uno de:

RC4 DYNAMIC ENCOUNTERS
APROBADA PARA PRUEBA MANUAL

o:

RC4 NECESITA CORRECCIONES

NO declarar 1.0 final.

======================================================================
75. MANTRA
======================================================================

EL USUARIO NO QUIERE PROGRAMAR UN SPAWNER.

QUIERE DECIR:

    "CUANDO ENTRE AQUÍ,
     QUE SALGAN CINCO CABRONES."

RCM DEBE ENCARGARSE DEL RESTO.
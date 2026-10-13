QUIERO HACER UNA PASADA FINAL DE PRODUCTO SOBRE REDEMPTION CHRONICLE MAKER.

NOMBRE DE ESTA PASADA:

RC3 — PODA, COHERENCIA Y CIERRE DE PRODUCTO

======================================================================
0. CONTEXTO ABSOLUTAMENTE IMPORTANTE
======================================================================

Redemption Chronicle Maker YA ES UN PRODUCTO FUNCIONAL Y MUY AVANZADO.

NO estamos empezando una nueva fase.
NO quiero una nueva ronda de features.
NO quiero convertir RCM en una suite profesional gigantesca.
NO quiero añadir complejidad porque "quedaría bien".
NO quiero aprovechar esta pasada para meter ideas nuevas.

RC2 YA TIENE:

- editor visual;
- visor 3D;
- campañas multi-escena;
- actores;
- objetos;
- conversaciones;
- eventos;
- triggers;
- quests;
- encuentros;
- cámaras/secuencias;
- entradas;
- waypoints;
- recorridos;
- recursos propios;
- paquetes;
- build;
- deploy;
- F5 / PROBAR EN REDEMPTION;
- tutorial;
- showcase;
- recuperación;
- backups;
- protección de archivos;
- locking;
- traducción ES/EN;
- configuración;
- diagnósticos;
- depuración;
- etc.

NO HAY QUE AÑADIR MÁS SISTEMAS.

Esta pasada consiste en:

    PODAR
    SIMPLIFICAR
    UNIFICAR
    ELIMINAR RESTOS LEGACY
    REDUCIR RUIDO VISUAL
    ARREGLAR INCOHERENCIAS
    HACER MÁS CLARO EL PRODUCTO
    CERRAR PEQUEÑOS HUECOS DE SEGURIDAD

La filosofía sigue siendo:

    "Aurora Toolset, pero para Vampire: The Masquerade — Redemption"

El usuario debe pensar en:

    Escenario
    Actor
    Conversación
    Quest
    Trigger
    Entrada
    Waypoint
    Cámara
    Evento
    Probar

y NO en:

    pipeline interno
    formatos
    deploy
    manifests
    caches
    build internals
    recursos binarios
    Java
    archivos del motor

RCM debe acercarse cada vez más a:

    IDEA -> EDITAR -> PROBAR EN REDEMPTION

======================================================================
1. REGLA PRINCIPAL: PROHIBIDO FEATURE CREEP
======================================================================

ESTA RC3 NO PUEDE CONVERTIRSE EN OTRA MACROFASE.

NO añadir:

- nuevas pestañas;
- nuevos modos principales;
- command palette;
- temas;
- skins;
- otro dashboard;
- nuevos gestores;
- más sistemas de onboarding;
- más asistentes salvo correcciones de los actuales;
- historial tipo Git;
- control de versiones interno complejo;
- nuevas capas de abstracción;
- nuevos formatos de proyecto salvo lo estrictamente necesario;
- nuevos sistemas de scripting;
- nuevos tipos de recursos;
- nueva funcionalidad de runtime;
- nuevos editores;
- nuevas herramientas "porque ya que estamos...";
- geometría editable;
- nada que aumente significativamente el alcance.

SI durante la revisión encuentras algo que sería "guay añadir":

NO LO AÑADAS.

Apúntalo como posible trabajo futuro sólo si es realmente importante.

RC3 debe terminar con MENOS RUIDO que RC2.

======================================================================
2. NO ROMPER LO QUE YA ESTÁ BIEN
======================================================================

Hay varias partes que NO deben simplificarse ni sustituirse porque ya están bien
resueltas.

PRESERVAR:

- guardado atómico;
- escritura mediante fichero temporal;
- flush;
- fsync;
- os.replace;
- backups automáticos;
- autosave/recovery;
- detección de modificación externa;
- posibilidad de recargar / guardar copia / sobrescribir;
- ProjectLock / QLockFile;
- protección de archivos originales;
- aislamiento workspace / instalación del juego;
- validación;
- flujo de build;
- deploy administrado;
- gestión segura de paquetes;
- diagnóstico;
- F5 / PROBAR EN REDEMPTION;
- política de NO automatizar los menús internos del juego;
- separación entre verificación offline y prueba manual real.

NO rehacer sistemas sólidos sólo porque se podría escribir "más bonito".

======================================================================
3. OBJETIVO DE RC3
======================================================================

Al terminar RC3 quiero que RCM dé esta sensación:

    "Está terminado."

NO:

    "Tiene otras 14 cosas nuevas."

Debe sentirse:

- más limpio;
- menos técnico;
- menos redundante;
- más coherente;
- más fácil de explicar;
- más agradable nada más abrirlo;
- con menos opciones repetidas;
- con menos controles legacy;
- con un Showcase mucho más entendible;
- con mejor gestión al cambiar instalación del juego;
- con apertura/importación de proyectos más coherente;
- preparado para formatos futuros sin corromper proyectos.

======================================================================
4. PRIORIDAD ALTA — DOCK INFERIOR
======================================================================

Actualmente existe el dock:

    Problemas / Construcción / Referencias

y ocupa espacio incluso cuando el usuario no necesita verlo.

QUIERO CAMBIAR ESTO.

COMPORTAMIENTO DESEADO:

El dock inferior debe permanecer OCULTO cuando no tiene utilidad inmediata.

Debe abrirse automáticamente sólo en casos justificables:

1. validación con errores;
2. build iniciado;
3. build fallido;
4. usuario pide Referencias;
5. usuario abre explícitamente información que vive ahí.

NO debe robar aproximadamente 150-200 px de pantalla constantemente.

CASO DE VALIDACIÓN LIMPIA:

Si la validación no tiene errores relevantes:

    NO abrir automáticamente el dock.

Si estaba cerrado:

    mantenerlo cerrado.

Si estaba abierto porque el usuario lo abrió manualmente:

    no hace falta cerrárselo agresivamente.

OBJETIVO:

La ventana normal debe dedicar la máxima superficie posible a:

    árbol + editor + viewport + propiedades

NO al registro técnico.

TESTS:

- abrir proyecto válido -> dock no aparece porque sí;
- validar proyecto válido -> sigue oculto;
- validar proyecto con error -> aparece en Problemas;
- build -> aparece Construcción;
- buscar referencias -> aparece Referencias;
- volver a trabajar -> comportamiento estable;
- restaurar layout -> estado razonable.

======================================================================
5. PRIORIDAD ALTA — "CREAR CAMPAÑA" ES LEGACY
======================================================================

Actualmente los proyectos nuevos ya nacen como CampaignDocument / formato actual.

Por tanto el botón:

    Crear campaña

NO debe aparecer como parte del flujo normal de proyectos nuevos.

QUIERO:

- mostrar "Crear campaña" SÓLO si se ha abierto un proyecto antiguo / legacy que
  todavía necesite conversión;
- ocultarlo completamente en proyectos actuales;
- evitar que un usuario normal piense:
      "¿Pero no estoy ya creando una campaña?"

Si existe alguna ruta antigua de compatibilidad:

    mantenerla.

PERO:

    convertirla en excepcional;
    no presentarla como operación principal.

TESTS:

- proyecto nuevo actual -> botón NO visible;
- proyecto format actual -> NO visible;
- proyecto legacy compatible -> visible;
- conversión legacy -> funciona;
- tras convertir -> desaparece.

NO eliminar compatibilidad antigua si todavía es útil.

======================================================================
6. PRIORIDAD ALTA — SHOWCASE: EL CONTENIDO ESTÁ BIEN, LA GUÍA NO
======================================================================

EL SHOWCASE ACTUAL ESTÁ BIEN DISEÑADO INTERNAMENTE.

NO quiero rehacerlo.

La estructura actual es buena porque separa:

HISTORIA PRINCIPAL:

    taller -> archivo -> regreso

LABORATORIO OPCIONAL:

    cámaras
    animaciones
    recorridos
    sonido
    combate opcional
    etc.

ESO HAY QUE CONSERVARLO.

EL PROBLEMA ES SU README / GUÍA.

Actualmente la guía del Showcase contiene un muro gigantesco de enlaces técnicos:

    cam1
    cam2
    cam3
    event1
    controls1
    controls2
    ...
    decenas y decenas de IDs

Eso NO es una guía humana.

QUIERO REESCRIBIR LA GUÍA DEL SHOWCASE.

ESTRUCTURA DESEADA:

--------------------------------------------------
# Taller del Narrador

Breve explicación de qué es el Showcase.

## Empieza aquí

Explica:

1. abre el taller;
2. habla con Anezka;
3. habla con la guía;
4. acepta / prueba la historia principal;
5. viaja al archivo;
6. regresa.

Con enlaces sólo a las entidades principales.

## Ruta principal

Explicar brevemente:

- escena inicial;
- archivo;
- regreso;
- quest;
- conversaciones principales.

## Laboratorio opcional

Subapartados claros:

### Cámaras

Explicar qué demuestra.
Enlazar sólo a las conversaciones / secuencias importantes.

### Animaciones

Explicar qué demuestra.

### Recorridos / Waypoints

Explicar qué demuestra.

### Sonido

Explicar qué demuestra.

### Objetos y notas

Explicar qué demuestra.

### Combate opcional

Explicar que NO es obligatorio para completar el Showcase.

## Prueba de campo

Explicar las escenas de prueba real.

## Índice técnico completo

SÓLO AQUÍ puede existir la lista exhaustiva de enlaces.

--------------------------------------------------

El usuario debe poder seguir el Showcase SIN entender IDs internos.

No eliminar enlaces útiles.

Reorganizarlos.

El Showcase debe servir como:

    tutorial avanzado
    ejemplo de referencia
    banco de pruebas

NO como volcado de estructura interna.

======================================================================
7. REVISAR NOMBRES PEDAGÓGICOS DEL SHOWCASE
======================================================================

Hay entidades con nombres como:

    "01 · Anezka: empieza aquí"
    "02 · Guía: viaje y laboratorio opcional"
    "Rata de las minas · combate fácil y opcional"
    "Cartel del taller: leer nota"

ESTOS NOMBRES SON MUY ÚTILES DENTRO DEL EDITOR.

NO LOS CAMBIES A CIEGAS.

ANTES:

verifica si ese "name" aparece visible para el jugador dentro de Redemption.

CASO A:

si sólo sirve al editor:

    conservarlos.

CASO B:

si el jugador ve literalmente esos nombres:

    separar:
        nombre natural de juego
        comentario / etiqueta pedagógica del editor

PERO:

NO inventar un nuevo sistema de comentarios si ya existe una propiedad apta.

Usar lo que ya haya.

Si no existe una separación limpia y cambiarlo implica abrir otro subsistema:

    dejarlo como está
    documentar el resultado

NO generar una feature nueva sólo por esto.

======================================================================
8. PRIORIDAD ALTA — CAMBIO DE INSTALACIÓN DEL JUEGO Y CACHE
======================================================================

ESTE ES UN PROBLEMA REAL DE PRODUCTO.

Actualmente RCM mantiene catálogos/cache derivados de la instalación de Redemption.

Si el usuario cambia:

    Vampire.exe
    instalación GOG
    carpeta del juego
    versión / contenido de Resource.nob
    Codex.nob
    Chronicles
    classes.zip
    etc.

NO debemos seguir usando silenciosamente catálogos válidos pero pertenecientes a
otra instalación.

QUIERO:

asociar el cache/catalogue a una IDENTIDAD DE INSTALACIÓN.

NO hace falta inventar una base de datos compleja.

Puede ser un fingerprint suficientemente robusto.

Por ejemplo combinando SHA256 / metadatos de recursos fundamentales:

- Vampire.exe;
- Resource.nob;
- Codex.nob;
- classes.zip;
- quizá manifiesto de Chronicles relevante.

Lo importante es:

    cache generado para instalación A
    NO debe considerarse válido para instalación B.

COMPORTAMIENTO:

Al iniciar:

1. determinar instalación configurada;
2. calcular/verificar identidad;
3. comparar con identidad con la que se generó el cache;
4. si coincide:
       usar cache;
5. si no coincide:
       invalidar/reconstruir índices regenerables;
       informar de forma humana.

MENSAJE:

    "La instalación de Redemption ha cambiado.
     RCM actualizará sus catálogos."

NO:

    "manifest hash mismatch resource index invalid..."

PRESERVAR:

- archivos originales;
- proyectos;
- recursos propios;
- backups.

NO borrar datos de usuario.

Los catálogos son regenerables.

TESTS:

- primera instalación -> genera identidad;
- segundo arranque misma instalación -> no reconstruye;
- cambiar ruta a instalación equivalente -> decidir por contenido, no sólo path;
- cambiar Resource.nob -> reconstruye;
- cambiar classes.zip -> actualiza;
- cache corrupto -> reconstruye como ya hacía;
- proyecto del usuario intacto.

======================================================================
9. PRIORIDAD MEDIA-ALTA — IMPORTAR PROYECTO DEBE USAR EL MISMO FLUJO DE APERTURA
======================================================================

Actualmente la importación de proyecto sigue una ruta separada y termina asignando
el documento directamente.

QUIERO UNIFICAR ESTO.

Después de importar un .rcmproject:

    debe pasar por el mismo flujo lógico que una apertura normal.

Eso significa, según corresponda:

- ProjectLock;
- liberación del lock del proyecto anterior;
- recientes;
- recuperación;
- estado inicial;
- selección;
- refresh;
- validación;
- seguridad de archivo;
- cualquier otra inicialización que open_path ya centralice.

NO quiero dos caminos distintos:

    abrir proyecto
    importar proyecto

que inicialicen cosas diferentes.

IDEAL:

    importar -> obtener project.yaml
            -> open_path(project.yaml)

o equivalente arquitectónicamente limpio.

NO duplicar código.

TESTS:

- importar proyecto;
- queda bloqueado igual que uno abierto normalmente;
- aparece en recientes;
- cerrar / reabrir;
- importar mientras otro proyecto está abierto;
- cancelar correctamente;
- no deja lock anterior colgado.

======================================================================
10. PRIORIDAD MEDIA — LIMPIAR CONTROLES LEGACY DEL CAMPAIGN PANEL
======================================================================

CampaignPanel todavía crea controles antiguos relacionados con:

- Guardar;
- Integridad;
- Deploy;
- Ejecutar;
- Ruta del juego;
- Acceso del juego;
- etc.

varios de ellos se crean y luego se ocultan.

ESO ES DEUDA LEGACY.

El shell principal de producto YA TIENE:

- Guardar;
- Validar;
- Construir;
- PROBAR EN REDEMPTION;
- Configuración;
- herramientas;
- paths;
- etc.

QUIERO ELIMINAR DEL CAMPAIGN PANEL:

- botones invisibles que ya no forman parte del producto;
- código muerto relacionado;
- callbacks obsoletos;
- métodos duplicados;
- rutas alternativas para hacer operaciones que ya tienen una única UI oficial.

PERO:

ANTES de borrar cualquier método:

buscar referencias en todo el repositorio.

NO borrar algo todavía usado por:

- tests;
- otros paneles;
- accesos indirectos;
- CLI;
- atajos;
- ejemplos.

OBJETIVO:

CampaignPanel debe ocuparse de:

    campaña
    escenas
    entradas
    waypoints
    recorridos
    quests
    encuentros
    cámaras/secuencias
    búsqueda global
    navegación

NO de:

    configuración del juego
    deploy
    launcher
    save global
    setup

======================================================================
11. PRIORIDAD MEDIA — PASADA COMPLETA DE TERMINOLOGÍA / I18N
======================================================================

Hacer una búsqueda exhaustiva de textos visibles al usuario.

BUSCAR MEZCLAS COMO:

    Chronicle Flags
    USED BY / Referenciado por
    AFFECTS / Referencia a
    + Waypoint
    + Quest
    Build actualizado
    etc.

OBJETIVO:

En español:

    una interfaz coherentemente española.

En inglés:

    una interfaz coherentemente inglesa.

NO es obligatorio traducir nombres técnicos que tenga sentido conservar como
términos del dominio.

Ejemplo:

"Waypoint" puede ser aceptable SI es una decisión consciente y consistente.

Lo que NO quiero es mezcla accidental:

    "USED BY / Referenciado por"
    "Build actualizado"
    "Chronicle Flags"

REVISAR:

- menús;
- toolbar;
- tabs;
- botones;
- inspector;
- CampaignPanel;
- welcome;
- settings;
- dialogs;
- errores;
- status bar;
- tooltips;
- Showcase;
- Tutorial;
- Help;
- paquetes;
- deploy;
- diagnóstico.

NO tocar:

- IDs internos;
- claves YAML;
- nombres de formatos;
- nombres de API;
- rutas;
- extensiones.

Sólo UI / documentación humana.

AÑADIR / AJUSTAR TESTS de traducción cuando tenga sentido.

======================================================================
12. PRIORIDAD MEDIA — UN SOLO SITIO PRINCIPAL PARA EL IDIOMA
======================================================================

Actualmente existe:

- Configuración -> Idioma;
- y además un submenu Idioma separado movido a Herramientas.

Esto es redundante.

QUIERO:

    Configuración

como lugar oficial para cambiar idioma.

Eliminar o retirar de la UI el selector rápido duplicado.

NO eliminar internamente:

- i18n;
- soporte ES/EN;
- persistencia;
- reinicio requerido.

Sólo evitar dos rutas de configuración para la misma preferencia.

Si existe algún test antiguo basado en language_menu:

    actualizarlo al flujo actual.

======================================================================
13. PRIORIDAD MEDIA — ACLARAR "TUTORIAL DEL PROYECTO"
======================================================================

Actualmente existe una acción llamada aproximadamente:

    Tutorial del proyecto

pero realmente abre el README / guía de la crónica actual.

Eso es ambiguo porque también existen:

- Tutorial rápido;
- Showcase completo;
- Guía del editor.

RENOMBRAR:

    "Guía de esta crónica"

o equivalente natural en inglés.

ESTRUCTURA MENTAL DE AYUDA:

    Tutorial rápido
        aprender lo mínimo

    Showcase completo
        ver todas las posibilidades

    Guía de esta crónica
        README / documentación del proyecto abierto

    Guía del editor
        documentación general de RCM

    Atajos
        atajos

Esto debe quedar clarísimo.

======================================================================
14. PRIORIDAD MEDIA — WELCOME MÁS JERÁRQUICO
======================================================================

La pantalla de bienvenida tiene acciones como:

    Nueva crónica
    Tutorial rápido
    Showcase completo
    Abrir crónica
    Instalar crónica…

Actualmente pueden tener un peso visual demasiado parecido.

QUIERO PRIORIZAR:

PRIMARIO:

    Nueva crónica

SECUNDARIOS MUY VISIBLES:

    Abrir crónica
    Tutorial rápido

SECUNDARIOS:

    Showcase completo

TERCIARIO:

    Instalar crónica…

"Instalar crónica…" NO debe parecer la razón principal de existir de RCM.

RCM ES UN EDITOR.

NO convertir Welcome en una landing page nueva.

NO añadir gráficos, tiles gigantes, ilustraciones ni otra pantalla nueva.

Sólo ajustar jerarquía visual con lo ya existente:

- tamaño;
- orden;
- espaciado;
- agrupación;
- quizá botón secundario.

Conservar proyectos recientes.

======================================================================
15. PRIORIDAD MEDIA — SIMPLIFICAR STATUS PERMANENTE
======================================================================

Actualmente el status puede mostrar algo parecido a:

    Guardado · Válido · Build actualizado · Desplegado

Esto funciona pero empieza a enseñar demasiado el pipeline interno.

QUIERO UNA CAPA HUMANA.

ESTADOS PRINCIPALES PROPUESTOS:

    ✓ Lista para probar

    ● Cambios sin guardar

    ✕ Hay errores

    ● Necesita actualizarse

Opcionalmente:

    ● Preparando prueba…

El detalle técnico:

- válido;
- build current/stale;
- deploy current/stale;
- etc.

puede conservarse internamente y mostrarse:

- tooltip;
- panel de build;
- diagnóstico.

NO eliminar el estado técnico interno.

SÓLO simplificar lo que ve constantemente el usuario.

IMPORTANTE:

NO crear una máquina de estados nueva si la actual ya contiene la información.

Esto debe ser una PRESENTACIÓN más simple de ProjectStatus existente.

======================================================================
16. BAJA/MEDIA — RENOMBRAR CAMPAÑA / MISIONES
======================================================================

Actualmente existe una pestaña:

    Campaña / Misiones

Su función real es más amplia:

- vista global;
- navegación entre escenas;
- quests;
- búsqueda global;
- entidades;
- secuencias;
- recorridos;
- etc.

El árbol izquierdo representa principalmente la escena activa.

Para reducir la sensación de duplicación:

RENOMBRAR la pestaña a algo como:

    Campaña / Vista global

o una denominación todavía más clara.

No cambiar funcionalidad.

No crear otra vista.

Sólo aclarar el propósito.

En inglés equivalente natural:

    Campaign / Overview

======================================================================
17. NO AÑADIR MÁS PESTAÑAS
======================================================================

Las pestañas principales actuales son aproximadamente:

    Espacio 3D
    Historia / Recursos
    Campaña / Misiones
    Recursos propios
    Prueba / Depuración
    Gráfico de historia
    Tutorial / Ayuda

YA SON SUFICIENTES.

RC3 NO PUEDE AÑADIR UNA OCTAVA PESTAÑA PRINCIPAL.

Si una corrección parece requerir otra pestaña:

    buscar otra solución.

======================================================================
18. PROTECCIÓN DE FORMATOS FUTUROS
======================================================================

Añadir una protección simple para evitar que una versión antigua de RCM abra y
potencialmente modifique un proyecto creado con un project_format más reciente.

DEFINIR:

    CURRENT_PROJECT_FORMAT = 9

o equivalente centralizado si no existe ya.

AL CARGAR:

si:

    project_format > CURRENT_PROJECT_FORMAT

ABORTAR APERTURA CON MENSAJE HUMANO:

    "Esta crónica fue creada con una versión más reciente de RCM.
     Actualiza Redemption Chronicle Maker para abrirla con seguridad."

NO intentar:

- ignorar campos;
- convertir hacia atrás;
- salvar parcialmente;
- abrir en modo edición;
- machacar el proyecto.

NO hace falta ahora crear:

    migraciones 9 -> 10
    framework enterprise de migraciones
    version graph

Sólo este gate.

Si el proyecto tiene formato anterior soportado:

    abrir normalmente / convertir por el mecanismo ya existente.

TESTS:

- format 9 -> abre;
- format menor soportado -> abre;
- format 10 -> rechaza;
- mensaje claro;
- archivo intacto.

======================================================================
19. NO CREAR GIT DENTRO DE RCM
======================================================================

RCM YA TIENE:

- .backup;
- backups rotatorios;
- autosave;
- recovery;
- versiones guardadas;
- duplicar crónica;
- protección contra cambios externos.

NO quiero:

- branches;
- commits;
- timeline visual avanzada;
- diff editor;
- merge;
- version graph;
- snapshots manuales ilimitados;
- repositorio interno.

NO FABRICAR GIT DENTRO DE RCM.

======================================================================
20. LIMPIEZA DE CÓDIGO
======================================================================

Aprovechar RC3 para eliminar SOLAMENTE deuda evidente relacionada con los puntos
anteriores.

BUSCAR:

- botones creados y ocultados permanentemente;
- métodos legacy no referenciados;
- callbacks antiguos;
- código de menú ya sustituido;
- ramas de UI imposibles de alcanzar;
- imports muertos producidos por esta limpieza.

PERO:

NO hacer una refactorización global.

NO cambiar arquitectura que funciona.

NO renombrar masivamente módulos.

NO aplicar "clean architecture" por deporte.

NO reescribir window.py entero.

NO migrar framework.

NO cambiar PySide.

NO dividir archivos gigantes si no es necesario para las tareas anteriores.

LA REGLA:

    cada cambio de código debe justificar una mejora visible,
    una corrección real
    o eliminación de deuda directamente relacionada con RC3.

======================================================================
21. FLUJO DE PRODUCTO QUE DEBE QUEDAR
======================================================================

PRIMER ARRANQUE:

    abrir RCM
        ->
    elegir Vampire.exe
        ->
    elegir idioma
        ->
    elegir carpeta de proyectos
        ->
    preparar catálogos
        ->
    Welcome

WELCOME:

    Nueva crónica
    Abrir crónica
    Tutorial rápido
    Showcase completo
    Instalar crónica… (secundario)
    Proyectos recientes

NUEVA CRÓNICA:

    nombre
    escenario inicial
    [Opciones avanzadas]
        ID
        carpeta

DESPUÉS:

    Espacio 3D

    colocar entrada
    colocar NPC
    escribir conversación
    guardar

PARA PROBAR:

    PROBAR EN REDEMPTION / F5

RCM:

    valida
    guarda
    construye
    despliega
    abre Redemption

usuario:

    entra manualmente en su crónica

NO volver a exponer:

    Deploy
    Run
    Build pipeline
    game shortcut
    raw paths

en el flujo normal.

Herramientas avanzadas pueden existir donde corresponde.

======================================================================
22. POLÍTICA DE PRUEBAS DE RUNTIME
======================================================================

NO AUTOMATIZAR REDemption.

NO usar Computer Use para:

- navegar menús;
- entrar en Multiplayer;
- cargar partida;
- simular gameplay;
- declarar que algo funciona in-game.

RCM puede:

- generar;
- validar;
- compilar;
- desplegar;
- lanzar el ejecutable.

LA VALIDACIÓN REAL DE GAMEPLAY LA HACE EL USUARIO MANUALMENTE.

ESTADOS CORRECTOS:

    OFFLINE VERIFIED
    GENERATED
    COMPILED
    DEPLOYED
    MANUAL RUNTIME TEST REQUIRED
    RUNTIME VERIFIED
    RUNTIME FAILED

NUNCA marcar:

    RUNTIME VERIFIED

sin reporte explícito del usuario.

======================================================================
23. TESTS OBLIGATORIOS DE RC3
======================================================================

Después de los cambios:

EJECUTAR TODOS LOS TESTS EXISTENTES.

CERO:

- failures;
- errors;
- skips inesperados.

AÑADIR TESTS ESPECÍFICOS PARA:

1. dock inferior oculto cuando no hace falta;
2. dock visible con errores;
3. dock visible durante build;
4. Referencias abre dock;
5. Crear campaña sólo visible para legacy;
6. format futuro rechazado;
7. importación usa flujo seguro de apertura;
8. lock correcto tras importar;
9. recent projects correcto tras importar;
10. cache asociado a instalación;
11. cambio de instalación invalida catálogos regenerables;
12. misma instalación no reconstruye innecesariamente;
13. idioma accesible desde Configuración;
14. no existe selector duplicado visible;
15. Welcome conserva acciones esenciales;
16. status simplificado representa correctamente los estados;
17. Help contiene nombres finales coherentes;
18. CampaignPanel sin controles legacy muertos.

NO escribir tests ficticios que sólo comprueben strings sin comprobar comportamiento
cuando pueda probarse mejor.

======================================================================
24. REVISIÓN MANUAL DE UI OFFSCREEN / GUI
======================================================================

Además de unit tests:

hacer una comprobación de GUI.

VERIFICAR:

WELCOME:

- jerarquía correcta;
- Nueva crónica visible;
- Abrir visible;
- Tutorial visible;
- Showcase visible;
- Instalar secundario;
- recientes intactos.

PROYECTO ABIERTO:

- no aparece "Crear campaña" en proyecto actual;
- dock inferior no ocupa pantalla porque sí;
- tabs sin cambios extraños;
- Campaña / Vista global coherente;
- propiedades siguen funcionando;
- árbol sigue funcionando;
- 3D sigue funcionando.

AYUDA:

- Tutorial rápido;
- Showcase completo;
- Guía de esta crónica;
- Guía del editor;
- Atajos.

CONFIGURACIÓN:

- idioma;
- workspace;
- Redemption;
- autosave;
- safe mode;
- hints;
- sin duplicar opciones.

SHOWCASE:

- guía humana;
- ruta principal clara;
- laboratorio opcional claro;
- índice técnico relegado al final.

======================================================================
25. NO ROMPER COMPATIBILIDAD
======================================================================

RC3 debe seguir pudiendo abrir:

- proyectos actuales;
- ejemplos actuales;
- Tutorial;
- Showcase;
- proyectos legacy soportados.

NO modificar automáticamente proyectos guardados sólo por abrirlos.

NO reescribir YAML innecesariamente.

NO borrar campos desconocidos de proyectos actuales si ya eran válidos.

NO cambiar IDs del Showcase salvo absoluta necesidad.

NO cambiar referencias porque "quedan más bonitas".

======================================================================
26. NO TOCAR LOS ORIGINALES DE REDEMPTION
======================================================================

Regla permanente:

los archivos originales del juego son READ ONLY.

RCM puede:

- leer;
- indexar;
- extraer a research;
- generar sus propios archivos;
- desplegar dentro de sus zonas administradas.

NO modificar:

- Resource.nob;
- Codex.nob;
- Chronicles originales;
- executables;
- assets originales;
- NOT originales.

======================================================================
27. SHOWCASE Y TUTORIAL NO SON LO MISMO
======================================================================

Conservar diferenciación:

TUTORIAL RÁPIDO:

    mínimo camino feliz.

Debe enseñar algo parecido a:

    crear/abrir
    entrar en 3D
    colocar actor
    conversación
    probar

SHOWCASE COMPLETO:

    referencia avanzada y demostración de capacidades.

NO convertir el tutorial en Showcase.

NO convertir Showcase en tutorial de 40 pasos.

======================================================================
28. CRITERIO DE CALIDAD PRINCIPAL
======================================================================

NO medir éxito por:

    cantidad de botones
    cantidad de APIs
    cantidad de paneles
    cantidad de features

MEDIRLO POR:

    cuánto tarda alguien en pasar de
    "quiero hacer esta escena"
    a
    "estoy jugándola en Redemption".

Cada cosa que distraiga de eso debe justificar muy bien su existencia.

======================================================================
29. ORDEN DE IMPLEMENTACIÓN
======================================================================

QUIERO ESTA SECUENCIA:

PASO 1
Auditar código actual y tests relacionados.

PASO 2
Crear checkpoint/commit previo si procede.

PASO 3
Arreglar project_format futuro.

PASO 4
Arreglar identidad de instalación/cache.

PASO 5
Unificar importación -> apertura segura.

PASO 6
Limpiar controles legacy CampaignPanel.

PASO 7
Arreglar dock inferior.

PASO 8
Limpiar duplicación de idioma / Help / nombres.

PASO 9
Simplificar status.

PASO 10
Ajustar Welcome.

PASO 11
Renombrar Campaña / Vista global.

PASO 12
Reescribir guía del Showcase.

PASO 13
Revisar nombres pedagógicos visibles o no in-game.

PASO 14
Pasada i18n global.

PASO 15
Tests.

PASO 16
GUI probe.

PASO 17
Auditoría final de deuda introducida.

NO MEZCLAR TODO EN UN REWRITE GIGANTE.

======================================================================
30. AUDITORÍA FINAL OBLIGATORIA
======================================================================

ANTES DE CONSIDERAR RC3 TERMINADA:

buscar en el repositorio:

"Deploy"
"Ejecutar"
"Crear campaña"
"Chronicle Flags"
"USED BY"
"AFFECTS"
"Build actualizado"
"Tutorial del proyecto"
"language_menu"

y revisar CADA resultado.

No significa borrarlos todos.

Significa confirmar si:

- es UI actual;
- es legacy;
- es traducción;
- es test;
- es código interno;
- debe quedarse;
- debe cambiar.

También buscar:

    hide()
    setVisible(False)

en CampaignPanel y shell principal para detectar widgets legacy creados para
ocultarlos permanentemente.

Buscar métodos no referenciados relacionados con:

    deploy
    run_game
    game_shortcut
    game_settings

y eliminar sólo los verdaderamente obsoletos.

======================================================================
31. LO QUE NO QUIERO QUE HAGAS
======================================================================

NO:

"Como mejora adicional he añadido..."

NO.

NO:

"He creado un nuevo Dashboard de Proyecto..."

NO.

NO:

"He añadido soporte de temas oscuro/claro..."

NO.

NO:

"He creado un sistema de migraciones extensible..."

NO.

NO:

"He añadido historial Git-like..."

NO.

NO:

"He añadido una nueva pestaña Startup..."

NO.

NO:

"He aprovechado para refactorizar toda la UI..."

NO.

NO:

"He convertido el Showcase a un nuevo formato..."

NO.

NO:

"He añadido auto-play de Redemption..."

NO.

NO:

"He añadido edición de geometría..."

ABSOLUTAMENTE NO.

======================================================================
32. RESULTADO FINAL ESPERADO
======================================================================

Quiero poder abrir RCM después de RC3 y pensar:

    "Hostia, ya está."

No:

    "Hostia, ahora tiene otras 17 cosas que revisar."

La RC3 debe dejar:

- menos botones;
- menos duplicidades;
- menos ruido;
- menos código legacy;
- menos tecnicismos visibles;
- más superficie útil;
- mejor Showcase;
- flujo más evidente;
- más seguridad al cambiar instalación;
- mejor coherencia al importar;
- protección frente a formatos futuros.

Y debe conservar TODO el poder actual.

======================================================================
33. INFORME FINAL QUE QUIERO
======================================================================

Al terminar, dame un informe MUY CONCRETO con:

1. CAMBIOS REALIZADOS

Agrupados por los puntos de RC3.

2. COSAS ELIMINADAS

Especialmente:
- botones legacy;
- métodos muertos;
- duplicados de UI.

3. COSAS QUE DELIBERADAMENTE NO TOCASTE

Para demostrar que no hubo feature creep.

4. TESTS

Número total:
    PASS
    FAIL
    SKIP

5. GUI PROBE

Qué flujos se comprobaron realmente.

6. SHOWCASE

Cómo quedó reorganizada su guía.

7. CACHE / INSTALACIÓN

Cómo se detecta ahora un cambio de instalación.

8. COMPATIBILIDAD

Qué formatos/proyectos continúan soportados.

9. RUNTIME

Debe decir explícitamente:

    MANUAL RUNTIME TEST REQUIRED

si yo todavía no he probado esta RC3 dentro de Redemption.

NO declarar runtime PASS por tests offline.

10. VEREDICTO

Uno de:

    RC3 APROBADA PARA PRUEBA MANUAL
    RC3 NECESITA CORRECCIONES

NO inventar una "Phase 10".

======================================================================
34. DEFINICIÓN DE TERMINADO
======================================================================

RC3 ESTÁ TERMINADA CUANDO:

[ ] no se añadió ninguna feature grande;
[ ] dock inferior deja de molestar;
[ ] Crear campaña es sólo legacy;
[ ] Showcase tiene guía humana;
[ ] cambiar instalación invalida cache correctamente;
[ ] importar usa el flujo seguro común;
[ ] CampaignPanel perdió controles legacy;
[ ] idioma no tiene dos selectores;
[ ] ayuda tiene nombres claros;
[ ] Welcome tiene jerarquía;
[ ] status es humano;
[ ] Campaña / Vista global explica mejor su propósito;
[ ] format futuro se rechaza de forma segura;
[ ] ES/EN están coherentes;
[ ] tests pasan;
[ ] GUI probe pasa;
[ ] originales de Redemption siguen intactos;
[ ] no se automatizó gameplay;
[ ] no se añadió otra pestaña;
[ ] no se añadió otro subsistema;
[ ] no se creó Phase 10;
[ ] el programa se siente MÁS PEQUEÑO aunque internamente siga siendo igual de potente.

======================================================================
35. PRINCIPIO FINAL
======================================================================

SI TIENES QUE ELEGIR ENTRE:

A)
añadir una capacidad nueva

o

B)
hacer más claro, simple y fiable lo que ya existe

ELIGE B.

SI TIENES QUE ELEGIR ENTRE:

A)
mostrar al usuario cómo funciona RCM internamente

o

B)
mostrarle el concepto de autoría que necesita

ELIGE B.

SI TIENES QUE ELEGIR ENTRE:

A)
hacer una arquitectura teóricamente más elegante

o

B)
no arriesgar un producto que ya funciona

ELIGE B.

RC3 NO ES UNA FASE DE EXPANSIÓN.

RC3 ES:

    QUITAR ANDAMIOS.
    LIMPIAR LA OBRA.
    CERRAR LA PUERTA.
    Y JUGAR.
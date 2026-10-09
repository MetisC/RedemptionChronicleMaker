# Embrace original y RCM — revisión de Fase 7

Se ha leído el **manual original de Embrace** del SDK de Nihilistic y las especificaciones NIL, NSC, NSL, NSS, NMF y documentación de CodexCamera, CodexSequence y CodexSound. Se recuperaron de copias archivadas de e-mods.net; HTML original, respuesta HTTP, texto legible y SHA-256 permanecen en `research/phase7/embrace/`. No se ha ejecutado Embrace ni instalado el SDK. El análisis de su interfaz es documental, no una sesión interactiva ni un análisis del binario Embrace.exe.

Manual local: [Embrace](../research/phase7/embrace/embrace_manual.htm.txt), [NIL](../research/phase7/embrace/NIL.htm.txt), [NSC](../research/phase7/embrace/NSC.htm.txt), [NSL](../research/phase7/embrace/NSL.htm.txt), [NSS](../research/phase7/embrace/NSS.htm.txt). Procedencia del manual: [copia archivada del original](https://web.archive.org/web/20210110082032id_/https://www.e-mods.net/nodsdk/Docs/embrace.htm). El mirror del ZIP en Patches Scrolls devolvió HTML; ModDB/GameFront rechazaron las descargas y el dominio e-mods actual no resolvió. Se obtuvo documentación primaria mediante Internet Archive; no se obtuvo el ejecutable del editor. No atribuir a los tutoriales comunitarios el carácter de especificación del motor.

Varias especificaciones llevan la cabecera **SDK 1.0**. Se conserva su procedencia, sin afirmar que se obtuvo el paquete 1.1. Las firmas y constantes utilizadas se contrastan con las clases de la instalación actual, y los formatos binarios con sus bytes; la antigüedad del documento no basta para asumir una estructura compatible.

## Qué significa scene

El manual describe una geometría NIL con una escena estática y posibles escenas adicionales NSD. La estática se identifica por el mismo nombre base del NIL y contiene decoraciones u otros objetos. Las adicionales agrupan entidades por capas. Cada escena tiene sus propios ajustes de entorno; los ajustes de la estática no se heredan automáticamente por todas las demás. Las regiones de visibilidad y superficies marcadas como cielo pertenecen al escenario geométrico.

En RCM, una escena de campaña contiene un level base, nuestras entidades y lógica. Varias escenas pueden referenciar la misma geometría. Una secuencia de cámara es una operación dentro de una escena; no es otro level. Seleccionar un perfil original copia exclusivamente sus 176 bytes de entorno, nunca sus NPC, scripts o bloques variables. El motor sigue pudiendo cargar objetos de la **escena estática original** junto con el NIL: no se ofrece todavía una operación para retirar o sustituir todos esos objetos base. La afirmación de que no importamos entidades se refiere a nuestro NSD adicional, no a una eliminación automática del contenido estático del juego.

## Comparación funcional

Estas funciones de Embrace están documentadas en sus secciones Thing & Templates, Scene Editor, Layers & View Options, Codex Linker, menú contextual y Export Output. El estado de RCM se ha contrastado con código y tests locales. “Disponible” no significa aceptado en una partida nativa de la versión actual.

| Función documentada | RCM actual | Falta o límite |
|---|---|---|
| Vistas 2D, altura y cámara 3D | Viewport texturizado, selección, transforms y referencias | Ensayar colocación/collision en motor; no inferirla del viewport |
| Origin y orientación por objeto | Coordenadas propias y aparición cerca del jugador | Sectores válidos y colisión requieren prueba nativa |
| Plantillas NOT e overrides | Catálogo, reader lossless, writer parcial, herencia y recursos propios | NOT/AI propios siguen sin aceptación nativa completa |
| Scene Editor, varias escenas por level | Campañas y varias escenas sobre la misma geometría | No reproduce el formato de edición MAP ni sus capas internas |
| Music, ambient, volumen y EAX por escena | Audio mediante acciones y preservación del entorno original | Volúmenes/EAX nativos no tienen autoría completa en GUI |
| Render: fog, color, distancias y ZClip | Nuevo selector de perfiles originales; bytes conservados | No hay sliders individuales ni preview de niebla fiel al motor |
| Sky: modelo y animación | Preservación por perfil y override YAML validado | La superficie Sky debe existir en la geometría; no crear portales de cielo |
| Layers 0–31 y static | Colecciones lógicas de RCM y escenas propias | Sin editor de grupos reutilizables o reemplazo de static base |
| Codex Linker con parámetros tipados/referencias | Modelo de eventos, referencias y Java propio | No importa ni edita genéricamente todos los parámetros CODEXPVALUE originales |
| Playerstarts y convstarts numerados | Entrada original 0 y NPC near_player | Entradas múltiples y conversación en puntos personalizados pendientes |
| Path corners e interest spots | No hay editor de waypoints | Decodificar/escribir bloques de paths y comprobar AI en motor |
| Lights y lightboxes | El entorno y la iluminación original se conservan | Luces dinámicas propias pendientes; lightmaps requieren geometría/export y quedan fuera |
| Sound objects/soundboxes, distancia de audición | Música/ambient por acciones | Sonido espacial con volumen/falloff/regiones propias pendiente |
| Regions y trigger volumes | Triggers propios de caja/esfera por muestreo Java | No equivalen a todos los tipos de región nativos; intervalos/bordes deben ensayarse |
| Quick Doors, template brushes y script Door/PivotDoor | No implementado en el editor | Distinguir controlar una puerta existente de generar su geometría/malla/path |
| Sectors, superficies, CSG, brushes, lightmaps | Sólo lectura | Fuera del alcance de geometría inmutable |
| Export NIL y NSD | NSD propio; referencia NIL original | No generar NIL ni depender del exportador antiguo |
| NSS del panel Storyteller | Se conserva catálogo de recursos, no se genera ese panel | NSS requiere el handler `advance` correspondiente; no confundirlo con archivos NSD |

## Corrección del catálogo

La especificación NSS define dos números de escena/subescena y una **clave NLS de descripción**. No establece que el primer número sea el índice de una location NSC ni que la descripción sea un nombre NSD. Se retiró esa suposición del scanner. Los perfiles se asocian por las referencias iniciales NSC y por la pareja estática NIL/NSD de nombre común. El orden mantiene primero la escena inicial histórica para conservar los builds existentes.

Los scripts originales contienen otras asociaciones mediante `CodexSequence.ChangeScene(location, scene)`: se extrajeron 45 llamadas con argumentos literales consecutivos en `research/phase7/codex_scene_links.json`, con línea de bytecode. Es una lista de evidencia para ampliar la investigación; no es un catálogo completo ni se importa automáticamente como presets. No deducir asociaciones sólo del prefijo del nombre.

## Prioridades de estabilización

El contrato de cámara distingue dos familias: `SetShot` utiliza `CAM_SHOT_*`, `CAM_ANGLE_*` y `CAM_DIST_*`; `ShotType`/`ShotAngle` utilizan `CAMERA_SHOT_*` y `CAMERA_ANGLE_*`. No se deben mezclar sus números de enum. RCM usa la segunda familia en sus secuencias actuales. Esta revisión conserva el comportamiento de diálogo existente; el manual de cutscenes aporta más posibilidades, pero no se añadieron llamadas nuevas sin ensayo nativo del problema de cámara.

1. Repetir aceptación nativa de diálogo/cursor/cámara y save/load en la demo de tres escenas. B1/B2 continúan abiertos.
2. Ensayar NOT/AI propios, inventario, reentrada y red. Mantener resultados por caso.
3. Decodificar con evidencia los campos individuales de entorno; probar audio/niebla/recorte antes de habilitar nuevos controles.
4. Estudiar entradas y paths nativos; añadir lectores/writers conservadores antes de exponer autoría.
5. Controlar puertas/sonidos/luces como contenido dinámico cuando la API lo permita. Mantener separado lo que necesita geometría.

Esta fase no promete paridad completa con Embrace. Revela y documenta sus huecos, corrige un error de asociación y hace explícita una capacidad útil ya respaldada por los archivos originales.

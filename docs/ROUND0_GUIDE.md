# Ronda 0 — editor y dos ejemplos

Versión 0.9.6. Abrir muestra únicamente Tutorial y Mini crónica. Espacio 3D → **Inicio** selecciona la llegada del jugador; Ayuda → **Tutorial del proyecto** abre la guía. La cámara automática entra en modo de conversación sin imponer un preset; el selector permite primeros planos y perfiles documentados por el SDK. Las cutscenes propias usan `BeginCutscene`/`EndCutscene`, bloquean la entrada de la escena mientras duran y toleran que el primer waypoint coincida con la posición inicial. Al cambiar al layout de combate, la guía confirma el cambio y explica la rata opcional. Consulta [TUTORIAL_CUTSCENE_LAYOUT_FIX.md](TUTORIAL_CUTSCENE_LAYOUT_FIX.md). Empieza una partida nueva; las partidas anteriores conservan entradas del journal y otra distribución de flags.

Consulta la pestaña **Tutorial / Ayuda** de cada proyecto: hay instrucciones y enlaces a sus elementos, no sólo un resultado generado. Tutorial: un level, tres layouts. Mini crónica: dos levels, tres escenas con historia, llave, quests, flags y regreso. Ambos usan una rata básica y combate elegido expresamente.

## Navegación adaptada de UE4.27

| Acceso | Acción |
|---|---|
| Derecho + arrastrar | Mirar |
| Izquierdo + arrastrar, fuera del gizmo | Avanzar/retroceder y girar |
| Izquierdo + derecho + arrastrar | Subir/bajar |
| Alt + izquierdo | Orbitar selección o punto delante de cámara |
| Alt + derecho | Acercar/alejar |
| Alt + central | Desplazar lateral/vertical |
| Derecho + WASD, flechas, Q/E, Page Up/Down | Vuelo |
| Derecho + rueda | Velocidad de vuelo |
| Derecho + Z/C | Campo de visión temporal |
| F | Enfocar selección |
| Clic derecho sin arrastre | Acciones frecuentes |

Referencia primaria: [Viewport Controls — UE4.27, Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/viewport-controls?application_version=4.27). Adaptación de navegación de perspectiva; los gizmos siguen usando 1/2/3. Central sin Alt también desplaza y rueda sin derecho acerca/aleja. Los atajos de vuelo también tienen equivalentes en el teclado numérico. Los controles ortográficos y las transformaciones de UE4 quedan fuera de esta adaptación.

## Cambios de interfaz

Icono propio de libro y ankh, independiente de Vampire.exe, aplicado a ventana, aplicación y distribución Windows. Tooltips completos en árbol, tablas, catálogo y lista de recursos propios. Catálogo con búsqueda, familia/recurso, procedencia y disponibilidad; sin botón de selección duplicado. Inventario con incorporación directa del catálogo, copias independientes y selección de objetos existentes que no tienen otro propietario; Cancelar no cambia el proyecto y Aplicar se puede deshacer.

Controles más compactos. Campaña tiene separador vertical ajustable y un mínimo útil para el formulario; la lista de waypoints deja visibles varias filas. `+ Escena` explica y ofrece layout vacío en el mismo escenario, copia del actual u otro level. La copia mantiene destinos de viaje explícitos; revísalos si quieres que vuelvan a la copia.

## Cámaras y cutscenes

En conversación: **Automática del juego** usa SetupCutscene para bloquear los controles y elegir el encuadre predeterminado del motor; no impone SetShot. Los presets aplican ambos mediante la API real. Las conversaciones antiguas sin la propiedad camera conservan el comportamiento previo. En secuencias formato 9, `steps` encadena planos por tiempo, actor/preset/transición; `move_path` usa navegación del motor. El final, diálogo nuevo, viaje o restore libera cámara y detiene el movimiento iniciado por la cutscene. No se reanuda una cutscene guardada a medias.

`camera_path` reproduce un NCP original único con PlayPath; no crea o edita sus puntos. Debe corresponder al escenario. Sólo se incluye EASTOttoVan en el tutorial como opción experimental separada. Writer NCP, cámara desde viewport y puertas físicas completas siguen pendientes. No se declara paridad con Embrace.

## Evidencia y alcance

Rat: registro original de Resource.nob/misc/Templates/Global.not, modelo Rat.nod, AI enemyGhoulRat.nai, instancia en SIM1_5_1 y otras escenas. Evidencia local en research/round0/rat_original.json; usar una rata reduce dificultad respecto a brujahFled_MD. No se promete una dificultad nativa medida en este build.

Se separan validación, suelo contra malla, compilación Java45.3, pruebas Qt/doubles, render GL y observación nativa. Las pruebas dentro del juego siguen aplazadas por el usuario. La geometría y archivos originales fuera de RCM permanecen sólo lectura. No se ejecuta Embrace ni otra herramienta original de autoría.

Los estados exactos de pruebas y despliegue se persisten en research/round0. Para reconstruir ejemplos: tools/round0_examples.py. El archivado histórico se hace una vez; su script conserva ZIPs verificados antes de mover carpetas.

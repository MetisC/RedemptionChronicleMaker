# Ronda 0 — editor y dos ejemplos

Actualización 0.9.12: acceso directo **Redemption Chronicle Maker.lnk** en la raíz. Los objetos ofrecen **Añadir nota al usar** y **Añadir conversación al usar**. En Eventos, **Historia / Mostrar nota** edita título y párrafos; **Cierran una nota** permite continuar después. El tutorial muestra el prólogo al iniciar, una carta en el laboratorio y una nota al pulsar el barril del paso 5. Los gestos de Christof vuelven al reposo usando la duración que devuelve el motor. Ver [NOTES_AND_MOTION_FIX.md](NOTES_AND_MOTION_FIX.md).

Versión 0.9.11. Abrir muestra únicamente Tutorial y Mini crónica. Espacio 3D → **Inicio** selecciona la llegada del jugador; Ayuda → **Tutorial del proyecto** abre la guía. La cámara predeterminada de conversación es **sobre el hombro**; el selector permite primeros planos y perfiles documentados por el SDK. Las cutscenes propias usan `BeginCutscene`/`EndCutscene` y bloquean la entrada de la escena mientras duran. La revisión añade animaciones por nodo, plano aéreo inicial y recuperación de la posición guardada. Consulta [ANIMATION_RESTORE_FIX.md](ANIMATION_RESTORE_FIX.md). Empieza una partida nueva; no hay migración de los saves anteriores.

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

En conversación formato 9: **Sobre hombro cercano hacia quien habla** es la opción predeterminada, también cuando falta `camera`. **Automática del motor (experimental)** conserva el encuadre nativo como elección explícita. En secuencias formato 9, `steps` encadena planos por tiempo, actor/preset/ángulo/transición; `move_path` usa navegación del motor. El final, viaje o restore libera cámara y detiene el movimiento iniciado por la cutscene. No se reanuda una cutscene guardada a medias. El tutorial deja avanzar los trece encuadres de conversación uno a uno.

Selecciona un nodo o una línea de conversación → **Animación al hablar**. Las opciones provienen del NMS real del modelo y de las constantes Codex. Deja Automática para conservar la actuación normal. El laboratorio contiene ejemplos identificables; su apariencia sigue pendiente de prueba visual.

`camera_path` reproduce un NCP original único con PlayPath; no crea o edita sus puntos. Debe corresponder al escenario. Sólo se incluye EASTOttoVan en el tutorial como opción experimental separada. Writer NCP, cámara desde viewport y puertas físicas completas siguen pendientes. No se declara paridad con Embrace.

## Evidencia y alcance

Rat: registro original de Resource.nob/misc/Templates/Global.not, modelo Rat.nod, AI enemyGhoulRat.nai, instancia en SIM1_5_1 y otras escenas. Evidencia local en research/round0/rat_original.json; usar una rata reduce dificultad respecto a brujahFled_MD. No se promete una dificultad nativa medida en este build.

Se separan validación, suelo contra malla, compilación Java45.3, pruebas Qt/doubles, render GL y observación nativa. Las pruebas dentro del juego siguen aplazadas por el usuario. La geometría y archivos originales fuera de RCM permanecen sólo lectura. No se ejecuta Embrace ni otra herramienta original de autoría.

Los estados exactos de pruebas y despliegue se persisten en research/round0. Para reconstruir ejemplos: tools/round0_examples.py. El archivado histórico se hace una vez; su script conserva ZIPs verificados antes de mover carpetas.

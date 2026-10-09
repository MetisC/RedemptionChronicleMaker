# Estabilidad y usabilidad — 0.9.11

Seguimiento 0.9.12: se amplía la cobertura con los casos reales de final de gesto y notas nativas, sin rediseñar el circuito de cámaras o la cutscene aceptada. Los objetos tienen accesos directos para notas/conversaciones; no se exige preparar manualmente un evento desde cero. Detalles y resultados actuales en NOTES_AND_MOTION_FIX.md y research/round0/notes_motion/final_quality/. Las cifras siguientes corresponden a la auditoría previa.

Objetivo: que un creador complete una tarea con pocos pasos, sepa qué ha seleccionado, pueda deshacer y entienda qué ocurrió. Se conserva el comportamiento aceptado; no se hace una reorganización general del editor en esta revisión.

## Alcance y evidencia

Revisión del código de ventanas, formularios, catálogo, inventario, tutorial y graph; pruebas Qt de tareas reales y render de nuestros formularios con Segoe UI en Fusion/offscreen. Evidencia: `research/round0/stability_usability/form_probe.json`, capturas PNG y layout_contract.json. Tamaños lógicos 1100×720 y 1430×900; se repite con texto de 15 puntos. Esto no es una prueba física de DPI, ratón, accesibilidad con lector de pantalla ni viewport GL.

Las pestañas mantienen su posición en todas las secciones comprobadas. El formulario de campaña dispone de al menos 190 px en la ventana mínima. La lista de recorrido puede requerir desplazamiento con texto grande; se conserva el scroll y el separador ajustable. El contraste medido del texto de tarjetas contra sus fondos es al menos 13.30:1. No se detectó truncado de los botones de campaña en el render con la fuente cargada.

## Tareas y contratos existentes

| Tarea | Protección actual y pruebas |
|---|---|
| Elegir el inicio | Botón Inicio selecciona la entrada incluso desde otro layout; test_round0. |
| Crear y borrar actor/trigger | Supr y botones; se retira el spawn propio, se protegen dependencias externas y se permite deshacer; test_editor_fixes y test_editor. |
| Añadir inventario | Catálogo con búsqueda/familia/procedencia, copias independientes, Cancelar sin cambios y Aplicar con undo; test_round0. |
| Crear otro layout | + Escena ofrece vacío/copia sobre el mismo level u otro mapa; test_round0. |
| Encontrar elementos largos | Tooltips de árbol y catálogo, búsqueda global y enlaces de guía; test_round0 y test_phase9_gui. |
| Cambiar diálogo/cámara | Preset de hombro inicial, respuestas/flags, final diferido y abortos; test_round0, test_dialogue_lifecycle y test_guided_tutorial. |
| Cambiar una actuación | Selector por nodo/línea, sólo slots reales, herencia, undo y reabrir; test_stability_gui y test_stability_revision. |
| Cambiar ruta o película | Orden de puntos, references/rename/delete protegido, planos y ángulos; test_phase9_gui y test_stability_gui. |
| Construir/desplegar | Build transaccional, huella de fuente, rechazo de build antiguo, backups y protección de originales/enlaces; tests de safety, phase6, phase9 y round0. |

## Hallazgos de usabilidad pendientes

| Prioridad | Problema observado | Simplificación recomendada |
|---|---|---|
| P1 | Campaña reúne ocho acciones de creación, edición y ejecución; no distingue tareas frecuentes de avanzadas. | En una próxima revisión, mostrar primero Escena/Entrada/Recorrido y agrupar el resto en Añadir. Mantener atajos y nombres conocidos. |
| P1 | Build, Deploy, Integridad, journal/quest, waypoint y layout mezclan idiomas y conceptos. | Adoptar vocabulario consistente y una ayuda breve junto a cada operación: guardar proyecto, preparar para el juego, actualizar prueba. No cambiar semántica de botones sin recorrido de regresión. |
| P1 | La ficha de película combina plano simple, preset, timeline, travelling y movimiento. | Elegir primero «Plano / Secuencia de planos / Travelling original» y mostrar sólo los ajustes pertinentes. Conservar datos ocultos o advertir antes de descartarlos. |
| P1 | Algunas fichas de Propiedades adquieren scroll horizontal por controles/listas largos; el texto explicativo puede quedar fuera de la zona inmediata. | Hacer el ancho adaptable y usar tooltips completos; probar 1100×720 y DPI físico de Windows antes de aceptar el cambio. |
| P1 | Una ruta o timeline extensa requiere bastante scroll, especialmente con texto grande. | Agrupar Añadir/Subir/Bajar/Quitar en una barra pequeña junto a la lista; encabezados plegables para planos. No reducir más el texto ni las áreas de edición. |
| P2 | El gráfico muestra nombres técnicos ENTRY/GOTO/RETURN y puede ser muy extenso. | Etiquetas «Inicio / Ir a / Terminar», ajuste de vista explícito y ayuda para seleccionar. Conservar los identificadores técnicos en detalle. |
| P2 | El tutorial requiere buscar un nodo por nombre para ajustar una animación. | Futuro enlace directo al nodo desde la guía, además del enlace actual a la conversación. |

No son funcionalidades implementadas ni una nueva fase iniciada. Las propuestas deben probarse una a una, conservando flujo, undo, referencias y fuentes originales.

## Cobertura y límites de estabilidad

Se añade cobertura dirigida a los fallos reales, no tests que sólo repitan la implementación. Incluye motor rechazando spawn/inventario/posición, timers duplicados, callback síncrono, abortos, guardado a mitad de película, carga/reentrada, premios idempotentes, dependencias, corruptos, seguridad de paquetes y edición gráfica. **257 pruebas pasan**, 21 más que la revisión previa, junto a Ruff y las comprobaciones de tipos configuradas. Resultados finales en `research/round0/stability_usability/final_quality/`. El informe global no equivale a cobertura del motor nativo: los escenarios Java usan dobles.

La medición informa 5611/7566 líneas y 2324/3684 ramas ejecutadas, 70.53% combinado. Es orientativa: coverage avisó de ausencia del tracer C y de un cambio de función de tracing durante la suite; no se usa ese porcentaje como criterio único de aceptación. `runtime9.py` tiene 99.4% combinado **del generador Python**, no del Java ejecutado en Redemption. Motion catalogue 84.6%, cinematics 90.7%, formats 92.0% y backend 93.6%; los escenarios Java adicionales verifican sus resultados.

No se considera suficiente la cobertura de toda la aplicación sólo por ese resultado: viewport 28%, assets 24%, gráfico 34% y recursos propios 31% necesitan más recorridos y pruebas de render/input. Los diálogos de instalación y el arranque en máquina limpia también tienen ramas no ejercitadas. Se priorizó proteger los fallos observados sin inventar una cobertura del 100% ni reimplementar módulos sanos.

Siguen abiertos: save/load visual y colisión de cámara de esta revisión, red real, writer NOT con cobertura nativa de todos sus campos, puertas originales con frames/pivots en varias geometrías, writer NCP, arranque portable en una máquina limpia y DPI/accesibilidad físicos. La aceptación del usuario de revisiones previas se conserva como evidencia histórica; no se extrapola a estas pruebas.

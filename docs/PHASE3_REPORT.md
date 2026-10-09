# Fase 3 — informe de entrega

Fecha: 8 de octubre de 2026. Versión 0.3.0. Autoría espacial implementada, aceptación en ventana real y build completados. Las comprobaciones locales se distinguen de la observación dentro del juego; no se ha iniciado Fase 4.

## IMPLEMENTADO

Viewport Qt OpenGL sobre el editor PySide6 existente. Level texturizado e inmutable, modelos originales, cámara libre, picking, colocación por clic, transformaciones, snap, volúmenes de trigger, referencias narrativas, outliner con visibilidad, Properties sincronizado y Deshacer/Rehacer. Un solo documento YAML alimenta GUI, viewport, CLI y build.

La crónica `chronicles/phase3_demo/project.yaml` fue creada mediante controles Qt, sin escribir manualmente sus posiciones/eventos. Incluye Victoria, otro personaje, barrel1, conversaciones/flags anteriores y Entrada del pacto. Su evento condicionado por `alliance` activa `entered` y crea el segundo actor. Distribución: `build/phase3_demo/phase3_demo_distribution.zip`.

## PARSING DE LEVELS

Catálogo automático del backend selecciona el NIL desde Levels.nob. Lector propio NIL v27 basado en la rutina nativa y contrastes de archivos. **112 de 112 NIL** pasan el análisis de sus bloques de sectores/superficies. No son 112 mapas revisados visualmente ni una interpretación completa del NIL.

Evidencia: `research/viewport/native_nil_reader.txt`, `nil_scan.json` y `src/rcm/spatial/geometry.py`. La cola global queda fuera del parser. No hay escritor ni cambios en NIL.

## GEOMETRÍA

EastLondon: 131 sectores, 45.927 triángulos, 109 materiales. Bounds [-5120,-4608,-80] a [4288,5824,1952]. XYZ conserva unidades originales y Z vertical. Posiciones, UV y grupos validados; triangulación en abanico presupone convexidad original.

Lectura NOD v7 completa de **1.476/1.476 modelos**, con índices locales por material. Victoria y barrel1 se muestran con mallas originales en pose estática. No se aplican animaciones ni se permite editar mallas.

## TEXTURAS

Resolución NAM/TGA directa desde NOB, UV difuso, mipmaps y texturas repetidas. Materiales simples de modelos resuelven TGA y NAM por basename inequívoco. EastLondon carga **109/109 materiales sin fallback**, incluidos agua mediante primera pasada estática; Victoria tiene cuatro materiales resueltos.

Alpha cutout y blending aproximado por grupo de material, sin equivalencia con el renderer nativo. Recurso ausente/unsupported produce patrón magenta o marcador y warning. Registro en `cache/levels/EastLondon.json`.

## NAVEGACIÓN

Botón derecho para mirar, WASD para mover, Q/E vertical, Shift rápido, rueda velocidad, F enfocar, Alt+botón izquierdo orbitar. Modo Suelo usa altura sobre intersección vertical; Volar permite recorrer cualquier zona. Recaptura de ratón evita detener el giro en bordes de pantalla. No hay colisión de cámara contra paredes.

## PICKING

Rayo desde cámara; geometría usa intersección triangular. Actores/props emplean bounds orientados por yaw con oclusión del mapa; cajas también, esferas intersección exacta. Selección sincroniza Outliner y Properties; dorado señala selección, verde relacionados. Helpers se dibujan como overlays; modelos usan profundidad.

## GIZMOS

Move XYZ, yaw con anillo y Size para cajas/esferas. Cajas rotadas usan ejes locales al redimensionar. Actores no admiten escala sin contrato de runtime. Snap suelo, grid e incrementos angulares opcionales. Cambios visuales/números sincronizados durante el gesto. Deshacer separa creación y cada nuevo arrastre, manteniendo hasta 40 estados en memoria.

## COLOCACIÓN

Resource Browser → actor u objeto compatible → Usar selección → click en suelo visible. Raycast obtiene posición absoluta sin introducir XYZ. Flujo comprobado con businessWoman y barrel1; ambos se movieron y giraron mediante gizmos. Mover un elemento relativo al jugador convierte explícitamente su transform; abrir el viewport no lo convierte.

## TRIGGERS

Cajas con yaw/esferas, centro/dimensiones/radio, activación una vez/cada entrada y eventos comunes con condiciones/acciones. Entrada del jugador se detecta por Java propio con GetPosition y timer de 0,15 s, solo servidor y ubicación actual. No requiere NSD geométrico ni herramienta antigua.

Trigger → Añadir evento abre el editor existente: flags como condiciones AND y acciones spawn/set/clear. Entidad tiene un único propietario de spawn. Estados de activación/disparo y GUIDs se guardan/restauran. Once se consume cuando algún evento cumple; condición fallida requiere salir/volver. Conversación activa pausa muestreo. Esas reglas están probadas con doubles y compiladas contra API original, aún sin prueba nativa.

## RELACIONES

Grafo derivado del YAML: actor/conversación/speaker, eventos, condiciones, flags, spawns y triggers. Inspector muestra dependencias/referencias y resumen de activación, condiciones y acciones. Selección de trigger o evento resalta sus entidades espaciales; enlaces alrededor de selección pueden ocultarse. No se inventan vínculos de quests/exits que el modelo no admite.

## FIND REFERENCES

Botón derecho o botón del inspector/viewport muestra entradas y salidas. Doble clic navega a evento, conversación o flag correspondiente. Renombrar IDs/alias mantiene referencias conocidas, incluidos eventos de trigger. Outliner y selección de mapa siguen rutas del mismo documento.

## PROBADO

- **84 tests**, cero fallos/errores: las 64 pruebas previas más 20 de parser, raycast, cache, modelo, relaciones, triggers, compilación y sincronización UI. Informe: `build/tests/test_report.json`; detalle: `tests.log`.
- Harnesses previos: 20 escenarios del prototipo y 13 de eventos/conversación. Harness nuevo: **11 comprobaciones espaciales con doubles**, en `build/tests/spatial_java/harness.log`. No se consideran ejecuciones del motor.
- **42 verificaciones en ventana Qt real**, incluyendo actores/objeto por click, gizmos, Undo/Redo, picking, outliner, trigger, condición/acciones, referencias, visibilidad, save/reopen, validación y build. `build/viewport/acceptance/report.json` contiene los pasos y resultados.
- Proyecto Fase 2 abierto/construido con viewport sin modificar su YAML. Distribución byte a byte idéntica: SHA-256 `90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab`.
- Clases de la demo espacial compiladas contra Codex original, versión 45.3; geometría no incluida en paquete.
- **43 fuentes originales** verificadas por hash; sin cambios. Los seis archivos nativos de pruebas anteriores conservan hashes; los tres de Fase 3 coinciden con el build final.

Resumen verificable: `research/viewport/final_verification.json`. Capturas: `editor_spatial.png` y `trigger.png` en la aceptación. La captura de framebuffer muestra los overlays que la captura general Qt puede omitir.

## PROBADO DENTRO DE REDEMPTION

Histórico Fase 1: el usuario observó menú/nombre, mapa, Victoria cercana, conversación a pantalla completa, elecciones recordadas y fondo gris adecuado. Fase 2: confirmó **«Va perfecto»** para editor_playtest y aclaró que no había probado personalmente el editor. Declaración/log nativo: `research/runtime_test/phase2_native_acceptance.json` y `native_phase2_accepted.log`.

Esa crónica y sus clases siguen intactas en RCM/east_demo. La regresión conserva sus recursos y la distribución de aceptación. No existe todavía una confirmación del usuario para los nuevos triggers ni para todas las coordenadas absolutas de Fase 3.

Con permiso expreso se preparó **RCM: Londres, autoría espacial** en la misma carpeta del acceso directo conocido; NOB + dos clases. Backup completo previo y hashes en `research/runtime_test/deployment_phase3_demo.json`. Preparar esos archivos no constituye ejecución del juego. El agente no ha lanzado Redemption.

## NO PROBADO

Spawn absoluto/collision real en los puntos nuevos, sentido de yaw en nuestro actor, entrada/salida/once de triggers, diálogos con varios hablantes, save/load, abortos y dos jugadores/replicación. Las reglas compiladas deben contrastarse con el runtime, especialmente callbacks tras restaurar y movimiento rápido atravesando un volumen.

La comodidad de navegación y autoría sigue pendiente de evaluación personal del usuario; la aceptación automatizada comprueba controles/resultados, no sustituye esa experiencia.

## LIMITACIONES

Un level por proyecto. Modelos estáticos, iluminación de autoría, agua estática y transparencia aproximada. Cámara sin colisión lateral. Picking por bounds de actores/props. Snap no conoce accesibilidad ni apoyo físico de cada plantilla. `near_player` es marcador aproximado, no punto exacto de inicio.

Original entities son hints NSD de una escena asociada y pueden contener omisiones/coincidencias: readonly y confianza explícita. No existe importación completa de puertas, exits, cámaras, regiones o lights. Las familias no admitidas no se ofrecen como operaciones ficticias.

Trigger polling puede perder un cruce entre muestras; agrega todos los jugadores, no eventos individuales por cada jugador. Tras restaurar, el estado inside se reinicia: un trigger repetible puede volver a evaluar entrada si alguien permanece dentro; native save/load pendiente. Añadir/reordenar entidades o triggers cambia el layout del save generado: no se promete migración de partidas antiguas a un proyecto modificado.

Undo es limitado a sesión; GPU mantiene modelos cargados hasta cambiar level. La geometría original no es editable y no se inicia Fase 4.

## FORMATOS TODAVÍA NO COMPRENDIDOS

Cola global NIL/BSP/lightmaps completos, NSD con bloques variables/regiones originales, todos los tags NOT y cola no indexada, NAD/skinning, materiales multipass completos, paths de cámara y semántica de varias familias auxiliares. NOD estático y NAM difuso sí están implementados; no se confunden con soporte completo de animación/materiales.

## PROBLEMAS DE RENDIMIENTO

EastLondon durante navegación normal con timer Qt: 124 llamadas paintGL en unos 1.991 s, **62.28/s**, coste CPU medio **2.52 ms** en esta máquina. No es medición de presentación del monitor ni GPU finalizada; no garantiza 60 FPS para todo hardware/level.

No hay parsing por frame: VBO/texturas/cache estáticos y trabajador de carga. El raycast filtra AABB pero no usa BVH; geometría completa sin culling de BSP/sectores. Muchos helpers/modelos o mapas mayores requieren medición propia. Subida inicial a GPU todavía se realiza en el hilo gráfico.

## DEUDA TÉCNICA

Completar prueba nativa de contratos espaciales/persistencia, acelerar raycasts/culling cuando una medición lo justifique, mejorar ordenación global de transparencias y liberar modelos GPU no usados. Sustituir hints por parser NSD completo para una familia concreta. Versionar contratos de save si se requiere migración. Los codecs conservan límites/rechazos en lugar de adivinar bloques desconocidos.

## PROPUESTA PARA FASE 4

Cerrar primero las comprobaciones nativas pendientes del alcance actual. Después elegir una capacidad limitada y verificable: varias ubicaciones/salidas, una quest simple o referencias originales NSD fiables. Mantener authoring moderno, fuente único y generación directa. Esta sección es una propuesta; **Fase 4 no iniciada**.

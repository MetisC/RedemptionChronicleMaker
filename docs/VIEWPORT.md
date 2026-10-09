# Viewport de autoría — Fase 3

## Decisión técnica

Se usa **QOpenGLWidget + Qt OpenGL** dentro de la aplicación PySide6 existente. Qt aporta contexto, texturas, buffers y shaders; NumPy resuelve geometría/intersecciones y Pillow decodifica TGA. No hace falta un motor completo: selección y Properties se sincronizan mediante las mismas señales Qt. El backend de compilación conserva sus dependencias originales.

Se solicita OpenGL 2.1, profundidad de 24 bits y multisampling; shaders GLSL 120 favorecen compatibilidad. En la máquina de aceptación el contexto efectivo es 4.6 de compatibilidad. Se prioriza integración estable y autoría, sin afirmar equivalencia con un renderer de juego moderno.

Referencias primarias: [QOpenGLWidget](https://doc.qt.io/qt-6/qopenglwidget.html), [binding PySide6](https://doc.qt.io/qtforpython-6.8/PySide6/QtOpenGLWidgets/QOpenGLWidget.html) y [ejemplo oficial de shaders/buffers](https://doc.qt.io/qtforpython-6/examples/example_opengl_hellogl2.html). Documentan Qt, no los formatos de Redemption.

## Carga de un level

`Backend.levels` identifica NIL y escenas mediante catálogos de la instalación. Un trabajador separado lee el recurso del NOB, valida la estructura, recupera/reconstruye cache, resuelve NAM/TGA y los NOD de las plantillas usadas. Muestra progreso de lectura, geometría, texturas y preparación.

Solo la subida a GPU ocurre en el hilo gráfico. VBO estáticos agrupados por material y texturas reutilizables evitan parsing por frame. Añadir otra plantilla carga el modelo necesario. Se descartan resultados de cargas anteriores si cambia el level. El cambio de proyecto/level cancela gestos pendientes; no se escriben coordenadas obtenidas sobre un escenario anterior mientras carga el nuevo. Cerrar mientras carga espera su terminación sin destruir el hilo en marcha.

El lector comprende superficies/sectores de NIL v27 y mallas estáticas NOD v7. Tablas completas en FORMAT_NOTES.md. Se saltan portales con longitudes verificadas, sin usar su visibilidad; la cola global NIL no se interpreta ni reemite.

## Materiales, texturas y modelos

- Level: nombre NIL → `materials/<nombre>.nam` → `texture` relativa al NAM → TGA del NOB.
- Modelo: nombre NOT → `3d/models/<nombre>.nod`; materiales simples resuelven también `3d/materials/<nombre>.tga` y NAM inequívoco por basename.
- Agua multipass: textura estática de `pass 0`; no simula reflejos ni scrolling.
- TGA convertido a RGBA; UV originales, repetición, filtrado y mipmaps. Imagen orientada para OpenGL.
- Alpha cutout descarta alpha inferior a 0,30. Materiales transparentes usan blending sin escritura de profundidad, ordenados por distancia del centro del grupo dentro de cada malla. Aproximación: sin ordenación global de triángulos ni equivalencia con el renderer nativo.
- Material ausente: patrón magenta y warning con recurso/ruta; la carga restante continúa. Modelo no compatible: marcador y aviso.

EastLondon carga sus **109 materiales** sin fallback. Victoria utiliza la malla businessWoman y cuatro materiales resueltos. Modelos en pose estática; NAD, animación y skinning quedan fuera de esta fase.

## Coordenadas y navegación

XYZ conserva el espacio del motor, **Z vertical**; no hay escala oculta entre escena, YAML y generador. `[pitch, roll, yaw]` conserva el orden Codex; el gizmo gira yaw alrededor de Z. Los valores equivalen a orientaciones originales, pero sentido positivo/unidades requieren contraste nativo.

| Control | Acción |
|---|---|
| Botón derecho + ratón | Mirar; captura con recentrado en bordes |
| WASD | Movimiento |
| Q / E | Descender / ascender |
| Shift | Velocidad ×3 |
| Rueda | Velocidad de 20 a 6.000 unidades por segundo |
| F / Enfocar | Centrar selección o elementos relacionados |
| Alt + botón izquierdo | Orbitar selección |
| Suelo | Mantener aproximadamente 110 unidades sobre la superficie |
| 1 / 2 / 3 | Mover / girar / tamaño |
| Esc | Cancelar colocación o gesto |

Volar es el modo inicial. Suelo hace raycast vertical; no incluye colisión contra paredes ni garantiza una ruta transitable en el juego. Cámara del editor independiente de las tomas de conversación nativas.

## Picking y colocación

Raycaster precalcula triángulos, normales y bounds. Filtra candidatos con slabs y aplica Möller–Trumbore vectorizado. Se elige la primera superficie visible; colocar exige normal Z suficiente para considerarla suelo. No busca un suelo oculto detrás de una pared.

Actores/objetos usan bounds orientados por yaw y oclusión de geometría; no es picking por píxel de malla. Cajas: bounds orientados. Esferas: intersección esférica exacta. Helpers son overlays visibles incluso tras paredes; modelos usan profundidad. Una referencia oculta no participa en picking.

Resource Browser → plantilla compatible → clic en suelo crea actor/objeto absoluto. **+ Trigger** sigue el mismo flujo; centro inicial elevado medio volumen para apoyar la caja. Escape cancela. Source guarda números Python, nunca scalars NumPy.

`near_player` conserva el dato relativo. Se representa aproximadamente junto a una referencia original, etiquetado **vista aproximada**; no es el punto real de inicio multijugador. Abrir/enfocar no altera YAML. Moverlo explícitamente convierte a posición absoluta.

## Gizmos y snap

Mover usa XYZ del mundo; girar usa anillo/yaw. Tamaño cambia dimensiones de cajas o radio de esferas; cajas rotadas muestran ejes locales. Actores mantienen escala original. Properties y gizmos actualizan el mismo documento inmediatamente.

Grid 0 y ángulo 0 significan libre. Snap suelo ajusta movimientos horizontales, conservando edición Z explícita. **Ajustar al suelo** opera sobre la selección. No hay apoyo físico automático de props: el origen de un modelo puede requerir offset en Properties.

Ctrl+Z / Ctrl+Y restauran snapshots YAML, hasta 40 estados en memoria. Creación independiente de ajustes posteriores; cada arrastre abre un grupo. Ediciones numéricas rápidas de la misma selección se agrupan. No se conserva historial tras cerrar.

## Capas y relaciones

Outliner: geometría y referencias originales, nuestros actores, objetos y triggers; categorías y entidades admiten visibilidad. Referencias en gris, solo lectura. Proceden de patrones de tags en una escena asociada; inspector muestra procedencia/confianza, sin afirmar que sean exhaustivas o infalibles.

Selección dorada; relacionados verdes. Relaciones consulta actores, conversaciones, eventos, flags y triggers realmente presentes. Links espaciales aparecen alrededor de la selección y se pueden ocultar. Quests, exits, waypoints y cámaras no tienen controles ficticios ni entidades propias en el modelo actual.

**Find References** ofrece entradas/salidas navegables. Inspector del trigger muestra activación, condiciones y acciones de sus eventos. Evento seleccionado en Historia → **Mostrar relacionados en 3D** resalta/enfoca entidades. Flags/conversaciones conservan inspectores narrativos sin posiciones inventadas.

## Triggers y runtime

Cajas orientadas y esferas YAML se compilan a tests de posición Java mediante API real, sin escribir regiones geométricas NSD. Servidor muestrea cada 0,15 segundos jugadores de la ubicación y detecta transición de ninguno dentro a alguno dentro. `once: true` se marca disparado cuando cumple algún evento; false permite otra entrada tras salir todos.

Condiciones se evalúan al entrar; si fallan, salir/volver permite reevaluar. Conversación activa pausa muestreo; entrar durante ella puede detectarse después. Cruces muy rápidos entre muestras pueden perderse. Acciones: spawn, activar/desactivar flag. Cada entidad tiene un propietario de spawn: inicio o trigger. Activación/disparo se guardan con GUIDs; save/load real pendiente. Tras restore se reinicia el estado inside: un trigger repetible puede evaluarse de nuevo si alguien sigue dentro. Cambiar cantidad/orden de entidades o triggers cambia el layout del save; no hay migración de partidas antiguas.

## Cache, errores y rendimiento

`cache/geometry/<SHA-NIL>-v1.npz`: arrays sin pickle, tamaños/índices/finitud/offsets validados; corrupto se regenera. `cache/textures/<SHA-TGA>.png`: RGBA regenerable. `cache/levels/<level>.json`: procedencia, cantidades, warnings/aciertos. Se pueden borrar esas tres carpetas para reconstruirlas; conservar catálogos y toolchain para no perder el backend preparado.

Cache y escrituras del editor dentro del workspace. Un fallo OpenGL muestra diagnóstico; no se atribuye al YAML. Offscreen usa placeholder para probar datos sin GPU.

Aceptación mide llamadas paintGL durante navegación con temporizador Qt en EastLondon de esta máquina: tiempo real, cantidad y coste CPU medio. No mide presentación de monitor ni finalización GPU, y no garantiza 60 FPS en todo level/hardware. No hay BVH, culling BSP ni streaming: se dibuja toda la geometría.

## Campañas de Fase 4

El selector de escena cambia las colecciones del documento activo. Geometría original y cache permanecen por level; no se recalculan por una edición de quest. Se cancelan colocaciones/arrastres al cambiar de escena, incluso si ambas reutilizan el mismo NIL. Las rutas del viewport son relativas a esa vista; undo conserva todos los mapas.

Un viaje puede enlazarse a un trigger espacial y su volumen actúa como marcador visible. No se ha implementado importación/editor de exits geométricos. Cámara de Fase 4 enfoca un actor: el botón preview localiza su modelo, no promete encuadre nativo. Inventario/NPC junto al jugador sigue siendo un marcador aproximado; una coordenada obtenida del raycast no garantiza accesibilidad del juego.

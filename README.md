# Redemption Chronicle Maker — 0.9.12

Abre **Redemption Chronicle Maker.lnk**, el acceso directo en la raíz del proyecto. `build/` conserva únicamente el editor actual (`portable/`) y los builds del Tutorial (`rcm_tutor/`) y la Mini crónica (`rcm_mini/`). Las licencias, fuentes, tests y evidencias necesarias para reconstruirlos se conservan.

Esta revisión añade notas nativas: prólogos, cartas y avisos con título y párrafos. En el editor: **Eventos → Historia / Mostrar nota**, o selecciona un objeto y pulsa **Añadir nota al usar**. **Añadir conversación al usar** vincula el objeto con una conversación existente y su personaje hablante. El tutorial muestra un prólogo, una carta en el laboratorio de Christof y una nota sobre el barril. Los gestos tienen ahora una pose de reposo debajo y recuperan el reposo al terminar. Evidencia y límites: [NOTES_AND_MOTION_FIX.md](docs/NOTES_AND_MOTION_FIX.md).

Esta revisión refuerza el guardado de posición y orientación, cancela correctamente las cutscenes al cargar y añade animaciones por nodo o línea de conversación. El laboratorio muestra los movimientos reales de su modelo; la película empieza con un plano aéreo amplio, sin transición inicial. Las comprobaciones y límites se detallan en [docs/ANIMATION_RESTORE_FIX.md](docs/ANIMATION_RESTORE_FIX.md). La auditoría del editor está en [docs/STABILITY_USABILITY_AUDIT.md](docs/STABILITY_USABILITY_AUDIT.md).

**Empieza una partida nueva** para probar esta revisión: el contrato de guardado ha cambiado y no hay migración de saves antiguos. La prueba visual en Redemption sigue pendiente; compilación y tests no la sustituyen.

El tutorial avanza por siete lecciones, con un docente cada vez y opción de omitir cada paso. Las opciones de experimentación están en un laboratorio a la izquierda de los profesores. Anezka presenta una película de doce segundos: puerta móvil, apertura, paseo y cuatro planos. Elena entrega una llave física. Se corrige la acumulación de temporizadores tras los diálogos. Diagnóstico y límites: [docs/CTD_CINEMA_INVENTORY_FIX.md](docs/CTD_CINEMA_INVENTORY_FIX.md).

Esta revisión usa la cámara sobre el hombro por defecto y Vera muestra los 13 encuadres uno por uno, al pulsar Siguiente. Se elimina la llamada que borraba las animaciones al hablar y provocaba la pose en T. Los textos y el journal se han reescrito con explicaciones más naturales. Diagnóstico y límites: [docs/DIALOGUE_MOTION_CAMERA_FIX.md](docs/DIALOGUE_MOTION_CAMERA_FIX.md).

Abre `build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe`. En **Abrir** quedan dos proyectos: **Tutorial** (un escenario con varios layouts) y **Mini crónica** (dos mapas y una historia corta). **Ayuda → Tutorial del proyecto** explica los elementos con enlaces dentro del editor. **Espacio 3D → Inicio** selecciona y enfoca el punto de aparición del jugador. Para ensayar el nuevo tutorial en Redemption, crea una **partida nueva** y elige **RCM · Tutorial paso a paso**.

El usuario ha confirmado que LAN funciona después de corregir la carga inicial de plantillas propias. El personaje se conserva. Diagnóstico y evidencia: [docs/ENGINE_NOTES.md](docs/ENGINE_NOTES.md#investigación-de-crash-lan--diagnóstico-mediante-volcados-09102026).

Guía: [docs/ROUND0_GUIDE.md](docs/ROUND0_GUIDE.md). Las nuevas pruebas dentro del juego siguen pendientes. Puertas físicas completas y writer de travelling NCP siguen abiertos; no se afirma paridad con Embrace. Los ejemplos antiguos necesarios para regresiones se conservan en `tests/fixtures/chronicles`.


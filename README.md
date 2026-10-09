# Redemption Chronicle Maker — 0.9.10, ronda 0

El tutorial avanza por siete lecciones, con un docente cada vez y opción de omitir cada paso. Las opciones de experimentación están en un laboratorio a la izquierda de los profesores. Anezka presenta una película de doce segundos: puerta móvil, apertura, paseo y cuatro planos. Elena entrega una llave física. Se corrige la acumulación de temporizadores tras los diálogos. Diagnóstico y límites: [docs/CTD_CINEMA_INVENTORY_FIX.md](docs/CTD_CINEMA_INVENTORY_FIX.md).

Esta revisión usa la cámara sobre el hombro por defecto y Vera muestra los 13 encuadres uno por uno, al pulsar Siguiente. Se elimina la llamada que borraba las animaciones al hablar y provocaba la pose en T. Los textos y el journal se han reescrito con explicaciones más naturales. Diagnóstico y límites: [docs/DIALOGUE_MOTION_CAMERA_FIX.md](docs/DIALOGUE_MOTION_CAMERA_FIX.md).

Abre `build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe`. En **Abrir** quedan dos proyectos: **Tutorial** (un escenario con varios layouts) y **Mini crónica** (dos mapas y una historia corta). **Ayuda → Tutorial del proyecto** explica los elementos con enlaces dentro del editor. **Espacio 3D → Inicio** selecciona y enfoca el punto de aparición del jugador. Para ensayar el nuevo tutorial en Redemption, crea una **partida nueva** y elige **RCM · Tutorial paso a paso**.

El usuario ha confirmado que LAN funciona después de corregir la carga inicial de plantillas propias. El personaje se conserva. Diagnóstico y evidencia: [docs/ENGINE_NOTES.md](docs/ENGINE_NOTES.md#investigación-de-crash-lan--diagnóstico-mediante-volcados-09102026).

Guía: [docs/ROUND0_GUIDE.md](docs/ROUND0_GUIDE.md). Las nuevas pruebas dentro del juego siguen pendientes. Puertas físicas completas y writer de travelling NCP siguen abiertos; no se afirma paridad con Embrace. Los ejemplos antiguos se conservan en `tests/fixtures/chronicles`; los trabajos previos del portable se respaldan en `research/round0/retired_user_projects.zip`.

# RedemptionChronicleMaker
Redemption Chronicle Maker

# Fase 9 · entrega de implementación, aceptación manual pendiente

Versión 0.9.0. Esta entrega integra la auditoría externa y continúa la implementación; no cierra la aceptación dentro del juego. Por petición del usuario, no se ha lanzado Vampire y todas las pruebas nativas de esta revisión quedan pendientes.

## Entregado

- Nuevas campañas en formato 9, compatibles con el pipeline previo: entradas nombradas, llegada por defecto, waypoints y recorridos editables en la vista 3D. Los proyectos antiguos conservan su generador.
- Viajes que comprueban llegada antes de ejecutar contenido; carga de partida que conserva la posición guardada. Recorridos con seguimiento, pausa durante diálogo, recuperación del estado y parada por fallo.
- Eventos de una sola ejecución con progreso y comprobación por acción, para reintentar un fallo sin repetir pasos ya completados. No garantizan atomicidad entre un efecto nativo y su guardado.
- Presets de cámara basados en SDK, sonido situado, control experimental de puertas y exits mediante identificadores reales. No se inventan identificadores ni se sustituye el script original de una puerta.
- Diagnóstico por escena, evento, acción, conversación y quest. Límites del bytecode medidos sobre las clases compiladas. Despliegue con propiedad de archivos, retirada de obsoletos propios y recuperación de la transacción.
- Auditoría de madurez, comparación de funciones, matriz de pruebas y bloqueos actualizados. No se presentan controles nuevos como evidencia de funcionamiento nativo.

## Crónica única para probar después

**Las voces de Londres · Circuito**, `chronicles/circuit/project.yaml`. Tres escenas sobre dos geometrías originales, seis NPC, dos quests, decisiones persistentes, objeto propio, AI y Java propios, dos recorridos, viajes de ida/regreso y combate opcional. Las posiciones se contrastaron con el suelo de la geometría; la navegación y colisión reales siguen pendientes.

Se retiraron 57 archivos de nuestras demos desplegadas, conservados en `research/phase9/retired_all_demos.zip`. RCM contiene un único paquete seleccionable de nuestra herramienta, en la carpeta que usa el acceso directo existente. Las crónicas oficiales y las partidas no se han eliminado. Las fuentes históricas permanecen como fixtures en el workspace.

El paquete completo está en `build/rcm_circuit/rcm_circuit.rcmpack`; el editor portable está en `build/portable/RedemptionChronicleMaker/`. El circuito está curado mediante nuestro generador; no se afirma que la aventura completa haya sido creada y aceptada manualmente desde la GUI.

## Evidencia y límites

La suite completa pasó 198 pruebas sin fallos ni omisiones. Después de los últimos ajustes de diagnóstico e interfaz pasaron las 11 pruebas específicas de Fase 9. Se compiló Java 45.3 y se midieron sus límites. Un ensayo del editor creó un proyecto básico con colocación mediante clic en suelo, edición, guardado, reapertura y compilación usando un contexto OpenGL real. El portable abrió y compiló en un workspace nuevo sin Python/JDK globales en PATH, en este mismo equipo; no equivale a una máquina independiente.

Los informes están en `research/phase9/`. Las pruebas de runtime con doubles verifican nuestra lógica y no acreditan los callbacks, HUD, journal o navegación de Redemption. La comparación de hashes verifica los originales catalogados, no todos los posibles archivos de la instalación.

Permanecen abiertos: control selectivo del contenido estático, autoría completa de puertas/cerraduras/conexiones, cámara exportable desde la vista 3D, significado completo de NCP, aceptación nativa de NOT/AI, save/load y aborto, autoría humana de una aventura completa desde la GUI, prueba portable en máquina independiente y multijugador. No se ha comenzado otra fase.

Consulta [PHASE9_PLAYTEST.md](PHASE9_PLAYTEST.md) para el recorrido manual, [AUTHORING_MATURITY_REPORT.md](AUTHORING_MATURITY_REPORT.md) para el estado de la auditoría y [RELEASE_BLOCKERS.md](RELEASE_BLOCKERS.md) para los requisitos pendientes de aceptación.

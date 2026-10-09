# Aceptación manual pendiente · circuito 0.9.0

El usuario ha solicitado aplazar los ensayos dentro del juego. **NOT TESTED** en todos los casos de esta revisión, sin convertir pruebas offline en aceptación nativa. Instrucciones completas en [PHASE9_PLAYTEST.md](PHASE9_PLAYTEST.md). Crónica visible: **Las voces de Londres · Circuito**. Acceso directo habitual intacto, carpeta `RCM/east_demo`, log propio en `RCM/rcm_circuit`.

Registrar versión, SHA del NOB/distribution del build, partida nueva/guardada, pasos, resultado PASS/FAIL/NOT TESTED y observación visible. Una lectura de trace sola no acredita HUD, journal o cámara.

| Caso | Esperado | Estado 0.9.0 |
|---|---|---|
| Menú/título | Una sola crónica propia, nombre y títulos legibles | NOT TESTED |
| Llegada inicial | Victoria y guía accesibles cerca; suelo y colisión correctos | NOT TESTED |
| Primera negativa | Rechazar, recuperar HUD/cursor/movimiento, volver a hablar | NOT TESTED · B1 |
| Abortar | Cámara/control liberados; ningún RETURN aplicado | NOT TESTED · B1 |
| Pacto recordado | Aceptar y ver conversación posterior; cargar y repetir | NOT TESTED |
| Dos quests | Journal muestra título, pasos y progreso sin duplicarlos | NOT TESTED |
| Rama negociación | Libro, flag, respuesta pacífica al regreso | NOT TESTED |
| Rama intimidación | Libro, flag y respuesta alternativa al regreso | NOT TESTED |
| Item propio | Un libro heredado de ledger en inventario; retiro al entregar | NOT TESTED · B3 |
| Template/AI/Java propios | Victoria correcta; herencia, modelo y script efectivos | NOT TESTED · B3 |
| Llegada al archivo | Cambio de geometría y transform elegido, cerca de dos NPC | NOT TESTED |
| Segunda escena EastLondon | Capa propia de testigo/mensajera; escena inicial conserva su capa | NOT TESTED |
| Dos patrullas | Orden/loop, sin atravesar obstáculos; pausa al hablar, reanuda después | NOT TESTED |
| Triggers de llegada | Se activan una vez, flags observables, bordes y reentrada | NOT TESTED |
| Plano y sonido | Two Shot tres segundos, devolución de cámara; fuente situada audible | NOT TESTED |
| Audio de escena | Música/ambient correctos, sin persistencia indebida al viajar | NOT TESTED |
| Final y recompensa | Libro retirado; quests completas; 650 XP una vez | NOT TESTED |
| Combate optativo | Cuatro enemigos sólo después de elegirlo; 100 XP una vez al vencer | NOT TESTED |
| Tres ciclos de regreso | Decisión/journal/inventario/GUIDs coherentes, sin duplicados | NOT TESTED · B2 |
| Save/load antes de decidir | Posición y estado inicial restaurados; no recoloca en entrada | NOT TESTED · B2 |
| Save/load con libro / transición | Posición, item, decisión y pasos conservados | NOT TESTED · B2 |
| Save/load después de final | No repetir XP, libro ni progreso; control intacto | NOT TESTED · B2 |
| Save/load durante diálogo/plano | Liberar estado de cámara/UI incompleto | NOT TESTED · B1/B2 |
| Exits originales | Seleccionar Cast ID comprobado; IsExitValid, abrir/cerrar | NOT TESTED · no estación ficticia incluida |
| Puerta existente frames/pivote | Seleccionar recurso real y sus frames; comportamiento/script coherentes | NOT TESTED · paridad incompleta |
| Contenido estático base | Identificar qué permanece e interferencias reales | NOT TESTED · selección ALL/NONE no implementada |
| Host/client | Dos clientes, decisiones, viajes y reentrada coherentes | NOT TESTED · B5, fuera de beta local |

La matriz histórica de System Test se conserva en [RUNTIME_TEST_MATRIX_PHASE6.md](RUNTIME_TEST_MATRIX_PHASE6.md). La observación humana limitada de 0.7.0 está en `research/phase9/phase7_user_observation.json`; no acepta este build.

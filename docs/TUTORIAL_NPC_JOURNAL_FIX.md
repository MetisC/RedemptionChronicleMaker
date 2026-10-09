# Tutorial 0.9.4 — PNJ y guía dentro del juego

## Confirmado por el usuario y el log nativo de 0.9.3

La llegada a [-176,-768,384] permite caminar. No aparecen PNJ. El log registra `SPAWN_FAILED template=R_rcm_tutor_s0_mentor guid=0` y posiciones posteriores del jugador. La primera acción de arrival espera a crear la mentora y no llega a las demás estaciones. Copia del log y fuente: research/round0/npc_journal_fix/native_failed_093.log y source_093.yaml.

La quest lesson se cargaba después de aceptar el diálogo de la mentora, por lo que tampoco había una indicación inicial en el journal. La guía del editor no sustituye al journal del juego.

## Confirmado en archivos originales / SDK

- CodexWorld.CreateThing(String,float[],float[]) y CodexThing.SpawnThingNear(String,float,int), SetPosition(float[]) y SetOrientation(float[]) existen en las clases originales. El segundo método creó Victoria en la prueba nativa aceptada de Fase 2.
- El NOT original businessWoman hereda `ped.nai` de _civilians_MD. Nuestra plantilla propia referenciaba el ID `AI_tutor`, aunque el archivo generado se llama `AI_tutor.nai`. En formato 9 se traducen IDs de catálogo a nombres reales de archivo para los campos AI y modelo; el ID de Java conserva el nombre de clase. Los builds de formato 5 conservan sus bytes históricos; la prueba golden no se redefine para ocultar un cambio.
- El JNI CreateThing tiene varias salidas con 0: mundo ausente, plantilla no resuelta o fallo al crear/situar. El 0 observado no distingue por sí solo cuál ocurrió. No se atribuye exclusivamente a la AI sin nueva evidencia nativa. Investigación reproducible: tools/research_spawn_journal_failure.py.
- La definición NQD y sus textos NLS se generan directamente. CodexQuest.Load carga la entrada del journal; su firma y uso constan en clases y scripts originales.

## Corrección preparada

Formato 9 mantiene CreateThing como primera vía. Si devuelve 0, precarga la misma plantilla, utiliza SpawnThingNear sobre el jugador y aplica las coordenadas y orientación propias. Si el motor rechaza el transform, elimina la instancia provisional y permite reintentar. No sustituye una plantilla propia por otra genérica ni marca un spawn fallido como completo. Registros: SPAWN_FACTORY_FAILED, SPAWN_POSITION_REJECTED y SPAWN_RECOVERED.

El tutorial carga automáticamente `Tutorial RCM: empieza aquí` en un evento independiente anterior al spawn. Su descripción explica estaciones, cámaras, inventario, llave, flags, escenas, encuentro opcional, guardar/cargar y controles del editor. La lección guiada sigue iniciándose con la mentora y sus pasos tienen instrucciones concretas. La guía del journal se completa en el final del circuito.

## Verificación y límites

La prueba de Java con doubles provoca fallo de ambas fábricas, comprueba que el journal se inicia de todos modos, rechaza la colocación temporal y comprueba su retirada, recupera la instancia en coordenadas propias, y verifica que retry y restore no duplican actor ni journal. Esto no es una prueba del motor real.

Se compila contra Codex original con versión de clases 45.3. La nueva revisión debe comenzar con partida nueva: añadir la quest y cambiar acciones modifica los flags reservados y el contrato de guardado. El despliegue afecta sólo a RCM y conserva backups. La aparición efectiva de PNJ, journal y su legibilidad siguen pendientes de nueva prueba manual. No se abre el juego automáticamente.

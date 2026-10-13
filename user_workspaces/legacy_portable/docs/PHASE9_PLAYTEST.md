# Circuito único · prueba manual posterior

No se ha abierto Redemption para probar esta revisión. Todo resultado de juego de 0.9.0 está **NOT TESTED**. Fuente: `chronicles/circuit/project.yaml`; paquete: `build/rcm_circuit/rcm_circuit.rcmpack`. El build exacto y sus hashes están en `build/rcm_circuit/build_report.json`.

Cuando quieras probarlo, abre **tu mismo acceso directo del escritorio**, sin cambiarlo. Entra en **Multiplayer → New Game → Las voces de Londres · Circuito**. Crea una partida nueva; las partidas de las demos anteriores no tienen el mismo contrato de estado.

## Qué debería verse y cómo completar el circuito

1. Apareces en EastLondon, en la llegada colocada cerca de **Victoria · empieza aquí**. Victoria está a unos 156 puntos de distancia; la guía está al lado, en un recorrido corto. Ambos están en suelo identificado en la geometría. La transitabilidad real queda por comprobar.
2. Habla con Victoria. Primero puedes rechazar, salir y volver a hablar. Acepta el encargo: deberían aparecer dos quests en el journal. No debe quedar cámara, cursor ni HUD bloqueado.
3. Habla con la guía y elige **Viajar al archivo**. Deberías aparecer cerca de la archivera y la custodia. Se reutiliza GunHaven como archivo; el contenido estático original de esa geometría puede permanecer.
4. Habla con la archivera. Elige **negociar** o **intimidar**: ambos caminos entregan un libro y avanzan las quests, pero el regreso recuerda una respuesta distinta. No debería ser necesario recoger manualmente el objeto.
5. La custodia ofrece **Probar plano y sonido situados**, como prueba aparte. El plano de dos personajes dura tres segundos. Después debería devolverse el control. El sonido de trueno procede del waypoint de prueba, no de una pista musical.
6. La custodia te lleva al **regreso**. Es otra escena sobre EastLondon: hay testigo y mensajera, con otra capa de contenido.
7. Habla con el testigo y entrega el libro. Deberían completarse ambas quests, retirarse el libro y recibirse **650 XP una sola vez**. Hablar de nuevo muestra el final.
8. La mensajera vuelve al comienzo. Victoria debe recordar el pacto. Repite tres ciclos: no deberían duplicarse NPC, libro ni recompensas.

**Combate opcional:** la tercera respuesta de la guía activa cuatro enemigos. No se activan por viajar ni por entrar al circuito. Haz esta prueba en una partida guardada aparte; no es necesaria para terminar la aventura. Cuando mueren los cuatro, la guía cambia de conversación y se conceden 100 XP una sola vez. Dificultad y navegación no están equilibradas ni verificadas en esta revisión.

## Guardar y cargar

Guardar/cargar antes de aceptar, con el libro, al llegar al regreso y después del final. Comprobar posición del jugador, quests, decisión, inventario, GUIDs y XP. La carga debería conservar la posición guardada, sin mover al jugador a la entrada. Ensayar también guardar con diálogo o plano activo; el controlador libera cámara al restaurarse.

Probar rechazar primera respuesta, abortar, repetir diálogo y guardar/salir/volver a abrir. Anotar PASS/FAIL por caso en [RUNTIME_TEST_MATRIX.md](RUNTIME_TEST_MATRIX.md). Las pruebas de lógica con doubles no sustituyen estas observaciones.

## Diagnóstico y recuperación

El log nuevo estará en `H:\GOG\Vampire The Masquerade - Redemption\RCM\rcm_circuit\runtime_trace.log`. En el editor, **Playtest / Debug → Leer trace** permite abrir escena, evento, acción, conversación o quest desde registros identificados. SAVE_STATE / RESTORE_STATE / RESTORED indican callbacks recibidos, no garantizan que el journal o HUD se vean bien.

Las demos antiguas fueron retiradas únicamente de RCM. Sus fuentes siguen en el workspace para regresiones. Las copias están en `research/phase9/retired_rcm_*.zip`; el inventario acumulado está en `research/phase9/deployment_cleanup.json`. No se han borrado partidas del juego ni cambiado el acceso directo.

## Crear y editar desde la interfaz

**Nueva crónica** crea una campaña de formato 9. Elige geometría en **Level base**. En **Campaña / Quests**, añade escenas, entradas, waypoints y recorridos. Entrada/waypoint: pulsa su botón y haz clic en suelo del viewport; mueve/gira o ajusta XYZ en Propiedades. La primera entrada es la llegada por defecto; puedes cambiarla en la escena.

Un recorrido elige actor, lista ordenada de waypoints, repetición, tolerancia y parámetro de movimiento. Se ejecuta mediante **Movimiento / Seguir recorrido** en un evento. Un viaje usa **Viaje / Escena y punto de llegada**, con dos selectores. **Guardar → Validar → Build → Deploy** actualiza el paquete y retira sus archivos propios obsoletos. El aviso de partida nueva aparece cuando cambia el contrato persistido.

Puertas existentes, exits y sonido situado son acciones experimentales. El movimiento de puerta requiere Cast ID, tipo de movimiento y frames originales; no hay editor de cerraduras ni sustitución del script original. No hay opción ficticia ALL/NONE/SELECTIVE de contenido estático ni cámara desde vista exportable todavía.

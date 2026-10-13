# Vigencia durante Fase 2

Este documento conserva el protocolo histórico del prototipo. Los despliegues a RCM descritos debajo ocurrieron en Fase 1. La petición de Fase 2 prohíbe escribir automáticamente en toda la instalación, incluida RCM: el build del título y la aceptación nueva solo están en el workspace.

Para la prueba manual actual utiliza el procedimiento de [EDITOR_GUIDE.md](EDITOR_GUIDE.md), que propone una copia independiente del juego y distingue la aceptación nueva del ensayo histórico del usuario. Estado final: [PHASE2_REPORT.md](PHASE2_REPORT.md).

---

# Seguimiento de la prueba nativa

El usuario confirmó en la revisión 3: nombre correcto, mapa cargado, halo desaparecido, Victoria visible junto al jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara de diálogo se percibe algo baja. Save/load y replicación en red no se han probado. La revisión 4 cambia únicamente los dos nombres de fondo del NSD: LondonNightSky → Sky, un recurso original con estrellas, luna, nubes y forma de skyline. No se afirma que reproduzca el fondo exacto de EastLondon. Java, NPC, diálogo, flags y demás bytes de escena son idénticos a la revisión 3. Su resultado visual cerca del muelle sigue pendiente. Investigación: research/sky/FINDINGS.md; estado: research/runtime_test/revision4_status.json.

## Comprobar ahora la revisión 5

Las dos referencias originales muestran gris y el usuario considera adecuado ese aspecto. Ya no hace falta repetir la comparación. Abrir el mismo acceso directo, crear una partida nueva de **Redemption Chronicle Maker: Londres nuevo** y comprobar que el fondo recupera ese aspecto sin el cielo estrellado. Victoria y las conversaciones deben comportarse igual. La fuente y el paquete conservan todos los metadatos originales del entorno.

## Ensayo de la demo

Revisión 5 desplegada en RCM/east_demo. Se comprobó que Vampire no estaba abierto antes de sustituir el paquete.

1. Abrir el acceso directo existente con `-user RCM\east_demo` e «Iniciar en» la raíz del juego.
2. Multiplayer → New Game: elegir **Redemption Chronicle Maker: Londres nuevo**. Debe sustituir la etiqueta corta; no cargar un save de la versión anterior.
3. Crear una partida nueva con un jugador. Esperar unos segundos: **Victoria**, con modelo `businessWoman`, debe aparecer junto al personaje, en un punto próximo elegido por el motor. Ya no hay que buscar el punto de Otto.
4. Acercarse al muelle y comprobar el fondo gris, como las referencias originales. La revisión 5 ya no añade Sky ni LondonNightSky. El halo desapareció en revisión 3 y se mantiene CLEARBUFFER.
5. Activar subtítulos, acercarse a Victoria y usar la interacción de hablar. Comprobar las dos respuestas y que aceptar cambia el siguiente saludo. Si falta Victoria, revisar la consola/log: el script imprime la creación y errores de spawn tras un máximo de 60 segundos de espera.

El despliegue ya está realizado: no hace falta copiar archivos ni cambiar el acceso directo. Se han guardado los archivos anteriores en `research/runtime_test/backups/` y retirado diez recursos sueltos antiguos que podían ocultar la versión del NOB.

Después de probar, consultar `H:\GOG\Vampire The Masquerade - Redemption\RCM\east_demo\runtime_trace.log`. Lo genera el juego al construir nuestro controlador; no existe un log nativo previo creado por el builder. Interpretación:

- Sin archivo: investigar carga del NSD/clase o escritura fallida del registro; no demuestra por sí solo cuál falla.
- `scene controller constructed` sin `beginscene`: clase creada pero callback de inicio no registrado en el log.
- `player=0` durante todos los intentos: no se encuentra un personaje válido en la ubicación; comprobar si se entró solo como storyteller.
- `SpawnThingNear GUID=0`: falla la creación/colocación; comprobar carga NOT, plantilla y collision.
- GUID distinto de cero: creación retornó un objeto; falta verificar su ubicación, visibilidad y modelo.
- `SPAWN EXCEPTION`: error Java/nativo registrado; conservar el mensaje exacto.

El log de `build/tests/RCM/east_demo/` pertenece al motor simulado. Nunca usarlo como prueba de la sesión del juego.

## Preparación y carga

1. Comprobar `build/east_demo/build_report.json`: estado compilado, ambas clases 45.3 y ausencia de NIL en la distribución.
2. Usar la carpeta RCM autorizada y ya actualizada; opcionalmente preparar una copia completa independiente del juego en build/runtime_test/game/, sin enlaces al original.
3. Verificar los hashes del original. El paquete contiene east_demo.nob y dos clases en codex/. Si se prepara otra copia para el ensayo, extraer el ZIP en su RCM/east_demo sin recursos sueltos antiguos. Ejecutar con -user RCM\east_demo y directorio de trabajo en la raíz del juego. Detalle en USER_DIRECTORY.md.
4. Activar subtítulos en la copia para observar texto sin voz hablada. Registrar versión del juego, opciones y modo de ejecución. La crónica se configura para modo multiplayer/storyteller con flags NSC 0x3, siguiendo un ejemplo original; primero usar un servidor local con un solo jugador.
5. Comprobar el nombre Redemption Chronicle Maker: Londres nuevo. Si todavía aparece east_demo, revisar la carga automática de strings/_R_east_demo.nls. Registrar logs/capturas en research/runtime_test/.
6. Cargar la crónica y comprobar que la geometría es EastLondon. Confirmar que no se ha importado la escena de Otto ni la narrativa original. Identificar si NIL aporta algún contenido residual.

## Escenario de aceptación

| Comprobación | Resultado esperado | Evidencia que guardar |
|---|---|---|
| Punto de entrada | Entrada 0 válida y beginscene del ghost | Log de carga/callback |
| Spawn dinámico | Una Victoria, no dos; plantilla/modelo correctos | GUID y captura |
| Transform | Punto próximo al jugador, yaw 180 en componente 2 | Lecturas GetPosition/GetOrientation |
| Collision | En suelo válido, visible y accesible | Captura y movimiento alrededor |
| Interacción | NPC neutral, AI pausada, clic de hablar | Callback clicked con ambos GUID |
| Diálogo inicial | Prompt y dos respuestas visibles | Captura y NVO resuelto |
| Respuesta 1 | convended devuelve 1; flag 1 true | Log/consulta del flag |
| Interacción posterior | Se elige conversación `ally` | Captura del texto diferente |
| Respuesta 2 | Devuelve 2; flag false; vuelve `intro` | Log y siguiente interacción |
| Aborto | No aplica una decisión ni queda bloqueo activo | Cancelación y nueva interacción |
| Save/load | Mantiene flag y una sola entidad; capture recuperado | Save en la copia y nueva interacción |
| Reload/scene lifecycle | Evita duplicar NPC tras volver a cargar | Conteo de entidades y GUIDs |

La revisión deja que SpawnThingNear busque un punto alrededor del jugador; el harness simula esa proximidad, pero no valida la collision nativa. El modo `absolute` sigue disponible para autoría por coordenadas; nunca abrir Embrace para colocar entidades.

## Aislar fallos

- **Error de Java**: revisar classpath nativo y carga de 45.3. Las clases entregadas van en `codex/`; el NOB de recursos no resuelve por sí solo el classpath de la JVM.
- **Plantilla ausente**: comprobar descubrimiento de `misc/templates/R_east_demo.not`, herencia, nombres de tags y recursos. Preservar el archivo fallido para comparar bytes; ampliar el codec propio si hace falta.
- **Escena no aceptada**: comparar cabecera y bloques vacíos con `RABI_CTD_1_1.nsd` u otra escena simple. No sustituir el generador por un exportador antiguo.
- **NPC visible pero sin hablar**: verificar TALKTO, Cast ID y CaptureThing; confirmar significado/orden de clicked y callbacks.
- **Texto no visible**: distinguir NCO/NVO no resuelto de subtítulos desactivados o duración de voz. El WAV silencioso existe; su estrategia aún necesita confirmación.
- **Flag/GUID perdido**: registrar orden save/restore/restored/beginscene y corregir la serialización propia. El harness no representa el guardado nativo.

Después del ensayo con el NOB de recursos y las clases, registrar precedencia frente a archivos sueltos de diagnóstico si se necesitan. No usar una distribución únicamente suelta bajo `-user` para comprobar la enumeración del selector. Finalmente repetir las decisiones con un segundo cliente para comprobar replicación; no confundir el guard de servidor del código con una prueba de red.

## Cierre del ensayo

Comparar otra vez los hashes del original, guardar logs y resultados por cada fila y actualizar `ENGINE_NOTES.md` con una categoría explícita de comprobación dentro del motor. La Fase 1 no podrá considerarse demostrada en juego por el mero hecho de que el ZIP exista o las pruebas offline pasen.

## Resultado de la comparación y revisión 5

El usuario confirmó que ambas comparaciones de EastLondon —mapa base con escena null y escena original EAST_28_1— muestran un fondo gris que considera adecuado. No se requiere añadir Sky para reproducir ese aspecto. La demo de revisión 5 omite level.sky y conserva íntegros los 176 bytes originales del entorno; los dos campos finales de modelo/animación están vacíos. Solo se eliminan las dos referencias añadidas; NPC, conversaciones, flags, Java y demás bytes de escena permanecen idénticos. Su aspecto final aún necesita comprobarse en una partida nueva de la demo.

Evidencia nativa aportada por el usuario: gris en ambas referencias. Evidencia estática: campos finales vacíos en los NSD originales y copia exacta de sus metadatos en la demo. La necesidad de un skybox extra queda descartada para este caso; no se generaliza a otros niveles. Los modelos añadidos en revisiones 3/4 fueron elecciones experimentales y no la configuración original de EastLondon. Estado y despliegue: research/runtime_test/revision5_status.json y deployment_revision5_2026_10_08.json. Se mantienen CLEARBUFFER y las correcciones funcionales de revisión 3. Las 26 pruebas pasan; save/load, red, aborto y ajuste de cámara siguen pendientes.

## Aceptación nativa de Fase 4 pendiente

Partida nueva: RCM: El libro de Londres. Verificar Victoria cercana/diálogo ramificado; aceptar encargo; journal y primer paso completado; viajar mediante respuesta y también trigger; WestLondon con dos NPC, tres enemigos, libro próximo y cámara/liberación; recoger libro y segundo paso; combatir y recompensa; regresar por Contact; entregar libro y quest/500 XP una vez; salir/volver no duplica; save/load en cada mapa y durante progreso; aborto de conversación conserva interacción. Revisar runtime_trace.log después.

No confundir la compilación Codex, los doubles o las capturas de editor con esos resultados. El script de aceptación Qt crea la campaña mediante controles, conserva los generados como salida del build y no ejecuta herramientas antiguas ni el juego.

# Revisión 0.9.11 — animaciones, plano inicial y guardado

La 0.9.10 recibió del usuario «en general todo bastante bien». Esta revisión conserva el recorrido de siete pasos, trece cámaras de diálogo, llave física, journal secuencial, rata opcional, control diferido de conversaciones y temporizador único. No cambia geometría ni fondo de EastLondon.

## Confirmado en archivos originales

- `research/original/Codex.nob/Codex.class`: constantes MOTION_* leídas desde ConstantValue, sin numeración inventada. TALK=117, LISTEN=118, GESTURE3=154, GESTURE10=194.
- `CodexThing.PlayMotionSetMode(int, boolean, float)`, GetPosition/GetOrientation y SetPosition/SetOrientation están en la API real. Java generado se compila contra esas clases, con destino 45.3.
- Los archivos NMS declaran slots y NAD concretos, con flags de reproducción. Se recorren los NOB originales para crear `cache/motions.json`; no se ejecuta un editor original.
- LonCiv1 utiliza LonCivUmbrella.nms, sin la variedad de gestos que necesitamos mostrar. ST_Christof_MD es un actor con hablar, escuchar, reposo y gestos 3/7/8/9/10. La evidencia copiada está en `research/round0/animation_restore_fix/`.

## Confirmado en SDK/documentación

`research/phase7/embrace/cutscene.htm.txt` explica que una conversación aplica TALK al hablante y LISTEN a los demás. Permite sustituirlos con PlayMotionSetMode; los movimientos dependen del NMS. El callback convreached recibe starter, índice EVENT, índice LINE, duración y GUID del hablante. El cuarto argumento no es un GUID.

## Cambios y pruebas de lógica

En formato 9, un nodo admite `motion` y sus líneas pueden sustituirlo. La validación rechaza un movimiento que no esté disponible para el actor de esa línea. El editor ofrece los movimientos comunes cuando un nodo incluye varios personajes. El comportamiento automático sigue siendo el valor inicial. No se añade StopActorMotion: esa llamada causó la regresión de pose en T de una revisión anterior.

El laboratorio usa ST_Christof_MD y separa los movimientos básicos de la página de gestos. Los nombres originales del NAD aparecen en el selector. La película conserva duración, puerta y paseo; su primer plano cambia a ANGULAR_B, LONG, HIGH y transición 0, para evitar interpolar desde la cámara anterior. No se añade una cámara XYZ ni se promete una altura en metros que la API no define.

Se guarda una marca y seis floats para la posición/orientación del jugador local. La recuperación espera un tick, tolera que el jugador aparezca más tarde y evita ejecutar otra llegada por defecto al recibir beginscene después de restore. Una flag de viaje explícito tiene prioridad. Datos no finitos se ignoran; los rechazos del motor tienen un límite de 20 intentos. El fallo se registra y la lógica continúa conservando la posición nativa.

La nueva prueba de carga durante película falló antes de la corrección: cinema se restablecía a -1 y stopCinema no podía cancelar el modo nativo ni el paseo guardado. Se persiste además una marca de película activa y se cancela explícitamente al cargar. Se comprueba también una película sin paseo. Fuera de ese caso, las rutas normales conservan su restauración previa.

Pruebas nuevas: `tests/test_stability_revision.py` y `tests/test_stability_gui.py`. Incluyen orden ENTRY primero en NCO aunque el YAML tenga otro orden, múltiples líneas, callback con duración distinta del GUID, herencia y sustitución de animación, modelos sin el gesto, caché truncada, posición/orientación tras recreación del jugador, llegadas explícitas, fallos finitos, no duplicar premios/actores/quests, cancelación de diálogo/cine y edición/deshacer/guardar/reabrir en Qt. El recorrido completo y el de omisión siguen en test_guided_tutorial.

## Inferido

No se ha demostrado por qué Redemption recoloca al jugador en la partida concreta del usuario. La recreación en una entrada durante carga es una hipótesis; las pruebas simulan esa situación y verifican que nuestro controlador conserva la posición. El plano LONG/HIGH debería dar una vista más clara, pero no demuestra que esté libre de geometría en el motor.

## Pendiente de verificar en Redemption

Partida nueva → lección 3: comprobar vista aérea, duración de doce segundos y recuperación del HUD. Laboratorio → Animaciones: comparar cada movimiento con su nombre y confirmar que no aparecen poses en T. Guardar tras caminar a otro sitio → cargar: comprobar punto y orientación, inventario, flags, progreso y diálogo posterior. Repetir una carga durante película. Verificar colisiones del plano y actor Christof. Ninguna prueba offline confirma estas apariencias.

## Compatibilidad

El contrato incluye `player_pose_record_v1` y `cinema_record_v2`; el build marca cambio de estructura. No hay migrador de saves anteriores. **Iniciar una partida nueva de 0.9.11**. Se conserva el perfil del personaje y las plantillas de objetos que pueda recordar; los archivos originales del juego permanecen sin modificar.

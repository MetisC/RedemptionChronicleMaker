# Revisión 0.9.12 — notas nativas y reposo tras gestos

## Confirmado en archivos originales

- El usuario observa en 0.9.11 que Christof se ve mientras ejecuta un gesto y desaparece al terminar, aunque permanece en la conversación. Es evidencia visual del usuario; no se ha controlado el juego automáticamente.
- `SOC1_DataPrintout1.clicked` invoca `ExecuteText(clicker,0,"SocietyDocument1")`. `CTD_Labyrinth.clicked` usa el GUID del objeto como segundo parámetro. `ItemNodFragment.textended(int)` continúa con una conversación después de cerrar el texto. Bytecode: `research/round0/animation_restore_fix/native_text_bytecode.txt`.
- `Local_Eng.nob/strings/mp_ctd.ntx` define el prólogo con `<TEXT IntroTextCTD none 0>`, `<TITLE ...>`, párrafos `<P 0xFFFFFFFF>` y cierre `</TEXT>`. Los documentos de Londres usan la misma estructura y pueden referenciar una voz. Nuestro generador usa el subconjunto sin voz.
- Christof.nms declara stand y varios gestos noloop. El catálogo conserva los nombres reales de las animaciones y los flags del NMS. No se edita NAD, NMS, geometría ni una plantilla original.

## Confirmado en SDK/documentación

`CodexThing.PlayMotionSetMode(int,boolean,float)` devuelve la duración de la animación en milisegundos, o -1 en caso de error. El booleano elige **motion channel** cuando es true y **action channel** cuando es false. No es un parámetro de bucle. Referencia descargada y conservada: `research/phase7/embrace/CodexThing.htm.decoded.htm`; texto legible en `research/round0/notes_motion/CodexThing.txt`.

La documentación de Codex confirma ExecuteText(ownerGuid,thingGuid,textName); el contrato NMF incluye NTX. Se conserva la documentación en research. La función real se compila contra las clases originales de Codex.

## Inferido

Un NPC con AI pausada puede quedar sin una pose base útil cuando termina la acción noloop. La coincidencia con lo descrito por el usuario hace de esto la causa probable, sin acreditar aún la ejecución visual de la corrección.

## Implementación y comprobaciones

Los overrides explícitos de animación ponen stand en el canal base y el gesto en el canal de acción. Se programa su final usando la duración devuelta por el motor y se restaura stand. Un nuevo callback de línea cancela la devolución anterior, permitiendo la actuación automática del motor; el cierre o aborto del diálogo cancela los timers y restaura reposo. El polling general no interrumpe el gesto. No se llama a StopActorMotion, ni se cambian las flags de los NPC o la actuación automática de conversaciones sin overrides. El validador exige un slot stand en el modelo para poder garantizar la pose base.

`show_note: {title: ..., text: ...}` genera directamente NTX, registrado en el NMF. La escritura y lectura de comprobación soportan nuestro subconjunto: texto sin voz, título, párrafos y flag 0. Se rechazan controles, marcado incrustado, títulos con saltos de línea y texto fuera de Windows-1252. No es un editor de todo el formato NTX original. El empaquetador admite NTX dentro del NOB propio; la prueba de compilación exporta y vuelve a inspeccionar el paquete `.rcmpack` con sus notas.

El evento `object_clicked` identifica su origen con `object`. Puede lanzar una nota, una conversación con un NPC existente u otras acciones. Al seleccionar un objeto, los dos botones de interacción crean el evento y llevan a sus propiedades; si ya existe, lo muestran sin duplicarlo. La conversación mantiene un actor como hablante: no se afirma soporte de un prop como actor hablante o de animaciones faciales de objetos.

ExecuteText mantiene la propiedad de la ventana hasta `textended(owner)`. Mientras está abierta se bloquean nuevas conversaciones y activaciones de eventos muestreados. El cierre se procesa en el siguiente timer, después de la limpieza nativa. `note_closed` permite continuar; usa condiciones de flag si necesitas distinguir varias notas. Un evento admite una sola operación modal: no puede abrir nota y conversación o viaje simultáneamente. La UI de nota es transitoria y no se reabre al cargar una partida.

Pruebas en `test_notes_motion.py` y `test_stability_gui.py`: gramática contrastada con el prólogo original, lectura del paquete y registro NMF, Java 45.3 real, referencias de objetos, renombrado, validación de errores, edición/deshacer/guardar/reabrir, duración y final del gesto, siguiente línea, abortos, actor retirado, ventana repetible, fallo de ExecuteText, callback síncrono y restauración. Los escenarios Java utilizan dobles; la compilación real no acredita comportamiento visual.

Resultado final: **278 tests pasan**, 21 más que 0.9.11. Ruff y las comprobaciones de tipos configuradas pasan. El golden histórico conserva su SHA-256 fijado; no se actualiza la referencia para aceptar un cambio. El recorrido completo y el de omisión del tutorial pasan cerrando primero el prólogo. Informes en `research/round0/notes_motion/final_quality/`. No se vuelve a medir cobertura global en esta revisión.

## Pendiente de verificar en Redemption

Partida nueva de **RCM · Tutorial paso a paso**: cerrar el prólogo, hablar con Christof, dejar terminar un gesto sin pulsar otra respuesta, probar otro gesto, volver y salir. Debe permanecer visible. Elegir «Leer una nota de ejemplo»; comprobar texto, cierre, ratón y nueva conversación. En el paso 5, pulsar el barril antes de hablar con el agente. Las demás lecciones, cámaras, llave y cutscene conservan su configuración.

## Limpieza y acceso

La limpieza elimina sólo builds intermedios, distribuciones anteriores y snapshots generados. Conserva src, herramientas, tests, dos proyectos, recursos de investigación y dependencias necesarias. El informe enumera las rutas y bytes en `research/round0/notes_motion/cleanup.json`. El acceso directo de la raíz apunta al editor actual y a su workspace existente. Los informes finales de pruebas se conservan en research, fuera de build.

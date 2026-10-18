# Producto vigente · 1.0.0-rc6

RCM crea crónicas sobre geometría original inmutable mediante autoría visual, datos propios, formatos generados y Java compilado contra Codex. No ejecuta Embrace, NOT Editor ni otros programas originales de autoría. Se mantienen formatos 9/10 y la versión rc6; no se declara 1.0 final.

## Cierre quirúrgico

La auditoría actual está en research/embrace_closure/FINAL_FLECKS_AUDIT.md. Se revisó HEAD real y se reconfirmaron referencias en el archivo Codex original: PushMusic 55 clases, PopMusic 53 y TeleportPartyToConversation 107. Son referencias de bytecode, no ejecuciones observadas.

- **Música temporal**: Actions normales, pista MP3 válida y volumen 0..100. Usa los métodos reales PushMusic/PopMusic. Codex conserva un único snapshot Java, no una pila anidada. RCM limita propiedad, rechaza Push anidado/Pop ajeno y limpia sólo su snapshot conocido. No inventa persistencia: Restore descarta propiedad transitoria. Start/Stop Music/Ambient se conservan.
- **Conversación nativa**: Automática, Entrada RCM anterior o grupo nativo mediante una a cuatro entradas nombradas existentes. Se reutilizan viewport, transforms, referencias, borrado y undo. Se escribe sólo la tabla demostrada en NSD propio y se llama a TeleportPartyToConversation. Se probaron 99 tablas originales / 473 registros; la formación y diferencias reales en MP requieren observación.
- **NCP estacionario**: PARTIAL. Los 22 pares de posición repetida también repiten parámetro. No demuestran una duración para giro/hold. Se conserva la restricción al escribir, el roundtrip de los 174 originales y el plano fijo de un punto. No se inventa un mínimo de tiempo o distancia.

Sin nueva pestaña, subsistema de música, formato 11, editor de marcadores paralelo ni controles geométricos. Los casos compartidos usan Events/Actions/Sequences/Resources existentes.

## Contenido preservado y ejemplos

Tutorial aceptado «Una carta al amanecer» en formato 9, mini crónica, Dynamic Encounter Lab, fuentes y recursos personales se preservan. El Showcase conserva la historia del libro; sólo se amplía su laboratorio opcional. Arrival at the refuge es una aventura independiente disponible en Ayuda.

Ambos laboratorios muestran puntos nativos para la party, conversación con Elena, cámara, mirada del guardia, gesto, recorrido, travelling propio, audio situado, música dramática temporal, fundido, una rata débil, journal y viaje. La puerta original se oculta y deja paso; no se inventa una animación para una cara fija del NIL. Las puertas con frames/pivote mantienen su soporte acotado.

## Aceptación nativa existente

- El usuario confirmó el tutorial anterior y las reparaciones de hover/clic y primer desplazamiento en su prueba previa.
- El cierre del Taller al cargar se localizó en la escritura nativa CASH (Vampire.exe+0x97c16): varios mapas acumulaban referencias sobre una tabla de tres slots. El generador unifica/deduplica y el gate rechaza desbordamientos.
- El usuario confirmó la carga inicial corregida el 18/10/2026: **«Funciona bien y abre»**. Esa confirmación no certifica los nuevos puntos nativos, música, cine, guardados, reentrada o red.

## Verificación

La suite completa pasó **525 pruebas, 0 fallos, 0 errores y 0 omitidas**. Tras compactar los controles del inspector pasaron otras **140 pruebas de interfaz**, también sin fallos, errores u omisiones. Ruff y el alcance configurado de mypy pasaron. Los resultados autoritativos actuales están en build/tests/quality_report.json y test_report.json; el recibo final del cierre está en research/embrace_closure/final_flecks_delivery.json. Distinguen suite, Ruff/mypy, compilación real Codex **45.3**, doubles, transacciones Qt, paquetes y portable.

Los probes EN/ES con carpeta movida, espacios/unicode y PATH restringido no equivalen a PC independiente, render OpenGL real, GPU o DPI físico. Originales: research/read_only_verification.json, 43 fuentes comprobadas por hash. El código y recursos del juego original permanecen sin modificar fuera de la carpeta RCM autorizada.

## Preguntas de cierre

1. **¿Queda una capacidad material no geométrica necesaria para una crónica normal?** No se ha identificado otro bloqueo material de autoría en los mecanismos auditados. Esto no es una certificación universal de cada opción de Embrace ni de toda su API.
2. **¿Qué limitación no geométrica concreta queda?** Crear giros NCP estacionarios temporizados sigue PARTIAL: no existe una regla de duración suficientemente demostrada. Se mantienen además los límites explícitos de codec NSD/NOT, planos sin FOV por key, puertas no universales y snapshot musical transitorio. No se anuncian como funciones completas.
3. **¿Qué significa cobertura?** El flujo normal permite construir la escena de aceptación desde la UI, sin Java/NCP manuales ni herramientas originales. IMPLEMENTED y OFFLINE VERIFIED no equivalen a RUNTIME VERIFIED. No se afirma 100 % de paridad ni 100 % de comportamiento nativo verificado.
4. **¿Qué pruebas manuales quedan?** EMB01–24, DYN01–12 y EMB-MUSIC-01..03, EMB-CONV-01..05 y EMB-NCP-01..05. Incluyen framing/clipping, party/colisión/MP, cancelación, música/save/load/travel, reentrada, WTD y PC/GPU/DPI independiente. La carga inicial aceptada sólo acredita esa parte de LOAD-META-01.
5. **¿Qué se entrega?** Editor portable EN/ES, ejemplos, generadores y paquetes propios, compilación 45.3 y evidencia diferenciada de integridad y pruebas. La suite completa es 525/0/0/0 y la regresión posterior de widgets 140/0/0/0. El recibo conserva hashes y alcance de cada verificación.

La geometría, CSG, UV/texturizado estructural, lightmaps y edición estructural de sectores/portales siguen fuera de alcance. No se inicia otra fase ni se buscan nuevas APIs por curiosidad.

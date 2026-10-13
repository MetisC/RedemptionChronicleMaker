# Revisión de Fase 1

**Resultado: núcleo y crónica generada/compilada; el usuario confirmó nombre, mapa, desaparición del halo, NPC próximo, diálogo y elecciones recordadas en interacciones posteriores.** Las referencias originales muestran gris; revisión 5 recupera sus metadatos de entorno sin cielo añadido. La comprobación visual de esa demo, save/load y red siguen pendientes. No se ha iniciado Fase 2 ni usado herramientas originales de autoría.

## 1. Qué hace actualmente el sistema

Analiza la instalación, extrae evidencia, descubre niveles/recursos, lee YAML seguro, valida referencias y genera archivos de crónica y Java propio. Produce un paquete con dos conversaciones de dos respuestas, creación dinámica de un NPC, posición/orientación y comportamiento posterior condicionado por un Chronicle Flag. Guarda/revincula GUIDs mediante callbacks y evita creación duplicada en la lógica generada.

El esquema también admite varios actores y objetos sencillos derivados de plantillas, con spawns al inicio; la demostración y el harness se centran en Victoria.

## 2. Qué recursos originales reutiliza

Referencia l1_east.nil, UI/strings del mapa, currency y businessWoman, con sus recursos visuales. La revisión 5 conserva los campos originales de fondo vacíos, retirando los modelos experimentales añadidos en revisiones anteriores. Conserva metadatos originales de música/ambiente y campos aún no interpretados. Usa Codex y classes.zip para compilar.

Los catálogos contienen 112 geometrías, 130 nombres de ubicación originales, 2.619 registros NOT, 291 escenas, 310 conversaciones, 136 AI, 45 quests, 18 definiciones de jugador, 174 paths de cámara y recursos visuales/audio. Se preservan las referencias fallidas y los nombres ambiguos. La disponibilidad en catálogo no demuestra que cada recurso haya sido instanciado.

## 3. Qué puede añadirse sin tocar geometría

El generador añade actores y objetos con identidad propia, transforms, lógica de escena, conversaciones, decisiones y flags. La API original además presenta vías para inventarios, efectos, quests, audio, cámaras, teletransportes y conexiones de exits. Estas últimas capacidades están investigadas y documentadas, pero todavía no se ofrecen como acciones completas del esquema 1.

No se puede convertir cualquier pared en puerta ni alterar la topología NIL. La creación de regiones de forma arbitraria y algunas entidades con bloques geométricos NSD requieren codecs adicionales.

## 4. Qué genera directamente

`.nsc`, `.nmf`, `.nco`, `.nvo`, `.nls`, `.not`, NSD simple, Java, classfiles 45.3, WAV y contenedores NOB/ZIP. El escritor NOT preserva tags desconocidos; se ha contrastado con cuatro archivos originales. NSD se limita a registros sin parámetros/meshes/frames. No se generan NIL ni modelos NOD nuevos.

## 5. Qué controla del runtime

El Java entregado llama funciones reales de creación, identificación y flags de entidades; pausa la AI del actor y habilita interacción; captura clics; ejecuta conversaciones; lee/escribe Chronicle Flags; prepara/libera cámara; guarda/restaura GUIDs. Las firmas se validaron compilando contra Codex real, y los callbacks se contrastaron con scripts originales y registro de callbacks del ejecutable.

La compilación verifica nombres/tipos, no los efectos nativos ni las condiciones de carga.

## 6. Qué está probado

- 26 pruebas automatizadas de formatos, esquema, referencias, protección de rutas, paquetes y Java generado; incluyen NLS de carga automática, fondo y modos de colocación.
- Reproducción byte a byte de los cuatro NOT y de 24 NSD originales del subconjunto soportado.
- Generación y compilación real a 45.3 con ECJ y biblioteca/API originales.
- 20 comprobaciones de lógica Java con un motor simulado: espera del jugador, proximidad, orientación, spawn único, conversación, decisiones, aborto, restore y errores. La collision real no está simulada.
- Paquetes sin geometría original; NCO/NVO/plantilla/Cast ID coherentes.
- Hashes de 43 fuentes originales comparados. El alcance preciso figura en `research/read_only_verification.json`.

Los doubles del harness están en `tests/java/`; sus clases no se empaquetan como runtime ni sustituyen a Codex en el build entregado.

## 7. Qué falta probar dentro del juego

El usuario confirmó en la revisión 3: nombre correcto, mapa cargado, halo desaparecido, Victoria visible junto al jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara de diálogo se percibe algo baja. Save/load y replicación en red no se han probado.

Pendientes: nuevo fondo Sky, save/load sin duplicación, aborto de diálogo, orientación/unidades y colocación absoluta, repetición del ciclo de escenas y red. El circuito básico de creación/interacción/decisión tiene confirmación del usuario, además del log nativo.

## 8. Qué formatos siguen incompletos

NIL interno, NSD complejo, semántica completa de tags NOT, 6.786 bytes no indexados de Multiplayer.not, NOD/NAD y otros recursos gráficos, NCP y auxiliares. Los formatos textuales de quests/AI/personajes/tiendas se han inspeccionado, pero no tienen generadores completos ni validación semántica nativa.

## 9. Limitaciones actuales

Una ubicación por crónica; requiere anchor estudiado. NPCs pausados/neutrales. Una conversación simultánea por controlador. Texto Windows-1252 y audio silencioso. Flags limitados por política de autoría. Metadatos de entorno parcialmente interpretados; fondo referenciado explícitamente. Sin navegación ni preview 3D. SpawnThingNear delega collision al motor; colocación absoluta disponible, sin validación contra la malla.

No hay catálogo manual obligatorio, GUI, herramientas de modelado, editor de geometría, launcher o installer.

## 10. Fase 2 propuesta

Primero cerrar la prueba nativa con este mismo ejemplo y registrar todos los contratos de carga. Después ampliar codecs/capacidades concretas: regiones, eventos/timers, múltiples escenas, quests, inventarios y cámaras/audio. Solo tras ese contrato estable conviene diseñar el editor visual de capas. La geometría seguiría siendo una referencia inmutable. Detalle y prioridades en `ROADMAP.md`; no se ha empezado ninguna de esas ampliaciones.

## Historial: revisión 3 tras el segundo ensayo

El usuario confirmó el nombre correcto, pero la revisión anterior no solucionó el NPC al inicio ni el fondo/halo. La revisión 3 añade `NOT R_east_demo.not` al NMF para cargar nuestra biblioteca explícitamente y conserva `LOCATION_FLAG_CLEARBUFFER` de la referencia original (EastLondon: `0x60`, antes `0x20`). Mantiene el spawn cercano y los recursos LondonNightSky. Añade un registro generado por el juego en `RCM/east_demo/runtime_trace.log`, para comprobar construcción de la clase, callback de inicio, jugador y GUID de spawn. El archivo solo se escribe dentro de RCM usando el directorio de trabajo habitual. La compilación 45.3 y las 26 pruebas pasan; el resultado visual sigue pendiente. No se considera que el cielo o el NPC hayan sido demostrados por los tests con doubles. Detalles en ENGINE_NOTES.md y TEST_PLAN.md.

## Estado actual: fondo, revisión 4

El usuario confirmó en la revisión 3: nombre correcto, mapa cargado, halo desaparecido, Victoria visible junto al jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara de diálogo se percibe algo baja. Save/load y replicación en red no se han probado.

La revisión 4 cambia únicamente los dos nombres de fondo del NSD: LondonNightSky → Sky, un recurso original con estrellas, luna, nubes y forma de skyline. No se afirma que reproduzca el fondo exacto de EastLondon. Java, NPC, diálogo, flags y demás bytes de escena son idénticos a la revisión 3. Su resultado visual cerca del muelle sigue pendiente. Investigación: research/sky/FINDINGS.md; estado: research/runtime_test/revision4_status.json.

## Seguimiento: Sky visible pero inadecuado; comparación directa

El usuario probó la revisión 4: ve estrellas, pero percibe el fondo enorme y de aparición brusca, sin el horizonte de muelle esperado. Esto verifica dibujo del cielo añadido; no acredita escala correcta ni un recurso faltante. La demo permanece igual. Se añadieron dos crónicas de diagnóstico en un NOB separado dentro de RCM/east_demo: mapa base original (null) y escena original (EAST_28_1.nsd), ambas con EastLondon como ubicación única y revive entrada 0. MP_London_Null comienza en WestLondon y London de historia en SocietyOfLeopold3; esto explica por qué las partidas oficiales no sirven como comparación inmediata. La coincidencia visual del punto de entrada y el fondo de las referencias siguen pendientes de observar. Procedimiento en docs/EASTLONDON_COMPARISON.md; paquete/manifiesto en build/diagnostics/east_compare y estado en research/runtime_test/east_comparison_status.json. Sin nuevo cambio de cielo, geometría, NPC o Java; sin autoría antigua ni Fase 2.

## Resultado de la comparación y revisión 5

El usuario confirmó que ambas comparaciones de EastLondon —mapa base con escena null y escena original EAST_28_1— muestran un fondo gris que considera adecuado. No se requiere añadir Sky para reproducir ese aspecto. La demo de revisión 5 omite level.sky y conserva íntegros los 176 bytes originales del entorno; los dos campos finales de modelo/animación están vacíos. Solo se eliminan las dos referencias añadidas; NPC, conversaciones, flags, Java y demás bytes de escena permanecen idénticos. Su aspecto final aún necesita comprobarse en una partida nueva de la demo.

Evidencia nativa aportada por el usuario: gris en ambas referencias. Evidencia estática: campos finales vacíos en los NSD originales y copia exacta de sus metadatos en la demo. La necesidad de un skybox extra queda descartada para este caso; no se generaliza a otros niveles. Los modelos añadidos en revisiones 3/4 fueron elecciones experimentales y no la configuración original de EastLondon. Estado y despliegue: research/runtime_test/revision5_status.json y deployment_revision5_2026_10_08.json. Se mantienen CLEARBUFFER y las correcciones funcionales de revisión 3. Las 26 pruebas pasan; save/load, red, aborto y ajuste de cámara siguen pendientes.

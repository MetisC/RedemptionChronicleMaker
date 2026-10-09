# Fondo: investigación y revisión 4, 8 de octubre de 2026

Reproducible con `tools/research_sky.py`; fuente principal Resource.nob y copia de Vampire.exe. Ninguna herramienta original ejecutada, ningún NIL modificado.

## Confirmado en archivos originales

- El lector NSD v8 termina leyendo nombres de modelo/animación de 32 bytes (`0x4a82a2`, `0x4a82db`). El renderer `0x420210` usa el modelo de la escena actual (`+0x94`), o la escena base si no hay escena actual. Si la escena actual existe pero su modelo está vacío, no busca el modelo de la base.
- El renderer coloca el cielo alrededor de la cámara y usa un alcance de 100000 durante ese dibujo. Por ello el fondo es un recurso de escena independiente de la geometría NIL.
- Los NSD de EastLondon examinados (`l1_east`, `EAST_28_1`, `EAST_28_4`, `EAST_30_1`, `EAST_32_1`) no nombran un cielo en esos campos. No hay una referencia directa que permita afirmar cuál era el fondo recordado por el usuario.
- `LondonNightSky.nod` v7: tres materiales (`highLevelCloudsLondon`, `wispyCloudsNight`, `fogLine`) y tres nombres de formas: nubes y línea de niebla. No contiene material StarField ni forma de luna/skyline.
- `Sky.nod` v7: cuatro materiales (`clouds1`, `moon`, `StarField2`, `dfltMatte`) y formas `a_SkyShape1`, `b_MoonShape`, `c_CloudLayerShape`, `d_SkylineShape`. `Sky.nad` existe. Escenas originales como CTDY_4_1, FLS1_40_1 y N1_FLS1 lo referencian.
- `newYorkDocks` contiene estrellas, luna y silueta de Nueva York (Empire State, World Trade Center, Estatua de la Libertad). Se ha examinado como contraste; no se ha elegido para la crónica de Londres.

## Confirmado en SDK/documentación

No se encontró especificación oficial adicional del sky ni de NOD/NAD en la instalación.

## Inferido

La selección anterior de LondonNightSky aporta capas de nubes/niebla, pero carece de elementos de fondo que sí contiene Sky. Eso puede explicar el fondo incompleto descrito. No demuestra por sí solo que sea la única causa de la zona azul.

Se elige Sky como fondo nocturno completo reutilizado del juego, sin afirmar que sea el fondo exacto de EastLondon. Es una elección explícita de nuestra escena, no una copia certificada del aspecto original.

## Pendiente de verificar

El aspecto nativo de Sky en EastLondon, especialmente cerca del muelle. Si continúa vacío, investigar visibilidad/portales y rendering en esa posición; no cambiar NIL ni reemplazar recursos a ciegas. También sigue pendiente identificar qué mapa oficial recuerda el usuario.

## Observado por el usuario

Revisión 3: halo desaparecido, Victoria visible, conversación a pantalla completa correcta y elecciones recordadas en las siguientes interacciones. Cámara algo baja. Esto no verifica todavía save/load o replicación en red. Log nativo preservado en `research/runtime_test/native_revision3_accepted.log`.

## Cambio acotado

Revisión 4 sustituye únicamente los dos nombres finales de cielo por Sky. Comparación con la revisión 3 instalada: los demás bytes del NSD, los demás miembros del NOB y ambas clases son idénticos. El registro Java sigue diciendo revisión 3 porque el controlador no cambió. El estado y despliegue del paquete se registran por separado en runtime_test.

Las ventanas iniciales native_loader.txt/native_world_sky.txt investigaban serialización de modelos de Thing; no acreditan un cielo incrustado en NIL. Esa hipótesis se descartó. El archivo reproducible native_evidence.txt contiene las funciones pertinentes.

## Seguimiento: Sky visible pero inadecuado; comparación directa

El usuario probó la revisión 4: ve estrellas, pero percibe el fondo enorme y de aparición brusca, sin el horizonte de muelle esperado. Esto verifica dibujo del cielo añadido; no acredita escala correcta ni un recurso faltante. La demo permanece igual. Se añadieron dos crónicas de diagnóstico en un NOB separado dentro de RCM/east_demo: mapa base original (null) y escena original (EAST_28_1.nsd), ambas con EastLondon como ubicación única y revive entrada 0. MP_London_Null comienza en WestLondon y London de historia en SocietyOfLeopold3; esto explica por qué las partidas oficiales no sirven como comparación inmediata. La coincidencia visual del punto de entrada y el fondo de las referencias siguen pendientes de observar. Procedimiento en docs/EASTLONDON_COMPARISON.md; paquete/manifiesto en build/diagnostics/east_compare y estado en research/runtime_test/east_comparison_status.json. Sin nuevo cambio de cielo, geometría, NPC o Java; sin autoría antigua ni Fase 2.

## Resultado de la comparación y revisión 5

El usuario confirmó que ambas comparaciones de EastLondon —mapa base con escena null y escena original EAST_28_1— muestran un fondo gris que considera adecuado. No se requiere añadir Sky para reproducir ese aspecto. La demo de revisión 5 omite level.sky y conserva íntegros los 176 bytes originales del entorno; los dos campos finales de modelo/animación están vacíos. Solo se eliminan las dos referencias añadidas; NPC, conversaciones, flags, Java y demás bytes de escena permanecen idénticos. Su aspecto final aún necesita comprobarse en una partida nueva de la demo.

Evidencia nativa aportada por el usuario: gris en ambas referencias. Evidencia estática: campos finales vacíos en los NSD originales y copia exacta de sus metadatos en la demo. La necesidad de un skybox extra queda descartada para este caso; no se generaliza a otros niveles. Los modelos añadidos en revisiones 3/4 fueron elecciones experimentales y no la configuración original de EastLondon. Estado y despliegue: research/runtime_test/revision5_status.json y deployment_revision5_2026_10_08.json. Se mantienen CLEARBUFFER y las correcciones funcionales de revisión 3. Las 26 pruebas pasan; save/load, red, aborto y ajuste de cámara siguen pendientes.

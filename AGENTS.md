# Instrucciones del proyecto

## Autoría y alcance

- Petición vigente: ejecutar Fase 9 según docs/PHASE9_PLAN.md, sumando la auditoría externa íntegra en docs/AUTHORING_AUDIT_REQUIREMENTS.md. La auditoría previa y baseline quedan en docs/AUTHORING_GAP_AUDIT.md y research/phase9/. No reimplementar capacidades correctas. Priorizar P0 nativo (diálogo, persistencia, reentrada, NOT), P1 entradas/puertas/exits/static/paths/portable y recorrido GUI. Multijugador no bloquea una beta local explícitamente limitada; conservar estado pendiente de red. Generado, compilado y verificado en motor son estados distintos. Esta petición posterior prevalece sobre los límites históricos de numeración de fases. No ejecutar herramientas originales de autoría ni alterar geometría.

- Petición actual: Fase 7 de estabilización, autorizada expresamente después de Fase 6. Analizar Embrace/SDK original como referencia de funciones, especialmente scenes, sin convertirlo en dependencia ni ejecutarlo para autoría. Descargar y extraer documentación/recursos de investigación sólo dentro del workspace. Priorizar scene/environment, entradas y estabilidad del flujo, sin editar geometría. Los bloqueos nativos de Fase 6 no quedan aceptados por cambiar de fase.

- Redemption Chronicle Maker genera sus propios formatos y Java mediante API real del motor. Ninguna herramienta original de autoría forma parte del flujo; no ejecutar Embrace, NOT Editor ni editores/frontends originales.
- La petición actual docs/PHASE6_REQUIREMENTS.md autoriza Fase 6: auditoría, estabilización, pruebas y cobertura de huecos críticos sobre el editor existente. Prevalece sobre las prohibiciones históricas de Fase 6. Geometría original inmutable. No empezar Fase 7. No declarar el writer NOT estable sin ensayo nativo; preservar campos desconocidos. La Fase 5 quedó parcialmente implementada; comprobar estado real y no asumir completa por la introducción del nuevo encargo.
- Código, fuentes, investigación, builds, pruebas y documentación permanecen en este workspace.

## Instalación del juego: autorización actual para RCM

Tras la entrega de Fase 2, el usuario vuelve a autorizar expresamente: «Puedes y debes cambiar lo que sea necesario de la carpeta RCM para poder probarlo». Esta instrucción posterior prevalece sobre el solo lectura del prompt de Fase 2 exclusivamente para `H:\GOG\Vampire The Masquerade - Redemption\RCM`.

Se pueden actualizar allí nuestros paquetes y clases para el ensayo, sin pedir de nuevo permiso. Preservar lo sustituido en el workspace, verificar rutas resueltas y enlaces antes de escribir/borrar/mover, y comprobar que Vampire esté cerrado antes de reemplazar recursos cargados. Ningún archivo del juego fuera de RCM puede modificarse. Los generadores/editor continúan escribiendo sus salidas en el workspace; esta autorización permite el despliegue puntual de los builds, no introduce instalador ni Fase 4.

## Historial de la excepción anterior

En Fase 1 el usuario autorizó manipular únicamente RCM. El prompt de Fase 2 suspendió el despliegue automático y se respetó durante su entrega. La nueva petición posterior vuelve a habilitar RCM para preparar la prueba.

## Evidencia

Separar compilación, tests con doubles, análisis estático y resultados observados en el juego. El usuario confirmó en revisión 3 nombre, mapa, halo desaparecido, Victoria cerca del jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara se percibe algo baja. Save/load, abortos y replicación en red siguen sin comprobarse.

El usuario confirmó que ambas comparaciones de EastLondon —mapa base con escena null y escena original EAST_28_1— muestran un fondo gris que considera adecuado. No se requiere añadir Sky para reproducir ese aspecto. La demo de revisión 5 omite level.sky y conserva íntegros los 176 bytes originales del entorno; los dos campos finales de modelo/animación están vacíos. Solo se eliminan las dos referencias añadidas; NPC, conversaciones, flags, Java y demás bytes de escena permanecen idénticos. Su aspecto final aún necesita comprobarse en una partida nueva de la demo.

Las revisiones 3/4 añadían LondonNightSky/Sky experimentalmente; no eran el fondo original. No reintroducirlos como supuesta reparación del muelle sin otra petición/evidencia. Las dos comparaciones permanecen en east_compare.nob para investigación, separadas de la demo. Investigación: research/sky/FINDINGS.md y docs/EASTLONDON_COMPARISON.md; estado actual: research/runtime_test/revision5_status.json. El juego genera RCM/east_demo/runtime_trace.log; build/tests contiene logs del motor simulado. Sin herramientas originales de autoría. Restricción histórica anterior; la petición posterior autoriza Fase 3.

## Confirmación nativa de Fase 2 y revisión del editor

El usuario confirmó «Va perfecto» para la crónica editor_playtest desplegada, aclarando que no ha probado personalmente el editor. Su declaración y log nativo están en research/runtime_test/phase2_native_acceptance.json y native_phase2_accepted.log. Esto acepta la prueba general, no acredita individualmente save/load, abortos, XYZ/collision ni red. La orden «continúa» se aplica a terminar/revisar Fase 2; no empezar Fase 3 sin otra petición explícita (recibida posteriormente y documentada abajo).

## Alcance actual: Fase 3

El usuario solicita expresamente docs/PHASE3_REQUIREMENTS.md. Prevalece sobre las prohibiciones históricas de Fase 3 anteriores. Implementar viewport texturizado y autoría espacial sobre el modelo existente, conservando CLI/build; no Fase 4.

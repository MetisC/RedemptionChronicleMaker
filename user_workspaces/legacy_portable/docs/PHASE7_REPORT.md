# Fase 7 — estabilización técnica 0.7.0

Se ha realizado una revisión documental de Embrace original y una estabilización acotada del editor/backend. El trabajo, demo, pruebas, portable e investigación permanecen en este workspace. **No se declara completada la aceptación nativa ni lista la beta privada.** B1–B5 continúan abiertos; no se ha empezado Fase 8.

## Investigación original

Se recuperaron el manual original de Embrace, especificaciones NIL/NSC/NSL/NSS/NMF y contratos de cámara, secuencia y audio desde copias archivadas del SDK. Se conserva también la documentación original de cutscenes. Cada descarga tiene URL, fecha, bytes y SHA-256; respuestas gzip se conservan junto a sus copias decodificadas. No se ejecutó Embrace ni se instaló el SDK. No se obtuvo su binario: los mirrors del ZIP fallaron. El análisis de la interfaz procede del manual, no de manipular la aplicación.

La [comparación funcional](EMBRACE_COMPARISON.md) identifica scenes, estática, capas, ambiente, niebla/recorte, cielo, entradas, Codex Linker, paths, luces/sonidos y puertas. Distingue capacidad runtime, autoría pendiente y funciones de geometría fuera de alcance. La iluminación y las superficies Sky del NIL no se pueden sustituir simplemente cambiando el entorno NSD.

## Cambios entregados

- Selector **Entorno original** en propiedades de Level base, por escena de campaña. Nuevo campo opcional `level.environment_scene`, roundtrip, deshacer/rehacer y limpieza al cambiar de geometría. Los proyectos sin campo mantienen su salida anterior.
- Catálogo automático: 130 locations/levels lógicos, 127 asociaciones de estática; 264 referencias de perfiles, **263 utilizables y 1 no disponible**. La referencia ausente es `EastGateNight → EGAT_7_1.nsd`. Se muestra error y se bloquea su selección para build; no se inventa el recurso.
- Corrección del scanner: `.NSS` contiene selecciones del Narrador y claves NLS, no nombres NSD ni índices de location. Ahora se asocian perfiles iniciales por NSC y estáticas por la pareja documentada NIL/NSD. Hay 45 enlaces literales adicionales en Codex guardados como investigación, sin importar automáticamente asociaciones incompletas.
- Reutilización directa y verificada de los 176 bytes de entorno NSD versión 8. Cielo conservado; campos inciertos opacos; entidades originales no importadas en nuestro NSD. Anchor independiente de la elección de entorno. La estática base que carga el juego puede conservar objetos originales.
- Hash/version/asociación inválidos bloquean validación/build. Los fingerprints cubren los NSD de entorno utilizados, además de YAML/archivos propios. Informe de build con procedencia y hashes por escena.
- Versión central `rcm.__version__` para diagnósticos y compatibilidad de paquetes, en lugar de cifras fijadas por separado. Corrección del texto del inspector que todavía declaraba un solo level por proyecto.
- Demo **Londres: prueba de estabilización**, ID `rcm_stable`: tres escenas sobre EastLondon/WestLondon. Mantiene diálogos, quests, libro, encuentro y cámaras de la fixture de Fase 6, añade un regreso con un testigo diferente sobre la misma geometría oriental y comparte el flag de alianza. Los tres perfiles son explícitos; no añade skyboxes.

## Verificación

**188 tests pasan**, sin fallos, errores ni skips. Incluyen 14 pruebas nuevas de escenas/perfiles/GUI/compatibilidad. Ruff pasa y mypy pasa para los tres módulos incluidos en su alcance; no se atribuye tipado completo a todo el programa. Cobertura global de líneas/ramas: 68%; `scene_profiles`: 95%. Reportes completos en `build/tests/`.

El paquete histórico de aceptación conserva exactamente el SHA-256 `90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab`. Los tests conservan también la fixture golden fijada de Fase 6; no se actualizó su expectativa para aceptar una regresión.

La demo compila siete clases contra Codex real, todas en versión **45.3**. NOB y `.rcmpack` se verifican con los lectores propios. No contienen NIL ni geometría reescrita. Esto comprueba contratos/formato/compilación, no ejecución del motor.

El portable actualizado se reconstruyó y abrió con un workspace nuevo y PATH limitado a Windows. Escaneó los originales, abrió la demo de tres escenas, creó un viewport OpenGL real y compiló las siete clases 45.3. Smoke: 9,36 s para carga/build una vez iniciado el editor. No faltan símbolos en la comprobación de imports de DLL incluidos. **Es un ensayo local, no un equipo/VM limpio independiente.** Evidencia en `research/phase7/portable_probe.json` y `build/phase7_portable_probe/`.

Los **43 archivos originales** registrados conservaron sus hashes antes y después del deploy. La demo se añadió a `H:\GOG\Vampire The Masquerade - Redemption\RCM\east_demo`, con Vampire cerrado, backup previo y comprobación de rutas. El acceso del escritorio no se cambió. La demo anterior permanece disponible. Informe `research/phase7/deployment.json`.

## Cómo revisarlo

Editor: `build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe` o `python editor.py chronicles/phase7_demo/project.yaml`. Conservar toda la carpeta portable. Fuente: `chronicles/phase7_demo/project.yaml`. Paquete: `build/rcm_stable/rcm_stable.rcmpack`. Usar el acceso habitual del escritorio y **Multiplayer → New Game → Londres: prueba de estabilización**. [Recorrido de prueba](PHASE7_PLAYTEST.md).

## Qué sigue pendiente

Esta revisión no inició una partida dentro de Redemption. Rechazo/aborto de diálogo, liberación de cámara/cursor, save/load, NOT/AI, recogida de libro/quest/recompensa, colisión, reentrada y host/client siguen **NOT TESTED** para esta versión. La evidencia histórica del usuario no se transfiere a ella. No repetir el fallo anterior de llamar “funciona” a una compilación.

Fog/ZClip/EAX individuales, entradas distintas de 0, sustitución de estática base, paths/interestspots, parámetros genéricos de scripts, luces/sonidos espaciales y puertas siguen pendientes. Writer NSD complejo y NOT/AI completos tampoco quedan resueltos por esta fase. [SCENE_MODEL.md](SCENE_MODEL.md) documenta los límites precisos.

El siguiente trabajo de estabilización debe cerrar primero la prueba nativa de esta demo y los bloqueos críticos B1/B2. Después podrá ampliar campos de entorno y entradas mediante formatos comprobados. No es una autorización para empezar Fase 8 ni para alterar geometría.

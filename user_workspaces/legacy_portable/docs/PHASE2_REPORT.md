# Informe de Fase 2 — 8 de octubre de 2026

La entrega convierte el pipeline funcional de Fase 1 en un editor propio de proyectos, actores, narrativa y eventos. El YAML y los generadores existentes siguen siendo la fuente y el backend. Fase 3 no iniciada.

## IMPLEMENTADO

- Editor Python/PySide6 con widgets Qt estándar: árbol de proyecto, contenido central, propiedades y Problems/Build Log. Atajos de proyecto y F5.
- Nueva crónica, abrir, guardar/guardar como dentro del workspace, cambios visibles, guardado atómico, recuperación periódica y protección al cerrar con cambios.
- Resource Browser real con búsqueda/filtro: levels con NIL/escenas/procedencia, templates de actores, ítems, modelos, escenas y AI. Selección bloqueada para levels no estudiados y plantillas ambiguas.
- Actores: ID/nombre/notas, template real, colocación junto al jugador o XYZ, orientación pitch/roll/yaw, spawn de inicio, conversación simple o selección según flag. Sin propiedades ficticias.
- Conversaciones en árbol: entrada, nodos, varias líneas/speakers, respuestas, GOTO y RETURN, renombre, eliminación y orden. Generación directa NCO/NVO.
- Flags por alias/índice; eventos Scene Start, Actor Clicked y Conversation Ended con condiciones booleanas y acciones spawn/start conversation/set/clear flag.
- API `Backend.validate/build` común a GUI y CLI, sin Qt en el backend. Build en QThread con snapshot del fuente, progreso y mensajes de error.
- Corrección del título de entrada: NLS propio traduce claves S/L del NSD con el nombre de la crónica o `level.name`. No cambia la escena/clases de Fase 1.

Archivos principales: `editor.py`, `src/rcm/editor/`, `src/rcm/service.py`, `src/rcm/document.py`, extensiones de `model.py`/`generator.py`, `requirements-editor.txt` y dependencias opcionales en `pyproject.toml`. Guía: `docs/EDITOR_GUIDE.md`.

## PROBADO

Antes de editar: 26 tests y build de Fase 1 correctos. Sin repositorio Git preexistente, se guardó `research/checkpoints/phase1_stable_2026_10_08.zip` con hash e informe de baseline.

Al finalizar:

- **64 tests pasan**, conservando los 26 originales. Cobertura añadida para round-trip, serialización, actor editable, referencias, flags, grafos, errores, guardado atómico con fallo simulado, recuperación, renombres y build API/CLI.
- **20 escenarios Java de Fase 1 + 13 de eventos nuevos** pasan usando doubles. Comprueban decisiones, guards, abortos simulados, resultados desconocidos, condiciones y spawn condicionado con espera. No prueban el motor nativo ni su lector NCO.
- Aceptación creada mediante **controles reales de Qt** con QtTest, incluidos Nueva crónica, Resource Dialogs, propiedades, árbol, respuestas, eventos, Validar y BuildWorker. Su YAML no fue escrito a mano.
- Proyecto: `chronicles/editor_acceptance/project.yaml`, ID `editor_demo`, nombre **RCM: Victoria y el pacto de Londres**. EastLondon, Victoria/businessWoman, XYZ `[1016,-54,0]`, yaw 180, conversación `intro` con bifurcación a `identity`, `ally` como saludo alternativo y Chronicle Flag `alliance` índice 1.
- Paquete: `build/editor_demo/editor_demo_distribution.zip`, clases 45.3 compiladas contra Codex original. Build desde GUI y CLI idéntico por SHA-256: `90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab`.
- Rebuild de Fase 1: 11 archivos runtime comparados con checkpoint; 10 idénticos. Solo cambia `strings/_R_east_demo.nls` para traducir los títulos S/L. Ambas clases y NSD idénticos byte a byte.
- Revisión visual de capturas: texto legible, propiedades sin corte horizontal y conversación/eventos/catalogue accesibles con widgets estándar. Capturas finales en `build/editor/acceptance/`.
- 43 fuentes originales verificadas: hashes coinciden. No se escribió en la instalación del juego, incluida RCM, durante Fase 2.

Evidencia persistida: `build/tests/tests.log`, `test_report.json`, `runtime_harness.log`, `event_harness.log`, `build/editor/acceptance/report.json`, `build/editor/phase2_verification.json` y `research/read_only_verification.json`. La compilación contiene el warning conocido de `PrintStream(OutputStream)` del entorno Java antiguo; no hay errores. La INFO de posición absoluta recuerda la comprobación de suelo/colisión pendiente.

## PROBADO DENTRO DE REDEMPTION

**Histórico de Fase 1, confirmado por el usuario:** crónica visible con nombre correcto, mapa cargado, Victoria cerca del inicio, conversación completa con elecciones, estado recordado al volver a hablar, halo eliminado y fondo original gris considerado correcto.

Tras el despliegue de la variante cercana al jugador, el usuario confirma: «Va perfecto. No he probado el editor aún, comprobado que funciona, continúa». Se registra como aceptación general de la crónica nueva dentro de Redemption. El log nativo conserva construcción del controlador, beginscene y SpawnThingNear con GUID 1073741889. No se atribuye al usuario una prueba detallada de cada callback o de save/load/abortos/red.

## NO PROBADO DENTRO DEL JUEGO

Save/load, abortos reales, replicación con otro cliente, varias líneas/hablantes, creación con XYZ y collision. La crónica cercana con bifurcación y estado tiene aceptación general del usuario; no hay un registro desglosado de cada elección o callback. El editor aún no tiene ensayo personal del usuario, aunque su recorrido completo y regresiones pasan con QtTest.

El entorno no ofrece control nativo de la aplicación para verificar esa partida. La prueba nativa aportada procede del usuario y se mantiene separada de los harnesses y de las pruebas Qt. Para la prueba rápida puede cambiarse Victoria a **Junto al jugador** desde el editor y reconstruir.

## LIMITACIONES ACTUALES

- Un único level por proyecto; catálogo de recursos no equivale a disponibilidad probada en todos los mapas. Solo se construyen levels con geometría inequívoca y anchor de escena estudiado.
- Sin visor 3D ni colocación con ratón. Las coordenadas son números validados; la colisión es una propiedad del motor que aún debe ensayarse.
- Configuración neutral de actores conservadora. No editor de clan, health, inventario, AI o NOT completo. Objetos existentes son editables, pero la superficie de creación está centrada en el NPC.
- Tres callbacks de eventos. No Actor Killed, Timer de autoría, regiones, remove actor, puertas, teleports, cambios de escena o quests configurables.
- Acciones de flags preceden al inicio de conversación y al spawn diferido; no existe un intérprete visual general de órdenes arbitrarias.
- Máximo conservador 0..255 para flags, IDs runtime de 31 bytes, hasta 64 nodos/64 líneas por nodo/8 respuestas y RETURN 1..32767 único por conversación. Textos del motor Windows-1252 y sin saltos de párrafo; notas internas UTF-8 libres.
- La cámara conserva SetupCutscene de Fase 1; el ángulo algo bajo no se modifica sin ensayo nativo.
- Sin undo/redo, bloqueo entre procesos, instalación automática, launcher ni ejecutable empaquetado. Autosave es protección básica, no historial.
- El editor no despliega automáticamente. Los paquetes de RCM sí se actualizaron mediante la autorización posterior, exclusivamente dentro de esa carpeta.

## DEUDA TÉCNICA

El parser existente informa el primer error estructural; el servicio añade warnings/INFO cuando el modelo se puede formar. La navegación de errores es contextual y conservadora, no una ubicación completa para cada caso. Queda mejorar esa cobertura y agrupar errores independientes.

La GUI conserva borradores semánticamente inválidos en el mismo esquema, rechazando estructuras corruptas antes de crear widgets. Los controles usan diccionarios del fuente; el modelo tipado se reconstruye al validar. Esto mantiene compatibilidad y evita duplicar el esquema, pero necesita una capa de comandos para undo/redo futuro.

Persistencia de GUIDs/captures, reevaluación de scene_start al cargar, varios hablantes, condiciones de colisión y red deben cerrarse con ensayos nativos. NOT complejo, NSD variable, NIL y NOD/NAD completos siguen pendientes; el editor reutiliza los codecs/recursos fiables de Fase 1.

## PROPUESTA PARA FASE 3

Primero cerrar la prueba nativa de Fase 2 y persistencia/aborto. Después elegir una mejora acotada: undo/redo y grafo más cómodo, o investigación del visor NIL para colocación. Varias ubicaciones/exits o quests simples requieren otro contrato probado antes de ampliar UI. Ninguno de esos trabajos se ha iniciado.

## Seguimiento posterior: despliegue autorizado en RCM

Después de la entrega el usuario autorizó expresamente cambiar RCM para probar. Se creó `chronicles/editor_playtest/project.yaml` mediante los controles de Guardar como, ID y colocación del editor y se hizo Build desde GUI: clase 45.3, Victoria junto al jugador, mismos nodos/eventos de la aceptación. La aceptación original con XYZ permanece intacta. Evidencia: `build/editor/playtest_preparation.json`.

Se copiaron seis archivos verificados a `RCM/east_demo`: los tres de la nueva variante y los tres de la demo anterior con título corregido. Se preservaron el paquete de diagnóstico y el log existente. Se creó `RCM/editor_playtest` para el log que escribirá el motor; los recursos de ambas crónicas se cargan con el acceso directo existente `-user RCM\east_demo`. No se modificó nada fuera de RCM en la instalación.

Backup: `research/runtime_test/backups/before_phase2_playtest_20261008_074911.zip`. Manifest de destinos/hashes: `research/runtime_test/deployment_phase2_playtest.json`. Los hashes de las 43 fuentes originales se comprobaron de nuevo y coinciden. El usuario probó posteriormente **RCM: Victoria y el pacto de Londres** y confirmó que funciona. Su aceptación general y log se preservan en `research/runtime_test/phase2_native_acceptance.json` y `native_phase2_accepted.log`. Este despliegue no añade instalador, automatización al editor ni Fase 3.

## Revisión posterior del editor

Se reprodujeron y corrigieron dos problemas de edición: guardar sin confirmar antes un identificador omitía ese cambio, y las filas del árbol podían conservar destinos/índices antiguos o perder el texto de condiciones/acciones. Guardar/Guardar como/Validar/Build confirman la edición pendiente; los errores mantienen el archivo guardado y la edición visible. Cerrar contempla guardar, cancelar o descartar ese campo. La representación de las filas se comparte entre creación y actualización, sin reconstruir el panel mientras se escribe texto.

Se añadieron cinco regresiones GUI, para un total de **64 pruebas correctas**, y se repitió la aceptación completa con controles Qt. El ZIP sigue idéntico entre GUI y CLI. El generador y los archivos de RCM aceptados por el usuario no han cambiado durante esta revisión. Checkpoint previo: `research/checkpoints/phase2_native_accepted_2026_10_08.zip`.

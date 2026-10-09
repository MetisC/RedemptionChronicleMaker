# Build, Deploy y Run

Campaña / Quests dispone de Integridad, Deploy, Ejecutar y Ruta del juego. También funcionan para un proyecto anterior abierto, sin convertirlo. La ruta seleccionada se valida por Vampire.exe y Resource.nob y se guarda en cache/game_settings.json; --game prevalece. La detección de esta instalación es una comodidad, no un requisito de unidad H: en otra máquina puede seleccionarse otra ruta.

1. Guardar / BUILD CHRONICLE.
2. Cerrar Vampire si está abierto.
3. Deploy: comprueba estado compilado y hashes del manifest, respalda destinos anteriores en el workspace y copia NOB + clases a RCM/<ID>. En la GUI compara también la huella del documento actual con la fuente compilada; si cambió, exige volver a Build. El CLI despliega explícitamente el último build del ID solicitado.
4. Ejecutar: abre Vampire.exe con -user RCM\<ID> y working directory en la raíz del juego. No hace clicks internos ni prueba automáticamente una partida.

CLI: `python tools/rcm.py deploy phase4_demo` y `python tools/rcm.py run phase4_demo`. Ejecutar es una acción explícita del usuario. No hay launcher/installer nuevo.

El NOB agrupa recursos con estructura interna propia; Java va en codex/*.class porque esa es la ruta JVM confirmada. Todo permanece dentro de una carpeta. Deploy nunca toca originales fuera de RCM. Rechaza rutas que escapan, enlaces/reparse points y destinos con hardlinks; verifica todos los destinos antes de escribir. Usa sustitución atómica por archivo y deja manifest/hash/backup. No es una transacción atómica de toda la carpeta ni migración de saves.

La entrega está añadida también a RCM/east_demo para aparecer con el acceso directo existente. La carpeta autónoma RCM/phase4_demo es la usada por el botón Ejecutar. La auditoría research/phase4/deployment_audit.json acredita diez archivos nuevos, doce archivos previos intactos y 43 fuentes originales intactas. El runtime escribe RCM/phase4_demo/runtime_trace.log: eventos, spawns y excepciones; no se hace hooking ni inyección. Después de un nuevo Build, el botón Deploy actualiza la carpeta autónoma; tools/deploy_phase4.py actualiza ambas carpetas de prueba.

Build/Deploy verificados no equivalen a prueba nativa. No se han automatizado clicks de Redemption; las capacidades de control nativo no están disponibles en este entorno.

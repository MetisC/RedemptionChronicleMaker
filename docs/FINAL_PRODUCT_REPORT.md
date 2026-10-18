# RC4 Dynamic Encounters · informe final

**RC4 DYNAMIC ENCOUNTERS APROBADA PARA PRUEBA MANUAL.**
**MANUAL RUNTIME TEST REQUIRED.** No es 1.0 final; no se ha abierto ni automatizado Redemption en esta pasada.

## 1. Investigación del motor

465 clases originales, 223 call sites de factories/preload y seis NOB auditados. CreateThing/SpawnThingNear, transforms, CaptureThing/ReleaseThing, killed, health/max health, timers, Save/Restore y Math.random proceden del bytecode real. NOT health/max son u32, clan/flags e herencia fundamentan metadata. Los hints NSD no son un parser completo. Evidencia: research/dynamic_encounters/ENGINE_SPAWNER_AUDIT.md, spawn_calls.json, enemy_catalogue.json y slices bytecode. Se distinguen original, SDK, RCM, inferencia, no encontrado y pendiente nativo.

## 2. Original Generator Script

Generator.class encontrado en Codex.nob; referencias en SEW4_35_1, SEW4_LOT_12_1, SIM1_5_1 y SIM2_5_1. Parametriza plantilla, retardo, frecuencia, máximo total/vivos. Usa SpawnThing, CaptureThing, killed y records de contadores; no roster completo ni guard explícito de GUID cero. MysticSpawner aporta azar/GUID persistido. RCM reutiliza mecanismos contrastados con protección propia; no ejecuta herramientas originales.

## 3. Arquitectura implementada

scene.generators en formato 10. Model/validator → generador Java propio → ECJ contra Codex → readback/paquete. Extensión exclusiva de formato 10, mismo poll de escena 0,15 s, cuatro apariciones compartidas por tick, métodos por generador/puntos. Fases bajadas a eventos internos en copia, mismas acciones/checkpoints. 32 generadores, 256 slots/escena, cap 1..64, listas/timers/retries acotados. No tracking histórico infinito. Dos flags de protección por generador y records detallados; contadores saturan a un millón. Formato 9 no se convierte al abrir y el tutorial conserva sus bytes/clases.

## 4. UX final

Asistente de cuatro pasos: tipo → enemigos/cantidad → puntos/activación → acciones finales. Opciones avanzadas plegadas; continuo muestra intervalo y cap, jefe muestra umbrales. Acceso desde Campaña, Asistentes y suelo 3D; siete pestañas existentes. Catálogo de enemigos originales sin dificultad inventada. Misma edición de acciones; referencias, safe-delete, renombrado, duplicado con self references ajustadas, undo/redo, guía/gráfico/debug. Un duplicado no copia callbacks externos de activación. ES/EN; idioma del contenido authored se conserva.

## 5. Modos soportados

Emboscada, oleadas al limpiar, continuo con intervalo/cap/target/máximo total, refuerzos por evento y jefe generado o actor authored. Round robin/azar ponderado, puntos alternos/azar y cerca del jugador. Iniciar/detener/pausar/reanudar/reiniciar se combinan con las acciones y condiciones normales. El prop visual es un objeto normal; efectos/audio usan callbacks existentes.

## 6. Health thresholds

Cruce: vida anterior > umbral y actual <= umbral mientras el actor válido sigue vivo. Porcentaje respecto a max health o HP absolutos. Una vez por defecto con checkpoint y record; repetible exige recuperación y un nuevo cruce. Acciones pendientes usan el checkpoint normal. Pausa suspende muestreo de fases. Un golpe mortal puede saltar umbrales: no hay evidencia de un hook general que garantice «antes de morir». No se introduce invulnerabilidad automática.

## 7. Save/load y reentrada

Guarda GUID/rol/entrada, estado, oleada, cantidades, batch/cursors, pausa, tiempos, kills, cooldown y fases. Reconcilia GUID local/plantilla antes de crear. Espera acotada si la restauración tarda; GUID o roster ausente → error sin reemplazar ni resetear ownership incierto. Una vez/continuar/reiniciar al volver/cooldown son políticas explícitas; reiniciar no borra recompensas/flags de otros eventos. La firma estructural obliga a nueva partida si cambia; no hay migrador de saves. La restauración real de captures/records entre instancias requiere DYN08–10.

## 8. Limitaciones

Sin solapamiento/avance manual dentro de una lista de oleadas (usar generadores independientes), volumen aleatorio arbitrario, nuevo preview de modelos, puertas universales o target de cámara por rol generado. No se expone retardo/cap/AI individual por entrada ni todos los equipos posibles en el asistente. Puntos específicos por grupo se validan pero no tienen editor dedicado. Team/actor-type NOT no contrastados no se inventan. Azar no conserva semilla/secuencia entre cargas. Colisión/pathfinding, orden de restore/capture, balance, red, GPU/DPI físico y PC independiente pendientes. Efecto/checkpoint nativo no es una transacción atómica. El tope de slots limita el roster, no la acumulación nativa de cadáveres en combates infinitos.

## 9. Tests

**474 casos completos correctos, 0 fallos, 0 errores y 0 omitidos**; Ruff y alcance mypy configurado PASS. Los trece casos de clic cubren el bucle de proximidad antiguo, enlaces a sí mismo, brushes/readback, selección de Tenebrae, acciones generales, llamadas entre eventos, borrado/referencias, guardado con doubles, interfaz y compilación real en formato 9/10. El ejecutable actual pasa dos recorridos empaquetados ES/EN con PATH restringido; sus 18 módulos modificados y traducciones coinciden con las fuentes. Sin juego automatizado. Evidencia vigente: research/runtime_test/click_interactions/.

Doubles ejecutan Java generado, save/load, ownership, retry, transforms y callbacks; no certifican el motor nativo. El stress de encuentros conserva 25 generadores, 400 entradas y mayor método de 1659/65535 bytes, clases 45.3. Red, GPU/DPI físico y PC independiente siguen pendientes.

## 10. Ejemplos / Showcase

Tutorial rápido intacto formato 9. Dynamic Encounter Lab independiente: Anezka → aceptar oleadas → barril/zona → 3 ratas → 2 ratas → jefe → dos refuerzos al 50% → sonido al 25% → quest al morir. Menú separado para continuo/stop/pause/resume. Showcase sólo añade estación dinámica optativa desde la Guía; su historia principal se compara con baseline retirando exactamente esas adiciones. Mini crónica preservada formato 9. Rats originales débiles; sólo boss del ejemplo con x10 health. Todos compilados, combate nuevo pendiente.

## 11. Manual Runtime Checklist

DYN01 trigger/3 enemigos; DYN02 segunda oleada; DYN03 cap continuo; DYN04 stop; DYN05 50% una vez; DYN06 25% una vez; DYN07 muerte/quest; DYN08 carga a mitad; DYN09 carga tras umbral; DYN10 salir/volver; DYN11 editar/F5; DYN12 fallo de spawn acotado. Procedimientos en MANUAL_RUNTIME_CHECKLIST.md. Estado de todos: MANUAL RUNTIME TEST REQUIRED.

## 12. Build RC4

build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe y acceso directo de raíz. VERSION y recursos EXE 1.0.0-rc4/1.0.0.4. Cuatro builds vigentes: rcm_tutor, rcm_showcase, rcm_mini, rcm_dynamic. Sin deploy/gameplay automático. Originales y archivos de usuario verificados en regression.json.

## 13. User Release RC4

RedemptionChronicleMaker-1.0.0-rc4-win64.zip: programa, JVM/Qt/ECJ, veintidós guías/checklists localizados, cuatro ejemplos propios y licencias. Sin extracción original, herramientas legacy, rutas personales ni workspace de desarrollo. Inventario/hashes comprobados por tools/product_release.py; release_manifest.json y SHA256SUMS.txt contienen resultados finales.

## 14. Workspace Archive

RedemptionChronicleMaker-1.0.0-rc4-workspace.zip, copia privada con fuentes, tests, dependencias, evidencia/build vigente y datos de usuario, sin .git. Incluye investigación extraída para uso privado; no es distribución pública. tools/release_workspace.py comprueba cada archivo. Su recibo queda en research/product_close/workspace_archive.json. Versiones y resultados desechables anteriores retirados tras verificar RC4.

## Corrección posterior: inventario al arrancar

El acceso habitual cargaba el tutorial/mini en una carpeta compartida sin la definición de la llave que el perfil había recogido en Showcase. Se restauró la biblioteca de arranque y su clase dentro de RCM, con copia de lo sustituido, sin modificar Crypt ni los paquetes del tutorial/mini. Deploy compartido/personalizado y cierre de pruebas desde el editor ahora conservan las definiciones. Seis regresiones nuevas; total 431 PASS, ocho recorridos de EXE PASS. Nueva confirmación LAN pendiente. Evidencia en research/runtime_test/profile_startup_repair.json; originales 43 y archivos protegidos 1798 conservados.

## Borrado de entidades y referencias

El árbol, Supr en el visor y Campaña usan un mismo borrado con vista previa. Las referencias llevan a la acción/condición o entidad editable, nunca a un campo escalar. Se puede cancelar, visitar el uso o eliminar las referencias junto con la entidad en una operación de undo. Se eliminan eventos vacíos y dependencias obligatorias; los puntos alternativos y acciones independientes se conservan. El borrado de una condición no convierte su evento en incondicional. Se retira metadata de asistentes que ya no puede resolverse. Ocho regresiones nuevas con una matriz sobre los diez asistentes. El ejecutable final pasó ocho recorridos en ES/EN y escalado Qt, con clic real de confirmación y undo; capturas del diálogo verificadas. Calidad vigente: research/runtime_test/delete_quality.json; no se modifica runtime, tutorial, mini ni proyectos del usuario.

## Objetos originales y puertas

Nueva acción optativa `control_original` para formatos 9/10, selector de props del NSD estático y asistente de paso/zona/viaje en las pestañas existentes. Acceso desde Añadir… de Campaña, menú derecho del visor y propiedades de una referencia original. Ocultar/restaurar/retirar, MoveToFrame y RotatePivot generan Java propio; no se ejecutan herramientas originales ni se modifica NIL/NSD original.

Identidad por plantilla original, ubicación y Cast ID o posición actual/frame 0, con tolerancia de ocho unidades y coincidencia única. Rechaza actores, objetos propios, otros levels y ambigüedades. Ocultar conserva cuatro bits originales y su estado mediante siete flags por objetivo; reentrada/carga reaplican visibilidad/retirada. Retirar no recrea; frames y pivotes requieren soporte real del objeto y no sincronizan el estado privado de su script.

Evidencia actual: `research/runtime_test/original_objects_compile.json`, `original_objects_baseline.json` y `research/engine_evidence/original_objects.txt`. Las pruebas de Java usan doubles además de compilación independiente contra Codex. ORG01–06 en el checklist permanecen pendientes dentro de Redemption; no se automatizó el juego ni se cambió el tutorial aceptado.

Validación de esta adición: 444 casos offline, un fallo por una aserción que rechazaba proyectos propios en chronicles; corregida y repetidos los 16 casos del módulo, todos PASS. Recibo íntegro y retry en original_objects_quality.json. Ejecutable nuevo: ocho recorridos Qt ES/EN/escalado PASS con selección, cancelación, creación y undo de paso. Archivos protegidos del usuario/mini: 1798 sin cambios; tutorial: cuatro fuentes/cinco clases idénticas. El editor cerrado fue sustituido en build/portable; el acceso de raíz apunta al ejecutable verificado. La copia temporal se ha retirado.

## Importación opcional Within The Darkness

Configuración permite elegir un NOB de cualquier carpeta. Se copian sólo los recursos admitidos al workspace y a RCM/_content; la interfaz WTD y campaña demo quedan fuera. Penthouse queda como level reutilizable, con su NIL intacto y NSD estático. La selección actual contiene 19 clanes nuevos, 9 disciplinas nuevas, 125 plantillas seleccionables y 28 modelos. Las referencias sin dependencias resueltas no se muestran. Sin importación no se añaden categorías ni acciones.

Actor → Clan y disciplinas configura la creación; los eventos pueden cambiar clan o nivel de disciplina de un NPC/Player por la API real. Java de los ejemplos sin estas propiedades se conserva. Build registra hash de importación y contrato de saves, y los ZIP de distribución no incluyen el mod. Deploy copia la dependencia local bajo RCM; los inventarios conservan sus bibliotecas sin editar Crypt. Pruebas específicas y prueba con el NOB real: research/mods/content_probe.json. WTD01–07 pendientes de usuario dentro del juego; no se proclama paridad completa ni garantías de licencia ajena.

La suite vigente incluye las pruebas de importación, filtrado, interfaz, traits, inventarios y compilación WTD. El NOB real conserva Penthouse byte a byte, resuelve 9136 triángulos y su contenido permanece local; los recibos de investigación están en research/mods. El ejecutable actual se comprueba en ES/EN, incluidas importación desde Configuración, edición/deshacer de disciplinas y compilación real. No es aceptación dentro de Redemption.

## Selección visual y puertas de Tenebrae

Clic derecho identifica el objeto bajo el cursor y abre el asistente con la identidad elegida; la lista puede localizarlo en 3D. Las mallas incrustadas NSD se previsualizan y seleccionan por triángulos, con rotación y oclusión. El enfoque de originales busca un punto con suelo y visión despejada. Las superficies fijas ofrecen una interacción nativa de clic con etiqueta y acciones editables, sin acciones de retirada del NIL. La salida real de Tenebrae es un tracker con malla CTdoor_L; las otras dos puertas decorativas son geometría NIL. Evidencia y scripts originales en `research/runtime_test/original_selection/`.

La suite de 474 casos, la comprobación específica de trece casos y los dos recorridos del ejecutable final ES/EN son correctos. Se conservan los 43 originales verificados, los 1798 archivos protegidos, las cuatro fuentes y las cinco clases aceptadas del tutorial. ORG07 y CLICK01–08 siguen pendientes dentro del juego; se verificó el acceso directo tras sustituir el editor cerrado.


La revisión de interacciones sustituye el asistente de proximidad por props pulsables nativos con hover/NLS y eventos object_clicked. Admite acciones generales y llamada a otro evento, excluye enlaces a sí mismo, valida ciclos y añade guardas en los nuevos runtimes. Genera brushes acotados en NSD propio, sin tocar NIL ni el NSD original. Las capas nuevas necesitan CLICK01–08 dentro de Redemption; no se atribuye esta aceptación al tutorial previo. Los proyectos de usuario y sus triggers anteriores no se migran en silencio.

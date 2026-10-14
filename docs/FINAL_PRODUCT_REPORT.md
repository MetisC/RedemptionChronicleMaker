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

**439 casos correctos tras repetir la comprobación de traducciones; 0 errores y 0 omitidos**; Ruff y alcance mypy configurado PASS. Doubles ejecutan Java generado, save/load, cruces, lethal skip, ownership, retry, transforms, callbacks, políticas, cooldown, batch, contador y un timer. Widgets prueban crear/editar/backup/cancelar/deshacer/referencias/gráfico/idiomas. Stress compila 25 generadores (20 con diez oleadas), 400 entradas, tres templates, dos puntos, diez thresholds y cuarenta callbacks; mayor método 1659/65535 bytes, clases 45.3. No benchmark nativo. Suite y receipts: research/dynamic_encounters/quality, stress.json, regression.json. El EXE se prueba en ocho recorridos offscreen ES/EN/rutas movidas/PATH restringido/escalado Qt; mismo PC, no prueba de Windows DPI real.

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

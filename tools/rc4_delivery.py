"""Current RC4 receipts, documentation and release-example verification."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    ws=Workspace(ROOT);backend=Backend(ws);reports={}
    for name in ('tutorial','showcase','mini_chronicle','dynamic_lab'):
        report=backend.build((ROOT/'chronicles'/name/'project.yaml').read_text(encoding='utf8'))
        if report['status']!='compiled-unverified-in-game' or not all(v=='45.3' for v in report['class_versions'].values()):raise ValueError(name)
        reports[name]={'id':report['chronicle'],'status':report['status'],'class_versions':report['class_versions'],'geometry_in_package':report['geometry_in_package']}
    baseline=json.loads((ROOT/'research/dynamic_encounters/rc3_baseline.json').read_text(encoding='utf8'))
    checks={name:digest(ROOT/'build/rcm_tutor/bundle/codex'/(name+'.class'))==row['sha256'] for name,row in baseline['tutorial_classes'].items()}
    sources={name:digest(ROOT/name)==sha for name,sha in baseline['files'].items() if name.startswith('chronicles/tutorial/')}
    if not all([*checks.values(),*sources.values()]):raise ValueError('Accepted tutorial changed')
    from rcm.catalogue import verify_sources
    originals=verify_sources(ws,Path(r'H:\GOG\Vampire The Masquerade - Redemption'))
    user={}
    archive=ROOT/'RedemptionChronicleMaker-1.0.0-rc3-workspace.zip'
    manifest_path=ROOT/'research/dynamic_encounters/user_baseline.json'
    if not manifest_path.exists():
        with zipfile.ZipFile(archive) as z:
            manifest=json.loads(z.read(ROOT.name+'/RELEASE_WORKSPACE_MANIFEST.json'))['files']
        selected={Path(path).relative_to(ROOT.name).as_posix():row for path,row in manifest.items() if Path(path).relative_to(ROOT.name).parts[0]=='user_workspaces' or Path(path).relative_to(ROOT.name).as_posix().startswith('chronicles/mini_chronicle/')}
        ws.write(manifest_path,json.dumps(selected,indent=2))
    manifest=json.loads(manifest_path.read_text(encoding='utf8'));mini={}
    for path,row in manifest.items():
        if path.startswith('user_workspaces/'):user[path]=digest(ROOT/path)==row['sha256']
        else:mini[path]=digest(ROOT/path)==row['sha256']
    if not user or not all(user.values()):raise ValueError('User workspace changed')
    if not mini or not all(mini.values()):raise ValueError('Mini chronicle source changed')
    receipt=dict(builds=reports,tutorial_classes=checks,tutorial_sources=sources,mini_sources=mini,originals=originals,user_files_verified=len(user),user_files_unchanged=all(user.values()),native_engine_test=False,game_written=False)
    ws.write('research/dynamic_encounters/regression.json',json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))


def document():
    ws=Workspace(ROOT);qa=json.loads((ROOT/'build/tests/test_report.json').read_text(encoding='utf8'));quality=json.loads((ROOT/'build/tests/quality_report.json').read_text(encoding='utf8'))
    if not qa['successful'] or not quality['successful']:raise ValueError('Quality gate has not passed')
    stress=json.loads((ROOT/'research/dynamic_encounters/stress.json').read_text(encoding='utf8'));largest=max(m['largest_method_bytes'] for m in stress['class_metrics'].values())
    count=qa['tests'];summary=f"{count} PASS, {qa['failures']} FAIL, {qa['errors']} ERROR, {qa['skipped']} SKIP"
    ws.write('CHANGELOG.md','''# Changes · 1.0.0-rc4

- Dynamic encounter wizard: ambush, waves, continuous spawning, reinforcements and boss phases, in Campaign, assistants and the existing 3D ground menu.
- Original enemy filtering and confirmed template health, AI, flags, clan and scene provenance.
- Waypoint/near-player spawning, caps, bounded retries, pause/resume/stop/reset, existing event actions and health/counter/state conditions.
- Native GUID ownership records, bounded restore reconciliation, wave/batch cursors, thresholds and cooldown. Missing ownership fails closed instead of spawning duplicates.
- References, safe deletion, duplication, undo, graph and trace navigation include generators. English/Spanish UI.
- Opt-in format 10 with a backup; format 9 opens unchanged. Accepted tutorial source/runtime preserved. Separate Dynamic Encounter Lab and small optional Showcase station.
- Alias-free YAML writing now round-trips shared point lists through the existing safe loader.

First-run, safe saving, deployment, cache identity and language preferences remain. Native gameplay, independent-PC and real GPU/DPI checks remain manual. Not final 1.0.
''')
    ws.write('RELEASE_NOTES.md','''# Redemption Chronicle Maker 1.0.0-rc4

Create dynamic combats without writing Java. Use **+ Dynamic encounter…** in Campaign, assistants or the 3D ground menu. Choose a mode, enemies/count, spawn waypoints and activation. Boss phases use percentage or absolute health crossings and the existing action editor.

The original Generator was found and studied. RCM uses confirmed factories, timers, capture/death callbacks, health and native save records with bounded ownership tracking and retries. Defaults retain original health/AI. Existing authored encounters and geometry are preserved.

Format 9 opens unchanged. The first dynamic encounter opts into format 10 with backup and undo. Structural changes may require a new game; saves are not migrated.

The accepted Quick tutorial is preserved. Open examples/dynamic_lab/project.yaml for the independent combat lab or select the optional dynamic station from the Showcase Guide. Weak original Rats are used; example bosses have increased health to make thresholds visible.

**MANUAL RUNTIME TEST REQUIRED.** Native combat/save ownership remain unaccepted. A lethal hit may skip a threshold; no universal before-death interception is promised. Waves advance on clear. Arbitrary random-volume positions, overlapping/manual advance inside one wave list, direct dynamic-role camera targets and per-entry delay/AI overrides are unavailable. Use separate generators/events and existing action targets where appropriate.

Projects live outside the program. Settings selects English/Spanish. No original authoring tools or game assets are distributed. Local single-player candidate; networking, independent-PC, physical DPI and real GPU validation remain pending. Not final 1.0.
''')
    ws.write('docs/FINAL_PRODUCT_REPORT.md',f'''# RC4 Dynamic Encounters · informe final

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

**{summary}**; Ruff y alcance mypy configurado PASS. Doubles ejecutan Java generado, save/load, cruces, lethal skip, ownership, retry, transforms, callbacks, políticas, cooldown, batch, contador y un timer. Widgets prueban crear/editar/backup/cancelar/deshacer/referencias/gráfico/idiomas. Stress compila {stress['generators']} generadores (20 con diez oleadas), {stress['enemy_entries']} entradas, tres templates, dos puntos, diez thresholds y cuarenta callbacks; mayor método {largest}/65535 bytes, clases 45.3. No benchmark nativo. Suite y receipts: research/dynamic_encounters/quality, stress.json, regression.json. El EXE se prueba en ocho recorridos offscreen ES/EN/rutas movidas/PATH restringido/escalado Qt; mismo PC, no prueba de Windows DPI real.

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
''')
    ws.write('docs/FINAL_UX_REPORT.md',f'''# Usabilidad vigente · RC4

Se conserva la estructura de siete pestañas, bienvenida, F5 y paneles inferiores bajo demanda. Encuentros dinámicos se integra en Campaña, Asistentes y menú contextual del suelo 3D.

El asistente pregunta tipo, enemigos/cantidad, puntos/cuándo y qué ocurre al terminar. El continuo muestra ritmo/cap sin abrir Advanced; sólo Jefe muestra fases. El editor de acciones reutiliza los controles normales sobre un borrador aislado. Aplicar es una operación undo; cancelar no muta. Formato 9 requiere backup al optar por 10; abrirlo no convierte.

Propiedades resume puntos, cantidades, cap, activación y acciones finales. Gráfico agrupa oleadas/callbacks/fases sin dibujar cada enemigo futuro. IDs/referencias/guías/debug navegan al generador. Duplicar ajusta self references y mantiene explícita la activación externa.

Se inspeccionan capturas del EXE bilingüe a escalas Qt 100/125/150/200%. {summary}; esto no verifica GPU/DPI físico ni gameplay. Ver FINAL_PRODUCT_REPORT.md y research/dynamic_encounters/portable.
''')
    for file in ('KNOWN_ISSUES.md','RELEASE_BLOCKERS.md','FIRST_RUN_REPORT.md'):
        p=ROOT/'docs'/file;text=p.read_text(encoding='utf8').replace('1.0.0-rc3','1.0.0-rc4').replace('RC3','RC4').replace('research/rc3','research/dynamic_encounters');ws.write(p,text)
    ws.write('docs/TESTING.md',f'''# Pruebas y calidad · RC4

Desde la raíz, Python y dependencias locales preparados:

```powershell
python tools/quality.py --fast
python tools/quality.py --no-coverage
python tools/test.py --pattern test_dynamic_encounters.py
python tools/test.py --pattern test_dynamic_gui.py
python tools/audit_spawners.py
python tools/rcm.py verify-originals
```

{summary}. Ruff y mypy en paths/input_limits/file_transaction; no tipado completo. Resultados actuales archivados en research/dynamic_encounters/quality. Doubles de Java y Qt offscreen no prueban el motor, OpenGL real ni DPI físico. Los ocho recorridos empaquetados y capturas están en research/dynamic_encounters/portable.

Stress: 25 generadores, 20 con diez oleadas, 400 entradas, tres templates, diez umbrales, callbacks y múltiples puntos. Bytecode/métodos medidos en stress.json; no rendimiento nativo certificado. Tutorial/clases, originales y archivos de usuario comparados en regression.json.

Cuatro fuentes vigentes: chronicles/tutorial, showcase, mini_chronicle y dynamic_lab. Baselines históricos necesarios sólo en tests/fixtures; no cambiar hashes para esconder fallos. Dependencias cache/vendor, devtools y toolchain.

Manual: MANUAL_RUNTIME_CHECKLIST.md, DYN01–12. Generado, compilado, probado con doubles/widgets y verificado en Redemption son estados separados. No se ha automatizado el juego.
''')
    for suffix,english in [('.md',False),('.en.md',True)]:
        text=('''# RC4 readiness

IMPLEMENTED: dynamic encounter wizard, five modes, original enemy metadata, health/counter/state conditions, bounded native ownership/save records and references/graph/debug. Format 10 opt-in backup; format 9 tutorial preserved.

VERIFIED OFFLINE: '''+summary+'''; real Codex 45.3 builds, class budgets, native doubles, shipped Qt controls and eight frozen bilingual/scaling runs on this PC. Evidence: research/dynamic_encounters. No independent-machine/GPU/native-combat acceptance.

VERIFIED IN REDEMPTION: prior tutorial acceptance remains scoped to that story. This pass did not open or automate Redemption.

REQUIRES HUMAN RUNTIME TEST: DYN01–12, Showcase/save/load/reentry, F5/first run, existing-item LAN and independent-PC/DPI checks. MANUAL RUNTIME TEST REQUIRED. Not final 1.0.

LIMITS: lethal damage can skip phases, no universal pre-death hook, clear-only waves, no direct dynamic-role cameras or arbitrary random-volume placement. Unresolved ownership stalls rather than duplicating enemies. Network remains experimental. Native effects/checkpoints are not atomic; no structural-save migration.
''' if english else '''# Preparación RC4

IMPLEMENTADO: asistente de encuentros dinámicos, cinco modos, metadata original, condiciones de vida/contador/estado, records de propiedad/guardado acotados y referencias/gráfico/debug. Formato 10 optativo con backup; tutorial 9 preservado.

VERIFICADO OFFLINE: '''+summary+'''; builds Codex 45.3, presupuestos de clases, doubles nativos, widgets y ocho recorridos del EXE bilingüe/escalado en este PC. Evidencia en research/dynamic_encounters. No aceptación de combate nativo, GPU o PC independiente.

VERIFICADO EN REDEMPTION: aceptación anterior del tutorial conservada sólo para esa historia. Esta pasada no abrió ni automatizó Redemption.

REQUIERE PRUEBA HUMANA: DYN01–12, Showcase/save/load/reentrada, primer arranque/F5, LAN con objeto previo y PC/DPI físico. MANUAL RUNTIME TEST REQUIRED. No es 1.0 final.

LÍMITES: daño mortal puede saltar fases, sin hook universal previo a muerte, oleadas al limpiar, sin cámaras por rol dinámico o posición aleatoria en volúmenes. Propiedad no resuelta detiene antes de duplicar. Red experimental. Efecto/checkpoint nativo no atómico; sin migrador estructural de partidas.
''')
        ws.write('docs/RELEASE_1_0_READINESS'+suffix,text)
    print(summary)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    prepare() if args.prepare else document()

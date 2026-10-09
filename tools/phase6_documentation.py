"""Publish audit documentation from persisted evidence, keeping native gaps visible."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def write(name,text):
    path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+'\n',encoding='utf8')
def read(name,default=None):
    try:return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return default
tests=read('build/tests/test_report.json',{});fast=read('build/tests/fast_test_report.json',{});coverage=read('build/tests/coverage.json',{});perf=read('research/phase6/performance.json',{});inventory=read('research/phase6/code_inventory.json',[])
write('README.md',r'''
# Redemption Chronicle Maker · 0.6.0

Editor moderno de crónicas para **Vampire: The Masquerade — Redemption**. Reutiliza escenarios originales como geometría inmutable y genera directamente nuestra capa de mundo, conversaciones, quests, estado y Java. No utiliza Embrace, NOT Editor ni otros programas originales de autoría.

**Estado: candidato técnico de Fase 6; beta privada todavía pendiente de aceptación nativa.** El informe distingue tests, compilación contra Codex real y observaciones dentro del juego. No se ha empezado Fase 7.

## Abrir

Distribución portable: `build/portable/RedemptionChronicleMaker/RedemptionChronicleMaker.exe`. Conserva **toda esa carpeta**: incluye las bibliotecas y la JVM; el EXE solo no es suficiente. No necesita instalar Python. Al arrancar crea su `workspace/`, detecta el juego o solicita su ubicación y genera catálogos leyendo la instalación. Los originales no se incluyen.

Para trabajar directamente con este workspace:

```powershell
python editor.py chronicles/system_test/project.yaml
```

Si Python no está en PATH, en este equipo está en `C:\Users\Usuario\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

Si falla el controlador gráfico: `python editor.py --safe-mode`. Puedes editar, guardar y compilar sin crear OpenGL. `--reset-settings` conserva una copia de la configuración antes de restablecerla.

## Probar una crónica

Abre `chronicles/system_test/project.yaml`, **Guardar → Validar → Build → Deploy**. En este equipo Deploy del editor usa la carpeta indicada por tu acceso directo existente: `RCM/east_demo`. **Ejecutar** abre exactamente ese `.lnk`, conservando destino, argumentos y carpeta de inicio. Puedes elegirlo mediante **Acceso del juego…**. El acceso no se reescribe.

En tu acceso del escritorio: **Multiplayer → New Game → RCM System Test**. Inicia una partida nueva. Victoria, Witness y la guía son pruebas de diálogo; hay quests, libro, cámaras y viaje al oeste. Las nuevas conversaciones de Witness/Keeper hacen que esos personajes ya no sean simples marcadores. El checklist completo está en [RUNTIME_TEST_MATRIX.md](docs/RUNTIME_TEST_MATRIX.md). Su resultado nativo actual se mantiene explícito allí; compilar no equivale a probar la partida.

Las campañas históricas se conservan. **RCM: Victoria y el pacto de Londres** tuvo aceptación del usuario en Fase 2. **Las voces de Londres** tuvo una regresión comunicada por el usuario; sus correcciones actuales necesitan repetición nativa.

## Un solo paquete

**Paquetes → Crear paquete de crónica** produce un `.rcmpack`. Es un ZIP verificado con manifest, NOB y clases. Al instalar se mantiene todo dentro de **RCM/<id>**, con copias de seguridad y sin sobrescribir archivos ajenos o modificados. El motor exige NOB en raíz y clases en `codex/`, pero todo pertenece a esa única carpeta.

**Exportar proyecto** produce `.rcmproject`: YAML y fuentes propias, sin recursos originales. Importar no ejecuta Java. Todo paquete que contenga clases exige revisión explícita antes de instalar; hashes no acreditan confianza ni autoría.

## Comandos de desarrollo

```powershell
python tools/rcm.py validate chronicles/system_test/project.yaml
python tools/rcm.py build chronicles/system_test/project.yaml
python tools/rcm.py package rcm_system build/rcm_system/rcm_system.rcmpack
python tools/rcm.py inspect-package build/rcm_system/rcm_system.rcmpack
python tools/quality.py --fast
python tools/quality.py
python tools/rcm.py verify-originals
```

La suite rápida usa fixtures sintéticos y no necesita juego, Qt ni Java. La completa necesita catálogos/copias técnicas extraídas y compilador/JVM; tampoco controla Redemption. Instalación de dependencias: `requirements.txt`, `requirements-editor.txt`, `requirements-dev.txt`, en `cache/vendor` y `cache/devtools`. [TESTING.md](docs/TESTING.md) detalla los comandos y categorías.

## Límites actuales

Writer NOT experimental sobre tags contrastados; campos desconocidos conservados. Sin geometría editable, waypoints, editor de disciplinas, timeline completa de cámara ni objetivos internos de quests no comprendidos. Las transiciones cambian locations mediante la API; no existe autoría general de puertas ni spawn de entrada arbitrario. Save/load nativo, abortos, combate y red necesitan ensayos actuales. Cambiar la estructura persistente puede exigir partida nueva; no hay migrador de saves de Redemption.

Fuente técnica: instalación original, clases, bytecode y documentación real. Solo `RCM/` está autorizado para despliegue; el resto del juego permanece de solo lectura.

[Informe de Fase 6](docs/PHASE6_REPORT.md) · [Matriz de funciones](docs/FEATURE_MATRIX.md) · [Bloqueos](docs/RELEASE_BLOCKERS.md) · [Guía del editor](docs/EDITOR_GUIDE.md) · [Problemas conocidos](docs/KNOWN_ISSUES.md) · [Formatos](docs/FORMAT_NOTES.md) · [Evidencia](docs/ENGINE_NOTES.md)
''')
write('docs/TESTING.md',r'''
# Pruebas y calidad

Desde la raíz, con Python 3.12 y dependencias locales preparadas:

```powershell
python tools/quality.py --fast
python tools/quality.py
python tools/test.py --pattern test_phase6_integration.py
python tools/phase6_fixtures.py
python tools/phase6_performance.py
python tools/phase6_viewport.py
python tools/phase4_regression.py
python tools/rcm.py verify-originals
```

`quality` ejecuta Ruff, mypy y unittest, devuelve código distinto de cero ante fallo y escribe `build/tests/quality_report.json`. En modo completo añade cobertura de ramas, JSON y HTML. No necesita hosting ni Git para incorporarse después a CI.

| Categoría | Evidencia / selección | Dependencias |
|---|---|---|
| UNIT / PACKAGE | `--fast`, test_safety_unit | PyYAML; fixtures sintéticos; sin juego, Qt ni compilador |
| FORMAT | test_core, test_phase5_resources, negativos sintéticos | Corpus técnico extraído para integración; corpus aleatorio propio en rápida |
| SERIALIZATION / REFERENCES | test_phase2, test_spatial, test_campaign | Catálogos extraídos; algunos casos también compilan |
| GUI-MODEL | test_editor, test_campaign_editor, test_phase6_gui | Qt offscreen; no acredita dibujo GPU ni menús de Redemption |
| BUILD / INTEGRATION | test_phase6_integration, test_campaign_callbacks | ECJ con hash verificado, JVM, API Codex real; doubles sólo para callbacks |
| OPENGL / PERFORMANCE | phase6_viewport, phase6_performance, phase4_regression | Ventana real del editor y recursos originales de lectura |
| RUNTIME NATIVO | RUNTIME_TEST_MATRIX | Redemption, partida y observaciones reales; nunca marcado por unittest |

Fixtures temporales permanecen bajo `build/tests`; se eliminan al acabar cuando es posible. Fuentes oficiales de regresión: `chronicles/system_test`, `golden`, `large_fixture`. `phase6_fixtures` recrea exclusivamente esas fuentes y su Java propio. No ejecutar acceptance histórico que reescribe su demo sin conservarla primero.

Cobertura: `build/tests/coverage.json` y `coverage_html/index.html`. Los porcentajes incluyen líneas y ramas. No persigue 100% global: revisar huecos en lógica crítica, negativos y errores reales. La cobertura de subprocess Java no aparece como Python; sus contratos tienen harness independiente. OpenGL y portable se ensayan aparte.

Mypy comprueba `paths`, `input_limits`, `file_transaction`, con imports externos al alcance tratados como Any. **No es tipado completo del programa.** El alcance reducido se mantiene explícito; el resto usa validación de datos y tests. Referencia: [documentación oficial de mypy sobre imports](https://mypy.readthedocs.io/en/stable/running_mypy.html).

Ante un fallo: identificar test y traceback, conservar el reporte, corregir la causa y añadir una regresión que compruebe conducta. No relajar un test para esconder la avería. La prueba de borrar un nodo cambió deliberadamente: ahora se espera que la operación sea bloqueada y que los datos permanezcan intactos.

Preparación limpia: instalar `requirements-dev.txt` en `cache/devtools`, dependencias runtime en `cache/vendor`; `tools/bootstrap.ps1` descarga ECJ y escanea originales sin ejecutarlos. La suite rápida sirve en CI sin instalación del juego. La completa requiere cache privada; no distribuir `research/original` ni archivos del juego como fixtures públicos.
''')
write('docs/TROUBLESHOOTING.md',r'''
# Resolución de problemas

| Síntoma | Acción |
|---|---|
| No aparece la campaña | Usar la carpeta de `-user` del acceso. NOB en raíz, `codex/*.class` dentro de esa carpeta. Cerrar Vampire antes de Deploy. En este equipo: `RCM/east_demo`. |
| Pide CD key con Ejecutar | Seleccionar **Acceso del juego…** y usar el acceso del escritorio que funciona. El editor lo abre directamente; no lo reconstruye. La causa exacta del comportamiento distinto del ejecutable directo no se ha establecido. |
| Campaña vieja / build anterior | Una validación/compilación/publicación fallida bloquea Deploy y Package. Revisar `build_report.json`, recompilar y empezar una partida nueva. |
| No se ve un NPC | Elegir una fixture `near_player` para comprobar primero callbacks. XYZ válida como dato no garantiza suelo/colisión. En el editor seleccionar actor y F para enfocarlo. |
| Fondo extraño | EastLondon conserva el entorno original gris; no añadir un sky artificial como reparación. El viewport no reproduce niebla/iluminación del motor. |
| Cursor/UI tras diálogo | Regresión reportada en Fase 5. El controlador actual prepara feedback antes de Execute y libera cámara en retorno, aborto y fallo. Pruebas offline pasan; repetir rechazo y aborto en juego según checklist. |
| Catálogos ausentes/corruptos | El arranque del editor conserva copias y reconstruye leyendo el juego. CLI: `scan --no-disassemble`. No redefinir un baseline original que ha cambiado. |
| Pantalla negra o crash gráfico | Arrancar `--safe-mode`; no crea OpenGL. `--reset-settings` respalda configuración. No modifica ajustes gráficos del juego ni Windows. |
| Java no compila | Ver `build/failed_attempts/<id>_<intento>/...compiler.log`, fuentes y source_map. El fallo no publica una distribución parcial. |
| Falta compiler / JVM | Portable necesita carpeta completa y `runtime/bin/java.exe`. Fuente necesita ECJ verificado y JVM. No usar javac moderno para producir clases del juego. |
| Archivo instalado modificado | Install/Uninstall se detienen y conservan el archivo. Revisar la diferencia y las copias en `research/package_backups`; no borran partidas ni logs ajenos. |
| Ruta rechazada | Salidas dentro del workspace; despliegue dentro de RCM. No usar enlaces, junctions, hardlinks, nombres Windows reservados ni rutas de escape. |

**Ayuda → Informe de diagnóstico**, o `tools/rcm.py diagnostics`, escribe `build/diagnostics/report.json`. Es local; no envía telemetría ni archivos. Incluye versiones y errores de índices. Revisa su contenido antes de compartirlo.

No hay cancelación de compilación activa. El editor bloquea cambios/cierre mientras termina el worker. Si un proceso externo interrumpe el programa, la validez del build debe comprobarse en su manifest; reiniciar y recompilar.
''')
write('docs/KNOWN_ISSUES.md',r'''
# Problemas conocidos · Fase 6

| ID | Severidad | Reproducción / estado | Evidencia / regresión |
|---|---|---|---|
| RCM-601 | CRITICAL, verificación pendiente | Fase 5: rechazar la primera conversación dejó cursor/UI ausentes y cámara sin cambio. Corrección: feedback activo antes de Execute, fallback de speaker en primera línea, liberar cámara en todos los finales. Falta repetir en motor. | test_campaign_callbacks; reporte del usuario; no declarar solución nativa |
| RCM-602 | CRITICAL, verificación pendiente | Callbacks save/restore de campaña habían usado firma sin capture. Corregidas a `(int)` según Codex real. Offline save/restore pasa; persistencia nativa todavía sin aceptación. | tests Java y signatures originales |
| RCM-603 | HIGH, corregido | Fuente identificable inválida tras build válido podía dejar manifest anterior disponible. Backend, CLI y botón Build invalidan intento. | test_invalid_build_invalidates_previous_distribution, test_build_failure_invalidates_known_id |
| RCM-604 | HIGH, corregido | Escritura fallida a mitad de Deploy/Install/Uninstall dejaba cambios parciales. Preflight total, backup, reemplazos y rollback; manifest último. | fault injection de replace_files, publicación fallida y eliminación obsoleta |
| RCM-605 | HIGH, corregido | Java visible editado sin guardar no contaba como cambio pendiente. Ahora Save/Build/switch/close consideran ese buffer y conservan backup. | test_pending_java_is_committed_before_save, cancel_close |
| RCM-606 | HIGH, corregido | Un script propio podía pisar un controlador generado; se rechaza su namespace y sources dentro del build propio. | test_generated_java_namespace_collision_blocked |
| RCM-607 | HIGH, corregido | Borrar nodos, actores, quests o escena de entrada rompía referencias. Ahora se preflightan enlaces y nuevos errores sin mutar fuente; se cancela si quedan referencias. | delete_candidate y tests GUI/quest/entry/GOTO |
| RCM-608 | HIGH, corregido | Java/texturas cambian sin cambiar YAML: huella anterior no lo detectaba. Se incluyen bytes propios y se comprueba modificación durante build. | test_own_file_edits_invalidate_build_fingerprint |
| RCM-609 | HIGH, corregido | Un manifest de clean con `build/id/../otro` escapaba de la carpeta del build. Se rechaza antes de borrar. | test_clean_internal_traversal_cannot_delete_another_build |
| RCM-610 | MEDIUM, corregido | El gráfico declaraba destinos de `jump` como no alcanzables al buscar solamente objetos en lugar de strings del schema real. | test_story_graph_real_transitions_cycles_dead_and_orphan |
| RCM-611 | MEDIUM, corregido | Índices/configuración inválidos bloqueaban inicio. Recovery preserva datos; fallback seguro sin OpenGL. | fresh scan/repair, corrupt settings/cache, portable smoke |
| RCM-612 | MEDIUM, mitigado | Runtime puede producir logs repetidos ante error. Campañas rotan al superar 1 MiB, conservando una copia; logs con fallos de I/O se reflejan en consola. | Java real compilado; límite no probado dentro del juego |
| RCM-613 | HIGH, limitación | Reordenar/cambiar quests/events/entidades puede cambiar índices de flags/capture. Firma del contrato avisa de partida nueva. No hay migración de saves entre builds. | test_save_contract_change_is_reported |
| RCM-614 | MEDIUM, limitación | SpawnNear con radio cero puede juntar actores y dificultar distinguirlos. System Test etiqueta Witness/Keeper y añade diálogo; no garantiza separación espacial. | Confirmación previa del usuario, no precisión de colisión verificada |
| RCM-615 | MEDIUM, limitación | UI visual no tiene cobertura completa; panel NOT/AI y gráfica siguen con caminos manuales. Fase 5 no estaba completa al empezar esta auditoría. | FEATURE_MATRIX, coverage, aceptación específica |

Los corregidos se consideran cerrados sólo en el ámbito de sus pruebas. RCM-601/602 siguen bloqueando aceptación de beta porque sus cambios no tienen todavía prueba nativa actual. Los informes antiguos son evidencia histórica, no aceptación de la versión 0.6.0.
''')
write('docs/RELEASE_BLOCKERS.md',r'''
# Release blockers

**Beta privada lista: NO, hasta completar la aceptación nativa actual.** Esta lista no se vacía artificialmente porque pase unittest.

| Bloqueo | Criterio de cierre |
|---|---|
| B1 · CRITICAL · Diálogo/UI/cámara | En partida nueva: aceptar, rechazar primera respuesta, abortar, reabrir; cámara y cursor/UI recuperados en todos los casos. Corregido offline, pendiente en Redemption. |
| B2 · CRITICAL · Persistencia | Guardar/cargar antes y después de decisiones, inventario, quest y transición; GUIDs coherentes, sin duplicados ni recompensas repetidas. Firma capture contrastada; comportamiento nativo pendiente. |
| B3 · HIGH · NOT/AI propios | Template propio e item instanciados y utilizables; herencia/modelo/script/AI comprobados en motor. Reader lossless y writer parcial no equivalen a estabilidad runtime. |
| B4 · HIGH · Distribución limpia | Portable probado en equipo/VM sin Python/JDK globales, otra ruta y permisos normales. El ensayo local con workspace nuevo/PATH restringido no sustituye esa máquina. |
| B5 · HIGH · Red y repetición | Host/client, reentrada de mapa y ciclos repetidos sin actor duplicado ni UI bloqueada. No hay aceptación de red. |

Puertas, waypoints, AI completa, editor visual de árbol de comportamiento y timeline de cámara están **NOT IMPLEMENTED**, no son botones vacíos ofrecidos como funcionales. La beta debe declarar ese alcance reducido; no son fallos ocultos que se den por soportados.

Antes de invitar usuarios: quality PASS, regresión de fuentes PASS, originales intactos, portable y paquete auditados, bugs CRITICAL nativos cerrados con evidencia, guía de primera ejecución ensayada. Publicación externa adicional requiere cerrar inventario/licencia propia y revisión de redistribución de dependencias; no se ha publicado nada.
''')
write('docs/RUNTIME_TEST_MATRIX.md',r'''
# Aceptación en Redemption · RCM System Test

Fuente `chronicles/system_test/project.yaml`, paquete `build/rcm_system/rcm_system.rcmpack`. **Cada casilla necesita observación en el juego.** El estado actualizado del intento está en `research/phase6/native_status.json`, si existe. No convertir resultados de doubles en PASS nativo.

Abrir exactamente el acceso `Vampire.exe - Acceso directo.lnk` del escritorio, con su carpeta y `-user RCM\east_demo`. Multiplayer → New Game → **RCM System Test**. Siempre partida nueva después de actualización estructural.

| Prueba | Resultado esperado | Estado actual |
|---|---|---|
| Chronicle/menu/título | RCM System Test y título legible de escena | NOT TESTED versión actual |
| Escenario y entorno | EastLondon, fondo gris original, sin halo | NOT TESTED actual; fondo aceptado históricamente |
| Victoria propia | Template T_rcm6_victoria y clase RCM6Actor | NOT TESTED |
| Witness/Guía | Hablar y volver al juego, repetir | NOT TESTED |
| Rechazar al primer diálogo | Cursor y HUD vuelven; próxima interacción disponible | NOT TESTED · B1 |
| Aceptar alianza / deshacerla | Flag cambia; conversación posterior refleja elección | NOT TESTED |
| Abortar conversación | Cámara y controles liberados, sin aplicar RETURN | NOT TESTED · B1 |
| Cámara de escena | Plano temporizado y liberación | NOT TESTED |
| Quests | Journal muestra títulos/pasos; sólo avance válido | NOT TESTED |
| Inventario | Libro recogible, entrega/quitar controlados | NOT TESTED |
| WestLondon | Viaje y regreso, Contact/Keeper interactivos | NOT TESTED |
| Encuentro | Guards creados una vez; combate y fin de grupo | NOT TESTED |
| Audio | Música y ambiente identificables, detener | NOT TESTED |
| Save/load durante recorrido | Restaurar actores/flags/objetos sin duplicar ni premiar dos veces | NOT TESTED · B2 |
| Save/load con conversación/cámara | Recuperar controles, no conservar conversación activa inválida | NOT TESTED · B2 |
| Reentrada y repetición | 3 ciclos de viaje, conversación y recarga | NOT TESTED |
| Host/client | Estado y callbacks coherentes en red | NOT TESTED · B5 |

Save/load: guardar antes de alianza; rechazar; recargar y aceptar; guardar con libro; cambiar mapa y recargar; completar quest; guardar/cargar y verificar que XP y objetos no se repitan. Registrar partida, revisión, acción y log; resultado PASS/FAIL/NOT TESTED por caso.

Prueba XYZ independiente: fuente `chronicles/editor_acceptance/project.yaml`; observar altura, posición y yaw, suelo y colisión. El viewport mide coordenadas reales pero no prueba la colisión del motor. Los triggers son muestreo en Java cada 150 ms y orientación yaw para cajas; probar borde, reentrada y `once`.

Copiar únicamente logs propios desde RCM al workspace como evidencia. No leer memoria ni inventar un inspector de estado en vivo. `runtime_trace.log` es observación de callbacks, no prueba por sí sola de HUD, cámara, audio o journal visible.
''')
write('docs/PACKAGES.md',r'''
# Paquetes y proyectos exportables

`.rcmpack`: ZIP determinista, `manifest.json` (format 1), `<id>.nob`, `codex/*.class` 45.3. Un `.rcmproject` lleva YAML y recursos fuente propios bajo assets. No lleva modelos/geometría ni librería/API original. El juego original es dependencia obligatoria.

Manifest: ID, nombre, versión exacta, autor/descripción, requisitos, templates propios, dependencias locales, files/size/SHA-256 y indicador de Java avanzado. Todo paquete con clases contiene código ejecutable; aunque `custom_code=false` porque el generador produjo las clases, se solicita revisión antes de instalar. No hay firmas criptográficas ni sandbox del Java; los hashes sólo comprueban integridad.

Comandos: `package <id> <destino>`, `inspect-package <archivo>`, `install-package <archivo> --accept-custom-code`, `uninstall-package <id>`, `export-project <YAML> <destino>`, `import-project <archivo> <carpeta-vacía>`. Salidas dentro del workspace. Menú **Paquetes** usa el mismo backend, con revisión de nombre/versión/lista de archivos/destino.

Instalar sólo dentro de `game/RCM/<id>`, con `.rcm_manifest.json` propio. Update/Uninstall verifican hashes anteriores, conservan archivos ajenos/logs/saves y se detienen si un archivo administrado fue modificado. Backups en `research/package_backups`. Preflight de enlaces, hardlinks, rutas y temporales; rollback de archivos escritos y obsoletos ante fallo. Cada reemplazo es atómico, el conjunto no tiene aislamiento de lectores ni garantía frente a apagado repentino; Vampire debe estar cerrado.

ZIP: límite 2000 entradas y 64 MiB descomprimidos por contenedor; sin duplicados por casefold, rutas absolutas, traversal, nombres Windows reservados, ADS, enlaces o entradas de directorio. Se rechazan geometría/modelos/binarios ajenos y clases con versión incompatible. En instalación se contrasta namespace de originales con catálogo disponible. No es un antivirus ni un verificador completo de bytecode malicioso.

Dependencias: comprobación de ID/versión local exacta y bloqueo de uninstall si otra depende de ella; conflicto conservador de templates. **No hay composición de recursos entre carpetas `-user` ni resolución/transmisión de dependencias remotas.** Cada crónica debe ser autosuficiente sobre recursos originales y sus recursos propios; no prometer que declarar una dependencia hace aparecer sus assets en el motor.

GUI Deploy para el acceso conocido utiliza `RCM/east_demo`; packaging instala en carpeta individual. Si pruebas un paquete individual, tu acceso debe usar esa carpeta y se puede seleccionar mediante **Acceso del juego…**. El sistema no modifica tu acceso ni instala en directorios originales.
''')
write('docs/AUDIT_DETAILS.md',r'''
# Auditoría del código y de las promesas

Inventario AST de todos los módulos Python de src/tools/tests: `research/phase6/code_inventory.json`, con SHA-256, clases, funciones y líneas. Constructos sospechosos: `suspicious_constructs.json`. Ruff y mypy tienen reportes reproducibles. La búsqueda automática es un inventario para revisión, **no certifica semánticamente cada función**.

Revisión de focos: modelo/shape/encoding/IDs; referencias y borrados; roundtrip/autosave/undo; generación por scene; callbacks/saves/conversaciones/cámaras; recursos propios y namespaces; build válido frente a fallo; publicación/rollback; rutas/junctions/hardlinks; catálogos/primer arranque; paquete y confianza; buffers Java; renderer/caches; CLI y doc histórica.

Constructos `pass`: catalogue omite del conjunto de roundtrip escenas con bloques variables que el codec no comprende; no las reescribe. Window omite referencias visuales a una selección antigua tras refresh, o preserva error original si falla el log. Service/build_transaction toleran fallo secundario de diagnóstico o report inexistente; el error real no se convierte en éxito. Fuzz de NOT acepta ValueError para bytes malformados. No se encontraron `NotImplementedError` usados como feature presentada al creador.

El `*_Passive extends Codex {}` generado es deliberado: evita ejecutar la lógica narrativa original heredada y recibe comportamiento por el controlador/click proxy. No es una implementación falsa de AI. El WAV de silencio sí es un recurso PCM generado para soporte de subtítulos, no voz sintetizada ni doblaje. Debug muestra logs observados; no lee estado vivo ni journal del motor.

Se eliminaron 47 imports sin uso y seis variables/cálculos sin efecto. No se aplicó formateo masivo. Static gate comprueba errores sintácticos/nombres/imports/locals; tipado limitado a tres módulos críticos nuevos, no a Qt completo. No se declaró la suite exhaustiva porque creció su número.

Huecos admitidos: storyboard derivado sin edición libre de grafo; NOT sólo tags contrastados y estructura contigua; AI sólo campos escalares conocidos; sin paths/waypoints; cámaras por actor/tipo/ángulo/duración sin timeline XYZ; puertas fuera del modelo; transiciones sin entrada espacial propia; objetivos de quest abstractos sobre flags/journal; release debug desactivado quita nuestra instrumentación de campaña, no controla logging de Java propio; no migración de saves nativos ni cancelación de compilación activa. Ver FEATURE_MATRIX y RELEASE_BLOCKERS.

La Fase 5 carecía de packaging/distribución y pruebas nativas completas. Se cubrieron esos huecos técnicos necesarios para comprobar Fase 6, sin iniciar nuevos editores ni Fase 7. Reader lossless, compilación de API y prueba simulada siguen separados de aceptación real del engine.
''')
write('docs/FEATURE_GAPS.md',r'''
# Huecos de funciones

| Función | Estado | Consecuencia |
|---|---|---|
| Packaging/export/import/rollback | IMPLEMENTED Fase 6 | Antes faltaban; ahora backend y menú propios, tests de seguridad y roundtrip |
| Primera ejecución/cache recovery | IMPLEMENTED Fase 6 | Reconstrucción de catálogos, backup y modo sin OpenGL |
| Safe Delete | IMPLEMENTED Fase 6 | Bloquea referencias, no rompe silenciosamente el proyecto |
| Java visible pendiente y huella de assets | IMPLEMENTED Fase 6 | Guardar/compilar/desplegar ven modificaciones de fuentes propias |
| NOT completo / stats, disciplinas | PARTIAL / NOT IMPLEMENTED | Sólo tags documentados, desconocidos preservados, writer experimental |
| AI / paths / waypoints | PARTIAL / NOT IMPLEMENTED | Escalares de .nai y pause/enable; no editor de rutas/comportamientos arbitrarios |
| Cámara / secuencia completa | PARTIAL | Plano por actor, tipo, ángulo y duración; no posiciones libres ni timeline |
| Puertas y entradas de viaje propias | NOT IMPLEMENTED | Jump cambia location y usa entrada del runtime original |
| Grafo de conversación editable | PARTIAL | Proyección y navegación; autoría por árbol/propiedades |
| Cache de relaciones incremental | NOT IMPLEMENTED | Grafo se deriva del YAML; fixture de 486 enlaces tarda ~12 ms con tracing |
| Migración de saves del juego | NOT IMPLEMENTED | Cambios estructurales avisan de partida nueva |
| Canceler Build | NOT IMPLEMENTED | Worker mantiene editor protegido mientras termina |
| Rendering fiel al engine | PARTIAL | Materiales/UV/modelos estáticos; iluminación, animación y niebla no reproducidas |
| Configuración viewport persistida | PARTIAL | Defaults seguros; no persistencia completa de todas las preferencias |
| Dependencias entre paquetes | PARTIAL | Validación local de versión/conflictos, sin composición de assets runtime |
| Distribución en máquina limpia | NOT TESTED | Ensayo local portable no sustituye VM/equipo independiente |
| Red | NOT TESTED | No dar por válida replicación por tener guardas NetIsClient |

Alcance de crónica completa actual: varios escenarios originales; NPCs/objetos/triggers/eventos; ramas y flags; quests/journal abstracto; inventario/encuentros; planos/audio/viajes; build y distribución propios. La cadena técnica está comprobada offline; la crónica completa necesita terminar el checklist nativo para ser aceptada como beta.
''')
rows=[
('Levels originales','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','catalogue/core/spatial; históricos aceptados'),
('Geometry/mesh read-only','PASS','PASS','NOT APPLICABLE','PASS','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','NOT TESTED','112 NIL y 1476 NOD históricos; regresión GL actual'),
('Actor/posición/orientación','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','core/spatial/campaign; colisión requiere motor'),
('Props/items originales','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','campaign/format/build'),
('Conversaciones/RETURN/GOTO','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','phase2/campaign_callbacks; fallo nativo previo documentado'),
('Grafo diálogo/story','PASS','PARTIAL','NOT APPLICABLE','PASS','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','story_graph derivado; árbol es fuente'),
('Flags/condiciones all-any-not','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','campaign/callback harness'),
('Quests/journal/pasos abstractos','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','campaign/CampaignEngine; límites NQD'),
('Inventario/pickup/give/take','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','campaign harness; identidad persistente'),
('Triggers box/sphere yaw','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','spatial y harness; muestreo 150 ms'),
('Eventos/acciones','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','ACTIONS/WHEN compartidos; Java compilado'),
('Encuentros/enemy/death','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','campaign; combate real pendiente'),
('Multi-level/Jump','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','2 y 5 mapas compilados; entrada original'),
('Cámara/plano temporizado','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','API CodexCamera real; callback mocks'),
('Timeline/XYZ cámara','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT TESTED','no botón presentado como terminado'),
('Música/ambiente','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','recursos reales y CodexSound'),
('Templates NOT propios','PARTIAL','PARTIAL','PASS','PASS','PARTIAL','PASS','PASS','NOT TESTED','NOT subset/opaque safety; writer experimental'),
('AI propia/Nai','PARTIAL','PARTIAL','PASS','PASS','PARTIAL','PASS','PASS','NOT TESTED','AI_FIELDS contrastados; neutral pausa AI'),
('Paths/waypoints','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT TESTED','fuera de authoring actual'),
('Java propio/texturas','PASS','PARTIAL','PASS','PASS','PASS','PASS','PASS','NOT TESTED','resources/integration/gui pendiente Java'),
('Rename/referencias','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT APPLICABLE','campaign/spatial/phase2'),
('Safe Delete','PASS','PASS','PASS','PASS','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','safe_edit tests; bloquea y conserva fuente'),
('Undo/redo/duplicate','PASS','PASS','PASS','PASS','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','GUI-model; history campaña completa'),
('Save/SaveAs/autosave/backup','PASS','PASS','PASS','PASS','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','document/phase2/editor'),
('Picking/gizmos/snap','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','math3d/spatial + GL; ground no collision'),
('Resource catalogue/cache','PASS','PASS','NOT APPLICABLE','PASS','PASS','PASS','PASS','NOT APPLICABLE','fresh scan/repair; contenidos originales readonly'),
('Build validado/determinista','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','e2e/réplicas/hash Phase2 idéntico'),
('Atomic publication/rollback','PASS','PASS','NOT APPLICABLE','PASS','PASS','PASS','PASS','NOT APPLICABLE','fault injection; manifest último, sin aislamiento total'),
('Clean owned artifacts','PASS','NOT IMPLEMENTED','NOT APPLICABLE','PASS','NOT APPLICABLE','PASS','NOT APPLICABLE','NOT APPLICABLE','CLI clean; no borra archivos ajenos'),
('Deploy/Install/Uninstall RCM','PASS','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','fake game tests; native deployment evidencia separada'),
('Project export/import','PASS','PASS','PASS','PASS','PASS','PASS','NOT APPLICABLE','NOT APPLICABLE','e2e byte-identical distribution + GUI roundtrip'),
('Package manifest/deps/trust','PARTIAL','PASS','PASS','PASS','PASS','PASS','PASS','NOT TESTED','version local; sin assets compartidos ni firma'),
('Playtest/logs/source map','PARTIAL','PARTIAL','PASS','PASS','PASS','PASS','PASS','NOT TESTED','trace parser; observaciones, no inspector vivo'),
('First run/settings/safe mode','PASS','PARTIAL','PASS','PASS','NOT APPLICABLE','PASS','NOT APPLICABLE','NOT APPLICABLE','startup + portable smoke separado'),
('Portable executable','PASS','PASS','NOT APPLICABLE','PASS','PASS','PASS','NOT APPLICABLE','NOT TESTED','local build/probe; máquina limpia pendiente'),
('Save/restore nativo','PASS','NOT APPLICABLE','PASS','PASS','PASS','PASS','PASS','NOT TESTED','firma capture real; engine todavía B2'),
('Puertas/entradas arbitrarias','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT TESTED','geometría no se edita; API parcial'),
('Multiplayer replication','PARTIAL','NOT APPLICABLE','NOT APPLICABLE','PARTIAL','PARTIAL','PASS','PASS','NOT TESTED','NetIsClient no prueba sincronización'),
('Cancel build','NOT IMPLEMENTED','NOT IMPLEMENTED','NOT APPLICABLE','NOT APPLICABLE','NOT APPLICABLE','NOT IMPLEMENTED','NOT APPLICABLE','NOT APPLICABLE','cierre/cambios bloqueados mientras compila')]
matrix='# Matriz de funciones · versión actual\n\nPASS se refiere al alcance descrito y a evidencia de esa columna. RUNTIME TEST corresponde exclusivamente a 0.6.0; las confirmaciones históricas no se transfieren automáticamente. PARTIAL/NOT IMPLEMENTED aparecen sin ocultar huecos.\n\n| Feature | Model | GUI | Save/load fuente | Validation | Generator | Build | Deploy | Runtime test | Evidencia/límite |\n|---|---|---|---|---|---|---|---|---|---|\n'
matrix+='\n'.join('| '+' | '.join(row)+' |' for row in rows)
write('docs/FEATURE_MATRIX.md',matrix)
(ROOT/'research/phase6/feature_matrix.json').write_text(json.dumps([dict(zip(['feature','model','gui','serialization','validation','generator','build','deploy','runtime','evidence'],row)) for row in rows],indent=2),encoding='utf8')
write('docs/PERFORMANCE.md','# Rendimiento local\n\nEquipo Windows 11, Python 3.12.14. Tiempos de load/save/validate/references/search medidos con tracemalloc activo; compilación sin tracing. No son promesa para otros equipos. Search aquí mide filtro de enlaces, no toda la UI de búsqueda.\n\n| Fixture | Load s | Save s | Validate s | References s | Build s | ZIP bytes |\n|---|---|---|---|---|---|---|\n'+'\n'.join('| '+name+' | '+' | '.join(str(round(p[k],4)) for k in ['load_seconds','save_seconds','validation_seconds','references_seconds','build_seconds'])+' | '+str(p['distribution_bytes'])+' |' for name,p in perf.get('projects',{}).items())+'\n\nFixture grande: 5 levels, 100 actores, 50 conversaciones, 20 quests, 100 eventos, 50 triggers, 30 objetos y 5 planos. 486 enlaces en esta revisión. Fuente YAML guardada en chronicles/large_fixture.\n\n`research/phase6/viewport.json`: cargas reales GL y repintados síncronos del editor; no equivale a FPS constante ni mide GPU memory. Las repeticiones de cargas conservan ~'+str(perf.get('repeated_loads',{}).get('retained_python_bytes_delta','pendiente'))+' bytes Python adicionales tras GC; no demuestra ausencia completa de fugas de Qt/GPU.\n\nEvidencia reproducible: phase6_performance.py y phase6_viewport.py. No se introdujo cache incremental de relaciones sin necesidad medida.\n')
write('docs/DEPENDENCIES_LICENSES.md',r'''
# Dependencias y avisos

Inventario exacto de distribuciones instaladas y textos locales: `research/phase6/dependencies.json`, `build/portable_notices`, `THIRD_PARTY_NOTICES` del portable. Generador: `tools/license_inventory.py`. No declarar una licencia por memoria cuando METADATA no la identifica: se conserva el aviso del paquete.

Runtime: Python 3.12.14 (PSF), PySide6/Shiboken 6.10.2 (alternativas LGPL/GPL indicadas en wheel), PyYAML 6.0.3 (MIT), NumPy 2.3.5 (BSD y avisos de librerías incluidas), Pillow 12.3.0 (MIT-CMU), ECJ 3.26.0 (avisos dentro del JAR), Temurin/OpenJDK 21.0.11 (legal y excepciones dentro de runtime/legal). Qt y NumPy pueden incluir dependencias binarias adicionales: conservar sus textos completos y registrar binarios del portable antes de publicación.

Desarrollo: coverage 7.10.6, Ruff 0.14.0, mypy 1.18.2, types-PyYAML 6.0.12.20250915, PyInstaller 6.16.0 y helpers según inventario. Versiones runtime flexibles de NumPy/Pillow están en requirements-editor; la medición corresponde a las versiones exactas del inventario. Sin descarga automática de paquetes de crónica ni acceso a servicios remotos.

El portable contiene módulos Python/Qt, JVM y compiler modernos. No contiene Embrace, NOT Editor, ejecutable del juego, classes.zip original, Codex.nob, Resource.nob, modelos, levels ni texturas originales. Esos datos se leen/copian en el workspace privado al escanear la instalación legítima del usuario. Un paquete de crónica incluye únicamente nuestra capa generada y recursos propios; el metadata de entorno/anchor necesario se deriva de escenas originales.

No se ha fijado una licencia pública para el código propio de RCM ni se ha publicado la aplicación. Esta lista es inventario técnico de avisos, no aprobación legal de distribución pública. Qt permanece como bibliotecas dinámicas en carpeta visible. No entregar un EXE suelto que descarte bibliotecas, avisos y JVM.

Referencias técnicas de herramientas: [Ruff](https://docs.astral.sh/ruff/linter/), [PyInstaller onedir](https://pyinstaller.org/en/stable/operating-mode.html), [tipos PyYAML](https://pypi.org/project/types-PyYAML/6.0.12.20250915/).
''')
heads={}
for match in re.finditer(r'^(\d+)\. (.+)$',(ROOT/'docs/PHASE6_REQUIREMENTS.md').read_text(encoding='utf8'),re.M):
    n=int(match[1])
    if n not in heads:heads[n]=match[2]
partial={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,42,44,45,46,47,48,49,54,56,58,59,60,61,62,64,65,67,68,69,70,71,72,75,76,78,79,80,81,84,85,92,95,96,97,98,99,100,101,102,104,105,106,107,108,109,112,114,115,116,117,119,120,121,123,124,125,127,128,129,130,131,133,134,135,136,140,141,142,143,145,146,147,149,151,152,153,154,156,157}
native={41,86,87,89,90,91,132,148,150}
missing={43,118}
failed={138,139}
audit='# Seguimiento de los 157 apartados\n\nEstados reflejan alcance real, no número de tests. PASS sólo significa que el apartado tiene entrega concreta comprobada; PARTIAL conserva trabajo no demostrado. Evidencia transversal: FEATURE_MATRIX, KNOWN_ISSUES, TESTING y JSON de research/phase6.\n\n| Apartado | Estado | Evidencia / límite |\n|---|---|---|\n'
for n in range(1,158):
    status='NOT TESTED' if n in native else 'NOT IMPLEMENTED' if n in missing else 'FAIL' if n in failed else 'PARTIAL' if n in partial else 'PASS'
    evidence='RUNTIME_TEST_MATRIX; aceptación nativa pendiente' if n in native else 'FEATURE_GAPS; no se ofrece como implementado' if n in missing else 'RELEASE_BLOCKERS; beta no aceptada' if n in failed else 'FEATURE_MATRIX y AUDIT_DETAILS; alcance parcial/documentado' if status=='PARTIAL' else 'Entrega persistida y comandos de TESTING; ver PHASE6_REPORT'
    audit+='| '+str(n)+'. '+heads.get(n,'Apartado no localizado')+' | '+status+' | '+evidence+' |\n'
write('docs/PHASE6_REQUIREMENTS_STATUS.md',audit)
critical=['model.py','formats.py','campaign.py','campaign_document.py','generator.py','campaign_generator.py','service.py','build_transaction.py','file_transaction.py','output_validation.py','packages.py','project_resources.py','campaign_relations.py','paths.py','input_limits.py']
cover_rows=[]
for path,data in coverage.get('files',{}).items():
    if Path(path.replace('\\','/')).name in critical:cover_rows.append((path.replace('\\','/'),data['summary']['percent_covered']))
coverage_table='| Módulo | Líneas + ramas |\n|---|---|\n'+'\n'.join('| '+p+' | '+str(round(percent,1))+'% |' for p,percent in cover_rows)
report=f'''# Fase 6 · estabilización y auditoría

## SUMMARY

Versión 0.6.0. Trabajo persistido en el workspace, sin herramientas originales de autoría, sin geometría editada, sin Fase 7. La Fase 5 estaba parcialmente implementada, no completamente terminada. Esta revisión añade protecciones verificables y cubre huecos de distribución necesarios; **beta privada aún NO aceptada**, por bloqueos nativos y ensayo de máquina independiente.

## FEATURE MATRIX SUMMARY

{len(rows)} funciones con estados separados Model/GUI/Save-load/Validation/Generator/Build/Deploy/Runtime: FEATURE_MATRIX.md. Seguimiento de los 157 apartados: PHASE6_REQUIREMENTS_STATUS.md. Inventario de {len(inventory)} módulos Python; AST y hashes no se presentan como certificación semántica exhaustiva.

## TEST SUITE / TEST COUNTS

Baseline: 120 tests. Resultado actual persistido: **{tests.get('tests','pendiente')} tests, {tests.get('failures','?')} failures, {tests.get('errors','?')} errors, {tests.get('skipped','?')} skipped; successful={tests.get('successful','pendiente')}**. Suite rápida: {fast.get('tests','pendiente')} fixtures sintéticos, successful={fast.get('successful','pendiente')}. Unit/format/package/GUI-model/build/integration/performance/GL se distinguen en TESTING.md. Native no forma parte de este recuento.

Fault injection: disk/write/replace/delete a mitad, clean traversal, ZIP corrupto, enlaces/hardlinks, hashes incompatibles, Java inválido, build previo tras error, export/import determinista, eliminación referenciada, caches/config corruptos, entrada de campaña, feedback inmediato/rechazo/aborto/reintento.

## COVERAGE

Global líneas+ramas: {round(coverage.get('totals',{}).get('percent_covered',0),1)}%. HTML/JSON en build/tests. No implica cobertura del motor ni de Java dentro del engine. El renderer y widgets visuales tienen cobertura Python menor y pruebas reales separadas. Mypy PASS limitado a 3 módulos; Ruff correctness PASS según quality_report. No se afirma tipado completo.

{coverage_table}

## RUNTIME TESTS

Confirmaciones históricas: nombre, escenario, entorno gris, NPC cercano y diálogo/elecciones de Fase 2. Regresión comunicada en Fase 5: cámara y cursor/UI al rechazar. Esta revisión tiene corrección y harness; el estado del intento nativo actual se registra aparte en research/phase6/native_status.json. RUNTIME_TEST_MATRIX no transforma compilación/doubles en PASS. Save/load, red, AI/NOT, audio y journal requieren observación actual.

## BUGS FOUND / BUGS FIXED / REGRESSIONS FOUND

KNOWN_ISSUES.md registra severidad, reproducción y regresión por cada fallo. Se corrigieron: publicación parcial, manifest stale tras error, namespace Java generado, Java pendiente invisible, huella de bytes propios, borrados que rompían referencias, clean traversal, alcance de gráfico jump, errores ZIP/arranque, diagnósticos perdidos por staging y lectura de acceso directo exacto. RCM-601/602 siguen pendientes de cierre nativo; no se ocultan.

## FEATURE GAPS FOUND / FEATURE GAPS FIXED

Antes faltaban packaging/export/import, portable actual, recuperación de primer arranque y preflight de Safe Delete. Ahora existen backend/menú y pruebas. Otros huecos permanecen declarados: waypoints, puertas, cámara XYZ/timeline, editor completo NOT/AI, cancelación, preferencias completas de viewport, composición de dependencias y migración de saves nativos. FEATURE_GAPS contiene consecuencias.

## KNOWN ISSUES / BLOCKERS / CRITICAL ISSUES

RELEASE_BLOCKERS: diálogo/UI/cámara actual, save/load nativo, NOT/AI propios, máquina limpia y red/repetición. No se declara 0 críticos. El scope de beta debe ser explícito y no ofrecer features ausentes como terminadas.

## PERFORMANCE

Fixture grande: 5 levels, 100 actores, 50 conversaciones, 20 quests, 100 eventos, 50 triggers, 30 items, 5 planos. Compila contra API real. PERFORMANCE.md y performance.json incluyen load/save/validation/references/build; viewport.json mide ventana GL y repintados. Repetición Python no prueba ausencia de fugas GPU.

## PROJECT MIGRATIONS

Schema 1 y 2 sobreviven sin migración implícita al abrir/guardar. Upgrade a project_format 5 es explícito y conserva copia previa. Cinco proyectos históricos abren con GL real, fuentes idénticas, recompilan; el ZIP Phase2 conserva SHA-256 90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab. Firma save_schema avisa si cambian estructuras de captura/flags. No hay conversor de saves nativos.

## .NOT STATUS

Reader lossless sobre corpus y fuzz propio; preserva tags desconocidos, comentarios, padding y cola. Cambios estructurales se bloquean con cola opaca. Writer para tags contrastados y herencia/copia es experimental hasta confirmar runtime; no se inventan stats/disciplinas. Nuevo template y AI/script compilados en fixture, aceptación nativa pendiente.

## VIEWPORT STATUS

EastLondon real: 45.927 triángulos, 109 materiales. Transform/undo y cargas repetidas de SystemTest/fixture grande funcionan en GL local. No representa iluminación/animación/niebla final ni sustituye colisión del juego. --safe-mode conserva autoría sin contexto GPU.

## BUILD STATUS

YAML → modelo/validator/catalogue → generadores propios → readback NOT/NSD/NCO/NVO/NLS/NMF/NSC/NQD → ECJ y clases 45.3 → staging/publicación. Verificación de links y hashes, fuentes no modificadas, ZIP determinista, compiler failure con diagnóstico preservado. Reemplazos individuales atómicos, manifest último; no aislamiento total ni garantía frente a apagado.

## DEPLOY STATUS

Sólo RCM, juego cerrado, hashes/source propios actuales, backups y rollback. Editor usa destino del acceso real del usuario y abre ese mismo .lnk. No altera originales ni el acceso. Evidencia de despliegue puntual y verificación de originales en research/phase6. La instalación del paquete individual y el acceso compartido east_demo son destinos distintos, documentados.

## PACKAGE STATUS

.rcmpack y .rcmproject, manifest/versions/hash/código/restricciones ZIP y registro de ownership. Import preserva fuente y bytes del build; install/update/uninstall conservan archivos ajenos y detienen cambios modificados. Dependencias locales exactas, sin composición automática de assets ni descarga. Portable onedir con JVM/ECJ y avisos; reporte propio y smoke test separado, no afirmación de máquina limpia. PACKAGES.md y DEPENDENCIES_LICENSES.md detallan alcance.

## BETA READINESS

**NO aceptar beta privada todavía.** La base técnica ahora tiene gate reproducible, más negativos y mejor trazabilidad. Terminar B1–B5 con evidencia, ensayar recorrido básico de principiante y actualizar matriz por observación. No llamar terminada la aceptación nativa por pasar los tests actuales.

## RECOMMENDATIONS FOR PHASE 7

Sin iniciar Fase 7: priorizar primero los bloqueos nativos y repetición, medir fallos reales de UI de creadores, ampliar tipos/cobertura en controles críticos y estabilizar contratos de saves. Decidir expansión NOT/AI/cámaras sólo con API/formato contrastado y aceptación. Ninguna herramienta original debe incorporarse al workflow.
'''
write('docs/PHASE6_REPORT.md',report)
probe=read('build/portable_probe/build/portable_smoke.json',{})
native=read('research/phase6/native_status.json',{})
if probe:
    path=ROOT/'docs/PHASE6_REPORT.md'
    with path.open('a',encoding='utf8') as out:out.write('\n## DISTRIBUTION LOCAL ACCEPTANCE\n\nWorkspace inicialmente vacío, PATH restringido a Windows System32: valid_project='+str(probe.get('valid_project'))+', real_gl='+str(probe.get('real_gl'))+', build_status='+str(probe.get('build_status'))+'. JVM propia incluida; clases 45.3. Exit 0 registrado. Es una prueba local, no de máquina limpia independiente. Evidencia: research/phase6/portable_probe.json. Se corrigieron shadowing de tools/rcm.py y captura accidental de ICU de Poppler al empaquetar.\n')
    with (ROOT/'docs/KNOWN_ISSUES.md').open('a',encoding='utf8') as out:out.write('\nRCM-616 (HIGH, corregido en ensayo portable): tools/rcm.py ocultaba el package y producía ModuleNotFoundError; entry de empaquetado trasladado a build. RCM-617 (HIGH, corregido en ensayo portable): PATH global hacía incluir ICU de Poppler incompatible con Qt; búsqueda aislada y análisis de imports/exports. La prueba de arranque con workspace vacío, GL y compilación regresiona ambos errores.\nRCM-618 (HIGH, corregido): validación de catálogo rechazaba archive:null de recursos sueltos originales; test_loose_resource_catalogue_accepts_null_archive conserva ese contrato y rechaza tipos corruptos.\n')
if native:
    with (ROOT/'docs/PHASE6_REPORT.md').open('a',encoding='utf8') as out:out.write('\n## CURRENT NATIVE ATTEMPT\n\n'+native.get('summary','Resultado en native_status.json')+'\n')
print('README, matrices, checklist, quality guides and Phase6 report persisted')

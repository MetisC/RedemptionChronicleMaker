# Fase 6 · estabilización y auditoría

## SUMMARY

Versión 0.6.0. Trabajo persistido en el workspace, sin herramientas originales de autoría, sin geometría editada, sin Fase 7. La Fase 5 estaba parcialmente implementada, no completamente terminada. Esta revisión añade protecciones verificables y cubre huecos de distribución necesarios; **beta privada aún NO aceptada**, por bloqueos nativos y ensayo de máquina independiente.

## FEATURE MATRIX SUMMARY

39 funciones con estados separados Model/GUI/Save-load/Validation/Generator/Build/Deploy/Runtime: FEATURE_MATRIX.md. Seguimiento de los 157 apartados: PHASE6_REQUIREMENTS_STATUS.md. Inventario de 88 módulos Python; AST y hashes no se presentan como certificación semántica exhaustiva.

## TEST SUITE / TEST COUNTS

Baseline: 120 tests. Resultado actual persistido: **174 tests, 0 failures, 0 errors, 0 skipped; successful=True**. Suite rápida: 28 fixtures sintéticos, successful=True. Unit/format/package/GUI-model/build/integration/performance/GL se distinguen en TESTING.md. Native no forma parte de este recuento.

Fault injection: disk/write/replace/delete a mitad, clean traversal, ZIP corrupto, enlaces/hardlinks, hashes incompatibles, Java inválido, build previo tras error, export/import determinista, eliminación referenciada, caches/config corruptos, entrada de campaña, feedback inmediato/rechazo/aborto/reintento.

## COVERAGE

Global líneas+ramas: 67.8%. HTML/JSON en build/tests. No implica cobertura del motor ni de Java dentro del engine. El renderer y widgets visuales tienen cobertura Python menor y pruebas reales separadas. Mypy PASS limitado a 3 módulos; Ruff correctness PASS según quality_report. No se afirma tipado completo.

| Módulo | Líneas + ramas |
|---|---|
| src/rcm/build_transaction.py | 95.1% |
| src/rcm/campaign.py | 91.3% |
| src/rcm/campaign_document.py | 89.3% |
| src/rcm/campaign_generator.py | 89.0% |
| src/rcm/campaign_relations.py | 100.0% |
| src/rcm/file_transaction.py | 82.8% |
| src/rcm/formats.py | 92.0% |
| src/rcm/generator.py | 95.2% |
| src/rcm/input_limits.py | 100.0% |
| src/rcm/model.py | 85.7% |
| src/rcm/output_validation.py | 95.2% |
| src/rcm/packages.py | 84.8% |
| src/rcm/paths.py | 86.5% |
| src/rcm/project_resources.py | 79.9% |
| src/rcm/service.py | 94.2% |

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

## DISTRIBUTION LOCAL ACCEPTANCE

Workspace inicialmente vacío, PATH restringido a Windows System32: valid_project=True, real_gl=True, build_status=compiled-unverified-in-game. JVM propia incluida; clases 45.3. Exit 0 registrado. Es una prueba local, no de máquina limpia independiente. Evidencia: research/phase6/portable_probe.json. Se corrigieron shadowing de tools/rcm.py y captura accidental de ICU de Poppler al empaquetar.

## CURRENT NATIVE ATTEMPT

El acceso exacto del escritorio abrió Vampire 1.1 y llegó al menú principal sin pedir CD-key. La captura muestra el menú; Tab/flecha arriba no cambiaron selección y el clic automatizado sobre Multiplayer no lo activó. No se inició RCM System Test, por lo que no hay aceptación actual de conversación, cámara, save/load ni NOT/AI. Se ha solicitado ayuda para iniciar la partida.

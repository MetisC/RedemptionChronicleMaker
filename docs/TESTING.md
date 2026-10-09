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
# Pruebas añadidas en Fase 7

`test_phase7_scenes` cubre asociación estática, rechazo de la interpretación NSS errónea, validación de perfiles, bytes completos de entorno, corrupción/versión desconocida, dos escenas sobre la misma geometría, GUI/guardar/undo/cambio de level, fingerprint y compatibilidad de paquete. La regresión histórica mantiene su SHA-256 fijado. Suite actual: 188 tests offline, Ruff y mypy con su alcance limitado. La demo de tres escenas compila contra Codex real y el portable tiene smoke local con GL; la aceptación nativa sigue aparte en `PHASE7_PLAYTEST.md`.


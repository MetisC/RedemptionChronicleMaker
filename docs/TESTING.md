# Pruebas y evidencia vigentes

Desde la raíz, con dependencias locales preparadas:

```powershell
python tools/quality.py --fast
python tools/quality.py --no-coverage
python tools/test.py --pattern "test_director*.py"
python tools/test.py --pattern test_camera_paths.py
python tools/test.py --pattern test_metadata_capacity.py
python tools/test.py --pattern "test_final_flecks*.py"
python tools/audit_embrace_closure.py
python tools/rcm.py verify-originals
```

Gate: build/tests/quality_report.json; detalle: build/tests/test_report.json. Ruff/mypy comprueban su alcance configurado. Evidencia del cierre: research/embrace_closure. Los 174 NCP originales deben conservar sus bytes en roundtrip; no cambiar fixtures/hashes para ocultar regresiones.

Separar datos/generación/paquetes, compilación real Codex 45.3, escenarios con doubles, widgets/transacciones y aplicación empaquetada, y observación del usuario en Redemption/PC independiente.

El gate no abre ni juega a Redemption. Los probes del EXE sólo leen la instalación real y escriben contra instalaciones sintéticas. Carpeta movida/PATH restringido/offscreen no certifica otro PC ni render OpenGL/DPI físico.

Tutorial, mini y laboratorio dinámico permanecen. Showcase añade una sala opcional; director_acceptance es independiente. La comparación narrativa retira sólo adiciones opcionales antes del fixture fijo.

Manual: MANUAL_RUNTIME_CHECKLIST.md/.en.md, EMB01–24, DYN01–12, puertas/WTD/cargas/red. Un PASS offline no convierte un caso manual en PASS.

Último gate completo del cierre: **525 tests, 0 failures, 0 errors, 0 skipped**. Ruff y mypy configurado pasan; 112 catálogos de sector verificados. Después del ajuste final de ancho de propiedades: **140 widgets/regressions, 0/0/0**, en build/tests/post_layout_gui_report.json, sin sustituir el informe de la suite completa. Las pruebas focales por sí solas no son un nuevo gate completo.

El recibo research/embrace_closure/final_flecks_delivery.json enlaza compilación real 45.3, portable EN/ES, integridad de 43 fuentes originales y la aceptación limitada de carga inicial por el usuario. Nuevos casos manuales: EMB-MUSIC-01..03, EMB-CONV-01..05 y EMB-NCP-01..05.

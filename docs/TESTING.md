# Pruebas y evidencia vigentes

Desde la raíz, con dependencias locales preparadas:

```powershell
python tools/quality.py --fast
python tools/quality.py --no-coverage
python tools/test.py --pattern "test_director*.py"
python tools/test.py --pattern test_camera_paths.py
python tools/audit_embrace_closure.py
python tools/rcm.py verify-originals
```

Gate: build/tests/quality_report.json; detalle: build/tests/test_report.json. Ruff/mypy comprueban su alcance configurado. Evidencia del cierre: research/embrace_closure. Los 174 NCP originales deben conservar sus bytes en roundtrip; no cambiar fixtures/hashes para ocultar regresiones.

Separar datos/generación/paquetes, compilación real Codex 45.3, escenarios con doubles, widgets/transacciones y aplicación empaquetada, y observación del usuario en Redemption/PC independiente.

El gate no abre ni juega a Redemption. Los probes del EXE sólo leen la instalación real y escriben contra instalaciones sintéticas. Carpeta movida/PATH restringido/offscreen no certifica otro PC ni render OpenGL/DPI físico.

Tutorial, mini y laboratorio dinámico permanecen. Showcase añade una sala opcional; director_acceptance es independiente. La comparación narrativa retira sólo adiciones opcionales antes del fixture fijo.

Manual: MANUAL_RUNTIME_CHECKLIST.md/.en.md, EMB01–24, DYN01–12, puertas/WTD/cargas/red. Un PASS offline no convierte un caso manual en PASS.

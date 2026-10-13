# Pruebas y calidad · RC4

Desde la raíz, Python y dependencias locales preparados:

```powershell
python tools/quality.py --fast
python tools/quality.py --no-coverage
python tools/test.py --pattern test_dynamic_encounters.py
python tools/test.py --pattern test_dynamic_gui.py
python tools/audit_spawners.py
python tools/rcm.py verify-originals
```

425 PASS, 0 FAIL, 0 ERROR, 0 SKIP. Ruff y mypy en paths/input_limits/file_transaction; no tipado completo. Resultados actuales archivados en research/dynamic_encounters/quality. Doubles de Java y Qt offscreen no prueban el motor, OpenGL real ni DPI físico. Los ocho recorridos empaquetados y capturas están en research/dynamic_encounters/portable.

Stress: 25 generadores, 20 con diez oleadas, 400 entradas, tres templates, diez umbrales, callbacks y múltiples puntos. Bytecode/métodos medidos en stress.json; no rendimiento nativo certificado. Tutorial/clases, originales y archivos de usuario comparados en regression.json.

Cuatro fuentes vigentes: chronicles/tutorial, showcase, mini_chronicle y dynamic_lab. Baselines históricos necesarios sólo en tests/fixtures; no cambiar hashes para esconder fallos. Dependencias cache/vendor, devtools y toolchain.

Manual: MANUAL_RUNTIME_CHECKLIST.md, DYN01–12. Generado, compilado, probado con doubles/widgets y verificado en Redemption son estados separados. No se ha automatizado el juego.

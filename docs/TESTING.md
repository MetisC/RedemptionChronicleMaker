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

439 casos correctos tras repetir la comprobación de traducciones; 0 errores y 0 omitidos. Ruff y mypy en paths/input_limits/file_transaction; no tipado completo. Resultados actuales archivados en research/dynamic_encounters/quality. Doubles de Java y Qt offscreen no prueban el motor, OpenGL real ni DPI físico. Los ocho recorridos empaquetados y capturas están en research/dynamic_encounters/portable.

Stress: 25 generadores, 20 con diez oleadas, 400 entradas, tres templates, diez umbrales, callbacks y múltiples puntos. Bytecode/métodos medidos en stress.json; no rendimiento nativo certificado. Tutorial/clases, originales y archivos de usuario comparados en regression.json.

Cuatro fuentes vigentes: chronicles/tutorial, showcase, mini_chronicle y dynamic_lab. Baselines históricos necesarios sólo en tests/fixtures; no cambiar hashes para esconder fallos. Dependencias cache/vendor, devtools y toolchain.

Manual: MANUAL_RUNTIME_CHECKLIST.md, DYN01–12. Generado, compilado, probado con doubles/widgets y verificado en Redemption son estados separados. No se ha automatizado el juego.

Borrado: test_delete_flow.py cubre punto de aparición → eliminar / cancelar / navegar / deshacer, puntos alternativos, inventarios, condiciones y entidades creadas por los diez asistentes. La pasada de 439 casos detectó textos nuevos ausentes del catálogo de inglés; se corrigió y se repitió esa comprobación, con Ruff/mypy actuales correctos. El recibo conserva el intento completo y el resultado de la repetición; no es evidencia de juego nativo.

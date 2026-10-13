# Pruebas y calidad

Desde la raíz, con Python y dependencias locales preparados:

```powershell
python tools/quality.py --fast
python tools/quality.py --no-coverage
python tools/test.py --pattern test_product_close.py
python tools/rcm.py verify-originals
```

quality ejecuta Ruff, el alcance configurado de mypy y unittest. Los resultados se escriben en build/tests. La ejecución completa sin --no-coverage genera también informes de cobertura; los harness Java tienen comprobaciones independientes.

La suite rápida utiliza datos sintéticos. La completa requiere Qt, compilador/JVM, catálogos y recursos originales extraídos. Los tests de interfaz offscreen no prueban OpenGL, DPI físico o menús del juego. Mypy comprueba paths, input_limits y file_transaction; no es tipado completo del programa.

Los proyectos históricos necesarios para regresión están exclusivamente en tests/fixtures/chronicles. Los baselines de bytes, distribuciones y geometría están en tests/fixtures/baselines. Sus nombres históricos no representan proyectos visibles ni nuevas versiones del producto. No modificar hashes para ocultar fallos.

Los tres ejemplos activos están en chronicles/tutorial, chronicles/showcase y chronicles/mini_chronicle. Las dependencias están en cache/vendor, cache/devtools y cache/toolchain. tools/bootstrap.ps1 prepara el compilador y escanea el juego sin ejecutar herramientas originales de autoría.

La última revisión completa pasó 357 pruebas; sus resultados están en research/product_close/final_quality. Las comprobaciones posteriores a la limpieza se conservan junto a esa evidencia. Los casos dentro de Redemption los realiza el usuario siguiendo [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md). Generado, compilado, probado con doubles y verificado en el motor son estados distintos.

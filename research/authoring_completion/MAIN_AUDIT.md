# Auditoría vigente de main · 20/10/2026

Base comprobada: `77fae480a1025615471be8f645908bfe3e79ce9e`, coincidente con
`origin/main` al iniciar y antes de integrar. Versión conservada: **1.0.0-rc7**.
Recibo verificable: [main_audit.json](main_audit.json).

## Resultado

- Batería completa final: **634 pruebas; 0 fallos, 0 errores, 0 omisiones**.
  Ruff y el alcance configurado de mypy también pasan. No se instrumentó cobertura.
- La primera pasada completa pasó 632 pruebas. La auditoría de archivos detectó
  que las pruebas antiguas aplicaban su retención rotativa sobre backups locales.
  Se restauraron ocho copias con sus bytes exactos y se aisló esa ruta en un
  temporal exclusivo de la batería. Dos regresiones nuevas comprueban retención,
  preservación de copias previas, límites de ruta y otros workspaces. El código
  del producto y su política normal de backups permanecen intactos.
- Los siete ejemplos se recompilan contra Codex; todas las clases son 45.3 y las
  fuentes y paquetes coinciden con las huellas anteriores. No se altera el tutorial
  aceptado ni la mini crónica, ni se incluye geometría en los paquetes.
- `chronicles/new_chronicle/project.yaml` es válido, sin problemas de validación.
  Sus dos clases compilan contra Codex como 45.3 y pasan la comprobación de salida.
  El compilador emite 15 avisos de helpers/campos sin uso, sin errores.
  YAML intacto; resultado en `build/new_chronicle/new_chronicle.nob` y su
  `build_report.json`, con estado `compiled-unverified-in-game`.
- El EXE coincide con los 112 módulos fuente y sus traducciones. Las pruebas
  portables frescas en inglés y castellano pasan en carpetas movidas, con PATH
  restringido y sin abrir Redemption.
- Se retiran del índice **16** autosaves, backups y un registro rotado mediante
  `git rm --cached`; sus archivos locales se conservan y se verifican por hash.
  Las nuevas exclusiones cubren autosaves, locks RCM y rotaciones de temporales/logs.
  Se verifican ocho casos de exclusión y dos proyectos que siguen siendo versionables.
- Los **1.868** archivos de proyectos, recursos personales y copias registrados
  al iniciar siguen presentes con el mismo contenido. No se eliminan proyectos
  personales, no se modifica Redemption ni se publica ninguna release.

## Reproducir

Desde la raíz del repositorio, con las dependencias locales preparadas:

```powershell
python tools/quality.py --no-coverage
python tools/verify_frozen_sources.py
python tools/probe_product_distribution.py --game "H:\GOG\Vampire The Masquerade - Redemption" --output build/main_audit_portable --quick
$env:PYTHONPATH='src;cache/vendor'
python -m rcm.cli --workspace . --game "H:\GOG\Vampire The Masquerade - Redemption" validate chronicles/new_chronicle/project.yaml
python -m rcm.cli --workspace . --game "H:\GOG\Vampire The Masquerade - Redemption" build chronicles/new_chronicle/project.yaml
```

La prueba completa incluye los tests de interfaz offscreen y compilación; Windows
debe permitir crear los enlaces de prueba. Los resultados locales están en
`build/tests/quality_report.json`, `test_report.json` y `tests.log`. Sus huellas,
comandos y resúmenes se conservan en el recibo de esta auditoría; `final_routes.json`
enlaza las capacidades con los tests ejecutados.

## Pendiente manual / nativo

No quedan fallos automatizados abiertos. No se automatiza ni juega Redemption.
Continúan los casos de `docs/MANUAL_RUNTIME_CHECKLIST.md`: DYN01–12, COMP01–06,
guardado/carga, reentrada, cámaras/audio y red cuando corresponda. La carga y las
interacciones de `new_chronicle` requieren observación dentro del juego.
El portable en este equipo no certifica otro PC ni GPU/DPI físico; esas comprobaciones
manuales ya previstas siguen separadas. No se declara aceptación nativa del 100 %.

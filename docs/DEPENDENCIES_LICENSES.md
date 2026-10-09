# Dependencias y avisos

Inventario exacto de distribuciones instaladas y textos locales: `research/phase6/dependencies.json`, `build/portable_notices`, `THIRD_PARTY_NOTICES` del portable. Generador: `tools/license_inventory.py`. No declarar una licencia por memoria cuando METADATA no la identifica: se conserva el aviso del paquete.

Runtime: Python 3.12.14 (PSF), PySide6/Shiboken 6.10.2 (alternativas LGPL/GPL indicadas en wheel), PyYAML 6.0.3 (MIT), NumPy 2.3.5 (BSD y avisos de librerías incluidas), Pillow 12.3.0 (MIT-CMU), ECJ 3.26.0 (avisos dentro del JAR), Temurin/OpenJDK 21.0.11 (legal y excepciones dentro de runtime/legal). Qt y NumPy pueden incluir dependencias binarias adicionales: conservar sus textos completos y registrar binarios del portable antes de publicación.

Desarrollo: coverage 7.10.6, Ruff 0.14.0, mypy 1.18.2, types-PyYAML 6.0.12.20250915, PyInstaller 6.16.0 y helpers según inventario. Versiones runtime flexibles de NumPy/Pillow están en requirements-editor; la medición corresponde a las versiones exactas del inventario. Sin descarga automática de paquetes de crónica ni acceso a servicios remotos.

El portable contiene módulos Python/Qt, JVM y compiler modernos. No contiene Embrace, NOT Editor, ejecutable del juego, classes.zip original, Codex.nob, Resource.nob, modelos, levels ni texturas originales. Esos datos se leen/copian en el workspace privado al escanear la instalación legítima del usuario. Un paquete de crónica incluye únicamente nuestra capa generada y recursos propios; el metadata de entorno/anchor necesario se deriva de escenas originales.

No se ha fijado una licencia pública para el código propio de RCM ni se ha publicado la aplicación. Esta lista es inventario técnico de avisos, no aprobación legal de distribución pública. Qt permanece como bibliotecas dinámicas en carpeta visible. No entregar un EXE suelto que descarte bibliotecas, avisos y JVM.

Referencias técnicas de herramientas: [Ruff](https://docs.astral.sh/ruff/linter/), [PyInstaller onedir](https://pyinstaller.org/en/stable/operating-mode.html), [tipos PyYAML](https://pypi.org/project/types-PyYAML/6.0.12.20250915/).

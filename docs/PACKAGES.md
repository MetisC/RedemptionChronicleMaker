# Paquetes y proyectos exportables

`.rcmpack`: ZIP determinista, `manifest.json` (format 1), `<id>.nob`, `codex/*.class` 45.3. Un `.rcmproject` lleva YAML y recursos fuente propios bajo assets. No lleva modelos/geometría ni librería/API original. El juego original es dependencia obligatoria.

Manifest: ID, nombre, versión exacta, autor/descripción, requisitos, templates propios, dependencias locales, files/size/SHA-256 y indicador de Java avanzado. Todo paquete con clases contiene código ejecutable; aunque `custom_code=false` porque el generador produjo las clases, se solicita revisión antes de instalar. No hay firmas criptográficas ni sandbox del Java; los hashes sólo comprueban integridad.

Comandos: `package <id> <destino>`, `inspect-package <archivo>`, `install-package <archivo> --accept-custom-code`, `uninstall-package <id>`, `export-project <YAML> <destino>`, `import-project <archivo> <carpeta-vacía>`. Salidas dentro del workspace. Menú **Paquetes** usa el mismo backend, con revisión de nombre/versión/lista de archivos/destino.

Instalar sólo dentro de `game/RCM/<id>`, con `.rcm_manifest.json` propio. Update/Uninstall verifican hashes anteriores, conservan archivos ajenos/logs/saves y se detienen si un archivo administrado fue modificado. Backups en `research/package_backups`. Preflight de enlaces, hardlinks, rutas y temporales; rollback de archivos escritos y obsoletos ante fallo. Cada reemplazo es atómico, el conjunto no tiene aislamiento de lectores ni garantía frente a apagado repentino; Vampire debe estar cerrado.

ZIP: límite 2000 entradas y 64 MiB descomprimidos por contenedor; sin duplicados por casefold, rutas absolutas, traversal, nombres Windows reservados, ADS, enlaces o entradas de directorio. Se rechazan geometría/modelos/binarios ajenos y clases con versión incompatible. En instalación se contrasta namespace de originales con catálogo disponible. No es un antivirus ni un verificador completo de bytecode malicioso.

Dependencias: comprobación de ID/versión local exacta y bloqueo de uninstall si otra depende de ella; conflicto conservador de templates. **No hay composición de recursos entre carpetas `-user` ni resolución/transmisión de dependencias remotas.** Cada crónica debe ser autosuficiente sobre recursos originales y sus recursos propios; no prometer que declarar una dependencia hace aparecer sus assets en el motor.

GUI Deploy para el acceso conocido utiliza `RCM/east_demo`; packaging instala en carpeta individual. Si pruebas un paquete individual, tu acceso debe usar esa carpeta y se puede seleccionar mediante **Acceso del juego…**. El sistema no modifica tu acceso ni instala en directorios originales.

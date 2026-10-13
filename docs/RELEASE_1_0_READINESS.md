# IMPLEMENTED

**1.0.0-rc3.** RC3 simplifica dock/controles legacy, Ayuda/bienvenida/estado/idioma; importación segura, rechazo de formatos futuros e identidad de instalación para los catálogos. Guía humana del Showcase.  Cierre de producto: primer arranque, selección de Vampire.exe, preferencias globales migradas sin borrar las antiguas, proyectos fuera del programa, bienvenida/recientes, nombre y escenario al crear, F5 con construcción y despliegue sólo cuando hace falta, ejecución directa por crónica y seguimiento de sesión. Versiones guardadas, recuperación, locks y detección de cambios externos. Tutorial aceptado intacto; Showcase separado con tres escenas, dos escenarios y laboratorio opcional. Portable curado, sin accesos personales ni originales del juego.

# VERIFIED OFFLINE

376 pruebas pasan sin fallos/errores/skips, con Ruff y los tipos configurados: research/rc3/quality. Los ocho recorridos del EXE y sus capturas se conservan en research/rc3/portable. Tres ejemplos compilados contra Codex real en 45.3. El YAML y las clases del tutorial coinciden con rc1. Los probes de Qt crean una aventura, usan asistentes, guardan/reabren, compilan y despliegan en un juego sintético. El EXE se ha probado con perfiles nuevos y PATH sin Python/JDK global en rutas con espacios y ñ, en ambos idiomas. Esto es el mismo PC; no prueba una máquina limpia ni OpenGL nativo. Los 1787 archivos del workspace antiguo se conservan con hashes idénticos fuera del programa.

# VERIFIED IN REDEMPTION

Se conserva la confirmación del usuario del 13 de octubre: «Funciona correctamente» para el recorrido del tutorial, junto al log de viaje, entrega, flag y quest completada. Evidencia: research/native_acceptance/native_acceptance.json. Esta revisión no automatiza ni abre Redemption; no extiende aquella aceptación al nuevo lanzamiento por carpeta, Showcase, todas las cargas/reentradas ni red.

# REQUIRES HUMAN RUNTIME TEST

**MANUAL RUNTIME TEST REQUIRED.**

Sigue docs/MANUAL_RUNTIME_CHECKLIST.md: primer arranque real, F5/tutorial, estaciones del Showcase, guardado/carga/reentrada y cambiar una frase/probar. Verificar especialmente LAN cuando el personaje conserva un objeto RCM de otra crónica. La compatibilidad reutiliza sólo definiciones/clases propias verificadas y no modifica Crypt; su prueba offline no demuestra la carga nativa. Portable en PC/VM independiente y DPI físico siguen pendientes. No se declara 1.0 final.

# DEFERRED POST-1.0

Geometría, escritor NCP, cámara XYZ/FOV arbitraria, puertas universales, eliminación universal de estática, AI avanzada, audio persistente avanzado y red verificada. Travelling original/puertas concretas/NOT permanecen Advanced o Experimental con sus límites. Extras de bajo riesgo no incluidos: instalador, selector de temas, preview de recursos y Ctrl+P. Secundarios parciales: acceso opcional en Escritorio, seguimiento continuo del trace y comparador de versiones de ejemplos.

# KNOWN ISSUES

El Showcase y el nuevo circuito de producto están compilados y verificados offline; requieren aceptación humana. Un efecto nativo y su checkpoint no son una transacción atómica. No hay migración de saves estructurales. La geometría y el suelo comprobados no garantizan pathfinding/colisión. La preferencia de idioma/carpeta/visor se aplica al reiniciar. El plano inicial del tutorial fue percibido como lejano y se conserva. Los informes históricos no sustituyen esta evidencia.

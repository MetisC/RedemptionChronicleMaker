# Primer arranque · RC4

El EXE empaquetado recorre widgets Qt reales: preferencias nuevas, elección de Vampire.exe, validación, preparación del catálogo, bienvenida, creación de aventura, entrada, NPC/conversación/zona/misión, undo/redo, guardar y reabrir, compilación Codex 45.3 y despliegue sintético. También abre tutorial, guía del Showcase, vista global, gráfico y Configuración.

Se comprueban dock oculto en bienvenida/proyecto válido, errores y referencias que lo abren, siete pestañas, conversión legacy oculta para proyectos modernos, instalación secundaria y selector único de idioma. Se inspeccionaron las capturas de bienvenida, guía/vista global y Configuración.

Ocho ejecuciones correctas: primer/segundo arranque ES y EN en dos carpetas alternativas (con espacios y ñ), más escalas Qt 1, 1.25, 1.5 y 2. PATH contiene sólo System32; Python y JVM globales no son necesarios. El segundo arranque valida identidad y reutiliza catálogo. La preparación inicial tarda unos 13 segundos y la segunda unos 2,3 segundos en este equipo; no son tiempos garantizados.

Evidencia: research/dynamic_encounters/portable/summary.json y capturas en sus carpetas scale_*. Los despliegues son sintéticos. No se lanzó ni se escribió en el juego real. Offscreen/safe mode no prueban OpenGL real, DPI físico, otra máquina ni LAN.

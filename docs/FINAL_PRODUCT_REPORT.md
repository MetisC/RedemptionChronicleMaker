# Cierre de producto · 1.0.0-rc3

**RC3 APROBADA PARA PRUEBA MANUAL. MANUAL RUNTIME TEST REQUIRED.**

Esta candidata simplifica el producto existente. No declara 1.0 final ni aceptación nativa del Showcase. La revisión no abrió ni automatizó Redemption.

## 1. Cambios realizados

- **Paneles:** dock inferior oculto al iniciar, abrir un proyecto válido y restablecer disposición. Errores, referencias y construcción abren la sección correspondiente. La validación limpia no abre el dock ni cierra uno abierto explícitamente.
- **Campaña:** conversión ofrecida sólo para documentos legacy; conserva la conversión existente. La pestaña se llama Campaña / Vista global (Campaign / Overview).
- **Apertura y formatos:** importar pasa por open_path, con locks, recientes, recuperación, validación y liberación del proyecto anterior. La versión actual se centraliza en 9; los formatos futuros se rechazan antes de escribir.
- **Presentación:** un selector de idioma en Configuración, nombres claros en Ayuda, bienvenida con creación/apertura prioritarias, instalación secundaria y estado humano basado en ProjectStatus. ES/EN revisados. Las rutas de la ficha de crónica quedan en tooltip; la explicación indica F5 en lugar de carpetas internas.
- **Catálogos y Showcase:** identidad por contenido de instalación; guía humana y nombres naturales conservando referencias y lógica. Detalles abajo.

## 2. Cosas eliminadas

CampaignPanel perdió los controles ocultos Guardar, Integridad, Deploy, Ejecutar, Ruta del juego y Acceso del juego. Se eliminaron sus métodos deploy, run_game, game_settings y game_shortcut, sin eliminar las operaciones vivas del backend. El menú Añadir usa acciones directamente, sin crear botones para mantenerlos ocultos.

Se retiraron el menú de idioma duplicado y su callback, y una acción de diagnóstico duplicada en Ayuda. Playtest / Debug reutiliza F5. Permanecen el diagnóstico útil, la construcción avanzada y las herramientas de recuperación. Se retiraron los paquetes RC2, las carpetas de pruebas generadas y sus duplicados; los informes actuales quedan en research/rc3. Las fuentes históricas necesarias para regresión siguen sólo en tests/fixtures.

## 3. Deliberadamente sin cambios

No hay nuevas pestañas, gestores, onboarding, dashboard, capacidad runtime, editor geométrico ni sistema de migraciones. Siguen siete pestañas.

Se conservan guardado atómico/fsync/os.replace, backups, recuperación, cambios externos, QLockFile, validación, transacciones de build/deploy, límites de paquetes, F5 y protección de originales. Los generadores y runtime narrativo no se han reescrito. El YAML del tutorial aceptado, sus recursos Java y sus clases vigentes se comparan con el checkpoint anterior. La lógica/IDs/eventos del Showcase se fijan mediante una comparación normalizada, permitiendo únicamente nombres/comentarios y Victoria → Anezka en textos.

## 4. Tests

| Resultado | Total |
|---|---:|
| PASS | 376 |
| FAIL | 0 |
| ERROR | 0 |
| SKIP | 0 |

Ruff pasa. Mypy pasa en los tres módulos configurados (no supone tipado completo). Hay 19 casos específicos RC3: formatos y rechazo seguro; identidad/cache/equivalencia de ruta; preservación de proyectos/recursos/backups; dock; conversión; importación/locks/recientes/cancelación; controles retirados; bienvenida/ayuda/estado; propiedades y guía/lógica del Showcase. La suite completa añade regresiones de guardado, transacciones, API, bytecode, formatos y harness Java con doubles.

Evidencia: research/rc3/quality/test_report.json, quality_report.json y tests.log. Los tres ejemplos compilan contra Codex real en Java 45.3; estado **compiled-unverified-in-game**.

## 5. GUI probe

Ocho ejecuciones del EXE congelado: primer/segundo arranque EN y ES desde rutas alternativas con espacios/ñ, y escalas Qt 1, 1.25, 1.5 y 2. PATH restringido a System32.

Se recorren widgets reales de setup, bienvenida, creación, entrada/NPC/conversación/zona/misión, undo/redo, guardar/reabrir, compilación, despliegue sintético, tutorial/Showcase, enlaces/gráfico, vista global y Configuración. Se verifican dock, conversión, siete pestañas y selector único. Se revisaron visualmente las capturas de bienvenida, guía/vista global y Configuración.

Evidencia: research/rc3/portable/summary.json y capturas. Offscreen/safe mode en el mismo PC **no prueba** OpenGL real, DPI físico ni una máquina independiente. No se interactuó con menús ni partida del juego.

## 6. Showcase

La guía comienza con dónde empezar y el encargo del libro, sigue la ruta taller → archivo → regreso y presenta aparte el laboratorio opcional: cámaras, animaciones, recorridos, sonido, objetos/notas y combate. Después queda la prueba de campo y, al final, el índice técnico completo. Todos los enlaces se conservan y resuelven a entidades reales.

Los nombres se emiten a NLS y los NOT remiten a esas cadenas: por ello los personajes/objetos muestran nombres naturales como Anezka, Guía o Rata de las minas. Los antiguos rótulos didácticos se conservan en el comentario visible como tooltip del editor. Esta conclusión procede del generador, no de una observación nativa RC3.

## 7. Cache / instalación

La identidad usa nombres relativos, tamaños y SHA-256 de NOB, Vampire.exe, classes.zip y Chronicles. Los recursos de audio sueltos se indexan por nombre/tamaño. Cambiar sólo la ruta con los mismos bytes no reconstruye; cambiar contenido o corromper identidad/catálogos sí reconstruye.

Se invalidan índices y extracciones derivados de forma acotada. Proyectos, fuentes Java/imágenes propias, backups y compilador permanecen. Las mallas/texturas conservan claves por contenido. La copia de classes.zip se refresca cuando cambia; la identidad sólo se publica al completar el escaneo. Las pruebas de cambio usan instalaciones sintéticas; el probe real demuestra primer/segundo arranque sin rescan repetido.

## 8. Compatibilidad

Se conservan schema 1 legacy y campañas schema 2 admitidas por los lectores existentes. RC3 prueba directamente formato 9, formato 5 y ausencia de project_format, además de las regresiones históricas. La conversión legacy no se elimina. No se promete admitir cualquier formato antiguo desconocido.

project_format mayor que 9 produce un aviso de actualizar RCM, sin migrar, sobrescribir, importar ni aplicar recuperación a la crónica abierta. El formato no cambia por abrir. La suite mantiene los límites de paquetes y seguridad existentes.

## 9. Runtime

**MANUAL RUNTIME TEST REQUIRED.** Se conserva la aceptación histórica del tutorial («Funciona correctamente»), con su alcance y evidencia en research/native_acceptance. No equivale a aceptar RC3, Showcase, save/load/reentrada completa ni red.

Los 43 archivos originales del manifiesto conservan sus hashes. No se ha escrito, desplegado ni lanzado el juego real durante RC3. Seguir MANUAL_RUNTIME_CHECKLIST.md: F5/tutorial, estaciones del Showcase, guardar/cargar/reentrar, personaje con objeto RCM anterior y cambiar una frase/probar. La máquina independiente, GPU y DPI físico también quedan pendientes.

## 10. Veredicto y entrega

**RC3 APROBADA PARA PRUEBA MANUAL.** La puerta offline y el probe del editor empaquetado pasan. No se declara 1.0 definitiva ni runtime PASS.

Abre Redemption Chronicle Maker.lnk en la raíz; apunta al EXE RC3 en build/portable/RedemptionChronicleMaker. build conserva sólo el portable y los tres ejemplos actuales. La entrega de usuario es RedemptionChronicleMaker-1.0.0-rc3-win64.zip; el archivo privado de workspace es separado. release_manifest.json y SHA256SUMS.txt identifican los paquetes verificados. Los proyectos recuperados del usuario permanecen fuera del programa.

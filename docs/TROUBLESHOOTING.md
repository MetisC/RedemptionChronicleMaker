# Resolución de problemas

| Síntoma | Acción |
|---|---|
| No aparece la campaña | Usar la carpeta de `-user` del acceso. NOB en raíz, `codex/*.class` dentro de esa carpeta. Cerrar Vampire antes de Deploy. En este equipo: `RCM/east_demo`. |
| Pide CD key con Ejecutar | Seleccionar **Acceso del juego…** y usar el acceso del escritorio que funciona. El editor lo abre directamente; no lo reconstruye. La causa exacta del comportamiento distinto del ejecutable directo no se ha establecido. |
| Campaña vieja / build anterior | Una validación/compilación/publicación fallida bloquea Deploy y Package. Revisar `build_report.json`, recompilar y empezar una partida nueva. |
| No se ve un NPC | Elegir una fixture `near_player` para comprobar primero callbacks. XYZ válida como dato no garantiza suelo/colisión. En el editor seleccionar actor y F para enfocarlo. |
| Fondo extraño | EastLondon conserva el entorno original gris; no añadir un sky artificial como reparación. El viewport no reproduce niebla/iluminación del motor. |
| Cursor/UI tras diálogo | Regresión reportada en Fase 5. El controlador actual prepara feedback antes de Execute y libera cámara en retorno, aborto y fallo. Pruebas offline pasan; repetir rechazo y aborto en juego según checklist. |
| Catálogos ausentes/corruptos | El arranque del editor conserva copias y reconstruye leyendo el juego. CLI: `scan --no-disassemble`. No redefinir un baseline original que ha cambiado. |
| Pantalla negra o crash gráfico | Arrancar `--safe-mode`; no crea OpenGL. `--reset-settings` respalda configuración. No modifica ajustes gráficos del juego ni Windows. |
| Java no compila | Ver `build/failed_attempts/<id>_<intento>/...compiler.log`, fuentes y source_map. El fallo no publica una distribución parcial. |
| Falta compiler / JVM | Portable necesita carpeta completa y `runtime/bin/java.exe`. Fuente necesita ECJ verificado y JVM. No usar javac moderno para producir clases del juego. |
| Archivo instalado modificado | Install/Uninstall se detienen y conservan el archivo. Revisar la diferencia y las copias en `research/package_backups`; no borran partidas ni logs ajenos. |
| Ruta rechazada | Salidas dentro del workspace; despliegue dentro de RCM. No usar enlaces, junctions, hardlinks, nombres Windows reservados ni rutas de escape. |

**Ayuda → Informe de diagnóstico**, o `tools/rcm.py diagnostics`, escribe `build/diagnostics/report.json`. Es local; no envía telemetría ni archivos. Incluye versiones y errores de índices. Revisa su contenido antes de compartirlo.

No hay cancelación de compilación activa. El editor bloquea cambios/cierre mientras termina el worker. Si un proceso externo interrumpe el programa, la validez del build debe comprobarse en su manifest; reiniciar y recompilar.

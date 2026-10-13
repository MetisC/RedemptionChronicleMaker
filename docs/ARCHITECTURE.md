# Arquitectura actual

El YAML es la fuente de autoría. El editor y la CLI comparten Backend, validación, catálogos y generadores. No existe un compilador narrativo paralelo ni un formato privado de interfaz.

```text
Instalación original (lectura) → catálogos y recursos
YAML → modelo → validación → Java y formatos runtime → ECJ → readback → paquete
                                            ↓
                                 despliegue acotado a RCM
```

Cada escena selecciona geometría y entorno por separado y contiene sus propios actores, objetos, entradas, recorridos, eventos, conversaciones y secuencias. Los lectores espaciales alimentan el viewport y raycasting; no se genera ni modifica geometría. scene_profiles valida el NSD y conserva sus 176 bytes de entorno. Véase [SCENE_MODEL.md](SCENE_MODEL.md).

CampaignDocument mantiene una única fuente, referencias, undo y edición de la escena activa. Los asistentes agregan metadatos editables sin introducir un ejecutor alternativo. Las acciones se generan en Java contra Codex real, con flags y records explícitos para persistencia; cambiar su contrato puede exigir una partida nueva.

Las preferencias globales, la instalación y el directorio de proyectos están separados del programa. La bienvenida copia ejemplos a proyectos editables. Guardado atómico, bloqueo entre ventanas, comprobación de cambios externos y recuperación protegen el trabajo. El portable incluye Python, Qt, ECJ y JVM; los recursos originales se indexan desde la instalación del usuario.

El build usa un directorio provisional, comprueba formatos, referencias, versión Java 45.3 y presupuestos de bytecode antes de publicar. Los fingerprints impiden desplegar una construcción desactualizada. Las transacciones verifican propiedad y hashes, publican el manifest al final y restauran ante fallos; no garantizan aislamiento frente a lectores concurrentes ni todos los cortes de alimentación.

F5 prepara, compila si hace falta, despliega a la carpeta de la crónica y lanza Redemption. Los menús y la partida los controla el usuario. profile_compatibility conserva definiciones propias requeridas por inventarios persistidos sin alterar el perfil del jugador.

Los paquetes validan tamaños, rutas, hashes, conflictos y dependencias. Importar fuentes no ejecuta Java. La apertura del proyecto importado usa open_path, con los mismos locks, recientes, recuperación y validación que una apertura normal. Las clases instaladas requieren revisión; no se afirma que tengan sandbox o firma de confianza. La instalación original permanece de lectura fuera de RCM.

Los recursos técnicos extraídos se conservan en research/original y cache. Las referencias del SDK están en research/sdk; los baselines de regresión, en tests/fixtures. La evidencia actual, límites y pruebas manuales están en [FINAL_PRODUCT_REPORT.md](FINAL_PRODUCT_REPORT.md) y [MANUAL_RUNTIME_CHECKLIST.md](MANUAL_RUNTIME_CHECKLIST.md).

La identidad de instalación usa nombres relativos, tamaño y SHA-256 de los archivos principales (archivos NOB, Vampire.exe, classes.zip y Chronicles). Una ruta diferente con los mismos bytes reutiliza el catálogo. Un cambio de contenido reconstruye sólo los índices y extracciones derivados; proyectos, recursos propios, backups y compilador permanecen. La identidad se publica al terminar el escaneo. Los cachés de mallas/texturas siguen ligados a sus propios hashes.

CURRENT_PROJECT_FORMAT centraliza la versión 10. Los documentos 9 se abren sin convertir; añadir el primer encuentro dinámico crea un backup y ofrece una modificación optativa que se puede deshacer. Los formatos futuros se rechazan antes de modificar, importar o recuperar.

RC4 añade scene.generators sobre los encuentros authored existentes. El asistente usa waypoints, eventos y acciones normales; las fases se bajan a eventos internos en una copia del modelo. Sólo el runtime de formato 10 incorpora la extensión dinámica. Usa el poll de escena, arrays acotados de GUID/roles y records nativos. Antes de crear después de una carga reconcilia plantilla, localidad y propiedad; un registro perdido detiene el encuentro para evitar duplicados. Dos flags por generador protegen inicio/finalización entre instancias; los checkpoints narrativos existentes controlan recompensas. No hay un ejecutor de eventos paralelo. Véase DYNAMIC_ENCOUNTERS.md.

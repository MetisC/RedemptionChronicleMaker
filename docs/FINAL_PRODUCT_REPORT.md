# Producto vigente · 1.0.0-rc7

RCM crea crónicas sobre geometría original inmutable mediante autoría visual,
formatos propios y originales generados directamente, y Java compilado contra
Codex. No ejecuta herramientas originales de autoría. Se mantienen formatos 9/10
y rc7; no se declara 1.0 final ni paridad Embrace del 100 %.

## Autoría y límites actuales

El editor conserva escenas, actores/objetos, interacciones al pulsar, diálogos,
notas, quests, flags, inventarios, encuentros dinámicos y Director cinematográfico.
Los cambios nuevos son optativos, accesibles desde los paneles existentes:

- Mapas visuales propios: imagen, puntos arrastrables, nombres, visibilidad,
  refugios y enlace de escenas, con NUI/TGA/NLS/NSC generados directamente.
- Regiones nativas caja con malla/sectores enlazados; scripts y parámetros
  region/item, además de escalares/actor/thing/frames anteriores. 440 constructores
  unívocos catalogados; propiedad y callbacks nativos separados de eventos RCM.
- Objetivos dinámicos por generador/rol/ordinal para cámara, gesto, movimiento,
  recorrido, inventario, comportamiento y audio/luz. Son vistas transitorias del
  roster GUID existente, sin otra instancia ni gestor ni registros alias de save.
- Giros y esperas estacionarios temporizados mediante NCP propios; modo anterior
  por distancias y174 originales conservados.
- Zonas activadoras de sonido y luz sobre los triggers/handles existentes,
  alternativa funcional explícita al recorte literal de cajas por sectores.
- EAX optativo mediante comando original roomtype después de cargar; requiere
  proveedor 3D compatible para efecto audible. Tail estático original intacto.
- Clanes y disciplinas base accesibles sin mod; WTD continúa siendo optativo.
- Entorno, propiedades por instancia, TreasureClass, interestspots, bibliotecas
  locales y dificultad anteriores conservados.

Uso, archivos y seis comprobaciones breves: AUTHORING_COMPLETION.md.
Cobertura completa y estados: EMBRACE_AUTHORING_PARITY.md. Evidencia:
research/authoring_completion/EVIDENCE.md. No se declara el 100 %: siguen desconocidos
el binding seguro de constructores CodexPlayer de campaña y el payload/recorte
literal soundbox/lightbox. No se presentan como imposibles. Hay rutas normales
Player Actions y zonas activadoras para los usos habituales. El NCP no contiene
FOV por keyframe; las bibliotecas de datos no importan código binario desconocido.

## Dificultad de combate

Las propiedades generales ofrecen Fácil, Normal, Difícil y Pesadilla. La ausencia
del campo equivale a Normal; no convierte el formato del proyecto.

| Dificultad | Salud / máxima | Fuerza base / actual | Resistencia base / actual |
|---|---:|---:|---:|
| Fácil | ×0,80 | ×0,90 | ×0,90 |
| Normal | ×1,00 | ×1,00 | ×1,00 |
| Difícil | ×1,20 | ×1,10 | ×1,10 |
| Pesadilla | ×1,50 | ×1,20 | ×1,20 |

Sólo escala enemigos nuevos controlados por RCM. Primero se aplica la salud
individual del encuentro, después la dificultad y finalmente se captura la base
del jefe. No altera jugadores, aliados ni neutrales; no vuelve a escalar GUID
existentes al cargar o reentrar. No añade registros al guardado. Normal no emite
el helper y conserva los bytes de salida anteriores en las regresiones.

Los factores son de atributos, no porcentajes directos de daño. Se respetan los
límites nativos. Destreza, absorciones por tipo de daño, equipo, disciplinas,
experiencia y recompensas permanecen iguales. Cambiar dificultad recomienda una
partida nueva para evitar enemigos antiguos y nuevos con escalas distintas.
La evidencia y pruebas están en research/combat_difficulty/EVIDENCE.md.

## Mapas y localizaciones

El editor permite imágenes y localizaciones propias mediante Mapas y localizaciones.
Los mapas son informativos como en el juego original: nombres al señalar,
visibilidad/descubrimiento y refugios; no se atribuye viaje al pulsar. La imagen
original sólo se referencia; una imagen nueva pertenece al autor del proyecto.

## Contenido preservado y ejemplos

Se conservan el tutorial aceptado «Una carta al amanecer» en formato 9, la mini
crónica, el laboratorio dinámico, el Showcase y los proyectos personales. EastLondon
conserva su entorno gris original. No se modifica su geometría ni se añade un
cielo experimental para corregirlo.

Arrival at the refuge y Cargo at the refuge son ejemplos independientes en Ayuda.
El segundo permite comprobar entorno, overrides, contenedores, script nativo y
grupos de interés sin reescribir el tutorial. Su observación nativa queda pendiente.

## Evidencia y verificación

Los resultados vigentes de la batería completa se guardan en
build/tests/quality_report.json y test_report.json; el recibo de esta entrega es
research/authoring_completion/delivery.json. Se separan suite completa, Ruff/mypy,
compilación real Codex JVM 45.3, doubles y transacciones Qt. El recibo recoge el
resultado real al terminar; la investigación no acredita gameplay nativo.

Las ventanas nuevas se han inspeccionado offscreen en inglés y castellano con
fuentes reales; cancelar conserva el proyecto. El portable se reconstruye sin
cambiar versión ni publicar release. Movimiento de carpeta, idioma y PATH
restringido son probes en este equipo, no PC independiente, GPU/DPI físico ni
observación del juego. No se incluyen assets originales de juego o mods.

El usuario confirmó anteriormente el tutorial, la reparación del clic/primer
desplazamiento y la carga inicial corregida del Taller («Funciona bien y abre»,
18/10/2026). Esto no certifica nuevos mecanismos, save/load, reentrada o red.
Los casos EMB01–24, DYN01–12, EMB-MUSIC/CONV/NCP, nuevos EMB-ENV/TEMPLATE/
TREASURE/CODEX/INTEREST/LIBRARY y DIFF01–06 siguen en MANUAL_RUNTIME_CHECKLIST.md.
COMP01–06 cubre las adiciones actuales. El usuario realiza esas pruebas; no se automatiza Redemption.

## Alcance

Geometría, CSG, UV/texturizado estructural, lightmaps y edición estructural de
sectores/portales quedan fuera de alcance. Las fuentes originales se usan en
lectura; las comprobaciones de despliegue usan instalaciones sintéticas dentro
del workspace. Esta entrega no modifica la instalación real del juego.

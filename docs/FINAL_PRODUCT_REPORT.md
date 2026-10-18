# Producto vigente · 1.0.0-rc7

RCM crea crónicas sobre geometría original inmutable mediante autoría visual,
formatos propios y originales generados directamente, y Java compilado contra
Codex. No ejecuta herramientas originales de autoría. Se mantienen formatos 9/10
y rc7; no se declara 1.0 final ni paridad Embrace del 100 %.

## Autoría y límites actuales

El editor conserva escenas, actores/objetos, interacciones al pulsar, diálogos,
notas, quests, flags, inventarios, encuentros dinámicos y Director cinematográfico.
Los cambios nuevos son optativos:

- Entorno inicial: música/ambiente y volúmenes, niebla, distancia de visión y
  pareja de cielo compatible. Se modifica el NSD generado; EAX original se hereda.
- Plantillas e instancias: AI, Foley, motions y texto al señalar. Los contenedores
  ofrecen heredar, desactivar o seleccionar TreasureClass de GAME.NTT.
- Scripts nativos: constructor real, parámetros tipados, enlaces a entidades y
  frames de movimiento. El script conserva sus callbacks y estado. No todos los
  contextos regionales de scripts originales son seguros en una entidad genérica.
- Interestspots: función opcional de waypoint con grupo nativo; no se equipara a
  un recorrido de patrulla.
- Bibliotecas NOT/NOB locales: importación de datos seleccionados y dependencias,
  con gestión de retirada y protección de referencias. No se importa código
  binario externo arbitrario ni interfaces/crónicas del mod. Los recursos ajenos
  no se redistribuyen dentro del programa ni del ZIP público de una crónica.
- Dificultad por crónica, descrita a continuación.

La matriz estricta vigente es EMBRACE_AUTHORING_PARITY.md. EAX editable, regiones
nativas generales, soundboxes/lightboxes y duración de giros NCP estacionarios
siguen siendo límites concretos, con evidencia en
research/embrace_strict_parity/SAFETY_DECISIONS.md. No se ocultan bajo la exclusión
de geometría. La compilación y las pruebas offline no certifican su comportamiento
en Redemption.

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

Los ocho mapas NUI originales, sus teselas TGA y las referencias NSC/NLS permiten
crear ilustraciones, puntos, nombres y visibilidad propios sin editar NIL.
El mapa original muestra información al señalar; no implica viaje al pulsar.
Actualmente RCM hereda metadatos del mapa y no ofrece un editor de mapas.
research/embrace_strict_parity/MAPS.md distingue viabilidad de implementación.

## Contenido preservado y ejemplos

Se conservan el tutorial aceptado «Una carta al amanecer» en formato 9, la mini
crónica, el laboratorio dinámico, el Showcase y los proyectos personales. EastLondon
conserva su entorno gris original. No se modifica su geometría ni se añade un
cielo experimental para corregirlo.

Arrival at the refuge y Cargo at the refuge son ejemplos independientes en Ayuda.
El segundo permite comprobar entorno, overrides, contenedores, script nativo y
grupos de interés sin reescribir el tutorial. Su observación nativa queda pendiente.

## Evidencia y verificación

La batería completa pasó 567 pruebas, sin fallos, errores ni omisiones. Ruff y
el alcance configurado de mypy también pasaron. Los resultados vigentes están
en build/tests/quality_report.json y test_report.json. El recibo de esta entrega está en
research/embrace_strict_parity/delivery.json. Distingue suite completa, Ruff/mypy,
compilación real Codex JVM 45.3, doubles, transacciones Qt y ejecutable portable.
La suite no se presenta como gameplay real ni como cobertura total de código.

El portable se comprueba en inglés y castellano desde carpetas movidas,
espacios/unicode, configuración nueva y PATH restringido. Son probes offscreen
en este equipo; no equivalen a PC independiente, render OpenGL real, GPU ni DPI
físico. El ZIP público se audita y todos sus archivos se verifican por hash.
El programa no incorpora los archivos originales del juego ni de mods importados.

El usuario confirmó anteriormente el tutorial, la reparación del clic/primer
desplazamiento y la carga inicial corregida del Taller («Funciona bien y abre»,
18/10/2026). Esto no certifica nuevos mecanismos, save/load, reentrada o red.
Los casos EMB01–24, DYN01–12, EMB-MUSIC/CONV/NCP, nuevos EMB-ENV/TEMPLATE/
TREASURE/CODEX/INTEREST/LIBRARY y DIFF01–06 siguen en MANUAL_RUNTIME_CHECKLIST.md.
El usuario realiza esas pruebas; no se automatiza Redemption.

## Alcance

Geometría, CSG, UV/texturizado estructural, lightmaps y edición estructural de
sectores/portales quedan fuera de alcance. Las fuentes originales se usan en
lectura; las comprobaciones de despliegue usan instalaciones sintéticas dentro
del workspace. Esta entrega no modifica la instalación real del juego.

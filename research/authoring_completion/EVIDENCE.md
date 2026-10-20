# Evidencia vigente del cierre de autoría

Base de trabajo: main; commit y hashes del cierre en delivery.json.
Instalación examinada sólo en lectura.
SHA256 Vampire.exe:62982319c28b18654585239a814a5a1002c415febe07b494735cb80272c5dd23.
Las direcciones siguientes son VA de ese binario; no son offsets de otros builds.
Ninguna herramienta original de autoría ni el videojuego se ejecutó para estas pruebas.

## CONFIRMADO EN ARCHIVOS ORIGINALES / EJECUTABLE

### Reverberación efectiva por otra vía

El tail NSD+76 conserva la prioridad estática descrita anteriormente. Esto no
impide una llamada después de activar la escena:

- Registro de comando406563: handler409150 y nombre4f67bc=`roomtype`.
- Handler409150: parsea un entero con `%d` y llama49e400.
- Setter49e400: proveedor `[this+1830]` no nulo, valor unsigned<26; guarda en
  this+f70 y llama IAT4eb348=`_AIL_set_3D_room_type@8`.
- La activación de escena42c71e usa el mismo setter. Evidencia desensamblada en
  eax_console_registration.txt, eax_native_xrefs.txt y eax_setter_calls.txt.
- CodexConsole.Execute(String):boolean existe en las clases reales/API.

Implementación: comando literal con número validado0..25, una aplicación después
de beginscene/restore y acciones explícitas. Se conserva el tail original.
**Execute=true no garantiza efecto audible**: el setter puede no disponer del
proveedor 3D requerido. No se anuncia simulación de EAX en hardware sin soporte.

### Regiones y constructor linker

native_regions_corpus.json compara51 regiones originales: tags, transformación,
bounds locales, materiales y sectores. El loader NSD4a881d..4a88b6 acepta links
en entidades type3 y los registra en listas nativas de los sectores NIL. Cada
sector tiene32 slots; los links no son una modificación del archivo NIL.
El bloque es u32count seguido de índices u32, después de brush/planos y antes
del bloque de iluminación. _region y trigger_region demuestran type3.

Ejemplos de descriptor y dato original: GOLDD_4_1 `(LCodexRegion;)V`, kind5;
FLS2_MeetVuk kinds8,5,8,3; TOL4_30_1_Main primer parámetro CodexItem, kind10.
El catálogo visual admite440 constructores unívocos,60 adicionales respecto al
baseline380; las entradas anteriores y sus tipos/labels siguen comprobadas.
script_contexts.json inventaría252 clases con constructores y callbacks para
auditar entered/exited/clicked/beginscene/convreached y dependencias de campaña.

Implementación acotada: caja yaw-only del trigger existente, malla local con
seis planos, sectores que intersectan la caja y parámetros tipados. La caja se
crea en el NSD propio antes de fijar índices. Puede tener script o estar enlazada
desde otro controlador. Sus scripts conservan callbacks/guardado nativos; no se
capture/pausa el script original desde el runtime RCM. Máximo8 cajas de autoría;
no se reescriben brushes originales ni caras/sectores/UV/lightmaps del NIL.

### Cámara estacionaria temporizada

La conclusión anterior mezclaba el builder por distancias con el lector/evaluador:

- Builder431110 salta los segmentos de distancia cero; sigue siendo cierto.
- Writer431530 y reader431600 escriben/leen104bytes por registro sin recalcular.
-430350 avanza el parámetro mediante deltaTime×rate.
-430479..4304bd selecciona tramo y calcula u=(parameter-base)×inverse_span.
-4304ea..43069a evalúa XYZ y Euler de forma independiente.

Por tanto un NCP generado directamente puede usar segundos como parámetro,
rate1 y tramos positivos aun con deltaXYZ=0. Euler variable produce giro y Euler
constante espera. RCM escribe el subconjunto lineal, no emula el suavizado cúbico
del builder antiguo. La restricción previa permanece en modo por distancia.
Todas las174 rutas originales mantienen roundtrip sin pérdidas. No hay campo
FOV por key en estos104bytes; el wrapper46e1a0 pasa una lente fija por separado.
Fuente desensamblada: research/embrace_closure/native_ncp.txt.

### Mapas

MAPS.md y map_catalogue.json prueban ocho NUI originales con12teselas TGA,
imagearray16×16, texto mapLocations, cierre y unión NSC/NLS. Callbacks410d89..410e9e
y4112bd..4112d2 muestran texto/visibilidad, sin viaje al pulsar. Las APIs reales
Get/Set/ClearLocationFlags manejan SHOWINMAP8 y HAVEN16. Generación propia usa
IDs separados y la imagen del autor; no incorpora imágenes del juego.

### Control de actores y recursos

Los alias leen los slots GUID/rol existentes: no son entidades nuevas, no llaman
a spawn/capture ni añaden registros alias al save. Se resuelven sólo con roster
configurado, reconciliado, local, actor vivo y plantilla compatible. Cámara fija
el GUID seguido y cancela si cambia. La ordinalidad es sobre vivos actuales,
no identidad persistente de un individuo. Las pruebas no atribuyen al contrato
de propiedad existente una detección universal de GUID extranjero de igual tipo.
La limpieza de luz dinámica vuelve a comprobar ese mismo roster/rol/propiedad
antes de retirar una luz anterior: si la identidad deja de ser fiable, conserva
el recurso ajeno. El doble incluye sustitución por otra plantilla.

Movimiento, animación, team/pause, inventario, cámara, sonido vinculado a GUID y
luces usan las mismas APIs reales del runtime anterior; no hay otro gestor de
combate/actores. Clanes y disciplinas base proceden de misc/game.ncd y game.ndd;
sólo se ofrece una disciplina con su clase real disponible. WTD sigue optativo.

### Los seis constructores CodexPlayer

`final_probe.py` reproduce la lectura de clases, parámetros NSD y el resolver;
`final_original_evidence.json` recoge hashes y referencias. En Resource.nob:

| Script/escena | Índice nativo kind9 | Plantilla enlazada |
|---|---:|---|
| ARC3_Erik / ARC3_17_1 | 10 | erik |
| DOCK_33_1_Main / DOCK_33_1 | 8 | samuel |
| HILL_13_1 / HILL_13_1 | 2 | serena |
| TEN1_28_1_MeetPink / TEN1_28_1 | 4 | pink |
| UNIV_7_7 / UNIV_7_7 | 0 | wilhem |
| WAR3_Main / WAR3_36_1 | 15 | wilhemmod |

Son plantillas kind7 players, derivadas de _player_DA/_player_MD, no actores
ordinarios kind0. El resolver4b5260 usa la tabla de colocación, GUID+20; el switch
4b5608 lleva kinds3/5/8/9/10 a4b5347. Su ruta de restauración puede recibir GUID
ya resueltos. No existe aquí un token «jugador humano actual». CodexPlayer(int)
envuelve ese GUID; CodexPlayer() consulta GetCurrentPlayer, no crea un jugador.

Además, los seis constructores hacen GetChronicleScript(0) y cast a
PragueChronicle/LondonChronicle/NewYorkChronicle. También presuponen CastIDs,
quests, diálogos y recursos de su campaña; algunos reclutan/capturan compañeros.
Ligar el PJ humano no resuelve estas dependencias y no es equivalente a los
compañeros originales. No tienen override save/restore propio: eso NO prueba
semántica completa de reenganche. Se conserva la propiedad nativa de los scripts
reutilizables soportados. Los seis privados no se ofrecen como portables.

### Payload de iluminación y lente

Loader4a88d1..4a895a: u32count acotado10000 y llamada4c44c0 para objeto de render.
El lector4c44c0 reserva count×4, lee dwords y reparte el array entre grupos de
malla (registros28bytes, número de vértices en+0x12). Véase
light_payload_reader.txt. Es información vinculada a vértices de malla, no una
estructura demostrada de caja RGB/radio. No se atribuye semántica completa a
las demás tablas opacas ni al clipping original.

El wrapper46e238..46e254 pasa 0x42a00000 (80.0f) como lente separada del NCP.
Las firmas reales CodexCamera no tienen setter de lente; el último float de
SetShot es lerpTime según SDK. final_native.txt conserva la evidencia. Se limita
el FOV por keyframe a la API soportada, sin afirmar imposibilidad de cualquier
manipulación hipotética del ejecutable.

## CONFIRMADO EN SDK / DOCUMENTACIÓN

NSC.htm documenta mapa, label y flags8/16 por localización. El manual de Embrace
describe regiones, soundboxes/lightboxes, interés, frames y controles de cámara.
cutscene.htm y las firmas Codex corroboran PlayPath/SetShot/SetupCutscene,
sonidos, luces y flags. El manual no prueba por sí solo offsets ni efectos
audibles. La UI usa estos mecanismos sin abrir los editores originales.
El manual distingue luces Editor Only para lightmaps, luces dinámicas y radios
interior/exterior/volumen de soundboxes. CodexCamera documenta el tiempo de
transición de SetShot; no lo confunde con FOV.

## INFERIDO / DECISIONES DE IMPLEMENTACIÓN

- Link de sectores de una región: intersección conservadora por planos y soporte
  de la caja orientada. Puede incluir algún sector extra; no recompila geometría.
- Presupuestos RCM:8regiones,16mapas,128puntos/mapa,32bucles,120s de cámara. No se
  venden todos como límites del motor.128keyframes sí es el búfer original NCP.
- Zonas de sonido y luz son una **alternativa de activación** mediante volume()
  existente y handles propios. No son copias del payload/recorte original por
  sectores. La luz es puntual; el sonido tiene radios. Guardar sonido conserva
  activo y recrea un handle; ocupación de zona se vuelve a evaluar al cargar.
- Las zonas combinan ocupación con un ChronicleFlag existente, sin nuevos
  registros de save. La luz se aplica por cambio de ocupación/flag; respeta una
  acción posterior. La salida retira sólo su configuración vigente y el fin de
  escena sólo GUID todavía propios. Roles dinámicos usan el gestor existente.
- Importar datos independientes reutiliza la misma biblioteca local y cierre
  de dependencias. NCP se valida con el lector real; no se crea una NOT vacía.
  El backend detecta referencias de cámara/audio al retirar contenido.
- Mapas640×480: imagen convertida y teselada por potencia de dos. Los marcadores
  editados se convierten al ejeY ascendente original y se exportan con enteros.

## PENDIENTE DE VERIFICAR / LÍMITES

COMP01–06 requieren observación del usuario en Redemption, incluyendo presencia
visual de regiones, render de cámara, audio/proveedorEAX y guardado/reentrada.
Qt offscreen no acredita GPU/DPI físico, PC independiente ni multijugador.

La semántica nativa completa de restauración de compañeros privados y todas las
tablas originales de luz/sonido no se presentan como descifradas. Trasplantarlas
literalmente no es requisito del cierre funcional acordado. Los usos narrativos
normales se configuran mediante acciones existentes y zonas; no se promete
reclutamiento/estados privados idénticos ni recorte/bake de iluminación.

La importación de código binario externo desconocido no se transforma en una
biblioteca segura de datos: sus dependencias ejecutables no están validadas por
el pipeline de importación. Se rechaza en vez de ejecutar/copiar código arbitrario.
Esto no es un dictamen sobre derechos de terceros ni licencia de redistribución.

## VERIFICACIÓN AUTOMATIZADA

tests/test_authoring_completion.py cubre 20 casos, además de las suites vigentes;
tests/test_final_closure.py añade 12 regresiones cruzadas:
formatos, límites, aliases/propiedad/restore con doubles, Codex real45.3,
mapas/paquetes/fingerprint, región typed links, UI/undo/cancel y no cambios en
fuentes tutorial/mini. El gate completo y el EXE se recogen en delivery.json
cuando concluyen; un resultado focalizado no sustituye ese gate.
final_routes.json enlaza las58 capacidades con archivos y tests que realmente
pasaron en el gate, sin convertir compilación o doubles en aceptación nativa.

La auditoría vigente de main del 20/10/2026 está en MAIN_AUDIT.md y main_audit.json:
634 pruebas completas, dos regresiones de aislamiento de backups, compilación
real de los siete ejemplos y new_chronicle, y portable bilingüe del EXE actual.
Se retiraron del índice 16 temporales conservando sus archivos locales; las
huellas de los 1.868 archivos de proyectos/datos originales siguen coincidiendo.
No se cambian versión, releases ni aceptación nativa.

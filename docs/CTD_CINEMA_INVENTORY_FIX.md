# Cutscene, llave y laboratorio — 0.9.10

La lección 3 la presenta Anezka. La película dura doce segundos: plano de la
puerta cerrada y del paseante detrás, apertura de tres segundos, paseo después
de la apertura y plano final. La puerta es el modelo original `testdoor.nod`,
instanciado como decorado propio y elevado mediante `SetPosition`; no se cambia
la geometría de Londres. No se afirma que reproduzca los mecanismos de frames
de todas las puertas originales.

En el editor, Cámaras → `walk_scene` contiene los planos y sus transiciones,
el objeto enfocado, el decorado móvil, su desplazamiento y el momento en que
el paseante comienza su recorrido. «Enfocar decorado» permite mirar la puerta
en vez del rostro del actor. El laboratorio está ahora a la izquierda de los
profesores, en la misma calle y con un trayecto directo comprobado contra el NIL.

La llave del tutorial hereda modelo e icono de BoneKey, pero su plantilla
propia `T_tutor_key` especifica `item_type: 0`. Es un objeto físico. La condición
para cambiar de layout comprueba su presencia; una flag sola no basta.
Elena conserva su turno si el motor no retiene el objeto, por ejemplo si no
puede colocarlo. Los registros `INVENTORY_GIVEN` y `INVENTORY_NOT_RETAINED`
permiten distinguir resultado real de una señal sonora.

## CONFIRMADO EN ARCHIVOS ORIGINALES

- `SetTimer` nativo en `0x46ec00` llama a `0x4b58a0`: reserva una entrada de
  36 bytes y la añade a una lista ordenada. No busca ni sustituye un ID previo.
  `KillTimer` recorre y retira las entradas del mismo script/ID (`0x4b5940`).
- Nuestro código anterior programaba 9400 desde `convended` y desde el bucle
  que ya estaba activo. Cada conversación podía añadir otra cadena recurrente.
  Los frames de cine contaban callbacks, por lo que estas cadenas acortaban
  la duración. `schedulePoll` retira 9400 antes de programarlo.
- BoneKey hereda `_questItems_DA`, con tag 20 igual a 7. La inserción nativa
  en `0x460e00` distingue ese tipo: en `0x460ec1..0x460edf` consume el objeto
  y devuelve éxito sin insertarlo en la cuadrícula. Por eso un retorno positivo
  de `AddToActorInventory` no acredita que se conserve físicamente.
- `IsActorGuid` acepta los tipos 0 y 7; los jugadores sí pasan esa función.
  No se atribuye la falta de llave a un supuesto rechazo del GUID del jugador.
- `CTD_Oubliette_Main` ejecuta conversaciones con feedback (flags 4), pausa
  AI tras iniciarlas, usa `convreached` para `PlayPath`, girar/mover personajes
  con `SendActorToPos` y modificar flags; libera cámara y AI desde `convended`.
  `CTD_LeComte` muestra el mismo control por líneas y recorridos NCP propios.
- `CTD_ChamberSkulls` usa `RotatePivot(1,3.0f)` para una puerta con frames
  originales y comprueba Chronicle Flags para abrirla. Las plantillas de muchas
  puertas heredan `tracker_thing`, sin modelo autónomo: sus meshes/frames están
  en la escena original. `testdoor` sí referencia un NOD independiente.

Bytecode conservado en `research/CTD_Oubliette_Main.bytecode.txt`,
`research/CTD_ChamberSkulls.bytecode.txt` y las copias previas de CTD.
La lectura del ejecutable y de las plantillas se reproduce mediante
`tools/research_ctd_cinema.py`; resultados en `research/round0/ctd_cinema_fix/`.
No se ejecutan herramientas originales de autoría.

## CONFIRMADO EN SDK/DOCUMENTACIÓN

`research/phase7/embrace/cutscene.htm.txt` describe el control de las películas
con `convreached`, los cambios de cámara, el movimiento de actores y el uso
de timers para secuencias sin diálogo. `CodexCamera.htm.txt` describe
`SetupCutscene`, `SetShot` y `Release`. La película propia es de este segundo
tipo: timeline temporizada, con API original y control de entrada explícito.

## INFERIDO

La acumulación de timers explica la película que acababa casi de inmediato,
especialmente después de recorrer los trece encuadres. La comparación nativa
y la simulación fiel respaldan esa explicación, pero no sustituyen un nuevo
ensayo visual. El tipo consumible de BoneKey explica la llave ausente; su variante
física debe verse con el mismo icono y modelo heredados.

## PENDIENTE DE VERIFICAR EN REDEMPTION

Composición de los cuatro planos, movimiento y colisión de la puerta y del
paseante, animación de Anezka, llave visible en la cuadrícula, acceso al laboratorio
y persistencia de estos elementos tras guardar/cargar. Empezar una partida nueva
de «RCM · Tutorial paso a paso» desde el acceso habitual.

Las pruebas Java ahora simulan una cola que acumula timers, recorren los trece
diálogos, verifican la duración de la película, la espera detrás de la puerta,
su apertura y el avance del personaje. También simulan un objeto consumido con
retorno exitoso: no se marca entregado ni se retira Elena hasta que se conserva.

## Verificación de entrega

La suite completa termina con 236 pruebas correctas, además de Ruff y Mypy.
La primera ejecución restringida no pudo crear el enlace de la prueba de
protección contra hardlinks; se conserva en `restricted_quality`. La repetición
completa fuera de esa restricción pasa, incluida esa protección; resultados
en `research/round0/ctd_cinema_fix/final_quality/`. Esta repetición no mide
cobertura; el informe de cobertura anterior conserva la ejecución restringida.

El ejecutable portable 0.9.10 carga y compila el tutorial mediante su GUI en
modo seguro/offscreen. Esto prueba la entrega del editor y su compilador;
no acredita render OpenGL nuevo ni observación visual dentro de Redemption.

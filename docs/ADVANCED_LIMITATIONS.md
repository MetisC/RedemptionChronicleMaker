# Límites de esta candidata

**CORE 1.0:** entrada, NPC/objeto, inventario, diálogo con RETURN/flags, notas, journal/quest, triggers condicionados, presets/planos y secuencia Player, encuentro sencillo, recompensa once, viaje/llegada, guardar/cargar según el contrato, GUI/undo, build/deploy y portable.

**ADVANCED / EXPERIMENTAL:** writer NOT con campos editables y preservación de bytes desconocidos; puertas originales conocidas; static conservador; NCP original ligado a una geometría; animaciones propias de cada modelo; AI existente y sonidos situados. La compilación o el readback de formatos no acreditan todos los campos nativos. La lista de animaciones depende del modelo; evita convertir slots inexistentes en presets universales.

**NO IMPLEMENTADO:** FOV por keyframe, puertas universales, static ALL/NONE/SELECTIVE completo, autoría AI sin restricciones, red replicada verificada y migración de saves. La geometría permanece fuera de alcance. NCP lineales propios, acciones temporales/de línea, bucles situados y controles pequeños de luz/clima están implementados; aceptación visual/sonora/restore pendiente en EMB01–24.

La aventura local utiliza el menú Multiplayer/LAN del juego como mecanismo de carga. Esto no significa que la red con varios clientes esté verificada. Usa un jugador local. El tutorial nuevo cambia el contrato de saves: partida nueva obligatoria. Las crónicas y perfiles Crypt previos no se borran; las plantillas antiguas del tutorial siguen publicadas para evitar perfiles huérfanos al abrir LAN.

Pendientes humanos: aspecto/colisión de cámara, posición al cargar, abortos/ratón/control, reentrada, premios y ensayo portable en otra máquina. No se declara paridad con Embrace ni versión final 1.0 mientras estos casos bloqueantes sigan pendientes.

Objetos originales: hay selector y acciones de ocultar/restaurar/retirar props identificados, además de frames/pivotes de puertas y interacciones nativas por clic con texto de hover y acciones de viaje u otros eventos. No elimina caras del NIL ni sincroniza el estado privado de Door/PivotDoor. ORG01–06 pendientes; el motor puede rechazar un candidato que no exista o no tenga los frames necesarios.

CLICK01–08: quedan pendientes en el juego el texto y resaltado, selección/colisión, alcance, diálogo/notas, guardado, reentrada y multijugador de la capa nueva. Se bloquean los enlaces a la propia escena; no se convierten en silencio los triggers de proximidad anteriores.

Current coverage: EMBRACE_AUTHORING_PARITY.md and AUTHORING_COMPLETION.md.
Own maps, native box regions/typed links, optional runtime EAX, timed stationary
camera paths, dynamic-role control and activation sound/light zones are now
implemented. Literal native box clipping and campaign-specific Player constructor
binding remain unknown, not proven impossible. Unknown code-bearing mod import
is intentionally rejected. Offline evidence is not native acceptance; no100% or
final1.0 claim. COMP01–06 are the short current manual checks.

# Tutorial paso a paso: un escenario, siete lecciones

Revisión 0.9.12: al empezar aparece un prólogo en la ventana de texto del juego. Ciérralo y habla con Tomás. Christof ofrece **Leer una nota de ejemplo** en su laboratorio opcional. En el paso 5, pulsa el barril antes de hablar con el agente para leer otra nota. En el editor, selecciona el objeto y usa **Añadir nota al usar**; el botón muestra el evento existente. Los gestos deben acabar en reposo sin hacer desaparecer a Christof. La visualización de estos cambios necesita confirmación en el juego.

Empieza una **partida nueva** en «RCM · Tutorial paso a paso». Esta revisión cambia el progreso respecto a los guardados anteriores.

El journal muestra el objetivo actual. Delante del punto de inicio aparece su profesor. Al completar u omitir una lección aparece el siguiente en el mismo sitio. El laboratorio está a la izquierda de los profesores, en la misma calle: no necesitas visitarlo para avanzar.

| Paso | Qué hacer en el juego | Dónde se edita |
|---|---|---|
| 1. Inicio | Habla con Tomás. Continuar u omitir. | [Entrada safe](rcm://workshop/entries/safe). Espacio 3D → Inicio; posición, orientación y llegada por defecto. |
| 2. Conversación | Vera muestra los 13 encuadres uno por uno. Tú decides cuándo pasar al siguiente o saltar los restantes. | [Conversación](rcm://workshop/conversations/camera), [primer plano del recorrido](rcm://workshop/conversations/framed). Propiedades → Cámara de diálogo. |
| 3. Cutscene | Anezka presenta una película de doce segundos: puerta cerrada, apertura, paseo y plano final. Verla u omitirla. | [walk_scene](rcm://workshop/sequences/walk_scene): planos, objeto enfocado, decorado móvil, desplazamiento y «Empieza a caminar». [Puerta](rcm://workshop/objects/stage_door), [walker_walk](rcm://workshop/paths/walker_walk). |
| 4. Inventario | Elena entrega una llave de hueso física; mírala en la cuadrícula del inventario. Omitir también la entrega para poder seguir. Deja espacio para el objeto. | [Elena](rcm://workshop/actors/keeper) → Editar inventario inicial → + Del catálogo; [next_4](rcm://workshop/events/next_4): Dar objeto y activar flag. Templates propios → T_tutor_key conserva modelo/icono de BoneKey y cambia item_type a 0. |
| 5. Layout | Observa el barril y habla con el agente. Comprueba que llevas la llave; cambiar layout conserva la calle y retira barril y profesores anteriores. | [change_layout](rcm://workshop/events/change_layout) requiere «Tiene objeto key». + Escena crea contenido sobre el mismo level. Viaje elige escena y entrada. |
| 6. Encuentro | El instructor crea una sola rata básica junto al inicio si lo pides. Matarla u omitir pasa al final. | [one_rat](rcm://combat/encounters/one_rat), [cleared](rcm://combat/events/cleared). Retirar la rata sin matarla no otorga el premio del combate. |
| 7. Guardado | Guarda, carga y comprueba llave y profesor. Terminar u omitir completa el tutorial. | [Final](rcm://finished/conversations/final). Guardar conserva el YAML; BUILD CHRONICLE lo compila; Deploy actualiza RCM. La partida se guarda dentro de Redemption. |

**El barril es decorado: no es una puerta ni se usa con un clic.** Las lecciones principales tienen dos opciones. Omitir prepara lo necesario para la siguiente. Sólo se carga un nuevo objetivo cada vez; los completados pueden aparecer en el historial del journal.

## El paseo de Vera por las cámaras

Al crear una conversación, el editor elige **Sobre hombro cercano hacia quien habla**. Si el YAML no especifica cámara, el generador usa ese mismo plano. La opción automática del motor se conserva para proyectos existentes, pero no es la predeterminada.

Vera empieza con ese plano y te deja cambiar, sin prisa, por todos los encuadres del selector. Cada ejemplo tiene «Siguiente plano» y «Omitir los demás planos». Al acabar aparece Anezka. Puedes ajustar cualquier ejemplo desde sus enlaces:

| Ejemplo | Cámara |
| --- | --- |
| [1](rcm://workshop/conversations/framed) | Sobre tu hombro, cerca de Vera |
| [2](rcm://workshop/conversations/frame_2) | Primerísimo plano de Vera |
| [3](rcm://workshop/conversations/frame_3) | Primerísimo plano de tu personaje |
| [4](rcm://workshop/conversations/frame_4) | Primer plano de Vera |
| [5](rcm://workshop/conversations/frame_5) | Primer plano de tu personaje |
| [6](rcm://workshop/conversations/frame_6) | Sobre el hombro de Vera, cerca de tu personaje |
| [7](rcm://workshop/conversations/frame_7) | Sobre tu hombro, más abierto |
| [8](rcm://workshop/conversations/frame_8) | Sobre el hombro de Vera, más abierto |
| [9](rcm://workshop/conversations/frame_9) | Perfil de Vera |
| [10](rcm://workshop/conversations/frame_10) | Perfil de tu personaje |
| [11](rcm://workshop/conversations/frame_11) | Los dos personajes |
| [12](rcm://workshop/conversations/frame_12) | Plano medio |
| [13](rcm://workshop/conversations/frame_13) | Plano entero |

## Laboratorio opcional

[Laboratorio](rcm://workshop/actors/lab), separado de los profesores:

- Iniciar/detener [su propio recorrido](rcm://workshop/paths/lab_walk) y pausar/reanudar AI.
- Probar [EASTOttoVan](rcm://workshop/sequences/original_path), un travelling original **experimental**; no representa un writer NCP.
- Acercarte a la [zona del libro](rcm://workshop/triggers/station) para recoger un objeto. Debug → Leer trace muestra entrada, salida y pickup.
- Activar/desactivar una flag sin cambiar las siete lecciones.
- Hablar con el **profesor de animación** → **Animaciones de conversación**. Ofrece reposo, gesto de reposo, hablar, escuchar y cinco gestos del modelo ST_Christof_MD. Los nombres de los archivos permiten identificarlos.

Para cambiar una actuación, abre [su conversación](rcm://workshop/conversations/lab), selecciona un nodo como `gesture10` y elige **Propiedades → Animación al hablar**. Una línea puede elegir otra animación; si no eliges ninguna, conserva la del nodo. Un nodo sin animación usa hablar/escuchar del motor. Sólo se ofrecen movimientos disponibles para sus personajes, no una lista universal.

La película comienza con **Vista aérea amplia en picado** y transición inicial de cero segundos. Cambia cada plano en [walk_scene](rcm://workshop/sequences/walk_scene). El aspecto y la ausencia de obstáculos aún deben comprobarse dentro del juego.

Esta revisión guarda la posición y orientación del jugador local. Al cargar, se recuperan después de la creación del personaje. Un viaje explícito usa su entrada elegida. Si el motor rechaza repetidamente la posición, se conserva la posición nativa y se registra el fallo, sin bloquear toda la lógica. **Usa una partida nueva de 0.9.12; los saves anteriores no son compatibles.**

## Verificación y límites

Compilación contra la API real y pruebas de las siete lecciones completas y omitidas. Las pruebas con dobles Java comprueban control y progresión; la cámara, animación, cambio de layout y save/load nuevos aún necesitan ensayo visual en Redemption.

No hay edición de geometría. La puerta de la lección 3 es un modelo móvil propio sobre la calle original. No sustituye el trabajo pendiente con las puertas y sus frames incrustados en escenas originales. Writer NCP y multijugador siguen limitados. El paso 5 es una transición lógica entre layouts.

# Director de escenas

Trabaja en **Campaña → seleccionar secuencia**. No hay otra pestaña principal. Se conservan los planos y travellings originales.

## Crear un travelling

1. Abre Espacio 3D y encuadra la primera vista.
2. Selecciona una secuencia y pulsa **Crear / editar travelling propio…**. Puedes navegar por el mapa con esa ventana abierta.
3. Mueve la cámara del visor y pulsa **Punto desde esta vista**. Repite para los demás puntos.
4. Selecciona un punto para editar posición y orientación. Puedes insertar, actualizar, duplicar, borrar y reordenar. Tras duplicar, mueve el punto: dos posiciones consecutivas no pueden coincidir.
5. Acepta. Toda la edición se puede deshacer de una vez. Elige Travelling como tipo de cámara si hace falta y ajusta la velocidad. F5 genera el NCP nativo.

Un plano fijo usa un punto. Un travelling usa interpolación lineal y hasta 128 puntos, el límite real del búfer original. El visor dibuja trayectoria y direcciones; no simula la colisión ni garantiza el encuadre del motor. No se inventa un campo FOV. El recurso recuerda escena y escenario de creación, y se avisa si se usa en otro contexto.

## Dirigir una escena

La **Timeline de escena** contiene tiempos y acciones normales. Añade una acción de escena, elige su momento y pulsa **Editar acciones…**. Es el mismo inspector que en eventos y clics sobre objetos.

Puedes cambiar plano o travelling, mirar a alguien o a un punto, reproducir un gesto, iniciar un recorrido, reproducir sonido, hacer un fundido, cambiar estado o ejecutar un evento. Los gestos proceden del motionset real del modelo elegido. Se conservan los planos y movimientos de decorado anteriores. El reloj de 150 ms cuantiza los tiempos; las acciones con el mismo tiempo conservan su orden. Máximo 64 entradas, como el presupuesto de planos existente; duración máxima vigente: 120 segundos.

Los fundidos ofrecen **Desde negro**, **A negro** y valores personalizados. Flash y filtro blanco utilizan la API nativa; no se ofrecen colores empaquetados de significado desconocido. **Limpiar efectos** retira los efectos activos. Un fallo cancela la película y devuelve el control. Al cargar una película con acciones temporizadas se cancela, sin repetir recompensas. Las películas Player anteriores sin estas acciones conservan su restauración habitual.

## Coordinar el diálogo

Selecciona una línea y pulsa **Acciones al comenzar esta línea…**. Puedes poner un primer plano, mirada, gesto, sonido o cambio de estado sin alterar RETURN/GOTO. Otra conversación, película, nota o viaje se inicia al terminar el diálogo, evitando interfaces que compitan dentro de una línea.

En la conversación, **Puesta en escena** ofrece Automática, Entrada RCM y Punto de conversación nativo. Las dos últimas reutilizan entradas con nombre: créalas y muévelas en Espacio 3D. Entrada RCM conserva su comportamiento anterior. El modo nativo escribe la tabla convstart propia y llama a TeleportPartyToConversation; puedes elegir hasta tres puntos adicionales para los compañeros. No son mecanismos internamente idénticos, especialmente en multijugador. Los puntos nativos admiten giro Z, sin inclinación X/Y; comprueba formación, orientación y colisión dentro del juego.

## Sonido, luz y ambiente

El sonido situado puede sonar una vez o mantenerse en bucle con nombre mientras la escena está activa. Usa un waypoint, volumen y radios interior/exterior. **Detener sonido situado** selecciona ese nombre. El máximo de 32 bucles es un presupuesto de propiedad y sondeo de RCM, no un límite atribuido al motor. Guardar/cargar conserva la activación y recrea un único handle; salir de escena detiene los sonidos propios.

Una luz dinámica se asocia a una entidad propia. Configura RGB, intensidad, radio y un estilo original; usa Retirar luz dinámica para apagarla. Luz y clima participan en el nuevo contrato de guardado. Sólo se ofrecen climas vistos en scripts originales. La iluminación horneada, lightmaps y geometría quedan fuera de alcance.

## Probar los ejemplos

- **Ayuda → Crónica de prueba: el refugio** abre una aventura de aceptación independiente. Pulsa la puerta original Refuge, habla con Elena, mira u omite la escena, vence a la rata básica y vuelve a hablar con ella. Después viajas a otra escena.
- En **Showcase completo**, el menú de laboratorios opcionales de la guía ofrece **Cinematic Director Lab**. El encargo principal del libro se conserva. Las copias personales no se sobrescriben: solicita una copia nueva del ejemplo si la tuya es anterior.

La puerta del refugio demuestra ocultar/restaurar decorado nativo y dejar paso. No se atribuye una animación de apertura a una malla original sin frames. Las puertas compatibles con frames/pivotes conservan sus herramientas.

Las extensiones son optativas en formatos 9/10. Abrir un proyecto anterior no lo convierte. Cambios estructurales de cine/audio/luz pueden necesitar partida nueva; RCM avisa al cambiar la firma de guardado. EMB01–24 separa las pruebas manuales: compilar y probar offline no confirma el resultado visual/sonoro dentro de Redemption.

## Música temporal

En cualquier lista de Actions elige **Audio / Música temporal**, pista y volumen. Más tarde, **Audio / Restaurar música anterior** recupera la pista y volumen previos. También funcionan en una línea o cue. Codex guarda una única pista anterior: se rechaza un segundo Push mientras RCM la tenga en propiedad. No es una pila con varios niveles.

La cancelación o fin de la película devuelve la música sólo si esa película la inició y la instantánea sigue siendo suya. Salir de escena hace la misma comprobación. Cambiar música permanentemente abandona esa propiedad. Al cargar una partida, RCM descarta la propiedad transitoria y no hace Pop sobre una instantánea desconocida; usa Música normal si necesitas establecer explícitamente la música después. No se anuncia persistencia nativa del snapshot sin prueba.

## Cámara sin desplazamiento

Un punto permite mantener un plano fijo. Los NCP propios requieren posiciones sucesivas distintas. Los originales con XYZ repetido también repiten el parámetro y tienen coeficientes cúbicos no triviales; no demuestran un giro estacionario con duración. No se inventa un tramo mínimo. Los originales se conservan y reproducen mediante el motor. Casos nuevos: EMB-MUSIC, EMB-CONV y EMB-NCP en el checklist.

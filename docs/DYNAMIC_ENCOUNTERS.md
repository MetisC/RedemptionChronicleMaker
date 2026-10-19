# Encuentros dinámicos

## Emboscada en 30 segundos

1. En **Espacio 3D**, pulsa el botón derecho sobre suelo visible y elige **Encuentro dinámico aquí…**.
2. Elige **Emboscada**. Por defecto hay tres ratas originales; puedes cambiar el tipo mediante el catálogo.
3. Conserva el punto marcado. Elige **Al entrar en una zona** y la zona nueva junto al punto, o selecciona una zona existente.
4. En **Qué ocurre al terminar**, elige acciones si quieres avanzar una misión, cambiar un flag, reproducir una película o abrir una salida ya existente.
5. Pulsa **Crear**, guarda y usa **F5**. En el juego entra en la zona manualmente.

Desde Campaña / Vista global también puedes usar **+ Encuentro dinámico…**. Marca uno o varios waypoints existentes. Si no hay puntos, colócalos antes en 3D o utiliza Cerca del jugador: en ese caso el motor decide la posición cercana. No se promete ausencia de colisiones.

## Oleadas

Elige **Oleadas**: el preset contiene tres grupos, con dos segundos entre oleadas. Añade/quita oleadas y tipos con su cantidad. La siguiente empieza cuando la anterior está limpia; la última sólo completa cuando no quedan enemigos vivos. No se crean actores ficticios en el proyecto.

## Generador continuo

Define **Crear uno cada** y **Máximo enemigos vivos**. El generador respeta el límite, reemplaza las bajas y permanece activo hasta un evento que lo detenga o hasta alcanzar un máximo total y vaciar el grupo. Las acciones normales permiten iniciar, detener, pausar y reanudar desde diálogos, zonas, misiones, temporizadores y condiciones.

En continuo, Cantidad es un lote secuencial: crea esa cantidad de ese tipo, uno por intervalo, antes de seleccionar otro tipo. El modo rotatorio recorre el pool; el aleatorio usa el Math.random original y pesos. Pausar detiene apariciones/fases; los actores ya creados siguen siendo actores del juego. Detener conserva los vivos por defecto.

## Refuerzos

El preset **Refuerzos** queda sin inicio automático. En otro evento añade **Encuentro dinámico / Iniciar** y selecciona ese grupo. Por ejemplo, un evento de estado con «otro encuentro activo y vivos como máximo 1», un timer de 30 segundos, una respuesta de conversación o una fase de jefe.

## Jefe por fases

Elige un actor existente o genera un jefe. Al generar, debe haber un rol único con cantidad 1. Por defecto conserva vida/AI/flags de la plantilla. Puedes ajustar vida en las opciones del enemigo, sin cambiar ningún recurso original.

El preset crea fases al 50% y 25% y un grupo de dos refuerzos vinculado. Edita cada fase para elegir porcentaje o HP y cualquier acción del editor: música, secuencia, flags, misiones o generadores. La finalización puede detener portales y completar la misión.

**La fase detecta anterior > umbral y actual <= umbral mientras el actor sigue válido y vivo. Un golpe mortal puede saltársela.** No hay garantía de «antes de morir», invulnerabilidad automática ni protección de fase. Las fases son una sola vez por defecto, incluso tras guardar/cargar/reentrar; las repetibles requieren un nuevo cruce tras recuperarse.

## Enemigos y puntos

El selector reutiliza Resource Browser. **Enemigos de la campaña original** se basa en la familia _Enemies y los flags originales, con referencias a escenas del catálogo. No es una dificultad inventada. Todos los actores y filtros de procedencia siguen disponibles. Los detalles muestran modelo, AI, script, salud/max salud, clan/flags cuando hay evidencia y escenas conocidas. Los hints de escenas no son una lectura completa de NSD; team/actor type que no se hayan decodificado no se inventan.

Los puntos son waypoints editables. Al seleccionar el encuentro se resaltan puntos, zona y representación visual vinculada. Una representación es un prop normal; no se crea un emitter ni geometría. Para sonidos, animaciones o efectos al empezar, usa los callbacks y acciones existentes.

## Guardar, cargar y volver

El sistema guarda estado, oleada, cantidades pendientes, GUID activos/rol, pausa, cooldown y fases en records nativos. Reconcilia GUID/localidad/plantilla y no crea reemplazos a ciegas al cargar. Si falta el registro persistente o un actor restaurado no aparece tras la espera acotada, el encuentro queda en error y la traza explica el motivo. Esto evita duplicar enemigos; la restauración real debe comprobarse dentro de Redemption.

Políticas: **Una vez** conserva finalización; **Continuar** mantiene progreso; **Reiniciar al volver** retira sólo sus actores conocidos y reinicia (no al cargar); **Repetir tras un tiempo** inicia otro ciclo después del cooldown. Las recompensas/eventos marcados una vez conservan sus propios checkpoints. Reiniciar un generador no borra arbitrariamente flags de otros eventos. No se migran partidas con otra estructura: el build avisa si cambia su firma.

## Opciones avanzadas y límites

Máximo vivos 1..64; máximo 256 simultáneos por escena y 32 generadores; 1..32 oleadas; grupos/cantidades, intervalos y reintentos acotados. Son límites conservadores de RCM, no benchmarks certificados del motor. Se usa el mismo poll de escena de 0,15 s y un presupuesto compartido de cuatro apariciones por tick. El tracking sólo guarda activos, nunca todos los GUID históricos; los contadores saturan a un millón.

El intento fallido rota puntos, deja traza y reintenta de forma limitada. No crea un timer por enemigo. La vida personalizada o multiplicador se aplica al actor generado; la plantilla queda intacta. El override de equipo usa valores nativos; no altera automáticamente flags de AI o invulnerabilidad.

Esta revisión soporta transición de oleada **al limpiar**, no solapamiento/avance manual de una lista de oleadas. Para solapar grupos, utiliza generadores independientes y eventos. No hay posición aleatoria arbitraria en volúmenes, preview nuevo de modelos ni cambio universal de puertas. Las cámaras y controles de actor aceptan roles dinámicos del roster existente; véase AUTHORING_COMPLETION.md. Una fase usa las mismas Actions.

Los roles generados sirven para vida y contadores. Las acciones de animación, AI, inventario o cámara dirigidas a un actor siguen usando actores authored; para controlar al jefe de esa forma, elige un actor existente como jefe. Las activaciones externas se editan en sus eventos normales; editar un generador conserva esos eventos y sólo añade una activación si la solicitas. Retardos/caps/estado AI por entrada no tienen controles propios en esta revisión. El límite de activos no implica limpieza automática de cadáveres del motor.

## Probar los ejemplos

**Tutorial rápido:** Una carta al amanecer permanece en formato 9 y sin cambios.

**Showcase:** habla con la Guía → Laboratorio opcional: encuentros dinámicos. Puedes iniciar dos ratas, un jefe y un refuerzo; o probar/detener un continuo limitado a dos vivos. No altera el encargo principal.

**Dynamic Encounter Lab:** abre chronicles/dynamic_lab/project.yaml. Anezka prepara las oleadas: después ve al barril para entrar en su zona. También ofrece continuo, pausa y reanudación. Todos usan Rat; el jefe multiplica vida para observar umbrales. Guarda/carga a mitad.

**MANUAL RUNTIME TEST REQUIRED.** La compilación Java 45.3, pruebas con doubles y widgets no acreditan estos combates dentro del juego. Sigue DYN01–DYN12 en MANUAL_RUNTIME_CHECKLIST.md.

# Fase 9 — propuesta para una primera beta privada aceptada

Fecha: 2026-10-08. Estado actualizado: **implementación técnica 0.9.0 y circuito único desplegado; aceptación nativa aplazada por el usuario**. La propuesta original se conserva debajo como contexto. El encargo externo está en AUTHORING_AUDIT_REQUIREMENTS.md; resultados en AUTHORING_MATURITY_REPORT.md. La instrucción posterior de continuar sin pruebas nativas modifica el orden propuesto, no sus requisitos de aceptación.

## Punto de partida comprobado

El último cierre documentado encontrado es [Fase 7, versión 0.7.0](PHASE7_REPORT.md). No se ha encontrado un cierre de Fase 8 que permita atribuirle mejoras o aceptación. Esta propuesta parte del código y de la evidencia presentes, no de una numeración de fases como prueba de progreso.

La base permite editar contenido, reutilizar geometría, definir varias escenas, generar Java y formatos del juego y construir un portable. La revisión documenta 188 tests satisfactorios y un ensayo local del portable. Siguen abiertos [B1–B5](RELEASE_BLOCKERS.md): diálogos/UI/cámara, persistencia, NOT/AI propios, equipo limpio y red/repetición. La prueba offline no acredita esos comportamientos dentro de Redemption.

Hay fricciones concretas que afectan al recorrido del creador:

- `MainWindow.create_project` crea un proyecto simple; añadir una campaña exige conversión posterior.
- El panel de campaña llama «mapas» al número de escenas, aunque varias puedan compartir geometría.
- La creación habitual de actores utiliza `near_player`; el radio cero puede superponerlos.
- El contrato actual de guardado puede cambiar al editar la campaña: no hay migración de partidas entre builds.
- La escena estática original puede cargar objetos base. Una escena adicional propia no garantiza eliminar todo ese contenido.

## Resultado que debe aceptar el usuario

**Crear una crónica pequeña desde un proyecto vacío en la interfaz, probarla en Redemption y completar un recorrido de juego de 15–30 minutos sin editar YAML o Java para las operaciones cubiertas.** Esa duración es el tamaño propuesto para el ensayo, no una estimación de desarrollo.

La campaña de aceptación tendrá tres escenas sobre dos geometrías originales. Dos escenas compartirán un mismo level con NPC y lógica diferentes. Incluirá un NPC inicial accesible, otro personaje separado espacialmente, conversación con dos respuestas, decisión persistente, quest con objeto y recompensa, una transición y un regreso. La cámara, controles, inventario y estado deberán recuperarse en todos los recorridos ensayados.

El alcance inicial es una sesión local abierta desde Multiplayer, que es el acceso utilizado por el juego para estas crónicas. Esto no equivale a multijugador probado con varios clientes. B5 seguirá abierto hasta completar host/client; una eventual beta local debe identificar esa restricción expresamente y registrar el cambio de alcance, sin declarar cerrada la aceptación completa existente.

## Orden del trabajo propuesto

### 1. Cerrar primero el comportamiento nativo crítico

Ensayar la revisión actual, registrar fallos reproducibles y corregir B1/B2 antes de ampliar controles. Matriz de conversación: aceptar, rechazar la primera respuesta, salir, abortar y volver a hablar. Verificar encuadre legible, devolución de cámara, cursor, HUD y movimiento.

Guardar/cargar antes y después de la decisión, recogida, entrega, recompensa y transición; ensayar también conversación/cámara activa. Reentrar en las escenas durante tres ciclos y comprobar actores, objetos, flags y recompensas. No dar una función por aceptada sólo porque aparece en un log.

Identificar cada resultado por versión/build, fuente, partida nueva o guardada, pasos y observación. La automatización que no puede manejar el menú no bloquea la posibilidad de una prueba manual guiada: la aceptación humana con revisión identificada es evidencia válida.

### 2. Hacer coherente el recorrido de creación

Crear campañas nuevas directamente y conservar compatibilidad de apertura de proyectos antiguos. Distinguir en toda la interfaz «geometría/level base», «escena de campaña» y «secuencia de cámara». Facilitar elegir escena inicial, seleccionar entorno original y conectar transiciones sin editar archivos.

Recorrer las operaciones habituales de actores, conversación, condiciones, flags, quest, objeto y transición. Resolver campos inaccesibles, referencias ambiguas y mensajes que impidan ese recorrido. Los errores deben indicar el elemento afectado y permitir localizarlo en el editor.

La validación de esta parte será una campaña creada desde cero en la interfaz, guardada, cerrada, reabierta y construida. Copiar una fixture mediante un script no sustituye ese ensayo.

### 3. Asegurar colocación y control de escenas

Usar posiciones y orientaciones explícitas para la campaña de aceptación y comprobarlas dentro del juego. Garantizar que los NPC de prueba sean visibles, alcanzables y separados. Revisar selección y altura en el viewport frente al resultado nativo; no prometer que cualquier coordenada sea transitable por verse en el editor.

Investigar el mínimo necesario para seleccionar llegadas/entradas útiles y para la vuelta a una escena. Sólo exponer entradas adicionales cuando su contrato esté demostrado en formatos/API y en partida. Si esa investigación no permite implementarlas con seguridad, declarar las entradas originales admitidas y probar el recorrido con ellas.

Ensayar dos escenas sobre la misma geometría con distinto contenido y conservar estado sin entidades duplicadas. Registrar qué objetos estáticos originales permanecen. Si interfieren con la campaña, ese caso es un bloqueo real: investigar cómo controlarlos directamente sin editar geometría, o limitar expresamente los escenarios admitidos. No anunciar sustitución completa del contenido base mientras siga sin demostrarse.

### 4. Completar el ciclo de construir, probar y revisar

El creador debe distinguir fuente modificada, build vigente y revisión desplegada. Aprovechar la validación, fingerprint, backup y acceso directo exacto ya existentes; verificar el ciclo completo desde la interfaz y la recuperación tras fallos.

Dar instrucciones visibles de qué crónica seleccionar y qué debería ocurrir al aparecer. Recoger diagnósticos propios suficientes para localizar el evento, actor o escena del fallo. No crear un nuevo launcher ni depender de herramientas originales.

Editar la campaña después del ensayo y comprobar que el build anterior no se ofrece como resultado de la nueva fuente. Avisar claramente cuándo el contrato exige partida nueva. La migración de saves entre versiones queda fuera del compromiso inicial.

### 5. Verificar recursos propios y distribución

Cerrar B3 con un template propio y un item utilizables en Redemption, dentro del subconjunto NOT/AI ofrecido. Un lector lossless o un writer parcial no bastan para declarar independencia completa de esos formatos.

Probar el portable en un equipo/VM independiente sin Python/JDK globales, con otra ruta y permisos normales. Repetir apertura, catálogo, edición, compilación e importación/exportación de un paquete propio. Comprobar proyectos anteriores y preservar los originales del juego, excepto el contenido propio autorizado dentro de RCM.

Si se anuncia soporte de varios jugadores, completar también host/client, decisiones, transiciones, retorno y desconexión/reentrada. No extrapolar una sesión local a funcionamiento en red.

## Criterios de salida

| Caso | Evidencia requerida |
|---|---|
| Autoría real | Campaña nueva completada en GUI sin editar YAML/Java para el recorrido cubierto; abrir/guardar/reabrir conserva datos |
| Diálogo | Aceptar, rechazar primero, abortar y reabrir; cámara/cursor/HUD/movimiento recuperados en todos los casos |
| Persistencia | Save/load en los puntos anteriores conserva decisiones, inventario y quest; sin recompensa repetida |
| Escenas | Tres ciclos de transición/regreso sin duplicados; dos escenas con la misma geometría y contenido propio distinto |
| Posicionamiento | NPC visibles y accesibles; transforms comprobados en juego; objetos base que permanezcan identificados |
| Recursos propios | Template e item propios instanciados y utilizables; subconjunto soportado declarado |
| Paquetes | Dos proyectos independientes sobre la misma geometría exportados/importados sin mezclar contenido |
| Distribución | Portable ejecutado en equipo/VM limpio independiente y otra ruta; prueba local adicional de workspace nuevo |
| Red | Host/client probado si forma parte de la beta anunciada; B5 permanece abierto en otro caso |
| Regresión | Checks apropiados satisfactorios, proyectos anteriores compatibles y evidencia identificada de integridad de originales |

No cerrar la fase con fallos críticos abiertos en el recorrido admitido. Mantener resultados PASS, FAIL y NOT TESTED por caso. Los tests deben cubrir defectos y contratos relevantes; una cifra mayor de tests o cobertura no sustituye la aceptación de juego y autoría.

## Qué queda aplazado

Geometría, modelado, texturas, disciplinas nuevas, AI completa, editor genérico de todas las plantillas NOT, paths completos, timeline cinematográfico, luces y audio espacial avanzados, paridad completa con Embrace y migración de saves. Puertas existentes se priorizan sólo si son necesarias para el recorrido elegido y se confirma su control runtime; no se incluye generar geometría de puertas.

Los ajustes individuales de niebla/EAX/ZClip pueden esperar si los perfiles originales ya permiten el escenario aceptado. Una función debe incorporarse antes sólo cuando resuelva un impedimento comprobado del recorrido.

## Entregables de ejecución futura

- Campaña de aceptación creada realmente desde el editor y paquete reproducible.
- Registro por caso de pruebas nativas, revisiones ensayadas y defectos resueltos o limitaciones.
- Guía corta que reproduzca el recorrido desde proyecto vacío hasta partida.
- Portable validado en entorno independiente y reporte de compatibilidad/regresión.
- Actualización de matriz de capacidades y release blockers según evidencia; no por cambio de número de fase.

La implementación técnica ya se ha iniciado y entregado. La experiencia aceptada de principio a final sigue pendiente de la prueba manual y de corregir los casos que se observen. No se han cambiado los resultados históricos ni se ha iniciado otra fase.

# RCM — Implementar dificultad configurable por crónica

Trabaja sobre mi repositorio privado de GitHub:

**MetisC/RedemptionChronicleMaker**

El proyecto es Redemption Chronicle Maker (RCM), actualmente en versión 1.0.0-rc7, un editor independiente de crónicas para Vampire: The Masquerade — Redemption.

## Objetivo

Implementar un **selector de dificultad de combate por crónica**, accesible desde las propiedades generales de la crónica en el editor.

Opciones:

- **Fácil:** enemigos menos resistentes y con atributos de combate ligeramente reducidos.
- **Normal:** comportamiento original, sin ninguna modificación.
- **Difícil:** enemigos moderadamente más resistentes y peligrosos.
- **Pesadilla:** enemigos considerablemente más resistentes y peligrosos.

La dificultad debe afectar a todos los enemigos controlados por RCM, tanto actores colocados manualmente como enemigos de encuentros dinámicos, incluidos jefes y oleadas.

## 1. Investigación obligatoria

Antes de modificar código:

1. Leer `AGENTS.md` y la documentación técnica vigente.
2. Estudiar `campaign.py`, `campaign_generator.py`, `dynamic_runtime.py`, `dynamic_encounters.py`, el inspector y los componentes de interfaz correspondientes.
3. Consultar `research/API_SIGNATURES.txt` para comprobar las funciones reales disponibles en Codex.
4. Analizar `GetActorStat`, `SetActorStat`, `GetActorBaseStat`, `SetActorBaseStat`, las funciones de salud y absorción.
5. Determinar qué atributos afectan realmente al combate, sin asumir que todos tienen efectos conocidos.

Utilizar exclusivamente APIs y mecanismos respaldados por evidencia del motor original. No inventar funciones ni modificar ejecutables del juego.

## 2. Implementación

Añadir un ComboBox de dificultad en las propiedades generales de cada crónica.

Persistir la selección en el YAML del proyecto. Las crónicas existentes sin esta propiedad deben utilizar Normal por defecto.

Crear una lógica de escalado centralizada y reutilizable desde:

- `spawn()` para enemigos normales con `behavior: enemy`.
- `dynamicSpawn()` para enemigos generados por el sistema de encuentros dinámicos.

Aplicar los modificadores una sola vez al crear o inicializar un enemigo nuevo. No modificar sus plantillas originales ni sus archivos fuente.

Proponer multiplicadores conservadores para salud y atributos ofensivos/defensivos, manteniendo siempre las diferencias relativas entre enemigos débiles, élites y jefes. Evitar que la dificultad consista exclusivamente en multiplicar los puntos de vida.

Respetar las opciones personalizadas de salud de los encuentros dinámicos, definiendo claramente el orden entre el override individual y la dificultad global.

No alterar jugadores, aliados, NPC neutrales ni personajes destinados únicamente a conversaciones. Tener en cuenta también los overrides de equipo de los generadores dinámicos.

## 3. Compatibilidad y seguridad

Requisitos imprescindibles:

- Mantener compatibilidad con formatos de proyecto 9 y 10.
- No actualizar obligatoriamente los proyectos existentes.
- No modificar el comportamiento de la dificultad Normal.
- No aplicar escalado repetido al cargar partidas o reentrar en escenas.
- Respetar la persistencia de GUID y el estado de enemigos existentes.
- No alterar innecesariamente el esquema de guardado nativo.
- Mantener las fases de jefes, eventos de muerte, recompensas, encuentros y demás lógica existente.
- No modificar recursos originales del juego.
- No introducir otro motor de combate ni un runtime paralelo.
- No incrementar la versión del producto sin necesidad.

Si modificar la dificultad de una crónica ya iniciada puede provocar inconsistencias, implementar la advertencia correspondiente y documentar el comportamiento.

## 4. Pruebas obligatorias

Añadir pruebas automatizadas que verifiquen:

- Lectura, escritura y validación del nuevo ajuste.
- Compatibilidad con crónicas antiguas.
- Dificultad Normal idéntica al comportamiento anterior.
- Escalado correcto en enemigos manuales y dinámicos.
- Exclusión de NPC neutrales y aliados.
- Ausencia de escalado duplicado.
- Respeto de overrides individuales y umbrales de jefes.
- Generación y compilación correcta del Java contra Codex.
- Compatibilidad de guardado/carga hasta donde permitan las pruebas automatizadas.

Ejecutar la batería de calidad del repositorio y corregir las regresiones introducidas.

No declarar validado el comportamiento dentro de Redemption mediante simulaciones o mocks. Las pruebas reales en el juego corresponden al usuario.

## 5. Método de trabajo

Trabaja de manera autónoma, investigando e implementando la solución completa.

Utiliza una rama independiente para los cambios. No modifiques directamente `main`.

No hagas refactorizaciones ajenas al objetivo, no sustituyas funcionalidades existentes y no añadas dependencias innecesarias.

Si alguna API no permite un escalado seguro de determinado atributo, descarta ese atributo y explica por qué. Prefiero una implementación limitada pero fiable antes que una aparentemente completa que pueda romper el juego.

## 6. Entrega final

Al terminar:

1. Presentar una tabla con los modificadores exactos de Fácil, Normal, Difícil y Pesadilla.
2. Explicar qué archivos se han modificado y por qué.
3. Indicar las pruebas ejecutadas, resultados y limitaciones.
4. Preparar un Pull Request con los cambios.
5. Proporcionar una pequeña lista de comprobaciones manuales que debo realizar dentro de Redemption.

**Importante:** el objetivo es ampliar RCM sin perjudicar ninguna funcionalidad existente. Investiga primero, implementa después y verifica antes de entregar. No declares una funcionalidad plenamente compatible con el motor hasta que haya evidencia suficiente.
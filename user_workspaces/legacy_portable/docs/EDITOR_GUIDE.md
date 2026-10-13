# Guía del editor — 0.7.0

La demo actual está en `chronicles/phase7_demo/project.yaml`, **Londres: prueba de estabilización**. El nuevo selector **Entorno original** está en las propiedades de Level base. [Prueba actual](PHASE7_PLAYTEST.md). Las instrucciones de Fase 6 que siguen se conservan como referencia del flujo común.

## Revisión de Fase 6

El ejemplo de aceptación actual es `chronicles/system_test/project.yaml` (**RCM System Test**). La distribución de `build/portable/RedemptionChronicleMaker/` incluye el EXE, bibliotecas y JVM: conserva toda esa carpeta. En un workspace nuevo, el primer arranque lee la instalación original y crea sus catálogos; no importa recursos originales dentro de la distribución.

Antes de compilar, **Guardar** confirma también el texto Java pendiente del panel Recursos y conserva backup. **Build** valida, compila y verifica referencias en una carpeta provisional; publica el resultado sólo si todo termina correctamente. Un fallo deja el build marcado como fallido y bloquea Deploy. **Limpiar build** elimina únicamente salidas registradas del generador, conservando archivos ajenos.

**Paquetes** permite exportar/importar proyectos y crear, revisar, instalar o desinstalar paquetes de crónica. Revisa nombre, versión, archivos y Java antes de instalar. Los paquetes instalados se mantienen dentro de `RCM/<id>`; dependencias declaradas se verifican por versión, pero no se incorporan recursos de otras crónicas automáticamente. [PACKAGES.md](PACKAGES.md) explica el contrato.

**Acceso del juego…** selecciona tu acceso `.lnk` existente. Deploy del editor utiliza su carpeta `-user`; Ejecutar abre exactamente ese acceso. En este equipo corresponde a `RCM/east_demo`. No cambia sus propiedades. Si el juego está abierto, ciérralo antes de reemplazar recursos. Una advertencia de cambios en el contrato de guardado exige iniciar partida nueva; no existe migración automática de partidas antiguas.

Eliminar una entidad con referencias se bloquea antes de cambiar el proyecto. Cancelar una confirmación conserva la selección y los datos. `--safe-mode` abre los paneles de datos sin contexto OpenGL. [TESTING.md](TESTING.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md) y [RUNTIME_TEST_MATRIX.md](RUNTIME_TEST_MATRIX.md) separan las comprobaciones del editor de los ensayos pendientes en Redemption.

## Abrir el ejemplo

Desde `H:\Repositorios\RedemptionChronicleMaker`:

```powershell
& 'C:\Users\Usuario\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' editor.py chronicles/phase3_demo/project.yaml
```

Espera a **Listo** en Espacio 3D. Selecciona **Victoria** en el árbol y pulsa **F** para encontrarla. El centro muestra el mapa; a la derecha, Properties; a la izquierda, Outliner. Abajo: Problems, Build / Log y Referencias. Arrastra los separadores para ampliar la vista. **Historia / Recursos** conserva los controles narrativos de Fase 2.

El ejemplo contiene Victoria, un segundo personaje, un barril original y **Entrada del pacto**, con condición `alliance` y acciones que activan `entered` y crean el segundo personaje. Los actores previstos para spawn diferido también se ven en el editor: la vista muestra la escena de autoría, no el estado de una partida.

## Navegar y seleccionar

| Control | Acción |
|---|---|
| Botón derecho y ratón | Mirar libremente |
| WASD | Mover cámara |
| Q / E | Bajar / subir |
| Shift | Mover más rápido |
| Rueda | Ajustar velocidad |
| F / Enfocar | Centrar selección |
| Alt + botón izquierdo | Orbitar selección |
| Click izquierdo sobre entidad | Seleccionarla |
| 1 / 2 / 3 | Mover / Girar / Tamaño |
| Esc | Cancelar colocación |
| Ctrl+Z / Ctrl+Y | Deshacer / rehacer |

**Suelo** mantiene altura aproximada al caminar; desmárcalo para volar. No incorpora colisión contra paredes. F permite recuperar una selección si te alejas. Seleccionar en el mapa, árbol o Properties sincroniza la misma entidad.

## Crear crónica y elegir level

1. **Archivo → Nueva crónica**, Ctrl+N: ID, nombre, descripción y directorio dentro del workspace.
2. **Level base → Elegir level base…**: busca por nombre/ID/procedencia; por ejemplo East London · EastLondon. Pulsa **Usar selección**.
3. **Título al entrar** define el texto de carga; vacío usa el nombre de la crónica.
4. Abre **Espacio 3D** y espera a que carguen geometría/texturas.

Levels **Solo catálogo** todavía no tienen una combinación inequívoca de geometría/escena estudiada para build. Los catálogos se generan del juego. El escenario conserva su geometría y entorno; no importa la narrativa/personajes originales.

## Colocar actores y objetos

1. Selecciona **Recursos originales**, categoría **Plantillas de actores**.
2. Busca `businessWoman`, selecciona la fila inequívoca y pulsa **Usar selección** o doble clic.
3. Vuelve automáticamente a Espacio 3D. Haz clic sobre una superficie de suelo visible.
4. El actor aparece allí; arrastra sus ejes con **Mover** y el anillo con **Girar**.
5. En Properties cambia ID/nombre y conversación. Renombrar actualiza referencias; coordenadas y yaw numéricos siguen disponibles para precisión.

También puedes usar **Actores → + Actor** desde Espacio 3D: abre el selector de plantilla antes de pedir el punto. Desde Historia conserva la creación como dato relativo al jugador.

Para props/ítems, usa categoría **Objetos**, por ejemplo `barrel1`, y el mismo flujo de colocación/movimiento/giro. Solo se ofrecen familias que acepta el backend; que un recurso exista no acredita su instanciación nativa. Plantillas sin modelo directo/compatible muestran marcador y aviso. Modelos, escenas y AI son consulta, no plantillas que puedan colocarse por sí solas.

Los nuevos elementos tienen spawn de inicio. Para que un trigger cree un actor/objeto, desmarca **Crear al iniciar la escena** y añade su spawn al evento de entrada. Un borrador sin propietario de spawn será ERROR hasta completar esa relación; no se permite duplicarla.

NPC actuales: neutros, AI pausada e interacción si tienen conversación/evento de clic. No existe una simulación de AI en el viewport.

## Ajustar y usar snap

**Mover** usa XYZ del mundo; **Girar** modifica yaw. **Tamaño** cambia dimensiones de caja/radio de esfera, sin escalar actores. Properties se actualiza durante el arrastre y sus campos actualizan la vista.

Grid 0 significa libre; otro valor activa snap. El campo angular controla el incremento de giro; 0 libre. **Snap suelo** ajusta altura en movimientos horizontales. **Ajustar al suelo** está en Properties. El origen de un prop puede necesitar un offset Z; esta ayuda no sustituye la colisión del motor.

**Junto al jugador** conserva la colocación relativa del YAML. Su marcador se etiqueta aproximado, pues el editor no conoce el jugador de una partida. Mover ese marcador lo convierte explícitamente a Coordenadas. Abrir el proyecto no lo convierte ni guarda cambios por sí solo.

## Crear y configurar triggers

1. En Espacio 3D pulsa **+ Trigger** y haz clic en el suelo.
2. Selecciona **Caja** o **Esfera** en Properties; ajusta centro, yaw de caja, dimensiones/radio y activación **Una vez / Cada entrada**.
3. Mueve/redimensiona con gizmos; una caja recién creada queda apoyada por su mitad inferior.
4. **Añadir evento de entrada** abre el Event Editor existente.
5. **+ Condición** elige flag y estado requerido; todas las condiciones deben cumplirse.
6. Edita la primera acción propuesta o añade otras con **+ Acción**: Crear actor/objeto, Activar flag o Desactivar flag. Completa sus objetivos.
7. Selecciona el trigger para revisar activación, condiciones, acciones y afectados; **Mostrar relacionados en 3D** los enfoca/resalta.

El evento propuesto tiene una acción de flag para empezar; cámbiala al estado que realmente necesites. La demo usa `alliance` activado como condición y `entered` como resultado. Si la condición falla al entrar, hay que salir y volver para reevaluarla. **Cada entrada** significa volver a entrar después de que todos los jugadores salgan; el polling de 0,15 s puede perder cruces muy rápidos. Una conversación activa pausa la comprobación.

Los triggers generan lógica Java propia, sin geometría nueva. Su comportamiento en una partida, save/load y red sigue pendiente de ensayo nativo.

## Dependencias, referencias y capas

En Properties, **USED BY / Dependencias** muestra quién referencia la selección; **AFFECTS / Referencias**, a qué apunta. Doble clic navega. **Find References / Buscar referencias** o botón derecho en el árbol abre una lista navegable abajo. Actores muestran conversaciones y eventos de spawn/clic; triggers muestran sus eventos y condiciones/acciones.

**Relaciones** activa líneas/resaltado local de relacionados. Selecciona un evento en Historia y **Mostrar relacionados en 3D** para ver sus objetivos. No se muestran permanentemente todos los enlaces.

Casillas del Outliner ocultan categorías o entidades. No cambian el YAML ni el build. Referencias originales aparecen grises, solo lectura, inicialmente ocultas. Se extraen de una escena asociada mediante patrones; no son un inventario exhaustivo. Nuestra capa se edita; paredes y geometría no se pueden mover ni borrar.

## Conversaciones, flags y eventos anteriores

**Conversaciones → + Conversación**: actor principal, nodo de entrada, líneas y respuestas. Una respuesta lleva a otro nodo (GOTO) o termina con RETURN positivo y único; puede activar/desactivar flag al finalizar. **+ Nodo / Línea / Respuesta** y **Subir/Bajar** editan la estructura. Las conversaciones simples antiguas no se migran al abrir; añadir un nodo las convierte explícitamente.

En el actor usa **Al hablar**, o eventos explícitos de clic, nunca ambos. **Chronicle Flags → + Flag** crea alias/índice único 0..255; renombrar actualiza referencias. El Event Editor admite inicio, clic, fin de conversación y entrada de trigger. Los eventos de clic requieren una conversación y se toma el primero cuyas condiciones coinciden. Aborto/RETURN desconocido no activa eventos de fin. Inicio puede volver a evaluarse tras cargar un save: evita reiniciar indiscriminadamente flags persistentes.

Ejemplo entregado: Victoria → **¿Quién eres? → Cuenta conmigo.** activa `alliance`; después el saludo recuerda el pacto. **El pacto termina aquí.** lo desactiva.

## Guardar, recuperar, validar y build

Ctrl+S guarda; Ctrl+Shift+S copia dentro del workspace. Para otro build independiente cambia también el ID de la crónica: rutas distintas con ID igual comparten `build/<ID>`. Asterisco indica cambios, incluidos IDs escritos sin confirmar. Guardar/Validar/Build confirman esos campos; un ID inválido no sobrescribe el fuente.

Deshacer/Rehacer mantiene hasta 40 estados en memoria. Al cerrar o abrir se ofrece guardar/descartar/cancelar. Cada 30 segundos hay autosave YAML; al abrir se ofrece recuperarlo. Esto complementa el historial, sin sustituir backup/versionado.

**Validar** muestra ERROR/WARNING/INFO; doble clic navega cuando hay contexto. Errores bloquean build. INFO de posición recuerda que el editor no prueba collision del runtime. Textura ausente usa patrón magenta y registra warning en `cache/levels/<level>.json`.

**BUILD CHRONICLE / F5** guarda y construye en un trabajador separado. Muestra generación, compilación y empaquetado. No edita/cierra el proyecto mientras compila. Resultado de la demo:

```text
build/phase3_demo/
    phase3_demo_distribution.zip
    phase3_demo.nob
    bundle/
        phase3_demo.nob
        codex/
            R_phase3_demo_Scene.class
            R_phase3_demo_Passive.class
    runtime/
    generated/java/
    compiler.log
    build_report.json
```

El ZIP es una carpeta compacta. Build successful acredita generación/compilación, no ejecución en Redemption. El editor no copia recursos al juego ni lo lanza automáticamente.

## Pruebas preparadas en RCM

Con la autorización expresa del usuario, se han añadido el NOB y dos clases de Fase 3 a **RCM/east_demo**, conservando los seis archivos de las pruebas anteriores. El directorio **RCM/phase3_demo** es para el log. Backup y manifiesto: `research/runtime_test/backups/` y `deployment_phase3_demo.json`.

Usa el acceso directo habitual con **-user RCM\east_demo**, trabajando desde la raíz del juego. En **Multiplayer → New Game**:

- **RCM: Victoria y el pacto de Londres**: la prueba cercana al jugador de Fase 2, ya aceptada; conserva diálogo/elecciones y el fondo gris.
- **RCM: Londres, autoría espacial**: nueva demo con posiciones absolutas elegidas en el editor. No promete NPC junto al inicio. Localiza primero Victoria y Entrada del pacto con F en el editor para estudiar la zona y prueba la escena en una partida nueva. NPC absoluto, props y triggers necesitan confirmación nativa.

Para probar el trigger nuevo, habla con Victoria y acepta el pacto; entra después en Entrada del pacto. Debe crear el segundo actor y activar `entered`. Salir/volver no debe duplicar una entidad. Conserva `RCM/phase3_demo/runtime_trace.log` para comprobar `trigger_enter`; no lo confundas con logs de tests. Prueba save/load por separado. El agente no ha ejecutado Redemption ni afirma que esa demo nueva esté aceptada.

Tras otro build, el resultado está en el workspace: para actualizar manualmente RCM, cierra el juego y copia el contenido completo de `bundle/` a la carpeta elegida, con backup previo y sin tocar originales fuera de RCM. No basta un NSC suelto. Todos los archivos propios permanecen juntos, como documenta USER_DIRECTORY.md.

## Fase 4: crear y probar una campaña

Abre chronicles/phase4_demo/project.yaml. La pestaña Campaña / Quests elige la escena activa; Espacio 3D e Historia editan sus mismas entidades. Para un proyecto anterior, pulsa Crear campaña explícitamente; no se migra al abrir. El ID de campaña admite 14 caracteres para reservar namespace a las escenas.

+ Mapa abre el catálogo original. Seleccionar su fila muestra propiedades y permite elegir Entrada. + Quest crea título, descripción, pasos y recompensa. + Encuentro selecciona enemigos ya creados; desactiva su spawn directo y usa Spawn Encounter en un evento. + Cámara crea un plano enfocado en actor.

El Event Editor existente ofrece callbacks ampliados, condiciones anidadas y acciones agrupadas por función. Las respuestas producen RETURN; un evento de fin con ese resultado aplica inventario/quest/viaje. Tiene objeto y Quitar permiten seleccionar objetos de otras escenas. Find References, global search y renombres conservan esos enlaces. Búsqueda Ctrl+Shift+F muestra resultados navegables de todos los mapas. Undo/Redo cubre el documento completo; también Ctrl+Shift+Z.

Demo RCM: El libro de Londres: Victoria está junto al jugador. Pregunta quién es y elige Cuenta conmigo; se inicia El libro desaparecido. Vuelve a hablar y elige Vamos al oeste de Londres, o usa el trigger Paso al oeste situado en el editor. En WestLondon aparecen Contact y Keeper, tres enemigos y el libro junto al jugador. Recoge el libro; habla con Contact y elige Continuar para regresar. Habla con Victoria y elige Seguimos juntos: requiere conservar el libro y tener el tercer paso activo; lo retira, completa la quest y entrega 500 XP. El encuentro concede 100 XP al observar muertos sus tres integrantes. Hay música de combate, música al despejar y un plano amplio al llegar.

**Esta es la conducta generada, pendiente de partida nativa.** Si algún paso falla, consulta RCM/phase4_demo/runtime_trace.log y no avances artificialmente para darlo por probado. No cargar una partida de otra versión del esquema; iniciar una nueva.

Deploy copia un build válido con backup dentro de RCM; exige volver a compilar si el documento cambió desde el build. Ejecutar abre el juego con esa carpeta de usuario; ve a Multiplayer → New Game y busca RCM: El libro de Londres. La entrega también está en RCM/east_demo para usar el acceso directo anterior. Más detalle en DEPLOYMENT.md, QUESTS.md e ITEMS.md.
# Perfiles de escena — Fase 7

Selecciona **Level base** y abre **Entorno original** en Propiedades. Automático conserva la selección histórica; una escena original asociada copia su bloque de entorno completo, sin importar NPC o scripts. Puedes guardar y deshacer la elección. Al cambiar de level se elimina ese perfil para evitar asociaciones cruzadas. `level.sky`, si existe en YAML, prevalece como override y se indica en el inspector. No se muestran controles de niebla individuales hasta confirmar sus offsets y comportamiento nativo.

Demo actual: `chronicles/phase7_demo/project.yaml`, nombre **Londres: prueba de estabilización**. [Recorrido de prueba](PHASE7_PLAYTEST.md) y [diferencias entre scene y level](SCENE_MODEL.md).

# Recorrido actual de Fase 9

Para crear una campaña de formato 9, colocar entradas y waypoints, editar recorridos y probar el circuito único, consulta [PHASE9_PLAYTEST.md](PHASE9_PLAYTEST.md). La guía histórica siguiente conserva el contexto del editor anterior. El portable actual está en `build/portable/RedemptionChronicleMaker/`.


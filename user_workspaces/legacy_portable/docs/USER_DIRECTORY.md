# Una carpeta por crónica: opción nativa -user

Investigación adicional: 8 de octubre de 2026. El agente no ha ejecutado el juego. Tras autorización expresa posterior se ha desplegado el paquete corregido exclusivamente dentro de RCM. Se corrige la recomendación anterior de que los archivos deban extraerse necesariamente en la raíz del juego.

## Confirmado en el ejecutable original

El análisis estático de `Vampire.exe` muestra:

- `-user` y `/user` se reconocen en `0x427be2` y `0x427bf8`.
- El handler `0x4281f1` obtiene el siguiente token y lo copia a un buffer de 128 bytes (`0x613bc4`), terminado en NUL.
- En `0x42848e` se comprueba ese buffer y se llama a la rutina `0x4cac10`, que registra la ruta adicional. Su constructor de lista `0x4cbbd0` busca contenedores con extensión `nob` en dicha ruta; el formato de unión de rutas es `%s\\%s`.
- La inicialización JVM `0x4b3ae0` usa el mismo buffer para construir este classpath cuando hay ruta de usuario:

```text
classes.zip;<user>\codex;<user>\codex\system;<user>\codex.nob;codex;codex\SP;codex\MP;codex\system;codex.nob
```

La evidencia reproducible está en `research/user_directory/string_references.json` y `disassembly.txt`. La herramienta `tools/research_user_directory.py` lee el ejecutable, guarda una copia en el workspace y lo analiza con Capstone 5.0.7; no lo ejecuta. Las ventanas auxiliares de desensamblado pueden empezar entre instrucciones; las funciones indicadas tienen ventanas específicas desde sus entradas.

## Corrección tras el primer ensayo del usuario

El usuario informa el 8 de octubre que el selector Multiplayer → New Game muestra solo crónicas oficiales. Se comprobó por lectura que los 12 archivos de la distribución antigua están correctamente situados en `RCM/east_demo/`, sin ningún `.nob` en esa carpeta. El acceso directo mostrado tiene `-user RCM\east_demo` y directorio de trabajo en la raíz del juego. No se pudo inspeccionar la línea de comandos del proceso mediante CIM por permisos; la comprobación del acceso directo se basa en la captura aportada.

La rutina del selector en `0x412a29` llama a `0x4cae60` con `chronicles` y `nsc`, carga cada candidato y filtra el bit `0x2` de flags. El enumerador construye la ruta prefijada en `0x4caec8`, pero en `0x4caee8` pasa el argumento original de directorio a la búsqueda física. Por tanto, esa búsqueda no enumera los NSC sueltos bajo la carpeta `-user`. Después recorre los índices de los NOB registrados desde `0x4cafc8`, añadiendo entradas con la extensión solicitada. Esta diferencia explica el fallo del despliegue únicamente con archivos sueltos.

El usuario confirmó en la revisión 3: nombre correcto, mapa cargado, halo desaparecido, Victoria visible junto al jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara de diálogo se percibe algo baja. Save/load y replicación en red no se han probado. El cielo Sky de revisión 4 espera comprobación.

## Estructura prevista y prueba

Una sola carpeta reúne toda la crónica; sus subcarpetas siguen representando las rutas internas de recursos. Para el primer ensayo, dentro de la **copia independiente del juego**:

```text
game/
    Vampire.exe
    RCM/
        east_demo/
            east_demo.nob
            codex/
                R_east_demo_Scene.class
                R_east_demo_Passive.class
```

La revisión actual ya está desplegada en RCM/east_demo. Para futuras actualizaciones, extraer los tres archivos del ZIP regenerado y retirar únicamente recursos sueltos antiguos de esta crónica después de preservarlos. Añadir solo el NOB a una instalación con recursos antiguos ya no basta: esos recursos sueltos pueden ocultar sus correcciones. Reiniciar el juego tras actualizar. El acceso directo mantiene:

```text
-user RCM\east_demo
```

El campo «Iniciar en» debe ser la raíz de la copia, donde está `Vampire.exe`. Usar una ruta corta sin espacios: el handler observado separa tokens mediante espacios/tabuladores y no se ha comprobado soporte para rutas entrecomilladas.

La carpeta `build/east_demo/bundle/` contiene la distribución compacta sin comprimir. También es candidata como ruta absoluta de `-user`, sin copiarla dentro del juego; la resolución absoluta debe comprobarse en el ensayo nativo. `runtime/` conserva los archivos sueltos para inspección, pero no constituye por sí sola la distribución prevista para el selector.

El usuario autorizó modificar RCM. Se actualizaron el NOB y las dos clases, y se retiraron diez recursos sueltos antiguos; el contenido anterior está en research/runtime_test/backups/. Hashes y operaciones en deployment_visual_fix_2026_10_08.json. No se escribieron archivos fuera de RCM dentro de la instalación.

## Límites de lo comprobado

El usuario confirmó enumeración, nombre, carga, NPC y diálogo. La revisión actual es Redemption Chronicle Maker: Londres nuevo, con fondo Sky pendiente de observar. Seguir TEST_PLAN.md.

Una carpeta única y un archivo único son objetivos distintos. El NOB actual agrupa los recursos, pero omite Java; el classpath permite un `<user>\codex.nob` para clases. Por ello es razonable investigar una distribución compacta con NOB de recursos más `codex.nob`, ambos en una carpeta. No se afirma que un NOB arbitrario único resuelva la JVM ni que esa variante compacta ya esté validada.

## Historial: revisión 3 tras el segundo ensayo

El usuario confirmó el nombre correcto, pero la revisión anterior no solucionó el NPC al inicio ni el fondo/halo. La revisión 3 añade `NOT R_east_demo.not` al NMF para cargar nuestra biblioteca explícitamente y conserva `LOCATION_FLAG_CLEARBUFFER` de la referencia original (EastLondon: `0x60`, antes `0x20`). Mantiene el spawn cercano y los recursos LondonNightSky. Añade un registro generado por el juego en `RCM/east_demo/runtime_trace.log`, para comprobar construcción de la clase, callback de inicio, jugador y GUID de spawn. El archivo solo se escribe dentro de RCM usando el directorio de trabajo habitual. La compilación 45.3 y las 26 pruebas pasan; el resultado visual sigue pendiente. No se considera que el cielo o el NPC hayan sido demostrados por los tests con doubles. Detalles en ENGINE_NOTES.md y TEST_PLAN.md.

## Estado actual: fondo, revisión 4

El usuario confirmó en la revisión 3: nombre correcto, mapa cargado, halo desaparecido, Victoria visible junto al jugador, conversación a pantalla completa y elecciones recordadas en interacciones posteriores. La cámara de diálogo se percibe algo baja. Save/load y replicación en red no se han probado.

La revisión 4 cambia únicamente los dos nombres de fondo del NSD: LondonNightSky → Sky, un recurso original con estrellas, luna, nubes y forma de skyline. No se afirma que reproduzca el fondo exacto de EastLondon. Java, NPC, diálogo, flags y demás bytes de escena son idénticos a la revisión 3. Su resultado visual cerca del muelle sigue pendiente. Investigación: research/sky/FINDINGS.md; estado: research/runtime_test/revision4_status.json.

## Resultado de la comparación y revisión 5

El usuario confirmó que ambas comparaciones de EastLondon —mapa base con escena null y escena original EAST_28_1— muestran un fondo gris que considera adecuado. No se requiere añadir Sky para reproducir ese aspecto. La demo de revisión 5 omite level.sky y conserva íntegros los 176 bytes originales del entorno; los dos campos finales de modelo/animación están vacíos. Solo se eliminan las dos referencias añadidas; NPC, conversaciones, flags, Java y demás bytes de escena permanecen idénticos. Su aspecto final aún necesita comprobarse en una partida nueva de la demo.

Evidencia nativa aportada por el usuario: gris en ambas referencias. Evidencia estática: campos finales vacíos en los NSD originales y copia exacta de sus metadatos en la demo. La necesidad de un skybox extra queda descartada para este caso; no se generaliza a otros niveles. Los modelos añadidos en revisiones 3/4 fueron elecciones experimentales y no la configuración original de EastLondon. Estado y despliegue: research/runtime_test/revision5_status.json y deployment_revision5_2026_10_08.json. Se mantienen CLEARBUFFER y las correcciones funcionales de revisión 3. Las 26 pruebas pasan; save/load, red, aborto y ajuste de cámara siguen pendientes.

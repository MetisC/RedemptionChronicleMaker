# Cierre funcional de autoría — uso y aceptación

Las funciones siguientes son optativas en formatos 9/10; los objetivos dinámicos
requieren los encuentros del formato10. No convierten el tutorial ni la mini
crónica. No hay otra pestaña ni edición de geometría. Para probarlas por separado,
abre **Ayuda → Laboratorio de autoría**. Solicita una copia nueva si ya tenías una.

## Usarlo sin editar archivos

1. **Mapas:** selecciona Crónica → Mapas y localizaciones, o Campaña → Añadir… →
   Mapas y localizaciones. Nuevo mapa pide una imagen, adaptada a640×480. Añade
   puntos, arrástralos, cambia sus nombres/Visible/Refugio y asigna cada escena en
   la parte inferior. Aceptar es una operación de undo; Cancelar no copia imágenes.
   Eventos → flags de localización permite descubrir/ocultar y marcar refugios;
   la condición de localización visible usa la API nativa. Es un mapa informativo,
   sin viaje al pulsar. Se generan NUI,12teselas TGA, etiquetas NLS y enlace NSC.
2. **Giro y espera de cámara:** selecciona una secuencia → Crear/editar travelling
   propio → Tiempo por tramo. Duplica un punto sin desplazarlo y cambia Yaw/Pitch
   para girar; dos posiciones/orientaciones iguales son una espera. Edita los
   segundos hasta el siguiente punto. Velocidad nativa1, total máximo 120s. El modo
   anterior por distancia sigue exigiendo posiciones distintas. NCP originales
   se conservan íntegros. No hay FOV por keyframe.
3. **Región nativa:** crea un trigger caja. Sus propiedades permiten Región nativa
   para scripts, o asignarle Script nativo de región. Elige constructor original
   y parámetros; enlaces region/item seleccionan elementos locales. El script
   conserva entered/exited y su estado. No se mezcla con eventos RCM sobre esa
   misma región. Un controlador puede referenciar una caja marcada como región
   sin script. Máximo8 cajas, giroZ, sectores reales del NIL; no modifica el NIL.
4. **Zonas de sonido/luz:** sobre el mismo tipo de trigger, abre Zona sonora o
   Zona de luz dinámica. Configura WAV/volumen/radios o entidad/RGB/intensidad/
   radio/estilo. El volumen activa/desactiva un sonido situado o luz puntual;
   no equivale al recorte de las cajas originales por sectores. El bucle usa los
   handles y guardado existentes. No mezclar propiedad con un script nativo.
5. **Reverberación:** Level → Entorno → Reverberación EAX ofrece heredar o preset
   original 0..25. La acción Entorno / Reverberación cambia después el preset.
   Se usa roomtype, comando original probado por desensamblado y compilación;
   el proveedor de audio3D instalado determina si se oye el efecto.
6. **Actores generados:** selectores normales de sujeto, referencia, actor y
   entidad ofrecen «generador / rol #n». Es el enésimo actor vivo del rol en los
   slots del gestor existente, no un nuevo actor ni identidad permanente. Sirve
   para planos, mirar, gesto, movimiento, recorrido, sonido asociado, luz,
   inventario y equipo/pausa de IA. Un objetivo ausente falla de forma acotada;
   si cambia el GUID seguido por una película, ésta libera el control. Guardar
   conserva el roster previo; los alias sólo se resuelven tras reconciliar.
7. **Clanes/disciplinas:** Actor → Clan y disciplinas ofrece también los recursos
   originales sin importar un mod. WTD añade sólo lo importado y disponible.
   Los setters se aplican al actor nuevo; no reinicializan su estado restaurado.

## Archivos principales

Backend: chronicle_maps.py, native_regions.py, native_scripts.py, script_parameters.py,
dynamic_targets.py, camera_paths.py, campaign.py/campaign_generator.py, audio.py,
scene_zones.py, world_effects.py, actor_traits.py y formatos/recursos/relaciones.
Interfaz: editor/maps.py, zones.py, director.py, native_scripts.py, environment.py,
campaign_panel.py e inspector.py. Tests: test_authoring_completion.py y toda la
batería vigente. Evidencia: research/authoring_completion/EVIDENCE.md.

## Prueba manual corta, en este orden

Partida nueva del Laboratorio de autoría; habla con Anezka. Cada ejercicio está
separado. El tutorial aceptado y la mini crónica siguen disponibles.

| Caso | Qué comprobar dentro de Redemption |
|---|---|
| COMP01 | Giro en el sitio y espera: encuadre, giro corto, final y cancelación recuperan GUI/ratón; guardar/cargar cancela las películas con cues o sujeto NPC; Player sin cues conserva la reanudación anterior desde el inicio, sin duplicar recompensas. |
| COMP02 | Acercarse a la caja nativa junto al guardia: campana al entrar, callbacks correctos, sin caja sólida visible ni duplicados tras guardar/cargar/reentrar. |
| COMP03 | Zona sonora/luz: entrar/salir, un bucle, radio/color y apagado. Cambiar reverb con proveedor 3D; comparar oído, no sólo traza. Guardar/cargar activo. |
| COMP04 | Abrir mapa normal: imagen/puntos/nombres y refugio. Revelar segundo layout, comprobar visibilidad, viajar por diálogo y volver. Guardar/cargar mantiene flags. |
| COMP05 | Generar rata débil, seguirla con cámara, terminar/cancelar y matarla. Generar invitado neutral, comprobar movimiento/pausa y entrega/retirada de Dagger. Guardar/cargar/reentrar sin reemplazar GUID ni duplicar objetos. |
| COMP06 | Copia del ejemplo: cambiar clan y disciplina original desde la interfaz sin WTD; comparar actor creado y restaurado. Tutorial/mini siguen cargando como antes. |

Son pruebas pendientes de observación del usuario. Compilar contra Codex, releer
binarios, doubles y Qt offscreen no son gameplay, GPU/DPI físico ni prueba de red.

## Lo que no se declara cerrado

La matriz EMBRACE_AUTHORING_PARITY.md distingue las funciones implementadas de
dos incógnitas: binding seguro de constructores de campaña con CodexPlayer y
paridad literal de payload/recorte soundbox/lightbox. No se han probado imposibles.
Las alternativas normales Player Actions y zonas activadoras están disponibles.
El NCP no almacena FOV por punto; la importación genérica de código binario
desconocido se rechaza explícitamente. Geometría/bake queda fuera del encargo.


Al convertir un travelling compartido a tiempo por tramo, se actualiza la velocidad a1 en sus secuencias y acciones de reproducción dentro de la misma operación de deshacer.

# Comparación del muelle de EastLondon

**Resultado observado:** ambas referencias muestran gris y el usuario considera correcto ese fondo. Revisión 5 retira el cielo añadido de la demo y conserva el entorno original. La comprobación visual final de la demo queda pendiente.

El usuario probó revisión 4: el cielo estrellado se dibuja, pero se percibe enorme y aparece de repente. Esto confirma que los campos NSD controlan un modelo de cielo visible; no confirma que Sky sea un fondo adecuado para EastLondon. No se ha demostrado que haya un problema de escala global ni un archivo faltante. Reducir el modelo sin evidencia no es la corrección elegida.

## Por qué Londres no comenzaba en el mismo lugar

`MP_London_Null.nsc` tiene WestLondon como primera ubicación y `reviveloc WestLondon 0`. `London.nsc` de la historia comienza en SocietyOfLeopold3 y lo indica en un comentario. La demo tiene EastLondon como única ubicación y `reviveloc EastLondon 0`. Son crónicas con distintos puntos de entrada, aunque compartan ubicaciones londinenses.

## Comparación preparada

El archivo adicional `east_compare.nob` reside junto a `east_demo.nob` en RCM/east_demo y añade dos crónicas de diagnóstico. El acceso directo sigue usando `-user RCM\east_demo`.

| Nombre del menú | Geometría | Escena añadida | Referencia original |
|---|---|---|---|
| RCM: EastLondon - mapa base original | l1_east.nil | null | MP_London_Null.nsc |
| RCM: EastLondon - escena original | l1_east.nil | EAST_28_1.nsd | London.nsc |
| Redemption Chronicle Maker: Londres nuevo | l1_east.nil | R_east_demo.nsd | Nuestra demo (revisión 5: entorno original; revisión 4: Sky) |

Las dos referencias entran directamente en EastLondon y declaran entrada de reaparición 0, como la demo. La coincidencia del punto visible debe comprobarse en juego: compartir identificador de entrada no sustituye esa observación. No añaden otro cielo ni modifican NIL, NSD, texturas o clases originales. La variante de escena original puede mostrar sus NPCs/scripts y no representa una campaña London completa; se usa para observar el entorno, sin probar sus quests o conversaciones.

## Cómo probar

1. Abrir el mismo acceso directo y entrar en Multiplayer → New Game.
2. Crear una partida nueva de **RCM: EastLondon - mapa base original**. Comprobar si reconoces el inicio de la demo y seguir el mismo recorrido al muelle.
3. Repetir con **RCM: EastLondon - escena original**. Comparar inicio y fondo en el mismo lugar, con una cámara parecida.
4. Comparar con **Redemption Chronicle Maker: Londres nuevo**. Registrar en cuál aparece el azul vacío, una silueta urbana o el cielo grande, y si la posición inicial coincide.

Si una referencia empieza en otro punto, conservar esa observación: investigaremos las entradas reales antes de comparar imágenes. No hace falta buscar el muelle recorriendo WestLondon.

## Qué permitirá decidir

- Fondo correcto en la referencia base pero distinto en la demo: investigar qué configuración de la escena nueva sustituye la del mapa base.
- Fondo distinto solo con la escena original: estudiar esa escena y sus capas; no importar por obligación su narrativa al generador.
- Azul también en ambas referencias: la ausencia de skyline no demuestra que nuestra herramienta haya omitido un recurso. Habrá que decidir un fondo apropiado para la nueva crónica o identificar otro mapa original.
- Cielo visible pero aparición brusca solo en la demo: contrastar la visibilidad del recurso añadido con los sectores/portales del NIL. No editar geometría ni escalar recursos antes de aislarlo.

Esto es investigación de Fase 1; las escenas originales solo sirven como comparación. El workflow de creación sigue usando nuestros formatos y Java, sin herramientas antiguas.

Paquete y manifiesto en `build/diagnostics/east_compare/`; generación reproducible mediante `tools/build_east_comparison.py`. Evidencia del despliegue en `research/runtime_test/deployment_east_comparison_2026_10_08.json`. Ambas opciones fueron probadas por el usuario: fondo gris en las dos.

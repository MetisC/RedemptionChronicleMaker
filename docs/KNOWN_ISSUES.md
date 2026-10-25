# Problemas y límites actuales · 1.0.0-rc10

- Nuevo primer arranque, lanzamiento directo, Showcase y ciclos de guardar/cargar requieren aceptación manual. La historia y clases del tutorial aceptado se conservan sin cambios.
- El ensayo con directorios limpios y PATH restringido en este equipo no demuestra funcionamiento en otra máquina.
- Red real experimental; se centra en uso local con un jugador.
- No hay migración de partidas entre estructuras diferentes.
- El encuadre inicial del tutorial fue percibido como lejano; se conserva el comportamiento aceptado.
- NCP lineal propio implementado; encuadre/reproducción nativa pendiente en EMB09–11. FOV por keyframe, geometría editable, puertas universales y eliminación universal de estática no están implementados.
- El guardado de estado nativo y sus efectos no constituyen una transacción atómica del motor.

## Modelos en el selector

La previsualización de modelos muestra la geometría y las texturas del modelo original en pose estática; no reproduce sus animaciones. Los recursos se leen de la instalación/importación del usuario y no se distribuyen en el portable. Un modelo ausente o no compatible muestra un aviso; explorar el catálogo no modifica la crónica.

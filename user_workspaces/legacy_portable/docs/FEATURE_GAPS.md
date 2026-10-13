# Huecos de funciones

| Función | Estado | Consecuencia |
|---|---|---|
| Packaging/export/import/rollback | IMPLEMENTED Fase 6 | Antes faltaban; ahora backend y menú propios, tests de seguridad y roundtrip |
| Primera ejecución/cache recovery | IMPLEMENTED Fase 6 | Reconstrucción de catálogos, backup y modo sin OpenGL |
| Safe Delete | IMPLEMENTED Fase 6 | Bloquea referencias, no rompe silenciosamente el proyecto |
| Java visible pendiente y huella de assets | IMPLEMENTED Fase 6 | Guardar/compilar/desplegar ven modificaciones de fuentes propias |
| NOT completo / stats, disciplinas | PARTIAL / NOT IMPLEMENTED | Sólo tags documentados, desconocidos preservados, writer experimental |
| AI / paths / waypoints | PARTIAL / NOT IMPLEMENTED | Escalares de .nai y pause/enable; no editor de rutas/comportamientos arbitrarios |
| Cámara / secuencia completa | PARTIAL | Plano por actor, tipo, ángulo y duración; no posiciones libres ni timeline |
| Puertas y entradas de viaje propias | NOT IMPLEMENTED | Jump cambia location y usa entrada del runtime original |
| Grafo de conversación editable | PARTIAL | Proyección y navegación; autoría por árbol/propiedades |
| Cache de relaciones incremental | NOT IMPLEMENTED | Grafo se deriva del YAML; fixture de 486 enlaces tarda ~12 ms con tracing |
| Migración de saves del juego | NOT IMPLEMENTED | Cambios estructurales avisan de partida nueva |
| Canceler Build | NOT IMPLEMENTED | Worker mantiene editor protegido mientras termina |
| Rendering fiel al engine | PARTIAL | Materiales/UV/modelos estáticos; iluminación, animación y niebla no reproducidas |
| Configuración viewport persistida | PARTIAL | Defaults seguros; no persistencia completa de todas las preferencias |
| Dependencias entre paquetes | PARTIAL | Validación local de versión/conflictos, sin composición de assets runtime |
| Distribución en máquina limpia | NOT TESTED | Ensayo local portable no sustituye VM/equipo independiente |
| Red | NOT TESTED | No dar por válida replicación por tener guardas NetIsClient |

Alcance de crónica completa actual: varios escenarios originales; NPCs/objetos/triggers/eventos; ramas y flags; quests/journal abstracto; inventario/encuentros; planos/audio/viajes; build y distribución propios. La cadena técnica está comprobada offline; la crónica completa necesita terminar el checklist nativo para ser aceptada como beta.

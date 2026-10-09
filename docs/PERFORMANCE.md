# Rendimiento local

Equipo Windows 11, Python 3.12.14. Tiempos de load/save/validate/references/search medidos con tracemalloc activo; compilación sin tracing. No son promesa para otros equipos. Search aquí mide filtro de enlaces, no toda la UI de búsqueda.

| Fixture | Load s | Save s | Validate s | References s | Build s | ZIP bytes |
|---|---|---|---|---|---|---|
| system_test | 0.151 | 0.0349 | 0.8395 | 0.0014 | 3.5404 | 394605 |
| golden | 0.1404 | 0.0321 | 0.8593 | 0.0013 | 3.4666 | 394610 |
| large_fixture | 1.1799 | 0.2482 | 2.4017 | 0.0118 | 8.1471 | 1089675 |

Fixture grande: 5 levels, 100 actores, 50 conversaciones, 20 quests, 100 eventos, 50 triggers, 30 objetos y 5 planos. 486 enlaces en esta revisión. Fuente YAML guardada en chronicles/large_fixture.

`research/phase6/viewport.json`: cargas reales GL y repintados síncronos del editor; no equivale a FPS constante ni mide GPU memory. Las repeticiones de cargas conservan ~1711 bytes Python adicionales tras GC; no demuestra ausencia completa de fugas de Qt/GPU.

Evidencia reproducible: phase6_performance.py y phase6_viewport.py. No se introdujo cache incremental de relaciones sin necesidad medida.

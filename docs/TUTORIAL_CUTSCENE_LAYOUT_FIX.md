# Revisión 0.9.6: cutscene y cambio de layout

Esta revisión corrige dos problemas observados durante la prueba del tutorial:

- el recorrido del caminante podía terminar en `PATH_FAILED` cuando el actor ya estaba colocado sobre el primer waypoint;
- el cambio al layout de combate no mostraba una confirmación clara cuando faltaba la flag o la llave.

## Confirmado en archivos originales y SDK

`research/phase7/embrace/cutscene.htm.txt` documenta `CodexCamera.SetupCutscene`, `SetShot`, los planos POV/OTS/profile y las distancias `EXTREMECLOSEUP`, `CLOSEUP`, `MEDIUM`, `FULL` y `LONG`. El bytecode de `MP_LeavesThree` conserva el patrón `BeginCutscene`/`EndCutscene`, `AIOff`/`AIOn` y la liberación de cámara al terminar una secuencia.

La API real de Codex declara `BeginCutscene(int,int)` y `EndCutscene(int,int)`. La generación propia los usa ahora alrededor de una timeline; no se ejecuta Embrace ni ninguna herramienta original.

## Cambio implementado

Una timeline propia hace lo siguiente:

1. entra en `BeginCutscene` y desactiva la AI global;
2. inicia el recorrido o el travelling original y aplica los planos de la timeline;
3. acepta como llegada válida que el actor ya esté dentro de la tolerancia del primer waypoint;
4. al terminar, detiene el recorrido, ejecuta `EndCutscene`, reactiva la AI y libera la cámara.

El editor muestra primeros planos adicionales: primerísimo primer plano, primer plano, sobre hombro cercano y perfil, para quien habla o escucha. Se basan en las constantes documentadas del SDK.

El tutorial añade una conversación de diagnóstico si se intenta abrir la salida sin haber aceptado la lección o sin la llave. Al entrar en `combat`, la guía aparece y abre automáticamente la conversación que confirma que se ha cambiado el layout sobre la misma geometría. La rata básica se mantiene como enemigo opcional.

## Inferido

`BeginCutscene` es el mecanismo nativo que debe conservar el control de la secuencia cuando el jugador mueve el ratón. La generación propia mantiene el final automático por duración de la timeline. La política de salto con una tecla se deja pendiente porque no se ha encontrado un callback de entrada documentado que permita inventar una API segura.

## Pendiente de verificar en Redemption

- que el cursor y el HUD permanezcan bloqueados durante los ocho segundos de `walk_scene` aunque se mueva el ratón;
- que el caminante avance desde el primer waypoint y que se vean los tres cambios de plano;
- que la confirmación de `combat` aparezca al completar las dos condiciones;
- que `EndCutscene` restaure controles y cámara sin dejar un estado intermedio;
- que el travelling original `EASTOttoVan` sea compatible con el level elegido.

La compilación contra la API original y los dobles Java pasan; eso no sustituye la prueba visual dentro de una partida nueva.

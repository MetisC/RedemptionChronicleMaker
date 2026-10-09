# Cámaras y secuencias básicas

+ Cámara crea un plano de actor: nombre, actor enfocado, duración, plano medio/cercano/amplio y ángulo bajo/medio/alto. Play Sequence genera SetupCutscene, ShotType y ShotAngle; un timer devuelve la cámara mediante Release. Empezar conversación o viajar libera un plano anterior. Los diálogos usan ángulo medio y se liberan al finalizar, también tras aborto.

El botón Enfocar actor en viewport es ayuda de ubicación. **No reproduce el encuadre nativo** ni se presenta como tal. No se genera una cámara con XYZ/FOV arbitrarios: no se ha confirmado una firma para ese contrato. Los paths de cámara tampoco están comprendidos; por ello esta fase no ofrece un timeline multi-shot ni editor de paths.

Se reutilizan las constantes originales CAMERA_SHOT_MS/CU/WS y CAMERA_ANGLE_LOW/MEDIUM/HIGH. No se supone el significado de los seis parámetros de SetShot ni se construye una llamada inventada. Compilan contra Codex real, incluyendo la cámara de la demo. Encuadre, bloqueo/liberación y tiempos percibidos permanecen pendientes de ensayo nativo.

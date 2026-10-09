"""SDK SetShot focuses target A (speaker) and C (listener); no guessed enums."""
PRESETS={'speaker_close':('Primer plano de quien habla','POV_A','CLOSEUP'),
         'listener_close':('Primer plano de quien escucha','POV_C','CLOSEUP'),
         'ots_speaker':('Sobre hombro hacia quien habla','OTS_C','MEDIUM'),
         'ots_listener':('Sobre hombro hacia quien escucha','OTS_A','MEDIUM'),
         'two_shot':('Dos personajes','ANGULAR_B','FULL'),
         'medium':('Plano medio','ANGULAR_C','MEDIUM'),
         'full':('Plano entero','ANGULAR_C','FULL')}
def shot_arguments(preset,angle='medium'):
    label,shot,distance=PRESETS[preset]
    return 'CAM_SHOT_'+shot+',CAM_ANGLE_'+angle.upper()+',CAM_DIST_'+distance

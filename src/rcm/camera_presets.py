"""SDK SetShot focuses target A (speaker) and C (listener); no guessed enums."""
DEFAULT_DIALOGUE_CAMERA = 'ots_speaker_close'
PRESETS={'speaker_extreme':('Primerísimo primer plano de quien habla','POV_A','EXTREMECLOSEUP'),
         'listener_extreme':('Primerísimo primer plano de quien escucha','POV_C','EXTREMECLOSEUP'),
         'speaker_close':('Primer plano de quien habla','POV_A','CLOSEUP'),
         'listener_close':('Primer plano de quien escucha','POV_C','CLOSEUP'),
         'ots_speaker_close':('Sobre hombro cercano hacia quien habla','OTS_C','CLOSEUP'),
         'ots_listener_close':('Sobre hombro cercano hacia quien escucha','OTS_A','CLOSEUP'),
         'ots_speaker':('Sobre hombro hacia quien habla','OTS_C','MEDIUM'),
         'ots_listener':('Sobre hombro hacia quien escucha','OTS_A','MEDIUM'),
         'profile_speaker':('Perfil de quien habla','PROFILE_A','CLOSEUP'),
         'profile_listener':('Perfil de quien escucha','PROFILE_C','CLOSEUP'),
         'two_shot':('Dos personajes','ANGULAR_B','FULL'),
         'medium':('Plano medio','ANGULAR_C','MEDIUM'),
         'full':('Plano entero','ANGULAR_C','FULL')}
CINEMA_PRESETS={**PRESETS,'aerial':('Vista aérea amplia en picado','ANGULAR_B','LONG')}

def shot_arguments(preset,angle='medium'):
    label,shot,distance=CINEMA_PRESETS[preset]
    if preset=='aerial':angle='high'
    return 'CAM_SHOT_'+shot+',CAM_ANGLE_'+angle.upper()+',CAM_DIST_'+distance

##############################################################################################
#
#  EFFECTS DEFINITIONS
#
##############################################################################################
#
#
#  Line Format:
#
#  name [icon | none] row [script | none] type subtype compose flags tick pc dc v1 v2 v3 v4 v5 v6
#
#
#  name                 name of the effect (single word, also used as localized stringId)
#  icon                 icon to use for screen display, or the keyword 'none'
#  row                  the row the icon has to be displayed on (0 = disciplines, 1 = others)
#  script               script to use for the visual/sound of the effect, or the keyword 'none'
#  type                 type of effect (see list)
#  subtype              subtype of effect inside each type (see list)
#  compose              how this effect is composed with others of same type and subtype (see list) 
#  flags                flags altering the behavior of the effect (see list)
#  tick                 tick rate for over time effects in milliseconds
#  pc                   permanent cost (how much to add to the cost of an object with this effect as permanent)
#  dc                   duration cost (how much to add to the cost of an object with this effect, per second of duration, per charge)
#  valN                 a preset value for the effect at level N
#
#
#  Effect Types:
#
#   0   NONE
#   1  *BSTI            base stat, instant
#   2  *BSTOT           base stat, over time
#   3  *STAT            modified stat
#   4  *BSOI            base soak, instant
#   5  *BSOOT           base soak, over time
#   6  *SOAK            modified soak
#   7  *DI              damage, instant
#   8  *DOT             damage, over time
#   9   HI              heal, instant
#  10   HOT             heal, over time
#  11   XOFFENSE        additional offense bonus, added to the offense formula                                          [hit if random(Adex + weaponAccuracy) + Axoffense > random(Ddex) + Dxdefense]
#  12   XDEFENSE        additional defense bonus added to the defense formula
#  13   XDAMAGE         additional damage bonus (same type as the damage being computed) added to the damage formula    [dam is random(Astr + weaponDamage) + Apotence + Axdamage - random(Dsoak [+ Dstamina]) [-Dfortitude] - Dxsoak]
#  14   XSOAK           additional soaking bonus (all damage types) added to the damage formula
#  15   POTENCE         potence (used in combat system, and certain checks)
#  16   FORTITUDE       fortitude (used in combat system)
#  17   MOVESPEED       multiplier for movement speed
#  18   ATTACKSPEED     multiplier for attack speed
#  19   HIDE            how well you are "hidden"
#  20   SENSE           how well you sense "hidden" things
#  21   STAKEPROT       a protection against staking
#  22   WANTED          wanted by the law!
#  23   MESMERIZED      mesmerized
#  24   FRENZY          frenzy (this is a system effect type, this is *NOT* meant to start frenzy)
#  25   AFRAID          afraid
#  26   DAZED           dazed
#  27   PET             becomes pet of someone else
#  28   POSSESSING      possessing someone else
#  29   MODELALPHA      changing the model's alpha
#  30   MODELSCALE      changing the model's scale
#  31   BLOODCOST       alters the cost in blood of using a discipline
#  32   MAJESTY         under the spell of 'majesty' (i.e. stands in place looking at the majestic thing)
#  33   IMMOBILIZE      immobilized
#  34   FEEDPROT        a protection against feeding
#  35   TEAMFRIENDLY    friendly to another team than his own (or more exactly, on top of his own)
#
#  n+1  USERMULT1       n = the last number above. You MUST use one of these to create your own MULTIPLICATIVE (compose = 6) user effect. 
#  n+2  USERMULT2       Use any other number for any other compose type, but MULTIPLICATIVE effects have a default of 1.0 instead of 0.0 
#  n+3  USERMULT3       and there is no higher level data structure for the effects to store that in (and a bit late to rework that :-))
#  n+4  USERMULT4
#  n+5  USERMULT5
#
#
#  Effect SubTypes:
#
#  The above Type marked with * have subtypes.
#
#  STAT
#
#   0   STRENGTH
#   1   DEXTERITY
#   2   STAMINA
#   3   PERCEPTION
#   4   INTELLIGENCE
#   5   WITS
#   6   BLOOD
#   7   HUMANITY
#   8   FRENZY
#   9   GENERATION
#  10   FAITH
#  11   CHARISMA
#  12   MANIPULATION
#  13   APPEARANCE
#  14   FRENZYRATING
#  15   BLOODRATING
#  16   BLOODPOOLSIZE
#  17   MANA
#  18   MANAPOOLSIZE
#
#  SOAK, DAMAGE, DOT
#
#   0   NORMAL
#   1   LETHAL
#   2   AGGRAVATED
#   3   ELECTRIC
#   4   FIRE
#   5   SUN
#   6   FAITH
#   7   COLD
#   8   POISON
#   9   DISEASE
#
#
#
#  Compose types:
#
#   0   NONE
#   1   FIRST
#   2   LAST
#   3   MIN
#   4   MAX
#   5   ADD
#   6   MUL
#   7   AVG
#
#   Note: only the compose of the FIRST effect of that type and subtype will be considered...
#
#
#
#  Effect Flags:
#  
#  0x1   no blink
#  0x2   keep (and display in rollover as) float value
#  0x4   effect negator (actually KILLS any effect of the same type/subtype with a lesser of equal value -- no instance is created, so this cannot have a script)
#  0x8   effect is NOT used in the rollover description (assuming a SPECIALDESCRIPTION has been set in the template)
#  0x10	 effect will be removed when its creator dies
#  0x20  display as a percentage in rollover (only valid when 0x2 is set too)
#  0x40	 this effect is synced only for the "owner" of the effect
#  0x80	 this effect is not synced to any clients
#  0x100 this effect is not saved
#  0x200 this effect is cancellable
#
#
##############################################################################################
#
#  08-14-99 YB Original definitions and coding
#  08-18-99 YB Added support for poison and disease
#  08-19-99 YB Added instant and over time effects
#  08-28-99 YB Added costs
#
##############################################################################################



# System effects (used directly by the game, do not remove them or some things won't work anymore)
# ---------------
#
#  name                         [icon | none]           row     [script | none]                 type   subtype  compose flags   tick    pc      dc      v0      v1      v2      v3      v4      v5

ef_increaseblood                none                    0       none                            1       6       5       0x40     0       0       0       10      25      40      55      70      100
ef_decreaseblood                none                    0       none                            1       6       5       0x40     0       0       0       -5      -10     -15     -20     -25     -30
ef_increasemana                 none                    0       none                            1       17      5       0x40     0       0       0       5       10      15      20      25      30
ef_decreasemana                 none                    0       none                            1       17      5       0x40     0       0       0       -5      -10     -15     -20     -25     -30

ef_increasebloodpoolsize        none                    0       none                            3       16      5       0x40     0       0       0       5       10      20      25      30      35      
ef_increasemanapoolsize         none                    0       none                            3       18      5       0x40     0       0       0       0       0       0       0       0       0       

ef_frenzy                       FXFrenzyIcon            1       none                            24      0       0       0x40     0       0       0       0       0       0       0       0       0
ef_increasefrenzy               none                    0       none                            1       8       5       0x40     0       0       0       1       2       3       4       5       6
ef_decreasefrenzy               none                    0       none                            2       8       5       0x40     2000    0       0       -2      -4      -6      -8      -10     -12
ef_decreasefrenzyfast           none                    0       none                            2       8       5       0x40     500     0       0       -2      -4      -6      -8      -10     -12
ef_increasemanaot               none                    0       none                            2       17      5       0x40     4000    0       0       1       2       3       4       5       6 
ef_increasebloodot              none                    0       none                            2       6       5       0x40     6000    0       0       1       1       1       1       1       1

ef_increasehumanity             none                    0       none                            1       7       5       0x40     0       0       0       5       10      15      20      25      30
ef_decreasehumanity             none                    0       none                            1       7       5       0x40     0       0       0       -5      -10     -15     -20     -25     -30

ef_lowergeneration              none                    0       none                            1       9       5       0x40     0       0       0       -1      0       0       0       0       0

ef_wanted                       none                    0       none                            22      0       6       0x80     0       0       0       1       2       3       4       5       6
ef_mesmerized                   none                    0       none                            23      0       6       0x0      0       0       0       1       2       3       4       5       6
ef_afraid                       none                    0       none                            25      0       0       0x40     0       0       0       1       2       3       4       5       6
ef_dazed                        none                    0       none                            26      0       0       0x0      0       0       0       1       2       3       4       5       6
ef_pet                          none                    0       none                            27      0       0       0x0      0       0       0       1       2       3       4       5       6
ef_majesty                      none                    0       none                            32      0       0       0x0      0       0       0       1       2       3       4       5       6

ef_restrain                     none                    0       none                            33      0       5       0x0      0       0       0       1       2       3       4       5       6 
ef_staked                       FXstakedIcon            1       none                            0       0       0       0x0      0       0       0       0       0       0       0       0       0 

ef_lowerdefense                 none                    0       none                            12      0       5       0x0      0       0       0       -5      -10     -15     -20     -25     -30

ef_speedcheat                   none                    0       none                            17      0       6       0x0      0       0       0       2.0     3.0     4.0     5.0     7.5     10.0

ef_stat_strength                none                    1       none                            3       0       5       0x40     0       50      1       5       10      15      20      25      30
ef_stat_dexterity               none                    1       none                            3       1       5       0x40     0       50      1       5       10      15      20      25      30
ef_stat_stamina                 none                    1       none                            3       2       5       0x40     0       50      1       5       10      15      20      25      30

ef_stat_perception              none                    1       none                            3       3       5       0x40     0       50      1       5       10      15      20      25      30
ef_stat_intelligence            none                    1       none                            3       4       5       0x40     0       50      1       5       10      15      20      25      30
ef_stat_wits                    none                    1       none                            3       5       5       0x40     0       50      1       5       10      15      20      25      30

ef_stat_charisma                none                    1       none                            3       11      5       0x40     0       50      1       5       10      15      20      25      30
ef_stat_manipulation            none                    1       none                            3       12      5       0x40     0       50      1       5       10      15      20      25      30
ef_stat_appearance              none                    1       none                            3       13      5       0x40     0       50      1       5       10      15      20      25      30

ef_stat_faith                   none                    1       none                            3       10      5       0x40     0       50      1       5       10      15      20      25      30
ef_stakeprotection              none                    0       none                            21      0       5       0x48     0       0       0       10      20      30      40      50      60 
ef_feedprotection               none                    0       none                            34      0       5       0x48     0       0       0       10      20      30      40      50      60 

	
# General effects
# ---------------
#
#  name                         [icon | none]           row     [script | none]                 type   subtype  compose flags   tick    pc      dc      v0      v1      v2      v3      v4      v5

ef_beheaded                     none                    0       none                            8       2       5       0x80     500     0       0       10      15      20      25      30      35

ef_dmg_sun                      FXSunIcon               1       none                             8      5       5       0x0      1000    0       0       1.0     1.0     0.80    0.50    0.10    1.0
ef_dmg_electric                 FXElecIcon              1       none                             8      3       5       0x0      250     0       0       1.0     1.0     0.80    0.50    0.10    1.0

ef_poison                       FXPoisonIcon            1       none                            8       8       5       0x40     2000    0       0       1       2       3       4       5       6 
ef_disease                      FXDiseaseIcon           1       none                            8       9       5       0x40     10000   0       0       1       2       3       4       5       6 

ef_curepoison                   none                    0       none                            8       8       0       0x44     0       0       0       1       2       3       4       5       6 
ef_curedisease                  none                    0       none                            8       9       0       0x44     0       0       0       1       2       3       4       5       6 

ef_soak_normal                  none                    1       none                            6       0       5       0x40     0       0       0       10      15      30      45      60      80
ef_soak_lethal                  none                    1       none                            6       1       5       0x40     0       0       0       10      15      30      45      60      80
ef_soak_aggravated              none                    1       none                            6       2       5       0x40     0       0       0       10      15      20      25      30      40
ef_soak_electric                none                    1       none                            6       3       5       0x40     0       0       0       3       5       10      20      30      40
ef_soak_fire                    none                    1       none                            6       4       5       0x40     0       0       0       3       5       10      20      30      40
ef_soak_sun                     none                    1       none                            6       5       5       0x40     0       0       0       3       5       10      20      30      40
ef_soak_faith                   none                    1       none                            6       6       5       0x40     0       0       0       3       5       10      20      30      40
ef_soak_cold                    none                    1       none                            6       7       5       0x40     0       0       0       3       5       10      20      30      40
ef_soak_poison                  none                    1       none                            6       8       5       0x40     0       0       0       3       5       10      20      30      40
ef_soak_disease                 none                    1       none                            6       9       5       0x40     0       0       0       3       5       10      20      30      40




# Effects of being damaged
# ------------------------
#
#  name                         [icon | none]           row     [script | none]                 type   subtype  compose flags   tick    pc      dc      v0      v1      v2      v3      v4      v5

ef_dmg_dexterity                none                    0       none                            3       1       5       0x40     0       0       0       0       0       -5      -10     -10     0
ef_dmg_strength                 none                    0       none                            3       0       5       0x40     0       0       0       0       0       0       -5      -10     0
ef_dmg_movespeed                none                    0       none                            17      0       6       0x40     0       0       0       1.0     1.0     0.8     0.60    0.40    0.10
ef_dmg_attackspeed              none                    0       none                            18      0       6       0x40     0       0       0       1.0     1.0     0.90    0.80    0.70    0.10


# Effects of being frenzied
# -------------------------

ef_frz_strength                 none                    0       none                            3       0       5       0x40     0       0       0       20       0      0       0       0       0
ef_frz_dexterity                none                    0       none                            3       1       5       0x40     0       0       0       -10      0      0       0       0       0


# Item effects
# ------------

ef_item_ainkurn1                none                    0       none                            2       6       5       0x0     500     0       0       1       2       3       4       5       6 
ef_item_ainkurn2                FXBloodIcon             1       EffectWeaponAinkurn             2       6       5       0x0     500     0       0       -1      -2      -3      -4      -5      -6
ef_item_argentbaton             none                    0       none                            7       2       5       0x0     0       0       0       1       2       3       4       5       6 
ef_item_gangreleye              eyesOfTheBeastIcon      0       none                            0       0       0       0x8     0       0       0       0       0       0       0       0       0
ef_item_femur                   none                    0       none                            7       2       5       0x0     0       0       0       1       2       3       4       5       6 
ef_item_handconrad              none                    0       none                            15      0       5       0x8     0       0       0       5       10      15      20      25      30
ef_item_heartshield             none                    0       none                            21      0       5       0x8     0       0       0       100     100     100     100     100     100
ef_item_sirefinger              none                    0       none                            3       14      5       0x8     0       0       0       -0.5    -0.5    -0.5    -0.5    -0.5    -0.5
ef_item_monocleclarity          none                    0       none                            20      0       5       0x8     0       0       0       1       2       3       4       5       6
ef_item_giantsblood             none                    0       none                            15      0       5       0x8     0       0       0       5       10      15      20      25      30
ef_item_blackgloves             ferrelClawsIcon         0       EffectItemBlackGloves           0       0       0       0x8     0       0       0       0       0       0       0       0       0

ef_item_disease                 none                    0       none                            8       9       5       0x8     10000   0       0       1       2       3       4       5       6 
ef_item_dread                   FXafraidIcon            1       none                            25      0       5       0x0     0       0       0       1       2       3       4       5       6
ef_item_frenzy                  FXrisingFrenzyIcon      1       none                            2       8       5       0x1     1000    0       0       4       5       6       7       8       10
ef_item_healthpotion            none                    0       none                            10      0       5       0x0     500     0       0       1       2       3       4       5       6 
ef_item_curepoisonpotion        none                    0       none                            8       8       0       0x4     0       0       0       1       2       3       4       5       6 
ef_item_curediseasepotion       none                    0       none                            8       9       0       0x4     0       0       0       1       2       3       4       5       6 
ef_item_taser                   none                    0       EffectWeaponTaser               0       0       0       0x0     0       0       0       0       0       0       0       0       0
ef_item_werewolfvitae           none                    0       none                            14      0       5       0x8     0       0       0       50      60      70      80      90      100
ef_item_attackspeed             none                    0       none                            18      0       6       0x0     0       0       0       1.0     1.1     1.2     1.3     1.4     1.5
ef_item_xoffense                none                    0       none                            11      0       5       0x0     0       0       0       5.0     10.0    15.0    20.0    25.0    30.0
ef_item_xdefense                none                    0       none                            12      0       5       0x0     0       0       0       5.0     10.0    15.0    20.0    25.0    30.0
ef_item_xdamage                 none                    0       none                            13      0       5       0x0     0       0       0       5.0     10.0    15.0    20.0    25.0    30.0
ef_item_xsoak                   none                    0       none                            14      0       5       0x0     0       0       0       5.0     10.0    15.0    20.0    25.0    30.0
ef_item_hide                    none                    0       none                            19      0       5       0x0     0       0       0       1       2       3       4       5       6
ef_item_hide2                   none                    0       none                            29      0       6       0x8     0       0       0       1       2       3       4       5       6
ef_item_discipline              none                    0       none                            31      0       6       0x22    0       0       0       0.90    0.80    0.70    0.60    0.50    0.40
ef_item_neckguard               none                    0       none                            34      0       5       0x8     0       0       0       100     100     100     100     100     100
ef_item_control                 none                    0       none                            3       14      5       0x8     0       0       0       -0.1    -0.2    -0.3    -0.4    -0.5    -0.6

ef_item_strength                none                    1       none                            3       0       5       0x8     0       50      1       5       10      15      20      25      50
ef_item_dexterity               none                    1       none                            3       1       5       0x8     0       50      1       5       10      15      20      25      50
ef_item_stamina                 none                    1       none                            3       2       5       0x8     0       50      1       5       10      15      20      25      50

ef_item_perception              none                    1       none                            3       3       5       0x8     0       50      1       5       10      15      20      25      50
ef_item_intelligence            none                    1       none                            3       4       5       0x8     0       50      1       5       10      15      20      25      50
ef_item_wits                    none                    1       none                            3       5       5       0x8     0       50      1       5       10      15      20      25      50

ef_item_charisma                none                    1       none                            3       11      5       0x8     0       50      1       5       10      15      20      25      50
ef_item_manipulation            none                    1       none                            3       12      5       0x8     0       50      1       5       10      15      20      25      50
ef_item_appearance              none                    1       none                            3       13      5       0x8     0       50      1       5       10      15      20      25      50

# Discipline effects
# ------------------
#
#  name                         [icon | none]           row     [script | none]                 type   subtype  compose flags   tick    pc      dc      v0      v1      v2      v3      v4      v5

ef_disc_bloodstrength           bloodStrengthIcon       0       EffectDiscBloodStrength         3       0       5       0x200   0       0       0       5       10      15      20      25      30
ef_disc_blooddexterity          bloodDexterityIcon      0       EffectDiscBloodDexterity        3       1       5       0x200   0       0       0       5       10      15      20      25      30
ef_disc_bloodstamina            bloodStaminaIcon        0       EffectDiscBloodStamina          3       2       5       0x200   0       0       0       5       10      15      20      25      30
ef_disc_potence                 potenceIcon             0       EffectDiscPotence               15      0       5       0x200   0       0       0       5       10      15      20      25      30
ef_disc_fortitude               fortitudeIcon           0       EffectDiscFortitude             16      0       5       0x200   0       0       0       5       10      15      20      20      25
ef_disc_celerity1               celerityIcon            0       EffectDiscCelerity              17      0       6       0x200   0       0       0       1.5     2.0     2.5     3.0     3.5     4.0
ef_disc_celerity2               none                    0       none                            18      0       6       0x0     0       0       0       1.1     1.2     1.3     1.4     1.5     1.6
ef_disc_mistform                mistFormIcon            0       EffectDiscMistForm              19      0       5       0x200   0       0       0       2       2       2       2       3       4
ef_disc_mistform2               none                    0       none                            6       4       5       0x100   0       0       0       5       10      15      20      25      30
ef_disc_mistform3               none                    0       none                            6       5       5       0x100   0       0       0       5       10      15      20      25      30
ef_disc_hsenses                 heightenedSensesIcon    0       EffectDiscHeightenedSenses      20      0       5       0x200   0       0       0       1       2       3       4       5       6
ef_disc_command                 FXPossessedIcon         1       EffectDiscCommand               28      0       5       0x10    0       0       0       1       2       3       4       5       6
ef_disc_mesmerize               FXmesmerizeIcon         1       EffectDiscMesmerize             23      0       5       0x110   0       0       0       1       2       3       4       5       6
ef_disc_possession              FXPossessedIcon         1       EffectDiscPossession            28      0       5       0x10    0       0       0       1       2       3       4       5       6
ef_disc_quellbeast              none                    0       EffectDiscQuellBeast            2       8       5       0x0     500     0       0       -4      -8      -12     -16     -20     -24
ef_disc_bloodhealing            none                    0       EffectDiscBloodHealing          9       0       5       0x0     0       0       0       20      30      40      60      80      100
ef_disc_dreadgaze               FXafraidIcon            1       EffectDiscDreadGaze             25      0       5       0x110   0       0       0       1       2       3       4       5       6
ef_disc_thehaunting             FXafraidIcon            1       EffectDiscTheHaunting           25      0       5       0x110   0       0       0       1       2       3       4       5       6
ef_disc_voiceofmadness          FXafraidIcon            1       EffectDiscVoiceOfMadness        25      0       5       0x110   0       0       0       5       10      15      20      25      30
ef_disc_voiceofmadness2         none                    0       none                            2       8       5       0x10    1000    0       0       2       2       3       3       4       4 
ef_disc_drawingoutbeast         FXrisingFrenzyIcon      1       EffectDiscDrawingOutBeast       2       8       5       0x0     500     0       0       +4      +8      +12     +16     +20     +24
ef_disc_passion                 FXrisingFrenzyIcon      1       EffectDiscPassion               2       8       5       0x0     500     0       0       +2      +4      +6      +8      +10     +12
ef_disc_passion2                none                    0       none                            3       5       5       0x0     0       0       0       -3      -6      -9      -12     -15     -18
ef_disc_theforgetfulmind        FXDazedIcon             1       EffectDiscTheForgetfulMind      26      0       5       0x0     0       0       0       0       0       0       0       0       0 
ef_disc_beckoning               FXSummonedIcon          1       EffectDiscBeckoning             27      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_feralwhispers           FXSummonedIcon          1       EffectDiscFeralWhispers         27      0       0       0x110   0       0       0       1       2       3       4       5       6
ef_disc_cloakofshadows          cloakOfShadowsDIcon     0       EffectDiscCloakOfShadows        19      0       5       0x200   0       0       0       1       2       3       4       5       6
ef_disc_cloakofshadows2         none                    0       none                            29      0       6       0x0     0       0       0       1       2       3       4       5       6
ef_disc_cloakthegathering       cloakTheGatheringIcon   0       EffectDiscCloakTheGathering     19      0       5       0x210   0       0       0       1       2       3       4       5       6
ef_disc_cloakthegathering2      none                    0       none                            29      0       6       0x10    0       0       0       1       2       3       4       5       6
ef_disc_invisibility            InvisibilityIcon        0       EffectDiscInvisibility          19      0       5       0x200   0       0       0       1       2       3       4       5       6
ef_disc_invisibility2           none                    0       none                            29      0       6       0x0     0       0       0       1       2       3       4       5       6
ef_disc_prayer                  FXFaithIcon             1       EffectDiscPrayer                8       6       5       0x0     500     0       0       2       4       6       8       10      12
ef_disc_awe                     FXmesmerizeIcon         1       EffectDiscAwe                   23      0       5       0x10    0       0       0       1       2       3       4       5       6
ef_disc_ignoreflame             ignoreTheSearingFlameIcon 0     EffectDiscIgnoreFlame           6       4       5       0x0     0       0       0       20      35      50      65      80      95
ef_disc_summonelemental         FXSummonedIcon          1       EffectDiscSummonElemental       27      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_darkhunter              FXSummonedIcon          1       EffectDiscDarkHunter            27      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_hatchtheviper           FXSummonedIcon          1       EffectDiscHatchTheViper         27      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_subsumethespirit        FXPossessedIcon         1       EffectDiscSubsumeTheSpirit      28      0       5       0x110   0       0       0       1       2       3       4       5       6
ef_disc_entrancement            FXPossessedIcon         1       EffectDiscEntrancement          28      0       5       0x10    0       0       0       1       2       3       4       5       6
ef_disc_eyesoftheserpent        FXmesmerizeIcon         1       EffectDiscEyesOfTheSerpent      23      0       5       0x10    0       0       0       1       2       3       4       5       6
ef_disc_skinoftheadder          skinOfTheAdderIcon      0       EffectDiscSkinOfTheAdder        16      0       5       0x200   0       0       0       4       8       12      18      18      24
ef_disc_skinoftheadder2         none                    0       none                            3       13      5       0x0     0       0       0       -25     -25     -25     -25     -25     -25
ef_disc_heartofstone            heartOfStoneIcon        0       EffectDiscHeartOfStone          21      0       5       0x0     0       0       0       20      35      50      65      80      95
ef_disc_theftofvitae1           theftOfVitaeIcon        0       none                            2       6       5       0x0     500     0       0       10      20      30      40      50      60 
ef_disc_theftofvitae2           FXBloodIcon             1       EffectDiscTheftOfVitae          2       6       5       0x0     500     0       0       -10     -20     -30     -40     -50     -60 
ef_disc_blackdeath              FXDiseaseIcon           1       EffectDiscBlackDeath            8       9       5       0x0     500     0       0       6       7       8       9       10      12
ef_disc_bloodrage1              FXrisingFrenzyIcon      1       EffectDiscBloodRage             2       8       5       0x0     500     0       0       2       4       6       8       10      12  
ef_disc_bloodrage2              none                    0       none                            2       6       5       0x0     500     0       0       -2      -4      -6      -8      -10     -12 
ef_disc_cauldronofblood1        none                    0       EffectDiscCauldronOfBlood       8       4       5       0x0     500     0       0       6       8       12      18      26      36 
ef_disc_cauldronofblood2        FXBloodIcon             1       none                            2       6       5       0x0     500     0       0       -2      -4      -6      -8      -10     -12 
ef_disc_decay                   FXDeathIcon             1       EffectDiscDecay                 8       2       5       0x0     500     0       0       3       4       5       6       9       10
ef_disc_acidictouch             FXDeathIcon             1       EffectDiscAcidicTouch           8       2       5       0x0     500     0       0       3       6       9       12      15      18
ef_disc_turntodust              FXDeathIcon             1       EffectDiscTurnToDust            8       2       5       0x0     500     0       0       15      20      25      30      35      40
ef_disc_summonsoul              FXSummonedIcon          1       EffectDiscSummonSoul            27      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_calllightning           FXElecIcon              1       EffectDiscCallLightning         7       3       5       0x0     0       0       0       15      30      45      60      75      90
ef_disc_prisonofice1            FXColdIcon              1       EffectDiscPrisonOfIce           8       7       5       0x0     1000    0       0       1       1       2       3       4       5
ef_disc_prisonofice2            none                    0       none                            33      0       5       0x0     0       0       0       1       2       3       4       5       6 
ef_disc_shapeofthebeast         shapeOfTheBeastIcon     0       EffectDiscShapeOfTheBeast       20      0       5       0x200   0       0       0       0       1       1       2       2       3 
ef_disc_shapeofthebeast2        none                    0       none                            10      0       5       0x0     2000    0       0       1       2       2       3       3       4
ef_disc_shapeofthebeast3        none                    0       none                            17      0       6       0x0     0       0       0       1.2     1.4     1.6     1.8     2.0     2.5
ef_disc_eyesofthebeast          eyesOfTheBeastIcon      0       EffectDiscEyesOfTheBeast        0       0       0       0x200   0       0       0       0       0       0       0       0       0
ef_disc_truesight               trueSightIcon           0       EffectDiscTrueSight             20      0       5       0x200   0       0       0       1       2       3       4       5       6
ef_disc_bloodofpotency          bloodOfPotencyIcon      0       EffectDiscBloodOfPotency        31      0       6       0x200   0       0       0       0.90    0.80    0.70    0.60    0.50    0.40
ef_disc_bloodofpotency2         none                    0       none                            3       9       5       0x0     0       0       0       0       -1      -1      -2      -2      -3   
ef_disc_atrophy                 FXDeathIcon             1       EffectDiscAtrophy               3       0       5       0x0     0       0       0       -5      -10     -15     -20     -25     -30
ef_disc_atrophy2                none                    0       none                            3       1       5       0x0     0       0       0       -5      -10     -15     -20     -25     -30
ef_disc_atrophy3                none                    0       none                            7       2       5       0x0     0       0       0       20      30      40      50      60      70
ef_disc_shamblinghordes         FXSummonedIcon          1       EffectDiscShamblingHordes       27      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_vigormortis             FXPossessedIcon         1       EffectDiscVigorMortis           28      0       5       0x10    0       0       0       1       2       3       4       5       6
ef_disc_psychicprojection       FXPossessedIcon         1       EffectDiscPsychicProjection     28      0       5       0x110   0       0       0       1       2       3       4       5       6
ef_disc_majesty                 majestyIcon             0       EffectDiscMajesty               0       0       0       0x100   0       0       0       1       2       3       4       5       6
ef_disc_majesty2                FXMesmerizeIcon         1       none                            32      0       0       0x10    0       0       0       1       2       3       4       5       6
ef_disc_earthmeld               earthMeldIcon           0       EffectDiscEarthMeld             10      0       5       0x200   2000    0       0       1       2       3       4       5       6 
ef_disc_earthmeld2              none                    0       none                            2       8       5       0x100   2000    0       0       -1      -1      -2      -2      -3      -3
ef_disc_earthmeld3              none                    0       none                            6       5       5       0x100   2000    0       0       1000    1000    1000    1000    1000    1000
ef_disc_mask1000faces           mask1000facesIcon       0       EffectDiscMask1000Faces         35      0       5       0x200   0       0       0       0       0       0       0       0       0
ef_disc_tongueoftheasp1         tongueOfTheAspIcon      0       none                            2       6       5       0x0     500     0       0       3       5       8       12      18      22 
ef_disc_tongueoftheasp2         FXBloodIcon             1       EffectDiscTongueOfTheAsp        2       6       5       0x0     500     0       0       -3      -5      -8      -12     -18     -22 
ef_disc_quellbeast2             FXDazedIcon             1       EffectDiscQuellBeast            26      0       5       0x0     0       0       0       0       0       0       0       0       0

ef_disc_torch                   torchIcon               0       EffectDiscTorch                 0       0       0       0x300   0       0       0       0       0       0       0       0       0
ef_disc_spiritstouch            none                    0       EffectDiscSpiritsTouch          0       0       0       0x0     0       0       0       0       0       0       0       0       0
ef_disc_feralclaws              ferrelClawsIcon         0       EffectDiscFeralClaws            0       0       0       0x200   0       0       0       0       0       0       0       0       0
ef_disc_auraperception          none                    0       EffectDiscAuraPerception        0       0       0       0x0     0       0       0       0       0       0       0       0       0
ef_disc_eyesofchaos             none                    0       EffectDiscEyesOfChaos           0       0       0       0x300   0       0       0       0       0       0       0       0       0
ef_disc_truefaith               trueFaithIcon           0       EffectDiscTrueFaith             0       0       0       0x200   0       0       0       0       0       0       0       0       0
ef_disc_immolate                none                    0       EffectDiscImmolate              7       4       5       0x0     0       0       0       15      30      45      60      75      90
ef_disc_heal                    none                    0       EffectDiscHeal                  9       0       5       0x0     0       0       0       10      20      35      50      75      100
ef_disc_nuke                    none                    0       none                            7       0       5       0x0     0       0       0       1000    1000    1000    1000    1000    1000

#  name                         [icon | none]           row     [script | none]                 type   subtype  compose flags   tick    pc      dc      v0      v1      v2      v3      v4      v5







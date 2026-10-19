"""Optional fresh-enemy modifiers, using proven native actor APIs only.

Normal emits no code. Persistence remains the engine's actor state plus the
existing RCM GUID/createdOnce records; there is no second scaling lifecycle.
"""

MODIFIERS={
    'easy':(0.8,0.9,0.9),
    'normal':(1.0,1.0,1.0),
    'hard':(1.2,1.1,1.1),
    'nightmare':(1.5,1.2,1.2),
}


def selected(source):
    value=source.get('chronicle',{}).get('difficulty','normal')
    if not isinstance(value,str) or value not in MODIFIERS:raise ValueError('chronicle.difficulty: easy, normal, hard, nightmare')
    return value


def active(source):return selected(source)!='normal'


def manual_call(source,actor,index):
    if active(source) and actor.get('behavior','npc')=='enemy':return f' if(fresh) difficultyEnemy(things[{index}]);'
    return ''


def extend(java,source):
    mode=selected(source)
    if mode=='normal':return java
    health,strength,stamina=MODIFIERS[mode]
    methods=f'''
 private float difficultyValue(float value,float multiplier) {{ float result=value*multiplier; return value>0.0f && !Float.isNaN(result) && !Float.isInfinite(result)?result:value; }}
 private void difficultyStat(CodexActor actor,int stat,float factor) {{ float base=actor.GetActorBaseStat(stat),current=actor.GetActorStat(stat); if(Float.isNaN(base)||Float.isInfinite(base)||Float.isNaN(current)||Float.isInfinite(current)||base<0.0f||current<0.0f) return; actor.SetActorBaseStat(stat,difficultyValue(base,factor)); actor.SetActorStat(stat,difficultyValue(current,factor)); }}
 private void difficultyEnemy(int who) {{
  if(NetIsClient()||IsPlayerGuid(who)||!IsActorGuid(who)||!local(who)) return;
  CodexActor actor=new CodexActor(who); int team=actor.GetActorTeam();
  if(team<TEAM_ENEMY_FIRST||team>TEAM_ENEMY_LAST||(actor.GetActorFlags()&THING_AF_NEUTRAL)!=0) return;
  float hp=actor.GetActorHealth(),maximum=actor.GetActorMaxHealth();
  if(hp<=0.0f||maximum<=0.0f||Float.isNaN(hp)||Float.isInfinite(hp)||Float.isNaN(maximum)||Float.isInfinite(maximum)) return;
  difficultyStat(actor,ACTOR_STAT_STRENGTH,{strength}f);
  difficultyStat(actor,ACTOR_STAT_STAMINA,{stamina}f);
  actor.SetActorMaxHealth(difficultyValue(maximum,{health}f));
  actor.SetActorHealth(Math.min(difficultyValue(hp,{health}f),actor.GetActorMaxHealth()));
 }}
'''
    if not java.endswith('}\n'):raise ValueError('Difficulty runtime integration missing')
    return java[:-2]+methods+'}\n'

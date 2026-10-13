"""Reproducible 1.0 examples, using the same entities produced by GUI recipes."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.recipes import apply


def scene(ident,level='EastLondon',position=(-62,-768,384)):
    return dict(id=ident,level=dict(source=level,environment_scene='EAST_28_1.nsd' if level=='EastLondon' else None),actors=[],objects=[],conversations=[],events=[],triggers=[],sequences=[],encounters=[],paths=[],waypoints=[],entries=[dict(id='start',name='Entrada del jugador',transform=dict(position=list(position),orientation=[0,0,180]))],default_entry='start')


def tutorial():
    root=dict(schema=2,project_format=9,chronicle=dict(id='rcm_tutor',name='RCM · Una carta al amanecer',description='Tutorial 1.0: conversación, objetivo, trigger condicionado, película sobre el jugador, carta, journal, rata y llegada.'),entry='square',state={'flags':{}},scenes=[scene('square'),scene('home')],quests=[],resources={},metadata={'version':'1.0.0'},build_options={'debug':True})
    # Keep previously shipped template definitions available at startup. Crypt
    # profiles can still own T_tutor_key even when the new story does not use it.
    import yaml
    previous=ROOT/'tests/fixtures/chronicles/tutorial_0913/project.yaml'
    if previous.exists():root['resources']=yaml.safe_load(previous.read_text(encoding='utf8')).get('resources',{})
    if previous.exists():
        legacy=yaml.safe_load(previous.read_text(encoding='utf8'));backend=Backend(Workspace(ROOT));backend.sync_resources(legacy)
        templates={t['id']:t for t in backend.resources['templates']}
        for i,s in enumerate(legacy['scenes']):
            for obj in s.get('objects',[]):
                if templates.get(obj['template'],{}).get('kind') in {'items','weapons','armour'}:
                    root['resources'].setdefault('templates',[]).append(dict(id='R_rcm_tutor_s'+str(i)+'_'+obj['id'],base=obj['template'],properties={}))
    root,rid=apply(root,'go_to_place','square',dict(name='01 · Anezka: el encargo',template='Anezka',position=[-176,-612,384],text='Necesito que lleves una carta a Elena. ¿Ves el barril en la zona ancha de la calle, cerca de donde has aparecido? Está solo, separado de las paredes. Acércate al barril: allí te mostraré la carta. No tienes que pulsarlo; basta con caminar hasta él. Tu diario te recordará qué hacer.',accept='Acepto el encargo. Voy al barril.',decline='Ahora no.'))
    recipe=root['authoring']['recipes'][0];refs=recipe['refs'];s=root['scenes'][0]
    old=refs['flag']['id'];old_done=refs['done_flag']['id']
    from rcm.campaign_document import CampaignDocument
    doc=CampaignDocument(Workspace(ROOT),root);doc.rename_flag(old,'go_to_square');doc.rename_flag(old_done,'square_reached')
    marker_position=[-320,-850,384]
    area=next(t for t in s['triggers'] if t['id']==refs['trigger']['id']);area['name']='02 · Acércate al barril: trigger condicionado';area['transform']['position']=list(marker_position);area['radius']=110
    film=next(q for q in s['sequences'] if q['id']==refs['sequence']['id']);film['name']='03 · Llegada del jugador: amplio a cercano'
    # Visible marker; it is a prop, not original geometry.
    s['objects'].append(dict(id='marker',name='Barril: acércate aquí',template='barrel1',transform=dict(placement='absolute',position=list(marker_position),orientation=[0,0,0])))
    s['events'].append(dict(id='marker_spawn',when='scene_start',actions=[{'spawn':'marker'}]))
    root,qrid=apply(root,'quest','square',dict(title='Una carta al amanecer',text='Anezka necesita que lleves una carta a Elena. Habla con ella y acércate al barril que está solo en la zona ancha de la calle, cerca del punto de inicio.',quest_steps=['Acepta el encargo de Anezka. Después camina hasta el barril, cerca de donde has aparecido: no hace falta pulsarlo.','Recoge el libro que aparece al lado del barril: es la carta para Elena. No tienes que usarlo en el inventario. Despeja la calle de la rata, o pide ayuda a Tomás.','Habla con Anezka y elige «Llévame a Elena». Allí habla con Elena y entrégale la carta.'],reward_xp=20))
    qref=next(r for r in root['authoring']['recipes'] if r['id']==qrid)['refs']['quest']['id'];s=root['scenes'][0]
    ended=next(e for e in s['events'] if e['id']==refs['end_event']['id']);ended['actions'] += [{'advance_quest':qref}]
    root,prid=apply(root,'pickup','square',dict(name='Carta para Elena',template='ledger',position=[-240,-950,384]))
    pref=next(r for r in root['authoring']['recipes'] if r['id']==prid)['refs'];s=root['scenes'][0]
    spawn=next(e for e in s['events'] if e['id']==pref['spawn_event']['id']);spawn.update(when='state_changed',conditions=[dict(flag='square_reached',is_set=True)],once=True)
    next(e for e in s['events'] if e['id']==pref['event']['id'])['conditions']=[dict(flag='square_reached',is_set=True)]
    root,erid=apply(root,'encounter','square',dict(name='05 · Una rata de las minas',template='Rat',position=[-62,-1000,384],reward_xp=5))
    eref=next(r for r in root['authoring']['recipes'] if r['id']==erid)['refs'];s=root['scenes'][0]
    enemy_spawn=next(e for e in s['events'] if e['id']==eref['spawn_event']['id']);enemy_spawn.update(when='item_picked_up',item=pref['object']['id'],once=True)
    complete=next(e for e in s['events'] if e['id']==eref['event']['id']);complete['actions'] += [{'advance_quest':qref}]
    root,trid=apply(root,'travel','square',dict(trigger_position=[-176,-612,384],radius=75,destination='home',arrival_position=[-62,-768,384],once=False))
    tref=next(r for r in root['authoring']['recipes'] if r['id']==trid)['refs'];s=root['scenes'][0]
    travel=next(e for e in s['events'] if e['id']==tref['event']['id']);travel['conditions']=[dict(flag=eref['flag']['id'],is_set=True),dict(flag='delivery_done',is_set=False)]
    area=next(t for t in s['triggers'] if t['id']==tref['trigger']['id']);area['name']='06 · Vuelve a Anezka: viaje a Elena';area['once']=False
    s['events'].append(dict(id='road_clear',when='encounter_complete',encounter=eref['encounter']['id'],once=True,actions=[{'show_note':dict(title='La calle está libre',text='Bien hecho. Ya puedes entregar la carta: no hace falta usar el libro en el inventario. Habla con Anezka, donde comenzó el encargo, y elige «Llévame a Elena».')}]))
    # The opt-out is a separate, understandable teacher at the next objective.
    root,skipid=apply(root,'talk','square',dict(name='Tomás: ayuda y omitir combate',template='LonCiv1',position=[-176,-1080,384],text='Recoge el libro de la calle: representa la carta. Después aparecerá una sola rata. Mátala y vuelve a Anezka. Si prefieres seguir sin combatir, puedo despejar el camino por ti.',accept='Prefiero omitir el combate.',decline='Lo intentaré yo.'))
    skipref=next(r for r in root['authoring']['recipes'] if r['id']==skipid)['refs'];s=root['scenes'][0]
    next(e for e in s['events'] if e['id']==skipref['spawn_event']['id']).update(when='state_changed',conditions=[dict(flag='square_reached',is_set=True)],once=True)
    s['events'].append(dict(id='skip_combat',when='conversation_ended',conversation=skipref['conversation']['id'],result=1,once=True,conditions=[dict(flag=eref['flag']['id'],is_set=False)],actions=[{'give_item':pref['object']['id']},{'remove_encounter':eref['encounter']['id']},{'set_flag':eref['flag']['id']},{'advance_quest':qref}]))
    # Pickup and clearing advance the same journal step once. No combat reward
    # is granted for skipping, and the enemy spawn is gated by completion.
    next(e for e in root['scenes'][0]['events'] if e['id']==eref['spawn_event']['id'])['conditions']=[dict(flag='square_reached',is_set=True),dict(flag=eref['flag']['id'],is_set=False)]
    root,finalid=apply(root,'talk','home',dict(name='07 · Elena: entrega',template='LonCiv2',position=[-176,-612,384],text='Gracias por traerla. Anezka me avisó de tu llegada. Abre tu diario: el encargo terminará cuando me entregues la carta. Después puedes guardar y volver a cargar para comprobar que no recibes el premio dos veces.',accept='Aquí está la carta.',decline='Un momento.'))
    finalref=next(r for r in root['authoring']['recipes'] if r['id']==finalid)['refs'];h=root['scenes'][1]
    h['events'].append(dict(id='delivery',when='conversation_ended',conversation=finalref['conversation']['id'],result=1,once=True,conditions=[{'owns_item':'square.'+pref['object']['id']}],actions=[{'take_item':'square.'+pref['object']['id']},{'advance_quest':qref},{'complete_quest':qref}]))
    # Optional return after delivery makes native reentry acceptance reachable.
    free=next(i for i in range(256) if i not in root['state']['flags'].values())
    root['state']['flags']['delivery_done']=free
    h['events'][-1]['actions'].append({'set_flag':'delivery_done'})
    # Talking stops the player's approach outside the old 75-unit travel area.
    # The existing conditional binding selects the journey after the encounter.
    # These are normal editable conversations and events, including the recipe.
    s=root['scenes'][0];mentor=next(a for a in s['actors'] if a['id']==refs['actor']['id'])
    mentor['conversation'].update(when_flag=eref['flag']['id'],then='to_elena')
    s['conversations'].append(dict(id='to_elena',speaker=mentor['id'],prompt='El camino ya está libre. La carta se entrega hablando con Elena; no hace falta usar el libro en el inventario. Puedo llevarte hasta ella. Si ya se la has entregado, puedes visitarla otra vez.',choices=[dict(text='Llévame a Elena.',result=1),dict(text='Todavía no.',result=2)],camera='ots_speaker_close'))
    s['events'].append(dict(id='talk_travel',when='conversation_ended',conversation='to_elena',result=1,once=False,conditions=[dict(flag=eref['flag']['id'],is_set=True)],actions=[{'travel':dict(scene='home',entry=tref['entry']['id'])}]))
    h=root['scenes'][1]
    next(a for a in h['actors'] if a['id']==finalref['actor']['id'])['conversation'].update(when_flag='delivery_done',then='delivered')
    h['conversations'].append(dict(id='delivered',speaker=finalref['actor']['id'],prompt='Gracias otra vez. Ya tengo la carta y el encargo está terminado. Puedes guardar y explorar, o volver al barril para regresar a la calle de Anezka. Tu diario conservará la entrega.',choices=[dict(text='Hasta pronto.',result=1)],camera='ots_speaker_close'))
    h['objects'].append(dict(id='marker',name='Barril: regreso a Anezka',template='barrel1',transform=dict(placement='absolute',position=list(marker_position),orientation=[0,0,0])))
    h['events'].append(dict(id='marker_spawn',when='scene_start',actions=[{'spawn':'marker'}]))
    root,_=apply(root,'travel','home',dict(trigger_position=list(marker_position),radius=110,destination='square',arrival_position=[-62,-768,384],once=False))
    root['scenes'][1]['events'][-1]['conditions']=[dict(flag='delivery_done',is_set=True)]
    root['scenes'][1]['triggers'][-1]['name']='08 · Volver a la calle de Anezka'
    root['scenes'][1]['conversations'][0]['prompt']+=' Cuando termines, vuelve al lugar del barril para regresar a la calle de Anezka. El diario conservará lo que has hecho.'
    s=root['scenes'][0]
    # Crypt retains inventory between new MP games. Remove only this tutorial's
    # old mission letter at first arrival, never other belongings or on restore.
    s['events'].append(dict(id='welcome',when='scene_start',once=True,actions=[{'take_item':pref['object']['id']},{'show_note':dict(title='Una carta al amanecer',text='Empiezas en una calle de Londres. Anezka está justo delante, a pocos pasos. Habla con ella para recibir el encargo.\n\nPuedes moverte, abrir el diario y guardar como en cualquier crónica. Sigue una instrucción cada vez. En el editor, Tutorial / Ayuda te lleva a los mismos elementos y abre sus asistentes.')}]))
    return root


def main():
    ws=Workspace(ROOT);archive=ws.output('tests/fixtures/chronicles/tutorial_0913')
    if not archive.exists():raise ValueError('Missing tutorial regression fixture')
    root=tutorial();backend=Backend(ws);v=backend.validate(root)
    if not v.valid:raise ValueError([p.message for p in v.problems if p.severity=='ERROR'])
    ws.write('chronicles/tutorial/project.yaml',source_text(root))
    # Add the player arrival circuit to the existing real mini adventure.
    import yaml
    mini=yaml.safe_load(ws.output('chronicles/mini_chronicle/project.yaml').read_text(encoding='utf8'))
    if not mini.get('authoring'):
        mini,rid=apply(mini,'trigger_cinematic','quay',dict(trigger_position=[-342,-950,384],radius=90,once=True,duration=6,reference='victoria'))
        seq=mini['scenes'][0]['sequences'][-1];seq['name']='Llegada al muelle'
        v=backend.validate(mini)
        if not v.valid:raise ValueError([p.message for p in v.problems if p.severity=='ERROR'])
        ws.write('chronicles/mini_chronicle/project.yaml',source_text(mini))
    print('Tutorial and mini validated; runtime observation pending.')


if __name__=='__main__':main()

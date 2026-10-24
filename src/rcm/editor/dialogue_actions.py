"""Direct response effects and boolean flag reactions using normal actions."""
import copy
from .i18n import tr


def behavior_action(actor, behavior='enemy'):
    return {'actor_behavior': dict(actor=actor, behavior=behavior,
                                   team=12 if behavior=='enemy' else 10,
                                   paused=behavior=='npc')}


def response_controls(ins, conversation, answer, path):
    win=ins.win
    if not hasattr(win.doc,'campaign') or win.doc.campaign.get('project_format') not in (9,10):return
    if 'goto' in answer:
        ins.note(tr('Para ejecutar acciones al terminar, usa una respuesta RETURN. Si continúas a otro nodo, puedes añadir acciones al comenzar su primera línea.'))
        return
    from . import director
    actions=answer.get('actions',[])
    if actions:ins.note(tr('Al elegir esta respuesta: ')+director.action_summary(actions))
    def apply(values):
        win.history_time=0
        ins.set(path+('actions',),values or None,True)
        win.inspect()
    ins.button(tr('Acciones al elegir esta respuesta…'),lambda:director.edit_actions(win,answer.get('actions',[]),apply,title=tr('Acciones al elegir esta respuesta…')),'answer_actions')
    def hostile():
        if not win.commit_properties():return
        action=behavior_action(conversation['speaker'])
        if action in answer.get('actions',[]):return
        answer.setdefault('actions',[]).append(action)
        win.history_time=0;win.changed(True)
    ins.button(tr('Volver hostil al interlocutor'),hostile,'answer_make_hostile')
    ins.note(tr('Estas acciones se ejecutan al cerrar la conversación con esta respuesta, después del cambio de flag. Una conversación cancelada no las ejecuta.'))


def edit_flag_reaction(win, alias, is_set):
    if not win.commit_properties():return
    flags=win.doc.data.get('state',{}).get('flags',{})
    if alias not in flags:
        path=win.selection
        if len(path)==3 and path[:2]==('state','flags') and path[2] in flags:alias=path[2]
        else:return
    events=win.doc.data['events']
    matches=[e for e in events if e['when']=='flag_changed' and e.get('flag')==alias and e.get('is_set')==is_set]
    existing=matches[0] if matches else None
    if len(matches)>1:
        from PySide6.QtWidgets import QInputDialog
        selected,ok=QInputDialog.getItem(win,tr('Reacción al flag'),tr('Evento'),[e['id'] for e in matches],0,False)
        if not ok:return
        existing=next(e for e in matches if e['id']==selected)
    from .director import edit_actions
    initial=copy.deepcopy(existing['actions']) if existing else []
    def apply(actions):
        if actions==initial:return
        if not actions:
            if existing is not None:
                from ..campaign_relations import graph
                target=('scenes',win.doc.active,'events',events.index(existing))
                if any(link.target==target for link in graph(win.doc.snapshot())):
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(win,tr('Reacción al flag'),tr('Otros elementos utilizan este evento. Usa «Ver evento» y Eliminar para revisar y retirar sus referencias.'));return
                events.remove(existing)
            else:return
        elif existing is not None:existing['actions']=actions
        else:
            stem='on_'+alias+('_set' if is_set else '_clear')
            events.append(dict(id=win.doc.unique_id('events',stem),when='flag_changed',flag=alias,is_set=is_set,once=False,actions=actions))
        win.history_time=0;win.changed(True)
    edit_actions(win,initial,apply,title=tr('Reacción al flag')+' · '+alias+' · '+tr('Activado' if is_set else 'Desactivado'))


def flag_controls(ins, alias):
    win=ins.win
    if not hasattr(win.doc,'campaign') or win.doc.campaign.get('project_format') not in (9,10):return
    ins.note(tr('El índice identifica dónde se guarda el flag; no es su valor. Durante la partida el flag está activado o desactivado. Estas reacciones se ejecutan cuando cambia, no por su estado inicial, y pertenecen a la escena activa.'))
    ins.button(tr('Acciones cuando se active…'),lambda:edit_flag_reaction(win,alias,True),'flag_on_actions')
    ins.button(tr('Acciones cuando se desactive…'),lambda:edit_flag_reaction(win,alias,False),'flag_off_actions')
    def view():
        if not win.commit_properties():return
        current=alias if alias in win.doc.data['state']['flags'] else win.selection[-1]
        from .linked_events import Reaction,open_event
        open_event(win,Reaction('flag',tr('Reacción al flag'),'flag_changed',dict(flag=current)))
    ins.button(tr('Ver eventos del flag…'),view,'flag_view_events').setEnabled(any(e['when']=='flag_changed' and e.get('flag')==alias for e in win.doc.data['events']))
    from .director import action_summary
    for state in (True,False):
        actions=[action for e in win.doc.data['events'] if e['when']=='flag_changed' and e.get('flag')==alias and e.get('is_set')==state for action in e['actions']]
        if actions:ins.note(tr('Activado' if state else 'Desactivado')+': '+action_summary(actions))

"""Contextual authoring of ordinary events; no additional runtime callbacks."""
import copy
from dataclasses import dataclass,field
from PySide6.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QLabel,QComboBox,
    QPushButton,QDialog,QDialogButtonBox,QCheckBox,QInputDialog,QSplitter,QSizePolicy)
from PySide6.QtCore import Qt
from .i18n import tr,diagnostic
from .click_actions import ClickActions
from .director import action_summary


@dataclass
class Reaction:
    key:str
    title:str
    when:str
    filters:dict=field(default_factory=dict)
    required:list=field(default_factory=list)
    once:bool=False
    origin:tuple=()


def available(win,path):
    specs=_available(win,path)
    for spec in specs:spec.origin=tuple(path)
    return specs


def _available(win,path):
    if not win.doc or not hasattr(win.doc,'campaign') or win.doc.campaign.get('project_format') not in (9,10):return []
    path=tuple(path)
    if path[:1]==('scenes',):
        if path[1]!=win.doc.active:return []
        path=path[2:] or ('level',)
    scene=win.doc.campaign['scenes'][win.doc.active]
    if path in (('level',),('chronicle',)):
        return [Reaction('start',tr('Al entrar en esta escena'),'scene_start'),
                Reaction('note',tr('Al cerrar cualquier nota de esta escena'),'note_closed')]
    if len(path)!=2:return []
    collection,index=path
    if collection not in {'actors','objects','triggers','conversations','sequences','encounters','generators','quests'} or type(index) is not int:return []
    row=win.doc.campaign['quests'][index] if collection=='quests' else scene.get(collection,[])[index]
    ident=row['id']
    def target(key,title,when,filter_key,once=False):return Reaction(key,title,when,{filter_key:ident},once=once)
    if collection=='actors':return [target('death',tr('Al morir este actor'),'actor_killed','actor',True)]
    if collection=='objects':
        result=[target('use',tr('Al usar este objeto'),'object_clicked','object')]
        kinds={t['id']:t['kind'] for t in win.backend.resources['templates']}
        if kinds.get(row.get('template')) in {'items','weapons','armour'}:result.append(target('pickup',tr('Cuando el jugador tenga este objeto'),'item_picked_up','item',True))
        return result
    if collection=='triggers':
        if row.get('native_script'):return []
        return [target('enter',tr('Al entrar en esta zona'),'trigger_enter','trigger',row.get('once',True)),
                target('leave',tr('Al salir de esta zona'),'trigger_leave','trigger')]
    if collection=='conversations':return [target('end',tr('Al terminar esta conversación'),'conversation_ended','conversation')]
    if collection=='sequences':return [target('end',tr('Al terminar esta secuencia'),'sequence_ended','sequence')] if row.get('steps') or row.get('camera_path') else []
    if collection=='encounters':return [target('complete',tr('Al derrotar a todo el grupo'),'encounter_complete','encounter',True)]
    if collection=='generators' and win.doc.campaign.get('project_format')==10:
        return [target(key,tr(title),when,'generator') for key,title,when in (
            ('start','Al empezar el encuentro dinámico','generator_started'),('wave_start','Al empezar cada oleada','wave_started'),
            ('wave_end','Al terminar cada oleada','wave_complete'),('complete','Al completar el encuentro dinámico','generator_complete'),
            ('stop','Al detener el encuentro dinámico','generator_stopped'))]
    if collection=='quests':
        return [Reaction('active',tr('Cuando la misión esté activa'),'state_changed',required=[dict(quest=ident,state='active')],once=True),
                Reaction('complete',tr('Cuando la misión esté completa'),'state_changed',required=[dict(quest=ident,state='complete')],once=True)]+[
            Reaction('step'+str(i),tr('Cuando esté activo el paso {0}').format(i+1)+' · '+step,'state_changed',required=[dict(quest=ident,step=i)],once=True) for i,step in enumerate(row['steps'])]
    return []


def matching(events,reaction):
    return [e for e in events if e.get('when')==reaction.when and
            all(e.get(k)==v for k,v in reaction.filters.items()) and
            all(c in e.get('conditions',[]) for c in reaction.required)]


def event_label(event):
    filters=' · '.join(k+'='+str(event[k]) for k in ('result','wave','phase','is_set') if k in event)
    return event['id']+(' · '+filters if filters else '')+' · '+action_summary(event['actions'])+(' · '+tr('Con condiciones') if event.get('conditions') else '')


def choose(win,reaction):
    matches=matching(win.doc.data['events'],reaction)
    if len(matches)<2:return matches[0] if matches else None
    labels=[event_label(e) for e in matches]
    selected,ok=QInputDialog.getItem(win,tr('Acciones vinculadas'),tr('Evento existente'),labels,0,False)
    return matches[labels.index(selected)] if ok else False


def edit_dialog(win,event,reaction):
    root=win.doc.snapshot();scene=root['scenes'][win.doc.active];draft=copy.deepcopy(event)
    for condition in reaction.required:draft.setdefault('conditions',[]).remove(condition)
    original_extra=copy.deepcopy(draft.get('conditions',[]))
    scene['events'].append(draft);index=len(scene['events'])-1
    dialog=QDialog(win);dialog.setObjectName('linked_event_dialog');dialog.setWindowTitle(reaction.title);dialog.resize(730,720)
    layout=QVBoxLayout(dialog);hint=QLabel(tr('Configura las acciones aquí. El enlace con el origen se conserva; también puedes editar el evento completo desde «Ver evento».'));hint.setWordWrap(True);layout.addWidget(hint)
    error=QLabel();error.setWordWrap(True)
    once=QCheckBox(tr('Una sola vez'));once.setObjectName('linked_once');once.setChecked(event.get('once',reaction.once));layout.addWidget(once)
    if reaction.required:
        condition=QLabel(reaction.title+' · '+tr('Se comprueba también al entrar en la escena.'));condition.setWordWrap(True);layout.addWidget(condition)
    split=QSplitter(Qt.Orientation.Vertical);layout.addWidget(split,1)
    actions=ClickActions(win,root,index,error,dialog);actions.setObjectName('linked_actions');split.addWidget(actions)
    show=QCheckBox(tr('Mostrar condiciones adicionales'));show.setObjectName('linked_show_conditions');show.setChecked(bool(draft.get('conditions')));layout.addWidget(show)
    conditions=ClickActions(win,root,index,error,dialog,field='conditions')
    conditions.scroll.setMinimumHeight(100);conditions.setObjectName('linked_conditions');split.addWidget(conditions)
    conditions.setVisible(show.isChecked());show.toggled.connect(conditions.setVisible);split.setSizes([360,180])
    layout.addWidget(error);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons)
    def accept():
        if not actions.commit() or not conditions.commit():return
        result=copy.deepcopy(actions.event);result['once']=once.isChecked()
        result['conditions']=copy.deepcopy(event.get('conditions',[])) if result.get('conditions',[])==original_extra else copy.deepcopy(reaction.required)+result.get('conditions',[])
        if not result['conditions']:result.pop('conditions',None)
        # Reject new invalid references without making unrelated existing drafts
        # impossible to edit. The ordinary project validator remains authoritative.
        trial=win.doc.snapshot();events=trial['scenes'][win.doc.active]['events']
        old=next((i for i,e in enumerate(events) if e['id']==event['id']),None)
        if result['actions']:
            if old is None:events.append(result)
            else:events[old]=result
            before={(p.path,p.message) for p in win.backend.validate(win.doc.snapshot()).problems if p.severity=='ERROR'}
            errors=[p for p in win.backend.validate(trial).problems if p.severity=='ERROR' and (p.path,p.message) not in before]
            if errors:error.setText('\n'.join(diagnostic(p.message) for p in errors));return
        dialog.event_result=result;dialog.accept()
    buttons.accepted.connect(accept);buttons.rejected.connect(dialog.reject)
    return dialog.event_result if dialog.exec()==QDialog.DialogCode.Accepted else None


def edit(win,reaction):
    if win.busy or not win.commit_properties():return
    if reaction.origin:
        reaction=next((s for s in available(win,reaction.origin) if s.key==reaction.key),None)
        if reaction is None:return
    existing=choose(win,reaction)
    if existing is False:return
    events=win.doc.data['events'];snapshot=win.doc.snapshot();document=win.doc
    stem='on_'+('_'.join(str(v) for v in reaction.filters.values()) or reaction.key)+'_'+reaction.key
    event=copy.deepcopy(existing) if existing else dict(id=win.doc.unique_id('events',stem[:48]),when=reaction.when,**reaction.filters,conditions=copy.deepcopy(reaction.required),once=reaction.once,actions=[])
    result=edit_dialog(win,event,reaction)
    if result is None or win.doc is not document or win.doc.snapshot()!=snapshot:return
    def normalized(value):
        value=copy.deepcopy(value);value.setdefault('once',reaction.once)
        if not value.get('conditions'):value.pop('conditions',None)
        return value
    if normalized(result)==normalized(event) or not result['actions'] and existing is None:return
    if not result['actions']:
        from ..campaign_relations import graph
        target=('scenes',win.doc.active,'events',events.index(existing))
        if any(link.target==target for link in graph(snapshot)):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(win,tr('Acciones vinculadas'),tr('Otros elementos utilizan este evento. Usa «Ver evento» y Eliminar para revisar y retirar sus referencias.'));return
        events.remove(existing)
    elif existing is None:events.append(result)
    else:existing.clear();existing.update(result)
    win.history_time=0;win.changed(True)


def open_event(win,reaction):
    if not win.commit_properties():return
    if reaction.origin:
        reaction=next((s for s in available(win,reaction.origin) if s.key==reaction.key),None)
        if reaction is None:return
    event=choose(win,reaction)
    if event:win.select(('events',win.doc.data['events'].index(event)))


def controls(win,path):
    options=available(win,path)
    if not options:return None
    panel=QWidget();panel.setObjectName('linked_events');layout=QVBoxLayout(panel);layout.setContentsMargins(0,5,0,0)
    bar=QHBoxLayout();layout.addLayout(bar);which=QComboBox();which.setObjectName('linked_when');bar.addWidget(which,1)
    which.setMinimumWidth(0);which.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    for i,spec in enumerate(options):
        which.addItem(spec.title);which.setItemData(i,spec.title,Qt.ItemDataRole.ToolTipRole)
    edit_button=QPushButton(tr('Acciones…'));edit_button.setObjectName('linked_edit');bar.addWidget(edit_button)
    view=QPushButton(tr('Ver evento'));view.setObjectName('linked_view');bar.addWidget(view)
    summary=QLabel();summary.setWordWrap(True);summary.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);summary.setObjectName('linked_summary');layout.addWidget(summary)
    def current():return options[which.currentIndex()]
    def refresh():
        spec=current();which.setToolTip(spec.title);matches=matching(win.doc.data['events'],spec)
        text='\n'.join(event_label(e) for e in matches) or tr('Sin acciones vinculadas. Pulsa «Acciones…» para añadirlas.')
        summary.setText(text);summary.setToolTip(text);view.setEnabled(bool(matches))
    which.currentIndexChanged.connect(refresh)
    edit_button.clicked.connect(lambda:win.guard(lambda:edit(win,current())))
    view.clicked.connect(lambda:win.guard(lambda:open_event(win,current())))
    refresh();return panel


def attach(ins):
    if not ins.win.doc:return
    panel=controls(ins.win,ins.path)
    if panel:ins.form.addRow(panel)


def context_menu(win,menu,path):
    options=available(win,path)
    if not options:return
    submenu=menu.addMenu(tr('Acciones vinculadas'));submenu.setObjectName('context_linked_events')
    for spec in options:
        action=submenu.addAction(spec.title);action.setEnabled(not win.busy)
        action.triggered.connect(lambda checked=False,spec=spec:win.guard(lambda:edit(win,spec)))

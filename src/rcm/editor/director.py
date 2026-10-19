"""Small director controls inside existing Sequences and conversation inspectors."""
import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QDialogButtonBox,QListWidget,QDoubleSpinBox,QFormLayout,QLineEdit,QWidget,QMessageBox,QCheckBox
from .i18n import tr,diagnostic
from .click_actions import ClickActions


def staging_controls(ins,conversation,path):
    value=conversation.get('staging');entries=ins.ids('entries')
    def update(value):
        ins.win.history_time=0
        ins.set(path+('staging',),copy.deepcopy(value),True)
        ins.win.refresh()
    choices=[(tr('Automática'),None)]+[(tr('Entrada RCM')+' · '+label,key) for label,key in entries]
    for label,key in entries:
        native=value if isinstance(value,dict) and value['entries'][0]==key else dict(mode='native',entries=[key])
        choices.append((tr('Punto de conversación nativo')+' · '+label,native))
    ins.combo(tr('Puesta en escena'),choices,value,update,'conversation_staging')
    if isinstance(value,dict):
        points=value['entries']
        for index in range(1,min(4,len(points)+1)):
            selected=points[index] if index<len(points) else None
            def change(v,index=index):
                result=copy.deepcopy(value)
                if v is None:result['entries']=result['entries'][:index]
                elif index<len(result['entries']):result['entries'][index]=v
                else:result['entries'].append(v)
                update(result)
            ins.combo(tr('Compañero')+' '+str(index),[(tr('Posición compartida'),None)]+[(label,key) for label,key in entries if key==selected or key not in points],selected,change,'conversation_party_'+str(index))
        ins.note(tr('Usa entradas nombradas para colocar al grupo. Crea y mueve esos puntos en Espacio 3D. Los puntos nativos admiten giro Z; comprueba formación y colisiones dentro del juego.'))


def default_action(kind,scene):
    actor=next((a['id'] for a in scene['actors']),'Player')
    return {'camera_shot':dict(actor=actor,reference='Player',preset='ots_speaker_close',transition=.3),
            'play_camera_path':dict(resource='',speed=30),
            'camera_fade':dict(initial=0,target=255,duration=1,bounce=False),
            'camera_flash':dict(initial=0,target=255,duration=.3,bounce=True),
            'camera_filter':dict(duration=1),
            'clear_camera_effects':True,'look_at':dict(actor=actor,target='Player'),
            'look_at_point':dict(actor=actor,waypoint=next((p['id'] for p in scene.get('waypoints',[])),'')),
            'play_motion':dict(actor=actor,motion='stand'),'stop_actor':actor,'set_weather':'drizzle',
            'set_dynamic_light':dict(entity=actor,color=[1,1,1],intensity=1,radius=300,style='constant'),
            'clear_dynamic_light':actor}[kind]


def render_action(ins,kind,value,path,scene):
    from ..cinematics import DIRECTOR_ACTIONS
    if kind not in DIRECTOR_ACTIONS:return False
    from ..camera_presets import CINEMA_PRESETS
    from ..dynamic_targets import choices
    actor_choices=ins.ids('actors')+choices(scene)
    actors=[(tr('Jugador'),'Player')]+actor_choices
    def set_key(key,v):ins.set(path+(kind,key),v)
    def actor(key,label):ins.combo(label,actors,value.get(key,'Player'),lambda v:set_key(key,v),'director_'+key)
    if kind=='clear_dynamic_light':ins.combo(tr('Entidad'),actor_choices+ins.ids('objects'),value,lambda v:ins.set(path+(kind,),v),'director_light_entity')
    elif kind=='set_dynamic_light':
        from ..world_effects import STYLES
        ins.combo(tr('Entidad'),actor_choices+ins.ids('objects'),value['entity'],lambda v:set_key('entity',v),'director_light_entity')
        for axis,label in enumerate([tr('Rojo'),tr('Verde'),tr('Azul')]):ins.spin(label,value['color'][axis],lambda v,axis=axis:ins.set(path+(kind,'color',axis),v),'director_light_'+str(axis),True,0,1)
        ins.spin(tr('Intensidad'),value['intensity'],lambda v:set_key('intensity',v),'director_light_intensity',True,0,1000)
        ins.spin(tr('Radio'),value['radius'],lambda v:set_key('radius',v),'director_light_radius',True,.01,100000)
        ins.combo(tr('Estilo'),[(v,v) for v in STYLES],value.get('style','constant'),lambda v:set_key('style',v),'director_light_style')
        ins.note(tr('Luz runtime asociada a esta entidad. No modifica la iluminación horneada del escenario. Requiere prueba dentro del juego.'))
    elif kind=='play_camera_path':
        choices=[((tr('Del proyecto') if e.get('project_owned') else tr('Original'))+' · '+e['id'],e['id']) for e in ins.win.backend.resources['entries'] if e['extension']=='.ncp']
        def choose_path(v):
            value['resource']=v
            if any(e.get('timed') and e['id']==v for e in ins.win.backend.resources['entries']):value['speed']=1
            ins.win.changed(True)
        ins.combo(tr('Travelling'),choices,value['resource'],choose_path,'director_camera_path')
        ins.spin(tr('Velocidad del travelling'),value['speed'],lambda v:set_key('speed',v),'director_path_speed',True,.01,100).setEnabled(not any(e.get('timed') and e['id']==value['resource'] for e in ins.win.backend.resources['entries']))
    elif kind=='set_weather':ins.combo(tr('Clima'),[(tr(label),v) for label,v in [('Llovizna','drizzle'),('Lluvia ligera','lightRain'),('Lluvia intensa','heavyRain'),('Nieve','snow')]],value,lambda v:ins.set(path+(kind,),v),'director_weather')
    elif kind=='stop_actor':ins.combo(tr('Actor'),actors,value,lambda v:ins.set(path+(kind,),v),'director_actor')
    elif kind in {'look_at','look_at_point'}:
        actor('actor',tr('Actor'))
        if kind=='look_at':actor('target',tr('Mira a'))
        else:ins.combo(tr('Punto'),[(p['name'],p['id']) for p in scene.get('waypoints',[])],value['waypoint'],lambda v:set_key('waypoint',v),'director_waypoint')
    elif kind=='play_motion':
        def change_actor(v):
            value['actor']=v;value['motion']='stand';ins.win.changed(True)
        ins.combo(tr('Actor'),actor_choices,value['actor'],change_actor,'director_actor')
        from ..motions import slots,label
        from ..instance_overrides import effective_template
        row=next((a for a in scene['actors'] if a['id']==value['actor']),None)
        if row is None:
            from ..dynamic_targets import candidates
            row=candidates(scene).get(value['actor'])
        template=(row['template'] if str(value['actor']).startswith('dynamic/') else effective_template(ins.win.doc.campaign,ins.win.doc.campaign['scenes'][ins.win.doc.active],row)) if row else None
        choices=[(label(slot),slot['mode']) for slot in slots(ins.win.backend.resources,template)]
        if row and row.get('templates'):choices=[(label_,mode) for label_,mode in choices if all(mode in {s['mode'] for s in slots(ins.win.backend.resources,t)} for t in row['templates'])]
        ins.combo(tr('Gesto'),choices,value['motion'],lambda v:set_key('motion',v),'director_motion')
    elif kind=='camera_shot':
        actor('actor',tr('Sujeto'));actor('reference',tr('Referencia'))
        ins.combo(tr('Plano'),[(tr(v[0]),k) for k,v in CINEMA_PRESETS.items()],value['preset'],lambda v:set_key('preset',v),'director_preset')
        ins.combo(tr('Ángulo'),[(tr(a),b) for a,b in [('Bajo','low'),('Medio','medium'),('Alto','high')]],value.get('angle','medium'),lambda v:set_key('angle',v),'director_angle')
        ins.spin(tr('Transición (s)'),value.get('transition',.3),lambda v:set_key('transition',v),'director_transition',True,0,10)
    elif kind in {'camera_fade','camera_flash','camera_filter'}:
        if kind=='camera_fade':
            def preset(v):
                if v is not None:value.update(initial=0 if v=='in' else 255,target=255 if v=='in' else 0);ins.win.changed(True)
            ins.combo(tr('Fundido'),[(tr('Personalizado'),None),(tr('Desde negro'),'in'),(tr('A negro'),'out')],None,preset,'director_fade_preset')
        if kind!='camera_filter':
            for key,label in [('initial',tr('Intensidad inicial')),('target',tr('Intensidad final'))]:ins.spin(label,value[key],lambda v,k=key:set_key(k,v),'director_'+key,True,0,255)
            ins.combo(tr('Repetir en sentido inverso'),[(tr('No'),False),(tr('Sí'),True)],value.get('bounce',False),lambda v:set_key('bounce',v),'director_bounce')
        ins.spin(tr('Duración (s)'),value['duration'],lambda v:set_key('duration',v),'director_duration',True,.01,120)
    return True


def at(root,path):
    for key in path:root=root[key]
    return root


def edit_actions(win,actions,apply):
    """Transactional reuse of the ordinary action inspector, with one undo."""
    if not win.commit_properties():return
    root=win.doc.snapshot();scene=root['scenes'][win.doc.active]
    scene['events'].append(dict(id='director_draft',when='manual',actions=copy.deepcopy(actions)))
    dialog=QDialog(win);dialog.setWindowTitle(tr('Acciones de escena'));dialog.resize(690,630)
    layout=QVBoxLayout(dialog);error=QLabel();error.setWordWrap(True)
    controls=ClickActions(win,root,len(scene['events'])-1,error,dialog);layout.addWidget(controls,1);layout.addWidget(error)
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons)
    def accept():
        if controls.commit():apply(copy.deepcopy(controls.event['actions']));dialog.accept()
    buttons.accepted.connect(accept);buttons.rejected.connect(dialog.reject);dialog.exec()


def action_summary(actions):
    from ..campaign import ACTIONS
    return ', '.join(tr(ACTIONS.get(next(iter(a)),(next(iter(a)),''))[0]) for a in actions)


def cue_controls(panel,form,row):
    win=panel.win;listing=QListWidget();listing.setObjectName('director_cues');listing.setMinimumHeight(130)
    for cue in row.get('cues',[]):listing.addItem(f'{cue["at"]:.2f} s · '+action_summary(cue['actions']))
    form.addRow(tr('Timeline de escena'),listing)
    buttons=QWidget();bar=QHBoxLayout(buttons);bar.setContentsMargins(0,0,0,0)
    def edit(index=None):
        if index is not None and index<0:return
        cues=row.get('cues',[]);cue=copy.deepcopy(cues[index]) if index is not None else dict(at=min(max([c['at'] for c in cues],default=-1)+1,max(0,row['duration']-.15)),actions=[{'camera_fade':dict(initial=0,target=255,duration=1)}])
        dialog=QDialog(win);dialog.setWindowTitle(tr('Acción de escena'));layout=QVBoxLayout(dialog);time=QDoubleSpinBox();time.setDecimals(2);time.setRange(0,max(0,row['duration']-.01));time.setSuffix(' s');time.setValue(cue['at']);layout.addWidget(time)
        label=QLabel(action_summary(cue['actions']));label.setWordWrap(True);layout.addWidget(label)
        button=QPushButton(tr('Editar acciones…'));button.clicked.connect(lambda:edit_actions(win,cue['actions'],lambda values:(cue.update(actions=values),label.setText(action_summary(values)))));layout.addWidget(button)
        choices=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(choices);choices.accepted.connect(dialog.accept);choices.rejected.connect(dialog.reject)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        if index is None and not cue['actions']:return
        cue['at']=time.value()
        def change():
            values=row.setdefault('cues',[])
            if index is None:values.append(cue)
            elif cue['actions']:values[index]=cue
            else:values.pop(index)
            values.sort(key=lambda c:c['at'])
        panel.mutate(change,True)
    for text,name,callback in [('+ '+tr('Añadir acción'),'director_add_cue',lambda:edit()),(tr('Editar'),'director_edit_cue',lambda:edit(listing.currentRow())),(tr('Eliminar'),'director_remove_cue',lambda:panel.mutate(lambda:row['cues'].pop(listing.currentRow()),True) if listing.currentRow()>=0 else None)]:
        button=QPushButton(text);button.setObjectName(name);button.clicked.connect(callback);bar.addWidget(button)
    form.addRow(buttons)


class CameraPathDialog(QDialog):
    """Modeless so the author can keep navigating the real viewport."""
    def __init__(self,win,sequence_path,resource_id=None):
        if win.spatial.viewport is None:raise ValueError(tr('El espacio 3D no está disponible. Activa la vista 3D para capturar puntos de cámara.'))
        super().__init__(win,Qt.WindowType.Tool);self.win=win;self.sequence_path=sequence_path;self.initial=win.doc.snapshot();self.root=copy.deepcopy(self.initial)
        self.setWindowTitle(tr('Travelling propio'));self.setWindowModality(Qt.WindowModality.NonModal);self.resize(610,610)
        scene=self.root['scenes'][win.doc.active];sequence=at(self.root,sequence_path) if sequence_path else {};rows=self.root.setdefault('resources',{}).setdefault('camera_paths',[])
        timed={a['play_camera_path']['resource'] for cue in sequence.get('cues',[]) for a in cue['actions'] if 'play_camera_path' in a and any(r['id']==a['play_camera_path']['resource'] for r in rows)}
        camera_id=resource_id or sequence.get('camera_path') or (next(iter(timed)) if len(timed)==1 else None)
        self.main_binding=bool(sequence_path and (not camera_id or sequence.get('camera_path')==camera_id))
        self.row=next((r for r in rows if r['id']==camera_id),None)
        if self.row is None:
            number=1
            while any(r['id']=='camera_path'+str(number) for r in rows):number+=1
            self.row=dict(id='camera_path'+str(number),name=tr('Travelling'),scene=scene['id'],level=scene['level']['source'],points=[self.capture()]);rows.append(self.row)
        if self.main_binding:sequence['camera_path']=self.row['id'];sequence.pop('steps',None);sequence.setdefault('path_speed',30)
        self.sequence=sequence
        layout=QVBoxLayout(self);form=QFormLayout();self.name=QLineEdit(self.row.get('name',self.row['id']));self.name.setObjectName('camera_path_name');form.addRow(tr('Nombre'),self.name);layout.addLayout(form)
        self.speed=QDoubleSpinBox();self.speed.setRange(.01,100);self.speed.setValue(sequence.get('path_speed',30));self.speed.setObjectName('camera_path_speed')
        if self.main_binding:form.addRow(tr('Velocidad del travelling'),self.speed)
        self.timed=QCheckBox(tr('Tiempo por tramo (permite giros y esperas sin desplazamiento)'));self.timed.setObjectName('camera_path_timed');self.timed.setChecked(self.row.get('timed',False));form.addRow(self.timed)
        def timing(value):
            if value:self.row['timed']=True;self.speed.setValue(1)
            else:
                self.row.pop('timed',None)
                for point in self.row['points']:point.pop('duration',None)
            self.speed.setEnabled(not value);self.select(self.list.currentRow())
        self.timed.toggled.connect(timing);self.speed.setEnabled(not self.timed.isChecked())
        self.start=QCheckBox(tr('Iniciar al entrar en la escena'));self.start.setObjectName('camera_path_start');self.start.setVisible(bool(sequence_path) and not any(a.get('play_sequence')==sequence.get('id') for e in scene['events'] for a in e['actions']));layout.addWidget(self.start)
        note=QLabel(tr('Navega en el espacio 3D y añade puntos desde esa vista. Trayectoria lineal; sin previsualización de colisión del motor.'));note.setWordWrap(True);layout.addWidget(note)
        self.list=QListWidget();self.list.setObjectName('camera_path_points');layout.addWidget(self.list,1);self.list.currentRowChanged.connect(self.select)
        self.axes=QWidget();self.axes_form=QFormLayout(self.axes);layout.addWidget(self.axes)
        for group in [[(tr('+ Punto desde esta vista'),'camera_add_point',self.add),(tr('Insertar después'),'camera_insert_point',self.insert)],[(tr('Actualizar desde esta vista'),'camera_update_point',self.update_point),(tr('Duplicar'),'camera_duplicate_point',self.duplicate)],[(tr('Eliminar'),'camera_delete_point',self.remove),(tr('Subir'),'camera_point_up',lambda:self.move(-1)),(tr('Bajar'),'camera_point_down',lambda:self.move(1))]]:
            bar=QHBoxLayout();layout.addLayout(bar)
            for text,name,callback in group:
                button=QPushButton(text);button.setObjectName(name);button.clicked.connect(callback);bar.addWidget(button)
        self.error=QLabel();self.error.setWordWrap(True);layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.finished.connect(self.clear_preview);self.refresh(0)
    def capture(self):
        view=self.win.spatial.viewport
        # Native camera basis 0x4bb5b0: forward=(-sin(yaw)*cos(pitch),
        # cos(yaw)*cos(pitch),sin(pitch)); Codex VEC_PITCH=0, ROLL=1, YAW=2.
        return dict(position=[float(v) for v in view.pos],orientation=[float(view.pitch),0.0,float(view.yaw-90)])
    def preview(self):
        self.win.spatial.viewport.director_preview=copy.deepcopy(self.row['points']);self.win.spatial.viewport.director_selected=self.list.currentRow();self.win.spatial.viewport.update()
    def clear_preview(self,*unused):self.win.spatial.viewport.director_preview=[];self.win.spatial.viewport.update()
    def refresh(self,index):
        self.list.blockSignals(True);self.list.clear()
        for i,p in enumerate(self.row['points']):self.list.addItem(str(i+1)+' · '+', '.join(f'{v:.1f}' for v in p['position']))
        self.list.setCurrentRow(min(max(0,index),len(self.row['points'])-1));self.list.blockSignals(False);self.select(self.list.currentRow());self.preview()
    def select(self,index):
        while self.axes_form.rowCount():self.axes_form.removeRow(0)
        if index<0:return
        point=self.row['points'][index]
        if self.row.get('timed') and index<len(self.row['points'])-1:
            duration=QDoubleSpinBox();duration.setRange(.15,120);duration.setDecimals(2);duration.setSuffix(' s');duration.setValue(point.get('duration',1));duration.setObjectName('camera_point_duration');duration.valueChanged.connect(lambda v:point.update(duration=v));self.axes_form.addRow(tr('Tiempo hasta el siguiente punto'),duration)
        for key,labels in [('position',['X','Y','Z']),('orientation',[tr('Inclinación vertical'),tr('Inclinación lateral'),tr('Orientación')])]:
            for axis,label in enumerate(labels):
                value=QDoubleSpinBox();value.setDecimals(3);value.setRange(-1e6,1e6);value.setValue(point[key][axis]);value.setObjectName('camera_point_'+key+'_'+str(axis));value.valueChanged.connect(lambda v,key=key,axis=axis:self.change_point(key,axis,v));self.axes_form.addRow(label,value)
        self.preview()
    def change_point(self,key,axis,value):self.row['points'][self.list.currentRow()][key][axis]=value;self.preview()
    def add(self):self.row['points'].append(self.capture());self.refresh(len(self.row['points'])-1)
    def insert(self):
        i=max(0,self.list.currentRow()+1);self.row['points'].insert(i,self.capture());self.refresh(i)
    def update_point(self):
        i=self.list.currentRow()
        if i>=0:
            duration=self.row['points'][i].get('duration');self.row['points'][i]=self.capture()
            if duration is not None:self.row['points'][i]['duration']=duration
            self.refresh(i)
    def duplicate(self):
        i=self.list.currentRow()
        if i>=0:self.row['points'].insert(i+1,copy.deepcopy(self.row['points'][i]));self.refresh(i+1)
    def remove(self):
        i=self.list.currentRow()
        if i>=0:self.row['points'].pop(i);self.refresh(i)
    def move(self,delta):
        i=self.list.currentRow();j=i+delta
        if i>=0 and 0<=j<len(self.row['points']):self.row['points'][i],self.row['points'][j]=self.row['points'][j],self.row['points'][i];self.refresh(j)
    def accept(self):
        try:
            if self.win.doc.snapshot()!=self.initial:raise ValueError(tr('El proyecto cambió mientras editabas el travelling. Cierra esta ventana y vuelve a abrirlo.'))
            from ..camera_paths import authored
            path=authored(self.row['points'],self.row.get('timed',False));self.row['name']=self.name.text()
            if self.main_binding:self.sequence['path_speed']=self.speed.value()
            if self.main_binding and self.row.get('timed'):self.sequence['duration']=max(self.sequence['duration'],path.total)
            if self.start.isChecked():
                scene=self.root['scenes'][self.win.doc.active];number=1
                while any(e['id']=='camera_start'+str(number) for e in scene['events']):number+=1
                scene['events'].append(dict(id='camera_start'+str(number),when='scene_start',once=True,actions=[{'play_sequence':self.sequence['id']}]))
            self.win.doc.data=self.root;self.win.history_time=0;self.win.changed(True);super().accept()
        except ValueError as error:self.error.setText(diagnostic(error))


def open_camera_path(win,path,resource_id=None):
    if not win.commit_properties():return
    if win.spatial.viewport is None:
        QMessageBox.information(win,tr('Travelling propio'),tr('El espacio 3D no está disponible. Activa la vista 3D para capturar puntos de cámara.'));return
    scene_index=path[1] if path else next((i for i,s in enumerate(win.doc.campaign['scenes']) if any(r['id']==resource_id and r['scene']==s['id'] for r in win.doc.campaign.get('resources',{}).get('camera_paths',[]))),win.doc.active)
    if scene_index!=win.doc.active:win.doc.active=scene_index;win.refresh()
    if win.spatial.loading:
        QMessageBox.information(win,tr('Travelling propio'),tr('Espera a que termine la carga del escenario.'));return
    dialog=CameraPathDialog(win,path,resource_id);win._director_dialog=dialog
    win.center_tabs.setCurrentWidget(win.spatial);dialog.show()

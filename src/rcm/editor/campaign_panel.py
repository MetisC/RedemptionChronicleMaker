"""Campaign authoring controls over the existing window/document and event inspector."""
from pathlib import Path
import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox,QLineEdit,QTreeWidget,QTreeWidgetItem,QScrollArea,QFormLayout,QSpinBox,QDoubleSpinBox,QListWidget,QListWidgetItem,QFileDialog,QMessageBox,QDialog,QSplitter,QDialogButtonBox,QInputDialog
from .browser import ResourceDialog
from ..campaign import ACTIONS,WHEN
from ..campaign_document import CampaignDocument

ROLE=Qt.ItemDataRole.UserRole

class CampaignPanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.path=None
        layout=QVBoxLayout(self)
        top=QHBoxLayout();self.scene=QComboBox();self.scene.setObjectName('campaign_scene');self.scene.currentIndexChanged.connect(self.switch_scene)
        top.addWidget(QLabel('Escena activa'));top.addWidget(self.scene,1)
        spatial=QHBoxLayout();story=QHBoxLayout()
        for i,(label,name,cb) in enumerate([('Crear campaña','convert_campaign',self.convert),('+ Escena','add_scene',self.add_scene),('+ Entrada','add_entry',lambda:self.add_marker('entries')),('+ Waypoint','add_waypoint',lambda:self.add_marker('waypoints')),('+ Recorrido','add_path',self.add_path),('+ Quest','add_quest',self.add_quest),('+ Encuentro','add_encounter',self.add_encounter),('+ Cámara','add_sequence',self.add_sequence)]):
            b=QPushButton(label);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));(spatial if i<5 else story).addWidget(b)
        layout.addLayout(top);layout.addLayout(spatial);layout.addLayout(story);self.dashboard=QLabel();self.dashboard.setWordWrap(True);layout.addWidget(self.dashboard)
        self.search=QLineEdit();self.search.setObjectName('global_search');self.search.setPlaceholderText('Buscar en toda la crónica · Ctrl+Shift+F');self.search.textChanged.connect(self.refresh_rows);layout.addWidget(self.search)
        self.panes=QSplitter(Qt.Orientation.Vertical);self.panes.setObjectName('campaign_panes');layout.addWidget(self.panes,1)
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['Elemento','Detalle']);self.tree.setColumnWidth(0,260);self.tree.setObjectName('campaign_tree');self.tree.itemClicked.connect(self.selected);self.panes.addWidget(self.tree)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.setMinimumHeight(190);self.panes.addWidget(self.scroll)
        self.panes.setStretchFactor(0,1);self.panes.setStretchFactor(1,3);self.panes.setSizes([150,400]);self.panes.setChildrenCollapsible(False)
        bottom=QHBoxLayout();gamebar=QHBoxLayout()
        for i,(label,name,cb) in enumerate([('Duplicar','duplicate_campaign',self.duplicate),('Borrar','delete_campaign',self.delete),('Referencias','campaign_references',lambda:win.find_references(self.path)),('Guardar','campaign_save',win.save_project),('Integridad','campaign_integrity',win.validate_from_ui),('Deploy','campaign_deploy',self.deploy),('Ejecutar','campaign_run',self.run_game),('Ruta del juego…','game_settings',self.game_settings),('Acceso del juego…','game_shortcut',self.game_shortcut)]):
            b=QPushButton(label);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));(bottom if i<5 else gamebar).addWidget(b)
        layout.addLayout(bottom);layout.addLayout(gamebar)
    def source(self):return self.win.doc.campaign if self.win.doc and hasattr(self.win.doc,'campaign') else None
    def focus_search(self):
        self.win.center_tabs.setCurrentWidget(self)
        self.search.setFocus()
    def convert(self):
        if not self.win.doc:raise ValueError('Crea primero una crónica y elige su mapa')
        if not self.win.commit_properties():return False
        if not hasattr(self.win.doc,'campaign'):
            if len(self.win.doc.data['chronicle']['id'])>14:raise ValueError('Acorta el ID de campaña a 14 caracteres')
            self.win.doc=CampaignDocument.convert(self.win.doc);self.win.selection=('chronicle',);self.win.refresh()
        self.win.center_tabs.setCurrentWidget(self)
        return True
    def refresh(self):
        root=self.source();self.scene.blockSignals(True);self.scene.clear()
        if root:
            for s in root['scenes']:self.scene.addItem(s['id']+' · '+s['level']['source'],s['id'])
            self.scene.setCurrentIndex(self.win.doc.active)
            self.dashboard.setText(root['chronicle']['name']+' · '+str(len(root['scenes']))+' escenas / '+str(len({s['level']['source'] for s in root['scenes']}))+' geometrías · '+str(sum(len(s['actors']) for s in root['scenes']))+' actores · '+str(len(root.get('quests',[])))+' quests · '+str(sum(len(s['events']) for s in root['scenes']))+' eventos')
        else:self.dashboard.setText('Convierte explícitamente un proyecto a campaña para añadir mapas, quests y encuentros. Los proyectos anteriores conservan su formato.')
        self.scene.blockSignals(False);self.refresh_rows()
        if not root:self.path=None
        if self.path:
            try:self.value()
            except (KeyError,IndexError,TypeError):self.path=None
        self.render()
    def refresh_rows(self):
        root=self.source();self.tree.clear()
        if not root:return
        query=self.search.text().casefold()
        def add(path,row,detail=''):
            if query and query not in str(row).casefold():return
            item=QTreeWidgetItem([row.get('title',row.get('name',row.get('id',''))),detail]);item.setData(0,ROLE,path);self.tree.addTopLevelItem(item)
            item.setToolTip(0,item.text(0));item.setToolTip(1,detail)
        for qi,q in enumerate(root.get('quests',[])):add(('quests',qi),q,'Quest · '+str(len(q['steps']))+' pasos')
        for si,s in enumerate(root['scenes']):
            add(('scenes',si),s,'Escena · '+s['level']['source'])
            for k in ['actors','objects','conversations','events','triggers','encounters','sequences','entries','waypoints','paths']:
                for i,row in enumerate(s.get(k,[])):add(('scenes',si,k,i),row,s['id']+' / '+k)
        for alias,index in root.get('state',{}).get('flags',{}).items():add(('state','flags',alias),{'id':alias},'Flag '+str(index))
    def switch_scene(self,index):
        if self.source() and index>=0 and index!=self.win.doc.active:
            if not self.win.commit_properties():
                self.scene.blockSignals(True);self.scene.setCurrentIndex(self.win.doc.active);self.scene.blockSignals(False)
                return
            self.win.doc.active=index;self.win.selection=('level',);self.path=None;self.win.refresh()
    def navigate(self,path):
        root=self.source()
        if not root:return
        if self.path!=tuple(path) and not self.win.commit_properties():return
        self.path=tuple(path)
        if path[0]=='scenes':
            self.win.doc.active=path[1]
            self.win.selection=tuple(path[2:]) if len(path)>2 else ('level',)
            self.win.refresh()
            if len(path)>2 and path[2] not in ['encounters','sequences','paths']:
                self.win.select(tuple(path[2:]));self.win.center_tabs.setCurrentIndex(1);return
        self.win.center_tabs.setCurrentWidget(self);self.render()
    def selected(self,item,column):self.navigate(item.data(0,ROLE))
    def mutate(self,callback,rebuild=False):
        if rebuild: self.win.history_time=0
        callback();self.win.changed(False)
        if rebuild:self.refresh_rows();self.render()
    def value(self):
        value=self.source()
        for k in self.path:value=value[k]
        return value
    def add_scene(self):
        if not self.convert():return
        mode,ok=QInputDialog.getItem(self,'Crear escena / layout','Cada escena tiene sus propios NPC, objetos y eventos. La geometría se reutiliza.', ['Nuevo layout vacío sobre este level','Duplicar layout actual','Escena sobre otro level…'],0,False)
        if not ok:return
        if mode=='Escena sobre otro level…':
            dialog=ResourceDialog(self.win.backend,'levels',self)
            if dialog.exec()!=QDialog.DialogCode.Accepted:return
            level={'source':dialog.selection}
        else:level=copy.deepcopy(self.source()['scenes'][self.win.doc.active]['level'])
        root=self.source();existing={s['id'] for s in root['scenes']};i=1
        while 'map'+str(i) in existing:i+=1
        row=copy.deepcopy(root['scenes'][self.win.doc.active]) if mode=='Duplicar layout actual' else {'level':level,'actors':[],'objects':[],'conversations':[],'events':[],'triggers':[],'encounters':[],'sequences':[]}
        row['id']='map'+str(i);root['scenes'].append(row)
        self.win.doc.active=len(root['scenes'])-1;self.path=('scenes',self.win.doc.active);self.win.selection=('level',);self.win.changed(True);self.render()
    def add_quest(self):
        if not self.convert():return
        root=self.source();i=1
        while any(q['id']=='quest'+str(i) for q in root['quests']):i+=1
        root['quests'].append({'id':'quest'+str(i),'title':'Nueva quest','description':'Describe la misión','steps':['Primer objetivo'],'reward_xp':0})
        self.path=('quests',len(root['quests'])-1);self.win.changed(True);self.render()
    def add_encounter(self):
        if not self.convert():return
        s=self.source()['scenes'][self.win.doc.active];rows=s.setdefault('encounters',[])
        rows.append({'id':self.unique(rows,'encounter'),'name':'Nuevo encuentro','actors':[]});self.path=('scenes',self.win.doc.active,'encounters',len(rows)-1);self.win.changed(True);self.render()
    def add_sequence(self):
        if not self.convert():return
        s=self.source()['scenes'][self.win.doc.active];rows=s.setdefault('sequences',[])
        rows.append({'id':self.unique(rows,'camera'),'name':'Nuevo plano','actor':s['actors'][0]['id'] if s['actors'] else '', 'duration':3.0,'shot':'medium','angle':'medium'})
        self.path=('scenes',self.win.doc.active,'sequences',len(rows)-1);self.win.changed(True);self.render()
    def enable_authoring9(self):
        if not self.convert():return False
        root=self.source();root['project_format']=9
        root.setdefault('resources',{});root.setdefault('metadata',{'version':'0.1.0'});root.setdefault('build_options',{'debug':True})
        for s in root['scenes']:
            for k in ('entries','waypoints','paths'):s.setdefault(k,[])
        return True
    def add_marker(self,kind):
        if self.enable_authoring9():self.win.spatial.begin_place(kind)
    def add_path(self):
        if not self.enable_authoring9():return
        s=self.source()['scenes'][self.win.doc.active];rows=s['paths']
        rows.append(dict(id=self.unique(rows,'path'),name='Nuevo recorrido',actor=s['actors'][0]['id'] if s['actors'] else '',points=[p['id'] for p in s['waypoints']],loop=False,tolerance=24,speed=90))
        self.path=('scenes',self.win.doc.active,'paths',len(rows)-1);self.win.changed(True);self.render()
    @staticmethod
    def unique(rows,stem):
        i=1
        while any(r['id']==stem+str(i) for r in rows):i+=1
        return stem+str(i)
    def duplicate(self):
        if not self.path:return
        if not self.win.commit_properties():return
        root=self.source();parent=root
        for k in self.path[:-1]:parent=parent[k]
        if not isinstance(parent,list):raise ValueError('Selecciona una entidad, quest o evento')
        row=copy.deepcopy(parent[self.path[-1]]);row['id']=self.unique(parent,'copy')
        if self.path[-2]=='actors':
            row.pop('conversation',None);row.pop('inventory',None)
        parent.append(row);self.path=self.path[:-1]+(len(parent)-1,);self.win.changed(True);self.render()
    def delete(self):
        if not self.path:return
        if not self.win.commit_properties():return
        parent=self.source()
        for k in self.path[:-1]:parent=parent[k]
        if self.path[0]=='scenes' and len(self.path)==2 and len(parent)==1:raise ValueError('La campaña necesita una escena')
        if not isinstance(parent,list):raise ValueError('No se puede borrar esa selección')
        from ..safe_edit import delete_candidate
        candidate=delete_candidate(self.win.doc,self.path,self.win.backend,remove_spawns=True)
        if QMessageBox.question(self,'Eliminar elemento','¿Eliminar este elemento? Puedes deshacer la operación.')!=QMessageBox.StandardButton.Yes:return
        self.win.doc.data=candidate;self.path=None;self.win.selection=('chronicle',);self.win.changed(True)
    def render(self):
        old=self.scroll.takeWidget();panel=QWidget();layout=QVBoxLayout(panel);form=QFormLayout();layout.addLayout(form);self.scroll.setWidget(panel)
        if old:old.deleteLater()
        if not self.path:return
        row=self.value();root=self.source()
        def line(label,key,name,rename=False):
            w=QLineEdit(str(row.get(key,'')));w.setObjectName(name)
            def commit():
                def change():
                    if rename and len(self.path)==2:self.win.doc.rename_global(self.path[0],self.path[1],w.text())
                    elif rename:
                        from ..model import identifier
                        identifier(w.text(),'ID',16);old=row[key];coll=self.path[-2]
                        if any(x is not row and x['id']==w.text() for x in root['scenes'][self.path[1]][coll]):raise ValueError('ID duplicado')
                        row[key]=w.text();keys={'encounters':{'spawn_encounter','remove_encounter','encounter'},'sequences':{'play_sequence'},'paths':{'start_patrol','move_path'}}[coll]
                        self.win.doc._replace(root['scenes'][self.path[1]],keys,old,w.text())
                    else:row[key]=w.text()
                return self.win.guard(lambda:self.mutate(change))
            w._rcm_pending=False
            def mark(value): w._rcm_pending=True; self.win._title()
            def safe_commit():
                result=commit();w._rcm_pending=result is False;return result is not False
            w.textChanged.connect(mark);w._rcm_commit=safe_commit
            w.editingFinished.connect(lambda:safe_commit() if w._rcm_pending else True);form.addRow(label,w)
        def combo(label,key,choices,name):
            w=QComboBox();w.setObjectName(name)
            for choice_label,value in choices:w.addItem(choice_label,value)
            def update():
                value=w.currentData()
                def change():
                    if value is None:
                        row.pop(key,None)
                        if key=='move_path':row.pop('move_at',None)
                    else:row[key]=value
                self.mutate(change,True if key=='move_path' else False)
            w.setCurrentIndex(max(0,w.findData(row.get(key))));w.currentIndexChanged.connect(update);form.addRow(label,w)
        line('ID','id','campaign_id',True)
        if self.path[0]=='quests':
            line('Título','title','quest_title');line('Descripción','description','quest_description')
            xp=QSpinBox();xp.setObjectName('quest_reward');xp.setRange(0,1000000);xp.setValue(row.get('reward_xp',0));xp.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('reward_xp',v)));form.addRow('Experiencia al completar',xp)
            for i,step in enumerate(row['steps']):
                w=QLineEdit(step);w.setObjectName('quest_step_'+str(i));w.textChanged.connect(lambda text,i=i:self.mutate(lambda:row['steps'].__setitem__(i,text)));form.addRow('Paso '+str(i+1),w)
            b=QPushButton('+ Paso');b.setObjectName('add_quest_step');b.clicked.connect(lambda:self.mutate(lambda:row['steps'].append('Siguiente objetivo'),True));form.addRow(b)
            b=QPushButton('Quitar último paso');b.setObjectName('delete_quest_step');b.clicked.connect(lambda:self.mutate(lambda:row['steps'].pop() if len(row['steps'])>1 else None,True));form.addRow(b)
            label=QLabel('Los eventos Iniciar / Avanzar / Completar quest controlan este journal nativo. Completar requiere todos los pasos.');label.setWordWrap(True);form.addRow(label)
        elif len(self.path)==2:
            w=QComboBox();w.setObjectName('campaign_entry')
            for s in root['scenes']:w.addItem(s['id'],s['id'])
            w.setCurrentIndex(w.findData(root['entry']));w.currentIndexChanged.connect(lambda:self.mutate(lambda:root.__setitem__('entry',w.currentData())));form.addRow('Entrada',w)
            if root.get('project_format')==9:
                combo('Llegada por defecto','default_entry',[('Entrada original',None)]+[(p['name'],p['id']) for p in row.get('entries',[])],'scene_default_entry')
            label=QLabel('Viaje / Escena y punto de llegada permite elegir una entrada colocada en 3D. El punto sólo mueve al jugador al entrar; cargar una partida conserva su posición.');label.setWordWrap(True);form.addRow(label)
        elif self.path[2]=='encounters':
            line('Nombre','name','encounter_name');lst=QListWidget();lst.setObjectName('encounter_members')
            s=root['scenes'][self.path[1]]
            for a in s['actors']:
                if a.get('behavior')!='enemy':continue
                item=QListWidgetItem(a['name']);item.setData(ROLE,a['id']);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Checked if a['id'] in row['actors'] else Qt.CheckState.Unchecked);lst.addItem(item)
            lst.itemChanged.connect(lambda item:self.mutate(lambda:row.__setitem__('actors',[lst.item(i).data(ROLE) for i in range(lst.count()) if lst.item(i).checkState()==Qt.CheckState.Checked])));form.addRow('Enemigos',lst)
        elif self.path[2]=='sequences':
            line('Nombre','name','sequence_name');s=root['scenes'][self.path[1]]
            combo('Actor enfocado','actor',[(a['name'],a['id']) for a in s['actors']],'sequence_actor')
            combo('Plano','shot',[('Medio','medium'),('Cercano','close'),('Amplio','wide')],'sequence_shot');combo('Ángulo','angle',[('Bajo','low'),('Medio','medium'),('Alto','high')],'sequence_angle')
            if root.get('project_format')==9:
                from ..camera_presets import CINEMA_PRESETS as PRESETS
                combo('Preset narrativo','preset',[('Usar plano simple',None)]+[(v[0],k) for k,v in PRESETS.items()],'sequence_preset')
                combo('Actor en movimiento','move_path',[('Sin movimiento',None)]+[(p['name'],p['id']) for p in s.get('paths',[])],'sequence_move_path')
                if row.get('move_path'):
                    when=QDoubleSpinBox();when.setRange(0,max(0,row['duration']-.1));when.setSuffix(' s');when.setValue(row.get('move_at',0));when.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('move_at',v)));form.addRow('Empieza a caminar',when)
                prop=QComboBox();prop.setObjectName('sequence_moving_prop');prop.addItem('Sin decorado móvil',None)
                for obj in s.get('objects',[]):
                    if obj['transform'].get('placement')=='absolute':prop.addItem(obj['name'],obj['id'])
                prop.setCurrentIndex(prop.findData(row.get('prop_motion',{}).get('object')))
                def choose_prop():
                    def change():
                        value=prop.currentData()
                        if value is None:row.pop('prop_motion',None)
                        else:row['prop_motion']={**row.get('prop_motion',dict(at=0,duration=min(3,row['duration']),translation=[0,0,192])),'object':value};row.pop('camera_path',None);row.setdefault('steps',[dict(at=0,actor=row['actor'],preset=row.get('preset','full'))])
                    self.mutate(change,True)
                prop.currentIndexChanged.connect(choose_prop);form.addRow('Mover decorado',prop)
                if row.get('prop_motion'):
                    motion=row['prop_motion']
                    for key,label in [('at','Apertura empieza'),('duration','Apertura dura')]:
                        value=QDoubleSpinBox();value.setRange(0 if key=='at' else .1,row['duration']);value.setSuffix(' s');value.setValue(motion[key]);value.valueChanged.connect(lambda v,key=key:self.mutate(lambda:motion.__setitem__(key,v)));form.addRow(label,value)
                    axes=QWidget();axisbar=QHBoxLayout(axes);axisbar.setContentsMargins(0,0,0,0)
                    for axis,label in enumerate(['X','Y','Z']):
                        value=QDoubleSpinBox();value.setRange(-10000,10000);value.setPrefix(label+' ');value.setValue(motion['translation'][axis]);value.valueChanged.connect(lambda v,axis=axis:self.mutate(lambda:motion['translation'].__setitem__(axis,v)));axisbar.addWidget(value)
                    form.addRow('Desplazamiento',axes)
                if not row.get('steps'):
                    combo('Travelling original NCP','camera_path',[('Sin recorrido de cámara',None)]+[(e['id'],e['id']) for e in self.win.backend.resources['entries'] if e['extension'].lower()=='.ncp'],'sequence_camera_path')
                if not row.get('camera_path'):
                    def add_shot():
                        def change():
                            steps=row.setdefault('steps',[dict(at=0,actor=row['actor'],preset=row.get('preset','medium'))]);at=steps[-1]['at']+2
                            steps.append(dict(at=at,actor=row['actor'],preset='speaker_close',transition=.3));row['duration']=max(row['duration'],at+2)
                        self.mutate(change,True)
                    b=QPushButton('+ Plano en timeline');b.setObjectName('sequence_add_shot');b.clicked.connect(add_shot);form.addRow(b)
                    for i,step in enumerate(row.get('steps',[])):
                        controls=QWidget();bar=QHBoxLayout(controls);bar.setContentsMargins(0,0,0,0)
                        at=QDoubleSpinBox();at.setRange(0,119.9);at.setSuffix(' s');at.setValue(step['at']);at.setEnabled(i>0);at.valueChanged.connect(lambda v,st=step:self.mutate(lambda:st.__setitem__('at',v)));bar.addWidget(at)
                        actor=QComboBox()
                        for a in s['actors']:actor.addItem(a['name'],a['id'])
                        actor.setCurrentIndex(actor.findData(step['actor']));actor.currentIndexChanged.connect(lambda _,c=actor,st=step:self.mutate(lambda:st.__setitem__('actor',c.currentData())));bar.addWidget(actor)
                        focus=QComboBox();focus.addItem('Enfocar actor',None)
                        for obj in s.get('objects',[]):focus.addItem(obj['name'],obj['id'])
                        focus.setCurrentIndex(focus.findData(step.get('focus')))
                        focus.currentIndexChanged.connect(lambda _,c=focus,st=step:self.mutate(lambda:st.__setitem__('focus',c.currentData()) if c.currentData() else st.pop('focus',None)))
                        preset=QComboBox()
                        for key,value in PRESETS.items():preset.addItem(value[0],key)
                        preset.setCurrentIndex(preset.findData(step['preset']));preset.currentIndexChanged.connect(lambda _,c=preset,st=step:self.mutate(lambda:st.__setitem__('preset',c.currentData())));bar.addWidget(preset)
                        transition=QDoubleSpinBox();transition.setRange(0,10);transition.setValue(step.get('transition',.3));transition.setToolTip('Transición entre planos, segundos');transition.valueChanged.connect(lambda v,st=step:self.mutate(lambda:st.__setitem__('transition',v)));bar.addWidget(transition)
                        if i>0:
                            remove=QPushButton('−');remove.clicked.connect(lambda checked=False,i=i:self.mutate(lambda:row['steps'].pop(i),True));bar.addWidget(remove)
                        form.addRow('Plano '+str(i+1),controls)
                        form.addRow('Enfocar decorado (plano '+str(i+1)+')',focus)
                        angle=QComboBox();angle.setObjectName('sequence_step_angle_'+str(i))
                        for name,key in [('Bajo','low'),('Medio','medium'),('Picado','high')]:angle.addItem(name,key)
                        angle.setCurrentIndex(angle.findData(step.get('angle','medium')))
                        angle.currentIndexChanged.connect(lambda _,c=angle,st=step:self.mutate(lambda:st.__setitem__('angle',c.currentData())))
                        form.addRow('Ángulo (plano '+str(i+1)+')',angle)
            w=QDoubleSpinBox();w.setObjectName('sequence_duration');w.setRange(.1,120);w.setValue(row['duration']);w.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('duration',v)));form.addRow('Duración (s)',w)
            b=QPushButton('Enfocar actor en viewport');b.clicked.connect(lambda:self.preview_sequence(row));form.addRow(b)
            note=QLabel('Los planos y el movimiento se ejecutan con la API del motor. Travelling NCP reutiliza un recorrido original: comprueba que corresponda al escenario. El preview sólo enfoca al actor. Al cargar partida se cancela la cutscene y se devuelve el control.');note.setWordWrap(True);form.addRow(note)
        elif self.path[2]=='paths':
            line('Nombre','name','path_name');s=root['scenes'][self.path[1]]
            combo('Actor','actor',[(a['name'],a['id']) for a in s['actors']],'path_actor')
            combo('Repetir','loop',[('Una vez',False),('Bucle',True)],'path_loop')
            # Ordered list supports repeated waypoints and explicit reordering.
            route=QListWidget();route.setObjectName('path_points');route.setMinimumHeight(100)
            for key in row['points']:route.addItem(key)
            form.addRow('Orden de waypoints',route)
            available=QComboBox();available.setObjectName('path_available')
            for point in s.get('waypoints',[]):available.addItem(point['name'],point['id'])
            form.addRow('Waypoint',available)
            def edit_route(operation):
                operation();self.win.changed(True);self.render()
            b=QPushButton('Añadir waypoint');b.setObjectName('path_add_point');b.clicked.connect(lambda:edit_route(lambda:row['points'].append(available.currentData())) if available.currentData() else None);form.addRow(b)
            def move(delta):
                i=route.currentRow();j=i+delta
                if i>=0 and 0<=j<len(row['points']):row['points'][i],row['points'][j]=row['points'][j],row['points'][i]
            for title,delta in [('Subir',-1),('Bajar',1)]:
                b=QPushButton(title);b.clicked.connect(lambda checked=False,d=delta:edit_route(lambda:move(d)));form.addRow(b)
            b=QPushButton('Quitar waypoint');b.clicked.connect(lambda:edit_route(lambda:row['points'].pop(route.currentRow())) if route.currentRow()>=0 else None);form.addRow(b)
            for label,key,lo,hi,default in [('Tolerancia de llegada','tolerance',1,256,24),('Parámetro de movimiento','speed',1,1000,90)]:
                w=QDoubleSpinBox();w.setObjectName('path_'+key);w.setRange(lo,hi);w.setValue(row.get(key,default));w.valueChanged.connect(lambda v,k=key:self.mutate(lambda:row.__setitem__(k,v)));form.addRow(label,w)
            form.addRow(QLabel('Usa Iniciar / Detener recorrido en un evento. Navegación, colisiones y velocidad pendientes de prueba manual en Redemption.'))
        layout.addStretch()
    def preview_sequence(self,row):
        for i,a in enumerate(self.win.doc.data['actors']):
            if a['id']==row['actor']:self.win.select(('actors',i));self.win.center_tabs.setCurrentIndex(0);self.win.spatial.viewport.focus_selection();return
    def game_settings(self):
        path=QFileDialog.getExistingDirectory(self,'Instalación de Redemption',str(self.win.backend.ws.game))
        if path:
            from ..deployment import save_settings
            baseline=self.win.backend.ws.output('research/source_manifest.json')
            if baseline.is_file():
                from ..catalogue import verify_sources
                verify_sources(self.win.backend.ws,Path(path))
            save_settings(self.win.backend.ws,Path(path));self.win.backend.ws.game=Path(path)
    def deploy(self):
        if not self.win.doc:raise ValueError('Abre una crónica')
        if not self.win.commit_properties():return
        from ..deployment import deploy
        from ..shortcut import launch_info
        info=launch_info(self.win.backend.ws)
        result=deploy(self.win.backend.ws,self.win.doc.data['chronicle']['id'],directory=info['relative'] if info else None,current_source=self.win.doc.snapshot());self.win.log.appendPlainText('Deploy verificado: '+str(result['destination']))
    def game_shortcut(self):
        path,_=QFileDialog.getOpenFileName(self,'Acceso directo que utilizas para jugar','','Accesos Windows (*.lnk)')
        if not path:return
        from ..shortcut import read_shortcut
        read_shortcut(path)
        from ..startup import settings
        import json
        data=settings(self.win.backend.ws);data['installation']=str(self.win.backend.ws.game);data['desktop_shortcut']=path;self.win.backend.ws.write('cache/game_settings.json',json.dumps(data,indent=2))
    def run_game(self):
        if not self.win.doc:raise ValueError('Abre una crónica')
        from ..deployment import run_game
        run_game(self.win.backend.ws,self.win.doc.data['chronicle']['id'])


def event_properties(ins):
    w=ins.win;p=ins.path;e=w.doc.data['events'][p[1]];s=w.doc.campaign['scenes'][w.doc.active]
    if len(p)==2:
        ins.line('ID',e.get('id',''),ins.rename_event,'event_id',True)
        def when(v):
            e['when']=v
            for k in ['actor','conversation','trigger','item','encounter','sequence','result','seconds']:e.pop(k,None)
            fk={'actor_clicked':('actor','actors'),'actor_killed':('actor','actors'),'conversation_ended':('conversation','conversations'),'trigger_enter':('trigger','triggers'),'trigger_leave':('trigger','triggers'),'item_picked_up':('item','objects'),'encounter_complete':('encounter','encounters'),'sequence_ended':('sequence','sequences')}.get(v)
            if fk:e[fk[0]]=next((x['id'] for x in s.get(fk[1],[])),'')
            if v=='timer':e['seconds']=1.0
            w.changed(True)
        ins.combo('CUANDO',[(label,key) for key,label in WHEN.items()],e['when'],when,'event_when')
        fk={'actor_clicked':('actor','actors'),'actor_killed':('actor','actors'),'conversation_ended':('conversation','conversations'),'trigger_enter':('trigger','triggers'),'trigger_leave':('trigger','triggers'),'item_picked_up':('item','objects'),'encounter_complete':('encounter','encounters'),'sequence_ended':('sequence','sequences')}.get(e['when'])
        if fk:ins.combo('Origen',[(x.get('name',x['id']),x['id']) for x in s.get(fk[1],[])],e.get(fk[0],''),lambda v:ins.set(p+(fk[0],),v),'event_'+fk[0])
        if e['when']=='conversation_ended':ins.spin('RETURN (0 = cualquiera)',e.get('result',0),lambda v:ins.set(p+('result',),v if v else None,True),'event_result')
        if e['when']=='timer':ins.spin('Segundos',e.get('seconds',1),lambda v:ins.set(p+('seconds',),v),'event_seconds',True,.15,86400)
        ins.combo('Repetición',[('Cada vez',False),('Una sola vez',True)],e.get('once',e['when'] in {'actor_killed','item_picked_up','encounter_complete','timer','state_changed'}),lambda v:ins.set(p+('once',),v),'event_once')
        ins.note('Las condiciones de la lista se combinan con AND; cada grupo puede usar ALL, ANY o NOT. Eventos de estado, muerte, pickup, encuentro y timer se ejecutan una vez por defecto.')
    elif p[-2]=='actions':
        a=w.at(p);kind=next(iter(a),'spawn')
        def change(v):a.clear();a[v]={'resource':'','waypoint':'','volume':100,'min_distance':128,'max_distance':512} if v=='play_sound' else {'cast_id':'','mode':'frames','frame':1,'parameter':150,'open':True} if v=='control_door' else {'scene':'','entry':''} if v=='travel' else True if ACTIONS[v][1]=='none' else 100 if ACTIONS[v][1]=='number' else '';w.changed(True)
        advanced={'travel','start_patrol','stop_patrol','open_exit','close_exit','control_door','play_sound'}
        ins.combo('Acción',[(label,key) for key,(label,_) in ACTIONS.items() if w.doc.campaign.get('project_format')==9 or key not in advanced],kind,change,'action_kind');category=ACTIONS.get(kind,('','none'))[1]
        if category=='arrival':
            value=a[kind]
            def destination(v):value['scene']=v;value['entry']='';w.changed(True)
            ins.combo('Escena destino',[('Elige…','')]+[(row['id']+' · '+row['level']['source'],row['id']) for row in w.doc.campaign['scenes']],value['scene'],destination,'travel_scene')
            target=next((row for row in w.doc.campaign['scenes'] if row['id']==value['scene']),{})
            ins.combo('Entrada destino',[('Elige…','')]+[(row['name'],row['id']) for row in target.get('entries',[])],value['entry'],lambda v:ins.set(p+(kind,'entry'),v),'travel_entry')
        elif category=='spatial_sound':
            value=a[kind]
            from collections import Counter
            sounds=[r['id'] for r in w.backend.resources['entries'] if r['extension'].lower()=='.wav'];counts=Counter(sounds)
            ins.combo('Sonido',[('Elige…','')]+[(key,key) for key in sorted(counts) if counts[key]==1],value['resource'],lambda v:ins.set(p+(kind,'resource'),v),'sound_resource')
            ins.combo('Posición',[('Elige…','')]+[(r['name'],r['id']) for r in s.get('waypoints',[])],value['waypoint'],lambda v:ins.set(p+(kind,'waypoint'),v),'sound_waypoint')
            for label,key,hi in [('Volumen','volume',100),('Radio interior','min_distance',100000),('Radio exterior','max_distance',100000)]:
                ins.spin(label,value[key],lambda v,k=key:ins.set(p+(kind,k),v),'sound_'+key,key!='volume',0,hi)
            ins.note('Reproducción única situada. El ambient continuo sigue siendo el de la escena; no se ofrece un loop espacial persistente sin contrato de restauración contrastado.')
        elif category=='door':
            value=a[kind]
            ins.line('Cast ID existente',value['cast_id'],lambda v:ins.set(p+(kind,'cast_id'),v),'door_cast_id',True)
            ins.combo('Movimiento',[('Frames / traslación','frames'),('Pivote / rotación','pivot')],value['mode'],lambda v:ins.set(p+(kind,'mode'),v),'door_mode')
            ins.spin('Frame destino',value['frame'],lambda v:ins.set(p+(kind,'frame'),v),'door_frame',maximum=255)
            ins.spin('Parámetro (frames: velocidad; pivote: duración)',value['parameter'],lambda v:ins.set(p+(kind,'parameter'),v),'door_parameter',True,.001,1000)
            ins.combo('Dirección del pivote',[('Abrir',True),('Cerrar',False)],value['open'],lambda v:ins.set(p+(kind,'open'),v),'door_open')
            ins.note('Experimental: requiere Cast ID y frames originales válidos. No sustituye su script de clic ni implementa bloqueo con llave. En frames, cerrar suele usar frame 0 y abrir frame 1; debes comprobarlo en el recurso elegido.')
        elif category=='native_exit':
            ins.line('Cast ID de salida original',a[kind],lambda v:ins.set(p+(kind,),v),'exit_cast_id',True)
            ins.note('Se comprueba IsExitValid al ejecutar. Esta acción no crea geometría ni cambia el script de una puerta.')
        elif category=='number':ins.spin('Experiencia',a[kind],lambda v:ins.set(p+(kind,),v),'action_amount',maximum=1000000)
        elif category!='none':
            if category=='flags':choices=ins.flags()
            elif category=='entity':choices=ins.ids('actors')+ins.ids('objects')
            elif category in {'item','item_global'}:
                templates={t['id']:t['kind'] for t in w.backend.resources['templates']}
                choices=[(o['name'],o['id']) for o in s.get('objects',[]) if templates.get(o['template']) in {'items','weapons','armour'}]
                if category=='item_global': choices += [(sc['id']+' / '+o['name'],sc['id']+'.'+o['id']) for sc in w.doc.campaign['scenes'] for o in sc.get('objects',[]) if templates.get(o['template']) in {'items','weapons','armour'}]
            elif category in {'music','ambient'}:choices=[(r['id'],r['id']) for r in w.backend.resources['entries'] if r['path'].lower().startswith('sounds/'+('stereoambient' if category=='ambient' else category)+'/')]
            elif category in {'quests','scenes'}:choices=[(r.get('title',r['id']),r['id']) for r in w.doc.campaign.get(category,[])]
            else:choices=[(r.get('name',r['id']),r['id']) for r in s.get(category,[])]
            ins.combo('Objetivo',[('Elige…','')]+choices,a.get(kind,''),lambda v:ins.set(p+(kind,),v),'action_target')
    elif p[-2]=='conditions':render_condition(ins,w.at(p),p)


def render_condition(ins,c,path,depth=0):
    w=ins.win;kind=next(iter(c),'flag');kind='quest_step' if 'step' in c else 'quest_state' if 'quest' in c else kind
    flags=ins.flags();firstflag=flags[0][1] if flags else ''
    def change(v):
        c.clear()
        if v in ('all','any'):c[v]=[{'flag':firstflag,'is_set':True}]
        elif v=='not':c[v]={'flag':firstflag,'is_set':True}
        elif v=='flag':c.update(flag=firstflag,is_set=True)
        elif v in ('quest_state','quest_step'):c.update(quest='',**({'state':'active'} if v=='quest_state' else {'step':0}))
        else:c[v]=''
        w.changed(True)
    suffix='_'.join(map(str,path[2:]));ins.combo('SI' if depth==0 else '  '*depth+'Condición',[(x,x) for x in ['flag','quest_state','quest_step','actor_alive','entity_exists','owns_item','all','any','not']],kind,change,'condition_type_'+suffix)
    if kind=='flag':
        ins.combo('Flag',flags,c.get('flag',''),lambda v:ins.set(path+('flag',),v),'condition_flag'+('' if depth==0 else suffix));ins.combo('Estado',[('Activado',True),('Desactivado',False)],c.get('is_set',True),lambda v:ins.set(path+('is_set',),v),'condition_state'+('' if depth==0 else suffix))
    elif kind.startswith('quest'):
        ins.combo('Quest',[('Elige…','')]+[(q['title'],q['id']) for q in w.doc.campaign.get('quests',[])],c.get('quest',''),lambda v:ins.set(path+('quest',),v),'condition_quest')
        if kind=='quest_state':ins.combo('Estado',[('Sin iniciar','not_started'),('Activa','active'),('Completa','complete')],c.get('state','active'),lambda v:ins.set(path+('state',),v),'condition_quest_state')
        else:ins.spin('Paso activo (desde 0)',c.get('step',0),lambda v:ins.set(path+('step',),v),'condition_quest_step',maximum=31)
    elif kind in ('all','any','not'):
        children=[c['not']] if kind=='not' else c[kind]
        for i,child in enumerate(children):render_condition(ins,child,path+(kind,) if kind=='not' else path+(kind,i),depth+1)
        if kind!='not':
            ins.button('+ Condición en grupo',lambda:(c[kind].append({'flag':firstflag,'is_set':True}),w.changed(True)),'condition_add_'+suffix)
            if len(children)>1:ins.button('Quitar última condición',lambda:(c[kind].pop(),w.changed(True)),'condition_remove_'+suffix)
    else:
        choices=ins.ids('actors') if kind=='actor_alive' else ins.ids('objects') if kind=='owns_item' else ins.ids('actors')+ins.ids('objects')
        if kind=='owns_item':
            templates={t['id']:t['kind'] for t in w.backend.resources['templates']}
            choices += [(sc['id']+' / '+o['name'],sc['id']+'.'+o['id']) for sc in w.doc.campaign['scenes'] for o in sc.get('objects',[]) if templates.get(o['template']) in {'items','weapons','armour'}]
        ins.combo('Entidad',[('Elige…','')]+choices,c.get(kind,''),lambda v:ins.set(path+(kind,),v),'condition_entity')

class InventoryDialog(QDialog):
    """Stage catalogue additions until Apply; each item has one creation owner."""
    def __init__(self,win,actor):
        super().__init__(win);self.win=win;self.actor=actor;self.additions=[];self.selected_ids=list(actor.get('inventory',[]))
        self.setWindowTitle('Inventario inicial · '+actor['name']);self.resize(760,520)
        layout=QVBoxLayout(self);layout.addWidget(QLabel('Añade directamente del catálogo; cada copia es un objeto independiente.'))
        bar=QHBoxLayout();add=QPushButton('+ Del catálogo…');add.setObjectName('inventory_add');add.clicked.connect(self.add_catalogue)
        remove=QPushButton('Quitar del inventario');remove.setObjectName('inventory_remove');remove.clicked.connect(self.remove_selected)
        bar.addWidget(add);bar.addWidget(remove);bar.addStretch();layout.addLayout(bar)
        self.items=QListWidget();self.items.setObjectName('inventory_items');layout.addWidget(self.items,1)
        reuse=QHBoxLayout();self.existing=QComboBox();self.existing.setObjectName('inventory_existing');reuse.addWidget(self.existing,1)
        b=QPushButton('Añadir objeto existente');b.clicked.connect(self.add_existing);reuse.addWidget(b);layout.addLayout(reuse)
        note=QLabel('Se crean dentro del NPC, sin colocarlos también en el suelo. Los objetos de otros inventarios o con spawn no se ofrecen. Aplicar conserva una única operación que puedes deshacer.');note.setWordWrap(True);layout.addWidget(note)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Apply).setObjectName('apply_inventory');buttons.button(QDialogButtonBox.StandardButton.Apply).setText('Aplicar');buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons);self.refresh()

    def refresh(self):
        scene=self.win.doc.data;objects=scene.get('objects',[])+self.additions;by_id={o['id']:o for o in objects}
        self.items.clear()
        for ident in self.selected_ids:
            row=by_id[ident];item=QListWidgetItem(row['name']+' · '+row['template']);item.setData(ROLE,ident);item.setToolTip(row['name']+'\nID: '+ident+'\nPlantilla: '+row['template']);self.items.addItem(item)
        used={x for a in scene['actors'] if a is not self.actor for x in a.get('inventory',[])}|{ac['spawn'] for ev in scene['events'] for ac in ev['actions'] if 'spawn' in ac}
        kinds={t['id']:t['kind'] for t in self.win.backend.resources['templates']};self.existing.clear()
        for row in scene.get('objects',[]):
            if row['id'] not in used|set(self.selected_ids) and kinds.get(row['template']) in {'items','weapons','armour'}:self.existing.addItem(row['name']+' · '+row['template'],row['id'])

    def add_catalogue(self):
        dialog=ResourceDialog(self.win.backend,'items',self);dialog.browser.allowed_families={'items','weapons','armour'};dialog.browser.refresh()
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        ids={e['id'] for k in ('actors','objects') for e in self.win.doc.data.get(k,[])}|{o['id'] for o in self.additions};i=1
        while 'inv'+str(i) in ids:i+=1
        ident='inv'+str(i);self.additions.append(dict(id=ident,name=dialog.selection,template=dialog.selection,transform=dict(placement='absolute',position=[0,0,0],orientation=[0,0,0])))
        self.selected_ids.append(ident);self.refresh()

    def add_existing(self):
        ident=self.existing.currentData()
        if ident:self.selected_ids.append(ident);self.refresh()

    def remove_selected(self):
        item=self.items.currentItem()
        if item:self.selected_ids.remove(item.data(ROLE));self.refresh()

    def apply(self):
        self.win.history_time=0
        self.win.doc.data.setdefault('objects',[]).extend(o for o in self.additions if o['id'] in self.selected_ids)
        self.actor['inventory']=self.selected_ids[:];self.win.changed(True)


def inventory_dialog(win,actor):
    dialog=InventoryDialog(win,actor)
    if dialog.exec()==QDialog.DialogCode.Accepted:dialog.apply()

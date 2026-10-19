from .i18n import tr
"""Campaign authoring controls over the existing window/document and event inspector."""
import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox,QLineEdit,QTreeWidget,QTreeWidgetItem,QScrollArea,QFormLayout,QSpinBox,QDoubleSpinBox,QListWidget,QListWidgetItem,QMessageBox,QDialog,QSplitter,QDialogButtonBox,QInputDialog,QMenu,QLayout
from .browser import ResourceDialog
from ..campaign import ACTIONS,WHEN
from ..actor_traits import catalogue as trait_catalogue
from ..dynamic_targets import choices as dynamic_choices
from ..campaign_document import CampaignDocument

ROLE=Qt.ItemDataRole.UserRole

class CampaignPanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.path=None
        layout=QVBoxLayout(self)
        top=QHBoxLayout();self.scene=QComboBox();self.scene.setObjectName('campaign_scene');self.scene.currentIndexChanged.connect(self.switch_scene)
        top.addWidget(QLabel(tr('Escena activa')));top.addWidget(self.scene,1)
        spatial=QHBoxLayout();story=QHBoxLayout()
        more=QMenu(self)
        from .maps import open_maps
        maps=more.addAction(tr('Mapas y localizaciones…'));maps.setObjectName('edit_maps');maps.triggered.connect(lambda:win.guard(lambda:open_maps(win)))
        for i,(label,name,cb) in enumerate([(tr('Crear campaña'),'convert_campaign',self.convert),(tr('+ Escena'),'add_scene',self.add_scene),(tr('+ Entrada'),'add_entry',lambda:self.add_marker('entries')),(tr('+ Punto de recorrido'),'add_waypoint',lambda:self.add_marker('waypoints')),(tr('+ Recorrido'),'add_path',self.add_path),(tr('+ Misión'),'add_quest',self.add_quest),(tr('+ Encuentro'),'add_encounter',self.add_encounter),(tr('+ Cámara'),'add_sequence',self.add_sequence)]):
            if i in (0,1,2,4):
                button=QPushButton(label);button.setObjectName(name);button.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));spatial.addWidget(button)
                if i==0:self.convert_button=button
            else:
                action=more.addAction(label);action.setObjectName(name);action.triggered.connect(lambda checked=False,cb=cb:win.guard(cb))
        from .dynamic_wizard import open_dynamic
        from .original_objects import use_selected
        original=more.addAction(tr('Objeto original / crear paso…'));original.setObjectName('use_original_object');original.triggered.connect(lambda:win.guard(lambda:use_selected(win)))
        dynamic=QPushButton(tr('+ Encuentro dinámico…'));dynamic.setObjectName('add_dynamic');dynamic.clicked.connect(lambda:win.guard(lambda:open_dynamic(win)));spatial.addWidget(dynamic)
        from .recipe_wizard import open_wizard
        guided=QPushButton(tr('Asistente…'));guided.setObjectName('open_recipe');guided.clicked.connect(lambda:win.guard(lambda:open_wizard(win)));spatial.addWidget(guided)
        extra=QPushButton(tr('Añadir…'));extra.setMenu(more);extra.setObjectName('campaign_add_more');spatial.addWidget(extra)
        layout.addLayout(top);layout.addLayout(spatial);layout.addLayout(story);self.dashboard=QLabel();self.dashboard.setWordWrap(True);layout.addWidget(self.dashboard)
        self.search=QLineEdit();self.search.setObjectName('global_search');self.search.setPlaceholderText(tr('Buscar en toda la crónica · Ctrl+Shift+F'));self.search.textChanged.connect(self.refresh_rows);layout.addWidget(self.search)
        self.panes=QSplitter(Qt.Orientation.Vertical);self.panes.setObjectName('campaign_panes');layout.addWidget(self.panes,1)
        self.tree=QTreeWidget();self.tree.setHeaderLabels([tr('Elemento'),tr('Detalle')]);self.tree.setColumnWidth(0,260);self.tree.setObjectName('campaign_tree');self.tree.itemClicked.connect(self.selected);self.panes.addWidget(self.tree)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.setMinimumHeight(190);self.panes.addWidget(self.scroll)
        self.panes.setStretchFactor(0,1);self.panes.setStretchFactor(1,3);self.panes.setSizes([150,400]);self.panes.setChildrenCollapsible(False)
        bottom=QHBoxLayout()
        for label,name,cb in [(tr('Duplicar'),'duplicate_campaign',self.duplicate),(tr('Borrar'),'delete_campaign',self.delete),(tr('Referencias'),'campaign_references',lambda:win.find_references(self.path))]:
            button=QPushButton(label);button.setObjectName(name);button.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bottom.addWidget(button)
        layout.addLayout(bottom)
    def source(self):return self.win.doc.campaign if self.win.doc and hasattr(self.win.doc,'campaign') else None
    def focus_search(self):
        self.win.center_tabs.setCurrentWidget(self)
        self.search.setFocus()
    def convert(self):
        if not self.win.doc:raise ValueError(tr('Crea primero una crónica y elige su mapa'))
        if not self.win.commit_properties():return False
        if not hasattr(self.win.doc,'campaign'):
            if len(self.win.doc.data['chronicle']['id'])>14:raise ValueError(tr('Acorta el ID de campaña a 14 caracteres'))
            self.win.doc=CampaignDocument.convert(self.win.doc);self.win.selection=('chronicle',);self.win.refresh()
        self.win.center_tabs.setCurrentWidget(self)
        return True
    def refresh(self):
        root=self.source();self.convert_button.setVisible(bool(self.win.doc) and not root);self.scene.blockSignals(True);self.scene.clear()
        if root:
            for s in root['scenes']:self.scene.addItem(s['id']+tr(' · ')+s['level']['source'],s['id'])
            self.scene.setCurrentIndex(self.win.doc.active)
            self.dashboard.setText(root['chronicle']['name']+tr(' · ')+str(len(root['scenes']))+tr(' escenas / ')+str(len({s['level']['source'] for s in root['scenes']}))+tr(' geometrías · ')+str(sum(len(s['actors']) for s in root['scenes']))+tr(' actores · ')+str(len(root.get('quests',[])))+tr(' misiones · ')+str(sum(len(s['events']) for s in root['scenes']))+tr(' eventos'))
        else:self.dashboard.setText(tr('Convierte este proyecto antiguo para trabajar con varias escenas, misiones y encuentros. Se conserva la compatibilidad con su formato.'))
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
            item.setToolTip(0,item.text(0)+('\n'+row['comment'] if row.get('comment') else ''));item.setToolTip(1,detail)
        for qi,q in enumerate(root.get('quests',[])):add(('quests',qi),q,tr('Misión · ')+str(len(q['steps']))+tr(' pasos'))
        for si,s in enumerate(root['scenes']):
            add(('scenes',si),s,tr('Escena · ')+s['level']['source'])
            for k in ['actors','objects','conversations','events','triggers','encounters','sequences','entries','waypoints','paths','generators']:
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
            if len(path)>2 and path[2] not in ['encounters','sequences','paths','generators']:
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
        mode,ok=QInputDialog.getItem(self,tr('Crear escena / layout'),tr('Cada escena tiene sus propios NPC, objetos y eventos. La geometría se reutiliza.'), [tr('Nuevo layout vacío sobre este escenario'),tr('Duplicar layout actual'),tr('Escena sobre otro escenario…')],0,False)
        if not ok:return
        if mode==tr('Escena sobre otro escenario…'):
            dialog=ResourceDialog(self.win.backend,'levels',self)
            if dialog.exec()!=QDialog.DialogCode.Accepted:return
            level={'source':dialog.selection}
        else:level=copy.deepcopy(self.source()['scenes'][self.win.doc.active]['level'])
        root=self.source();existing={s['id'] for s in root['scenes']};i=1
        while 'map'+str(i) in existing:i+=1
        row=copy.deepcopy(root['scenes'][self.win.doc.active]) if mode==tr('Duplicar layout actual') else {'level':level,'actors':[],'objects':[],'conversations':[],'events':[],'triggers':[],'encounters':[],'sequences':[]}
        row['id']='map'+str(i);root['scenes'].append(row)
        self.win.doc.active=len(root['scenes'])-1;self.path=('scenes',self.win.doc.active);self.win.selection=('level',);self.win.changed(True);self.render()
    def add_quest(self):
        if not self.convert():return
        root=self.source();i=1
        while any(q['id']=='quest'+str(i) for q in root['quests']):i+=1
        root['quests'].append({'id':'quest'+str(i),'title':tr('Nueva quest'),'description':tr('Describe la misión'),'steps':[tr('Primer objetivo')],'reward_xp':0})
        self.path=('quests',len(root['quests'])-1);self.win.changed(True);self.render()
    def add_encounter(self):
        if not self.convert():return
        s=self.source()['scenes'][self.win.doc.active];rows=s.setdefault('encounters',[])
        rows.append({'id':self.unique(rows,'encounter'),'name':tr('Nuevo encuentro'),'actors':[]});self.path=('scenes',self.win.doc.active,'encounters',len(rows)-1);self.win.changed(True);self.render()
    def add_sequence(self):
        if not self.convert():return
        s=self.source()['scenes'][self.win.doc.active];rows=s.setdefault('sequences',[])
        rows.append({'id':self.unique(rows,'camera'),'name':tr('Nuevo plano'),'actor':s['actors'][0]['id'] if s['actors'] else '', 'duration':3.0,'shot':'medium','angle':'medium'})
        self.path=('scenes',self.win.doc.active,'sequences',len(rows)-1);self.win.changed(True);self.render()
    def enable_authoring9(self):
        if not self.convert():return False
        root=self.source();root['project_format']=max(9,root.get('project_format',0))
        root.setdefault('resources',{});root.setdefault('metadata',{'version':'0.1.0'});root.setdefault('build_options',{'debug':True})
        for s in root['scenes']:
            for k in ('entries','waypoints','paths'):s.setdefault(k,[])
        return True
    def add_marker(self,kind):
        if self.enable_authoring9():self.win.spatial.begin_place(kind)
    def add_path(self):
        if not self.enable_authoring9():return
        s=self.source()['scenes'][self.win.doc.active];rows=s['paths']
        rows.append(dict(id=self.unique(rows,'path'),name=tr('Nuevo recorrido'),actor=s['actors'][0]['id'] if s['actors'] else '',points=[p['id'] for p in s['waypoints']],loop=False,tolerance=24,speed=90))
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
        if not isinstance(parent,list):raise ValueError(tr('Selecciona una entidad, quest o evento'))
        row=copy.deepcopy(parent[self.path[-1]]);ident=self.unique(parent,'copy')
        if self.path[-2]=='generators':
            from ..product_edit import rewire_generator
            rewire_generator(row,row['id'],ident)
        row['id']=ident
        if self.path[-2]=='actors':
            row.pop('conversation',None);row.pop('inventory',None)
        parent.append(row);self.path=self.path[:-1]+(len(parent)-1,);self.win.changed(True);self.render()
    def delete(self):
        if not self.path:return
        if not self.win.commit_properties():return
        parent=self.source()
        for k in self.path[:-1]:parent=parent[k]
        if self.path[0]=='scenes' and len(self.path)==2 and len(parent)==1:raise ValueError(tr('La campaña necesita una escena'))
        if not isinstance(parent,list):raise ValueError(tr('No se puede borrar esa selección'))
        from .deletion import confirm_delete
        candidate=confirm_delete(self.win,self.path)
        if candidate is None:return
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
                        coll=self.path[-2];identifier(w.text(),'ID',64 if coll=='events' else 16,allow_upper=coll=='events');old=row[key]
                        if any(x is not row and x['id']==w.text() for x in root['scenes'][self.path[1]][coll]):raise ValueError(tr('ID duplicado'))
                        row[key]=w.text();keys={'encounters':{'spawn_encounter','remove_encounter','encounter'},'sequences':{'play_sequence'},'paths':{'start_patrol','move_path'}}[coll]
                        self.win.doc._replace(root['scenes'][self.path[1]],keys,old,w.text())
                        if coll=='sequences':self.win.doc._replace(root['scenes'][self.path[1]],{'sequence'},old,w.text())
                        from ..recipes import rename_references
                        rename_references(root,coll,old,w.text(),root['scenes'][self.path[1]]['id'])
                    else:row[key]=w.text()
                return self.win.guard(lambda:self.mutate(change))
            w._rcm_pending=False
            def mark(value): w._rcm_pending=True; self.win._title()
            def safe_commit():
                if getattr(w,'_rcm_committing',False):return False
                w._rcm_committing=True
                try:
                    result=commit();w._rcm_pending=result is False;return result is not False
                finally:w._rcm_committing=False
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
                    else:
                        row[key]=value
                        if key=='camera_path' and any(e.get('timed') and e['id']==value for e in self.win.backend.resources['entries']):row['path_speed']=1
                self.mutate(change,True if key=='move_path' else False)
            w.setCurrentIndex(max(0,w.findData(row.get(key))));w.currentIndexChanged.connect(update);form.addRow(label,w)
        line('ID','id','campaign_id',True)
        if self.path[0]=='quests':
            line(tr('Título'),'title','quest_title');line(tr('Descripción'),'description','quest_description')
            xp=QSpinBox();xp.setObjectName('quest_reward');xp.setRange(0,1000000);xp.setValue(row.get('reward_xp',0));xp.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('reward_xp',v)));form.addRow(tr('Experiencia al completar'),xp)
            for i,step in enumerate(row['steps']):
                w=QLineEdit(step);w.setObjectName('quest_step_'+str(i));w.textChanged.connect(lambda text,i=i:self.mutate(lambda:row['steps'].__setitem__(i,text)));form.addRow(tr('Paso ')+str(i+1),w)
            b=QPushButton(tr('+ Paso'));b.setObjectName('add_quest_step');b.clicked.connect(lambda:self.mutate(lambda:row['steps'].append(tr('Siguiente objetivo')),True));form.addRow(b)
            b=QPushButton(tr('Quitar último paso'));b.setObjectName('delete_quest_step');b.clicked.connect(lambda:self.mutate(lambda:row['steps'].pop() if len(row['steps'])>1 else None,True));form.addRow(b)
            label=QLabel(tr('Los eventos Iniciar / Avanzar / Completar quest controlan este journal nativo. Completar requiere todos los pasos.'));label.setWordWrap(True);form.addRow(label)
        elif len(self.path)==2:
            w=QComboBox();w.setObjectName('campaign_entry')
            for s in root['scenes']:w.addItem(s['id'],s['id'])
            w.setCurrentIndex(w.findData(root['entry']));w.currentIndexChanged.connect(lambda:self.mutate(lambda:root.__setitem__('entry',w.currentData())));form.addRow(tr('Entrada'),w)
            if root.get('project_format') in (9,10):
                combo(tr('Llegada por defecto'),'default_entry',[(tr('Entrada original'),None)]+[(p['name'],p['id']) for p in row.get('entries',[])],'scene_default_entry')
            label=QLabel(tr('Viaje / Escena y punto de llegada permite elegir una entrada colocada en 3D. El punto sólo mueve al jugador al entrar; cargar una partida conserva su posición.'));label.setWordWrap(True);form.addRow(label)
        elif self.path[2]=='generators':
            from .dynamic_wizard import open_dynamic
            line(tr('Nombre'),'name','dynamic_property_name')
            form.addRow(QLabel(tr('Encuentro dinámico')+tr(' · ')+tr(__import__('rcm.dynamic_encounters',fromlist=['MODES']).MODES.get(row['mode'],row['mode']))))
            b=QPushButton(tr('Editar encuentro dinámico…'));b.setObjectName('edit_dynamic');b.clicked.connect(lambda:open_dynamic(self.win,row['id']));form.addRow(b)
            for wi,wave in enumerate(row['waves']):form.addRow(tr('Oleada ')+str(wi+1),QLabel(', '.join(e['template']+' × '+str(e['count']) for e in wave['groups'])))
        elif self.path[2]=='encounters':
            line(tr('Nombre'),'name','encounter_name');lst=QListWidget();lst.setObjectName('encounter_members')
            s=root['scenes'][self.path[1]]
            for a in s['actors']:
                if a.get('behavior')!='enemy':continue
                item=QListWidgetItem(a['name']);item.setData(ROLE,a['id']);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Checked if a['id'] in row['actors'] else Qt.CheckState.Unchecked);lst.addItem(item)
            lst.itemChanged.connect(lambda item:self.mutate(lambda:row.__setitem__('actors',[lst.item(i).data(ROLE) for i in range(lst.count()) if lst.item(i).checkState()==Qt.CheckState.Checked])));form.addRow(tr('Enemigos'),lst)
        elif self.path[2]=='sequences':
            line(tr('Nombre'),'name','sequence_name');s=root['scenes'][self.path[1]]
            mode=QComboBox();mode.setObjectName('sequence_mode')
            for label,key in [('Plano','shot'),('Secuencia de planos','timeline'),('Travelling','ncp')]:mode.addItem(tr(label),key)
            current_mode='ncp' if row.get('camera_path') else 'timeline' if row.get('steps') else 'shot'
            mode.setCurrentIndex(mode.findData(current_mode));form.addRow(tr('Tipo de cámara'),mode)
            def change_mode():
                selected=mode.currentData()
                if selected==current_mode:return
                if row.get('steps') or row.get('camera_path'):
                    if QMessageBox.question(self,tr('Cambiar tipo de cámara'),tr('Cambiar de tipo sustituye la configuración de planos o travelling. Puedes deshacerlo. ¿Continuar?'))!=QMessageBox.StandardButton.Yes:
                        mode.blockSignals(True);mode.setCurrentIndex(mode.findData(current_mode));mode.blockSignals(False);return
                def change():
                    row.pop('steps',None);row.pop('camera_path',None);row.pop('path_speed',None)
                    if selected=='timeline':row['steps']=[dict(at=0,actor=row['actor'],preset=row.get('preset','full'),transition=0)]
                    if selected=='ncp':row['camera_path']=''
                self.mutate(change,True)
            mode.currentIndexChanged.connect(change_mode)
            combo(tr('Actor enfocado'),'actor',[(tr('Jugador'),'Player')]+[(a['name'],a['id']) for a in s['actors']]+dynamic_choices(s),'sequence_actor')
            combo(tr('Referencia de cámara'),'reference',[(tr('Automática'),None)]+([] if row['actor']=='Player' else [(tr('Jugador'),'Player')])+[(a['name'],a['id']) for a in s['actors'] if a['id']!=row['actor']]+dynamic_choices(s),'sequence_reference')
            combo(tr('Plano'),'shot',[(tr('Medio'),'medium'),(tr('Cercano'),'close'),(tr('Amplio'),'wide')],'sequence_shot');combo(tr('Ángulo'),'angle',[(tr('Bajo'),'low'),(tr('Medio'),'medium'),(tr('Alto'),'high')],'sequence_angle')
            if root.get('project_format') in (9,10):
                from ..camera_presets import CINEMA_PRESETS as PRESETS
                combo(tr('Preset narrativo'),'preset',[(tr('Usar plano simple'),None)]+[(tr(v[0]),k) for k,v in PRESETS.items()],'sequence_preset')
                combo(tr('Actor en movimiento'),'move_path',[(tr('Sin movimiento'),None)]+[(p['name'],p['id']) for p in s.get('paths',[])],'sequence_move_path')
                if row.get('move_path'):
                    when=QDoubleSpinBox();when.setRange(0,max(0,row['duration']-.1));when.setSuffix(' s');when.setValue(row.get('move_at',0));when.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('move_at',v)));form.addRow(tr('Empieza a caminar'),when)
                prop=QComboBox();prop.setObjectName('sequence_moving_prop');prop.addItem(tr('Sin decorado móvil'),None)
                for obj in s.get('objects',[]):
                    if obj['transform'].get('placement')=='absolute':prop.addItem(obj['name'],obj['id'])
                prop.setCurrentIndex(prop.findData(row.get('prop_motion',{}).get('object')))
                def choose_prop():
                    def change():
                        value=prop.currentData()
                        if value is None:row.pop('prop_motion',None)
                        else:row['prop_motion']={**row.get('prop_motion',dict(at=0,duration=min(3,row['duration']),translation=[0,0,192])),'object':value};row.pop('camera_path',None);row.setdefault('steps',[dict(at=0,actor=row['actor'],preset=row.get('preset','full'))])
                    self.mutate(change,True)
                prop.currentIndexChanged.connect(choose_prop);form.addRow(tr('Mover decorado'),prop)
                if row.get('prop_motion'):
                    motion=row['prop_motion']
                    for key,label in [('at',tr('Apertura empieza')),('duration',tr('Apertura dura'))]:
                        value=QDoubleSpinBox();value.setRange(0 if key=='at' else .1,row['duration']);value.setSuffix(' s');value.setValue(motion[key]);value.valueChanged.connect(lambda v,key=key:self.mutate(lambda:motion.__setitem__(key,v)));form.addRow(label,value)
                    axes=QWidget();axisbar=QHBoxLayout(axes);axisbar.setContentsMargins(0,0,0,0)
                    for axis,label in enumerate(['X','Y','Z']):
                        value=QDoubleSpinBox();value.setRange(-10000,10000);value.setPrefix(label+' ');value.setValue(motion['translation'][axis]);value.valueChanged.connect(lambda v,axis=axis:self.mutate(lambda:motion['translation'].__setitem__(axis,v)));axisbar.addWidget(value)
                    form.addRow(tr('Desplazamiento'),axes)
                if not row.get('steps'):
                    combo(tr('Travelling'),'camera_path',[(tr('Sin recorrido de cámara'),None)]+[(tr('Del proyecto')+' · '+e['id'] if e.get('project_owned') else tr('Original')+' · '+e['id'],e['id']) for e in self.win.backend.resources['entries'] if e['extension'].lower()=='.ncp'],'sequence_camera_path')
                    speed=QDoubleSpinBox();speed.setObjectName('sequence_path_speed');speed.setRange(.01,100);speed.setValue(row.get('path_speed',30));speed.setEnabled(not any(e.get('timed') and e['id']==row.get('camera_path') for e in self.win.backend.resources['entries']));speed.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('path_speed',v)));form.addRow(tr('Velocidad del travelling'),speed)
                if current_mode!='ncp':
                    def add_shot():
                        def change():
                            steps=row.setdefault('steps',[dict(at=0,actor=row['actor'],preset=row.get('preset','medium'))]);at=steps[-1]['at']+2
                            steps.append(dict(at=at,actor=row['actor'],preset='speaker_close',transition=.3));row['duration']=max(row['duration'],at+2)
                        self.mutate(change,True)
                    b=QPushButton(tr('+ Plano en timeline'));b.setObjectName('sequence_add_shot');b.clicked.connect(add_shot);form.addRow(b)
                    for i,step in enumerate(row.get('steps',[])):
                        controls=QWidget();bar=QHBoxLayout(controls);bar.setContentsMargins(0,0,0,0)
                        at=QDoubleSpinBox();at.setRange(0,119.9);at.setSuffix(' s');at.setValue(step['at']);at.setEnabled(i>0);at.valueChanged.connect(lambda v,st=step:self.mutate(lambda:st.__setitem__('at',v)));bar.addWidget(at)
                        actor=QComboBox()
                        actor.addItem(tr('Jugador'),'Player')
                        for a in s['actors']:actor.addItem(a['name'],a['id'])
                        for label,key in dynamic_choices(s):actor.addItem(label,key)
                        actor.setCurrentIndex(actor.findData(step['actor']));actor.currentIndexChanged.connect(lambda _,c=actor,st=step:self.mutate(lambda:st.__setitem__('actor',c.currentData())));bar.addWidget(actor)
                        focus=QComboBox();focus.addItem(tr('Enfocar actor'),None)
                        for obj in s.get('objects',[]):focus.addItem(obj['name'],obj['id'])
                        focus.setCurrentIndex(focus.findData(step.get('focus')))
                        focus.currentIndexChanged.connect(lambda _,c=focus,st=step:self.mutate(lambda:st.__setitem__('focus',c.currentData()) if c.currentData() else st.pop('focus',None)))
                        preset=QComboBox()
                        for key,value in PRESETS.items():preset.addItem(tr(value[0]),key)
                        preset.setCurrentIndex(preset.findData(step['preset']));preset.currentIndexChanged.connect(lambda _,c=preset,st=step:self.mutate(lambda:st.__setitem__('preset',c.currentData())));bar.addWidget(preset)
                        transition=QDoubleSpinBox();transition.setRange(0,10);transition.setValue(step.get('transition',.3));transition.setToolTip(tr('Transición entre planos, segundos'));transition.valueChanged.connect(lambda v,st=step:self.mutate(lambda:st.__setitem__('transition',v)));bar.addWidget(transition)
                        if i>0:
                            remove=QPushButton('−');remove.clicked.connect(lambda checked=False,i=i:self.mutate(lambda:row['steps'].pop(i),True));bar.addWidget(remove)
                        form.addRow(tr('Plano ')+str(i+1),controls)
                        reference=QComboBox();reference.setObjectName('sequence_step_reference_'+str(i));reference.addItem(tr('Automática'),None)
                        if step['actor']!='Player':reference.addItem(tr('Jugador'),'Player')
                        for a in s['actors']:
                            if a['id']!=step['actor']:reference.addItem(a['name'],a['id'])
                        for label,key in dynamic_choices(s):reference.addItem(label,key)
                        reference.setCurrentIndex(max(0,reference.findData(step.get('reference'))))
                        reference.currentIndexChanged.connect(lambda _,c=reference,st=step:self.mutate(lambda:st.__setitem__('reference',c.currentData()) if c.currentData() else st.pop('reference',None)))
                        form.addRow(tr('Referencia de cámara'),reference)
                        form.addRow(tr('Enfocar decorado (plano ')+str(i+1)+')',focus)
                        angle=QComboBox();angle.setObjectName('sequence_step_angle_'+str(i))
                        for name,key in [(tr('Bajo'),'low'),(tr('Medio'),'medium'),(tr('Picado'),'high')]:angle.addItem(name,key)
                        angle.setCurrentIndex(angle.findData(step.get('angle','medium')))
                        angle.currentIndexChanged.connect(lambda _,c=angle,st=step:self.mutate(lambda:st.__setitem__('angle',c.currentData())))
                        form.addRow(tr('Ángulo (plano ')+str(i+1)+')',angle)
            w=QDoubleSpinBox();w.setObjectName('sequence_duration');w.setRange(.1,120);w.setValue(row['duration']);w.valueChanged.connect(lambda v:self.mutate(lambda:row.__setitem__('duration',v)));form.addRow(tr('Duración (s)'),w)
            b=QPushButton(tr('Enfocar actor en viewport'));b.clicked.connect(lambda:self.preview_sequence(row));form.addRow(b)
            if root.get('project_format') in (9,10):
                from .director import cue_controls,open_camera_path
                button=QPushButton(tr('Crear / editar travelling propio…'));button.setObjectName('director_camera_path');button.clicked.connect(lambda:open_camera_path(self.win,self.path));form.addRow(button)
                cue_controls(self,form,row)
            note=QLabel(tr('Planos y movimiento usan el motor. El travelling puede ser original o propio: comprueba el encuadre final en Redemption. Las películas con acciones temporales se cancelan al cargar y devuelven el control.'));note.setWordWrap(True);form.addRow(note)
            if row['actor']=='Player' and not row.get('cues'):note.setText(tr('La secuencia presenta al jugador. Usa una referencia de cámara para orientar los planos. Al cargar una partida a mitad, esta película empieza de nuevo y su progreso se completa una sola vez.'))
            # Hide irrelevant camera controls without modifying their stored data.
            for control in panel.findChildren(QComboBox):
                name=control.objectName()
                if name in {'sequence_shot','sequence_angle','sequence_preset'}:form.setRowVisible(control,current_mode=='shot')
                if name=='sequence_camera_path':form.setRowVisible(control,current_mode=='ncp')
        elif self.path[2]=='paths':
            line(tr('Nombre'),'name','path_name');s=root['scenes'][self.path[1]]
            combo(tr('Actor'),'actor',[(a['name'],a['id']) for a in s['actors']]+dynamic_choices(s),'path_actor')
            combo(tr('Repetir'),'loop',[(tr('Una vez'),False),(tr('Bucle'),True)],'path_loop')
            # Ordered list supports repeated waypoints and explicit reordering.
            route=QListWidget();route.setObjectName('path_points');route.setMinimumHeight(100)
            for key in row['points']:route.addItem(key)
            form.addRow(tr('Orden de waypoints'),route)
            available=QComboBox();available.setObjectName('path_available')
            for point in s.get('waypoints',[]):available.addItem(point['name'],point['id'])
            form.addRow(tr('Punto de recorrido'),available)
            def edit_route(operation):
                operation();self.win.changed(True);self.render()
            b=QPushButton(tr('Añadir waypoint'));b.setObjectName('path_add_point');b.clicked.connect(lambda:edit_route(lambda:row['points'].append(available.currentData())) if available.currentData() else None);form.addRow(b)
            def move(delta):
                i=route.currentRow();j=i+delta
                if i>=0 and 0<=j<len(row['points']):row['points'][i],row['points'][j]=row['points'][j],row['points'][i]
            for title,delta in [(tr('Subir'),-1),(tr('Bajar'),1)]:
                b=QPushButton(title);b.clicked.connect(lambda checked=False,d=delta:edit_route(lambda:move(d)));form.addRow(b)
            b=QPushButton(tr('Quitar waypoint'));b.clicked.connect(lambda:edit_route(lambda:row['points'].pop(route.currentRow())) if route.currentRow()>=0 else None);form.addRow(b)
            for label,key,lo,hi,default in [(tr('Tolerancia de llegada'),'tolerance',1,256,24),(tr('Parámetro de movimiento'),'speed',1,1000,90)]:
                w=QDoubleSpinBox();w.setObjectName('path_'+key);w.setRange(lo,hi);w.setValue(row.get(key,default));w.valueChanged.connect(lambda v,k=key:self.mutate(lambda:row.__setitem__(k,v)));form.addRow(label,w)
            form.addRow(QLabel(tr('Usa Iniciar / Detener recorrido en un evento. Navegación, colisiones y velocidad pendientes de prueba manual en Redemption.')))
        layout.addStretch()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        panel.setMinimumHeight(layout.sizeHint().height())
    def preview_sequence(self,row):
        for i,a in enumerate(self.win.doc.data['actors']):
            if a['id']==row['actor']:self.win.select(('actors',i));self.win.center_tabs.setCurrentIndex(0);self.win.spatial.viewport.focus_selection();return


def event_properties(ins):
    w=ins.win;p=ins.path;e=w.doc.data['events'][p[1]];s=w.doc.campaign['scenes'][w.doc.active]
    if len(p)==2:
        ins.line('ID',e.get('id',''),ins.rename_event,'event_id',True)
        def when(v):
            e['when']=v
            for k in ['actor','object','conversation','trigger','item','encounter','sequence','result','seconds','generator','wave','phase']:e.pop(k,None)
            fk={'object_clicked':('object','objects'),'actor_clicked':('actor','actors'),'actor_killed':('actor','actors'),'conversation_ended':('conversation','conversations'),'trigger_enter':('trigger','triggers'),'trigger_leave':('trigger','triggers'),'item_picked_up':('item','objects'),'encounter_complete':('encounter','encounters'),'sequence_ended':('sequence','sequences')}.get(v)
            if fk:e[fk[0]]=next((x['id'] for x in s.get(fk[1],[])),'')
            if v.startswith(('generator_','wave_')):e['generator']=next((g['id'] for g in s.get('generators',[])),'')
            if v=='timer':e['seconds']=1.0
            w.changed(True)
        ins.combo(tr('CUANDO'),[(tr(label),key) for key,label in WHEN.items() if key!='generator_threshold' and (w.doc.campaign.get('project_format')==10 or not key.startswith(('generator_','wave_'))) and (w.doc.campaign.get('project_format') in (9,10) or key not in {'object_clicked','note_closed'})],e['when'],when,'event_when')
        fk={'object_clicked':('object','objects'),'actor_clicked':('actor','actors'),'actor_killed':('actor','actors'),'conversation_ended':('conversation','conversations'),'trigger_enter':('trigger','triggers'),'trigger_leave':('trigger','triggers'),'item_picked_up':('item','objects'),'encounter_complete':('encounter','encounters'),'sequence_ended':('sequence','sequences')}.get(e['when'])
        if fk:ins.combo(tr('Origen'),[(x.get('name',x['id']),x['id']) for x in s.get(fk[1],[])],e.get(fk[0],''),lambda v:ins.set(p+(fk[0],),v),'event_'+fk[0])
        if e['when'].startswith(('generator_','wave_')):
            ins.combo(tr('Encuentro dinámico'),[(g['name'],g['id']) for g in s.get('generators',[])],e.get('generator',''),lambda v:ins.set(p+('generator',),v),'event_generator')
            if e['when'].startswith('wave_'):ins.spin(tr('Oleada (0 = cualquiera)'),e.get('wave',0),lambda v:ins.set(p+('wave',),v if v else None,True),'event_wave',maximum=32)
        if e['when']=='conversation_ended':ins.spin(tr('RETURN (0 = cualquiera)'),e.get('result',0),lambda v:ins.set(p+('result',),v if v else None,True),'event_result')
        if e['when']=='timer':ins.spin(tr('Segundos'),e.get('seconds',1),lambda v:ins.set(p+('seconds',),v),'event_seconds',True,.15,86400)
        ins.combo(tr('Repetición'),[(tr('Cada vez'),False),(tr('Una sola vez'),True)],e.get('once',e['when'] in {'actor_killed','item_picked_up','encounter_complete','timer','state_changed'}),lambda v:ins.set(p+('once',),v),'event_once')
        ins.note(tr('Las condiciones de la lista se combinan con AND; cada grupo puede usar ALL, ANY o NOT. Eventos de estado, muerte, pickup, encuentro y timer se ejecutan una vez por defecto.'))
    elif p[-2]=='actions':
        a=w.at(p);kind=next(iter(a),'spawn')
        def change(v):
            from ..cinematics import DIRECTOR_ACTIONS
            if v=='set_room_type':a.clear();a[v]=0;w.changed(True);return
            if v in ('move_actor','actor_inventory','actor_behavior'):
                a.clear();a[v]=dict(actor='Player',**(dict(waypoint='',speed=90) if v=='move_actor' else dict(item='',operation='give') if v=='actor_inventory' else dict(team=12,paused=False)));w.changed(True);return
            if v=='set_location_flags':a.clear();a[v]=dict(scene=s['id'],visible=True,haven=False);w.changed(True);return
            if v=='push_music':
                a.clear();a[v]=dict(resource=next((r['id'] for r in w.backend.resources['entries'] if r['path'].lower().startswith('sounds/music/') and r['extension'].lower()=='.mp3'),''),volume=50);w.changed(True);return
            if v in DIRECTOR_ACTIONS:
                from .director import default_action
                a.clear();a[v]=default_action(v,s);w.changed(True);return
            a.clear();a[v]={'actor':'Player','clan':trait_catalogue(w.backend.resources)['clans'][0]['id']} if v=='set_actor_clan' else {'actor':'Player','discipline':trait_catalogue(w.backend.resources)['disciplines'][0]['id'],'level':1} if v=='set_discipline' else {'level':s['level']['source'],'template':'','operation':'hide'} if v=='control_original' else {'title':tr('Nota'),'text':tr('Escribe aquí lo que leerá el jugador.')} if v=='show_note' else {'resource':'','waypoint':'','volume':100,'min_distance':128,'max_distance':512} if v=='play_sound' else {'cast_id':'','mode':'frames','frame':1,'parameter':150,'open':True} if v=='control_door' else {'scene':'','entry':''} if v=='travel' else True if ACTIONS[v][1]=='none' else 100 if ACTIONS[v][1]=='number' else '';w.changed(True)
        advanced={'show_note','travel','start_patrol','stop_patrol','open_exit','close_exit','control_door','control_original','play_sound','push_music','pop_music','set_location_flags','set_room_type','move_actor','actor_inventory','actor_behavior'}
        advanced|={'set_actor_clan','set_discipline'}
        from ..cinematics import DIRECTOR_ACTIONS
        advanced|=DIRECTOR_ACTIONS
        ins.combo(tr('Acción'),[(tr(label),key) for key,(label,_) in ACTIONS.items() if (trait_catalogue(w.backend.resources) or key not in {'set_actor_clan','set_discipline'}) and (w.doc.campaign.get('project_format')==10 or not key.endswith('_generator')) and (w.doc.campaign.get('project_format') in (9,10) or key not in advanced)],kind,change,'action_kind');category=ACTIONS.get(kind,('','none'))[1]
        from .director import render_action
        if render_action(ins,kind,a[kind],p,s):pass
        elif category=='room_type':ins.combo(tr('Reverberación EAX'),[(tr('Preset original')+' '+str(i),i) for i in range(26)],a[kind],lambda v:ins.set(p+(kind,),v),'action_room_type')
        elif category in ('actor_move','actor_inventory','actor_behavior'):
            from ..dynamic_targets import choices
            value=a[kind];ins.combo(tr('Actor'),[(tr('Jugador'),'Player')]+ins.ids('actors')+choices(s),value['actor'],lambda v:ins.set(p+(kind,'actor'),v),'control_actor')
            ins.note(tr('Un rol dinámico se resuelve entre los enemigos vivos del encuentro. Si falta, la acción se detiene sin crear sustitutos.'))
            if category=='actor_move':
                ins.combo(tr('Punto'),ins.ids('waypoints'),value['waypoint'],lambda v:ins.set(p+(kind,'waypoint'),v),'control_waypoint');ins.spin(tr('Velocidad'),value['speed'],lambda v:ins.set(p+(kind,'speed'),v),'control_speed',True,1,1000)
            elif category=='actor_inventory':
                templates={r['id']:r['kind'] for r in w.backend.resources['templates']}
                items=[(r['name'],r['id']) for r in s.get('objects',[]) if templates.get(r['template']) in ('items','weapons','armour')]
                ins.combo(tr('Objeto'),items,value['item'],lambda v:ins.set(p+(kind,'item'),v),'control_item');ins.combo(tr('Acción'),[(tr('Dar'),'give'),(tr('Quitar'),'take')],value['operation'],lambda v:ins.set(p+(kind,'operation'),v),'control_inventory')
            else:
                ins.combo(tr('Equipo'),[(tr('Equipo')+' '+str(i),i) for i in range(20)],value['team'],lambda v:ins.set(p+(kind,'team'),v),'control_team');ins.combo(tr('AI pausada'),[(tr('Sí'),True),(tr('No'),False)],value['paused'],lambda v:ins.set(p+(kind,'paused'),v),'control_paused')
        elif category=='map_flags':
            value=a[kind]
            ins.combo(tr('Escena'),[(r['id'],r['id']) for r in w.doc.campaign['scenes']],value['scene'],lambda v:ins.set(p+(kind,'scene'),v),'map_flags_scene')
            for key,label in [('visible','Visible en el mapa'),('haven','Refugio')]:ins.combo(tr(label),[(tr('Sí'),True),(tr('No'),False)],value[key],lambda v,k=key:ins.set(p+(kind,k),v),'map_flags_'+key)
        elif category=='temporary_music':
            ins.combo(tr('Música'),[(r['id'],r['id']) for r in w.backend.resources['entries'] if r['path'].lower().startswith('sounds/music/') and r['extension'].lower()=='.mp3'],a[kind]['resource'],lambda v:ins.set(p+(kind,'resource'),v),'temporary_music_resource')
            ins.spin(tr('Volumen'),a[kind]['volume'],lambda v:ins.set(p+(kind,'volume'),v),'temporary_music_volume',maximum=100)
            ins.note(tr('Restaura la música anterior antes de iniciar otra música temporal. Después de cargar una partida, usa Música normal para elegir la pista. Restaurar no altera una música cambiada por otro evento o script.'))
        elif category in {'wtd_clan','wtd_discipline'}:
            value=a[kind];data=trait_catalogue(w.backend.resources);field='clan' if category=='wtd_clan' else 'discipline'
            ins.combo(tr('Actor'),[(tr('Jugador'),'Player')]+ins.ids('actors')+dynamic_choices(s),value['actor'],lambda v:ins.set(p+(kind,'actor'),v),'trait_actor')
            ins.combo(tr('Clan' if field=='clan' else 'Disciplina'),[(r['id'],r['id']) for r in data.get('clans' if field=='clan' else 'disciplines',[])],value[field],lambda v:ins.set(p+(kind,field),v),'trait_value')
            if field=='discipline':ins.spin(tr('Nivel'),value['level'],lambda v:ins.set(p+(kind,'level'),v),'trait_level',maximum=5)
        elif category=='original':
            from .original_objects import choose_target
            choose_target(ins,p+(kind,),a[kind])
        elif category=='note':
            value=a[kind]
            ins.line(tr('Título'),value['title'],lambda v:ins.set(p+(kind,'title'),v),'note_title')
            control=ins.text(tr('Texto'),value['text'],lambda v:ins.set(p+(kind,'text'),v),'note_text');control.setMaximumHeight(350);control.setMinimumHeight(180)
            ins.note(tr('Ventana del juego para prólogos, cartas y avisos. Separa los párrafos con una línea vacía. Para continuar después, usa el evento «Cierran una nota» y, si hay varias, una condición de flag.'))
        elif category=='arrival':
            value=a[kind]
            def destination(v):value['scene']=v;value['entry']='';w.changed(True)
            ins.combo(tr('Escena destino'),[(tr('Elige…'),'')]+[(row['id']+tr(' · ')+row['level']['source'],row['id']) for row in w.doc.campaign['scenes'] if row['id']!=s['id']],value['scene'],destination,'travel_scene')
            ins.note(tr('El destino debe ser otra escena. Para cambiar un layout, crea otra escena que reutilice el mismo level.'))
            target=next((row for row in w.doc.campaign['scenes'] if row['id']==value['scene']),{})
            ins.combo(tr('Entrada destino'),[(tr('Elige…'),'')]+[(row['name'],row['id']) for row in target.get('entries',[])],value['entry'],lambda v:ins.set(p+(kind,'entry'),v),'travel_entry')
        elif category=='spatial_sound':
            value=a[kind]
            from collections import Counter
            sounds=[r['id'] for r in w.backend.resources['entries'] if r['extension'].lower()=='.wav'];counts=Counter(sounds)
            ins.combo(tr('Sonido'),[(tr('Elige…'),'')]+[(key,key) for key in sorted(counts) if counts[key]==1],value['resource'],lambda v:ins.set(p+(kind,'resource'),v),'sound_resource')
            def sound_source(field):
                value.pop('actor',None);value.pop('waypoint',None);value[field]='Player' if field=='actor' else '';w.changed(True)
            ins.combo(tr('Origen'),[(tr('Punto'),'waypoint'),(tr('Actor'),'actor')],'actor' if 'actor' in value else 'waypoint',sound_source,'sound_source_kind')
            if 'actor' in value:ins.combo(tr('Actor'),[(tr('Jugador'),'Player')]+ins.ids('actors')+dynamic_choices(s),value['actor'],lambda v:ins.set(p+(kind,'actor'),v),'sound_actor')
            else:ins.combo(tr('Posición'),[(tr('Elige…'),'')]+[(r['name'],r['id']) for r in s.get('waypoints',[])],value.get('waypoint',''),lambda v:ins.set(p+(kind,'waypoint'),v),'sound_waypoint')
            for label,key,hi in [(tr('Volumen'),'volume',100),(tr('Radio interior'),'min_distance',100000),(tr('Radio exterior'),'max_distance',100000)]:
                ins.spin(label,value[key],lambda v,k=key:ins.set(p+(kind,k),v),'sound_'+key,key!='volume',0,hi)
            def loop(v):
                if v:value['loop']=True;value.setdefault('id','sound_loop')
                else:value.pop('loop',None);value.pop('id',None)
                w.changed(True)
            ins.combo(tr('Reproducción'),[(tr('Una vez'),False),(tr('Bucle mientras escena activa'),True)],value.get('loop',False),loop,'sound_loop')
            if value.get('loop'):
                def rename_loop(v):
                    from ..audio import rename_loop as rename
                    rename(s,value['id'],v);w.changed(False)
                ins.line(tr('Nombre del sonido'),value['id'],rename_loop,'sound_source_id',True)
        elif category=='sound_source':
            from ..audio import loops
            ins.combo(tr('Sonido'),[(name,name) for name in loops(s)],a[kind],lambda v:ins.set(p+(kind,),v),'sound_stop_source')
        elif category=='door':
            value=a[kind]
            ins.line(tr('Cast ID existente'),value['cast_id'],lambda v:ins.set(p+(kind,'cast_id'),v),'door_cast_id',True)
            ins.combo(tr('Movimiento'),[(tr('Frames / traslación'),'frames'),(tr('Pivote / rotación'),'pivot')],value['mode'],lambda v:ins.set(p+(kind,'mode'),v),'door_mode')
            ins.spin(tr('Frame destino'),value['frame'],lambda v:ins.set(p+(kind,'frame'),v),'door_frame',maximum=255)
            ins.spin(tr('Parámetro (frames: velocidad; pivote: duración)'),value['parameter'],lambda v:ins.set(p+(kind,'parameter'),v),'door_parameter',True,.001,1000)
            ins.combo(tr('Dirección del pivote'),[(tr('Abrir'),True),(tr('Cerrar'),False)],value['open'],lambda v:ins.set(p+(kind,'open'),v),'door_open')
            ins.note(tr('Experimental: requiere Cast ID y frames originales válidos. No sustituye su script de clic ni implementa bloqueo con llave. En frames, cerrar suele usar frame 0 y abrir frame 1; debes comprobarlo en el recurso elegido.'))
        elif category=='native_exit':
            ins.line(tr('Cast ID de salida original'),a[kind],lambda v:ins.set(p+(kind,),v),'exit_cast_id',True)
            ins.note(tr('Se comprueba IsExitValid al ejecutar. Esta acción no crea geometría ni cambia el script de una puerta.'))
        elif category=='number':ins.spin(tr('Experiencia'),a[kind],lambda v:ins.set(p+(kind,),v),'action_amount',maximum=1000000)
        elif category!='none':
            if category=='flags':choices=ins.flags()
            elif category=='entity':choices=ins.ids('actors')+ins.ids('objects')
            elif category in {'item','item_global'}:
                templates={t['id']:t['kind'] for t in w.backend.resources['templates']}
                choices=[(o['name'],o['id']) for o in s.get('objects',[]) if templates.get(o['template']) in {'items','weapons','armour'}]
                if category=='item_global': choices += [(sc['id']+' / '+o['name'],sc['id']+'.'+o['id']) for sc in w.doc.campaign['scenes'] for o in sc.get('objects',[]) if templates.get(o['template']) in {'items','weapons','armour'}]
            elif category in {'music','ambient'}:choices=[(r['id'],r['id']) for r in w.backend.resources['entries'] if r['path'].lower().startswith('sounds/'+('stereoambient' if category=='ambient' else category)+'/')]
            elif category in {'quests','scenes'}:choices=[(r.get('title',r['id']),r['id']) for r in w.doc.campaign.get(category,[]) if category!='scenes' or r['id']!=s['id']]
            else:choices=[(r.get('name',r['id']),r['id']) for r in s.get(category,[])]
            if category=='actors':
                choices+=dynamic_choices(s)
            ins.combo(tr('Objetivo'),[(tr('Elige…'),'')]+choices,a.get(kind,''),lambda v:ins.set(p+(kind,),v),'action_target')
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
        elif v=='actor_health':c[v]={'actor':'','comparison':'<=','percent':50}
        elif v=='actor_owns_item':c[v]=dict(actor='Player',item='')
        elif v=='generator_count':c[v]={'generator':'','counter':'alive','comparison':'<=','value':1}
        elif v=='generator_state':c[v]={'generator':'','state':'complete'}
        else:c[v]=''
        w.changed(True)
    suffix='_'.join(map(str,path[2:]));options=[(x,x) for x in ['flag','quest_state','quest_step','actor_alive','entity_exists','owns_item','all','any','not']]+[(tr('Localización descubierta'),'location_visible'),(tr('Objeto en inventario de actor'),'actor_owns_item')]
    if w.doc.campaign.get('project_format')==10:options += [(tr('Vida del actor'),'actor_health'),(tr('Enemigos vivos / muertos'),'generator_count'),(tr('Estado del encuentro dinámico'),'generator_state')]
    ins.combo(tr('SI') if depth==0 else '  '*depth+tr('Condición'),options,kind,change,'condition_type_'+suffix)
    if kind=='flag':
        ins.combo('Flag',flags,c.get('flag',''),lambda v:ins.set(path+('flag',),v),'condition_flag'+('' if depth==0 else suffix));ins.combo(tr('Estado'),[(tr('Activado'),True),(tr('Desactivado'),False)],c.get('is_set',True),lambda v:ins.set(path+('is_set',),v),'condition_state'+('' if depth==0 else suffix))
    elif kind.startswith('quest'):
        ins.combo(tr('Misión'),[(tr('Elige…'),'')]+[(q['title'],q['id']) for q in w.doc.campaign.get('quests',[])],c.get('quest',''),lambda v:ins.set(path+('quest',),v),'condition_quest')
        if kind=='quest_state':ins.combo(tr('Estado'),[(tr('Sin iniciar'),'not_started'),(tr('Activa'),'active'),(tr('Completa'),'complete')],c.get('state','active'),lambda v:ins.set(path+('state',),v),'condition_quest_state')
        else:ins.spin(tr('Paso activo (desde 0)'),c.get('step',0),lambda v:ins.set(path+('step',),v),'condition_quest_step',maximum=31)
    elif kind in {'actor_health','generator_state','generator_count'}:
        render_dynamic_condition(ins,c,path)
    elif kind=='location_visible':ins.combo(tr('Escena'),[(s['id'],s['id']) for s in w.doc.campaign['scenes']],c[kind],lambda v:ins.set(path+(kind,),v),'condition_location')
    elif kind=='actor_owns_item':
        value=c[kind];scene=w.doc.campaign['scenes'][w.doc.active];templates={t['id']:t['kind'] for t in w.backend.resources['templates']}
        ins.combo(tr('Actor'),[(tr('Jugador'),'Player')]+ins.ids('actors')+dynamic_choices(scene),value['actor'],lambda v:ins.set(path+(kind,'actor'),v),'condition_inventory_actor')
        ins.combo(tr('Objeto'),[(r['name'],r['id']) for r in scene.get('objects',[]) if templates.get(r['template']) in ('items','weapons','armour')],value['item'],lambda v:ins.set(path+(kind,'item'),v),'condition_inventory_item')
    elif kind in ('all','any','not'):
        children=[c['not']] if kind=='not' else c[kind]
        for i,child in enumerate(children):render_condition(ins,child,path+(kind,) if kind=='not' else path+(kind,i),depth+1)
        if kind!='not':
            ins.button(tr('+ Condición en grupo'),lambda:(c[kind].append({'flag':firstflag,'is_set':True}),w.changed(True)),'condition_add_'+suffix)
            if len(children)>1:ins.button(tr('Quitar última condición'),lambda:(c[kind].pop(),w.changed(True)),'condition_remove_'+suffix)
    else:
        choices=ins.ids('actors') if kind=='actor_alive' else ins.ids('objects') if kind=='owns_item' else ins.ids('actors')+ins.ids('objects')
        if kind in ('actor_alive','entity_exists'):choices+=dynamic_choices(w.doc.campaign['scenes'][w.doc.active])
        if kind=='owns_item':
            templates={t['id']:t['kind'] for t in w.backend.resources['templates']}
            choices += [(sc['id']+' / '+o['name'],sc['id']+'.'+o['id']) for sc in w.doc.campaign['scenes'] for o in sc.get('objects',[]) if templates.get(o['template']) in {'items','weapons','armour'}]
        ins.combo(tr('Entidad'),[(tr('Elige…'),'')]+choices,c.get(kind,''),lambda v:ins.set(path+(kind,),v),'condition_entity')

def render_dynamic_condition(ins,c,path):
    from ..dynamic_encounters import MODES,unique_health_role
    kind=next(iter(c));value=c[kind];w=ins.win;s=w.doc.campaign['scenes'][w.doc.active];prefix=path+(kind,)
    generators=s.get('generators',[]);choices=[(tr('Elige…'),'')]+[(g['name']+' · '+tr(MODES[g['mode']]),g['id']) for g in generators]
    if kind=='actor_health':
        targets=[(a['name'],'actor:'+a['id']) for a in s['actors']]
        for g in generators:
            roles={e['role']:sum(e2['count'] for wave in g['waves'] for e2 in wave['groups'] if e2['role']==e['role']) for wave in g['waves'] for e in wave['groups']}
            targets += [(g['name']+' / '+role,'role:'+g['id']+'/'+role) for role in roles if unique_health_role(g,role)]
        selected='actor:'+value['actor'] if 'actor' in value else 'role:'+value.get('generator','')+'/'+value.get('role','')
        def target(key):
            for k in ('actor','generator','role'):value.pop(k,None)
            if key.startswith('actor:'):value['actor']=key[6:]
            elif key.startswith('role:'):value['generator'],value['role']=key[5:].split('/',1)
            else:value['actor']=''
            w.changed(True)
        ins.combo(tr('Actor o jefe generado'),[(tr('Elige…'),'')]+targets,selected,target,'health_target')
        unit='percent' if 'percent' in value else 'value'
        def units(key):
            old=value.pop('percent',value.get('value',50));value.pop('value',None);value[key]=min(old,100) if key=='percent' else old;w.changed(True)
        ins.combo(tr('Medida'),[(tr('Porcentaje'),'percent'),(tr('Puntos de vida'),'value')],unit,units,'health_unit')
        ins.spin(tr('Vida'),value.get(unit,50),lambda v:ins.set(prefix+(unit,),v),'health_threshold',True,0,100 if unit=='percent' else 1000000)
        ins.note(tr('La condición se comprueba por muestreo. Las fases del jefe detectan cruces; no garantizan actuar antes de un golpe mortal.'))
    else:
        ins.combo(tr('Encuentro dinámico'),choices,value.get('generator',''),lambda v:ins.set(prefix+('generator',),v),'condition_generator')
        if kind=='generator_state':
            ins.combo(tr('Estado'),[(tr(label),key) for label,key in [('Sin iniciar','ready'),('Activo','active'),('Pausado','paused'),('Completo','complete'),('Detenido','stopped'),('Error','error')]],value.get('state','complete'),lambda v:ins.set(prefix+('state',),v),'generator_condition_state');return
        ins.combo(tr('Contador'),[(tr(label),key) for label,key in [('Vivos','alive'),('Muertos','killed'),('Generados','total'),('Oleada','wave')]],value.get('counter','alive'),lambda v:ins.set(prefix+('counter',),v),'generator_counter')
        ins.spin(tr('Cantidad'),value.get('value',1),lambda v:ins.set(prefix+('value',),v),'generator_counter_value',maximum=1000000)
        g=next((g for g in generators if g['id']==value.get('generator')),None)
        roles=sorted({e['role'] for wave in (g or {}).get('waves',[]) for e in wave['groups']})
        ins.combo(tr('Rol (opcional)'),[(tr('Todos'),'')]+[(r,r) for r in roles],value.get('role',''),lambda v:ins.set(prefix+('role',),v if v else None,True),'generator_counter_role')
    ins.combo(tr('Comparación'),[(tr('Menor que'),'<' ),(tr('Como máximo'),'<='),(tr('Mayor que'),'>'),(tr('Como mínimo'),'>=')]+([(tr('Igual'),'==')] if kind=='generator_count' else []),value.get('comparison','<='),lambda v:ins.set(prefix+('comparison',),v),'dynamic_comparison')

class InventoryDialog(QDialog):
    """Stage catalogue additions until Apply; each item has one creation owner."""
    def __init__(self,win,actor):
        super().__init__(win);self.win=win;self.actor=actor;self.additions=[];self.selected_ids=list(actor.get('inventory',[]))
        self.setWindowTitle(tr('Inventario inicial · ')+actor['name']);self.resize(760,520)
        layout=QVBoxLayout(self);layout.addWidget(QLabel(tr('Añade directamente del catálogo; cada copia es un objeto independiente.')))
        bar=QHBoxLayout();add=QPushButton(tr('+ Del catálogo…'));add.setObjectName('inventory_add');add.clicked.connect(self.add_catalogue)
        remove=QPushButton(tr('Quitar del inventario'));remove.setObjectName('inventory_remove');remove.clicked.connect(self.remove_selected)
        bar.addWidget(add);bar.addWidget(remove);bar.addStretch();layout.addLayout(bar)
        self.items=QListWidget();self.items.setObjectName('inventory_items');layout.addWidget(self.items,1)
        reuse=QHBoxLayout();self.existing=QComboBox();self.existing.setObjectName('inventory_existing');reuse.addWidget(self.existing,1)
        b=QPushButton(tr('Añadir objeto existente'));b.clicked.connect(self.add_existing);reuse.addWidget(b);layout.addLayout(reuse)
        note=QLabel(tr('Se crean dentro del NPC, sin colocarlos también en el suelo. Los objetos de otros inventarios o con spawn no se ofrecen. Aplicar conserva una única operación que puedes deshacer.'));note.setWordWrap(True);layout.addWidget(note)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Apply).setObjectName('apply_inventory');buttons.button(QDialogButtonBox.StandardButton.Apply).setText(tr('Aplicar'));buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons);self.refresh()

    def refresh(self):
        scene=self.win.doc.data;objects=scene.get('objects',[])+self.additions;by_id={o['id']:o for o in objects}
        self.items.clear()
        for ident in self.selected_ids:
            row=by_id[ident];item=QListWidgetItem(row['name']+tr(' · ')+row['template']);item.setData(ROLE,ident);item.setToolTip(row['name']+'\nID: '+ident+tr('\nPlantilla: ')+row['template']);self.items.addItem(item)
        used={x for a in scene['actors'] if a is not self.actor for x in a.get('inventory',[])}|{ac['spawn'] for ev in scene['events'] for ac in ev['actions'] if 'spawn' in ac}
        kinds={t['id']:t['kind'] for t in self.win.backend.resources['templates']};self.existing.clear()
        for row in scene.get('objects',[]):
            if row['id'] not in used|set(self.selected_ids) and kinds.get(row['template']) in {'items','weapons','armour'}:self.existing.addItem(row['name']+tr(' · ')+row['template'],row['id'])

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

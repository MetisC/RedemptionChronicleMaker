"""Native two-page assistants editing ordinary campaign entities atomically."""
import copy
from PySide6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QFormLayout,
    QComboBox, QLineEdit, QPlainTextEdit, QDoubleSpinBox, QSpinBox, QCheckBox,
    QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox, QInputDialog)
from .i18n import tr,diagnostic
from .. import recipes as api
from ..camera_presets import PRESETS, CINEMA_PRESETS

LABELS = {
    'talk': 'NPC que habla', 'go_to_place': 'NPC te manda a un lugar',
    'trigger_actions': 'Trigger que ejecuta acciones', 'trigger_cinematic': 'Trigger cinematográfico',
    'pickup': 'Objeto recogible', 'quest': 'Quest sencilla', 'encounter': 'Encuentro de enemigos',
    'travel': 'Viaje a otra escena', 'note': 'Nota / carta', 'object_conversation': 'Objeto que inicia conversación'}


def commit(win, candidate):
    if win.busy or not win.commit_properties():return False
    win.doc.data = candidate
    win.selection = ('chronicle',)
    win.changed(True)
    return True


class RecipeWizard(QWizard):
    def __init__(self, win, kind=None, recipe_id=None):
        super().__init__(win)
        self.win = win;self.recipe_id = recipe_id;self.repair = False;self.controls = {}
        self.source = win.doc.snapshot();self.open_snapshot=copy.deepcopy(self.source)
        self.saved = next((r for r in api.recipes(self.source) if r['id'] == recipe_id), None)
        self.scene_id = self.saved['scene'] if self.saved else self.source['scenes'][win.doc.active]['id']
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setWindowTitle(tr('Asistentes de crónica'));self.setObjectName('recipe_wizard');self.resize(700, 620)
        first = QWizardPage();first.setTitle(tr('Elige una tarea'));layout = QVBoxLayout(first)
        self.kind = QComboBox();self.kind.setObjectName('recipe_kind')
        for key, label in LABELS.items():self.kind.addItem(tr(label), key)
        self.kind.setCurrentIndex(self.kind.findData(self.saved['type'] if self.saved else kind or 'talk'))
        self.kind.setEnabled(not self.saved);layout.addWidget(self.kind)
        hint = QLabel(tr('El asistente edita los elementos normales del proyecto. Puedes ajustarlos después en Propiedades y volver aquí. Aplicar es una sola operación que puedes deshacer.'));hint.setWordWrap(True);layout.addWidget(hint)
        self.status = QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        if self.saved:
            self.references = QLabel();self.references.setWordWrap(True);layout.addWidget(self.references)
            bar = QHBoxLayout()
            for label, cb in [('Reparar configuración', self.enable_repair), ('Elegir otro recurso', self.choose_resource), ('Desvincular asistente', self.unlink)]:
                b = QPushButton(tr(label));b.clicked.connect(cb);bar.addWidget(b)
            layout.addLayout(bar)
        layout.addStretch();self.addPage(first)
        self.edit = QWizardPage();self.edit.setTitle(tr('Configura y aplica'));self.edit_layout = QVBoxLayout(self.edit)
        from PySide6.QtWidgets import QScrollArea
        self.scroll = QScrollArea();self.scroll.setWidgetResizable(True);self.edit_layout.addWidget(self.scroll)
        self.error = QLabel();self.error.setWordWrap(True);self.edit_layout.addWidget(self.error)
        self.addPage(self.edit);self.update_status()
        self.setButtonText(QWizard.WizardButton.FinishButton, tr('Aplicar'))

    def update_status(self):
        absent = api.missing(self.source, self.saved) if self.saved else []
        self.status.setText(tr('Configuración incompleta') + ': ' + ', '.join(absent) if absent else tr('Nueva configuración') if not self.saved else tr('Editar configuración existente'))
        if self.saved:self.references.setText('\n'.join(role+': '+ref['id'] for role,ref in self.saved['refs'].items()))

    def enable_repair(self):
        if QMessageBox.question(self, tr('Reparar configuración'), tr('Se crearán únicamente las referencias que faltan. Los elementos existentes se conservan. ¿Continuar?')) == QMessageBox.StandardButton.Yes:
            self.repair = True;self.status.setText(tr('Reparación preparada; revisa los campos y pulsa Aplicar.'))

    def choose_resource(self):
        role, ok = QInputDialog.getItem(self, tr('Elegir otro recurso'), tr('Referencia'), list(self.saved['refs']), 0, False)
        if not ok:return
        old = self.saved['refs'][role];coll = old['collection'];choices = []
        if coll == 'flags':choices = [(key, dict(collection=coll, id=key)) for key in self.source.get('state', {}).get('flags', {})]
        elif coll == 'quests':choices = [(r['id'], dict(collection=coll, id=r['id'])) for r in self.source.get('quests', [])]
        else:
            for s in self.source['scenes']:
                if coll!='entries' and s['id']!=old.get('scene'):continue
                for row in s.get(coll, []):choices.append((s['id'] + '/' + row['id'], dict(collection=coll, scene=s['id'], id=row['id'])))
        if not choices:return
        label, ok = QInputDialog.getItem(self, tr('Elegir otro recurso'), tr('Recurso'), [p[0] for p in choices], 0, False)
        if ok:
            try:
                self.source = api.rebind(self.source, self.recipe_id, role, dict(choices)[label])
                self.saved = next(r for r in api.recipes(self.source) if r['id'] == self.recipe_id);self.update_status()
            except ValueError as error:self.status.setText(diagnostic(error))

    def unlink(self):
        if QMessageBox.question(self, tr('Desvincular asistente'), tr('Los elementos de la crónica se conservarán. ¿Desvincular sólo este asistente?')) == QMessageBox.StandardButton.Yes:
            if commit(self.win, api.unlink(self.source, self.recipe_id)):super().accept()

    def initializePage(self, page_id):
        if page_id != 1:return
        self.controls = {};kind = self.kind.currentData()
        current = api.values(self.source, self.saved) if self.saved else {}
        scene = next((s for s in self.source['scenes'] if s['id'] == self.scene_id), self.source['scenes'][0])
        start = next(iter(scene.get('entries', [])), {}).get('transform', {}).get('position', [-62, -768, 384])
        defaults = dict(name=tr('Nuevo elemento'), text=tr('Hola. Tengo algo que pedirte.'), title=tr('Un encargo'), accept=tr('De acuerdo.'), decline=tr('Ahora no.'), position=[start[0]-114, start[1]+156, start[2]], trigger_position=[start[0]-280, start[1]-250, start[2]], radius=90, duration=6, reward_xp=10, camera='ots_speaker_close', target='Player', quest_steps=[tr('Encuentra la carta.')])
        data = {**defaults, **current};self.loaded_values = data
        panel = QWidget();form = QFormLayout(panel);form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.scroll.setWidget(panel)
        def text(key, label, multi=False):
            control = QPlainTextEdit(str(data.get(key, ''))) if multi else QLineEdit(str(data.get(key, '')))
            if multi:control.setMaximumHeight(110)
            self.put(key, control);form.addRow(tr(label), control)
        def number(key, label, default, maximum=1000000):
            control = QDoubleSpinBox();control.setRange(0, maximum);control.setValue(data.get(key, default));self.put(key, control);form.addRow(tr(label), control)
        def vector(key, label):
            box = QWidget();bar = QHBoxLayout(box);bar.setContentsMargins(0,0,0,0);axes=[]
            for i, axis in enumerate('XYZ'):
                c=QDoubleSpinBox();c.setRange(-1000000,1000000);c.setPrefix(axis+' ');c.setValue(data.get(key, start)[i]);bar.addWidget(c);axes.append(c)
            self.controls[key]=axes;form.addRow(tr(label),box)
        def combo(key, label, options, selected):
            c=QComboBox()
            for title, value in options:c.addItem(title,value)
            if c.findData(selected)<0:c.addItem(str(selected),selected)
            c.setCurrentIndex(c.findData(selected));self.put(key,c);form.addRow(tr(label),c);return c
        if kind in {'talk','go_to_place','pickup','encounter','note','object_conversation'}:
            text('name','Nombre')
            from .browser import ResourceDialog
            template=QLineEdit(current.get('template', 'Rat' if kind=='encounter' else 'ledger' if kind=='pickup' else 'barrel1' if kind=='note' else 'Anezka'));self.put('template',template)
            row=QWidget();bar=QHBoxLayout(row);bar.setContentsMargins(0,0,0,0);bar.addWidget(template)
            choose=QPushButton(tr('Catálogo…'));bar.addWidget(choose)
            category='actors' if kind in {'talk','go_to_place','encounter','object_conversation'} else 'items'
            def browse():
                picker=ResourceDialog(self.win.backend, category, self)
                if picker.exec() and picker.selection:template.setText(picker.selection)
            choose.clicked.connect(browse);form.addRow(tr('Plantilla'),row);vector('position','Posición')
        if kind in {'talk','go_to_place','object_conversation','note','quest'}:
            text('text','Texto',True)
        if kind in {'talk','go_to_place','object_conversation'}:
            text('accept','Primera respuesta');text('decline','Segunda respuesta')
            combo('camera','Cámara',[(tr(v[0]),k) for k,v in PRESETS.items()],data['camera'])
        if kind in {'note','quest'}:text('title','Título')
        if kind=='object_conversation':
            data['object_template']=current.get('object_template','barrel1');data['object_name']=current.get('object_name',tr('Objeto que habla'));data['object_position']=current.get('object_position',[start[0]-200,start[1],start[2]])
            text('object_template','Plantilla del objeto');text('object_name','Nombre del objeto');vector('object_position','Posición del objeto')
        if kind=='quest':
            data['quest_steps']='\n'.join(data['quest_steps']);text('quest_steps','Pasos (uno por línea)',True);number('reward_xp','Experiencia',10)
        if kind=='encounter':number('reward_xp','Experiencia',10)
        if kind in {'go_to_place','trigger_actions','trigger_cinematic','travel'}:
            vector('trigger_position','Centro del trigger');number('radius','Radio',90,100000)
        if kind in {'go_to_place','trigger_cinematic'}:
            number('duration','Duración (segundos)',6,120)
            combo('target','Actor enfocado',[(tr('Jugador'),'Player')]+[(a['name'],a['id']) for a in scene['actors']],data['target'])
            combo('reference','Referencia de cámara',[(tr('Sin referencia'),None)]+[(a['name'],a['id']) for a in scene['actors']],current.get('reference'))
            # Existing arbitrary timelines are kept. These controls edit only the
            # first and last shot, preserving intermediate shots and actors.
            steps=current.get('steps',[])
            combo('wide_preset','Plano inicial',[(tr(v[0]),k) for k,v in CINEMA_PRESETS.items()],steps[0]['preset'] if steps else 'aerial')
            combo('close_preset','Plano final',[(tr(v[0]),k) for k,v in CINEMA_PRESETS.items()],steps[-1]['preset'] if steps else 'speaker_close')
        if kind in {'trigger_actions','trigger_cinematic'}:
            cond=QComboBox();cond.addItem(tr('Sin condición'),None)
            for alias in self.source.get('state',{}).get('flags',{}):cond.addItem(alias,alias)
            conditions=current.get('conditions',[])
            selected=conditions[0].get('flag') if len(conditions)==1 and set(conditions[0])=={'flag','is_set'} and conditions[0]['is_set'] else None
            cond.setCurrentIndex(cond.findData(selected));self.put('condition_flag',cond);form.addRow(tr('Sólo si esta flag está activa'),cond)
            self.original_conditions=conditions;self.condition_initial=selected
            once=QCheckBox(tr('Una sola vez'));once.setChecked(current.get('once',True));self.put('once',once);form.addRow(once)
        if kind=='trigger_actions':
            self.action_controls=[]
            for action in current.get('actions',[{'reward_xp':10}]):self.add_action_control(form,scene,action)
            add=QPushButton(tr('Añadir acción'));add.clicked.connect(lambda:self.add_action_control(form,scene,{'reward_xp':0}));form.addRow(add)
        if kind=='travel':
            dest=combo('destination','Escena de destino',[(s['id'],s['id']) for s in self.source['scenes'] if s['id']!=self.scene_id],current.get('destination',next((s['id'] for s in self.source['scenes'] if s['id']!=self.scene_id),None)))
            vector('arrival_position','Punto de llegada')
            dest.setToolTip(tr('Crea antes la escena de destino con + Escena. El punto de llegada se guarda en ella.'))
        note=QLabel(tr('Puedes ver y mover posiciones en Espacio 3D. Los IDs se conservan al editar.'));note.setWordWrap(True);form.addRow(note)

    def put(self,key,control):
        control.setObjectName('recipe_'+key);self.controls[key]=control

    def add_action_control(self,form,scene,action):
        from ..campaign import ACTIONS
        key=next(iter(action));box=QWidget();bar=QHBoxLayout(box);bar.setContentsMargins(0,0,0,0)
        types=QComboBox();target=QComboBox();amount=QSpinBox();amount.setRange(0,1000000)
        common=('set_flag','clear_flag','spawn','remove','start_quest','advance_quest','complete_quest','play_sequence','reward_xp')
        for kind in common:types.addItem(tr(ACTIONS[kind][0]),kind)
        if key not in common:types.addItem(key,key)
        types.setCurrentIndex(types.findData(key));bar.addWidget(types);bar.addWidget(target);bar.addWidget(amount)
        def refresh():
            kind=types.currentData();target.clear();amount.setVisible(kind=='reward_xp');target.setVisible(kind!='reward_xp')
            rows=self.source.get('quests',[]) if 'quest' in kind else scene.get('sequences',[]) if kind=='play_sequence' else scene['actors']+scene.get('objects',[]) if kind in {'spawn','remove'} else [{'id':k} for k in self.source.get('state',{}).get('flags',{})]
            for row in rows:target.addItem(row.get('name',row.get('title',row['id'])),row['id'])
        types.currentIndexChanged.connect(refresh);refresh()
        if isinstance(action[key],str):target.setCurrentIndex(target.findData(action[key]))
        if key=='reward_xp':amount.setValue(action[key])
        enabled=QCheckBox(tr('Incluir'));enabled.setChecked(True);bar.addWidget(enabled)
        self.action_controls.append((types,target,amount,enabled,copy.deepcopy(action)));form.addRow(box)

    def configuration(self):
        data={}
        for key,c in self.controls.items():
            if isinstance(c,list):data[key]=[axis.value() for axis in c]
            elif isinstance(c,QPlainTextEdit):data[key]=c.toPlainText()
            elif isinstance(c,QLineEdit):data[key]=c.text()
            elif isinstance(c,QComboBox):data[key]=c.currentData()
            elif isinstance(c,QCheckBox):data[key]=c.isChecked()
            else:data[key]=c.value()
        if 'quest_steps' in data:data['quest_steps']=[s.strip() for s in data['quest_steps'].splitlines() if s.strip()]
        if 'reward_xp' in data:data['reward_xp']=int(data['reward_xp'])
        if 'wide_preset' in data:
            steps=copy.deepcopy(self.loaded_values.get('steps',[])) or [dict(at=0,actor='Player',preset='aerial',transition=0),dict(at=3,actor='Player',preset='speaker_close',transition=1.5)]
            steps[0]['preset']=data.pop('wide_preset');steps[-1]['preset']=data.pop('close_preset');data['steps']=steps
        if 'condition_flag' in data:
            alias=data.pop('condition_flag');data['conditions']=copy.deepcopy(self.original_conditions) if alias==self.condition_initial else [dict(flag=alias,is_set=True)] if alias else []
        if self.kind.currentData()=='trigger_actions':
            data['actions']=[old if types.currentData() not in {'set_flag','clear_flag','spawn','remove','start_quest','advance_quest','complete_quest','play_sequence','reward_xp'} else {types.currentData():amount.value() if types.currentData()=='reward_xp' else target.currentData()} for types,target,amount,enabled,old in self.action_controls if enabled.isChecked()]
        return data

    def accept(self):
        try:
            if self.win.doc.snapshot()!=self.open_snapshot:raise ValueError(tr('El proyecto cambió mientras el asistente estaba abierto. Vuelve a abrirlo.'))
            candidate,ident=api.apply(self.source,self.kind.currentData(),self.scene_id,self.configuration(),self.recipe_id,self.repair)
            before={p.message for p in self.win.backend.validate(self.win.doc.snapshot()).problems if p.severity=='ERROR'}
            errors={p.message for p in self.win.backend.validate(candidate).problems if p.severity=='ERROR'}-before
            if errors:raise ValueError('\n'.join(sorted(errors)))
            if commit(self.win,candidate):self.recipe_id=ident;super().accept()
        except (ValueError,KeyError,TypeError) as error:self.error.setText(diagnostic(error))


def open_wizard(win,kind=None,recipe_id=None):
    if win.busy or not win.doc or not win.commit_properties():return
    if not hasattr(win.doc,'campaign') or win.doc.campaign.get('project_format')!=9:
        QMessageBox.information(win,tr('Asistentes de crónica'),tr('Crea o convierte primero una campaña de formato 9.'));return
    if recipe_id is None:
        matches=[r for r in api.recipes(win.doc.campaign) if (kind is None or r['type']==kind) and r['scene']==win.doc.campaign['scenes'][win.doc.active]['id']]
        if matches:
            options=[tr('Crear otra configuración')]+[r['id'] for r in matches]
            choice,ok=QInputDialog.getItem(win,tr('Asistentes de crónica'),tr('Configuración'),options,1,False)
            if not ok:return
            recipe_id=choice if choice!=options[0] else None
    RecipeWizard(win,kind,recipe_id).exec()

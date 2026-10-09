from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QCheckBox, QSizePolicy)

from ..model import identifier


class Inspector(QWidget):
    def __init__(self, window):
        super().__init__()
        self.win = window
        self.path = window.selection
        layout = QVBoxLayout(self)
        title = QLabel("PROPIEDADES")
        title.setStyleSheet("font-weight: 600; padding: 7px 0;")
        layout.addWidget(title)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        layout.addLayout(self.form)
        if not window.doc:
            self.note("Crea una crónica o abre un proyecto existente.")
        else:
            self.render()
            self.relationships()
        layout.addStretch()

    def note(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        label.setStyleSheet("padding: 7px 0;")
        self.form.addRow(label)

    def line(self, label, value, callback, name=None, finished=False):
        control = QLineEdit(str(value))
        control.setObjectName(name or label)
        if finished:
            control._rcm_pending = False
            def mark_pending(value):
                control._rcm_pending = True
                self.win._title()
            def commit():
                if not control._rcm_pending:
                    return True
                result = self.win.guard(lambda: callback(control.text()))
                control._rcm_pending = result is False
                self.win._title()
                return result is not False
            control._rcm_commit = commit
            control.textChanged.connect(mark_pending)
            control.editingFinished.connect(commit)
        else:
            control.textChanged.connect(lambda v: self.win.guard(lambda: callback(v)))
        self.form.addRow(label, control)
        return control

    def text(self, label, value, callback, name):
        control = QPlainTextEdit(str(value))
        control.setObjectName(name)
        control.setMinimumHeight(95)
        control.setMaximumHeight(150)
        control.textChanged.connect(lambda: self.win.guard(lambda: callback(control.toPlainText())))
        self.form.addRow(label, control)
        return control

    def combo(self, label, choices, selected, callback, name):
        control = QComboBox()
        control.setObjectName(name)
        for text, value in choices:
            control.addItem(str(text), value)
        index = control.findData(selected)
        if index < 0 and selected not in (None, ""):
            control.addItem("Referencia pendiente: " + str(selected), selected)
            index = control.count()-1
        control.setCurrentIndex(max(index, 0))
        control.currentIndexChanged.connect(lambda: self.win.guard(lambda: callback(control.currentData())))
        self.form.addRow(label, control)
        return control

    def spin(self, label, value, callback, name, floating=False, minimum=0, maximum=32767):
        control = QDoubleSpinBox() if floating else QSpinBox()
        control.setObjectName(name)
        control.setRange(minimum, maximum)
        if floating:
            control.setDecimals(3)
            control.setSingleStep(1)
        control.setValue(value)
        control.valueChanged.connect(lambda v: self.win.guard(lambda: callback(v)))
        self.form.addRow(label, control)
        return control

    def button(self, label, callback, name):
        control = QPushButton(label)
        control.setObjectName(name)
        control.clicked.connect(lambda checked=False: self.win.guard(callback))
        self.form.addRow(control)
        return control

    def ids(self, collection, blank=False):
        return ([("Ninguna", "")] if blank else []) + [(i.get("name", i["id"]), i["id"]) for i in self.win.doc.data.get(collection, [])]

    def flags(self, blank=False):
        return ([("Ninguno", "")] if blank else []) + [(f"{alias} · {value}", alias) for alias, value in self.win.doc.data.get("state", {}).get("flags", {}).items()]

    def set(self, path, value, optional=False):
        self.win.set_value(path, value, optional)

    def rename(self, value):
        p = self.path
        def operation():
            old = self.win.at(p)["id"]
            if old == value:
                return
            if p[0] == "conversations" and len(p) == 4:
                self.win.doc.rename_node(p[1], p[3], value)
            else:
                self.win.doc.rename(p[0], p[1], value)
            self.win.changed(True)
        return self.win.guard(operation)

    def render(self):
        p = self.path
        data = self.win.doc.data
        if p == ("chronicle",):
            chron = data["chronicle"]
            def change_id(value):
                def operation():
                    identifier(value, "ID de crónica", 14 if hasattr(self.win.doc,'campaign') else 18)
                    self.set(("chronicle", "id"), value)
                return self.win.guard(operation)
            self.line("ID interno", chron["id"], change_id, "chronicle_id", True)
            self.line("Nombre", chron["name"], lambda v: self.set(("chronicle", "name"), v), "chronicle_name")
            self.text("Descripción", chron.get("description", ""), lambda v: self.set(("chronicle", "description"), v), "chronicle_description")
            self.note("Archivo: " + str(self.win.doc.path))
            self.note("Cada escena usa una geometría original. Las campañas pueden contener varias escenas. Los builds se guardan en build/<ID>.")
        elif p == ("level",):
            source = data["level"].get("source", "")
            self.note(self.win.backend.level_label(source) + " · " + source if source in self.win.backend.levels else "Elige el escenario de tu crónica.")
            self.button("Elegir level base…", self.win.choose_level, "choose_level")
            self.line("Título al entrar", data["level"].get("name", ""), lambda v: self.set(("level", "name"), v, True), "level_name")
            self.note("Si no escribes un título, aparecerá el nombre de la crónica.")
            if source in self.win.backend.levels:
                level = self.win.backend.levels[source]
                self.note("Geometría: " + level["nil"] + "\nEscenas conocidas: " + ", ".join(level["scenes"]))
                profiles = self.win.backend.scene_profiles(source)
                def choose_environment(value):
                    self.set(('level', 'environment_scene'), value, True)
                    self.win.inspect()
                self.combo('Entorno original', [('Automático (compatible)', '')] +
                           [(row['id'] + (' · no disponible' if 'error' in row else ''), row['id']) for row in profiles],
                           data['level'].get('environment_scene', ''), choose_environment, 'environment_scene')
                chosen = data['level'].get('environment_scene')
                if chosen:
                    row = next((r for r in profiles if r['id'].casefold() == chosen.casefold()), None)
                    if row and 'error' not in row:
                        self.note('Cielo del perfil: ' + (row['sky_model'] or 'sin modelo de cielo') +
                                  '\nSe conservan todos los ajustes originales de entorno; sus actores no se importan.')
                if data['level'].get('sky'):
                    self.note('Este proyecto tiene un override de cielo en YAML. Prevalece sobre el perfil original.')
            self.note("Entorno y contenido pertenecen a la escena. La geometría sigue siendo la del level original.")
        elif p[0] in {"actors", "objects"} and len(p) == 2:
            self.actor()
        elif p[0] == 'triggers' and len(p) == 2:
            self.trigger()
        elif p[0] in ('entries','waypoints') and len(p)==2:
            self.marker()
        elif p[0] == 'original' and len(p) == 2:
            e = self.win.at(p)
            self.note('REFERENCIA ORIGINAL · SÓLO LECTURA\nEl viewport la muestra como referencia. El motor puede cargar contenido estático asociado a la geometría; esta vista no lo elimina.')
            for k in ('template', 'position', 'orientation', 'sector', 'script', 'origin', 'confidence'):
                self.note(k + ': ' + str(e.get(k)))
        elif p[0] == "conversations" and len(p) >= 2:
            self.conversation()
        elif p[0] == "events" and len(p) >= 2:
            self.event_properties()
        elif p[0] == "state" and len(p) == 3:
            alias = p[2]
            def rename_flag(value):
                def operation():
                    self.win.doc.rename_flag(alias, value)
                    self.win.selection = ("state", "flags", value)
                    self.win.changed(True)
                if alias != value:
                    return self.win.guard(operation)
            self.line("Alias", alias, rename_flag, "flag_alias", True)
            self.spin("Índice", data["state"]["flags"][alias], lambda v: self.set(p, v), "flag_index", maximum=255)
            self.note("Estado booleano de la crónica. El backend actual admite índices 0–255; los índices deben ser únicos.")
        else:
            self.note("Selecciona un elemento de la lista para editarlo.")

    def actor(self):
        p = self.path
        actor = self.win.at(p)
        self.line("ID interno", actor["id"], self.rename, "actor_id", True)
        self.line("Nombre", actor["name"], lambda v: self.set(p + ("name",), v), "actor_name")
        self.note("Plantilla: " + (actor.get("template") or "Sin elegir"))
        self.button("Elegir plantilla…", lambda: self.win.choose_template(p), "choose_template")
        self.note("Level: " + self.win.doc.data["level"].get("source", "Sin elegir"))
        if hasattr(self.win.doc, 'campaign'):
            if p[0] == 'actors':
                self.combo('Comportamiento', [('NPC neutral', 'npc'), ('Enemigo · AI original', 'enemy')], actor.get('behavior', 'npc'), lambda v: self.set(p+('behavior',), v), 'actor_behavior')
                def inventory():
                    from .campaign_panel import inventory_dialog
                    inventory_dialog(self.win, actor)
                self.button('Editar inventario inicial…', inventory, 'actor_inventory')
            else:
                self.combo('Objeto de quest', [('No', False), ('Sí', True)], actor.get('quest_item', False), lambda v: self.set(p+('quest_item',), v), 'object_quest_item')
        trans = actor["transform"]
        placement = trans.get("placement", "absolute")
        def change_placement(value):
            trans["placement"] = value
            if value == "near_player":
                trans.pop("position", None)
            else:
                trans.setdefault("position", [0, 0, 0])
            self.win.changed(True)
        self.combo("Colocación", [("Junto al jugador", "near_player"), ("Coordenadas", "absolute")], placement, change_placement, "actor_placement")
        for i, label in enumerate(["X", "Y", "Z"]):
            spin = self.spin(label, trans.get("position", [0, 0, 0])[i],
                lambda v, index=i: self.set(p + ("transform", "position", index), v), "position_"+label.lower(), True, -1e7, 1e7)
            spin.setEnabled(placement == "absolute")
        for i, label in enumerate(["Pitch", "Roll", "Yaw / rumbo"]):
            self.spin(label, trans["orientation"][i], lambda v, index=i: self.set(p + ("transform", "orientation", index), v),
                "orientation_"+str(i), True, -36000, 36000)
        check = QCheckBox("Crear al iniciar la escena")
        check.setObjectName("actor_spawn")
        events = self.win.doc.data["events"]
        check.setChecked(any(a.get("spawn") == actor["id"] for e in events if e['when']=='scene_start' for a in e["actions"]))
        def set_spawn(enabled):
            if enabled:
                event = next((e for e in events if e["when"] == "scene_start" and not e.get("conditions")), None)
                if event is None:
                    event = {"id": self.win.doc.unique_id("events", "event"), "when": "scene_start", "actions": []}
                    events.append(event)
                for previous in events:
                    previous['actions'] = [a for a in previous['actions'] if a.get('spawn') != actor['id']]
                event["actions"].append({"spawn": actor["id"]})
            else:
                for event in events:
                    if event['when']=='scene_start':
                        event["actions"] = [a for a in event["actions"] if a.get("spawn") != actor["id"]]
                events[:] = [e for e in events if e["actions"]]
            self.win.changed(True)
        check.toggled.connect(set_spawn)
        self.form.addRow(check)
        if p[0] == "actors":
            binding = actor.get("conversation", {})
            def binding_field(key, value):
                if key == "default" and not value:
                    actor.pop("conversation", None)
                else:
                    bound = actor.setdefault("conversation", {"default": ""})
                    if value:
                        bound[key] = value
                    else:
                        bound.pop(key, None)
                        if key == "when_flag":
                            bound.pop("then", None)
                self.win.changed()
                self.win.inspect()
            choices = [("Ninguna", "")] + [(c["id"], c["id"]) for c in self.win.doc.data["conversations"] if c["speaker"] == actor["id"]]
            self.combo("Al hablar", choices, binding.get("default", ""), lambda v: binding_field("default", v), "actor_conversation")
            flags = self.combo("Si el flag está activo", self.flags(True), binding.get("when_flag", ""), lambda v: binding_field("when_flag", v), "actor_when_flag")
            flags.setEnabled(bool(binding.get("default")))
            then = self.combo("Conversación alternativa", choices, binding.get("then", ""), lambda v: binding_field("then", v), "actor_then")
            then.setEnabled(bool(binding.get("when_flag")))
            self.note("Actor neutral con AI pausada. Hablar se habilita al asociar una conversación o un evento de clic.")
        self.text("Notas del diseñador", actor.get("comment", ""), lambda v: self.set(p + ("comment",), v), "actor_comment")
        if self.win.spatial.viewport:
            self.button('Enfocar en 3D', self.win.spatial.viewport.focus_selection, 'focus_entity')
            self.button('Ajustar al suelo', self.win.spatial.snap_selected, 'snap_ground')

    def marker(self):
        p=self.path;row=self.win.at(p)
        self.line('ID interno',row['id'],self.rename,'marker_id',True)
        self.line('Nombre',row['name'],lambda v:self.set(p+('name',),v),'marker_name')
        for i,axis in enumerate('xyz'):
            self.spin('Posición '+axis.upper(),row['transform']['position'][i],lambda v,i=i:self.set(p+('transform','position',i),v),'position_'+axis,True,-1e7,1e7)
        for i,label in enumerate(('Pitch','Roll','Yaw')):
            self.spin(label,row['transform']['orientation'][i],lambda v,i=i:self.set(p+('transform','orientation',i),v),'orientation_'+str(i),True,-360,360)
        self.note('Punto lógico de llegada tras el viaje. No modifica los portales ni la geometría original.' if p[0]=='entries' else 'El recorrido solicita al motor desplazarse hasta estos puntos mediante su navegación existente.')
        if self.win.spatial.viewport:
            self.button('Enfocar en 3D',self.win.spatial.viewport.focus_selection,'focus_entity')
            self.button('Ajustar al suelo',self.win.spatial.snap_selected,'snap_ground')

    def trigger(self):
        p = self.path
        t = self.win.at(p)
        self.line('ID interno', t['id'], self.rename, 'trigger_id', True)
        self.line('Nombre', t['name'], lambda v: self.set(p+('name',), v), 'trigger_name')
        def shape(value):
            t['shape'] = value
            if value == 'sphere':
                t['radius'] = max(t.pop('size', [120,120,120]))/2
                t['transform']['orientation'] = [0,0,0]
            else:
                t['size'] = [2*t.pop('radius',60)]*3
            self.win.changed(True)
        self.combo('Volumen', [('Caja', 'box'), ('Esfera', 'sphere')], t['shape'], shape, 'trigger_shape')
        for i, axis in enumerate('XYZ'):
            self.spin(axis, t['transform']['position'][i], lambda v,i=i: self.set(p+('transform','position',i), v), 'trigger_position_'+axis, True, -1e7, 1e7)
        if t['shape'] == 'box':
            self.spin('Yaw', t['transform']['orientation'][2], lambda v: self.set(p+('transform','orientation',2), v), 'trigger_yaw', True, -36000, 36000)
            for i, axis in enumerate('XYZ'):
                self.spin('Tamaño '+axis, t['size'][i], lambda v,i=i: self.set(p+('size',i), v), 'trigger_size_'+axis, True, 1, 1e7)
        else:
            self.spin('Radio', t['radius'], lambda v: self.set(p+('radius',), v), 'trigger_radius', True, 1, 1e7)
        self.combo('Activación', [('Una vez', True), ('Cada entrada', False)], t.get('once', True), lambda v: self.set(p+('once',), v), 'trigger_once')
        self.note('CUANDO un jugador entra en el volumen. Configura condiciones y acciones en sus eventos de entrada. La posición indica el centro del volumen.')
        self.button('Añadir evento de entrada', self.add_trigger_event, 'trigger_event')
        self.button('Ajustar al suelo', self.win.spatial.snap_selected, 'snap_ground')

    def add_trigger_event(self):
        data = self.win.doc.data
        tid = self.win.at(self.path)['id']
        flag = next(iter(data.get('state', {}).get('flags', {})), None)
        if flag is None:
            flag = 'triggered'
            data.setdefault('state', {}).setdefault('flags', {})[flag] = 0
        index = len(data['events'])
        data['events'].append(dict(id=self.win.doc.unique_id('events','event'), when='trigger_enter', trigger=tid, conditions=[], actions=[{'set_flag':flag}]))
        self.win.selection = ('events', index)
        self.win.changed(True)
        self.win.center_tabs.setCurrentIndex(1)

    def relationships(self):
        if not self.win.doc or self.path[0] not in {'actors','objects','triggers','events','conversations','state'}:
            return
        from ..spatial.relations import references
        from PySide6.QtWidgets import QListWidget, QListWidgetItem
        from PySide6.QtCore import Qt
        path = self.path if self.path[0] == 'state' else self.path[:2]
        if hasattr(self.win.doc, 'campaign'):
            from ..campaign_relations import graph
            if path[0] != 'state': path=('scenes',self.win.doc.active)+path
            links=graph(self.win.doc.campaign)
            incoming,outgoing=[x for x in links if x.target==path],[x for x in links if x.source==path]
        else:
            incoming, outgoing = references(self.win.doc.data, path)
        self.button('Find References / Buscar referencias', lambda:self.win.find_references(path), 'find_references')
        if self.win.spatial.viewport:
            def show_related():
                self.win.center_tabs.setCurrentIndex(0)
                self.win.spatial.links.setChecked(True)
                self.win.spatial.viewport.focus_selection()
            self.button('Mostrar relacionados en 3D', show_related, 'show_related')
        for label, rows, attr in [('USED BY · Dependencias', incoming, 'source'), ('AFFECTS · Referencias', outgoing, 'target')]:
            self.note(label)
            if not rows:
                self.note('Sin referencias declaradas')
                continue
            listing = QListWidget()
            listing.setMaximumHeight(120)
            for link in rows:
                target = getattr(link, attr)
                labels = {'spawn':'Crear', 'set_flag':'Activar flag', 'clear_flag':'Desactivar flag', 'start_conversation':'Iniciar conversación', 'speaker':'Actor principal', 'default':'Al hablar', 'when_flag':'Condición', 'then':'Conversación alternativa'}
                item = QListWidgetItem(labels.get(link.label,link.label) + ' · ' + self.win.reference_label(target))
                item.setData(Qt.ItemDataRole.UserRole, target)
                listing.addItem(item)
            listing.itemDoubleClicked.connect(lambda item: self.win.navigate_reference(item.data(Qt.ItemDataRole.UserRole)))
            self.form.addRow(listing)
            if attr == 'source':
                for link in rows:
                    if link.source[0] == 'events':
                        event = self.win.at(link.source)
                        from .window import TRIGGER_LABELS, ACTION_LABELS
                        conditions = [c['flag'] + (' activado' if c['is_set'] else ' desactivado') if 'flag' in c else str(c) for c in event.get('conditions', [])]
                        actions = [ACTION_LABELS.get(k,k)+': '+str(v) for a in event.get('actions', []) for k,v in a.items()]
                        self.note('CUANDO: '+TRIGGER_LABELS.get(event['when'],event['when'])+'\nSI: '+(' y '.join(conditions) or 'Sin condiciones')+'\nHACER:\n'+'\n'.join(actions))

    def conversation(self):
        p = self.path
        conv = self.win.doc.data["conversations"][p[1]]
        if len(p) == 2:
            self.line("ID", conv["id"], self.rename, "conversation_id", True)
            self.combo("Actor principal", self.ids("actors"), conv["speaker"], lambda v: self.set(p + ("speaker",), v), "conversation_speaker")
            if "nodes" in conv:
                self.combo("Nodo de entrada", [(n["id"], n["id"]) for n in conv["nodes"]], conv.get("entry", ""), lambda v: self.set(p + ("entry",), v), "conversation_entry")
                self.note("Las respuestas pueden llevar a otro nodo o terminar con un resultado. Las acciones de flags se aplican al terminar.")
            else:
                self.note("Conversación simple de Fase 1. Su sintaxis se conserva hasta que añadas un nodo.")
        elif len(p) == 3 and p[2] == "prompt":
            self.text("Texto", conv["prompt"], lambda v: self.set(p, v), "line_text")
        elif len(p) == 4 and p[2] == "nodes":
            node = self.win.at(p)
            self.line("ID del nodo", node["id"], self.rename, "node_id", True)
            self.button("Usar como entrada", lambda: self.set(("conversations", p[1], "entry"), node["id"]), "make_entry")
            self.note("Añade líneas y respuestas con los botones del editor central.")
        elif p[-2] == "lines":
            line = self.win.at(p)
            self.combo("Actor", self.ids("actors"), line.get("speaker", conv["speaker"]), lambda v: self.set(p + ("speaker",), v), "line_speaker")
            self.text("Texto", line["text"], lambda v: self.set(p + ("text",), v), "line_text")
            self.note("Escribe un solo parlamento por línea, sin saltos de párrafo. Puedes añadir varias líneas al nodo y reordenarlas.")
        elif p[-2] == "choices":
            answer = self.win.at(p)
            self.text("Respuesta", answer["text"], lambda v: self.set(p + ("text",), v), "answer_text")
            nodes = conv.get("nodes", [])
            def mode(value):
                if value == "goto":
                    answer.pop("result", None)
                    answer.pop("set_flag", None)
                    answer.pop("clear_flag", None)
                    answer["goto"] = nodes[0]["id"] if nodes else ""
                else:
                    answer.pop("goto", None)
                    answer["result"] = self.win.next_result(conv) if nodes else max(a["result"] for a in conv["choices"])+1
                self.win.changed(True)
            modes = [("Terminar (RETURN)", "return")] + ([("Ir a otro nodo", "goto")] if nodes else [])
            self.combo("Destino", modes, "goto" if "goto" in answer else "return", mode, "answer_mode")
            if "goto" in answer:
                self.combo("Nodo", [(n["id"], n["id"]) for n in nodes], answer["goto"], lambda v: self.set(p + ("goto",), v), "answer_target")
            else:
                self.spin("Resultado", answer.get("result", 1), lambda v: self.set(p + ("result",), v), "answer_result", minimum=1)
                current = "set_flag" if "set_flag" in answer else "clear_flag" if "clear_flag" in answer else ""
                def effect(value):
                    previous = answer.get("set_flag", answer.get("clear_flag", ""))
                    answer.pop("set_flag", None)
                    answer.pop("clear_flag", None)
                    if value:
                        answer[value] = previous or next(iter(self.win.doc.data.get("state", {}).get("flags", {})), "")
                    self.win.changed(True)
                self.combo("Cambiar estado", [("Sin cambio", ""), ("Activar flag", "set_flag"), ("Desactivar flag", "clear_flag")], current, effect, "answer_effect")
                if current:
                    self.combo("Flag", self.flags(), answer[current], lambda v: self.set(p + (current,), v), "answer_flag")

    def event_properties(self):
        if hasattr(self.win.doc, 'campaign'):
            from .campaign_panel import event_properties
            return event_properties(self)
        p = self.path
        event = self.win.doc.data["events"][p[1]]
        if len(p) == 2:
            self.line("ID", event.get("id", "event"+str(p[1]+1)), self.rename_event, "event_id", True)
            def change_trigger(value):
                event["when"] = value
                for key in ["actor", "conversation", "result", "trigger"]:
                    event.pop(key, None)
                if value == "actor_clicked":
                    event["actor"] = next((a["id"] for a in self.win.doc.data["actors"]), "")
                elif value == "conversation_ended":
                    event["conversation"] = next((c["id"] for c in self.win.doc.data["conversations"]), "")
                elif value == 'trigger_enter':
                    event['trigger'] = next((t['id'] for t in self.win.doc.data.get('triggers',[])), '')
                # Keep authored actions: incompatible ones are reported, never silently dropped.
                self.win.changed(True)
            self.combo("CUANDO", [("Inicia la escena", "scene_start"), ("Hablan con un actor", "actor_clicked"),
                ("Termina una conversación", "conversation_ended"), ('Jugador entra en trigger', 'trigger_enter')], event["when"], change_trigger, "event_when")
            if event['when'] == 'trigger_enter':
                self.combo('Volumen', self.ids('triggers'), event.get('trigger',''), lambda v:self.set(p+('trigger',),v), 'event_trigger')
            if event["when"] == "actor_clicked":
                self.combo("Actor", self.ids("actors"), event.get("actor", ""), lambda v: self.set(p + ("actor",), v), "event_actor")
                self.note("Si hay varios eventos de clic para ese actor, se usa el primer evento cuyas condiciones se cumplen. Usa eventos o el enlace Al hablar del actor.")
            elif event["when"] == "conversation_ended":
                self.combo("Conversación", [(c["id"], c["id"]) for c in self.win.doc.data["conversations"]], event.get("conversation", ""), lambda v: self.set(p + ("conversation",), v), "event_conversation")
                self.spin("Resultado (0 = cualquiera)", event.get("result", 0), lambda v: self.set(p + ("result",), v if v else None, True), "event_result")
                self.note("Se ejecuta tras aplicar la acción de la respuesta. Una conversación abortada no dispara este evento.")
            self.note("Añade condiciones y acciones en el editor central. Scene Start permite crear actores y cambiar flags; los eventos de clic inician conversaciones.")
        elif p[-2] == "conditions":
            condition = self.win.at(p)
            self.combo("Flag", self.flags(), condition.get("flag", ""), lambda v: self.set(p + ("flag",), v), "condition_flag")
            self.combo("Estado requerido", [("Activado", True), ("Desactivado", False)], condition["is_set"], lambda v: self.set(p + ("is_set",), v), "condition_state")
        elif p[-2] == "actions":
            action = self.win.at(p)
            current = next(iter(action), "spawn")
            allowed = [("Activar flag", "set_flag"), ("Desactivar flag", "clear_flag")]
            if event["when"] in {"scene_start", "trigger_enter"}:
                allowed.insert(0, ("Crear actor / objeto", "spawn"))
            elif event["when"] == "actor_clicked":
                allowed.insert(0, ("Iniciar conversación", "start_conversation"))
            def mode(value):
                action.clear()
                action[value] = ""
                self.win.changed(True)
            self.combo("Acción", allowed, current, mode, "action_kind")
            if current == "spawn":
                choices = self.ids("actors") + self.ids("objects")
            elif current == "start_conversation":
                choices = [(c["id"], c["id"]) for c in self.win.doc.data["conversations"] if c["speaker"] == event.get("actor")]
            else:
                choices = self.flags()
            # Empty is an explicit draft value, never silently replaced by the first row.
            self.combo("Objetivo", [("Elige…", "")] + choices, action.get(current, ""), lambda v: self.set(p + (current,), v), "action_target")

    def rename_event(self, value):
        p = self.path
        def operation():
            identifier(value, "ID de evento")
            if any(i != p[1] and e.get("id") == value for i, e in enumerate(self.win.doc.data["events"])):
                raise ValueError("Ese evento ya existe.")
            self.set(p + ("id",), value)
            self.win.changed(True)
        return self.win.guard(operation)

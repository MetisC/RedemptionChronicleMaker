from .i18n import tr
"""Project template/AI library; never edits an original library."""
from pathlib import Path
import copy,json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QComboBox,QListWidget,QFormLayout,QLineEdit,QScrollArea,QDoubleSpinBox,QPlainTextEdit,QFileDialog,QInputDialog,QMessageBox
from .browser import ResourceDialog
from ..campaign_document import CampaignDocument
from ..project_resources import AI_FIELDS,original_entry,original_bytes,resource_identifier

class ProjectResourcesPanel(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.index=-1
        layout=QVBoxLayout(self);bar=QHBoxLayout();self.kind=QComboBox();self.kind.setObjectName('project_resource_kind')
        for name,key in [(tr('Templates propios'),'templates'),(tr('Perfiles AI propios'),'ai_profiles'),(tr('Texturas propias'),'textures'),(tr('Java propio · avanzado'),'scripts'),(tr('Recorridos de cámara propios'),'camera_paths')]:self.kind.addItem(name,key)
        bar.addWidget(self.kind)
        for text,name,cb in [(tr('Upgrade formato 5'),'upgrade_format',self.upgrade),(tr('Clonar / Nuevo'),'clone_project_resource',self.new),(tr('Duplicar'),'duplicate_project_resource',self.duplicate),(tr('Borrar'),'delete_project_resource',self.delete)]:
            b=QPushButton(text);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bar.addWidget(b)
        layout.addLayout(bar);notice=QLabel(tr('Recursos del proyecto. Originales sólo lectura. Writer NOT experimental hasta verificar la nueva plantilla dentro de Redemption.'));notice.setWordWrap(True);layout.addWidget(notice)
        self.list=QListWidget();self.list.setObjectName('project_resource_list');layout.addWidget(self.list,1);self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);layout.addWidget(self.scroll,3)
        self.previous_kind=0
        self.kind.currentIndexChanged.connect(self.category_changed);self.list.currentRowChanged.connect(self.select)
    def category_changed(self,index):
        if not self.win.commit_properties():
            self.kind.blockSignals(True);self.kind.setCurrentIndex(self.previous_kind);self.kind.blockSignals(False);return
        self.previous_kind=index;self.index=-1;self.refresh()
    def root(self):return self.win.doc.campaign if self.win.doc and hasattr(self.win.doc,'campaign') else None
    def rows(self):return self.root().get('resources',{}).get(self.kind.currentData(),[]) if self.root() else []
    def upgrade(self):
        if not self.win.doc:raise ValueError(tr('Abre o crea primero una crónica'))
        if not self.win.commit_properties():return False
        if not hasattr(self.win.doc,'campaign'):self.win.doc=CampaignDocument.convert(self.win.doc)
        root=self.root()
        if root.get('project_format') not in (5,9,10):
            if self.win.doc.path and self.win.doc.path.exists():self.win.doc._atomic_write(self.win.doc.path.with_name(self.win.doc.path.name+'.pre_format5'),self.win.doc.path.read_text(encoding='utf8'))
            root.update(project_format=5,metadata={'author':'','version':'0.1.0','requires_game':'Redemption 1.1','dependencies':[]},resources={'templates':[],'ai_profiles':[],'scripts':[],'textures':[]},build_options={'debug':True},playtests=[]);self.win.changed(True)
        self.win.center_tabs.setCurrentWidget(self);return True
    def refresh(self):
        self.list.blockSignals(True);self.list.clear()
        for row in self.rows():self.list.addItem(row['id']+tr(' · ')+row.get('base',tr('Proyecto')))
        for i in range(self.list.count()):self.list.item(i).setToolTip(self.list.item(i).text())
        self.index=min(self.index,len(self.rows())-1);self.list.setCurrentRow(self.index);self.list.blockSignals(False);self.render()
    def select(self,index):
        if not self.win.commit_properties():
            self.list.blockSignals(True);self.list.setCurrentRow(self.index);self.list.blockSignals(False);return
        self.index=index;self.render()
    def new(self):
        if not self.upgrade():return
        kind=self.kind.currentData();rows=self.root()['resources'].setdefault(kind,[])
        if kind=='camera_paths':
            scene=self.root()['scenes'][self.win.doc.active]
            if not scene.get('sequences'):raise ValueError(tr('Crea primero una secuencia en Campaña.'))
            from .director import open_camera_path
            open_camera_path(self.win,('scenes',self.win.doc.active,'sequences',0));return
        if kind in {'templates','ai_profiles'}:
            category='.nai'
            if kind=='templates':
                family,ok=QInputDialog.getItem(self,tr('Familia de template'),tr('Contenido'),[tr('Actor'),tr('Item / prop / arma')],0,False)
                if not ok:return
                category='actors' if family==tr('Actor') else 'items'
            dialog=ResourceDialog(self.win.backend,category,self)
            if not dialog.exec():return
            base=dialog.selection
        else:base=None
        stem='T_'+self.root()['chronicle']['id']+'_npc' if kind=='templates' else 'AI_'+self.root()['chronicle']['id'] if kind=='ai_profiles' else 'RCM5Script' if kind=='scripts' else 'TX_'+self.root()['chronicle']['id']
        ident,ok=QInputDialog.getText(self,tr('Recurso propio'),tr('ID único (máximo 31 caracteres)'),text=stem)
        if not ok:return
        resource_identifier(ident)
        if any(r['id'].casefold()==ident.casefold() for r in rows):raise ValueError(tr('ID duplicado'))
        row={'id':ident}
        if kind in {'templates','ai_profiles'}:row.update(base=base,properties={})
        if kind=='templates':row['mode']='inherit'
        if kind in {'textures','scripts'}:
            folder=self.win.doc.path.parent if self.win.doc.path else self.win.backend.ws.root/'chronicles'/self.root()['chronicle']['id']
            if kind=='textures':
                source,_=QFileDialog.getOpenFileName(self,tr('Importar textura'),'',tr('Imágenes (*.png *.tga *.bmp)'))
                if not source:return
                target=folder/'resources'/(ident+Path(source).suffix.lower());self.win.backend.ws.write(target,Path(source).read_bytes())
            else:
                target=folder/'resources'/(ident+'.java')
                if target.exists():self.win.log.appendPlainText(tr('Java propio existente conservado: ')+target.name)
                else:self.win.backend.ws.write(target,'public class '+ident+' extends Codex {\n public '+ident+'() { CodexConsole.Print(0,0,"RCM custom script '+ident+'"); }\n}\n')
            row['source']=target.relative_to(self.win.backend.ws.root).as_posix()
        rows.append(row);self.index=len(rows)-1;self.win.changed(True);self.refresh()
    def clone_original(self,base):
        if not self.upgrade():return
        ident,ok=QInputDialog.getText(self,tr('Clonar al proyecto'),tr('ID único'),text='T_'+self.root()['chronicle']['id']+'_npc')
        if not ok:return
        resource_identifier(ident);rows=self.root()['resources']['templates']
        if any(r['id'].casefold()==ident.casefold() for r in rows):raise ValueError(tr('ID duplicado'))
        rows.append(dict(id=ident,base=base,mode='inherit',properties={}));self.kind.setCurrentIndex(0);self.index=len(rows)-1;self.win.changed(True);self.refresh()
    def duplicate(self):
        if self.index<0:return
        if not self.win.commit_properties():return
        if self.kind.currentData()=='scripts':raise ValueError(tr('Java propio: crea otra clase para evitar renombrar código manual'))
        rows=self.rows();row=copy.deepcopy(rows[self.index]);i=1
        while any(r['id']==row['id'][:26]+'_c'+str(i) for r in rows):i+=1
        row['id']=row['id'][:26]+'_c'+str(i);rows.append(row);self.index=len(rows)-1;self.win.changed(True)
    def references(self,ident):
        found=[]
        def walk(v,path=()):
            if isinstance(v,dict):
                for k,x in v.items():
                    if k in {'template','base','ai','script','camera_path'} and x==ident:found.append(path+(k,))
                    elif k=='class' and path[-1:]==('native_script',) and x==ident:found.append(path+(k,))
                    elif k=='resource' and path[-1:]==('play_camera_path',) and x==ident:found.append(path+(k,))
                    else:walk(x,path+(k,))
            elif isinstance(v,list):
                for i,x in enumerate(v):walk(x,path+(i,))
        walk(self.root());return found
    def delete(self):
        if self.index<0:return
        ident=self.rows()[self.index]['id'];refs=self.references(ident)
        if self.kind.currentData()=='camera_paths' or hasattr(self.win.doc,'campaign') and self.root().get('project_format') in (9,10):
            from .deletion import confirm_delete
            candidate=confirm_delete(self.win,('resources',self.kind.currentData(),self.index))
            if candidate is not None:self.win.doc.data=candidate;self.win.history_time=0;self.win.changed(True)
            return
        if refs:raise ValueError(tr('No se borra ')+ident+tr(': ')+str(len(refs))+tr(' referencias. Reasigna las entidades/recursos primero'))
        if QMessageBox.question(self,tr('Borrar recurso propio'),tr('Borrar ')+ident+tr(' del proyecto? Los archivos fuente se conservan.'))!=QMessageBox.StandardButton.Yes:return
        self.rows().pop(self.index);self.win.changed(True)
    def render(self):
        old=self.scroll.takeWidget();body=QWidget();form=QFormLayout(body);self.scroll.setWidget(body)
        if old:old.deleteLater()
        if self.index<0 or self.index>=len(self.rows()):return
        row=self.rows()[self.index];kind=self.kind.currentData();root=self.root();props=row.setdefault('properties',{}) if kind in {'templates','ai_profiles'} else None
        def change(k,v):
            if props is not None:
                if v=='':props.pop(k,None)
                else:props[k]=v
            self.win.changed(kind=='templates')
        field=QLineEdit(row['id']);field.setObjectName('resource_id');form.addRow(tr('ID propio'),field);field._rcm_pending=False
        def rename():
            new=resource_identifier(field.text());old=row['id']
            if kind=='scripts' and new!=old:raise ValueError(tr('No renombres una clase Java desde su recurso'))
            if any(r is not row and r['id'].casefold()==new.casefold() for r in self.rows()):raise ValueError(tr('ID duplicado'))
            for path in self.references(old):
                node=root
                for k in path[:-1]:node=node[k]
                node[path[-1]]=new
            row['id']=new;self.win.changed(False);field._rcm_pending=False;return True
        def mark(value):field._rcm_pending=True;self.win._title()
        field.textChanged.connect(mark);field._rcm_commit=lambda:self.win.guard(rename)
        field.editingFinished.connect(lambda:field._rcm_commit() if field._rcm_pending else True)
        def combo(label,key,choices,current,fn=None):
            box=QComboBox();box.setObjectName('resource_'+key)
            for title,value in choices:box.addItem(title,value)
            index=box.findData(current)
            if index<0:box.addItem(tr('Ausente: ')+str(current),current);index=box.count()-1
            box.setCurrentIndex(index);box.currentIndexChanged.connect(lambda i:(fn or (lambda value:change(key,value)))(box.itemData(i)));form.addRow(label,box);return box
        if kind=='templates':
            combo(tr('Base original / propia'),'base',[(t['id'],t['id']) for t in self.win.backend.resources['templates'] if t['id']!=row['id']],row['base'],lambda v:(row.update(base=v),self.win.changed(True)))
            combo(tr('Relación'),'mode',[(tr('Herencia real'),'inherit'),(tr('Copiar registro, preservar raw'),'copy')],row.get('mode','inherit'),lambda v:(row.update(mode=v),self.win.changed(False)))
            for label,key,ext in [(tr('Modelo'),'model','.nod'),('AI','ai','.nai'),(tr('Foley / sonidos del objeto'),'foley','.nag'),(tr('Conjunto de animaciones'),'motions','.nms'),(tr('Script · avanzado'),'script','.class')]:
                values=sorted({e['id'] for e in self.win.backend.resources['entries'] if e['extension'].lower()==ext})
                if key=='script':
                    from ..native_scripts import available
                    scripts=available(self.win.backend.ws,self.win.backend.original_resources,root)
                    values=[name for name in values if name in scripts and not scripts[name]['parameters']]
                    def set_script(value):
                        if value is None:props.pop('script',None)
                        else:props['script']=value
                        self.win.changed(True)
                    combo(label,key,[(tr('Heredar de la base'),None),(tr('Sin script'), '')]+[(x,x) for x in values],props.get(key),set_script)
                else:combo(label,key,[(tr('Heredar de la base'),'')]+[(x,x) for x in values],props.get(key,''))
            hover=QLineEdit(row.get('hover_text',''));hover.setObjectName('resource_hover_text');hover.setPlaceholderText(tr('Heredar texto de la plantilla'));form.addRow(tr('Texto al señalar'),hover)
            def save_hover():
                def update():
                    value=hover.text()
                    if value.strip():row['hover_text']=value
                    else:row.pop('hover_text',None)
                    hover._rcm_pending=False;self.win.changed(False);return True
                return self.win.guard(update)
            hover._rcm_pending=False;hover.textChanged.connect(lambda value:setattr(hover,'_rcm_pending',True));hover._rcm_commit=save_hover;hover.editingFinished.connect(lambda:save_hover() if hover._rcm_pending else True)
            base=next((t for t in self.win.backend.resources['templates'] if t['id']==row['base']),{})
            if base.get('kind')=='containers':
                from ..treasure import catalogue
                choices=[(tr('Heredar de la base'),None),(tr('Sin tesoro'),0)]+[(str(r['id'])+' · '+r['description'],r['id']) for r in catalogue(self.win.backend.ws,self.win.backend.resources)]
                def set_treasure(value):
                    if value is None:props.pop('treasure_class',None)
                    else:props['treasure_class']=value
                    self.win.changed(False)
                combo(tr('Botín / clase de tesoro'),'treasure_class',choices,props.get('treasure_class'),set_treasure)
            note=QLabel(tr('Los controles modifican sólo tags contrastados. Clan/health/stats no se muestran como bytes supuestamente conocidos.'));note.setWordWrap(True);form.addRow(note)
            bits=QLineEdit(hex(props['actor_flags']) if 'actor_flags' in props else '');bits.setObjectName('resource_actor_flags');bits.setPlaceholderText(tr('Heredar; valor hexadecimal sólo en modo técnico'));form.addRow(tr('Actor flags · avanzado'),bits)
            def save_bits():
                def update():
                    if bits.text().strip():props['actor_flags']=int(bits.text(),0)
                    else:props.pop('actor_flags',None)
                    bits._rcm_pending=False;self.win.changed(False);return True
                return self.win.guard(update)
            bits._rcm_pending=False;bits.textChanged.connect(lambda value:setattr(bits,'_rcm_pending',True));bits._rcm_commit=save_bits;bits.editingFinished.connect(lambda:save_bits() if bits._rcm_pending else True)
            raw=QPlainTextEdit(json.dumps(row,ensure_ascii=False,indent=2));raw.setReadOnly(True);form.addRow(tr('Definición propia'),raw)
        elif kind=='ai_profiles':
            base=original_entry(self.win.backend.original_resources,'.nai',row['base']);text=original_bytes(self.win.backend.ws,base).decode('cp1252')
            presets=QComboBox();presets.setObjectName('ai_preset')
            for label,key in [(tr('Ajuste manual'),''),(tr('Quieto / sin vagar'),'still'),(tr('Alerta cercana'),'alert'),(tr('Persecución amplia'),'pursuit')]:presets.addItem(label,key)
            def apply_preset():
                import re
                settings={'still':{'wanderRadius':0},'alert':{'chaseDist':512,'searchDist':256},'pursuit':{'chaseDist':2048,'searchDist':1024}}.get(presets.currentData(),{})
                for key,value in settings.items():
                    if re.search(r'^\s*'+key+r'\s+',text,re.M):props[key]=value
                self.win.changed(True);self.render()
            button=QPushButton(tr('Aplicar ajuste'));button.setObjectName('apply_ai_preset');button.clicked.connect(apply_preset);form.addRow(tr('Ajuste de AI original'),presets);form.addRow(button)
            labels={'attackRate':tr('Intervalo de ataque'),'attackAlt':tr('Ataque alternativo'),'moveDist':tr('Distancia de movimiento'),'moveRate':tr('Intervalo de movimiento'),'chaseDist':tr('Distancia de persecución'),'chaseRate':tr('Intervalo de persecución'),'searchDist':tr('Distancia de búsqueda'),'searchRate':tr('Intervalo de búsqueda'),'wanderRadius':tr('Radio de paseo'),'wakeupDelay':tr('Demora de activación'),'interestNum':tr('Grupo de interés · -1 desactiva')}
            for key,(low,high) in AI_FIELDS.items():
                import re
                match=re.search(r'^[ \t]*'+key+r'[ \t]+(-?[0-9.]+)',text,re.M)
                if not match:continue
                spin=QDoubleSpinBox();spin.setObjectName('ai_'+key);spin.setRange(low,high);spin.setDecimals(0 if key=='interestNum' else 3);spin.setValue(props.get(key,float(match[1])));spin.valueChanged.connect(lambda v,k=key:change(k,int(v) if k=='interestNum' else v));form.addRow(labels[key],spin)
            note=QLabel(tr('Son ajustes de campos del perfil base, no un árbol de comportamiento. La afinidad y pausa del actor se controlan aparte; verifica su resultado en partida.'));note.setWordWrap(True);form.addRow(note)
            raw=QPlainTextEdit(text);raw.setReadOnly(True);form.addRow(tr('Base original; líneas desconocidas preservadas'),raw)
        elif kind=='camera_paths':
            form.addRow(QLabel(row.get('name',row['id'])+' · '+str(len(row['points']))+' · '+row['level']+' / '+row['scene']))
            sequence=next((('scenes',si,'sequences',i) for si,s in enumerate(root['scenes']) for i,seq in enumerate(s.get('sequences',[])) if seq.get('camera_path')==row['id']),None)
            from .director import open_camera_path
            button=QPushButton(tr('Editar puntos de cámara…'));button.clicked.connect(lambda:open_camera_path(self.win,sequence,row['id']));form.addRow(button)
        elif kind=='scripts':
            from .script_metadata import edit_metadata
            metadata=QPushButton(tr('Parámetros del constructor…'));metadata.setObjectName('custom_script_parameters');metadata.clicked.connect(lambda:edit_metadata(self.win,row));form.addRow(metadata)
            path=self.win.backend.ws.output(row['source']);editor=QPlainTextEdit(path.read_text(encoding='utf8'));editor.setObjectName('custom_java');form.addRow(tr('Java propio, no generado por Build'),editor)
            editor._rcm_pending=False
            def mark_java():editor._rcm_pending=True;self.win._title()
            editor.textChanged.connect(mark_java)
            def save_java():
                self.win.doc._atomic_write(path.with_name(path.name+'.backup'),path.read_text(encoding='utf8'))
                self.win.doc._atomic_write(path,editor.toPlainText());editor._rcm_pending=False;self.win._title();return True
            editor._rcm_commit=lambda:self.win.guard(save_java)
            b=QPushButton(tr('Guardar Java propio'));b.setObjectName('save_custom_java');b.clicked.connect(editor._rcm_commit);form.addRow(b)
        else:
            from PIL import Image
            image=Image.open(self.win.backend.ws.output(row['source']));form.addRow(QLabel(str(image.size)+tr(' · ')+image.mode+tr(' · ')+row['source']))
            from PySide6.QtGui import QPixmap
            label=QLabel();label.setPixmap(QPixmap(str(self.win.backend.ws.output(row['source']))).scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio));form.addRow(label)

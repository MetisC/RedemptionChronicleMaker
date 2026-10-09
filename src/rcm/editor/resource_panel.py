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
        for name,key in [('Templates propios','templates'),('Perfiles AI propios','ai_profiles'),('Texturas propias','textures'),('Java propio · avanzado','scripts')]:self.kind.addItem(name,key)
        bar.addWidget(self.kind)
        for text,name,cb in [('Upgrade formato 5','upgrade_format',self.upgrade),('Clonar / Nuevo','clone_project_resource',self.new),('Duplicar','duplicate_project_resource',self.duplicate),('Borrar','delete_project_resource',self.delete)]:
            b=QPushButton(text);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bar.addWidget(b)
        layout.addLayout(bar);notice=QLabel('Recursos del proyecto. Originales sólo lectura. Writer NOT experimental hasta verificar la nueva plantilla dentro de Redemption.');notice.setWordWrap(True);layout.addWidget(notice)
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
        if not self.win.doc:raise ValueError('Abre o crea primero una crónica')
        if not self.win.commit_properties():return False
        if not hasattr(self.win.doc,'campaign'):self.win.doc=CampaignDocument.convert(self.win.doc)
        root=self.root()
        if root.get('project_format') not in (5,9):
            if self.win.doc.path and self.win.doc.path.exists():self.win.doc._atomic_write(self.win.doc.path.with_name(self.win.doc.path.name+'.pre_format5'),self.win.doc.path.read_text(encoding='utf8'))
            root.update(project_format=5,metadata={'author':'','version':'0.1.0','requires_game':'Redemption 1.1','dependencies':[]},resources={'templates':[],'ai_profiles':[],'scripts':[],'textures':[]},build_options={'debug':True},playtests=[]);self.win.changed(True)
        self.win.center_tabs.setCurrentWidget(self);return True
    def refresh(self):
        self.list.blockSignals(True);self.list.clear()
        for row in self.rows():self.list.addItem(row['id']+' · '+row.get('base','Proyecto'))
        self.index=min(self.index,len(self.rows())-1);self.list.setCurrentRow(self.index);self.list.blockSignals(False);self.render()
    def select(self,index):
        if not self.win.commit_properties():return
        self.index=index;self.render()
    def new(self):
        if not self.upgrade():return
        kind=self.kind.currentData();rows=self.root()['resources'].setdefault(kind,[])
        if kind in {'templates','ai_profiles'}:
            category='.nai'
            if kind=='templates':
                family,ok=QInputDialog.getItem(self,'Familia de template','Contenido',['Actor','Item / prop / arma'],0,False)
                if not ok:return
                category='actors' if family=='Actor' else 'items'
            dialog=ResourceDialog(self.win.backend,category,self)
            if not dialog.exec():return
            base=dialog.selection
        else:base=None
        stem='T_'+self.root()['chronicle']['id']+'_npc' if kind=='templates' else 'AI_'+self.root()['chronicle']['id'] if kind=='ai_profiles' else 'RCM5Script' if kind=='scripts' else 'TX_'+self.root()['chronicle']['id']
        ident,ok=QInputDialog.getText(self,'Recurso propio','ID único (máximo 31 caracteres)',text=stem)
        if not ok:return
        resource_identifier(ident)
        if any(r['id'].casefold()==ident.casefold() for r in rows):raise ValueError('ID duplicado')
        row={'id':ident}
        if kind in {'templates','ai_profiles'}:row.update(base=base,properties={})
        if kind=='templates':row['mode']='inherit'
        if kind in {'textures','scripts'}:
            folder=self.win.doc.path.parent if self.win.doc.path else self.win.backend.ws.root/'chronicles'/self.root()['chronicle']['id']
            if kind=='textures':
                source,_=QFileDialog.getOpenFileName(self,'Importar textura','','Imágenes (*.png *.tga *.bmp)')
                if not source:return
                target=folder/'resources'/(ident+Path(source).suffix.lower());self.win.backend.ws.write(target,Path(source).read_bytes())
            else:
                target=folder/'resources'/(ident+'.java')
                if target.exists():self.win.log.appendPlainText('Java propio existente conservado: '+target.name)
                else:self.win.backend.ws.write(target,'public class '+ident+' extends Codex {\n public '+ident+'() { CodexConsole.Print(0,0,"RCM custom script '+ident+'"); }\n}\n')
            row['source']=target.relative_to(self.win.backend.ws.root).as_posix()
        rows.append(row);self.index=len(rows)-1;self.win.changed(True);self.refresh()
    def clone_original(self,base):
        if not self.upgrade():return
        ident,ok=QInputDialog.getText(self,'Clonar al proyecto','ID único',text='T_'+self.root()['chronicle']['id']+'_npc')
        if not ok:return
        resource_identifier(ident);rows=self.root()['resources']['templates']
        if any(r['id'].casefold()==ident.casefold() for r in rows):raise ValueError('ID duplicado')
        rows.append(dict(id=ident,base=base,mode='inherit',properties={}));self.kind.setCurrentIndex(0);self.index=len(rows)-1;self.win.changed(True);self.refresh()
    def duplicate(self):
        if self.index<0:return
        if not self.win.commit_properties():return
        if self.kind.currentData()=='scripts':raise ValueError('Java propio: crea otra clase para evitar renombrar código manual')
        rows=self.rows();row=copy.deepcopy(rows[self.index]);i=1
        while any(r['id']==row['id'][:26]+'_c'+str(i) for r in rows):i+=1
        row['id']=row['id'][:26]+'_c'+str(i);rows.append(row);self.index=len(rows)-1;self.win.changed(True)
    def references(self,ident):
        found=[]
        def walk(v,path=()):
            if isinstance(v,dict):
                for k,x in v.items():
                    if k in {'template','base','ai','script'} and x==ident:found.append(path+(k,))
                    else:walk(x,path+(k,))
            elif isinstance(v,list):
                for i,x in enumerate(v):walk(x,path+(i,))
        walk(self.root());return found
    def delete(self):
        if self.index<0:return
        ident=self.rows()[self.index]['id'];refs=self.references(ident)
        if refs:raise ValueError('No se borra '+ident+': '+str(len(refs))+' referencias. Reasigna las entidades/recursos primero')
        if QMessageBox.question(self,'Borrar recurso propio','Borrar '+ident+' del proyecto? Los archivos fuente se conservan.')!=QMessageBox.StandardButton.Yes:return
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
        field=QLineEdit(row['id']);field.setObjectName('resource_id');form.addRow('ID propio',field);field._rcm_pending=False
        def rename():
            new=resource_identifier(field.text());old=row['id']
            if kind=='scripts' and new!=old:raise ValueError('No renombres una clase Java desde su recurso')
            if any(r is not row and r['id'].casefold()==new.casefold() for r in self.rows()):raise ValueError('ID duplicado')
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
            if index<0:box.addItem('Ausente: '+str(current),current);index=box.count()-1
            box.setCurrentIndex(index);box.currentIndexChanged.connect(lambda i:(fn or (lambda value:change(key,value)))(box.itemData(i)));form.addRow(label,box);return box
        if kind=='templates':
            combo('Base original / propia','base',[(t['id'],t['id']) for t in self.win.backend.resources['templates'] if t['id']!=row['id']],row['base'],lambda v:(row.update(base=v),self.win.changed(True)))
            combo('Relación','mode',[('Herencia real','inherit'),('Copiar registro, preservar raw','copy')],row.get('mode','inherit'),lambda v:(row.update(mode=v),self.win.changed(False)))
            for label,key,ext in [('Modelo','model','.nod'),('AI','ai','.nai'),('Script · avanzado','script','.class')]:
                values=sorted({e['id'] for e in self.win.backend.resources['entries'] if e['extension'].lower()==ext});combo(label,key,[('Heredar de la base','')]+[(x,x) for x in values],props.get(key,''))
            note=QLabel('Los controles modifican sólo tags contrastados. Clan/health/stats no se muestran como bytes supuestamente conocidos.');note.setWordWrap(True);form.addRow(note)
            bits=QLineEdit(hex(props['actor_flags']) if 'actor_flags' in props else '');bits.setObjectName('resource_actor_flags');bits.setPlaceholderText('Heredar; valor hexadecimal sólo en modo técnico');form.addRow('Actor flags · avanzado',bits)
            def save_bits():
                def update():
                    if bits.text().strip():props['actor_flags']=int(bits.text(),0)
                    else:props.pop('actor_flags',None)
                    bits._rcm_pending=False;self.win.changed(False);return True
                return self.win.guard(update)
            bits._rcm_pending=False;bits.textChanged.connect(lambda value:setattr(bits,'_rcm_pending',True));bits._rcm_commit=save_bits;bits.editingFinished.connect(lambda:save_bits() if bits._rcm_pending else True)
            raw=QPlainTextEdit(json.dumps(row,ensure_ascii=False,indent=2));raw.setReadOnly(True);form.addRow('Definición propia',raw)
        elif kind=='ai_profiles':
            base=original_entry(self.win.backend.original_resources,'.nai',row['base']);text=original_bytes(self.win.backend.ws,base).decode('cp1252')
            presets=QComboBox();presets.setObjectName('ai_preset')
            for label,key in [('Ajuste manual',''),('Quieto / sin vagar','still'),('Alerta cercana','alert'),('Persecución amplia','pursuit')]:presets.addItem(label,key)
            def apply_preset():
                import re
                settings={'still':{'wanderRadius':0},'alert':{'chaseDist':512,'searchDist':256},'pursuit':{'chaseDist':2048,'searchDist':1024}}.get(presets.currentData(),{})
                for key,value in settings.items():
                    if re.search(r'^\s*'+key+r'\s+',text,re.M):props[key]=value
                self.win.changed(True);self.render()
            button=QPushButton('Aplicar ajuste');button.setObjectName('apply_ai_preset');button.clicked.connect(apply_preset);form.addRow('Ajuste de AI original',presets);form.addRow(button)
            labels={'attackRate':'Intervalo de ataque','attackAlt':'Ataque alternativo','moveDist':'Distancia de movimiento','moveRate':'Intervalo de movimiento','chaseDist':'Distancia de persecución','chaseRate':'Intervalo de persecución','searchDist':'Distancia de búsqueda','searchRate':'Intervalo de búsqueda','wanderRadius':'Radio de paseo','wakeupDelay':'Demora de activación'}
            for key,(low,high) in AI_FIELDS.items():
                import re
                match=re.search(r'^\s*'+key+r'\s+([0-9.]+)',text,re.M)
                if not match:continue
                spin=QDoubleSpinBox();spin.setObjectName('ai_'+key);spin.setRange(low,high);spin.setDecimals(3);spin.setValue(props.get(key,float(match[1])));spin.valueChanged.connect(lambda v,k=key:change(k,v));form.addRow(labels[key],spin)
            note=QLabel('Son ajustes de campos del perfil base, no un árbol de comportamiento. La afinidad y pausa del actor se controlan aparte; verifica su resultado en partida.');note.setWordWrap(True);form.addRow(note)
            raw=QPlainTextEdit(text);raw.setReadOnly(True);form.addRow('Base original; líneas desconocidas preservadas',raw)
        elif kind=='scripts':
            path=self.win.backend.ws.output(row['source']);editor=QPlainTextEdit(path.read_text(encoding='utf8'));editor.setObjectName('custom_java');form.addRow('Java propio, no generado por Build',editor)
            editor._rcm_pending=False
            def mark_java():editor._rcm_pending=True;self.win._title()
            editor.textChanged.connect(mark_java)
            def save_java():
                self.win.doc._atomic_write(path.with_name(path.name+'.backup'),path.read_text(encoding='utf8'))
                self.win.doc._atomic_write(path,editor.toPlainText());editor._rcm_pending=False;self.win._title();return True
            editor._rcm_commit=lambda:self.win.guard(save_java)
            b=QPushButton('Guardar Java propio');b.setObjectName('save_custom_java');b.clicked.connect(editor._rcm_commit);form.addRow(b)
        else:
            from PIL import Image
            image=Image.open(self.win.backend.ws.output(row['source']));form.addRow(QLabel(str(image.size)+' · '+image.mode+' · '+row['source']))
            from PySide6.QtGui import QPixmap
            label=QLabel();label.setPixmap(QPixmap(str(self.win.backend.ws.output(row['source']))).scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio));form.addRow(label)

"""Transactional informational map authoring in the existing campaign workflow."""
import copy
import hashlib
import io
from pathlib import Path
from PySide6.QtCore import Qt,QPointF
from PySide6.QtGui import QPixmap,QImage,QBrush,QColor,QPen
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,QPushButton,QLineEdit,QListWidget,QLabel,QCheckBox,QDialogButtonBox,QFileDialog,QGraphicsView,QGraphicsScene,QGraphicsEllipseItem,QScrollArea,QWidget,QMessageBox
from .i18n import tr,diagnostic


class Marker(QGraphicsEllipseItem):
    def __init__(self,point,select):
        super().__init__(0,0,16,16);self.point=point;self.select=select
        self.setBrush(QBrush(QColor('#f2c66d')));self.setPen(QPen(QColor('#111111'),2));self.setZValue(1)
        self.setFlags(self.GraphicsItemFlag.ItemIsMovable|self.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPos(point['position'][0],464-point['position'][1]);self.setToolTip(point['name'])
    def itemChange(self,change,value):
        if change==self.GraphicsItemChange.ItemPositionChange:return QPointF(max(0,min(624,value.x())),max(0,min(464,value.y())))
        return super().itemChange(change,value)
    def mousePressEvent(self,event):self.select();super().mousePressEvent(event)
    def mouseReleaseEvent(self,event):
        super().mouseReleaseEvent(event);self.point['position']=[round(self.pos().x()),round(464-self.pos().y())]


class MapDialog(QDialog):
    def __init__(self,win):
        super().__init__(win);self.win=win;self.initial=win.doc.snapshot();self.root=copy.deepcopy(self.initial);self.pending={}
        self.rows=self.root.setdefault('resources',{}).setdefault('maps',[])
        self.setWindowTitle(tr('Mapas y localizaciones'));self.resize(1000,760)
        layout=QVBoxLayout(self);bar=QHBoxLayout();layout.addLayout(bar)
        self.maps=QComboBox();self.maps.setObjectName('map_choice');bar.addWidget(self.maps,1)
        for label,name,callback in [('Nuevo mapa','map_new',self.add_map),('Importar imagen…','map_image',self.import_image),('Eliminar mapa','map_delete',self.delete_map)]:
            button=QPushButton(tr(label));button.setObjectName(name);button.clicked.connect(callback);bar.addWidget(button)
        form=QFormLayout();layout.addLayout(form);self.name=QLineEdit();self.name.setObjectName('map_name');form.addRow(tr('Nombre'),self.name);self.name.textEdited.connect(lambda value:self.row().update(name=value) if self.row() else None)
        body=QHBoxLayout();layout.addLayout(body,1);left=QVBoxLayout();body.addLayout(left,1)
        self.points=QListWidget();self.points.setObjectName('map_points');left.addWidget(self.points,1)
        buttons=QHBoxLayout();left.addLayout(buttons)
        for label,name,callback in [('+ Localización','map_point_add',self.add_point),('Eliminar','map_point_delete',self.delete_point)]:
            button=QPushButton(tr(label));button.setObjectName(name);button.clicked.connect(callback);buttons.addWidget(button)
        self.point_name=QLineEdit();self.point_name.setObjectName('map_point_name');left.addWidget(self.point_name);self.point_name.textEdited.connect(self.rename_point)
        self.visible=QCheckBox(tr('Visible en el mapa'));self.visible.setObjectName('map_point_visible');left.addWidget(self.visible)
        self.haven=QCheckBox(tr('Refugio'));self.haven.setObjectName('map_point_haven');left.addWidget(self.haven)
        for box,key in ((self.visible,'visible'),(self.haven,'haven')):box.toggled.connect(lambda value,k=key:self.point().update({k:value}) if self.point() else None)
        self.canvas=QGraphicsScene(0,0,640,480);self.view=QGraphicsView(self.canvas);self.view.setObjectName('map_canvas');self.view.setMinimumSize(480,360);body.addWidget(self.view,3)
        bindings=QScrollArea();bindings.setWidgetResizable(True);bindings.setMaximumHeight(150);body=QWidget();self.bindings=QFormLayout(body);bindings.setWidget(body);layout.addWidget(bindings)
        note=QLabel(tr('Arrastra los puntos sobre la imagen. El mapa informa de las localizaciones; no viaja al pulsarlas. La imagen se adapta a 640 × 480.'));note.setWordWrap(True);layout.addWidget(note)
        self.error=QLabel();self.error.setWordWrap(True);layout.addWidget(self.error)
        choices=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(choices);choices.accepted.connect(self.accept);choices.rejected.connect(self.reject)
        self.maps.currentIndexChanged.connect(self.refresh_map);self.points.currentRowChanged.connect(self.select_point);self.refresh_maps()
    def row(self):
        i=self.maps.currentIndex();return self.rows[i] if 0<=i<len(self.rows) else None
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'view'):self.view.fitInView(self.canvas.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def point(self):
        row=self.row();i=self.points.currentRow();return row['points'][i] if row and 0<=i<len(row['points']) else None
    def refresh_maps(self,index=0):
        self.maps.blockSignals(True);self.maps.clear()
        for row in self.rows:self.maps.addItem(row['name'],row['id'])
        self.maps.setCurrentIndex(min(index,len(self.rows)-1));self.maps.blockSignals(False);self.refresh_map()
    def refresh_map(self,*_):
        row=self.row();self.name.setText(row['name'] if row else '');self.name.setEnabled(bool(row));self.refresh_points();self.refresh_bindings()
    def image_bytes(self,row):return self.pending.get(row['source']) or self.win.doc.ws.output(row['source']).read_bytes()
    def refresh_points(self,index=0):
        row=self.row();self.points.blockSignals(True);self.points.clear();self.canvas.clear()
        if row:
            for point in row['points']:self.points.addItem(point['name'])
            try:
                image=QImage.fromData(self.image_bytes(row));self.canvas.addPixmap(QPixmap.fromImage(image).scaled(640,480,Qt.AspectRatioMode.IgnoreAspectRatio,Qt.TransformationMode.SmoothTransformation))
            except (OSError,ValueError):pass
            for i,point in enumerate(row['points']):self.canvas.addItem(Marker(point,lambda i=i:self.points.setCurrentRow(i)))
        self.points.setCurrentRow(min(index,self.points.count()-1));self.points.blockSignals(False);self.select_point();self.view.fitInView(self.canvas.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def select_point(self,*_):
        point=self.point();self.point_name.setText(point['name'] if point else '');self.point_name.setEnabled(bool(point))
        for box,key in ((self.visible,'visible'),(self.haven,'haven')):box.blockSignals(True);box.setChecked(bool(point and point.get(key,False)));box.setEnabled(bool(point));box.blockSignals(False)
    def rename_point(self,value):
        point=self.point()
        if point:point['name']=value;self.points.currentItem().setText(value)
    def refresh_bindings(self):
        while self.bindings.rowCount():self.bindings.removeRow(0)
        options=[(tr('Mapa original'),None)]+[(row['name']+' / '+point['name'],dict(map=row['id'],point=point['id'])) for row in self.rows for point in row['points']]
        for scene in self.root['scenes']:
            choice=QComboBox();choice.setObjectName('map_scene_'+scene['id'])
            for label,value in options:choice.addItem(label,value)
            choice.setCurrentIndex(next((i for i,(_,v) in enumerate(options) if v==scene.get('map_location')),0))
            def bind(index,scene=scene,choice=choice):
                value=choice.itemData(index)
                if value is None:scene.pop('map_location',None)
                else:scene['map_location']=value
            choice.currentIndexChanged.connect(bind);self.bindings.addRow(scene['id'],choice)
    def add_map(self):
        if not self.import_image(new=True):return
        self.refresh_maps(len(self.rows)-1)
    def import_image(self,checked=False,new=False):
        file,_=QFileDialog.getOpenFileName(self,tr('Imagen de mapa'),'',tr('Imágenes (*.png *.jpg *.jpeg *.bmp *.tga)'))
        if not file:return False
        try:
            from ..chronicle_maps import map_image
            source=Path(file)
            buffer=io.BytesIO();map_image(source).save(buffer,format='PNG')
            data=buffer.getvalue();path=self.win.doc.path.parent if self.win.doc.path else self.win.doc.ws.output('chronicles/'+self.root['chronicle']['id'])
            name=(path/'assets'/('map_'+hashlib.sha256(data).hexdigest()[:16]+'.png')).relative_to(self.win.doc.ws.root).as_posix();self.pending[name]=data
            if new or not self.row():
                if len(self.rows)>=16:raise ValueError('Map authoring budget: maximum 16 maps')
                number=1
                while any(r['id']=='map'+str(number) for r in self.rows):number+=1
                self.rows.append(dict(id='map'+str(number),name=tr('Mapa')+' '+str(number),source=name,points=[]));self.refresh_maps(len(self.rows)-1)
            else:self.row()['source']=name;self.refresh_points()
            return True
        except (OSError,ValueError) as error:self.error.setText(diagnostic(error));return False
    def delete_map(self):
        row=self.row()
        if not row:return
        for scene in self.root['scenes']:
            if scene.get('map_location',{}).get('map')==row['id']:scene.pop('map_location',None)
        self.rows.remove(row);self.refresh_maps()
    def add_point(self):
        row=self.row()
        if not row:return
        number=1
        while any(p['id']=='place'+str(number) for p in row['points']):number+=1
        row['points'].append(dict(id='place'+str(number),name=tr('Localización')+' '+str(number),position=[312,232],visible=True,haven=False));self.refresh_points(len(row['points'])-1);self.refresh_bindings()
    def delete_point(self):
        point=self.point();row=self.row()
        if not point:return
        for scene in self.root['scenes']:
            if scene.get('map_location')==dict(map=row['id'],point=point['id']):scene.pop('map_location',None)
        row['points'].remove(point);self.refresh_points();self.refresh_bindings()
    def accept(self):
        try:
            if self.win.doc.snapshot()!=self.initial:raise ValueError('Project changed while editing map')
            from ..chronicle_maps import validate
            for row in self.rows:validate(row,self.root['scenes'])
            if not self.rows and 'maps' not in self.initial.get('resources',{}):self.root['resources'].pop('maps',None)
            # Commit imported files only after OK, never while browsing/cancelling.
            from ..file_transaction import replace_files
            ws=self.win.doc.ws;used={r['source'] for r in self.rows};files={ws.output(name):data for name,data in self.pending.items() if name in used}
            if files:replace_files(files,[],ws.output('research/package_backups/map_import.zip'),ws.root,ws.output)
            self.win.doc.data=self.root;self.win.history_time=0;self.win.changed(True);super().accept()
        except (OSError,ValueError) as error:self.error.setText(diagnostic(error))


def open_maps(win,map_index=0,point_index=0):
    if not win.commit_properties() or not hasattr(win.doc,'campaign'):return
    if win.doc.campaign.get('project_format') not in (9,10):
        QMessageBox.information(win,tr('Mapas y localizaciones'),tr('Esta función requiere formato de proyecto 9 o 10.'));return
    dialog=MapDialog(win);dialog.maps.setCurrentIndex(map_index);dialog.points.setCurrentRow(point_index);dialog.exec()

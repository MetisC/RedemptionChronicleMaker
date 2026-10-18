import copy
from PySide6.QtWidgets import QDialog,QFormLayout,QComboBox,QLineEdit,QDialogButtonBox,QLabel,QMessageBox
from .i18n import tr


def edit_overrides(win,entity,actor):
    if not win.commit_properties():return
    dialog=QDialog(win);dialog.setWindowTitle(tr('Propiedades de esta instancia'));dialog.resize(520,350);form=QFormLayout(dialog);controls={};values=entity.get('overrides',{})
    fields=[('foley',tr('Foley / sonidos del objeto'),'.nag'),('motions',tr('Conjunto de animaciones'),'.nms')]
    if actor:fields.insert(0,('ai','AI','.nai'))
    for key,label,ext in fields:
        box=QComboBox();box.setObjectName('instance_'+key);box.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon);box.setMinimumContentsLength(12);box.addItem(tr('Heredar de la plantilla'),None)
        for name in sorted({r['id'] for r in win.backend.resources['entries'] if r['extension'].lower()==ext}):box.addItem(name,name)
        index=box.findData(values.get(key));box.setCurrentIndex(max(0,index));box.setToolTip(box.currentText());box.currentTextChanged.connect(box.setToolTip);form.addRow(label,box);controls[key]=box
    text=QLineEdit(values.get('hover_text',''));text.setObjectName('instance_hover_text');text.setPlaceholderText(tr('Heredar texto de la plantilla'));form.addRow(tr('Texto al señalar'),text)
    record=next((t for t in win.backend.resources['templates'] if t['id']==entity.get('template')),{})
    if record.get('kind')=='containers':
        from ..treasure import catalogue
        box=QComboBox();box.setObjectName('instance_treasure_class');box.addItem(tr('Heredar de la plantilla'),None);box.addItem(tr('Sin tesoro'),0)
        for row in catalogue(win.backend.ws,win.backend.resources):box.addItem(str(row['id'])+' · '+row['description'],row['id'])
        box.setCurrentIndex(max(0,box.findData(values.get('treasure_class'))));form.addRow(tr('Botín / clase de tesoro'),box);controls['treasure_class']=box
    note=QLabel(tr('Sólo afecta a esta instancia. Los demás personajes y objetos que usan la plantilla conservan sus propiedades. El conjunto de animaciones debe corresponder al modelo.'));note.setWordWrap(True);form.addRow(note)
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);form.addRow(buttons)
    if dialog.exec()!=QDialog.DialogCode.Accepted:return
    result={k:c.currentData() for k,c in controls.items() if c.currentData() is not None}
    if text.text().strip():result['hover_text']=text.text()
    # Check only the edited resource fields, so an unrelated unfinished event
    # does not prevent this local edit. Never mutate the live document on error.
    from ..project_resources import prepare
    from .i18n import diagnostic
    candidate=copy.deepcopy(win.doc.snapshot());scene=candidate['scenes'][win.doc.active]
    row=next(r for r in scene['actors']+scene.get('objects',[]) if r['id']==entity['id'])
    row['overrides']=result
    try:prepare(win.backend.ws,candidate,win.backend.original_resources)
    except ValueError as error:
        QMessageBox.warning(win,tr('Revisa las propiedades'),diagnostic(error));return
    if result:entity['overrides']=result
    else:entity.pop('overrides',None)
    win.changed(True)

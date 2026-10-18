"""Explicit advanced custom-Java declaration, checked against real bytecode."""
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QTableWidget,QTableWidgetItem,QComboBox,QPushButton,QDialogButtonBox,QMessageBox
from .i18n import tr,diagnostic


def edit_metadata(win,row):
    if not win.commit_properties():return
    dialog=QDialog(win);dialog.setWindowTitle(tr('Parámetros del constructor'));dialog.resize(560,440);layout=QVBoxLayout(dialog)
    note=QLabel(tr('Sólo Java propio avanzado. Declara los parámetros en el mismo orden que el constructor público. El build comprueba los tipos contra el classfile real; no se deducen del texto Java.'));note.setWordWrap(True);layout.addWidget(note)
    table=QTableWidget(0,2);table.setObjectName('custom_parameter_table');table.setHorizontalHeaderLabels([tr('Tipo'),tr('Etiqueta')]);layout.addWidget(table,1)
    def add(value=None):
        if table.rowCount()>=16:return
        value=value or dict(type='integer',label='Parameter '+str(table.rowCount()+1));i=table.rowCount();table.insertRow(i);combo=QComboBox()
        for kind in ('integer','float','string','thing','actor'):combo.addItem(kind,kind)
        combo.setCurrentIndex(max(0,combo.findData(value['type'])));table.setCellWidget(i,0,combo);table.setItem(i,1,QTableWidgetItem(value['label']))
    for value in row.get('parameters',[]):add(value)
    bar=QHBoxLayout();layout.addLayout(bar);button=QPushButton(tr('Añadir parámetro'));button.clicked.connect(lambda:add());bar.addWidget(button);remove=QPushButton(tr('Quitar selección'));remove.clicked.connect(lambda:table.removeRow(table.currentRow()) if table.currentRow()>=0 else None);bar.addWidget(remove)
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons);buttons.rejected.connect(dialog.reject)
    def accept():
        try:
            values=[dict(type=table.cellWidget(i,0).currentData(),label=table.item(i,1).text()) for i in range(table.rowCount())]
            from ..native_scripts import declared
            declared(dict(parameters=values))
            if values:row['parameters']=values
            else:row.pop('parameters',None)
            win.changed(True);dialog.accept()
        except ValueError as error:QMessageBox.warning(dialog,tr('Revisa los parámetros'),diagnostic(error))
    buttons.accepted.connect(accept);dialog.exec()

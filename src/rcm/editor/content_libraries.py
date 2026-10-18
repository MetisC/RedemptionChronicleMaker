"""Review a selected template library; never import an entire mod implicitly."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QFileDialog,QComboBox,QTreeWidget,QTreeWidgetItem,QDialogButtonBox,QMessageBox
from .i18n import tr,diagnostic
from .busy import busy


def open_import(win):
    if not win.commit_properties():return
    source,_=QFileDialog.getOpenFileName(win,tr('Importar biblioteca de plantillas'),'',tr('Biblioteca NOT/NOB (*.not *.nob)'))
    if not source:return
    try:
        from ..content_libraries import preview,import_content
        with busy(win,tr('Leyendo biblioteca…')):libraries=preview(source)
        if not libraries:raise ValueError(tr('El archivo no contiene bibliotecas NOT'))
        dialog=QDialog(win);dialog.setWindowTitle(tr('Importar biblioteca de plantillas'));dialog.resize(650,510);layout=QVBoxLayout(dialog);choose=QComboBox();choose.setObjectName('library_not')
        for name in sorted(libraries):choose.addItem(name)
        layout.addWidget(choose);note=QLabel(tr('Marca las plantillas nuevas que quieres usar. Se incluyen sus padres y datos necesarios. No se copian menús, crónicas ni código del mod. El contenido permanece como dependencia local y no se incluye en los ZIP exportados.'));note.setWordWrap(True);layout.addWidget(note)
        tree=QTreeWidget();tree.setObjectName('library_templates');tree.setHeaderLabels([tr('Plantilla'),tr('Disponibilidad')]);layout.addWidget(tree,1);original={t['id'].casefold() for t in win.backend.original_resources['templates']}
        def populate():
            tree.clear()
            for name in libraries[choose.currentText()]:
                exists=name.casefold() in original;item=QTreeWidgetItem(tree,[name,tr('Ya disponible') if exists else tr('Nueva')]);item.setToolTip(0,name)
                if not exists:item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(0,Qt.CheckState.Unchecked)
            tree.resizeColumnToContents(0)
        choose.currentIndexChanged.connect(populate);populate()
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons);buttons.rejected.connect(dialog.reject)
        def accept():
            selected=[tree.topLevelItem(i).text(0) for i in range(tree.topLevelItemCount()) if tree.topLevelItem(i).checkState(0)==Qt.CheckState.Checked]
            try:
                with busy(win,tr('Importando biblioteca…')):record=import_content(win.backend,source,choose.currentText(),selected)
                win.refresh();win.browser.refresh();dialog.accept();QMessageBox.information(win,tr('Contenido disponible'),tr('Biblioteca importada: {0} plantillas.').format(len(record['templates'])))
            except (ValueError,OSError,KeyError) as error:QMessageBox.warning(dialog,tr('No se pudo importar'),diagnostic(error))
        buttons.accepted.connect(accept);dialog.exec()
    except (ValueError,OSError,KeyError) as error:QMessageBox.warning(win,tr('No se pudo importar'),diagnostic(error))


def import_widget(win,layout):
    row=QHBoxLayout();button=QPushButton(tr('Importar biblioteca de plantillas NOT/NOB…'));button.setObjectName('settings_import_library');button.clicked.connect(lambda:open_import(win));row.addWidget(button);layout.addLayout(row)
    manage=QPushButton(tr('Bibliotecas importadas…'));manage.setObjectName('settings_manage_libraries');manage.clicked.connect(lambda:manage_libraries(win));row.addWidget(manage)


def manage_libraries(win):
    if not win.commit_properties():return
    from ..content_libraries import manifests,remove_content
    dialog=QDialog(win);dialog.setWindowTitle(tr('Bibliotecas importadas'));dialog.resize(620,420);layout=QVBoxLayout(dialog)
    note=QLabel(tr('Retirar una biblioteca elimina sólo la copia importada de este workspace. No modifica el mod original, otras crónicas ni lo instalado en Redemption. Las crónicas que la necesiten requerirán importarla otra vez.'));note.setWordWrap(True);layout.addWidget(note)
    tree=QTreeWidget();tree.setObjectName('installed_libraries');tree.setHeaderLabels([tr('Biblioteca'),tr('Plantillas')]);layout.addWidget(tree,1)
    def refresh():
        tree.clear()
        for r in manifests(win.backend.ws):
            item=QTreeWidgetItem(tree,[r['name'],str(len(r['templates']))]);item.setData(0,Qt.ItemDataRole.UserRole,r['id']);item.setToolTip(0,r['id'])
    refresh();remove=QPushButton(tr('Retirar biblioteca seleccionada'));remove.setObjectName('library_remove');layout.addWidget(remove)
    def uninstall():
        item=tree.currentItem()
        if item is None:return
        if QMessageBox.question(dialog,tr('Retirar biblioteca'),tr('¿Retirar esta biblioteca del workspace?'))!=QMessageBox.StandardButton.Yes:return
        try:
            remove_content(win.backend,item.data(0,Qt.ItemDataRole.UserRole),win.doc.snapshot() if win.doc else None);win.refresh();win.browser.refresh();refresh()
        except (ValueError,OSError) as error:QMessageBox.warning(dialog,tr('No se pudo retirar'),diagnostic(error))
    remove.clicked.connect(uninstall);buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons);dialog.exec()

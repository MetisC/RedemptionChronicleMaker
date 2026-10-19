"""Native product shell: setup, welcome, preferences and one-click playtest."""
from pathlib import Path
import base64
import json
import time

from PySide6.QtCore import Qt,QTimer,QThread,QObject,Signal,QByteArray,QUrl
from PySide6.QtGui import QAction,QDesktopServices
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QDialog,QFormLayout,QLineEdit,QComboBox,QDialogButtonBox,QFileDialog,QMessageBox,
    QStackedWidget,QListWidget,QCheckBox,QSpinBox,QToolBar,QInputDialog,QMenu)
from .i18n import tr,diagnostic


def open_folder(path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


class SetupDialog(QDialog):
    def __init__(self,preferences,game=None,workspace=None,parent=None):
        super().__init__(parent);self.preferences=preferences
        self.setWindowTitle(tr('Bienvenido a Redemption Chronicle Maker'));self.resize(660,360)
        layout=QVBoxLayout(self)
        intro=QLabel(tr('Selecciona tu copia de Redemption. RCM leerá sus escenarios y recursos para que puedas crear tus propias aventuras.'));intro.setWordWrap(True);layout.addWidget(intro)
        form=QFormLayout();layout.addLayout(form)
        self.exe=QLineEdit(str(Path(game)/'Vampire.exe') if game else '');self.exe.setObjectName('setup_executable')
        row=QHBoxLayout();row.addWidget(self.exe,1);pick=QPushButton(tr('Seleccionar Vampire.exe…'));pick.clicked.connect(self.pick_exe);row.addWidget(pick);form.addRow(tr('Redemption'),row)
        self.language=QComboBox();self.language.addItem('English','en');self.language.addItem('Español','es');self.language.setCurrentIndex(self.language.findData(preferences.data['language']));form.addRow(tr('Idioma'),self.language)
        from ..app_settings import default_workspace
        self.workspace=QLineEdit(str(workspace or default_workspace()));self.workspace.setObjectName('setup_workspace');form.addRow(tr('Tus proyectos'),self.workspace)
        hint=QLabel(tr('Tus crónicas se guardan fuera del programa. Los archivos originales del juego se conservan.'));hint.setWordWrap(True);layout.addWidget(hint)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr('Preparar RCM'));buttons.accepted.connect(self.check);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.exe.textChanged.connect(self.inspect);self.inspect()
    def pick_exe(self):
        path,_=QFileDialog.getOpenFileName(self,tr('Selecciona Vampire.exe'),self.exe.text(),tr('Redemption (Vampire.exe)'))
        if path:self.exe.setText(path)
    def inspect(self):
        game=Path(self.exe.text()).parent
        self.status.setText('\n'.join(('✓ ' if (game/name).is_file() else '✗ ')+name for name in ('Vampire.exe','Resource.nob','classes.zip')))
    def check(self):
        try:
            if Path(self.exe.text()).name.casefold()!='vampire.exe':raise ValueError(tr('Selecciona Vampire.exe.'))
            from ..product import verify_installation
            game=verify_installation(Path(self.exe.text()).parent)
            from ..product import validate_workspace
            self.ws=validate_workspace(self.workspace.text(),game)
            self.ws.app_settings=self.preferences
            self.accept()
        except (ValueError,OSError) as error:self.status.setText(diagnostic(error))


class Welcome(QWidget):
    def __init__(self,win):
        super().__init__();self.win=win;self.setObjectName('welcome')
        layout=QVBoxLayout(self);layout.setContentsMargins(40,25,40,25)
        title=QLabel('Redemption Chronicle Maker');title.setStyleSheet('font-size:24px;font-weight:600');layout.addWidget(title)
        subtitle=QLabel(tr('Crea una aventura. Pon un personaje. Escribe una conversación. Pruébala en Redemption.'));subtitle.setWordWrap(True);layout.addWidget(subtitle)
        for label,name,cb in [(tr('Nueva crónica'),'welcome_new',win.new_project),(tr('Abrir crónica'),'welcome_open',win.open_project),(tr('Tutorial rápido'),'welcome_tutorial',lambda:open_example(win,'tutorial')),(tr('Showcase completo'),'welcome_showcase',lambda:open_example(win,'showcase')),(tr('Instalar crónica…'),'welcome_install',lambda:__import__('rcm.editor.package_panel',fromlist=['install_package']).install_package(win))]:
            b=QPushButton(label);b.setObjectName(name);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb))
            if name=='welcome_new':b.setStyleSheet('font-weight:600;padding:10px');layout.addSpacing(10)
            elif name=='welcome_install':b.setFlat(True);layout.addSpacing(10)
            layout.addWidget(b)
        layout.addWidget(QLabel(tr('Proyectos recientes')));self.recents=QListWidget();self.recents.setObjectName('recent_projects');self.recents.itemDoubleClicked.connect(self.open_recent);self.recents.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu);self.recents.customContextMenuRequested.connect(self.context);layout.addWidget(self.recents,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status);self.refresh()
    def refresh(self):
        self.recents.clear();prefs=getattr(self.win.backend.ws,'app_settings',None)
        for row in prefs.data['recent_projects'] if prefs else []:
            from PySide6.QtWidgets import QListWidgetItem
            exists=Path(row['path']).is_file();item=QListWidgetItem(row['name']+' · '+Path(row['path']).parent.name+('' if exists else ' · '+tr('No encontrado')))
            item.setData(Qt.ItemDataRole.UserRole,row['path']);item.setToolTip(row['path']+'\n'+row['opened']);self.recents.addItem(item)
        from .. import __version__
        self.status.setText(tr('✓ Redemption configurado · ✓ Catálogos listos')+'\n'+__version__)
    def open_recent(self,item):
        self.win.guard(lambda:self.win.open_path(item.data(Qt.ItemDataRole.UserRole)))
    def context(self,pos):
        item=self.recents.itemAt(pos)
        if not item:return
        path=item.data(Qt.ItemDataRole.UserRole);menu=QMenu(self)
        menu.addAction(tr('Abrir'),lambda:self.open_recent(item));menu.addAction(tr('Abrir carpeta'),lambda:open_folder(Path(path).parent))
        prefs=getattr(self.win.backend.ws,'app_settings',None)
        if prefs:menu.addAction(tr('Quitar de recientes'),lambda:(prefs.remove_recent(path),self.refresh()))
        menu.exec(self.recents.mapToGlobal(pos))


def open_example(win,name):
    if not win.can_leave():return
    from ..product import copy_example
    ws=win.backend.ws;path=ws.output('chronicles/'+name+'/project.yaml');clean=False
    if path.exists():
        choice=QMessageBox(win);choice.setWindowTitle(tr('Ejemplo disponible'));choice.setText(tr('Puedes abrir tu copia o crear una copia limpia sin sustituir tu trabajo.'))
        own=choice.addButton(tr('Abrir mi copia'),QMessageBox.ButtonRole.AcceptRole);fresh=choice.addButton(tr('Crear copia limpia'),QMessageBox.ButtonRole.ActionRole);choice.addButton(tr('Cancelar'),QMessageBox.ButtonRole.RejectRole);choice.exec()
        if choice.clickedButton() not in (own,fresh):return
        clean=choice.clickedButton()==fresh
    win.open_path(copy_example(ws,name,clean));win.open_project_guide()


class PlayWorker(QObject):
    progress=Signal(str);done=Signal(object);failed=Signal(str);completed=Signal()
    def __init__(self,backend,source):super().__init__();self.backend=backend;self.source=source
    def run(self):
        try:
            from ..playtest import prepare_playtest
            self.done.emit(prepare_playtest(self.backend,self.source,self.progress.emit))
        except Exception as error:self.failed.emit(str(error))
        finally:self.completed.emit()


def playtest(win):
    if getattr(win.backend,'restart_required',False):raise ValueError(tr('Reinicia el editor para aplicar la instalación o la carpeta de proyectos seleccionada.'))
    if not win.doc or win.busy or not win.commit_properties():return
    validation=win.validate_project()
    if not validation.valid:
        win.bottom_tabs.setCurrentIndex(0);win.build_dock.show()
        for i,p in enumerate(validation.problems):
            if p.severity=='ERROR':win.problem_table.selectRow(i);win.problem_selected(i,0);break
        return
    if not win.save_project():return
    from ..playtest import current_build
    if not current_build(win.backend.ws,win.doc.snapshot()):win.show_bottom(1);win.log.clear()
    from ..deployment import game_running
    if game_running():raise ValueError(tr('Cierra Vampire antes de iniciar otra prueba. No se ha cerrado el juego automáticamente.'))
    win.busy=True;win.splitter.setEnabled(False);win.actions['playtest'].setEnabled(False)
    refresh_status(win)
    win.play_thread=QThread(win);win.play_worker=PlayWorker(win.backend,win.doc.snapshot());win.play_worker.moveToThread(win.play_thread)
    win.play_thread.started.connect(win.play_worker.run);win.play_worker.progress.connect(win.append_build_progress)
    result=[];win.play_worker.done.connect(result.append)
    def failed(text):
        win.show_bottom(1);win.log.appendPlainText(diagnostic(text));QMessageBox.warning(win,tr('No se pudo iniciar la prueba'),diagnostic(text))
    win.play_worker.failed.connect(failed)
    win.play_worker.completed.connect(win.play_thread.quit);win.play_worker.completed.connect(win.play_worker.deleteLater)
    def finished():
        win.busy=False;win.splitter.setEnabled(True);win.actions['playtest'].setEnabled(True);win.play_thread.deleteLater()
        if not result:return
        win.last_build=result[0]['report'];ident=win.doc.data['chronicle']['id']
        prefs=getattr(win.backend.ws,'app_settings',None)
        if prefs and prefs.data.get('show_playtest_hint',True):
            dialog=QMessageBox(win);dialog.setWindowTitle(tr('Probar en Redemption'));dialog.setText(tr('Redemption se abrirá con tu crónica preparada.\nDentro del juego: Multiplayer → LAN → New Game → ')+win.doc.data['chronicle']['name']+tr('\nRCM no automatiza los menús del juego.'))
            check=QCheckBox(tr('No volver a mostrar'));dialog.setCheckBox(check);dialog.exec()
            prefs.data['show_playtest_hint']=not check.isChecked();prefs.save()
        def launch():
            from ..playtest import launch_playtest
            win.game_process,win.play_record=launch_playtest(win.backend.ws,ident);win.game_timer.start();refresh_status(win)
        win.guard(launch)
    win.play_thread.finished.connect(finished);win.play_thread.start()


def refresh_status(win):
    from ..playtest import ProjectStatus,current_build,current_deploy
    status=ProjectStatus(last_playtest=getattr(win,'play_record',None),game_running=bool(getattr(win,'game_process',None)))
    if win.doc:
        status.dirty=win.doc.modified or bool(win.pending_properties())
        status.valid=getattr(win,'product_valid',None)
        if not status.dirty:
            report=current_build(win.backend.ws,win.doc.snapshot())
            status.build='current' if report else 'stale'
            if report:status.deploy='current' if current_deploy(win.backend.ws,report) else 'stale'
        else:status.build=status.deploy='stale'
        if win.busy:label=tr('● Preparando prueba…')
        elif status.valid is False:label=tr('✕ Hay errores')
        elif status.dirty:label=tr('● Cambios sin guardar')
        elif status.valid and status.build=='current' and status.deploy=='current':label=tr('✓ Lista para probar')
        else:label=tr('● Necesita actualizarse')
        win.product_status.setText(label)
        validation_label=tr('Proyecto válido') if status.valid is True else tr('Hay errores por corregir') if status.valid is False else tr('Validación pendiente')
        details=[tr('Cambios sin guardar') if status.dirty else tr('Guardado'),validation_label,tr('Construcción actualizada') if status.build=='current' else tr('Necesita construir'),tr('Prueba preparada') if status.deploy=='current' else tr('Necesita preparar la prueba')]
        win.product_status.setToolTip('\n'.join(details))
    else:win.product_status.setText(tr('Abre el tutorial o crea una crónica para empezar.'));win.product_status.setToolTip('')
    win.project_status=status
    win.product_stack.setCurrentWidget(win.splitter if win.doc else win.welcome)
    if not win.doc:win.build_dock.hide()
    win.actions['playtest'].setEnabled(bool(win.doc) and not win.busy)


def poll_game(win):
    process=getattr(win,'game_process',None)
    if process is None:return
    code=process.poll()
    if code is None:return
    from ..playtest import finish_playtest
    win.play_record=finish_playtest(win.backend.ws,win.play_record,code);win.game_process=None;win.game_timer.stop()
    try:win.debug_panel.read_trace()
    except (OSError,ValueError):pass
    win.statusBar().showMessage(tr('Playtest terminado. Abre Prueba / Depuración para ver el registro.'),15000);refresh_status(win)
    if win.play_record.get('profile_compatibility_error'):
        win.show_bottom(1);win.log.appendPlainText(diagnostic(win.play_record['profile_compatibility_error']))
        QMessageBox.warning(win,tr('No se pudo preparar el inventario guardado'),tr('Revisa el registro antes de abrir otra crónica. Tu personaje guardado no se ha modificado.'))


def settings_dialog(win):
    if win.busy:raise ValueError(tr('Espera a que termine la compilación.'))
    prefs=getattr(win.backend.ws,'app_settings',None)
    if not prefs:raise ValueError(tr('Abre el editor desde la aplicación para configurar preferencias globales.'))
    dialog=QDialog(win);dialog.setObjectName('settings_dialog');dialog.setWindowTitle(tr('Configuración'));dialog.resize(660,450);layout=QVBoxLayout(dialog);form=QFormLayout();layout.addLayout(form)
    lang=QComboBox();lang.setObjectName('settings_language');lang.addItem('English','en');lang.addItem('Español','es');lang.setCurrentIndex(lang.findData(prefs.data['language']));form.addRow(tr('Idioma (al reiniciar)'),lang)
    workspace=QLineEdit(str(win.backend.ws.root));workspace.setObjectName('settings_workspace');form.addRow(tr('Tus proyectos (al reiniciar)'),workspace)
    exe=QLineEdit(str(win.backend.ws.game/'Vampire.exe') if win.backend.ws.game else '');exe.setObjectName('settings_executable');row=QHBoxLayout();row.addWidget(exe,1)
    def pick():
        path,_=QFileDialog.getOpenFileName(dialog,tr('Selecciona Vampire.exe'),exe.text(),tr('Redemption (Vampire.exe)'))
        if path:exe.setText(path)
    browse=QPushButton(tr('Elegir…'));browse.clicked.connect(pick);row.addWidget(browse);form.addRow(tr('Redemption'),row)
    autosave=QSpinBox();autosave.setRange(0,600);autosave.setSuffix(tr(' segundos (0 desactiva)'));autosave.setValue(prefs.data.get('autosave_seconds',30));form.addRow(tr('Recuperación automática'),autosave)
    safe=QCheckBox(tr('Iniciar sin visor 3D (al reiniciar)'));safe.setChecked(prefs.data.get('safe_mode',False));form.addRow(safe)
    hint=QCheckBox(tr('Mostrar ayuda al iniciar una prueba'));hint.setChecked(prefs.data.get('show_playtest_hint',True));form.addRow(hint)
    from .wtd import import_widget
    import_widget(win,layout)
    from .content_libraries import import_widget as import_library_widget
    import_library_widget(win,layout)
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);layout.addWidget(buttons)
    def accept():
        try:
            from ..product import verify_installation
            from ..product import validate_workspace
            game=verify_installation(Path(exe.text()).parent)
            validate_workspace(workspace.text(),game)
            previous=prefs.data.copy()
            prefs.data.update(language=lang.currentData(),workspace=str(Path(workspace.text()).resolve()),game_installation=str(game),safe_mode=safe.isChecked(),autosave_seconds=autosave.value(),show_playtest_hint=hint.isChecked())
            try:prefs.save()
            except (ValueError,OSError):prefs.data=previous;raise
            win.backend.restart_required=game!=win.backend.ws.game or Path(workspace.text()).resolve()!=win.backend.ws.root
            win.autosave_timer.setInterval(max(1,autosave.value())*1000)
            if autosave.value():win.autosave_timer.start()
            else:win.autosave_timer.stop()
            win.statusBar().showMessage(tr('Preferencias guardadas. Los cambios de idioma, instalación, proyectos y visor se aplican al reiniciar.'),10000);dialog.accept()
        except (ValueError,OSError) as error:QMessageBox.warning(dialog,tr('Revisa la configuración'),diagnostic(error))
    buttons.accepted.connect(accept);buttons.rejected.connect(dialog.reject);dialog.exec()


def reset_layout(win):
    win.resize(1430,900);win.splitter.setSizes([220,740,410]);win.center_tabs.setCurrentIndex(0)
    win.campaign_panel.panes.setSizes([150,400]);win.build_dock.hide()


def restore_ui(win):
    prefs=getattr(win.backend.ws,'app_settings',None)
    if not prefs:return
    data=prefs.data
    if data.get('window_geometry'):
        win.restoreGeometry(QByteArray.fromBase64(data['window_geometry'].encode()))
        from PySide6.QtWidgets import QApplication
        if not any(s.availableGeometry().intersects(win.frameGeometry()) for s in QApplication.screens()):
            rect=QApplication.primaryScreen().availableGeometry();win.move(rect.center()-win.rect().center())
    if data.get('window_state'):win.restoreState(QByteArray.fromBase64(data['window_state'].encode()))
    win.build_dock.hide()
    if data.get('splitter_sizes'):win.splitter.setSizes(data['splitter_sizes'])
    win.center_tabs.setCurrentIndex(min(data.get('last_tab',0),win.center_tabs.count()-1))
    interval=data.get('autosave_seconds',30)
    if interval:win.autosave_timer.setInterval(interval*1000)
    else:win.autosave_timer.stop()


def save_ui(win):
    prefs=getattr(win.backend.ws,'app_settings',None)
    if prefs:
        prefs.data.update(window_geometry=base64.b64encode(bytes(win.saveGeometry())).decode(),window_state=base64.b64encode(bytes(win.saveState())).decode(),splitter_sizes=win.splitter.sizes(),last_tab=win.center_tabs.currentIndex());prefs.save()
    lock=getattr(win,'project_lock',None)
    if lock:lock.release()


def close_project(win):
    if not win.can_leave():return
    lock=getattr(win,'project_lock',None)
    if lock:lock.release();win.project_lock=None
    win.doc=None;win.refresh();win.welcome.refresh();refresh_status(win)


def duplicate_selection(win):
    if not win.doc or not win.commit_properties():return
    path=win.campaign_panel.path if win.center_tabs.currentWidget()==win.campaign_panel else win.selection
    source=win.doc.snapshot()
    if hasattr(win.doc,'campaign') and path and path[0] not in ('scenes','quests'):
        path=('scenes',win.doc.active,*path)
    from ..product_edit import duplicate_entity
    candidate,selected=duplicate_entity(source,path)
    validation=win.backend.validate(candidate)
    if not validation.valid:raise ValueError('\n'.join(p.message for p in validation.problems if p.severity=='ERROR'))
    win.doc.data=candidate;win.changed(True)
    if selected[0] in ('scenes','quests'):win.campaign_panel.navigate(selected)
    else:win.select(selected)


def duplicate_project(win):
    if not win.doc or not win.commit_properties():return
    name,ok=QInputDialog.getText(win,tr('Duplicar crónica'),tr('Nombre de la copia'))
    if not ok or not name.strip():return
    from ..product import project_id
    from ..project_safety import duplicate_project
    ident=project_id(name,win.backend.ws.root);path=win.backend.ws.output('chronicles/'+ident)
    doc=duplicate_project(win.backend.ws,win.doc.snapshot(),path,name,ident,win.doc.path.parent)
    if win.can_leave():win.open_path(doc.path)


def backups_dialog(win):
    if not win.doc:return
    directory=win.backend.ws.output('backups/'+win.doc.data['chronicle']['id']);rows=sorted(directory.glob('*.yaml'),reverse=True)
    if not rows:raise ValueError(tr('Todavía no hay versiones guardadas. Se crean al guardar cambios.'))
    dialog=QDialog(win);dialog.setWindowTitle(tr('Versiones guardadas'));dialog.resize(640,380);layout=QVBoxLayout(dialog);listing=QListWidget();layout.addWidget(listing)
    for path in rows:listing.addItem(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(path.stat().st_mtime))+' · '+str(path.stat().st_size)+' bytes · '+path.name)
    listing.setCurrentRow(0);bar=QHBoxLayout();layout.addLayout(bar)
    def restore():
        if QMessageBox.question(dialog,tr('Restaurar versión'),tr('¿Restaurar esta versión? Primero se guardará una copia del estado actual.'),QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return
        from ..project_safety import restore_backup
        win.guard(lambda:restore_backup(win.doc,rows[listing.currentRow()]));win.refresh();dialog.accept()
    def as_copy():
        from ..document import Document
        from ..product import project_id
        from ..project_safety import duplicate_project
        saved=Document.load(win.backend.ws,rows[listing.currentRow()]);name=saved.data['chronicle']['name']+tr(' (copia recuperada)');ident=project_id(name,win.backend.ws.root)
        copy=duplicate_project(win.backend.ws,saved.snapshot(),win.backend.ws.output('chronicles/'+ident),name,ident)
        if win.can_leave():win.open_path(copy.path);dialog.accept()
    for label,cb in [(tr('Abrir como copia'),as_copy),(tr('Restaurar'),restore),(tr('Cerrar'),dialog.reject)]:
        b=QPushButton(label);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bar.addWidget(b)
    dialog.exec()


def help_document(win,name):
    from .i18n import language
    import sys
    base=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[3]
    localized=name+'.en.md' if language()=='en' else name+'.md'
    path=base/'docs'/localized
    win.guide_panel.text.setMarkdown(path.read_text(encoding='utf8'));win.center_tabs.setCurrentWidget(win.guide_panel)


def install(win):
    old=win.takeCentralWidget();win.product_stack=QStackedWidget();win.product_stack.addWidget(old);win.welcome=Welcome(win);win.product_stack.addWidget(win.welcome);win.setCentralWidget(win.product_stack)
    toolbar=win.findChild(QToolBar);toolbar.setObjectName('project_toolbar')
    action=QAction(tr('PROBAR EN REDEMPTION'),win);action.setObjectName('action_playtest');action.setShortcut('F5');action.triggered.connect(lambda:win.guard(lambda:playtest(win)));win.actions['playtest']=action;toolbar.addAction(action)
    win.actions['build'].setText(tr('Construir'));win.actions['build'].setShortcut('Ctrl+B')
    duplicate=QAction(tr('Duplicar selección'),win);duplicate.setShortcut('Ctrl+D');duplicate.triggered.connect(lambda:win.guard(lambda:duplicate_selection(win)));win.edit_menu.addAction(duplicate);win.actions['duplicate']=duplicate
    win.actions['save_as'].setText(tr('Duplicar crónica…'))
    win.actions['save_as'].triggered.disconnect();win.actions['save_as'].triggered.connect(lambda:win.guard(lambda:duplicate_project(win)))
    win.product_status=QLabel();win.product_status.setObjectName('project_status');win.statusBar().addPermanentWidget(win.product_status)
    file_menu=win.file_menu;file_menu.addAction(tr('Versiones guardadas…'),lambda:win.guard(lambda:backups_dialog(win)));file_menu.addAction(tr('Cerrar crónica'),lambda:close_project(win));file_menu.addAction(tr('Salir'),win.close)
    tools=win.menuBar().addMenu(tr('Herramientas'));tools.addAction(tr('Configuración…'),lambda:win.guard(lambda:settings_dialog(win))).setObjectName('action_settings')
    win.tools_menu=tools
    tools.addAction(tr('Abrir carpeta del proyecto'),lambda:open_folder(win.doc.path.parent if win.doc else win.backend.ws.root));tools.addAction(tr('Abrir mis proyectos'),lambda:open_folder(win.backend.ws.root))
    tools.addAction(tr('Abrir carpeta de la prueba'),lambda:open_folder(win.backend.ws.game/'RCM'/win.doc.data['chronicle']['id'] if win.doc else win.backend.ws.game/'RCM'))
    tools.addAction(tr('Crear acceso a la aplicación'),lambda:win.guard(lambda:__import__('rcm.shortcut',fromlist=['application_shortcut']).application_shortcut(win.backend.ws)))
    tools.addAction(tr('Diagnóstico de instalación…'),lambda:win.guard(lambda:doctor_dialog(win)))
    tools.addAction(tr('Crónicas desplegadas…'),lambda:win.guard(lambda:deployments_dialog(win)))
    view=win.menuBar().addMenu(tr('Ver'));view.addAction(tr('Restablecer disposición'),lambda:reset_layout(win));view.addAction(win.build_dock.toggleViewAction())
    win.view_menu=view
    for i in range(win.center_tabs.count()):view.addAction(win.center_tabs.tabText(i),lambda checked=False,i=i:win.center_tabs.setCurrentIndex(i))
    help_menu=win.help_menu
    tutorial_action=help_menu.addAction(tr('Tutorial rápido'),lambda:win.guard(lambda:open_example(win,'tutorial')));tutorial_action.setObjectName('help_tutorial')
    showcase_action=help_menu.addAction(tr('Showcase completo'),lambda:win.guard(lambda:open_example(win,'showcase')));showcase_action.setObjectName('help_showcase')
    help_menu.addAction(tr('Crónica de prueba: el refugio'),lambda:win.guard(lambda:open_example(win,'director_acceptance'))).setObjectName('help_director_acceptance')
    help_menu.addAction(tr('Prueba de autoría avanzada: el cargamento'),lambda:win.guard(lambda:open_example(win,'strict_acceptance'))).setObjectName('help_strict_acceptance')
    help_menu.addAction(tr('Laboratorio de autoría'),lambda:win.guard(lambda:open_example(win,'completion_lab'))).setObjectName('help_completion_lab')
    help_menu.addAction(tr('Director de escenas: guía'),lambda:win.guard(lambda:help_document(win,'CINEMATIC_DIRECTOR'))).setObjectName('help_director_guide')
    help_menu.addAction(tr('Crear paquete de soporte…'),lambda:win.guard(lambda:support_dialog(win)))
    help_menu.addAction(tr('Atajos'),lambda:win.guard(lambda:help_document(win,'SHORTCUTS')),'F1').setObjectName('help_shortcuts')
    help_menu.addAction(tr('Acerca de'),lambda:QMessageBox.information(win,tr('Acerca de'),'Redemption Chronicle Maker '+__import__('rcm').__version__+'\n\n'+tr('Herramienta de autoría no oficial para Vampire: The Masquerade — Redemption.')))
    preferred=('help_tutorial','help_showcase','help_project_guide','help_editor_guide','help_shortcuts')
    ordered=[next(a for a in help_menu.actions() if a.objectName()==name) for name in preferred]
    ordered += [a for a in help_menu.actions() if a.objectName() not in preferred]
    for action in ordered:help_menu.removeAction(action);help_menu.addAction(action)
    win.game_process=None;win.game_timer=QTimer(win);win.game_timer.setInterval(1500);win.game_timer.timeout.connect(lambda:poll_game(win))
    # Keep existing actions and shortcuts, while avoiding duplicate top-level groups.
    for action in win.campaign_menu.actions():win.chronicle_menu.addAction(action)
    win.menuBar().removeAction(win.campaign_menu.menuAction())
    win.menuBar().removeAction(win.package_menu.menuAction());win.tools_menu.addMenu(win.package_menu)
    for menu in (win.file_menu,win.edit_menu,win.view_menu,win.chronicle_menu,win.build_menu,win.tools_menu,win.help_menu):
        win.menuBar().removeAction(menu.menuAction());win.menuBar().addMenu(menu)
    restore_ui(win);refresh_status(win)
    win.setAcceptDrops(True)


def doctor_dialog(win):
    from ..diagnostics import diagnostic_report
    report=diagnostic_report(win.backend.ws);dialog=QDialog(win);dialog.setWindowTitle(tr('Diagnóstico de instalación'));dialog.resize(640,420);layout=QVBoxLayout(dialog)
    from PySide6.QtWidgets import QPlainTextEdit
    text=QPlainTextEdit(json.dumps(report,ensure_ascii=False,indent=2));text.setReadOnly(True);layout.addWidget(text)
    b=QPushButton(tr('Reconstruir catálogos'));layout.addWidget(b)
    def repair():
        # Only invalidate regenerateable workspace indices. Originals are read only.
        ws=win.backend.ws
        for name in ('levels','resources','scene_hints'):
            path=ws.output('cache/'+name+'.json')
            if path.is_file():ws.write('backups/catalogues/'+str(time.time_ns())+'_'+name+'.json',path.read_bytes());path.unlink()
        dialog.accept();QMessageBox.information(win,tr('Reinicia el editor'),tr('Los catálogos se reconstruirán al abrir el editor. Tus proyectos y los archivos originales se conservan.'))
    b.clicked.connect(lambda:win.guard(repair));dialog.exec()


def support_dialog(win):
    path,_=QFileDialog.getSaveFileName(win,tr('Crear paquete de soporte'),str(win.backend.ws.root/'support.zip'),tr('ZIP (*.zip)'))
    if not path:return
    from ..support import support_bundle
    support_bundle(win.backend.ws,path)
    win.statusBar().showMessage(tr('Paquete de soporte creado localmente. No se ha enviado.'))


def deployments_dialog(win):
    from ..managed_deployments import list_deployments,remove_deployment
    rows=list_deployments(win.backend.ws);dialog=QDialog(win);dialog.setWindowTitle(tr('Crónicas desplegadas'));dialog.resize(650,400);layout=QVBoxLayout(dialog);listing=QListWidget();layout.addWidget(listing)
    for row in rows:listing.addItem(row['id']+' · '+tr('Modificada' if row['modified'] else 'Preparada'));listing.item(listing.count()-1).setToolTip(str(row['path']))
    listing.setCurrentRow(0);bar=QHBoxLayout();layout.addLayout(bar)
    def selected():
        if listing.currentRow()<0:raise ValueError(tr('No hay crónicas administradas'))
        return rows[listing.currentRow()]
    def remove():
        row=selected()
        if QMessageBox.question(dialog,tr('Retirar crónica'),tr('¿Retirar sólo los archivos propios sin modificar? Se conservan partidas, registros y archivos ajenos.'),QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            remove_deployment(win.backend.ws,row['id']);dialog.accept()
    for label,cb in [(tr('Jugar'),lambda:__import__('rcm.deployment',fromlist=['run_game']).run_game(win.backend.ws,selected()['id'])),(tr('Abrir carpeta'),lambda:open_folder(selected()['path'])),(tr('Crear acceso'),lambda:__import__('rcm.shortcut',fromlist=['chronicle_shortcut']).chronicle_shortcut(win.backend.ws,selected()['id'],selected()['id'])),(tr('Retirar'),remove)]:
        b=QPushButton(label);b.clicked.connect(lambda checked=False,cb=cb:win.guard(cb));bar.addWidget(b)
    dialog.exec()

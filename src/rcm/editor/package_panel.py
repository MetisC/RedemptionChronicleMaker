from .i18n import tr
"""Explicit file review for package operations, sharing the CLI backend."""
import json
from PySide6.QtWidgets import QFileDialog,QMessageBox
from .. import packages


def menu(win):
    bar=win.menuBar().addMenu(tr('Paquetes'))
    win.package_menu=bar
    for title,fn in [(tr('Exportar proyecto…'),export_project),(tr('Importar proyecto…'),import_project),(tr('Crear paquete de crónica…'),create_package),(tr('Inspeccionar / instalar paquete…'),install_package),(tr('Desinstalar paquete…'),uninstall_package)]:
        bar.addAction(title,lambda checked=False,fn=fn:win.guard(lambda:fn(win)))


def export_project(win):
    if not win.doc or not win.commit_properties():return
    path,_=QFileDialog.getSaveFileName(win,tr('Exportar fuentes propias'),str(win.backend.ws.root/'chronicles'/'project.rcmproject'),tr('Proyecto RCM (*.rcmproject)'))
    if path:
        packages.export_project(win.backend.ws,win.doc.snapshot(),path)
        win.statusBar().showMessage(tr('Proyecto exportado con sus recursos propios'))


def import_project(win):
    if not win.can_leave():return
    path,_=QFileDialog.getOpenFileName(win,tr('Importar proyecto'),'',tr('Proyecto RCM (*.rcmproject)'))
    if not path:return
    target=QFileDialog.getExistingDirectory(win,tr('Carpeta vacía del workspace'),str(win.backend.ws.root/'chronicles'))
    if not target:return
    doc=packages.import_project(win.backend.ws,path,target)
    if doc.snapshot().get('resources',{}).get('scripts'):
        QMessageBox.information(win,tr('Java propio importado'),tr('El proyecto contiene Java propio. Revisa sus fuentes antes de compilarlo o ejecutarlo.'))
    win.open_path(doc.path)


def create_package(win):
    if not win.doc or not win.commit_properties():return
    ident=win.doc.data['chronicle']['id']
    from ..service import source_fingerprint,build_inputs_fingerprint
    report=json.loads(win.backend.ws.output('build/'+ident+'/build_report.json').read_text(encoding='utf8'))
    if report.get('authoring_source_sha256')!=source_fingerprint(win.doc.snapshot()):raise ValueError(tr('El proyecto cambió desde el build; vuelve a compilar'))
    if report.get('build_inputs_sha256')!=build_inputs_fingerprint(win.backend.ws,win.doc.snapshot()):raise ValueError(tr('Java/texturas propios cambiaron; vuelve a compilar'))
    path,_=QFileDialog.getSaveFileName(win,tr('Paquete de crónica'),str(win.backend.ws.root/'build'/ident/(ident+'.rcmpack')),tr('Crónica RCM (*.rcmpack)'))
    if path:packages.create_package(win.backend.ws,ident,path);win.statusBar().showMessage(tr('Paquete creado; requiere el juego original'))


def install_package(win,path=None):
    if path is None:path,_=QFileDialog.getOpenFileName(win,tr('Revisar paquete'),'',tr('Crónica RCM (*.rcmpack)'))
    if not path:return
    manifest,files=packages.inspect_package(path)
    detail=manifest['name']+tr('\nVersión ')+manifest['version']+tr('\nDestino: RCM/')+manifest['id']+'\n'+('\n'.join(manifest['files']))
    contains_code=any(name.endswith('.class') for name in files)
    if contains_code:detail+=tr('\n\nContiene Java ejecutable: sus clases se ejecutarán dentro del juego. El manifest y sus hashes no acreditan su autoría. Instala sólo paquetes que hayas revisado y en los que confíes.')
    if QMessageBox.question(win,tr('Instalar paquete revisado'),detail,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
        packages.install_package(win.backend.ws,path,contains_code);win.statusBar().showMessage(tr('Instalado en su carpeta RCM/')+manifest['id'])


def uninstall_package(win):
    registry=packages.installed(win.backend.ws)
    from PySide6.QtWidgets import QInputDialog
    if not registry:raise ValueError(tr('No hay paquetes administrados por RCM'))
    ident,ok=QInputDialog.getItem(win,tr('Desinstalar paquete'),tr('Paquete'),sorted(registry),0,False)
    if ok and QMessageBox.question(win,tr('Desinstalar'),tr('Eliminar sólo los archivos registrados de ')+ident+tr('? Partidas/logs y archivos ajenos se conservan.'))==QMessageBox.StandardButton.Yes:
        packages.uninstall_package(win.backend.ws,ident);win.statusBar().showMessage(tr('Archivos del paquete retirados; backup en research/package_backups'))

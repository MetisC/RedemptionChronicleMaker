"""Explicit file review for package operations, sharing the CLI backend."""
import json
from PySide6.QtWidgets import QFileDialog,QMessageBox
from .. import packages


def menu(win):
    bar=win.menuBar().addMenu('Paquetes')
    for title,fn in [('Exportar proyecto…',export_project),('Importar proyecto…',import_project),('Crear paquete de crónica…',create_package),('Inspeccionar / instalar paquete…',install_package),('Desinstalar paquete…',uninstall_package)]:
        bar.addAction(title,lambda checked=False,fn=fn:win.guard(lambda:fn(win)))


def export_project(win):
    if not win.doc or not win.commit_properties():return
    path,_=QFileDialog.getSaveFileName(win,'Exportar fuentes propias',str(win.backend.ws.root/'chronicles'/'project.rcmproject'),'Proyecto RCM (*.rcmproject)')
    if path:
        packages.export_project(win.backend.ws,win.doc.snapshot(),path)
        win.statusBar().showMessage('Proyecto exportado con sus recursos propios')


def import_project(win):
    if not win.can_leave():return
    path,_=QFileDialog.getOpenFileName(win,'Importar proyecto','','Proyecto RCM (*.rcmproject)')
    if not path:return
    target=QFileDialog.getExistingDirectory(win,'Carpeta vacía del workspace',str(win.backend.ws.root/'chronicles'))
    if not target:return
    doc=packages.import_project(win.backend.ws,path,target)
    if doc.snapshot().get('resources',{}).get('scripts'):
        QMessageBox.information(win,'Java propio importado','El proyecto contiene Java propio. Revisa sus fuentes antes de compilarlo o ejecutarlo.')
    win.doc=doc;win.selection=('chronicle',);win.refresh()


def create_package(win):
    if not win.doc or not win.commit_properties():return
    ident=win.doc.data['chronicle']['id']
    from ..service import source_fingerprint,build_inputs_fingerprint
    report=json.loads(win.backend.ws.output('build/'+ident+'/build_report.json').read_text(encoding='utf8'))
    if report.get('authoring_source_sha256')!=source_fingerprint(win.doc.snapshot()):raise ValueError('El proyecto cambió desde el build; vuelve a compilar')
    if report.get('build_inputs_sha256')!=build_inputs_fingerprint(win.backend.ws,win.doc.snapshot()):raise ValueError('Java/texturas propios cambiaron; vuelve a compilar')
    path,_=QFileDialog.getSaveFileName(win,'Paquete de crónica',str(win.backend.ws.root/'build'/ident/(ident+'.rcmpack')),'Crónica RCM (*.rcmpack)')
    if path:packages.create_package(win.backend.ws,ident,path);win.statusBar().showMessage('Paquete creado; requiere el juego original')


def install_package(win):
    path,_=QFileDialog.getOpenFileName(win,'Revisar paquete','','Crónica RCM (*.rcmpack)')
    if not path:return
    manifest,files=packages.inspect_package(path)
    detail=manifest['name']+'\nVersión '+manifest['version']+'\nDestino: RCM/'+manifest['id']+'\n'+('\n'.join(manifest['files']))
    contains_code=any(name.endswith('.class') for name in files)
    if contains_code:detail+='\n\nContiene Java ejecutable: sus clases se ejecutarán dentro del juego. El manifest y sus hashes no acreditan su autoría. Instala sólo paquetes que hayas revisado y en los que confíes.'
    if QMessageBox.question(win,'Instalar paquete revisado',detail,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
        packages.install_package(win.backend.ws,path,contains_code);win.statusBar().showMessage('Instalado en su carpeta RCM/'+manifest['id'])


def uninstall_package(win):
    registry=packages.installed(win.backend.ws)
    from PySide6.QtWidgets import QInputDialog
    if not registry:raise ValueError('No hay paquetes administrados por RCM')
    ident,ok=QInputDialog.getItem(win,'Desinstalar paquete','Paquete',sorted(registry),0,False)
    if ok and QMessageBox.question(win,'Desinstalar','Eliminar sólo los archivos registrados de '+ident+'? Partidas/logs y archivos ajenos se conservan.')==QMessageBox.StandardButton.Yes:
        packages.uninstall_package(win.backend.ws,ident);win.statusBar().showMessage('Archivos del paquete retirados; backup en research/package_backups')

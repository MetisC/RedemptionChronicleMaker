from .i18n import tr
from pathlib import Path
import argparse
import sys


def main(argv=None):
    from PySide6.QtWidgets import QApplication, QMessageBox,QProgressDialog
    from PySide6.QtGui import QFont
    from ..service import Backend
    from ..paths import Workspace
    parser = argparse.ArgumentParser(description="Redemption Chronicle Maker Desktop Editor")
    parser.add_argument("project", nargs="?", type=Path)
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--settings-directory", type=Path, default=None)
    parser.add_argument("--game", type=Path, default=None)
    parser.add_argument('--safe-mode',action='store_true',help=tr('Abrir editor de datos sin crear el contexto OpenGL'))
    parser.add_argument('--reset-settings',action='store_true',help=tr('Respaldar configuración y usar valores seguros'))
    parser.add_argument('--smoke-test',action='store_true',help=tr('Prueba del editor distribuido: abrir ejemplo, comprobar renderer y compilar'))
    args = parser.parse_args(argv)
    from ..deployment import default_game
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("Redemption Chronicle Maker")
    from .identity import set_identity
    set_identity(app)
    app.setStyle("Fusion")
    from .theme import editor_palette
    app.setPalette(editor_palette(app.palette()))
    app.setFont(QFont("Segoe UI", 10))
    try:
        from ..app_settings import AppSettings,default_workspace
        preferences=AppSettings(args.settings_directory)
        if args.workspace:preferences.migrate(args.workspace)
        args.workspace=args.workspace or Path(preferences.data.get('workspace',default_workspace()))
        args.game=args.game or (Path(preferences.data['game_installation']) if preferences.data.get('game_installation') else None) or default_game(args.workspace)
        ws=Workspace(args.workspace,args.game);ws.app_settings=preferences
        if args.reset_settings:
            from ..startup import reset_settings
            reset_settings(ws)
        from .i18n import configure, install_qt, diagnostic
        configure(ws)
        install_qt(app)
        from ..startup import cache_errors,prepare_workspace
        first_run=not preferences.data.get('setup_complete',False)
        if first_run or not args.game:
            from .product_ui import SetupDialog
            dialog=SetupDialog(preferences,args.game,args.workspace)
            if not dialog.exec():return 0
            ws=dialog.ws;args.workspace=ws.root;args.game=ws.game
            preferences.data['language']=dialog.language.currentData()
            configure(ws);install_qt(app)
        else:
            from ..product import validate_workspace,verify_installation
            verify_installation(args.game)
            ws=validate_workspace(args.workspace,args.game);ws.app_settings=preferences
        from ..product import ensure_runtime_root
        # Check the managed runtime's permissions before the expensive scan.
        ensure_runtime_root(ws.game)
        if cache_errors(ws) or not ws.output('cache/toolchain/classes.zip').is_file() or not ws.output('cache/toolchain/ecj-3.26.0.jar').is_file():
            # Scanning reads archives on a worker; the dialog stays responsive.
            from PySide6.QtCore import QThread,QObject,Signal,Qt
            class Worker(QObject):
                done=Signal();failed=Signal(str);progress=Signal(str)
                def run(self):
                    try:prepare_workspace(ws,lambda text:self.progress.emit(diagnostic(text)))
                    except Exception as error:self.failed.emit(str(error))
                    finally:self.done.emit()
            progress=QProgressDialog(tr('Preparando catálogos originales…'),'',0,0);progress.setCancelButton(None);progress.setWindowModality(Qt.WindowModality.ApplicationModal)
            worker=Worker();thread=QThread();worker.moveToThread(thread);errors=[]
            worker.progress.connect(progress.setLabelText);worker.failed.connect(errors.append);worker.done.connect(progress.accept);worker.done.connect(thread.quit);thread.started.connect(worker.run);thread.start();progress.exec();thread.quit();thread.wait()
            if errors:raise ValueError(errors[0])
        preferences.data.update(workspace=str(ws.root),game_installation=str(ws.game),setup_complete=True)
        preferences.save()
        backend=Backend(ws);backend.safe_mode=args.safe_mode or preferences.data.get('safe_mode',False)
        from .window import MainWindow
        window = MainWindow(backend)
        if args.smoke_test and not args.project:args.project=ws.output('chronicles/tutorial/project.yaml')
        if args.project:
            window.open_path(args.project)
        window.show()
        if preferences.warning:window.statusBar().showMessage(diagnostic(preferences.warning),20000)
        # A local crash report, never uploaded. Unexpected UI exceptions are visible.
        import traceback,time
        def unexpected(kind,error,tb):
            try:
                text='RCM '+__import__('rcm').__version__+'\n'+traceback.format_exception(kind,error,tb)[-1]+'\n'+''.join(traceback.format_tb(tb))
                ws.write('build/editor/crash_'+str(time.time_ns())+'.log',text)
                QMessageBox.critical(window,tr('Error inesperado'),tr('RCM encontró un error inesperado. Guarda una copia de tu trabajo y crea un paquete de soporte desde Ayuda.')+'\n'+str(error))
            except Exception:pass
        sys.excepthook=unexpected
        if args.smoke_test:
            from .smoke import start
            start(window,app)
    except (ValueError, OSError) as error:
        from .i18n import diagnostic
        QMessageBox.critical(None, tr("No se pudo abrir el editor"), diagnostic(error) + tr("\nComprueba los catálogos del workspace."))
        return 1
    return app.exec()

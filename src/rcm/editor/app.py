from pathlib import Path
import argparse
import sys


def main(argv=None):
    from PySide6.QtWidgets import QApplication, QMessageBox,QFileDialog,QProgressDialog
    from PySide6.QtGui import QFont
    from .window import MainWindow
    from ..service import Backend
    from ..paths import Workspace
    parser = argparse.ArgumentParser(description="Redemption Chronicle Maker Desktop Editor")
    parser.add_argument("project", nargs="?", type=Path)
    source_root = Path(__file__).resolve().parents[3]
    parser.add_argument("--workspace", type=Path, default=source_root if (source_root / "cache/levels.json").exists() else Path.cwd())
    parser.add_argument("--game", type=Path, default=None)
    parser.add_argument('--safe-mode',action='store_true',help='Abrir editor de datos sin crear el contexto OpenGL')
    parser.add_argument('--reset-settings',action='store_true',help='Respaldar configuración y usar valores seguros')
    parser.add_argument('--smoke-test',action='store_true',help='Prueba del editor distribuido: abrir ejemplo, comprobar renderer y compilar')
    args = parser.parse_args(argv)
    from ..deployment import default_game
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("Redemption Chronicle Maker")
    app.setStyle("Fusion")
    from .theme import editor_palette
    app.setPalette(editor_palette(app.palette()))
    app.setFont(QFont("Segoe UI", 10))
    try:
        args.game = args.game or default_game(args.workspace)
        ws=Workspace(args.workspace,args.game)
        if args.reset_settings:
            from ..startup import reset_settings
            reset_settings(ws)
        from ..startup import cache_errors,prepare_workspace
        if cache_errors(ws) and not args.game:
            selected=QFileDialog.getExistingDirectory(None,'Selecciona la instalación original de Redemption')
            if not selected:return 0
            from ..deployment import save_settings
            args.game=save_settings(ws,Path(selected));ws=Workspace(args.workspace,args.game)
        if cache_errors(ws) or not ws.output('cache/toolchain/classes.zip').is_file() or not ws.output('cache/toolchain/ecj-3.26.0.jar').is_file():
            # Scanning reads archives on a worker; the dialog stays responsive.
            from PySide6.QtCore import QThread,QObject,Signal,Qt
            class Worker(QObject):
                done=Signal();failed=Signal(str);progress=Signal(str)
                def run(self):
                    try:prepare_workspace(ws,self.progress.emit)
                    except Exception as error:self.failed.emit(str(error))
                    finally:self.done.emit()
            progress=QProgressDialog('Preparando catálogos originales…','',0,0);progress.setCancelButton(None);progress.setWindowModality(Qt.WindowModality.ApplicationModal)
            worker=Worker();thread=QThread();worker.moveToThread(thread);errors=[]
            worker.progress.connect(progress.setLabelText);worker.failed.connect(errors.append);worker.done.connect(progress.accept);worker.done.connect(thread.quit);thread.started.connect(worker.run);thread.start();progress.exec();thread.quit();thread.wait()
            if errors:raise ValueError(errors[0])
        backend=Backend(ws);backend.safe_mode=args.safe_mode
        window = MainWindow(backend)
        if args.smoke_test and not args.project:args.project=ws.output('chronicles/system_test/project.yaml')
        if args.project:
            window.open_path(args.project)
        window.show()
        if args.smoke_test:
            from .smoke import start
            start(window,app)
    except (ValueError, OSError) as error:
        QMessageBox.critical(None, "No se pudo abrir el editor", str(error) + "\nComprueba los catálogos del workspace.")
        return 1
    return app.exec()

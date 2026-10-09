"""Prepare a nearby-player copy via real editor controls; no game writes."""
from pathlib import Path
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def main():
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont, QFontDatabase
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QFileDialog, QDialogButtonBox, QLineEdit, QComboBox, QPlainTextEdit
    from rcm.paths import Workspace
    from rcm.service import Backend
    from rcm.editor.window import MainWindow

    ws = Workspace(ROOT, Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
    target = ws.output("chronicles/editor_playtest/project.yaml")
    if target.exists():
        raise ValueError("Playtest project already exists; open it in the editor instead of replacing it.")
    target.parent.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    app.setStyle("Fusion")
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow(Backend(ws))
    w.open_path(ROOT / "chronicles/editor_acceptance/project.yaml")
    w.show(); app.processEvents()
    failures = []

    def save_as_dialog():
        dialog = app.activeModalWidget()
        try:
            assert isinstance(dialog, QFileDialog)
            dialog.setDirectory(str(target.parent))
            dialog.selectFile(str(target))
            buttons = dialog.findChild(QDialogButtonBox)
            QTest.mouseClick(buttons.button(QDialogButtonBox.StandardButton.Save), Qt.MouseButton.LeftButton)
        except Exception as error:
            failures.append(str(error))
            if dialog:
                dialog.reject()

    QTimer.singleShot(100, save_as_dialog)
    w.actions["save_as"].trigger()
    assert not failures, failures
    assert w.doc.path == target, w.doc.path
    w.nav.setCurrentItem(w.nav_items[("chronicle",)]); app.processEvents()
    field = w.properties.widget().findChild(QLineEdit, "chronicle_id")
    field.setText("editor_playtest")
    QTest.keyClick(field, Qt.Key.Key_Return); app.processEvents()
    assert w.doc.data["chronicle"]["id"] == "editor_playtest"
    w.nav.setCurrentItem(w.nav_items[("actors", 0)]); app.processEvents()
    control = w.properties.widget().findChild(QComboBox, "actor_placement")
    control.setCurrentIndex(control.findData("near_player")); app.processEvents()
    w.properties.widget().findChild(QPlainTextEdit, "actor_comment").setPlainText("Copia para probar la Fase 2 con Victoria junto al jugador.")
    assert w.validate_project().valid
    reports = []
    w.build_completed.connect(reports.append)
    w.actions["build"].trigger()
    deadline = time.monotonic() + 50
    while w.busy and time.monotonic() < deadline:
        app.processEvents(); QTest.qWait(20)
    assert not w.busy and reports and reports[0]["status"] == "compiled-unverified-in-game", w.log.toPlainText()
    assert not w.doc.modified
    ws.write("build/editor/playtest_preparation.json", json.dumps({
        "source": str(target.relative_to(ROOT)), "parent": "chronicles/editor_acceptance/project.yaml",
        "created_using": "Qt editor Save As dialog, chronicle ID and actor placement controls; GUI build",
        "placement": "near_player", "class_versions": reports[0]["class_versions"], "native_engine_test": False
    }, ensure_ascii=False, indent=2))
    print("Playtest prepared via GUI: editor_playtest; Victoria near player; classfiles 45.3")
    w.close()


if __name__ == "__main__":
    main()

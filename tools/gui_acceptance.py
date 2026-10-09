"""Exercise the real Qt editor controls; never author the acceptance YAML directly.

Runs headlessly by default, preserving screenshots, source and compiled output.
Requires the optional editor dependencies. It does not launch or modify the game.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", action="store_true", help="Archive the previous acceptance YAML before recreating it")
    args = parser.parse_args()
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont, QFontDatabase
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QLineEdit, QPlainTextEdit, QComboBox, QDoubleSpinBox, QSpinBox, QPushButton, QDialogButtonBox, QMessageBox
    from rcm.paths import Workspace
    from rcm.service import Backend
    from rcm.editor.window import MainWindow, NewProjectDialog
    from rcm.editor.browser import ResourceDialog

    ws = Workspace(ROOT, Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
    path = ws.output("chronicles/editor_acceptance/project.yaml")
    if path.exists():
        if not args.repeat:
            raise ValueError("Acceptance project already exists; use --repeat to archive and recreate it.")
        backup = ws.output("build/tests/gui_previous")
        backup.mkdir(parents=True, exist_ok=True)
        for existing in [path, path.with_name(path.name + ".autosave")]:
            if existing.exists():
                ws.write(backup / (existing.name + "." + str(time.time_ns())), existing.read_bytes())
                existing.unlink()
    evidence = ws.output("build/editor/acceptance")
    evidence.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    # The offscreen Qt platform has no Windows font discovery; register the
    # installed Windows font solely for readable test captures.
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    w = MainWindow(Backend(ws))
    w.show()
    steps, errors = [], []

    def pump():
        app.processEvents()
        QTest.qWait(10)
        if errors:
            raise AssertionError(errors[-1])

    def modal_errors():
        active = app.activeModalWidget()
        if isinstance(active, QMessageBox):
            errors.append(active.text())
            active.accept()
    watch = QTimer()
    watch.timeout.connect(modal_errors)
    watch.start(100)

    def property_widget(kind, name):
        widget = w.properties.widget().findChild(kind, name)
        assert widget is not None, name
        return widget

    def line(name, text):
        widget = property_widget(QLineEdit, name)
        widget.setFocus()
        widget.setText(text)
        QTest.keyClick(widget, Qt.Key.Key_Return)
        pump()

    def text(name, value):
        property_widget(QPlainTextEdit, name).setPlainText(value)
        pump()

    def combo(name, value):
        widget = property_widget(QComboBox, name)
        index = widget.findData(value)
        assert index >= 0, (name, value)
        widget.setCurrentIndex(index)
        pump()

    def spin(name, value, floating=False):
        property_widget(QDoubleSpinBox if floating else QSpinBox, name).setValue(value)
        pump()

    def navigate(target):
        # Select the actual tree items, driving their normal selection signals.
        target = tuple(target)
        parent = target[:2] if target[0] in {"actors", "conversations", "events"} and len(target) > 1 else target
        item = w.nav_items[parent]
        w.nav.scrollToItem(item)
        QTest.mouseClick(w.nav.viewport(), Qt.MouseButton.LeftButton, pos=w.nav.visualItemRect(item).center())
        pump()
        if len(target) > len(parent):
            w.content.setCurrentItem(w.content_items[target])
            pump()
        assert w.selection == target, (w.selection, target)

    def click(key):
        button = w.buttons[key]
        assert button.isVisible() and button.isEnabled(), key
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        pump()

    def dialog_action(action, fill):
        def perform():
            dialog = app.activeModalWidget()
            try:
                fill(dialog)
            except Exception as error:
                errors.append(str(error))
                if dialog:
                    dialog.reject()
        QTimer.singleShot(30, perform)
        action()
        pump()

    def create(dialog):
        assert isinstance(dialog, NewProjectDialog)
        dialog.pid.setText("editor_demo")
        dialog.name.setText("RCM: Victoria y el pacto de Londres")
        dialog.description.setPlainText("Crónica de aceptación de Fase 2 creada con los controles del editor.")
        dialog.directory.setText(str(path.parent))
        QTest.mouseClick(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok), Qt.MouseButton.LeftButton)

    def choose(dialog, category, ident):
        assert isinstance(dialog, ResourceDialog)
        assert dialog.browser.category.currentData() == category
        dialog.browser.search.setText(ident)
        matches = [r for r in range(dialog.browser.table.rowCount()) if dialog.browser.table.item(r, 0).data(Qt.ItemDataRole.UserRole)[0] == ident]
        assert len(matches) == 1, (ident, matches)
        dialog.browser.table.selectRow(matches[0])
        QTest.mouseClick(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok), Qt.MouseButton.LeftButton)

    try:
        dialog_action(w.actions["new"].trigger, create)
        steps.append("New Project dialog creates editor_demo")
        navigate(("level",))
        dialog_action(lambda: QTest.mouseClick(property_widget(QPushButton, "choose_level"), Qt.MouseButton.LeftButton), lambda d: choose(d, "levels", "EastLondon"))
        line("level_name", "Londres: un nuevo pacto")
        steps.append("Resource Browser selects EastLondon; set entry title")
        click("actor")
        line("actor_id", "victoria")
        line("actor_name", "Victoria")
        dialog_action(lambda: QTest.mouseClick(property_widget(QPushButton, "choose_template"), Qt.MouseButton.LeftButton), lambda d: choose(d, "actors", "businessWoman"))
        combo("actor_placement", "absolute")
        for axis, value in zip("xyz", [1016, -54, 0]):
            spin("position_" + axis, value, True)
        spin("orientation_2", 180, True)
        text("actor_comment", "Posición de referencia original. La colisión debe comprobarse dentro del juego.")
        steps.append("Create Victoria; original template; XYZ and yaw edited")
        w.grab().save(str(evidence / "actors.png"))
        navigate(("state", "flags")); click("flag"); line("flag_alias", "alliance"); spin("flag_index", 1)
        steps.append("Create Chronicle Flag alliance = 1")
        navigate(("conversations",)); click("conversation"); line("conversation_id", "intro")
        navigate(("conversations", 0, "nodes", 0, "lines", 0))
        text("line_text", "Londres guarda secretos. ¿Quieres saber quién soy?")
        click("node"); line("node_id", "identity")
        navigate(("conversations", 0, "nodes", 1, "lines", 0))
        text("line_text", "Me llaman Victoria. Necesito un aliado para esta noche.")
        navigate(("conversations", 0, "nodes", 1, "choices", 0))
        text("answer_text", "Cuenta conmigo."); combo("answer_effect", "set_flag"); combo("answer_flag", "alliance")
        click("answer"); text("answer_text", "No quiero involucrarme.")
        navigate(("conversations", 0, "nodes", 0, "choices", 0))
        text("answer_text", "¿Quién eres?"); combo("answer_mode", "goto"); combo("answer_target", "identity")
        navigate(("conversations", 0, "nodes", 0, "choices", 1)); text("answer_text", "Me voy.")
        w.grab().save(str(evidence / "conversation.png"))
        steps.append("Create branched intro, GOTO and two answers per node; RETURN sets alliance")
        navigate(("conversations",)); click("conversation"); line("conversation_id", "ally")
        navigate(("conversations", 1, "nodes", 0, "lines", 0)); text("line_text", "Recuerdo nuestro pacto. Gracias por volver.")
        navigate(("conversations", 1, "nodes", 0, "choices", 0)); text("answer_text", "Seguimos juntos.")
        navigate(("conversations", 1, "nodes", 0, "choices", 1)); text("answer_text", "El pacto termina aquí."); combo("answer_effect", "clear_flag"); combo("answer_flag", "alliance")
        steps.append("Create ally dialogue; second RETURN clears alliance")
        # Two Actor Clicked events route to different conversations by state.
        for event_index, ident, state, target in [(1, "greet_new", False, "intro"), (2, "greet_ally", True, "ally")]:
            navigate(("events",)); click("event"); line("event_id", ident); combo("event_when", "actor_clicked")
            combo("event_actor", "victoria"); click("condition"); combo("condition_flag", "alliance"); combo("condition_state", state)
            click("action"); combo("action_target", target)
        steps.append("Scene Start spawn plus two conditional Actor Clicked events")
        navigate(("events", 2)); w.grab().save(str(evidence / "events.png"))
        w.actions["validate"].trigger(); pump()
        validation = w.validate_project()
        assert validation.valid, validation.problems
        steps.append("GUI validation passes (absolute coordinate INFO acknowledged)")
        reports = []
        w.build_completed.connect(reports.append)
        w.actions["build"].trigger()
        deadline = time.monotonic() + 50
        while w.busy and time.monotonic() < deadline:
            pump(); QTest.qWait(25)
        assert not w.busy and reports, w.log.toPlainText()
        assert reports[0]["status"] == "compiled-unverified-in-game"
        assert set(reports[0]["class_versions"].values()) == {"45.3"}
        steps.append("GUI threaded build produces native API classfiles 45.3 and distribution ZIP")
        w.grab().save(str(evidence / "build.png"))
        assert path.is_file() and not w.doc.modified
        w.open_path(path); pump()
        assert w.backend.validate(w.doc.data).valid
        steps.append("Reopen saved YAML without losing branch, flags or events")
        for target, filename in [(("actors", 0), "actors.png"), (("conversations", 0, "nodes", 0, "choices", 0), "conversation.png"), (("events", 2), "events.png"), (("resources",), "resources.png")]:
            navigate(target)
            w.validate_project()
            if target == ("resources",):
                w.browser.category.setCurrentIndex(w.browser.category.findData("actors"))
                w.browser.search.setText("businessWoman")
                w.browser.table.selectRow(0)
            pump()
            assert w.grab().save(str(evidence / filename))
        package = ws.output("build/editor_demo/editor_demo_distribution.zip")
        report = {"successful": True, "ui_driver": "PySide6 QtTest: real widgets, dialogs, signals and BuildWorker", "yaml_manually_authored": False,
                  "project": str(path.relative_to(ROOT)), "steps": steps, "gui_distribution_sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
                  "problems": [{"severity": p.severity, "message": p.message} for p in validation.problems], "native_game_test": False, "game_modified": False}
        ws.write(evidence / "report.json", json.dumps(report, ensure_ascii=False, indent=2))
        if (evidence / "failure.log").exists():
            (evidence / "failure.log").rename(evidence / ("previous_failure_" + str(time.time_ns()) + ".log"))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        w.close()
        return 0
    except Exception:
        import traceback
        ws.write(evidence / "failure.log", traceback.format_exc())
        # Preserve authored edits for diagnosis; source still originates in widgets.
        if w.doc and not w.busy:
            w.doc.autosave()
        w.doc = None
        w.close()
        raise


if __name__ == "__main__":
    raise SystemExit(main())

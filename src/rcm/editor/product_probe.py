"""Offline acceptance through the packaged Qt widgets, never game automation."""
from pathlib import Path
import argparse,hashlib,json,time
from PySide6.QtWidgets import QApplication


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--settings-directory',type=Path,required=True);parser.add_argument('--game',type=Path,required=True);parser.add_argument('--language',choices=('en','es'),default='en');args=parser.parse_args(argv)
    app=QApplication.instance() or QApplication([]);app.setApplicationName('Redemption Chronicle Maker');app.setStyle('Fusion')
    import os
    from PySide6.QtGui import QFontDatabase,QFont
    font=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts/segoeui.ttf'
    if font.is_file():QFontDatabase.addApplicationFont(str(font))
    symbols=font.with_name('seguisym.ttf')
    if symbols.is_file():QFontDatabase.addApplicationFont(str(symbols))
    app.setFont(QFont('Segoe UI',10))
    from ..paths import Workspace
    from ..app_settings import AppSettings
    from .i18n import configure,install_qt
    prefs=AppSettings(args.settings_directory);fresh=not prefs.exists;prefs.data['language']=args.language
    ws=Workspace(args.workspace,args.game);ws.app_settings=prefs;configure(ws);install_qt(app)
    from .product_ui import SetupDialog
    started=time.perf_counter();setup=SetupDialog(prefs,args.game,args.workspace);setup.check()
    if setup.result()!=SetupDialog.DialogCode.Accepted:raise ValueError(setup.status.text())
    ws=setup.ws
    from ..startup import prepare_workspace
    steps=[];prepare_workspace(ws,steps.append)
    from ..product import copy_example
    for name in ('tutorial','showcase','mini_chronicle'):copy_example(ws,name)
    prefs.data.update(setup_complete=True,workspace=str(ws.root),game_installation=str(ws.game));prefs.save()
    prepared=time.perf_counter()
    from ..service import Backend
    backend=Backend(ws);backend.safe_mode=True
    from .window import MainWindow,NewProjectDialog
    from .recipe_wizard import RecipeWizard
    win=MainWindow(backend);win.autosave_timer.stop();win.resize(1100,720);win.show();app.processEvents()
    ws.output('build/probe').mkdir(parents=True,exist_ok=True)
    win.grab().save(str(ws.output('build/probe/welcome.png')))
    setup.grab().save(str(ws.output('build/probe/setup.png')))
    self_ready=win.product_stack.currentWidget()==win.welcome
    dialog=NewProjectDialog(ws,win);dialog.name.setText('First adventure');dialog.level.setCurrentIndex(dialog.level.findData('EastLondon'));dialog.check_accept()
    if dialog.result()!=dialog.DialogCode.Accepted:raise ValueError('New project dialog failed')
    win.create_project(dialog)
    # Ordinary placement controller: the spatial coordinates come from the
    # accepted tutorial entry, not YAML edited or written by this probe.
    win.add_spatial_entity('entries','',[-62,-768,384])
    recipe=RecipeWizard(win,'talk');recipe.initializePage(1);recipe.controls['template'].setText('Anezka');recipe.controls['text'].setPlainText('Welcome to my first adventure.');recipe.accept()
    if recipe.error.text():raise ValueError(recipe.error.text())
    for kind in ('trigger_actions','quest'):
        wizard=RecipeWizard(win,kind);wizard.initializePage(1);wizard.accept()
        if wizard.error.text():raise ValueError(wizard.error.text())
    win.undo_project();win.redo_project();win.save_project();created=win.doc.path
    win.open_path(created);valid=win.validate_project().valid
    if not valid:raise ValueError('Widget-created project is invalid')
    report=backend.build(win.doc.snapshot())
    # Test deployment against a synthetic installation, leaving the real game untouched.
    from ..deployment import deploy
    fake=ws.output('build/probe/game');fake.mkdir(parents=True,exist_ok=True);(fake/'Vampire.exe').write_bytes(b'MZtest');(fake/'Resource.nob').write_bytes(b'test');saved_game=ws.game;saved_pref=prefs.data['game_installation']
    ws.game=fake;prefs.data['game_installation']=str(fake)
    from .. import deployment as deployment_api
    original_running=deployment_api.game_running
    try:
        # The synthetic executable cannot be running; no real process is queried.
        deployment_api.game_running=lambda:False
        deployment=deploy(ws,win.doc.data['chronicle']['id'],current_source=win.doc.snapshot())
    finally:
        deployment_api.game_running=original_running;ws.game=saved_game;prefs.data['game_installation']=saved_pref;prefs.save()
    before=hashlib.sha256(ws.output('chronicles/tutorial/project.yaml').read_bytes()).hexdigest()
    win.open_path(ws.output('chronicles/tutorial/project.yaml'));tutorial_open=time.perf_counter();win.open_path(ws.output('chronicles/showcase/project.yaml'));showcase_open=time.perf_counter()
    from PySide6.QtCore import QUrl
    for link in ('rcm://quay/actors/guide','rcm://quay/conversations/cam1','rcm://quay/conversations/anim/nodes/menu','rcm://quay/sequences/sequence1','rcm://quay/paths/guide_walk','rcm://resources/templates/T_mini_victoria'):
        win.guide_panel.navigate(QUrl(link))
    win.center_tabs.setCurrentWidget(win.graph_panel);win.select(('conversations',0));win.graph_panel.refresh();app.processEvents();win.grab().save(str(ws.output('build/probe/showcase.png')))
    win.doc._saved=__import__('rcm.service',fromlist=['source_text']).source_text(win.doc.snapshot());win.close();app.processEvents()
    reopened=AppSettings(args.settings_directory)
    result=dict(fresh_settings=fresh,welcome=self_ready,setup_steps=steps,setup_seconds=prepared-started,total_seconds=time.perf_counter()-started,gui_authored_valid=valid,build_status=report['status'],class_versions=report['class_versions'],synthetic_deployment=str(deployment['destination']),setup_not_repeated=reopened.data.get('setup_complete',False),tutorial_unmodified=before==hashlib.sha256(ws.output('chronicles/tutorial/project.yaml').read_bytes()).hexdigest(),language=args.language,native_game_test=False,clean_machine_test=False,real_opengl=False,game_originals_written=False,tutorial_open_timestamp=tutorial_open,showcase_open_timestamp=showcase_open)
    ws.write('build/product_probe.json',json.dumps(result,ensure_ascii=False,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())

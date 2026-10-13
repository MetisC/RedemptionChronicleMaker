"""Offline acceptance through the packaged Qt widgets, never game automation."""
from pathlib import Path
import argparse,hashlib,json,time
from PySide6.QtWidgets import QApplication,QPushButton,QDialog,QComboBox,QDialogButtonBox


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
    steps=[];preparation=prepare_workspace(ws,steps.append)
    from ..product import copy_example
    for name in ('tutorial','showcase','mini_chronicle','dynamic_lab'):copy_example(ws,name)
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
    rc3={'welcome':self_ready,'seven_tabs':win.center_tabs.count()==7,'dock_hidden_on_welcome':not win.build_dock.isVisible(),'install_secondary':win.welcome.findChild(QPushButton,'welcome_install').isFlat(),'one_language_control':not hasattr(win,'language_menu')}
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
    rc3.update(dock_hidden_for_valid_project=not win.build_dock.isVisible(),conversion_hidden_for_current_project=win.campaign_panel.convert_button.isHidden() and not win.convert_campaign_action.isVisible())
    win.doc.data['level']['source']='unknown';win.validate_project();rc3['errors_open_problems']=win.build_dock.isVisible() and win.bottom_tabs.currentIndex()==0
    win.doc.data['level']['source']='EastLondon';win.validate_project();win.find_references(('state','flags'));rc3['references_open_dock']=win.build_dock.isVisible() and win.bottom_tabs.currentIndex()==2
    win.build_dock.hide();win.grab().save(str(ws.output('build/probe/project.png')))
    from PySide6.QtCore import QTimer
    from .product_ui import settings_dialog
    def inspect_settings():
        dialog=win.findChild(QDialog,'settings_dialog');combo=dialog.findChild(QComboBox,'settings_language')
        rc3['settings_has_language']=combo is not None and combo.currentData()==args.language
        dialog.grab().save(str(ws.output('build/probe/settings.png')));dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Cancel).click()
    QTimer.singleShot(0,inspect_settings);settings_dialog(win)
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
    win.open_project_guide();app.processEvents();win.grab().save(str(ws.output('build/probe/guide.png')))
    guide=win.guide_panel.text.toPlainText();first='Start here' if args.language=='en' else 'Empieza aquí';technical='Complete technical index' if args.language=='en' else 'Índice técnico completo';rc3['human_showcase_guide']=first in guide and technical in guide and guide.index(first)<guide.index(technical)
    win.center_tabs.setCurrentWidget(win.campaign_panel);app.processEvents();win.grab().save(str(ws.output('build/probe/overview.png')))
    from PySide6.QtCore import QUrl
    for link in ('rcm://quay/actors/guide','rcm://quay/conversations/cam1','rcm://quay/conversations/anim/nodes/menu','rcm://quay/sequences/sequence1','rcm://quay/paths/guide_walk','rcm://resources/templates/T_mini_victoria'):
        win.guide_panel.navigate(QUrl(link))
    win.center_tabs.setCurrentWidget(win.graph_panel);win.select(('conversations',0));win.graph_panel.refresh();app.processEvents();win.grab().save(str(ws.output('build/probe/showcase.png')))
    # RC4 goes through the shipped wizard and ordinary document/history controls.
    from .dynamic_wizard import DynamicWizard
    from PySide6.QtWidgets import QGroupBox
    win.open_path(ws.output('chronicles/mini_chronicle/project.yaml'));original_source=win.doc.path.read_bytes();original=win.doc.snapshot()
    wizard=DynamicWizard(win,position=[-62,-1000,384]);wizard.show();app.processEvents()
    rc4=dict(wizard_four_pages=len(wizard.pageIds())==4,advanced_collapsed=not wizard.findChild(QGroupBox,'dynamic_advanced').isChecked())
    def button_visible(kind):
        button=wizard.button(kind)
        return button.isVisible() and wizard.rect().contains(button.mapTo(wizard,button.rect().topLeft())) and wizard.rect().contains(button.mapTo(wizard,button.rect().bottomRight()))
    from PySide6.QtWidgets import QWizard
    rc4['next_and_cancel_visible']=all(button_visible(k) for k in (QWizard.WizardButton.NextButton,QWizard.WizardButton.CancelButton))
    wizard.grab().save(str(ws.output('build/probe/dynamic_wizard.png')))
    wizard.mode.setCurrentIndex(wizard.mode.findData('boss'))
    for unused in range(3):wizard.button(QWizard.WizardButton.NextButton).click();app.processEvents()
    rc4['finish_and_cancel_visible']=all(button_visible(k) for k in (QWizard.WizardButton.FinishButton,QWizard.WizardButton.CancelButton))
    wizard.grab().save(str(ws.output('build/probe/dynamic_boss.png')))
    wizard.mode.setCurrentIndex(wizard.mode.findData('ambush'));wizard.accept();app.processEvents()
    rc4['wizard_created_valid']=wizard.result()==QDialog.DialogCode.Accepted and backend.validate(win.doc.snapshot()).valid
    rc4['upgrade_opt_in_backup']=win.doc.campaign['project_format']==10 and any(ws.output('backups/'+win.doc.campaign['chronicle']['id']).glob('*.yaml')) and win.doc.path.read_bytes()==original_source
    win.undo_project();rc4['atomic_undo']=win.doc.snapshot()==original;win.redo_project();win.save_project();rc4['format_10_saved']=win.doc.campaign['project_format']==10
    rc4['tutorial_still_format_9']=__import__('rcm.input_limits',fromlist=['parse_source']).parse_source(ws.output('chronicles/tutorial/project.yaml').read_text(encoding='utf8'))['project_format']==9
    compiled_dynamic=backend.build(win.doc.snapshot());rc4['real_api_compiled']=compiled_dynamic['status']=='compiled-unverified-in-game' and all(v=='45.3' for v in compiled_dynamic['class_versions'].values())
    gen=win.doc.campaign['scenes'][0]['generators'][0];win.guide_panel.navigate(QUrl('rcm://'+win.doc.campaign['scenes'][0]['id']+'/generators/'+gen['id']));rc4['guide_navigation']=win.selection==('generators',0)
    win.center_tabs.setCurrentWidget(win.graph_panel);win.graph_panel.kind.setCurrentIndex(win.graph_panel.kind.findData('generators'));app.processEvents();win.graph_panel.refresh();win.graph_panel.fit();win.grab().save(str(ws.output('build/probe/dynamic_graph.png')));rc4['graph_in_existing_tab']=win.center_tabs.count()==7 and bool(win.graph_panel.scene.items())
    wizard.close()
    win.doc._saved=__import__('rcm.service',fromlist=['source_text']).source_text(win.doc.snapshot());win.close();app.processEvents()
    reopened=AppSettings(args.settings_directory)
    if not all(rc3.values()):raise ValueError('RC3 widget acceptance failed: '+json.dumps(rc3))
    if not all(rc4.values()):raise ValueError('RC4 widget acceptance failed: '+json.dumps(rc4))
    result=dict(rc3=rc3,cache_rebuilt=preparation['cache_rebuilt'],fresh_settings=fresh,welcome=self_ready,setup_steps=steps,setup_seconds=prepared-started,total_seconds=time.perf_counter()-started,gui_authored_valid=valid,build_status=report['status'],class_versions=report['class_versions'],synthetic_deployment=str(deployment['destination']),setup_not_repeated=reopened.data.get('setup_complete',False),tutorial_unmodified=before==hashlib.sha256(ws.output('chronicles/tutorial/project.yaml').read_bytes()).hexdigest(),language=args.language,native_game_test=False,clean_machine_test=False,real_opengl=False,game_originals_written=False,tutorial_open_timestamp=tutorial_open,showcase_open_timestamp=showcase_open)
    result['rc4']=rc4;ws.write('build/product_probe.json',json.dumps(result,ensure_ascii=False,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())

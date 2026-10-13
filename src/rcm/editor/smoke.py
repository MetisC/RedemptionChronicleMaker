"""Exercise this application's controllers; never automates native game input."""
import json,time
from PySide6.QtCore import QTimer


def start(win,app):
    state={'started':False,'started_at':time.monotonic(),'errors':[]}
    timer=QTimer(win);timer.setInterval(100)
    def finish(report):
        from .i18n import language,tr
        from PySide6.QtWidgets import QDialogButtonBox
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        cancel=buttons.button(QDialogButtonBox.StandardButton.Cancel).text().replace('&','');buttons.deleteLater()
        result={'valid_project':win.backend.validate(win.doc.snapshot()).valid,'build_status':report.get('status'),'class_versions':report.get('class_versions'),'real_gl':bool(win.spatial.viewport and win.spatial.viewport.isValid()),'safe_mode':bool(getattr(win.backend,'safe_mode',False)),'native_engine_test':False,'elapsed_seconds':time.monotonic()-state['started_at']}
        result.update(editor_language=language(),save_label=win.actions['save'].text(),cancel_label=cancel,tab_labels=[win.center_tabs.tabText(i) for i in range(win.center_tabs.count())])
        result['localized_ui']=result['save_label']==tr('Guardar') and cancel==('Cancelar' if language()=='es' else 'Cancel')
        win.backend.ws.write('build/portable_smoke.json',json.dumps(result,indent=2))
        successful=result['valid_project'] and result['localized_ui'] and result['build_status']=='compiled-unverified-in-game' and (result['real_gl'] or result['safe_mode'])
        def close():win.doc=None;win.close();app.exit(0 if successful else 1)
        QTimer.singleShot(500,close)
    win.build_completed.connect(finish)
    def tick():
        if time.monotonic()-state['started_at']>120:
            timer.stop();win.backend.ws.write('build/portable_smoke.json',json.dumps({'status':'timeout','native_engine_test':False}));app.exit(1);return
        if state['started'] or win.spatial.loading:return
        if win.spatial.viewport and win.spatial.viewport.level is None:return
        validation=win.backend.validate(win.doc.snapshot())
        if not validation.valid:
            timer.stop()
            win.backend.ws.write('build/portable_smoke.json',json.dumps({'status':'validation-failed','native_engine_test':False,'errors':[p.message for p in validation.problems if p.severity=='ERROR']},indent=2))
            win.doc=None;win.close();app.exit(1);return
        state['started']=True;timer.stop();win.actions['build'].trigger()
    timer.timeout.connect(tick);timer.start()
    return timer

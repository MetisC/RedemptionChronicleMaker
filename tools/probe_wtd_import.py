"""Read the user's NOB and verify an isolated import/build; never play the game."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--game',type=Path,required=True);args=parser.parse_args()
    from rcm.paths import Workspace
    from rcm.service import Backend
    from rcm.wtd import prepare_import,ROOT as IMPORT_ROOT,ARCHIVE
    from rcm.spatial.assets import Assets
    ws=Workspace(ROOT,args.game);backend=Backend(ws);data,record=prepare_import(ws,args.source,backend.base_resources)
    (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as d:
        isolated=Workspace(Path(d),args.game)
        for name in ('levels','resources','scene_hints'):isolated.write('cache/'+name+'.json',ROOT.joinpath('cache/'+name+'.json').read_bytes())
        shutil.copytree(ROOT/'research/original/Codex.nob',isolated.output('research/original/Codex.nob'))
        for name in ('classes.zip','ecj-3.26.0.jar'):isolated.write('cache/toolchain/'+name,ROOT.joinpath('cache/toolchain/'+name).read_bytes())
        isolated.write(IMPORT_ROOT+'/'+ARCHIVE,data);isolated.write(IMPORT_ROOT+'/import.json',json.dumps(record))
        active=Backend(isolated);level=Assets(active).load('WTDPenthouse')
        sys.path.insert(0,str(ROOT/'tests'))
        from test_release10 import blank
        source=blank();source['chronicle']['id']='wtd_probe';source['scenes']=source['scenes'][:1];source['scenes'][0]['level']={'source':'WTDPenthouse'}
        actor=next(t['id'] for t in record['templates'] if t['kind']=='actors' and not t['id'].startswith('_'))
        clan=next(r['id'] for r in record['catalogue']['clans'] if r['imported']);power=next(r['id'] for r in record['catalogue']['disciplines'] if r['imported'])
        source['scenes'][0]['actors']=[dict(id='mentor',name='Mentor',template=actor,transform=dict(position=[-135,-176,72],orientation=[0,0,0]),traits=dict(clan=clan,disciplines={power:1}))]
        source['scenes'][0]['events']=[dict(id='start',when='scene_start',once=True,actions=[{'spawn':'mentor'}])]
        report=active.build(source)
        with zipfile.ZipFile(isolated.output('build/wtd_probe/wtd_probe_distribution.zip')) as archive:assert ARCHIVE not in archive.namelist()
        with zipfile.ZipFile(args.source) as original,zipfile.ZipFile(isolated.output(IMPORT_ROOT+'/'+ARCHIVE)) as imported:
            assert hashlib.sha256(original.read('levels/WTDPenthouse.nil')).hexdigest()==hashlib.sha256(imported.read('levels/WTDPenthouse.nil')).hexdigest()
            assert not any(n.lower().endswith(('.nui','.nsc','.nss','.nsl')) for n in imported.namelist())
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFontDatabase,QFont
        from rcm.editor.window import MainWindow
        from rcm.editor.wtd import TraitsDialog
        from rcm.campaign_document import CampaignDocument
        app=QApplication.instance() or QApplication([])
        font=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'Fonts/segoeui.ttf'
        if font.is_file():QFontDatabase.addApplicationFont(str(font))
        app.setFont(QFont('Segoe UI',10));active.safe_mode=True;win=MainWindow(active);win.doc=CampaignDocument(isolated,source);win.refresh()
        dialog=TraitsDialog(win,win.doc.data['actors'][0]);dialog.show();app.processEvents();dialog.grab().save(str(ws.output('research/mods/traits_dialog.png')));dialog.reject();win.doc=None;win.close()
        result=dict(source_sha256=record['source_sha256'],import_sha256=record['sha256'],counts=record['counts'],files=record['files'],penthouse_triangles=len(level.mesh.material_ids),penthouse_material_warnings=level.warnings,penthouse_geometry_identical=True,class_versions=report['class_versions'],third_party_assets_in_distribution=False,game_written=False,native_game_test=False)
    ws.write('research/mods/content_probe.json',json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()

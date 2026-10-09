"""Record the delivered editor, examples and exact deployment contents."""
from pathlib import Path
import hashlib,json,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.deployment import default_game
import pefile
from rcm import __version__
from rcm.formats import NotFile,cstring
from rcm.document import Document

def main():
    if len(Document.load(Workspace(ROOT),'chronicles/tutorial/project.yaml').snapshot()['quests'][0]['steps'])==7:
        from guided_tutorial_delivery_check import main as guided_check
        return guided_check()
    ws=Workspace(ROOT);app=ws.output('build/portable/RedemptionChronicleMaker')
    exe=app/'RedemptionChronicleMaker.exe'
    pe=pefile.PE(str(exe));resource_types={e.id for e in pe.DIRECTORY_ENTRY_RESOURCE.entries}
    if not {3,14}.issubset(resource_types):raise ValueError('Missing Windows icon resources')
    pe.close()
    sources={}
    for folder in ('tutorial','mini_chronicle'):
        for source in (ROOT/'chronicles'/folder).rglob('*'):
            if not source.is_file():continue
            relative=source.relative_to(ROOT/'chronicles')
            for target in (app/'examples'/relative,app/'workspace/chronicles'/relative):
                if source.read_bytes()!=target.read_bytes():raise ValueError('Example differs: '+str(target))
            sources[relative.as_posix()]=hashlib.sha256(source.read_bytes()).hexdigest()
    visible=sorted(p.name for p in (app/'workspace/chronicles').iterdir())
    if visible!=['mini_chronicle','tutorial']:raise ValueError('Unexpected visible projects')
    game=default_game(ROOT);destination=game/'RCM/east_demo'
    manifest=json.loads((destination/'.rcm_deployment.json').read_text(encoding='utf8'))
    if set(manifest['owners'])!={'rcm_tutor','rcm_mini'}:raise ValueError('Deployment owners differ')
    for name,digest in manifest['files'].items():
        if hashlib.sha256((destination/name).read_bytes()).hexdigest()!=digest:raise ValueError('Deployment differs: '+name)
    if sorted(p.name for p in destination.glob('*.nob'))!=['rcm_mini.nob','rcm_tutor.nob']:raise ValueError('Unexpected selectable chronicle')
    with zipfile.ZipFile(destination/'rcm_tutor.nob') as archive:
        mentor=NotFile.read(archive.read('misc/templates/_R_rcm_tutor_custom.not')).templates[0]
        if cstring(mentor.values()[56])!='AI_tutor.nai':raise ValueError('Mentor AI filename missing')
        if 'misc/AI/AI_tutor.nai' not in archive.namelist():raise ValueError('Mentor AI file missing')
        if 'Tutorial RCM: empieza aquí' not in archive.read('strings/_R_rcm_tutor.nls').decode('cp1252'):raise ValueError('Initial journal title missing')
    doc=Document.load(ws,'chronicles/tutorial/project.yaml').snapshot()
    first=doc['scenes'][0]
    back=next(e for e in first['events'] if e['id']=='help_back')
    if back['actions']!=[{'start_conversation':'menu'}]:raise ValueError('Help return link missing')
    guide=next(q for q in doc['quests'] if q['id']=='guide')
    if len(guide['steps'])!=1 or len(guide['steps'][0])>300:raise ValueError('Initial objective is not concise')
    java=ws.output('build/rcm_tutor/generated/java/R_rcm_tutor_s0_Scene.java').read_text(encoding='utf8')
    if 'CodexQuest.Load("R_rcm_tutor_q1")' in java:raise ValueError('Initial journal still loads the summary row')
    if 'finishDialogue();' not in java or 'pendingDialogueEnd=true; SetTimer(0.15f,9400)' not in java:raise ValueError('Dialogue end is not deferred')
    if 'case 0: CodexCamera.SetupCutscene(who,target,who); return;' not in java:raise ValueError('Automatic dialogue does not acquire cutscene mode')
    if 'BeginCutscene(player,0); AIOff();' not in java or 'EndCutscene(client,0); AIOn();' not in java:raise ValueError('Timeline does not own native cutscene lifecycle')
    if 'double tolerance=24.0' not in java or 'CUTSCENE_END' not in java:raise ValueError('Timeline patrol/cutscene cleanup missing')
    if b'DIALOGUE_RELEASE player=' not in (destination/'codex/R_rcm_tutor_s0_Scene.class').read_bytes():raise ValueError('Deployed class has no deferred release trace')
    for name in ('test_report.json','quality_report.json','tests.log'):
        target=ws.output('research/round0/cutscene_layout_fix/final_quality/'+name)
        if not target.exists():ws.write(target,ws.output('build/tests/'+name).read_bytes())
    result=dict(version=__version__,executable=str(exe),executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),windows_icon_resources=True,examples_match_sources=True,visible_projects=visible,source_sha256=sources,deployment_files_verified=len(manifest['files']),deployed_chronicles=manifest['chronicles'],mentor_ai_filename_verified=True,initial_journal_resources_verified=True,single_initial_objective_policy_verified=True,help_returns_to_menu=True,deferred_dialogue_release_class_verified=True,automatic_cutscene_mode_verified=True,cinematic_lifecycle_verified=True,waypoint_start_tolerance_verified=True,portable_smoke=json.loads(ws.output('research/round0/cutscene_layout_fix/portable_probe.json').read_text(encoding='utf8')),native_game_test=False)
    ws.write('research/round0/cutscene_layout_fix/delivery.json',json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))

if __name__=='__main__':main()

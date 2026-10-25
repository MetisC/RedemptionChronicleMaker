"""Reproducible onedir user product. No original game assets."""
from pathlib import Path
import argparse,json,os,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]
from rcm.paths import Workspace
USER_DOCS=['GETTING_STARTED','EDITOR_GUIDE','AUTHORING_GUIDE','AUTHORING_COMPLETION','TUTORIAL','SHOWCASE','FIRST_RUN','TROUBLESHOOTING','SHORTCUTS','ADVANCED_LIMITATIONS','DYNAMIC_ENCOUNTERS','CINEMATIC_DIRECTOR','MANUAL_RUNTIME_CHECKLIST']

def resolve_jlink(java_home=None):
    for home in [java_home,os.environ.get('JAVA_HOME')]:
        if home:
            path=Path(home)/'bin'/('jlink.exe' if os.name=='nt' else 'jlink')
            if path.is_file():return path
    found=shutil.which('jlink')
    if found:return Path(found)
    raise ValueError('Portable build requires jlink. Set JAVA_HOME, --java-home, or a verified JDK jlink on PATH. End users need no JDK.')

def windows_version(version):
    """Map 1.2.3[-rcN] to Windows' four-integer file version."""
    match=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?',version)
    if not match:raise ValueError('Portable version must look like X.Y.Z or X.Y.Z-rcN: '+version)
    values=[int(match.group(i) or 0) for i in range(1,5)]
    if any(value<0 or value>65535 for value in values):raise ValueError('Windows version components must fit 0..65535: '+version)
    return tuple(values)

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--destination',default='build/portable');parser.add_argument('--java-home',type=Path);args=parser.parse_args(argv)
    ws=Workspace(ROOT);destination=ws.output(args.destination);destination.mkdir(parents=True,exist_ok=True);app=ws.output(destination/'RedemptionChronicleMaker')
    if (app/'workspace').exists():raise ValueError('Preserve the user workspace outside this distribution before rebuilding.')
    for old in app.rglob('*'):ws.output(old)
    jlink=resolve_jlink(args.java_home)
    entry=ws.write('build/portable_entry.py',(ROOT/'tools/portable_entry.py').read_bytes())
    from rcm import __version__
    file_version=windows_version(__version__)
    version_info=ws.write('build/version_info.txt',"VSVersionInfo(ffi=FixedFileInfo(filevers="+repr(file_version)+",prodvers="+repr(file_version)+",mask=0x3f,flags=0x0,OS=0x40004,fileType=0x1,subtype=0x0,date=(0,0)),kids=[StringFileInfo([StringTable('040904B0',[StringStruct('ProductName','Redemption Chronicle Maker'),StringStruct('FileDescription','Redemption Chronicle Maker'),StringStruct('FileVersion','"+__version__+"'),StringStruct('ProductVersion','"+__version__+"'),StringStruct('OriginalFilename','RedemptionChronicleMaker.exe')])]),VarFileInfo([VarStruct('Translation',[1033,1200])])])")
    env=dict(os.environ,PYTHONPATH=os.pathsep.join([str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]))
    env['PATH']=os.pathsep.join([str(ROOT/'cache/vendor/PySide6'),str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32')])
    command=[sys.executable,'-m','PyInstaller','--clean','--noconfirm','--onedir','--windowed','--name','RedemptionChronicleMaker','--version-file',str(version_info),'--icon',str(ROOT/'src/rcm/editor/assets/chronicle.ico'),'--distpath',str(destination),'--workpath',str(ws.output('build/pyinstaller_work')),'--specpath',str(ws.output('build/pyinstaller_spec')),'--paths',str(ROOT/'src'),'--paths',str(ROOT/'cache/vendor'),'--hidden-import','numpy','--hidden-import','PIL.Image','--hidden-import','yaml','--hidden-import','PySide6.QtOpenGLWidgets','--add-data',str(ROOT/'cache/toolchain/ecj-3.26.0.jar')+';toolchain','--add-data',str(ROOT/'src/rcm/editor/assets')+';rcm/editor/assets','--add-data',str(ROOT/'cache/vendor/PySide6/translations/qtbase_es.qm')+';translations',str(entry)]
    run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',errors='replace');ws.write('build/portable_build.log',run.stdout+run.stderr)
    if run.returncode:raise SystemExit('PyInstaller failed; see build/portable_build.log')
    runtime=app/'runtime'
    if not runtime.exists():subprocess.run([str(jlink),'--add-modules','java.base,java.compiler,jdk.unsupported','--strip-debug','--no-header-files','--no-man-pages','--output',str(runtime)],check=True)
    docs=app/'docs'
    if docs.exists():
        for path in docs.rglob('*'):ws.output(path)
        shutil.rmtree(ws.output(docs))
    docs.mkdir()
    for stem in USER_DOCS:
        for suffix in ('.md','.en.md'):shutil.copy2(ROOT/'docs'/(stem+suffix),docs/(stem+suffix))
    for name in ['CHANGELOG.md','RELEASE_NOTES.md','LICENSE']:shutil.copy2(ROOT/name,app/name)
    ws.write(app/'README.txt','Redemption Chronicle Maker '+__version__+'\n\nOpen RedemptionChronicleMaker.exe. Choose Vampire.exe when requested. Projects stay in Documents, outside this program. Open Quick tutorial or Full showcase, then press F5 to playtest.\n\nAbre RedemptionChronicleMaker.exe. Selecciona Vampire.exe. Tus proyectos se guardan en Documentos, fuera del programa. Abre Tutorial rapido o Showcase completo y pulsa F5 para probar.\n\nUnofficial fan-made authoring tool for Vampire: The Masquerade - Redemption. Requires your own complete game installation.\n')
    ws.write(app/'VERSION',__version__+'\n')
    for folder in ('tutorial','showcase','mini_chronicle','dynamic_lab','director_acceptance','strict_acceptance','completion_lab','scenery_lab'):
        target=app/'examples'/folder
        if target.exists():shutil.rmtree(ws.output(target))
        for file in (ROOT/'chronicles'/folder).rglob('*'):
            if file.is_file() and file.suffix in ('.yaml','.md','.java','.png'):ws.write(target/file.relative_to(ROOT/'chronicles'/folder),file.read_bytes())
    notices=ROOT/'docs/licenses/portable'
    if not notices.is_dir():notices=ROOT/'build/portable_notices'
    notice_target=app/'THIRD_PARTY_NOTICES'
    if notice_target.exists():shutil.rmtree(ws.output(notice_target))
    if notices.is_dir():
        for name in ['ECJ','numpy','Pillow','PyInstaller','PySide6','PySide6_Addons','PySide6_Essentials','shiboken6','PyYAML','setuptools','packaging','PYTHON_LICENSE.txt']:
            source=notices/name;target=notice_target/name
            if source.is_dir():shutil.copytree(source,target)
            elif source.is_file():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    for filename in ('README.md','README.en.md','requirements.txt','portable_console.log'):
        p=ws.output(app/filename)
        if p.is_file():p.unlink()
    report=dict(executable=str(app/'RedemptionChronicleMaker.exe'),version=__version__,original_game_assets_included=False,original_tools_included=False,jvm_bundled=True,native_game_test=False,clean_machine_test=False,user_data_inside_program=False,user_doc_whitelist=USER_DOCS)
    ws.write('build/portable_build_report.json',json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()

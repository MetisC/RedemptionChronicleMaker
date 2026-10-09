"""Build a Windows onedir application, excluding all original game assets."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]
from rcm.paths import Workspace
parser=argparse.ArgumentParser();parser.add_argument('--destination',default='build/portable');args=parser.parse_args()
ws=Workspace(ROOT);destination=ws.output(args.destination);destination.mkdir(parents=True,exist_ok=True)
app=ws.output(destination/'RedemptionChronicleMaker')
if (app/'workspace').exists():raise ValueError('La distribución contiene un workspace de usuario. Consérvalo fuera de la carpeta de distribución antes de reconstruirla')
for old in app.rglob('*'):ws.output(old)
# PyInstaller puts the entry directory first; tools/rcm.py would shadow src/rcm.
entry=ws.write('build/portable_entry.py',(ROOT/'tools/portable_entry.py').read_bytes())
env=dict(os.environ,PYTHONPATH=os.pathsep.join([str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]))
# A machine-wide Poppler PATH can shadow Windows' ICU forwarding DLLs.
# Only the chosen Qt tree and Windows are dependency search locations.
env['PATH']=os.pathsep.join([str(ROOT/'cache/vendor/PySide6'),str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32')])
command=[sys.executable,'-m','PyInstaller','--noconfirm','--onedir','--windowed','--name','RedemptionChronicleMaker','--distpath',str(destination),'--workpath',str(ws.output('build/pyinstaller_work')),'--specpath',str(ws.output('build/pyinstaller_spec')),'--paths',str(ROOT/'src'),'--paths',str(ROOT/'cache/vendor'),'--hidden-import','numpy','--hidden-import','PIL.Image','--hidden-import','yaml','--hidden-import','PySide6.QtOpenGLWidgets','--add-data',str(ROOT/'cache/toolchain/ecj-3.26.0.jar')+';toolchain',str(entry)]
command.insert(4,'--clean')
command[4:4]=['--icon',str(ROOT/'src/rcm/editor/assets/chronicle.ico'),'--add-data',str(ROOT/'src/rcm/editor/assets')+';rcm/editor/assets']
run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True);ws.write('build/portable_build.log',run.stdout+run.stderr)
if run.returncode:raise SystemExit('PyInstaller falló; consulta build/portable_build.log')
jdk=Path(r'C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot');runtime=app/'runtime'
if not runtime.exists():
    subprocess.run([str(jdk/'bin/jlink.exe'),'--add-modules','java.base,java.compiler,jdk.unsupported','--strip-debug','--no-header-files','--no-man-pages','--output',str(runtime)],check=True)
for name in ['README.md','requirements.txt']:shutil.copy2(ROOT/name,app/name)
notices=ROOT/'docs/licenses/portable'
if not notices.is_dir():notices=ROOT/'build/portable_notices'
if notices.is_dir():shutil.copytree(notices,app/'THIRD_PARTY_NOTICES',dirs_exist_ok=True)
shutil.copytree(ROOT/'docs',app/'docs',dirs_exist_ok=True)
shutil.copytree(ROOT/'chronicles',app/'examples',dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.backup','*.autosave','*.pre_format5','__pycache__'))
report={'executable':str(app/'RedemptionChronicleMaker.exe'),'original_game_assets_included':False,'original_tools_included':False,'jvm_bundled':str(runtime),'native_game_test':False,'clean_machine_test':False}
ws.write('build/portable_build_report.json',json.dumps(report,indent=2));print(json.dumps(report))

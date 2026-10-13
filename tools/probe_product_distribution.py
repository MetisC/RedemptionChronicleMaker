"""Moved frozen app acceptance, reduced PATH, bilingual and Qt scale simulation."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path,required=True);args=parser.parse_args()
    source=ROOT/'build/portable/RedemptionChronicleMaker';destination=ROOT/'research/dynamic_encounters/portable';destination.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,PATH=str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'),PYTHONPATH='',QT_QPA_PLATFORM='offscreen')
    records=[]
    for code,name in [('en','Moved App'),('es','Prueba con espacios ñ')]:
        root=destination/name;app=root/'application';shutil.copytree(source,app,dirs_exist_ok=True);workspace=root/'projects';settings=root/'settings'
        command=[str(app/'RedemptionChronicleMaker.exe'),'--product-probe','--workspace',str(workspace),'--settings-directory',str(settings),'--game',str(args.game),'--language',code]
        for phase in ('fresh','second'):
            started=time.perf_counter();run=subprocess.run(command,env=env,cwd=ROOT,timeout=150,capture_output=True)
            report=workspace/'build/product_probe.json';data=json.loads(report.read_text(encoding='utf8')) if report.is_file() else {}
            record=dict(language=code,phase=phase,returncode=run.returncode,elapsed_seconds=time.perf_counter()-started,report=data,path_restricted=True,independent_machine=False)
            records.append(record);(destination/(code+'_'+phase+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
            if run.returncode or not all(data.get('rc3',{}).values()) or not data.get('rc3') or not all(data.get('rc4',{}).values()) or not data.get('rc4') or not data.get('gui_authored_valid') or phase=='fresh' and not data.get('fresh_settings') or phase=='second' and data.get('fresh_settings'):raise ValueError(record)
        if code=='en':
            for scale in ['1','1.25','1.5','2']:
                run=subprocess.run(command,env=dict(env,QT_SCALE_FACTOR=scale),cwd=ROOT,timeout=150,capture_output=True)
                data=json.loads(report.read_text(encoding='utf8'));record=dict(qt_scale=scale,returncode=run.returncode,report=data,physical_windows_dpi_test=False);records.append(record)
                captures=destination/('scale_'+scale);captures.mkdir(exist_ok=True)
                for name in ['welcome','setup','showcase','project','guide','overview','settings','dynamic_wizard','dynamic_boss','dynamic_graph']:shutil.copy2(workspace/'build/probe'/(name+'.png'),captures/(name+'.png'))
                if run.returncode:raise ValueError(record)
    (destination/'summary.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
    print('Frozen bilingual fresh/repeat runs and four Qt scaling simulations passed. No game was launched.')


if __name__=='__main__':main()

"""Read PE imports against bundled DLL exports; does not load or execute DLLs."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'cache/devtools'))
import pefile
base=ROOT/'build/portable/RedemptionChronicleMaker/_internal';dlls={p.name.casefold():p for p in base.glob('*.dll')};exports={};missing=[]
for name,path in dlls.items():
    pe=pefile.PE(str(path),fast_load=True,max_symbol_exports=100000);pe.parse_data_directories(directories=[0]);exports[name]={s.name for s in getattr(pe,'DIRECTORY_ENTRY_EXPORT',type('Empty',(),{'symbols':[]})()).symbols};pe.close()
for path in list((base/'PySide6').glob('*.pyd'))+list((base/'shiboken6').glob('*.pyd'))+list(base.glob('Qt*.dll')):
    pe=pefile.PE(str(path),fast_load=True);pe.parse_data_directories(directories=[1])
    for lib in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
        name=lib.dll.decode().casefold()
        if name in exports:
            for entry in lib.imports:
                if entry.name is not None and entry.name not in exports[name]:missing.append({'module':path.name,'dll':name,'symbol':entry.name.decode(errors='replace'),'bundled_dll':str(dlls[name])})
    pe.close()
(ROOT/'research/phase6/portable_missing_exports.json').write_text(json.dumps(missing,indent=2),encoding='utf8');print(json.dumps({'missing_symbols':len(missing),'sample':missing[:8]},indent=2))

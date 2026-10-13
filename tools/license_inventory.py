"""Collect installed dependency notices from their distributions, not game data."""
from pathlib import Path
import importlib.metadata as metadata
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'cache/vendor'),str(ROOT/'cache/devtools')]
names=['PySide6','PySide6_Addons','PySide6_Essentials','shiboken6','PyYAML','numpy','Pillow','coverage','ruff','mypy','types-PyYAML','PyInstaller','pyinstaller-hooks-contrib','altgraph','packaging','pefile','pywin32-ctypes','setuptools','capstone']
dest=ROOT/'build/portable_notices';dest.mkdir(parents=True,exist_ok=True);inventory=[]
for name in names:
    dist=metadata.distribution(name);row={'name':dist.metadata['Name'],'version':dist.version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License','unspecified'),'classifiers':[x for x in dist.metadata.get_all('Classifier',[]) if x.startswith('License')],'copied_notices':[]}
    for item in dist.files or []:
        if any(word in str(item).lower() for word in ['license','copying','notice']) and str(item).split('/')[0].endswith('.dist-info'):
            path=Path(dist.locate_file(item))
            if path.is_file():
                target=dest/name/Path(str(item));target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes());row['copied_notices'].append(target.relative_to(dest).as_posix())
    inventory.append(row)
python_license=Path(sys.executable).parent/'LICENSE.txt'
if python_license.is_file():(dest/'PYTHON_LICENSE.txt').write_bytes(python_license.read_bytes())
inventory.append({'name':'ECJ','version':'3.26.0','license':'See embedded META-INF notices','copied_notices':[]})
import zipfile
with zipfile.ZipFile(ROOT/'cache/toolchain/ecj-3.26.0.jar') as jar:
    for name in jar.namelist():
        if name.lower().endswith(('about.html','license','notice')):
            target=dest/'ECJ'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(jar.read(name));inventory[-1]['copied_notices'].append(target.relative_to(dest).as_posix())
(ROOT/'research/product_close').mkdir(parents=True,exist_ok=True)
(ROOT/'research/product_close/dependencies.json').write_text(json.dumps(inventory,indent=2),encoding='utf8');print('Dependency inventory and installed notices saved')

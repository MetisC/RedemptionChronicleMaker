"""Identify disposable backups by exact equality to regression fixtures."""
import copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor'),str(ROOT/'tests')]
import yaml
from rcm.paths import Workspace
from rcm.campaign_document import CampaignDocument
from rcm.document import Document
from test_campaign import source
from test_phase2 import graph_source

ws=Workspace(ROOT);campaign=source();east=graph_source();models=[campaign,east]
for title in ('Otro título','Título pendiente'):
    row=copy.deepcopy(campaign);row['quests'][0]['title']=title;models.append(row)
recovered=copy.deepcopy(east);recovered['chronicle']['name']='Recuperado';models.append(recovered)
renamed=Document(ws,copy.deepcopy(east));renamed.rename('actors',0,'vicky');models.append(renamed.snapshot())
models.append(CampaignDocument.new(ws,'nueva_campana','Nueva campaña','build/empty_probe').snapshot())
rows=[]
for path in (ROOT/'backups').rglob('*.yaml'):
    data=yaml.safe_load(path.read_text(encoding='utf8'))
    rows.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),exact_test_fixture_match=any(data==model for model in models)))
ws.write('research/dynamic_encounters/disposable_backup_audit.json',json.dumps(rows,indent=2))
print(json.dumps(dict(exact_matches=sum(r['exact_test_fixture_match'] for r in rows),unmatched=[r['path'] for r in rows if not r['exact_test_fixture_match']])))

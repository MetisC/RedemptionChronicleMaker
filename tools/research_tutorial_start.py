"""Inspect original walking NPC anchors, floor clearance and static neighbours."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.deployment import default_game
from rcm.spatial.assets import Assets
from rcm.spatial.geometry import read_nil
from rcm.spatial.math3d import Raycaster

ws=Workspace(ROOT,default_game(ROOT));backend=Backend(ws);entry=backend.levels['EastLondon']['geometry'][0]
ray=Raycaster(read_nil(Assets(backend).read(entry['path'],entry['archive'])))
offsets=[(0,0),(0,156),(-166,0),(114,0),(0,-160),(-166,-110),(84,0),(84,-100),(-166,-250)]
report=[]
for anchor in [(-1720,-2136,128),(-176,-768,384),(-2208,-32,512)]:
    rows=[]
    for dx,dy in offsets:
        point=[anchor[0]+dx,anchor[1]+dy,anchor[2]];floor=ray.ground(point,64,128)
        hits=[]
        if floor:
            for x,y in [(0,0),(20,0),(-20,0),(0,20),(0,-20)]:
                hit=ray.cast(floor.position+[x,y,1],[0,0,1],False,110)
                if hit:hits.append(hit.distance)
        static=[dict(template=e['template'],position=e['position']) for e in backend.hints['l1_east.nsd']['entities'] if (e['position'][0]-point[0])**2+(e['position'][1]-point[1])**2<100**2]
        rows.append(dict(point=point,floor=floor.position.tolist() if floor else None,headroom_hits=hits,nearby_static=static))
    report.append(dict(anchor=anchor,points=rows))
ws.write('research/round0/start_anchor_candidates.json',json.dumps(report,indent=2));print(json.dumps(report,indent=2))

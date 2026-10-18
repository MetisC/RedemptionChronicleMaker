"""Native AI interest groups, NOT ordered actor routes.

Loader 4a803e..810e; NAI loader field 14 -> +60; consumer 47bfb0..c026
matches group at record+56 and requires records sorted by group.
The final 128.0/0/0 fields are preserved original defaults, not editable.
"""
import math,struct


def validate_record(raw):
    if len(raw)!=72:raise ValueError('Interest spot: 72 bytes required')
    sector,polygon,*rest=struct.unpack('<II12fIfII',raw)
    values=rest[:12];group=rest[12]
    if sector>=100000 or polygon!=0 or not 0<=group<=9 or not all(math.isfinite(v) and abs(v)<1e7 for v in values):raise ValueError('Interest spot: invalid sector, group or transform')
    axes=[values[i:i+3] for i in (0,3,6)]
    if any(abs(sum(v*v for v in a)-1)>.01 for a in axes) or any(abs(sum(a*b for a,b in zip(axes[i],axes[j])))>.01 for i,j in ((0,1),(0,2),(1,2))):raise ValueError('Interest spot: invalid basis')
    return raw


def records(ws,level,scene):
    points=[r for r in scene.get('waypoints',[]) if 'interest_group' in r]
    if not points:return []
    from .native_arrivals import planes,sector_at
    sectors=planes(ws,level);result=[]
    for row in sorted(points,key=lambda r:r['interest_group']):
        # Reproduce the original default, including its negative zero basis.
        p=row['transform']['position'];group=row['interest_group']
        result.append(validate_record(struct.pack('<II12fIfII',sector_at(sectors,p),0,1,0,-0.0,0,1,0,0,0,1,*p,group,128.0,0,0)))
    return result

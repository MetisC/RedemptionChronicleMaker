"""Read-only NSD brush previews; no scene or geometry writer.

The bounded probe recognises the embedded mesh body by material names, counts,
index groups and its trailing bounds. It does not decode the surrounding NSD
script parameters, collision planes or lighting arrays.
"""
import re
import struct
import numpy as np
from .geometry import Reader,Mesh


def read_brush(data,offset):
    r=Reader(data);r.pos=offset
    count=r.count('I',64)
    if not count:raise ValueError('Empty brush')
    names=[]
    for _ in range(count):
        raw=r.take(32)
        if b'\0' not in raw or not re.fullmatch(rb'[A-Za-z0-9_./\\ -]{1,31}',raw.split(b'\0',1)[0]):raise ValueError('Invalid brush material')
        names.append(raw.split(b'\0',1)[0].decode('cp1252'))
    nv,nt,ng,flags=r.unpack('IIHI')
    if not 0<nv<=200000 or not 0<nt<=200000 or not 0<ng<=4096 or flags&~7:raise ValueError('Invalid brush counts')
    points=np.frombuffer(r.take(nv*40),dtype='<f4').reshape(-1,10)
    if not np.isfinite(points).all() or np.abs(points[:,:3]).max()>1e7:raise ValueError('Invalid brush vertices')
    if flags&1:r.take(nv*2)
    triangles=np.frombuffer(r.take(nt*6),dtype='<u2').reshape(-1,3)
    vertices=[];ids=[];vi=ti=0
    for _ in range(ng):
        group=r.take(28);mid=struct.unpack_from('<i',group)[0];ntri,nvert=struct.unpack_from('<HH',group,16)
        if not -1<=mid<count or vi+nvert>nv or ti+ntri>nt:raise ValueError('Invalid brush group')
        indices=triangles[ti:ti+ntri].astype(np.int64)
        if len(indices) and int(indices.max())>=nvert:raise ValueError('Invalid brush index')
        vertices.extend(points[(indices+vi).reshape(-1)][:,[0,1,2,6,7]]);ids.extend([mid]*ntri);vi+=nvert;ti+=ntri
    if vi!=nv or ti!=nt:raise ValueError('Incomplete brush groups')
    bounds=np.array(r.unpack('6f')).reshape(2,3)
    if not np.allclose(bounds,[points[:,:3].min(0),points[:,:3].max(0)],atol=.05):raise ValueError('Brush bounds mismatch')
    return Mesh(np.asarray(vertices,dtype=np.float32).reshape(-1,5),np.asarray(ids,dtype=np.int32),names,0,r.pos,[])


def find_brush(data,start,end):
    # Only inspect the variable header immediately after the entity tags.
    for offset in range(start,min(start+1024,end-54),4):
        if not 0<struct.unpack_from('<I',data,offset)[0]<=64:continue
        try:
            mesh=read_brush(data[:end],offset)
            return dict(mesh_offset=offset,mesh_bounds=[v.tolist() for v in mesh.bounds],mesh_materials=mesh.materials)
        except (ValueError,struct.error):continue
    return {}

"""Native NCP polynomial paths, grounded in the original reader/evaluator.

Original cubic coefficients round-trip verbatim. New paths use the proven
linear polynomial subset; FOV is not stored by this format.
"""
from dataclasses import dataclass
import math,struct
from .model import mapping

MAX_KEYS=128  # Native loader 0x43167e, fixed 128-record camera buffer.


@dataclass(frozen=True)
class CameraPath:
    total: float
    records: tuple

    @classmethod
    def read(cls,data):
        if len(data)<8:raise ValueError('NCP truncado')
        count,total=struct.unpack_from('<If',data)
        if not 1<=count<=MAX_KEYS or len(data)!=8+104*count:raise ValueError('NCP: número de puntos o tamaño inválido')
        records=tuple(struct.unpack_from('<26f',data,8+104*i) for i in range(count))
        if not math.isfinite(total) or total<0 or any(not math.isfinite(x) for row in records for x in row):raise ValueError('NCP: valores no finitos')
        if any(row[0]<0 or row[0]>total+.001 or row[1]<0 or i and row[0]<records[i-1][0] for i,row in enumerate(records)):raise ValueError('NCP: parámetros inválidos')
        return cls(total,records)

    def encode(self):
        data=struct.pack('<If',len(self.records),self.total)+b''.join(struct.pack('<26f',*row) for row in self.records)
        self.read(data)
        return data

    def sample(self,parameter):
        """Evaluate the demonstrated polynomial; no collision/render preview."""
        if not math.isfinite(parameter):raise ValueError('Parámetro NCP no finito')
        if len(self.records)==1 or parameter>=self.total:
            row=self.records[-1];return list(row[2:5]),list(row[14:17])
        index=0
        while index+1<len(self.records) and parameter>=self.records[index+1][0]:index+=1
        row=self.records[index];u=max(0,parameter-row[0])*row[1]
        def value(start):return [row[start+i]+row[start+3+i]*u+row[start+6+i]*u*u+row[start+9+i]*u*u*u for i in range(3)]
        return value(2),value(14)


def vector(value,label):
    if not isinstance(value,list) or len(value)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1_000_000 for v in value):raise ValueError(label+': requiere tres valores finitos')
    return list(map(float,value))


def authored(points,timed=False):
    if not isinstance(points,list) or not 1<=len(points)<=MAX_KEYS:raise ValueError('Travelling: requiere 1..128 puntos de cámara')
    if type(timed) is not bool:raise ValueError('Timed camera path requires boolean')
    values=[]
    for point in points:
        mapping(point,{'position','orientation','duration'} if timed else {'position','orientation'},{'position','orientation'},'Punto de cámara')
        if timed and (type(point.get('duration',1)) not in (int,float) or not math.isfinite(point.get('duration',1)) or not .15<=point.get('duration',1)<=120):raise ValueError('Camera segment duration: 0.15..120 seconds')
        values.append((vector(point['position'],'Posición'),vector(point['orientation'],'Orientación')))
    records=[];distance=0.0
    for i,(position,orientation) in enumerate(values):
        row=[0.0]*26;row[0]=distance;row[2:5]=position;row[14:17]=orientation
        if i+1<len(values):
            other,angles=values[i+1];delta=[b-a for a,b in zip(position,other)];length=math.sqrt(sum(x*x for x in delta))
            if timed:length=float(points[i].get('duration',1))
            elif length<.001:raise ValueError('Mueve el punto de cámara: dos puntos consecutivos no pueden coincidir')
            row[1]=1/length;row[5:8]=delta;row[17:20]=[(b-a+180)%360-180 for a,b in zip(orientation,angles)];distance+=length
        records.append(tuple(row))
    if timed and distance>120:raise ValueError('Timed camera path: maximum 120 seconds')
    return CameraPath.read(CameraPath(distance,tuple(records)).encode())


def validate_resource(row,levels,scenes):
    mapping(row,{'id','name','scene','level','points','timed'},{'id','scene','level','points'},'Travelling propio')
    if row['level'] not in levels:raise ValueError('Level de travelling desconocido')
    if row['scene'] not in {s['id'] for s in scenes}:raise ValueError('Escena de creación del travelling ausente')
    return authored(row['points'],row.get('timed',False))

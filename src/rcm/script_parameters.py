"""Evidenced native parameter stream (4b5060), separate from movement frames."""
from dataclasses import dataclass
import math,struct

WRITABLE={1,2,3,7,8}


@dataclass(frozen=True)
class Parameter:
    kind:int
    raw:bytes
    def encode(self):
        if type(self.kind) is not int or not 1<=self.kind<=11:raise ValueError('Tipo de parámetro nativo desconocido')
        if self.kind==7:
            if not 1<=len(self.raw)<=4096 or self.raw[-1:]!=b'\0' or b'\0' in self.raw[:-1]:raise ValueError('Cadena de parámetro nativo no terminada o excesiva')
            return struct.pack('<II',7,len(self.raw))+self.raw
        size=0 if self.kind==6 else 4
        if len(self.raw)!=size:raise ValueError('Tamaño de parámetro nativo inválido')
        return struct.pack('<I',self.kind)+self.raw


def read(data,offset,count):
    if type(count) is not int or not 0<=count<=16:raise ValueError('Parámetros nativos: máximo 16')
    rows=[]
    for unused in range(count):
        if offset<0 or offset+4>len(data):raise ValueError('Parámetros nativos truncados')
        kind=struct.unpack_from('<I',data,offset)[0];offset+=4
        if not 1<=kind<=11:raise ValueError('Tipo de parámetro nativo desconocido')
        size=0 if kind==6 else 4
        if kind==7:
            if offset+4>len(data):raise ValueError('Parámetros nativos truncados')
            size=struct.unpack_from('<I',data,offset)[0];offset+=4
            if not 1<=size<=4096:raise ValueError('Cadena nativa excesiva')
        if offset+size>len(data):raise ValueError('Parámetros nativos truncados')
        row=Parameter(kind,data[offset:offset+size]);row.encode();rows.append(row);offset+=size
    return rows,offset


def authored(kind,value,entities):
    if kind not in WRITABLE:raise ValueError('Tipo no soportado para autoría nativa')
    if kind==1:
        if type(value) is not int or not -2147483648<=value<=2147483647:raise ValueError('Parámetro entero fuera de int32')
        raw=struct.pack('<i',value)
    elif kind==2:
        if type(value) not in (float,int) or not math.isfinite(value) or abs(value)>1e7:raise ValueError('Parámetro float finito fuera de rango')
        raw=struct.pack('<f',value)
    elif kind==7:
        if not isinstance(value,str) or '\0' in value or len(value)>255:raise ValueError('Parámetro de texto: máximo 255 caracteres sin NUL')
        raw=value.encode('cp1252')+b'\0'
    else:
        if value is None:raw=struct.pack('<i',-1)
        elif not isinstance(value,str) or value not in entities:raise ValueError('Parámetro: selecciona una entidad de esta escena')
        else:raw=struct.pack('<i',entities[value])
    return Parameter(kind,raw)

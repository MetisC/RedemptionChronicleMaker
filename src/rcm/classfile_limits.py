"""Measure real Java classfile budgets; do not estimate from source length."""
import struct

def inspect_class(data, metadata=False):
    pos=0
    def take(n):
        nonlocal pos
        if n<0 or pos+n>len(data):raise ValueError('Classfile truncado')
        result=data[pos:pos+n];pos+=n;return result
    def u2():return struct.unpack('>H',take(2))[0]
    def u4():return struct.unpack('>I',take(4))[0]
    if take(4)!=bytes.fromhex('cafebabe'):raise ValueError('Classfile sin cabecera Java')
    minor,major=u2(),u2();count=u2();strings={};classes={};literals={};fields={};names={};i=1
    while i<count:
        tag=take(1)[0]
        if tag==1:strings[i]=take(u2()).decode('utf8',errors='replace')
        elif tag==7:classes[i]=u2()
        elif tag==8:literals[i]=u2()
        elif tag==9:fields[i]=(u2(),u2())
        elif tag==12:names[i]=(u2(),u2())
        elif tag in (3,4,10,11):take(4)
        elif tag in (5,6):take(8);i+=1
        else:raise ValueError('Constant-pool tag no compatible con 45.3: '+str(tag))
        i+=1
    access,classname,parent=u2(),u2(),u2();take(2*u2());methods=[]
    def member(is_method):
        access=u2();name,descriptor=u2(),u2()
        for unused in range(u2()):
            attr= strings.get(u2());payload=take(u4())
            if attr=='Code' and is_method:
                if len(payload)<8:raise ValueError('Atributo Code truncado')
                length=struct.unpack_from('>I',payload,4)[0]
                if not 0<length<=65535 or length+8>len(payload):raise ValueError('Método excede límite Java o está truncado')
                method={'name':strings.get(name,'?'),'descriptor':strings.get(descriptor,'?'),'code_bytes':length,'access_flags':access}
                if metadata:method['bytecode']=payload[8:8+length].hex()
                methods.append(method)
    for unused in range(u2()):member(False)
    for unused in range(u2()):member(True)
    for unused in range(u2()):take(2);take(u4())
    if pos!=len(data):raise ValueError('Classfile con bytes no interpretados')
    result={'version':str(major)+'.'+str(minor),'class':strings.get(classes.get(classname),''),'superclass':strings.get(classes.get(parent),''),'access_flags':access,'constant_pool_entries':count-1,'constant_pool_limit':65534,'largest_method_bytes':max((m['code_bytes'] for m in methods),default=0),'method_limit_bytes':65535,'methods':methods}
    if metadata:
        result['string_literals']={k:strings[v] for k,v in literals.items()}
        result['field_names']={k:tuple(strings.get(n,'') for n in names.get(v[1],())) for k,v in fields.items()}
    return result

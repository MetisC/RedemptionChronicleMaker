"""Read original bindings/templates and CTD bytecode; never run authoring tools."""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/vendor'),str(ROOT/'cache/devtools'),str(ROOT/'src')]
import capstone
import pefile
from rcm.formats import NotFile, cstring

def main():
    out=ROOT/'research/round0/ctd_cinema_fix'
    out.mkdir(parents=True,exist_ok=True)
    data=Path(r'H:\GOG\Vampire The Masquerade - Redemption\Vampire.exe').read_bytes()
    pe=pefile.PE(data=data);base=pe.OPTIONAL_HEADER.ImageBase
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    def dis(address,limit=200):
        rows=[]
        for op in decoder.disasm(pe.get_data(address-base,limit),address):
            rows.append(dict(address=hex(op.address),instruction=op.mnemonic+' '+op.op_str))
        return rows
    bindings={}
    for name in ['SetTimer','KillTimer','AddToActorInventory','IsActorGuid','IsPlayerGuid']:
        offset=data.index(name.encode()+b'\0');pointer=base+pe.get_rva_from_offset(offset)
        matches=list(re.finditer(re.escape(struct.pack('<I',pointer)),data))
        address=struct.unpack_from('<I',data,matches[0].start()+8)[0]
        rows=dis(address,80)
        calls=[int(r['instruction'].split()[1],16) for r in rows if r['instruction'].startswith('call 0x')]
        bindings[name]=dict(binding=hex(address),body=rows,callees={hex(a):dis(a) for a in calls})
    (out/'native_bindings.json').write_text(json.dumps(dict(sha256=hashlib.sha256(data).hexdigest(),bindings=bindings),indent=2))
    (out/'timer_queue.json').write_text(json.dumps(dict(append=dis(0x4b58a0,144),remove=dis(0x4b5940,170)),indent=2))
    (out/'item_consumption.json').write_text(json.dumps(dict(add=dis(0x46dce0,100),insert=dis(0x460e00,470)),indent=2))
    templates={}
    for path in (ROOT/'research/original/Resource.nob').rglob('*.not'):
        for t in NotFile.read(path.read_bytes()).templates:
            templates[t.name.casefold()]=(t,path)
    chosen={}
    for name in ['BoneKey','IronKeyLondon','Anezka','Otto']:
        chain=[];key=name.casefold()
        while key in templates:
            t,path=templates[key]
            chain.append(dict(name=t.name,source=str(path.relative_to(ROOT)),tags=[dict(id=r.id,text=cstring(r.value),hex=r.value.hex()) for r in t.tags]))
            key=cstring(t.values().get(0,b'')).casefold()
        chosen[name]=chain
    (out/'templates.json').write_text(json.dumps(chosen,indent=2))
    print('Bindings:',{k:v['binding'] for k,v in bindings.items()})
    print('Anezka matches:',[v[0].name for k,v in templates.items() if 'anezka' in k])
    print('Doors:',[v[0].name for k,v in templates.items() if 'door' in k])

if __name__=='__main__':main()

"""Read original notes/motion contracts. No authoring tool or engine is run."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,struct,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/vendor'),str(ROOT/'cache/devtools')]
import pefile,capstone

class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)

def main():
    folder=ROOT/'research/round0/notes_motion';folder.mkdir(parents=True,exist_ok=True)
    for name in ('CodexThing','Codex'):
        path=ROOT/'research/phase7/embrace'/(name+'.htm.decoded.htm')
        parser=Text();parser.feed(path.read_text(encoding='utf8',errors='replace'))
        text='\n'.join(s.strip() for s in parser.parts if s.strip())
        (folder/(name+'.txt')).write_text(text,encoding='utf8')
        for method in ('PlayMotionSetMode','ExecuteText'):
            at=text.rfind(method)
            if at!=-1:print(text[at-100:at+1700])
    game=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
    records=[]
    for archive in game.glob('*.nob'):
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                if name.lower().endswith('.nls'):
                    data=z.read(name)
                    for line in data.decode('cp1252').splitlines():
                        if line.startswith(('SocietyDocument1 ','NodFragment ','Narrator_15_1_560 ')):
                            records.append(dict(archive=archive.name,path=name,text=line))
                elif name.lower().endswith('.nad') and Path(name).name.lower() in {'christof_wave.nad','christof_give.nad','christof_bowfealty2.nad','christof_menacing.nad','christof_taunt.nad'}:
                    data=z.read(name);(folder/Path(name).name).write_bytes(data)
                    records.append(dict(archive=archive.name,path=name,header=data[:80].hex(),bytes=len(data)))
    (folder/'original_resources.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    data=(game/'Vampire.exe').read_bytes();pe=pefile.PE(data=data);base=pe.OPTIONAL_HEADER.ImageBase
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    def disasm(address,size=600):
        rows=[]
        for op in decoder.disasm(pe.get_data(address-base,size),address):
            rows.append(dict(address=hex(op.address),instruction=op.mnemonic+' '+op.op_str))
            if op.mnemonic=='ret':break
        return rows
    bindings={}
    for name in ('PlayMotionSetMode','ExecuteText'):
        pointer=base+pe.get_rva_from_offset(data.index(name.encode()+b'\0'))
        for match in re.finditer(re.escape(struct.pack('<I',pointer)),data):
            address=struct.unpack_from('<I',data,match.start()+8)[0]
            if not base<=address<base+pe.OPTIONAL_HEADER.SizeOfImage:continue
            body=disasm(address)
            calls=[int(r['instruction'].split()[1],16) for r in body if r['instruction'].startswith('call 0x')]
            bindings[name]=dict(address=hex(address),body=body,callees={hex(a):disasm(a) for a in calls[-2:]})
    (folder/'native_bindings.json').write_text(json.dumps(dict(sha256=hashlib.sha256(data).hexdigest(),bindings=bindings,executed=False),indent=2),encoding='utf8')
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()

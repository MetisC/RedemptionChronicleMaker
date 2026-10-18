"""Read-only primary-source inventory for the Embrace authoring closure."""
from pathlib import Path
import collections,hashlib,json,math,struct,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/devtools'),str(ROOT/'cache/vendor'),str(ROOT/'src')]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
OUT=ROOT/'research/embrace_closure'
METHODS=['PlayPath','AddFade','AddFlash','AddFilter','ClearAllEffects','LookAtThing','LookAtPos','PlayMotionSetMode','StopActorAction','SendActorToPos','TeleportPartyToConversation','GetInterest','SetWeatherEffect','AllocateDynamicLight','SetDynamicLightColor','SetDynamicLightRadius','SetDynamicLightIntensity','SetDynamicLightStyle','ClearDynamicLight','EnableLightStyle','DisableLightStyle','PushMusic','PopMusic']


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    catalogue=[];columns=[[] for _ in range(26)]
    with zipfile.ZipFile(GAME/'Resource.nob') as archive:
        for name in archive.namelist():
            if not name.lower().endswith('.ncp'):continue
            data=archive.read(name);count,total=struct.unpack_from('<If',data)
            frames=[list(struct.unpack_from('<26f',data,8+104*i)) for i in range(count)]
            for row in frames:
                for i,v in enumerate(row):columns[i].append(v)
            catalogue.append(dict(path=name,archive='Resource.nob',sha256=hashlib.sha256(data).hexdigest(),size=len(data),count=count,total=total,matches=len(data)==8+104*count,frames=frames))
    (OUT/'ncp_catalogue.json').write_text(json.dumps(catalogue,indent=2),encoding='utf8')
    analysis=[dict(offset=i*4,finite=all(math.isfinite(v) for v in column),min=min(column),max=max(column),unique=len(set(column)),zero=sum(v==0 for v in column)) for i,column in enumerate(columns)]
    (OUT/'ncp_field_analysis.json').write_text(json.dumps(dict(files=len(catalogue),count_histogram=dict(collections.Counter(r['count'] for r in catalogue)),columns=analysis),indent=2),encoding='utf8')
    classes=[];matches={m:[] for m in METHODS}
    with zipfile.ZipFile(GAME/'Codex.nob') as archive:
        for name in archive.namelist():
            if not name.endswith('.class') or name.startswith(('Codex','java/')):continue
            data=archive.read(name);found=[m for m in METHODS if m.encode() in data]
            if found:
                classes.append(Path(name).stem)
                for m in found:matches[m].append(name)
    (OUT/'original_method_references.json').write_text(json.dumps(matches,indent=2),encoding='utf8')
    text=[]
    for start in range(0,len(classes),35):
        result=subprocess.run(['javap','-classpath',str(GAME/'Codex.nob'),'-c','-p',*classes[start:start+35]],capture_output=True,text=True,encoding='utf8',errors='replace',check=True)
        text.append(result.stdout)
    (OUT/'original_callsites.txt').write_text('\n'.join(text),encoding='utf8')
    import pefile,capstone
    pe=pefile.PE(str(GAME/'Vampire.exe'));base=pe.OPTIONAL_HEADER.ImageBase;decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    ranges=[(0x430350,0x431720),(0x46e1a0,0x46e520),(0x4079d0,0x407a10)]
    text=[]
    for start,end in ranges:
        text.append('RANGE '+hex(start)+'..'+hex(end))
        text.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in decoder.disasm(pe.get_data(start-base,end-start),start))
    (OUT/'native_ncp.txt').write_text('\n'.join(text),encoding='utf8')
    (OUT/'source_identity.json').write_text(json.dumps(dict(head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),vampire_sha256=hashlib.sha256((GAME/'Vampire.exe').read_bytes()).hexdigest(),native_engine_test=False),indent=2),encoding='utf8')
    print(json.dumps(dict(ncp_files=len(catalogue),script_classes=len(classes),method_references={m:len(v) for m,v in matches.items()}),indent=2))


if __name__=='__main__':run()

"""Read-only evidence from the installed game; no game or authoring tool runs."""
import hashlib,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor'),str(ROOT/'cache/devtools')]
from rcm.formats import read_tags,cstring,u32
from rcm.script_parameters import read
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
import pefile

GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
NAMES=['ARC3_Erik','DOCK_33_1_Main','HILL_13_1','TEN1_28_1_MeetPink','UNIV_7_7','WAR3_Main']


def tag_records(data):
    records=[]
    for match in re.finditer(rb'\x00\x00\x00\x00([A-Za-z_][A-Za-z_0-9]{2,31})\x00',data):
        offset=match.start()-4
        if offset<84:continue
        count=u32(data,offset)
        if not 1<=count<=100 or offset+4+count*36>len(data):continue
        tags,end=read_tags(data,offset);values={t.id:t.value for t in tags}
        if len(values)!=count or 0 not in values:continue
        records.append(dict(offset=offset,end=end,template=cstring(values[0]),script=cstring(values[11]) if 11 in values else None))
    return records


def main():
    folder=ROOT/'cache/research/player_contexts';folder.mkdir(parents=True,exist_ok=True)
    classes=[]
    with zipfile.ZipFile(GAME/'Codex.nob') as z:
        for name in NAMES+['CodexPlayer','CodexCamera']:
            path=next(p for p in z.namelist() if Path(p).stem==name and p.endswith('.class'))
            data=z.read(path);(folder/(name+'.class')).write_bytes(data)
            text=subprocess.run(['javap','-c','-p','-classpath',str(folder),name],capture_output=True,text=True,check=True).stdout
            (folder/(name+'.txt')).write_text(text,encoding='utf8')
            if name in NAMES:
                ctor=text.split('  public '+name+'(',1)[1].split('\n  public ',1)[0]
                classes.append(dict(class_=name,sha256=hashlib.sha256(data).hexdigest(),constructor='('+ctor.split(';',1)[0]+';',chronicle_casts=sorted(set(re.findall(r'// class (\w+Chronicle)',ctor))),player_fields=sorted(set(re.findall(r'Field (\w+):LCodexPlayer;',ctor))),captures_constructor_argument='Method Codex.CaptureThing:' in ctor,save_override='public void save(' in text,restore_override='public void restore(' in text,hardcoded_strings=sorted(set(re.findall(r'// String ([^\n]+)',text)))))
    scenes=[]
    with zipfile.ZipFile(GAME/'Resource.nob') as z:
        for name in z.namelist():
            if not name.lower().endswith('.nsd'):continue
            data=z.read(name)
            if not any(n.encode()+b'\0' in data for n in NAMES):continue
            rows=tag_records(data)
            for row in rows:
                if row['script'] not in NAMES:continue
                p=row['end'];p+=4+24*u32(data,p);params,end=read(data,p+4,u32(data,p));links=[]
                for arg in params:
                    if arg.kind!=9:continue
                    index=struct.unpack('<i',arg.raw)[0]
                    target=rows[index]['template'] if len(rows)==u32(data,80) and 0<=index<len(rows) else None
                    links.append(dict(kind=9,index=index,target_template=target))
                scenes.append(dict(scene=name,class_=row['script'],declared_entities=u32(data,80),recognised_tag_sets=len(rows),player_links=links,evidence='bounded tag-set scan; target name only when count matches; not a production full NSD reader'))
    exe=(GAME/'Vampire.exe').read_bytes();pe=pefile.PE(data=exe);base=pe.OPTIONAL_HEADER.ImageBase;md=Cs(CS_ARCH_X86,CS_MODE_32)
    targets={str(kind):struct.unpack('<I',pe.get_data(0x4b5608-base+(kind-1)*4,4))[0] for kind in (3,5,8,9,10)}
    ranges=[(0x4b5302,0x4b53df),(0x4b5fc0,0x4b6080),(0x46e238,0x46e268),(0x4a87a0,0x4a894e)]
    lines=[]
    for start,end in ranges:
        lines.append('\nRANGE '+hex(start))
        lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in md.disasm(pe.get_data(start-base,end-start),start))
    (ROOT/'research/authoring_completion/final_native.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
    light='\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in md.disasm(pe.get_data(0x4c44c0-base,0x1e0),0x4c44c0))+'\n'
    (ROOT/'research/authoring_completion/light_payload_reader.txt').write_text(light,encoding='utf8')
    strings=sorted(set(s.decode('ascii') for s in re.findall(rb'[\x20-\x7e]{3,100}\0',exe) for s in [s[:-1]] if re.search(rb'\bfov\b|field.?of.?view|lens',s,re.I)))
    report=dict(executable_sha256=hashlib.sha256(exe).hexdigest(),player_classes=classes,scenes=scenes,entity_reference_switch=targets,camera_lens_string_candidates=strings,native_game_test=False,game_originals_written=False)
    (ROOT/'research/authoring_completion/final_original_evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(classes=len(classes),scenes=len(scenes),player_links=scenes,reference_targets=targets,lens_candidates=strings),ensure_ascii=False))


if __name__=='__main__':main()

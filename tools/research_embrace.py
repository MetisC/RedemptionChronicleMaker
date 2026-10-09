"""Fetch archived SDK references into workspace; never installs or runs old tools."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,time,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'research/phase7/embrace';DEST.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('url');parser.add_argument('name');args=parser.parse_args()
if Path(args.name).name!=args.name:raise ValueError('Nombre de investigación inválido')
request=urllib.request.Request(args.url,headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(request,timeout=30) as response:
    data=response.read(64*1024*1024+1);url=response.url;kind=response.headers.get('Content-Type','')
if len(data)>64*1024*1024:raise ValueError('Descarga excesiva')
path=DEST/args.name;path.write_bytes(data)
record={'source':args.url,'final_url':url,'downloaded_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'file':str(path.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':kind,'executed':False}
(DEST/(args.name+'.json')).write_text(json.dumps(record,indent=2),encoding='utf8')
if zipfile.is_zipfile(path):
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        if len(infos)>5000 or sum(i.file_size for i in infos)>128*1024*1024:raise ValueError('SDK archive excesivo')
        targets=[]
        for info in infos:
            name=info.filename.replace('\\','/')
            if name.startswith('/') or ':' in name or '..' in Path(name).parts:raise ValueError('Ruta insegura en SDK')
            target=(DEST/'sdk'/name).resolve()
            if not target.is_relative_to((DEST/'sdk').resolve()):raise ValueError('SDK fuera de research')
            if not info.is_dir():targets.append((info,target))
        for info,target in targets:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(info))
        (DEST/'sdk_inventory.json').write_text(json.dumps([{'path':i.filename,'bytes':i.file_size} for i in infos],indent=2),encoding='utf8')
else:
    if data.startswith(b'\x1f\x8b'):
        data=gzip.decompress(data)
        if len(data)>128*1024*1024:raise ValueError('Documento expandido excesivo')
        decoded=DEST/(args.name+'.decoded.htm');decoded.write_bytes(data)
        record['decoded_file']=str(decoded.relative_to(ROOT));record['decoded_sha256']=hashlib.sha256(data).hexdigest()
    text=data.decode('utf8',errors='replace')
    record['links']=[url for url in re.findall(r'(?:href|src)=[\"\']([^\"\']+)',text) if any(k in url.lower() for k in ['download','zip','htm','embrace','scene'])]
(DEST/(args.name+'.json')).write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record,indent=2))

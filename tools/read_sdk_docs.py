"""Decode archived HTTP gzip bodies and make readable local research copies."""
from pathlib import Path
from html.parser import HTMLParser
import gzip, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'research/phase7/embrace'
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.hidden=0
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data)
    def handle_starttag(self,tag,attrs):
        if tag in {'style','script'}:self.hidden+=1
        if tag in {'p','br','h1','h2','h3','h4','tr','li','div'}:self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in {'style','script'}:self.hidden=max(0,self.hidden-1)
for path in sorted(DEST.glob('*.htm')):
    if '.decoded.' in path.name:continue
    data=path.read_bytes();meta_path=path.with_name(path.name+'.json')
    meta=json.loads(meta_path.read_text(encoding='utf8')) if meta_path.exists() else {}
    if data.startswith(b'\x1f\x8b'):
        data=gzip.decompress(data);target=path.with_name(path.name+'.decoded.htm');target.write_bytes(data)
        meta.update(decoded_file=str(target.relative_to(ROOT)),decoded_sha256=hashlib.sha256(data).hexdigest())
    parser=Text();parser.feed(data.decode('cp1252',errors='replace'))
    text='\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
    output=path.with_name(path.name+'.txt');output.write_text(text,encoding='utf8')
    meta.update(text_file=str(output.relative_to(ROOT)),text_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    meta_path.write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(path.name,len(data),len(text))

"""A scene view holds references into ONE campaign source, never another file."""
import copy
from .document import Document,draft_shape
from .service import source_text
from .model import identifier

class CampaignDocument(Document):
    def __init__(self,ws,campaign,path=None):
        self.campaign=campaign; self.active=0;self.ws=ws;self.path=ws.output(path) if path else None
        self._saved=source_text(campaign) if path else None
    @property
    def data(self):
        s=self.campaign['scenes'][self.active]
        return {'schema':2,'chronicle':self.campaign['chronicle'],'state':self.campaign.setdefault('state',{'flags':{}}),
                **{k:s.setdefault(k,[] if k!='level' else {'source':''}) for k in ['level','actors','objects','conversations','events','triggers']},
                **({k:s.setdefault(k,[]) for k in ('entries','waypoints')} if self.campaign.get('project_format')==9 else {})}
    @data.setter
    def data(self,value):
        # Undo/redo snapshots always contain the complete campaign.
        if value.get('schema')!=2 or 'scenes' not in value: raise ValueError('Se requiere snapshot de campaña completo')
        self.campaign=value;self.active=min(self.active,len(value['scenes'])-1)
    @property
    def modified(self):return source_text(self.campaign)!=self._saved
    def snapshot(self):return copy.deepcopy(self.campaign)
    @classmethod
    def new(cls,ws,pid,name,directory,description=''):
        identifier(pid,'ID de crónica',14)
        from pathlib import Path
        path=ws.output(Path(directory)/'project.yaml')
        if path.exists():raise ValueError('Ya existe project.yaml en ese directorio')
        scene=dict(id='scene1',level={'source':''},actors=[],objects=[],conversations=[],events=[],triggers=[],encounters=[],sequences=[],entries=[],waypoints=[],paths=[])
        data=dict(schema=2,project_format=9,chronicle=dict(id=pid,name=name,description=description),state={'flags':{}},entry='scene1',scenes=[scene],quests=[],resources={},metadata={'version':'0.1.0'},build_options={'debug':True})
        doc=cls(ws,data);doc.path=path;return doc
    @classmethod
    def load_data(cls,ws,data,path):
        from .input_limits import check_data
        check_data(data)
        if not isinstance(data.get('resources',{}),dict):raise ValueError('Recursos: requiere objeto')
        for key,rows in data.get('resources',{}).items():
            if key not in {'templates','ai_profiles','textures','scripts'} or not isinstance(rows,list):raise ValueError('Categoría de recursos inválida')
            for row in rows:
                if not isinstance(row,dict) or not isinstance(row.get('id'),str):raise ValueError('Recurso: requiere registro e ID')
                if key in {'scripts','textures'} and not isinstance(row.get('source'),str):raise ValueError('Recurso: requiere source')
                if key in {'templates','ai_profiles'} and (not isinstance(row.get('base'),str) or not isinstance(row.get('properties',{}),dict)):raise ValueError('Template/AI: requiere base y propiedades')
        if not isinstance(data.get('scenes'),list) or not data['scenes']:raise ValueError('Campaña sin escenas')
        def records(value,label):
            if not isinstance(value,list) or any(not isinstance(v,dict) for v in value):raise ValueError(label+': requiere registros')
            return value
        def strings(row,keys,label):
            if any(not isinstance(row.get(k),str) for k in keys):raise ValueError(label+': requiere texto')
        def condition(c,depth=0):
            if not isinstance(c,dict) or depth>12:raise ValueError('Forma de condición inválida')
            for key in ('all','any'):
                if key in c:
                    for child in records(c[key],'Condiciones'):condition(child,depth+1)
            if 'not' in c:condition(c['not'],depth+1)
        # GUI accepts semantic drafts, but never corrupt structures.
        for s in records(data['scenes'],'Escenas'):
            strings(s,['id'],'Escena')
            if not all(k in s for k in ['level','actors','conversations','events']):raise ValueError('Escena incompleta')
            view={'schema':1,'chronicle':data['chronicle'],'state':data.get('state',{}),**s}
            # Extended conditions are checked by the campaign validator, not the old flag-only shape check.
            view['events']=[]
            draft_shape(view)
            if not isinstance(s.get('events'),list) or any(not isinstance(e,dict) or not isinstance(e.get('actions'),list) or not isinstance(e.get('conditions',[]),list) for e in s['events']):raise ValueError('Forma de evento inválida')
            for e in s['events']:
                strings(e,['id','when'],'Evento');records(e['actions'],'Acciones')
                for c in e.get('conditions',[]):condition(c)
            for a in s['actors']:
                if 'inventory' in a and (not isinstance(a['inventory'],list) or any(not isinstance(i,str) for i in a['inventory'])):raise ValueError('Inventario: requiere IDs de objetos')
            for g in records(s.get('encounters',[]),'Encuentros'):
                strings(g,['id','name'],'Encuentro')
                if not isinstance(g.get('actors'),list) or any(not isinstance(a,str) for a in g['actors']):raise ValueError('Encuentro: requiere IDs de actores')
            for seq in records(s.get('sequences',[]),'Secuencias'):
                strings(seq,['id','name','actor','shot','angle'],'Secuencia')
                if type(seq.get('duration')) not in (int,float):raise ValueError('Duración: requiere un número')
                if 'camera_path' in seq and not isinstance(seq['camera_path'],str):raise ValueError('Recorrido de cámara requiere ID')
                for step in records(seq.get('steps',[]),'Planos'):
                    strings(step,['actor','preset'],'Plano')
                    if type(step.get('at')) not in (int,float):raise ValueError('Tiempo del plano requiere número')
            if data.get('project_format')==9:
                from .authoring9 import validate_markers
                # Loading semantic drafts permits unresolved path/entry references,
                # but finite transforms are mandatory for safe spatial rendering.
                validate_markers({k:v for k,v in s.items() if k not in ('paths','default_entry')},{})
                for row in records(s.get('paths',[]),'Recorridos'):
                    strings(row,['id','name','actor'],'Recorrido')
                    if not isinstance(row.get('points'),list) or any(not isinstance(p,str) for p in row['points']):raise ValueError('Recorrido: requiere lista de waypoints')
        for q in records(data.get('quests',[]),'Quests'):
            strings(q,['id','title','description'],'Quest')
            if not isinstance(q.get('steps'),list) or any(not isinstance(st,str) for st in q['steps']):raise ValueError('Pasos: requiere textos')
            if type(q.get('reward_xp',0)) is not int:raise ValueError('Recompensa: requiere un entero')
        return cls(ws,data,path)
    def save(self,path=None):
        target=self.ws.output(path or self.path)
        if target.exists():self._atomic_write(target.with_name(target.name+'.backup'),target.read_text(encoding='utf8'))
        content=source_text(self.campaign);self._atomic_write(target,content);old=self.recovery_path
        self.path=target;self._saved=content
        for recovery in (old,self.recovery_path):
            if recovery and recovery.exists():self.ws.output(recovery).unlink()
        return target
    def autosave(self):
        if self.modified and self.recovery_path:self._atomic_write(self.recovery_path,source_text(self.campaign))
    def recover(self):
        if not self.recovery_path or not self.recovery_path.exists(): return False
        recovered=Document.load(self.ws,self.recovery_path)
        self.data=recovered.snapshot()
        return True
    def rename(self,collection,index,new):
        identifier(new,'ID',16);rows=self.data[collection];old=rows[index]['id']
        if any(i!=index and v['id']==new for i,v in enumerate(rows)):raise ValueError('ID duplicado')
        rows[index]['id']=new
        keys={'actors':{'speaker','actor','spawn','remove','actor_alive','entity_exists','enable_ai','disable_ai','stop_patrol'},'objects':{'spawn','remove','item','owns_item','give_item','take_item','entity_exists','object','focus'},'conversations':{'default','then','start_conversation','conversation'},'events':set(),'triggers':{'trigger'},'entries':{'default_entry'},'waypoints':set()}[collection]
        self._replace(self.campaign['scenes'][self.active],keys,old,new)
        if collection=='entries':
            sid=self.campaign['scenes'][self.active]['id']
            for s in self.campaign['scenes']:
                for e in s['events']:
                    for a in e['actions']:
                        if isinstance(a.get('travel'),dict) and a['travel']['scene']==sid and a['travel']['entry']==old:a['travel']['entry']=new
        if collection=='waypoints':
            for route in self.campaign['scenes'][self.active].get('paths',[]):route['points']=[new if p==old else p for p in route['points']]
        if collection=='objects':
            sid=self.campaign['scenes'][self.active]['id']
            self._replace(self.campaign,{'owns_item','take_item'},sid+'.'+old,sid+'.'+new)
        for g in self.campaign['scenes'][self.active].get('encounters',[]):g['actors']=[new if x==old and collection=='actors' else x for x in g['actors']]
        for a in self.data['actors']:a['inventory']=[new if x==old and collection=='objects' else x for x in a.get('inventory',[])]
    def rename_global(self,collection,index,new):
        identifier(new,'ID',16);rows=self.campaign[collection];old=rows[index]['id']
        if any(i!=index and r['id']==new for i,r in enumerate(rows)):raise ValueError('ID duplicado')
        rows[index]['id']=new
        keys={'quests':{'quest','start_quest','advance_quest','complete_quest'},'scenes':{'jump','scene'}}[collection]
        if collection=='scenes' and self.campaign['entry']==old:self.campaign['entry']=new
        self._replace(self.campaign,keys,old,new)
        if collection=='scenes':
            for obj in rows[index].get('objects',[]):self._replace(self.campaign,{'owns_item','take_item'},old+'.'+obj['id'],new+'.'+obj['id'])
    def rename_flag(self,old,new):
        super().rename_flag(old,new)
        self._replace(self.campaign,{'flag','set_flag','clear_flag','when_flag'},old,new)

    @classmethod
    def convert(cls,doc):
        data=doc.snapshot();scene={k:v for k,v in data.items() if k not in {'schema','chronicle','state'}}
        scene['id']='london';scene.setdefault('objects',[]);scene.setdefault('triggers',[])
        for i,e in enumerate(scene['events']):e.setdefault('id','event'+str(i+1))
        source={'schema':2,'chronicle':data['chronicle'],'state':data.get('state',{'flags':{}}),'entry':scene['id'],'scenes':[scene],'quests':[]}
        converted=cls(doc.ws,source,doc.path);converted._saved=doc._saved;return converted

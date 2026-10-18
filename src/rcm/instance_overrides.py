"""Placed-instance intent, lowered to a minimal inherited NOT record, not a clone."""
import hashlib
from .model import mapping


def lower(root):
    for scene in root.get('scenes',[]):
        for entity in scene.get('actors',[])+scene.get('objects',[]):
            if 'overrides' not in entity:continue
            if root.get('project_format') not in (9,10):raise ValueError('Overrides de instancia requieren formato 9 o 10')
            value=entity.pop('overrides')
            mapping(value,{'ai','foley','motions','hover_text','treasure_class'},label='Overrides de instancia')
            if not value:continue
            name='O_'+hashlib.sha256((root['chronicle']['id']+'/'+scene['id']+'/'+entity['id']).encode()).hexdigest()[:22]
            row=dict(id=name,base=entity['template'],properties={k:v for k,v in value.items() if k!='hover_text'})
            if 'hover_text' in value:row['hover_text']=value['hover_text']
            templates=root.setdefault('resources',{}).setdefault('templates',[])
            if any(r['id']==name for r in templates):raise ValueError('Colisión de template de instancia')
            templates.append(row);entity['template']=name

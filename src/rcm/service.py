"""Shared validation/build API for the CLI and desktop editor; no Qt dependency."""
from dataclasses import dataclass
import json
import hashlib
import threading
import yaml

from .model import parse_project, UniqueLoader, Project
from .generator import build
from .paths import Workspace
from .input_limits import parse_source


@dataclass(frozen=True)
class Problem:
    severity: str
    message: str
    path: tuple = ()


@dataclass
class Validation:
    project: Project | None
    problems: list[Problem]

    @property
    def valid(self):
        return self.project is not None and not any(p.severity == "ERROR" for p in self.problems)


class SourceDumper(yaml.SafeDumper):
    def ignore_aliases(self,data):return True


def source_text(data):
    # Sources must round-trip through our alias-free, bounded loader even when
    # a recipe shares an immutable list between several definitions.
    return yaml.dump(data,Dumper=SourceDumper,allow_unicode=True,sort_keys=False,width=110)


class Backend:
    def __init__(self, workspace: Workspace):
        self.ws = workspace
        from .startup import cache_errors
        errors=cache_errors(workspace)
        if errors:raise ValueError('Catálogos ausentes o corruptos. Ejecuta scan o abre el editor para reconstruirlos: '+'; '.join(errors))
        self.levels = json.loads(workspace.output("cache/levels.json").read_text(encoding="utf8"))
        self.resources = json.loads(workspace.output("cache/resources.json").read_text(encoding="utf8"))
        from .motions import ensure_catalogue
        self.resources['motion_catalogue']=ensure_catalogue(workspace,self.resources)
        self.original_resources=self.resources
        self.project_payload={}
        self.hints = json.loads(workspace.output("cache/scene_hints.json").read_text(encoding="utf8"))
        self._build_lock = threading.Lock()
        self.strings = {}
        for path in workspace.output("research/original/Local_Eng.nob/strings").glob("*.nls"):
            for line in path.read_text(encoding="cp1252", errors="replace").splitlines():
                parts = line.strip().split(None, 1)
                if len(parts) == 2 and not parts[0].startswith(("#", "//")):
                    self.strings[parts[0]] = parts[1]

    def sync_resources(self,source):
        from .project_resources import prepare
        key=build_inputs_fingerprint(self.ws,{k:source.get(k) for k in ['project_format','resources','chronicle']})
        if key==getattr(self,'_resources_key',None):return
        _,self.resources,self.project_payload,_=prepare(self.ws,source,self.original_resources)
        self._resources_key=key

    def validate(self, source: str | dict, catalogue=None):
        if not isinstance(source, (str, dict)):
            return Validation(None, [Problem("ERROR", "El proyecto debe ser texto YAML o un objeto de datos")])
        try:
            raw = parse_source(source)
            authoring_raw=raw
            resources=catalogue or self.original_resources
            if isinstance(raw,dict) and any(k in raw for k in ['project_format','resources','metadata','playtests','build_options']):
                from .project_resources import prepare
                raw,resources,_,_=prepare(self.ws,raw,self.original_resources)
            if isinstance(raw, dict) and raw.get('schema') == 2:
                from .campaign import parse_campaign, integrity
                campaign = parse_campaign(raw, self.levels, resources)
                problems = integrity(campaign)
                from .recipes import recipes,missing
                for i,recipe in enumerate(recipes(authoring_raw)):
                    absent=missing(authoring_raw,recipe)
                    if absent:problems.append(Problem('WARNING','Incomplete configuration: '+recipe['id']+' ('+', '.join(absent)+')',('authoring','recipes',i)))
                for si, (scene, project) in enumerate(campaign.scenes):
                    if not (project.entities and project.conversations):
                        problems += [Problem(p.severity, scene['id']+': '+p.message, ('scenes',si)+p.path) for p in self.environment_problems(project)]
                    if not self.level_usable(project.level):
                        problems.append(Problem('ERROR', 'Escena sin anchor original estudiado', ('scenes', si, 'level')))
                    if project.entities and project.conversations:
                        prior = self.validate(project_source(project),resources)
                        problems += [Problem(p.severity, scene['id']+': '+p.message, ('scenes',si)+p.path) for p in prior.problems]
                return Validation(campaign, problems)
            project = parse_project(source_text(raw),self.levels, resources)
        except (ValueError, yaml.YAMLError, TypeError, KeyError, OSError) as error:
            if isinstance(error, yaml.YAMLError):
                mark = getattr(error, "problem_mark", None)
                message = "YAML inválido" + (f" en línea {mark.line+1}" if mark else "")
            else:
                message = str(error) if isinstance(error, ValueError) else "Tipo o referencia inválidos en el proyecto"
            data = source if isinstance(source, dict) else None
            return Validation(None, [Problem("ERROR", message, self.error_path(data, message))])
        problems = self.environment_problems(project)
        indices = {"actor": 0, "object": 0}
        for entity in project.entities:
            i = indices[entity.kind]
            indices[entity.kind] += 1
            if entity.transform.position == (0, 0, 0):
                problems.append(Problem("WARNING", f"{entity.name}: posición 0, 0, 0; comprueba que sea válida.", ("actors" if entity.kind == "actor" else "objects", i)))
            if entity.transform.placement == "absolute":
                problems.append(Problem("INFO", f"{entity.name}: coordenadas válidas como datos; el suelo y la colisión deben comprobarse en el juego.", ("actors" if entity.kind == "actor" else "objects", i)))
        for i, conv in enumerate(project.conversations):
            if not conv.nodes:
                continue
            nodes = {n.id: n for n in conv.nodes}
            reached, pending = set(), [conv.entry]
            while pending:
                nid = pending.pop()
                if nid in reached:
                    continue
                reached.add(nid)
                pending.extend(c.target for c in nodes[nid].choices if c.target is not None)
            for j, node in enumerate(conv.nodes):
                if node.id not in reached:
                    problems.append(Problem("WARNING", f"{conv.id}: el nodo {node.id} no es alcanzable desde la entrada.", ("conversations", i, "nodes", j)))
            escaping = {n.id for n in conv.nodes if any(c.target is None for c in n.choices)}
            while True:
                expanded = escaping | {n.id for n in conv.nodes if any(c.target in escaping for c in n.choices)}
                if expanded == escaping:
                    break
                escaping = expanded
            for j, node in enumerate(conv.nodes):
                if node.id not in escaping:
                    problems.append(Problem("ERROR" if node.id == conv.entry else "WARNING",
                        f"{conv.id}: desde {node.id} no hay camino a una respuesta de salida.", ("conversations", i, "nodes", j)))
        if not self.level_usable(project.level):
            problems.append(Problem("ERROR", "Este level no dispone de una escena de referencia estudiada para construir la capa propia.", ("level",)))
        return Validation(project, problems)

    def environment_problems(self, project):
        from .scene_profiles import environment
        try:
            environment(self.ws, self.levels[project.level], self.hints, project.environment_scene)
        except (ValueError, OSError, KeyError) as error:
            return [Problem('ERROR', str(error), ('level', 'environment_scene'))]
        return []

    def scene_profiles(self, level):
        from .scene_profiles import catalogue
        return catalogue(self.ws, {level:self.levels[level]}, self.hints)[level]

    def error_path(self, data, message):
        """Conservative navigation for contextual parser errors, never guessed offsets."""
        if not data:
            return ()
        if message.startswith("Level") or message.startswith("Recurso sky"):
            return ("level",)
        if "flag" in message.lower() and not message.startswith("Conversación"):
            return ("state", "flags")
        conv_rows = data.get("conversations", [])
        for i, conv in enumerate(conv_rows if isinstance(conv_rows, list) else []):
            if isinstance(conv, dict) and (f"Conversación {conv.get('id')}:" in message or f"Conversación {conv.get('id')}," in message):
                nodes = conv.get("nodes", [])
                for j, node in enumerate(nodes if isinstance(nodes, list) else []):
                    if isinstance(node, dict) and f"nodo {node.get('id')}:" in message:
                        return ("conversations", i, "nodes", j)
                return ("conversations", i)
        if message.startswith("Plantilla desconocida"):
            for key in ["actors", "objects"]:
                actor_rows = data.get(key, [])
                for i, actor in enumerate(actor_rows if isinstance(actor_rows, list) else []):
                    if isinstance(actor, dict) and message.endswith(": " + str(actor.get("template"))):
                        return (key, i)
        return ()

    def level_usable(self, name):
        level = self.levels.get(name, {})
        return (len(level.get("geometry", [])) == 1 and not level.get("alternative_geometry")
                and any(self.hints.get(s.casefold(), {}).get("entities") for s in level.get("scenes", [])))

    def level_label(self, name):
        refs = self.levels[name]["references"]
        return self.strings.get(refs[0]["map_label"], name) if refs else name

    def build(self, source, compile_java=True, progress=None):
        with self._build_lock:
            return self._build_locked(source,compile_java,progress)

    def _build_locked(self, source, compile_java=True, progress=None):
        progress = progress or (lambda message: None)
        progress("Leyendo y validando el proyecto…")
        validation = self.validate(source)
        if not validation.valid:
            error=ValueError("\n".join(p.message for p in validation.problems if p.severity == "ERROR"))
            from .build_transaction import failed_report
            try:failed_report(self.ws,parse_source(source),error)
            except (ValueError,OSError,yaml.YAMLError):pass
            raise error
        if validation.valid:
            from .build_transaction import StagedWorkspace
            prior={}
            try:prior=json.loads(self.ws.output('build/'+validation.project.id+'/build_report.json').read_text(encoding='utf8'))
            except (OSError,ValueError):pass
            staged=StagedWorkspace(self.ws,validation.project.id)
            try:
                initial_inputs=build_inputs_fingerprint(self.ws,source)
                from .build_transaction import failed_report
                failed_report(self.ws,{'chronicle':{'id':validation.project.id}},'Build en curso; despliegue bloqueado')
                raw=yaml.load(source,Loader=UniqueLoader) if isinstance(source,str) else source
                from .project_resources import prepare,add_to_build
                _,resources,payload,info=prepare(self.ws,raw,self.original_resources)
                from .campaign import Campaign
                if isinstance(validation.project, Campaign):
                    from .campaign_generator import build_campaign
                    transform=None
                    if info:
                        from .debugging import instrument
                        transform=lambda java,campaign,scene:instrument(java,campaign,scene,info)
                    report=build_campaign(staged, validation.project, self.levels, resources, self.hints, compile_java, progress,transform)
                else:
                    report=build(staged, validation.project, self.levels, resources, self.hints,
                                 compile_java, progress)
                if info:report=add_to_build(staged,report,payload,info,compile_java)
                from .output_validation import verify_output
                report['format_validation']=verify_output(staged,report,resources)
                report['authoring_source_sha256']=source_fingerprint(source)
                if initial_inputs!=build_inputs_fingerprint(self.ws,source):raise ValueError('Las fuentes propias cambiaron durante el build. Vuelve a compilar')
                report['build_inputs_sha256']=initial_inputs
                p=validation.project
                from .campaign import Campaign
                scenes=[(s['id'],project) for s,project in p.scenes] if isinstance(p,Campaign) else [('single',p)]
                contract={'flags':dict(scenes[0][1].flags),'reserved':p.reserved if isinstance(p,Campaign) else {},'scenes':[{'id':sid,'entities':[e.id for e in project.entities],'conversations':[c.id for c in project.conversations],'events':[e.id for e in project.events],'triggers':[t.id for t in project.triggers]} for sid,project in scenes]}
                if isinstance(p,Campaign) and p.source.get('runtime_profile') in ('phase9','phase10'):
                    contract['runtime_profile']='phase9-v1'
                    contract['player_pose_record_v1']=[s['id'] for s,project in p.scenes]
                    contract['movement']=[{'scene':s['id'],'paths':s.get('paths',[]),'entries':s.get('entries',[])} for s,project in p.scenes]
                    cinematic_scenes=[s['id'] for s,project in p.scenes if any(any(k in seq for k in ('steps','move_path','camera_path','prop_motion')) for seq in s.get('sequences',[]))]
                    if cinematic_scenes:contract['cinema_record_v2']=cinematic_scenes
                    player_cinema=[s['id'] for s,project in p.scenes if any(seq['actor']=='Player' for seq in s.get('sequences',[]))]
                    if player_cinema:contract['player_cinema_resume_v1']=player_cinema
                if isinstance(p,Campaign) and p.source.get('runtime_profile')=='phase10':
                    contract['dynamic_records_v1']=[{'scene':s['id'],'generators':s.get('generators',[])} for s,project in p.scenes]
                report['save_schema_sha256']=source_fingerprint(contract)
                report['new_game_required']=bool(prior) and prior.get('save_schema_sha256')!=report['save_schema_sha256']
                if report['new_game_required']:report['save_warning']='La estructura persistida ha cambiado o no tiene firma previa. Inicia una partida nueva; no hay migrador de saves nativos.'
                return staged.publish(report)
            except Exception as error:
                diagnostic='build/failed_attempts/'+validation.project.id+'_'+staged.stage.name
                try:
                    for path in staged.stage.rglob('*'):
                        if path.is_file() and (path.suffix in {'.log','.java'} or path.name=='source_map.json'):
                            self.ws.write(diagnostic+'/'+path.relative_to(staged.stage).as_posix(),path.read_bytes())
                    self.ws.write(diagnostic+'/failure.txt',str(error))
                    if isinstance(error,ValueError):error.args=(str(error)+'\nDiagnóstico: '+diagnostic,)
                except (OSError,ValueError):pass
                try:
                    failed_report(self.ws,{'chronicle':{'id':validation.project.id}},error)
                except (OSError, ValueError):
                    pass  # Keep the actual build failure if reporting also fails.
                raise
            finally:
                staged.close()


def source_fingerprint(source):
    data=parse_source(source)
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')).hexdigest()

def build_inputs_fingerprint(ws,source):
    data=parse_source(source)
    files={}
    for kind in ['scripts','textures']:
        for row in (data.get('resources') or {}).get(kind,[]):
            path=ws.output(row['source']);files[row['source']]=hashlib.sha256(path.read_bytes()).hexdigest()
    profiles={}
    level_file=ws.output('cache/levels.json');hint_file=ws.output('cache/scene_hints.json')
    if level_file.is_file() and hint_file.is_file():
        from .scene_profiles import environment
        levels=json.loads(level_file.read_text(encoding='utf8'));hints=json.loads(hint_file.read_text(encoding='utf8'))
        for scene in data.get('scenes',[data]):
            level=scene.get('level',{})
            if isinstance(level,dict) and level.get('source') in levels:
                _,record=environment(ws,levels[level['source']],hints,level.get('environment_scene'))
                profiles[level['source']+'/'+record['id']]=record['source_sha256']
    return source_fingerprint({'source':data,'owned_files':files,'original_environment_sources':profiles})


def project_source(p: Project):
    """Typed model -> the same source schema; both legacy and node forms survive."""
    chron = {"id": p.id, "name": p.name}
    if p.description:
        chron["description"] = p.description
    level = {"source": p.level}
    if p.level_name:
        level["name"] = p.level_name
    if p.sky:
        level["sky"] = {"model": p.sky[0], "animation": p.sky[1]}
    if p.environment_scene:
        level['environment_scene'] = p.environment_scene
    data = {"schema": 1, "chronicle": chron, "level": level, "state": {"flags": dict(p.flags)},
            "actors": [], "conversations": [], "events": []}
    for e in p.entities:
        trans = {"orientation": list(e.transform.orientation)}
        if e.transform.placement == "near_player":
            trans["placement"] = "near_player"
        else:
            trans["position"] = list(e.transform.position)
        item = {"id": e.id, "template": e.template, "name": e.name, "transform": trans}
        if e.comment:
            item["comment"] = e.comment
        if e.conversation:
            item["conversation"] = {"default": e.conversation}
            if e.when_flag:
                item["conversation"].update(when_flag=e.when_flag, then=e.after_conversation)
        data.setdefault("actors" if e.kind == "actor" else "objects", []).append(item)
    def choice(c):
        result = {"text": c.text, **({"goto": c.target} if c.target is not None else {"result": c.result})}
        if c.flag:
            result["set_flag" if c.value else "clear_flag"] = c.flag
        return result
    for c in p.conversations:
        item = {"id": c.id, "speaker": c.speaker}
        if c.nodes:
            item.update(entry=c.entry, nodes=[{"id": n.id,
                "lines": [{"speaker": l.speaker, "text": l.text} for l in n.lines],
                "choices": [choice(ch) for ch in n.choices]} for n in c.nodes])
        else:
            item.update(prompt=c.prompt, choices=[choice(ch) for ch in c.choices])
        data["conversations"].append(item)
    for e in p.events:
        item = {"when": e.when, "actions": [{a.kind: a.target} for a in e.actions]}
        if e.id:
            item["id"] = e.id
        if e.conditions:
            item["conditions"] = [{"flag": c.flag, "is_set": c.is_set} for c in e.conditions]
        for key in ["actor", "conversation", "result", "trigger"]:
            if getattr(e, key) is not None:
                item[key] = getattr(e, key)
        data["events"].append(item)
    if p.triggers:
        data['triggers'] = []
        for t in p.triggers:
            item = dict(id=t.id, name=t.name, shape=t.shape, once=t.once,
                        transform=dict(position=list(t.transform.position), orientation=list(t.transform.orientation)))
            if t.size is not None:
                item['size'] = list(t.size)
            if t.radius is not None:
                item['radius'] = t.radius
            data['triggers'].append(item)
    return data

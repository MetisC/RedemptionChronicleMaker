"""Strict YAML -> typed layer model -> validation against discovered resources."""
from dataclasses import dataclass
import math
import re
import yaml


class UniqueLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValueError("No se admiten aliases YAML en el esquema 1")
        return super().compose_node(parent, index)


def unique_mapping(loader, node, deep=False):
    result = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"Clave YAML no textual o duplicada: {key!r}")
        result[key] = loader.construct_object(v, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def mapping(value, allowed, required=(), label="campo"):
    if not isinstance(value, dict):
        raise ValueError(f"{label}: se esperaba un mapping")
    extra = set(value) - set(allowed)
    missing = set(required) - set(value)
    if extra or missing:
        raise ValueError(f"{label}: claves desconocidas {sorted(extra)}, ausentes {sorted(missing)}")
    return value


def identifier(value, label, limit=24):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", value) or len(value) > limit:
        raise ValueError(f"{label}: identificador [a-z][a-z0-9_]*, máximo {limit}")
    if value.upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise ValueError(f"{label}: nombre reservado por Windows")
    return value


def text(value, label):
    if not isinstance(value, str) or not value.strip() or any(c in value for c in "\r\n\0") or "//" in value or "#" in value:
        raise ValueError(f"{label}: texto de una línea sin comentarios ni caracteres de control")
    try:
        value.encode("cp1252")
    except UnicodeEncodeError as e:
        raise ValueError(f"{label}: el runtime usa Windows-1252") from e
    return value


def vector(value, label):
    if not isinstance(value, list) or len(value) != 3 or any(type(x) not in (int, float) or not math.isfinite(x) or abs(x) > 1e7 for x in value):
        raise ValueError(f"{label}: tres números finitos dentro del rango de autoría")
    return tuple(float(x) for x in value)


def sequence(value, label):
    if not isinstance(value, list):
        raise ValueError(f"{label}: se esperaba una lista")
    return value


@dataclass(frozen=True)
class Transform:
    position: tuple[float, float, float] | None
    orientation: tuple[float, float, float]
    placement: str = "absolute"


@dataclass(frozen=True)
class Entity:
    id: str
    template: str
    name: str
    transform: Transform
    kind: str
    conversation: str | None
    when_flag: str | None = None
    after_conversation: str | None = None
    comment: str = ""


@dataclass(frozen=True)
class Choice:
    text: str
    result: int | None
    flag: str | None
    value: bool | None
    target: str | None = None


@dataclass(frozen=True)
class DialogueLine:
    speaker: str
    text: str
    motion: str | None = None
    motion_value: int | None = None


@dataclass(frozen=True)
class DialogueNode:
    id: str
    lines: tuple[DialogueLine, ...]
    choices: tuple[Choice, ...]
    motion: str | None = None


@dataclass(frozen=True)
class Conversation:
    id: str
    speaker: str
    prompt: str
    choices: tuple[Choice, ...]
    nodes: tuple[DialogueNode, ...] = ()
    entry: str | None = None


@dataclass(frozen=True)
class Condition:
    flag: str
    is_set: bool


@dataclass(frozen=True)
class Action:
    kind: str
    target: str


@dataclass(frozen=True)
class Event:
    id: str | None
    when: str
    actions: tuple[Action, ...]
    conditions: tuple[Condition, ...] = ()
    actor: str | None = None
    conversation: str | None = None
    result: int | None = None
    trigger: str | None = None


@dataclass(frozen=True)
class SpatialTrigger:
    id: str
    name: str
    shape: str
    transform: Transform
    size: tuple[float, float, float] | None = None
    radius: float | None = None
    once: bool = True


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    level: str
    flags: dict[str, int]
    entities: tuple[Entity, ...]
    conversations: tuple[Conversation, ...]
    spawns: tuple[str, ...]
    sky: tuple[str, str] | None = None
    events: tuple[Event, ...] = ()
    description: str = ""
    level_name: str | None = None
    triggers: tuple[SpatialTrigger, ...] = ()
    environment_scene: str | None = None

    @property
    def prefix(self):
        return "R_" + self.id


def parse_project(data: str, levels: dict, resources: dict, allow_empty=False, allow_motions=False) -> Project:
    if len(data) > 1024 * 1024:
        raise ValueError("Proyecto YAML demasiado grande")
    root = mapping(yaml.load(data, Loader=UniqueLoader), {"schema", "chronicle", "level", "state", "actors", "objects", "conversations", "events", "triggers"}, {"schema", "chronicle", "level", "actors", "conversations", "events"}, "proyecto")
    if type(root["schema"]) is not int or root["schema"] != 1:
        raise ValueError("Solo se admite schema: 1")
    chron = mapping(root["chronicle"], {"id", "name", "description"}, {"id", "name"}, "chronicle")
    pid = identifier(chron["id"], "chronicle.id", 18)
    name = text(chron["name"], "chronicle.name")
    description = chron.get("description", "")
    if not isinstance(description, str) or len(description) > 8192:
        raise ValueError("La descripción interna debe ser texto de hasta 8192 caracteres")
    level_data = mapping(root["level"], {"source", "sky", "name", "environment_scene"}, {"source"}, "level")
    level_name = text(level_data["name"], "level.name") if "name" in level_data else None
    level = level_data["source"]
    if not isinstance(level, str) or level not in levels or len(levels[level]["geometry"]) != 1 or levels[level].get("alternative_geometry"):
        raise ValueError("Level desconocido, ausente o con geometría ambigua en el catálogo")
    environment_scene = level_data.get('environment_scene')
    if 'environment_scene' in level_data:
        if (not isinstance(environment_scene, str) or not environment_scene
                or environment_scene.casefold() not in {s.casefold() for s in levels[level].get('scenes', [])}):
            raise ValueError('Level: environment_scene debe referenciar una escena original asociada a este level')
    sky = None
    if "sky" in level_data:
        sky_data = mapping(level_data["sky"], {"model", "animation"}, {"model", "animation"}, "level.sky")
        for key, extension in [("model", ".nod"), ("animation", ".nad")]:
            value = sky_data[key]
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,30}", value):
                raise ValueError("Sky requiere nombres de recursos sin extensión de máximo 31 bytes")
            matches = [r for r in resources["entries"] if r["extension"].lower() == extension and r["id"].casefold() == value.casefold()]
            if len(matches) != 1:
                raise ValueError(f"Recurso sky desconocido o ambiguo: {value}{extension}")
        sky = (sky_data["model"], sky_data["animation"])
    state = mapping(root.get("state", {}), {"flags"}, (), "state")
    flags = state.get("flags", {})
    if not isinstance(flags, dict):
        raise ValueError("state.flags: se esperaba un mapping")
    for k, v in flags.items():
        identifier(k, "flag")
        # Conservative authoring policy; not claimed as the native engine maximum.
        if type(v) is not int or not 0 <= v <= 255:
            raise ValueError("Índices de flags admitidos por la herramienta: 0..255")
    if len(set(flags.values())) != len(flags):
        raise ValueError("Dos flags no pueden compartir índice")
    catalogue = {}
    for t in resources["templates"]:
        catalogue.setdefault(t["id"], []).append(t)
    entities, entity_ids = [], set()
    for kind, key in [("actor", "actors"), ("object", "objects")]:
        for row in sequence(root.get(key, []), key):
            v = mapping(row, {"id", "template", "name", "transform", "conversation", "comment", "level"}, {"id", "template", "name", "transform"}, key)
            if "level" in v and v["level"] != level:
                raise ValueError("Solo se admite una ubicación por proyecto; el actor debe usar el level base")
            comment = v.get("comment", "")
            if not isinstance(comment, str) or len(comment) > 8192:
                raise ValueError("El comentario interno debe ser texto de hasta 8192 caracteres")
            eid = identifier(v["id"], key + ".id")
            if eid in entity_ids or len("R_" + pid + "_" + eid) > 31:
                raise ValueError("Identificador de entidad duplicado o namespace mayor de 31 bytes")
            entity_ids.add(eid)
            template = v["template"]
            if not isinstance(template, str) or len(catalogue.get(template, [])) != 1:
                raise ValueError(f"Plantilla desconocida o ambigua: {template}")
            expected = {"actors"} if kind == "actor" else {"items", "props", "weapons", "armour"}
            if catalogue[template][0]["kind"] not in expected:
                raise ValueError(f"La plantilla {template} no sirve como {kind}")
            trans = mapping(v["transform"], {"position", "orientation", "placement"}, {"orientation"}, "transform")
            placement = trans.get("placement", "absolute")
            if placement not in ("absolute", "near_player"):
                raise ValueError("transform.placement debe ser absolute o near_player")
            if (placement == "absolute") != ("position" in trans):
                raise ValueError("absolute requiere position; near_player usa la posición del jugador y no admite position")
            transform = Transform(vector(trans["position"], "position [x,y,z]") if placement == "absolute" else None, vector(trans["orientation"], "orientation [pitch,roll,yaw]"), placement)
            conv = v.get("conversation")
            when_flag, after = None, None
            if conv is not None:
                if kind != "actor":
                    raise ValueError("Las conversaciones solo se asocian a actores en Fase 1")
                conv = mapping(conv, {"default", "when_flag", "then"}, {"default"}, "conversation binding")
                default = conv["default"]
                when_flag, after = conv.get("when_flag"), conv.get("then")
                if bool(when_flag) != bool(after) or (when_flag and when_flag not in flags):
                    raise ValueError("when_flag requiere un flag declarado y una conversación then")
            else:
                default = None
            entities.append(Entity(eid, template, text(v["name"], "name"), transform, kind, default, when_flag, after, comment))
    conversations, conv_ids = [], set()
    for row in sequence(root["conversations"], "conversations"):
        v = mapping(row, {"id", "speaker", "prompt", "choices", "entry", "nodes"}, {"id", "speaker"}, "conversation")
        cid = identifier(v["id"], "conversation.id")
        if cid in conv_ids:
            raise ValueError("Conversación duplicada")
        conv_ids.add(cid)
        if v["speaker"] not in entity_ids or next(e for e in entities if e.id == v["speaker"]).kind != "actor":
            raise ValueError("Speaker debe referenciar un actor declarado")
        conversations.append(parse_conversation(v, cid, pid, entities, flags,resources,allow_motions))
    for e in entities:
        for cid in [e.conversation, e.after_conversation]:
            if cid is not None and (cid not in conv_ids or next(c for c in conversations if c.id == cid).speaker != e.id):
                raise ValueError(f"Conversación {cid} ausente o asociada a otro speaker")
    for c in conversations:
        if not c.nodes and len("R_" + pid + "_" + c.id + "_line") > 31:
            raise ValueError("Identificador NVO generado supera el límite conservador de 31 bytes")
    triggers, trigger_ids = [], set()
    for row in sequence(root.get('triggers', []), 'triggers'):
        v = mapping(row, {'id', 'name', 'shape', 'transform', 'size', 'radius', 'once'}, {'id', 'name', 'shape', 'transform'}, 'trigger')
        tid = identifier(v['id'], 'trigger.id')
        if tid in trigger_ids or tid in entity_ids:
            raise ValueError('ID de trigger duplicado')
        trigger_ids.add(tid)
        trans = mapping(v['transform'], {'position', 'orientation', 'placement'}, {'position', 'orientation'}, 'trigger.transform')
        orient = vector(trans['orientation'], 'trigger.orientation')
        if trans.get('placement', 'absolute') != 'absolute' or orient[:2] != (0, 0):
            raise ValueError('Trigger requiere posición absoluta y orientación horizontal')
        transform = Transform(vector(trans['position'], 'trigger.position'), orient)
        size, radius = None, None
        if v['shape'] == 'box' and 'radius' not in v:
            size = vector(v.get('size'), 'trigger.size')
            if min(size) <= 0:
                raise ValueError('Tamaño de trigger debe ser positivo')
        elif v['shape'] == 'sphere' and 'size' not in v:
            radius = v.get('radius')
            if type(radius) not in (int, float) or not math.isfinite(radius) or not 0 < radius <= 1e7:
                raise ValueError('Radio de trigger debe ser positivo y finito')
            if orient[2] != 0:
                raise ValueError('Una esfera no tiene orientación')
        else:
            raise ValueError('Trigger admite box + size o sphere + radius')
        if type(v.get('once', True)) is not bool:
            raise ValueError('trigger.once debe ser booleano')
        triggers.append(SpatialTrigger(tid, text(v['name'], 'trigger.name'), v['shape'], transform, size, radius, v.get('once', True)))
    events, spawns = parse_events(root["events"], entities, conversations, flags, triggers)
    if set(spawns) != entity_ids:
        raise ValueError("Todas las entidades deben tener un único spawn en scene_start o trigger_enter")
    if not allow_empty and (not entities or not conversations):
        raise ValueError("Se requiere al menos una entidad y una conversación")
    return Project(pid, name, level, flags, tuple(entities), tuple(conversations), tuple(spawns), sky, events, description, level_name, tuple(triggers), environment_scene)


def parse_conversation(v, cid, pid, entities, flags,resources=None,allow_motions=False):
    actors = {e.id for e in entities if e.kind == "actor"}
    results = set()
    def choices(rows, allow_goto=False):
        parsed = []
        for row in sequence(rows, "choices"):
            ch = mapping(row, {"text", "result", "goto", "set_flag", "clear_flag"}, {"text"}, f"conversation {cid} choice")
            if ("result" in ch) == ("goto" in ch):
                raise ValueError(f"Conversación {cid}: cada respuesta requiere RETURN o GOTO, exclusivamente")
            result, target = ch.get("result"), ch.get("goto")
            flag = ch.get("set_flag", ch.get("clear_flag"))
            if target is not None:
                if not allow_goto or flag is not None:
                    raise ValueError(f"Conversación {cid}: GOTO solo en nodos; acciones de flag solo al retornar")
                identifier(target, "choice.goto")
            elif type(result) is not int or not 1 <= result <= 32767 or result in results:
                raise ValueError(f"Conversación {cid}: resultados únicos, enteros 1..32767; 0 reservado")
            if ("set_flag" in ch and "clear_flag" in ch) or (flag is not None and flag not in flags):
                raise ValueError(f"Conversación {cid}: acción de flag contradictoria o flag no declarado")
            if target is None:
                results.add(result)
            parsed.append(Choice(text(ch["text"], "choice.text"), result, flag, "set_flag" in ch if flag else None, target))
        if not 1 <= len(parsed) <= 8:
            raise ValueError(f"Conversación {cid}: cada nodo requiere entre 1 y 8 respuestas")
        return tuple(parsed)
    if "nodes" not in v:
        if "entry" in v or "prompt" not in v or "choices" not in v:
            raise ValueError(f"Conversación {cid}: faltan prompt/choices o nodes/entry")
        return Conversation(cid, v["speaker"], text(v["prompt"], "prompt"), choices(v["choices"]))
    if "prompt" in v or "choices" in v or "entry" not in v:
        raise ValueError(f"Conversación {cid}: no mezclar prompt/choices con nodes/entry")
    nodes, ids = [], set()
    for row in sequence(v["nodes"], "nodes"):
        n = mapping(row, {"id", "lines", "choices", "motion"}, {"id", "lines", "choices"}, "node")
        nid = identifier(n["id"], "node.id")
        if nid in ids:
            raise ValueError(f"Conversación {cid}: nodo duplicado {nid}")
        ids.add(nid)
        lines = []
        for row2 in sequence(n["lines"], "lines"):
            line = mapping(row2, {"speaker", "text", "motion"}, {"text"}, "line")
            speaker = line.get("speaker", v["speaker"])
            if speaker not in actors:
                raise ValueError(f"Conversación {cid}, nodo {nid}: actor inexistente {speaker}")
            motion=line.get('motion',n.get('motion'))
            motion_value=None
            if motion is not None:
                if not allow_motions:raise ValueError('Animación de diálogo requiere formato de proyecto 9')
                from .motions import validate_motion
                motion_value=validate_motion(motion,next(e.template for e in entities if e.id==speaker),resources or {})
            lines.append(DialogueLine(speaker, text(line["text"], "line.text"),motion,motion_value))
        if not lines or len(lines) > 64:
            raise ValueError(f"Conversación {cid}, nodo {nid}: requiere entre 1 y 64 líneas")
        nodes.append(DialogueNode(nid, tuple(lines), choices(n["choices"], True),n.get('motion')))
    if not nodes or len(nodes) > 64 or v["entry"] not in ids:
        raise ValueError(f"Conversación {cid}: nodo de entrada ausente o número de nodos inválido")
    for node in nodes:
        for ch in node.choices:
            if ch.target is not None and ch.target not in ids:
                raise ValueError(f"Conversación {cid}, nodo {node.id}: destino inexistente {ch.target}")
    for i, node in enumerate(nodes):
        for kind, count in [("l", len(node.lines)), ("a", len(node.choices))]:
            if len(f"R_{pid}_{cid}_n{i}_{kind}{count-1}") > 31:
                raise ValueError(f"Conversación {cid}: identificadores generados superan 31 bytes; acorta los IDs")
    terminal = tuple(ch for n in nodes for ch in n.choices if ch.target is None)
    if not terminal:
        raise ValueError(f"Conversación {cid}: falta una respuesta de salida RETURN")
    return Conversation(cid, v["speaker"], nodes[0].lines[0].text, terminal, tuple(nodes), v["entry"])


def parse_events(rows, entities, conversations, flags, triggers=()):
    actors = {e.id for e in entities if e.kind == "actor"}
    ids, spawned, events = set(), [], []
    convs = {c.id: c for c in conversations}
    for row in sequence(rows, "events"):
        v = mapping(row, {"id", "when", "actor", "conversation", "result", "conditions", "actions", "trigger"}, {"when", "actions"}, "event")
        eid = v.get("id")
        if eid is not None:
            identifier(eid, "event.id")
            if eid in ids:
                raise ValueError(f"Evento duplicado: {eid}")
            ids.add(eid)
        when = v["when"]
        if when not in {"scene_start", "actor_clicked", "conversation_ended", "trigger_enter"}:
            raise ValueError(f"Evento no soportado: {when}")
        actor, conv, result = v.get("actor"), v.get("conversation"), v.get("result")
        trigger = v.get('trigger')
        if when == 'trigger_enter':
            if trigger not in {t.id for t in triggers} or any(k in v for k in ('actor', 'conversation', 'result')):
                raise ValueError('Trigger Enter requiere trigger válido sin filtros actor/conversation/result')
        elif trigger is not None:
            raise ValueError('Filtro trigger sólo se admite en trigger_enter')
        if when == "actor_clicked":
            if actor not in actors or conv is not None or result is not None:
                raise ValueError("Actor Clicked requiere un actor válido, sin conversation/result")
            if next(e for e in entities if e.id == actor).conversation:
                raise ValueError(f"Actor {actor}: usa enlace de conversación o eventos de clic, no ambos")
        elif when == "conversation_ended":
            if conv not in convs or actor is not None:
                raise ValueError("Conversation Ended requiere una conversación válida, sin actor")
            if result is not None and (type(result) is not int or result not in {ch.result for ch in convs[conv].choices}):
                raise ValueError("El resultado del evento no corresponde a un RETURN de la conversación")
        elif when == 'scene_start' and any(k in v for k in ("actor", "conversation", "result")):
            raise ValueError("Scene Start no admite filtros actor/conversation/result")
        conditions = []
        for row2 in sequence(v.get("conditions", []), "conditions"):
            c = mapping(row2, {"flag", "is_set"}, {"flag", "is_set"}, "condition")
            if c["flag"] not in flags or type(c["is_set"]) is not bool:
                raise ValueError("Condición requiere un flag declarado y is_set booleano")
            conditions.append(Condition(c["flag"], c["is_set"]))
        actions = []
        for row2 in sequence(v["actions"], "actions"):
            a = mapping(row2, {"spawn", "start_conversation", "set_flag", "clear_flag"}, (), "action")
            if len(a) != 1:
                raise ValueError("Cada acción requiere exactamente una operación")
            kind, target = next(iter(a.items()))
            if kind == "spawn":
                if when not in {"scene_start", "trigger_enter"} or target not in {e.id for e in entities} or target in spawned:
                    raise ValueError("Spawn desconocido, duplicado o fuera de Scene Start")
                spawned.append(target)
            elif kind == "start_conversation":
                if when != "actor_clicked" or target not in convs or convs[target].speaker != actor:
                    raise ValueError("Start Conversation requiere clic sobre su actor/speaker")
            elif target not in flags:
                raise ValueError("Acción refiere a un flag no declarado")
            actions.append(Action(kind, target))
        if not actions or (when == "actor_clicked" and sum(a.kind == "start_conversation" for a in actions) != 1):
            raise ValueError("Evento sin acciones o clic sin una única conversación")
        events.append(Event(eid, when, tuple(actions), tuple(conditions), actor, conv, result, trigger))
    return tuple(events), tuple(spawned)

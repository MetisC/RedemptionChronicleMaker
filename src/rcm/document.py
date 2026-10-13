"""Editable YAML source, atomic workspace-only saves and basic recovery."""
from pathlib import Path
import copy
import os
import tempfile
import math
import yaml

from .model import identifier
from .service import source_text


class Document:
    def __init__(self, workspace, data, path=None):
        self.ws = workspace
        self.data = data
        self.path = workspace.output(path) if path else None
        self._saved = source_text(data) if path else None
        from .project_safety import disk_hash
        self._disk_hash = disk_hash(self.path)
        self._disk_path = self.path

    @property
    def modified(self):
        return source_text(self.data) != self._saved

    @classmethod
    def new(cls, ws, pid, name, directory, description=""):
        identifier(pid, "ID de crónica", 18)
        path = ws.output(Path(directory) / "project.yaml")
        if path.exists():
            raise ValueError("Ya existe project.yaml en ese directorio. Ábrelo o elige otro.")
        data = {"schema": 1, "chronicle": {"id": pid, "name": name, "description": description},
                "level": {"source": ""}, "state": {"flags": {}}, "actors": [], "conversations": [], "events": []}
        doc = cls(ws, data)
        doc.path = path
        doc._expects_new_file=True
        return doc

    @classmethod
    def load(cls, ws, path):
        path = ws.output(path)
        source = path.read_text(encoding="utf-8-sig")
        try:
            from .input_limits import parse_source
            data = parse_source(source)
        except yaml.YAMLError as error:
            raise ValueError("No se puede abrir: el archivo YAML tiene sintaxis inválida.") from error
        if isinstance(data, dict) and data.get('schema') == 2:
            from .campaign_document import CampaignDocument
            return CampaignDocument.load_data(ws, data, path)
        if not isinstance(data, dict) or not all(k in data for k in ["chronicle", "level", "actors", "conversations", "events"]):
            raise ValueError("El archivo no tiene la estructura de un proyecto RCM.")
        draft_shape(data)
        # Opening a semantically invalid draft is supported; the backend reports its errors.
        doc = cls(ws, data, path)
        return doc

    def _atomic_write(self, path, content):
        path = self.ws.output(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf8", newline="\n") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp, path)
        finally:
            if Path(tmp).exists():
                Path(tmp).unlink()

    def save(self, path=None, force=False):
        target = self.ws.output(path or self.path) if (path or self.path) else None
        if target is None:
            raise ValueError("Elige un archivo de proyecto antes de guardar.")
        content = source_text(self.data)
        from .project_safety import before_save,disk_hash
        before_save(self,target,content,force)
        if target.is_file():
            self._atomic_write(target.with_name(target.name + '.backup'), target.read_text(encoding='utf8'))
        self._atomic_write(target, content)
        old_recovery = self.recovery_path
        self.path, self._saved = target, content
        self._expects_new_file=False
        self._disk_hash = disk_hash(target)
        self._disk_path = target
        for recovery in [old_recovery, self.recovery_path]:
            if recovery and recovery.exists():
                self.ws.output(recovery).unlink()
        return target

    @property
    def recovery_path(self):
        return self.path.with_name(self.path.name + ".autosave") if self.path else None

    def autosave(self):
        if self.modified and self.recovery_path:
            self._atomic_write(self.recovery_path, source_text(self.data))

    def recover(self):
        if not self.recovery_path or not self.recovery_path.exists():
            return False
        recovered = Document.load(self.ws, self.recovery_path)
        self.data = recovered.data
        return True

    def unique_id(self, collection, stem):
        existing = {v.get("id") for v in self.data.get(collection, [])}
        index = 1
        while stem + str(index) in existing:
            index += 1
        return stem + str(index)

    def rename(self, collection, index, new):
        identifier(new, "ID")
        old = self.data[collection][index]["id"]
        if any(i != index and v.get("id") == new for i, v in enumerate(self.data[collection])):
            raise ValueError("Ese identificador ya existe.")
        keys = {"actors": {"speaker", "actor", "spawn"}, "objects": {"spawn"},
                "conversations": {"default", "then", "start_conversation", "conversation"},
                "events": set(), "triggers": {"trigger"}}[collection]
        self.data[collection][index]["id"] = new
        self._replace(self.data, keys, old, new)

    def rename_flag(self, old, new):
        identifier(new, "Alias del flag")
        flags = self.data.setdefault("state", {}).setdefault("flags", {})
        if new != old and new in flags:
            raise ValueError("Ese alias ya existe.")
        value = flags.pop(old)
        flags[new] = value
        self._replace(self.data, {"flag", "set_flag", "clear_flag", "when_flag"}, old, new)

    def rename_node(self, ci, ni, new):
        identifier(new, "ID de nodo")
        conversation = self.data["conversations"][ci]
        if any(i != ni and n["id"] == new for i, n in enumerate(conversation["nodes"])):
            raise ValueError("Ese nodo ya existe.")
        old = conversation["nodes"][ni]["id"]
        conversation["nodes"][ni]["id"] = new
        self._replace(conversation, {"entry", "goto"}, old, new)

    @staticmethod
    def _replace(value, keys, old, new):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in keys and isinstance(item, str) and item == old:
                    value[key] = new
                elif isinstance(item, (list, dict)):
                    Document._replace(item, keys, old, new)
        elif isinstance(value, list):
            for item in value:
                Document._replace(item, keys, old, new)

    def snapshot(self):
        return copy.deepcopy(self.data)


def draft_shape(data):
    """Reject corrupt shapes before they reach widgets; preserve invalid references.

    This checks only the editable structure, not engine semantics or catalogue
    availability. Empty IDs/text, missing references, duplicate indices and
    unsupported source keys are still editable and reported by the backend.
    """
    def record(value, label):
        if not isinstance(value, dict):
            raise ValueError(label + ": se esperaba un objeto YAML")
        return value

    def strings(value, keys, label):
        for key in keys:
            if not isinstance(value.get(key), str):
                raise ValueError(label + "." + key + ": se esperaba texto")

    def optional_strings(value, keys, label):
        strings(value, [k for k in keys if k in value], label)

    def rows(value, label):
        if not isinstance(value, list):
            raise ValueError(label + ": se esperaba una lista")
        for item in value:
            record(item, label)
        return value

    def answers(value, label):
        for answer in rows(value, label):
            strings(answer, ["text"], label)
            if "goto" in answer:
                strings(answer, ["goto"], label)
            if "result" in answer and type(answer["result"]) is not int:
                raise ValueError(label + ": RETURN requiere un entero")

    strings(record(data["chronicle"], "chronicle"), ["id", "name"], "chronicle")
    optional_strings(data["chronicle"], ["description"], "chronicle")
    strings(record(data["level"], "level"), ["source"], "level")
    optional_strings(data["level"], ["name", "environment_scene"], "level")
    flags = record(record(data.get("state", {}), "state").get("flags", {}), "state.flags")
    if any(type(v) is not int for v in flags.values()):
        raise ValueError("state.flags: los índices deben ser enteros")
    for key in ["actors", "objects"]:
        for actor in rows(data.get(key, []), key):
            strings(actor, ["id", "name", "template"], key)
            optional_strings(actor, ["comment", "level"], key)
            trans = record(actor.get("transform"), key + ".transform")
            optional_strings(trans, ["placement"], "transform")
            for name in ["orientation"] + (["position"] if "position" in trans else []):
                vector = trans.get(name)
                if not isinstance(vector, list) or len(vector) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector):
                    raise ValueError(key + ".transform." + name + ": requiere tres números")
            if "conversation" in actor:
                binding = record(actor["conversation"], key + ".conversation")
                optional_strings(binding, ["default", "when_flag", "then"], "conversation binding")
    for trigger in rows(data.get('triggers', []), 'triggers'):
        strings(trigger, ['id', 'name', 'shape'], 'trigger')
        trans = record(trigger.get('transform'), 'trigger.transform')
        for key in ('position', 'orientation'):
            val = trans.get(key)
            if not isinstance(val, list) or len(val) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) for v in val):
                raise ValueError('trigger.transform.' + key + ': requiere tres números')
        if trigger['shape'] == 'box':
            val = trigger.get('size')
            if not isinstance(val, list) or len(val) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in val):
                raise ValueError('trigger.size: requiere tres números positivos')
        elif trigger['shape'] == 'sphere' and (type(trigger.get('radius')) not in (int, float) or not math.isfinite(trigger['radius']) or trigger['radius'] <= 0):
            raise ValueError('trigger.radius: requiere número positivo')
    for conv in rows(data["conversations"], "conversations"):
        strings(conv, ["id", "speaker"], "conversation")
        optional_strings(conv, ["entry"], "conversation")
        if "nodes" in conv:
            for node in rows(conv["nodes"], "nodes"):
                strings(node, ["id"], "node")
                for line in rows(node.get("lines"), "lines"):
                    strings(line, ["text"], "line")
                    optional_strings(line, ["speaker"], "line")
                answers(node.get("choices"), "choices")
        else:
            strings(conv, ["prompt"], "conversation")
            answers(conv.get("choices"), "choices")
            if any("result" not in a for a in conv["choices"]):
                raise ValueError("Las respuestas de una conversación simple requieren result")
    for event in rows(data["events"], "events"):
        strings(event, ["when"], "event")
        optional_strings(event, ["id", "actor", "conversation", "trigger"], "event")
        if "result" in event and type(event["result"]) is not int:
            raise ValueError("event.result: requiere un entero")
        rows(event.get("actions"), "actions")
        for condition in rows(event.get("conditions", []), "conditions"):
            strings(condition, ["flag"], "condition")
            if type(condition.get("is_set")) is not bool:
                raise ValueError("condition.is_set: requiere true o false")

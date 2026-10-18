"""Read-only game discovery, evidence extraction and resource catalogues."""
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

from .formats import NotFile, cstring, u32, scene_entity_hints, Scene
from .paths import Workspace

RESEARCH_EXTENSIONS = {".class", ".nco", ".nsd", ".nai", ".nqd", ".npc", ".nbs", ".not", ".nls", ".nvo", ".ntx", ".ncd", ".ned", ".ndd", ".ndg", ".npd", ".ntt", ".txt", ".bat", ".dsp"}
KINDS = {0: "actors", 1: "items", 2: "props", 3: "regions", 4: "projectiles", 5: "weapons", 6: "armour", 7: "players", 8: "containers", 9: "none"}


def digest(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def identity_from_records(records, loose=()):
    """Content identity, independent of the installation's absolute path."""
    files = [{'file':r['file'].casefold(), 'size':r['size'], 'sha256':r['sha256']}
             for r in records if r['file'].lower().endswith('.nob') or r['file'].lower() in {'vampire.exe','classes.zip'} or r['file'].lower().startswith('chronicles/')]
    files += [{'file':r['path'].casefold(),'size':r['size'],'sha256':None} for r in loose if r.get('archive') is None and r.get('extension') in {'.wav','.mp3'}]
    files.sort(key=lambda r:r['file'])
    encoded=json.dumps(files,sort_keys=True,separators=(',',':')).encode('utf8')
    return {'format':1,'sha256':hashlib.sha256(encoded).hexdigest(),'files':files}


def installation_identity(game):
    game=Path(game)
    paths=[*game.glob('*.nob'),game/'Vampire.exe',game/'classes.zip']
    if (game/'Chronicles').is_dir():paths.extend(p for p in (game/'Chronicles').iterdir() if p.is_file())
    records=[{'file':p.relative_to(game).as_posix(),'size':p.stat().st_size,'sha256':digest(p)} for p in paths]
    loose=[{'path':p.relative_to(game).as_posix(),'size':p.stat().st_size,'extension':p.suffix.lower(),'archive':None}
           for p in (game/'Sounds').rglob('*') if p.is_file() and p.suffix.lower() in {'.wav','.mp3'}]
    return identity_from_records(records,loose)


def rows(text):
    for number, line in enumerate(text.splitlines(), 1):
        line = line.split("#", 1)[0].split("//", 1)[0].strip()
        if line:
            yield number, line.split()


def parse_chronicle(data: bytes):
    locations, exits, settings = [], [], {}
    for line, tokens in rows(data.decode("cp1252")):
        key = tokens[0].lower()
        if key == "location":
            if len(tokens) != 7:
                raise ValueError(f"location NSC inesperada en línea {line}")
            locations.append(dict(zip(["id", "nil", "scene", "map_ui", "map_label", "flags"], tokens[1:])) | {"line": line})
        elif key == "exit":
            exits.append({"from": tokens[1], "to": tokens[2], "flags": tokens[3] if len(tokens) > 3 else "0x0", "line": line})
        else:
            settings[key] = tokens[1:]
    return {"locations": locations, "exits": exits, "settings": settings}


def discover(ws: Workspace, game: Path, disassemble: bool = True, progress=lambda _:None, refresh_installation=False):
    game = game.resolve()
    if not (game / "Codex.nob").is_file():
        raise ValueError("No se encuentra Codex.nob en la instalación")
    # A rescan must not silently redefine the original safety baseline.
    baseline_path = ws.output("research/source_manifest.json")
    if baseline_path.is_file() and not refresh_installation:
        baseline = json.loads(baseline_path.read_text(encoding="utf8"))
        changed = [r["file"] for r in baseline if not (game / r["file"]).is_file() or digest(game / r["file"]) != r["sha256"]]
        if changed:
            raise ValueError(f"Las fuentes difieren del baseline original; scan cancelado: {changed}")
    entries, manifests, counts, raw_templates = [], [], {}, []
    scene_data = {}
    from .wtd import IGNORED_ROOT_ARCHIVES
    ignored=[]
    for archive in sorted(game.glob("*.nob")):
        if archive.name.casefold() in IGNORED_ROOT_ARCHIVES:
            ignored.append({'file':archive.name,'size':archive.stat().st_size,'sha256':digest(archive)});continue
        progress('Leyendo recursos: '+archive.name)
        manifests.append({"file": archive.name, "size": archive.stat().st_size, "sha256": digest(archive)})
        with zipfile.ZipFile(archive) as z:
            counts[archive.name] = dict(collections.Counter(PurePosixPath(i.filename).suffix.lower() for i in z.infolist()))
            for i in z.infolist():
                posix = PurePosixPath(i.filename.replace("\\", "/"))
                if posix.is_absolute() or ".." in posix.parts or ":" in i.filename:
                    raise ValueError("Ruta insegura en archivo NOB")
                ext = posix.suffix.lower()
                item = {"id": posix.stem, "archive": archive.name, "path": str(posix), "extension": ext, "size": i.file_size, "crc32": f"{i.CRC:08x}"}
                entries.append(item)
                if ext in RESEARCH_EXTENSIONS:
                    data = z.read(i)
                    item["sha256"] = hashlib.sha256(data).hexdigest()
                    ws.write(Path("research/original") / archive.name / str(posix), data)
                    if ext == ".not":
                        nf = NotFile.read(data)
                        for t in nf.templates:
                            raw_templates.append((t, item))
                    elif ext == ".nsd":
                        scene_data[posix.name.casefold()] = (data, item)
    progress('Indexando escenarios y escenas…')
    chronicle_files = sorted((game / "Chronicles").iterdir())
    chronicles, levels = {}, {}
    for p in chronicle_files:
        if not p.is_file():
            continue
        data = p.read_bytes()
        manifests.append({"file": "Chronicles/" + p.name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        ws.write(Path("research/original/Chronicles") / p.name, data)
        if p.suffix.lower() != ".nsc":
            continue
        chron = parse_chronicle(data)
        chronicles[p.stem] = chron
        for loc in chron["locations"]:
            candidates = [e for e in entries if e["extension"] == ".nil" and PurePosixPath(e["path"]).name.casefold() == loc["nil"].casefold()]
            level = levels.setdefault(loc["id"], {"nil": loc["nil"], "geometry": candidates, "scenes": [], "references": []})
            if level["nil"].casefold() != loc["nil"].casefold():
                level.setdefault("alternative_geometry", []).append(loc["nil"])
            level["references"].append({"chronicle": p.name, **loc})
            if loc["scene"].lower() != "null" and loc["scene"] not in level["scenes"]:
                level["scenes"].append(loc["scene"])
    associate_static_scenes(levels, scene_data)
    by_name = collections.defaultdict(list)
    for t, origin in raw_templates:
        by_name[t.name.casefold()].append((t, origin))

    def resolve(t, trail=()):
        values = t.values()
        parent = cstring(values[0]) if 0 in values else None
        if parent:
            if parent.casefold() in trail:
                raise ValueError(f"Herencia NOT circular: {t.name}")
            options = by_name.get(parent.casefold(), [])
            if len(options) == 1:
                values = resolve(options[0][0], trail + (parent.casefold(),)) | values
        return values

    progress('Preparando el catálogo de personajes y objetos…')
    templates = []
    for t, origin in raw_templates:
        v = resolve(t)
        templates.append({"id": t.name, "archive": origin["archive"], "path": origin["path"],
                          "parent": cstring(t.values()[0]) if 0 in t.values() else None,
                          "kind": KINDS.get(u32(v[16]), "unknown") if 16 in v else "unknown",
                          "model": cstring(v[4]) if 4 in v else None,
                          "ai": cstring(v[56]) if 56 in v else None,
                          "script": cstring(v[11]) if 11 in v else None,
                          "cast_id": cstring(v[81]) if 81 in v else None,
                          "actor_flags": u32(v[114]) if 114 in v else 0,
                          "tag_ids": [x.id for x in t.tags],
                          "inheritance_complete": 0 not in t.values() or len(by_name.get(cstring(t.values()[0]).casefold(), [])) == 1})
    resources = {"entries": entries, "templates": templates, "groups": {}}
    mapping = {"models": {".nod"}, "animations": {".nad", ".nag", ".nms"}, "conversations": {".nco"}, "sounds": {".wav"}, "music": {".mp3"}, "ai": {".nai"}, "quests": {".nqd"}, "scenes": {".nsd"}, "player_definitions": {".npc"}, "stores": {".nbs"}, "camera_paths": {".ncp"}}
    for group, extensions in mapping.items():
        resources["groups"][group] = [e for e in entries if e["extension"] in extensions]
    resources["groups"]["voice"] = [e for e in entries if e["extension"] in {".wav", ".mp3"} and "voice" in PurePosixPath(e["path"]).parts]
    resources["groups"]["ambient"] = []
    # Music is loose under Sounds in this installation.
    for p in sorted((game / "Sounds").rglob("*")):
        if p.is_file() and p.suffix.lower() in {".mp3", ".wav"}:
            item = {"id": p.stem, "archive": None, "path": p.relative_to(game).as_posix(), "extension": p.suffix.lower(), "size": p.stat().st_size}
            entries.append(item)
            resources["groups"]["sounds"].append(item)
            parts = [s.lower() for s in p.relative_to(game).parts]
            if "music" in parts:
                resources["groups"]["music"].append(item)
            elif "dialog" in parts:
                resources["groups"]["voice"].append(item)
            elif "stereoambient" in parts:
                resources["groups"]["ambient"].append(item)
    for kind in KINDS.values():
        resources["groups"][kind + "_templates"] = [t for t in templates if t["kind"] == kind]
    scene_hints, simple = {}, []
    for name, (data, item) in scene_data.items():
        scene_hints[name] = {"source": item, "entities": scene_entity_hints(data)}
        try:
            parsed = Scene.read(data)
            assert parsed.encode() == data
            simple.append(item["path"])
        except ValueError:
            pass
    for f in [game / "classes.zip", game / "Vampire.exe", game / "manual.pdf", game / "Readme.rtf", game / "ReadmePatch.rtf"]:
        if not f.is_file():continue
        manifests.append({"file": f.name, "size": f.stat().st_size, "sha256": digest(f)})
    ws.write("cache/toolchain/classes.zip", (game / "classes.zip").read_bytes())
    summary = {"archive_counts": counts, "levels": len(levels), "nil_files": sum(e["extension"] == ".nil" for e in entries), "templates": len(templates), "template_kind_counts": dict(collections.Counter(t["kind"] for t in templates)), "nsd_supported_roundtrips": simple, "sdk_present": False}
    geometries = {}
    for e in entries:
        if e["extension"] == ".nil":
            geometries[e["path"]] = {"resource": e, "location_ids": [name for name, l in levels.items() if PurePosixPath(e["path"]).name.casefold() == l["nil"].casefold()]}
    for path, data in [("cache/levels.json", levels), ("cache/geometry.json", geometries), ("cache/resources.json", resources), ("cache/chronicles.json", chronicles), ("cache/scene_hints.json", scene_hints), ("research/source_manifest.json", manifests), ("research/discovery_summary.json", summary)]:
        ws.write(path, json.dumps(data, ensure_ascii=False, indent=2))
    from .scene_profiles import catalogue
    ws.write('cache/scene_profiles.json', json.dumps(catalogue(ws, levels, scene_hints), ensure_ascii=False, indent=2))
    if disassemble:
        classes = ws.output("research/original/Codex.nob")
        names = sorted(p.stem for p in classes.glob("*.class"))
        command = ["javap", "-classpath", str(classes), "-c", "-p", "-constants", *names]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        ws.write("research/ALL_CODEX.bytecode.txt", result.stdout)
        api = subprocess.run(["javap", "-classpath", str(classes), "-constants", *[n for n in names if n.startswith("Codex")]], capture_output=True, text=True, check=True)
        ws.write("research/API_SIGNATURES.txt", api.stdout)
    from .motions import ensure_catalogue
    progress('Indexando animaciones disponibles…')
    ws.output('cache/motions.json').unlink(missing_ok=True)
    ensure_catalogue(ws,resources,game)
    ws.write('cache/installation_identity.json',json.dumps(identity_from_records(manifests+ignored,entries),indent=2))
    return summary


def associate_static_scenes(levels, scenes):
    """SDK NIL/Embrace docs: matching-stem NSD loads automatically with the NIL.

    NSS describes ST menu entries, not NSD filenames or location ordinals.
    Keep NSC initial scenes first so historical automatic environments survive.
    """
    for level in levels.values():
        initial = list(dict.fromkeys(r['scene'] for r in level['references'] if r['scene'].casefold() != 'null'))
        level['scenes'] = initial
        level['scene_evidence'] = {name: 'NSC initial scene' for name in initial}
        key = (PurePosixPath(level['nil']).stem + '.nsd').casefold()
        if key in scenes:
            entry = scenes[key]
            # Accept both discovery's (bytes, resource) and cached hint records.
            source = entry[1] if isinstance(entry, tuple) else entry['source']
            name = PurePosixPath(source['path']).name
            level['static_scene'] = name
            if name.casefold() not in {s.casefold() for s in initial}:
                level['scenes'].append(name)
            level['scene_evidence'][name] = 'SDK matching-stem static NSD'


def verify_sources(ws: Workspace, game: Path):
    manifest = json.loads(ws.output("research/source_manifest.json").read_text(encoding="utf8"))
    mismatches = [row["file"] for row in manifest if digest(game / row["file"]) != row["sha256"]]
    report = {"checked_files": len(manifest), "hashes_match": not mismatches, "mismatches": mismatches, "scope": "six NOB archives, Chronicles, JVM library, executable, bundled manuals/readmes"}
    ws.write("research/read_only_verification.json", json.dumps(report, indent=2))
    if mismatches:
        raise ValueError(f"Las fuentes originales han cambiado: {mismatches}")
    return report

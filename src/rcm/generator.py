import hashlib
import io
import json
from pathlib import Path
import subprocess
import wave
import zipfile
from dataclasses import asdict

from .formats import NotFile, Template, Tag, Scene, fixed
from .model import Project
from .paths import Workspace
from .catalogue import parse_chronicle, rows

ECJ_SHA256 = "ac0ba5876eaf7ebb47749a0d1be179c51f194b9dd0b875d1c09e1b530f5a2db5"


def java_string(value):
    return json.dumps(value, ensure_ascii=True)


def java_vector(values):
    return "new float[]{" + ", ".join(f"{v:.9g}f" if "." in f"{v:.9g}" or "e" in f"{v:.9g}" else f"{v:.9g}.0f" for v in values) + "}"


def runtime_java(p: Project):
    prefix, cname = p.prefix, p.prefix + "_Scene"
    entities = {e.id: (i, e) for i, e in enumerate(p.entities)}
    convs = {c.id: i for i, c in enumerate(p.conversations)}
    clicked_events = [e for e in p.events if e.when == "actor_clicked"]
    end_events = [e for e in p.events if e.when == "conversation_ended"]
    scene_events = [e for e in p.events if e.when == "scene_start"]
    spatial_events = [e for e in p.events if e.when == 'trigger_enter']
    spatial_spawns = {a.target for e in spatial_events for a in e.actions if a.kind == 'spawn'}
    gated_spawns = {a.target: i for i, e in enumerate(scene_events) for a in e.actions if a.kind == "spawn" and e.conditions}
    interactive = {e.actor for e in clicked_events}
    def condition(event):
        return " && ".join(("" if c.is_set else "!") + f"CodexSequence.GetChronicleFlag({p.flags[c.flag]})" for c in event.conditions) or "true"
    def flag_actions(event, indent):
        return [indent + f"CodexSequence.{'SetChronicleFlag' if a.kind == 'set_flag' else 'ClearChronicleFlag'}({p.flags[a.target]});"
                for a in event.actions if a.kind in {"set_flag", "clear_flag"}]
    code = [f"public class {cname} extends Codex {{",
            f"    private int[] things = new int[{len(p.entities)}];",
            "    private int active = -1;", "    private int starter = 0;",
            "    private boolean restoredState = false;",
            "    private int spawnRetries = 0;",
            f"    private void trace(String message) {{",
            "        try {",
            f"            java.io.FileOutputStream file = new java.io.FileOutputStream({java_string('RCM/' + p.id + '/runtime_trace.log')}, true);",
            "            java.io.PrintStream out = new java.io.PrintStream(file);",
            "            out.println(System.currentTimeMillis() + \" \" + message);",
            "            out.close();",
            "        } catch (java.io.IOException error) { CodexConsole.PrintError(\"RCM trace: \" + error); }", "    }",
            f"    public {cname}() {{ trace(\"RCM revision 3: scene controller constructed\"); }}",
            "    private boolean isLocal(int guid) {",
            "        boolean valid = IsActorGuid(guid) || IsPlayerGuid(guid) || IsPropGuid(guid) || IsItemGuid(guid) || IsWeaponGuid(guid) || IsArmorGuid(guid);",
            "        return valid && new CodexThing(guid).GetLocationNum() == CodexSequence.GetCurrentLocation();", "    }",
            "    private int localPlayer(int candidate) {",
            "        if (IsPlayerGuid(candidate) && isLocal(candidate)) return candidate;",
            "        for (int i = 0; i < CodexPlayer.GetNumMPPlayers(); i++) {",
            "            int guid = CodexPlayer.GetMPPlayer(i);",
            "            if (IsPlayerGuid(guid) && isLocal(guid)) return guid;", "        }",
            "        int current = CodexPlayer.GetCurrentPlayer();",
            "        return IsPlayerGuid(current) && isLocal(current) ? current : 0;", "    }",
            "    private void spawnLayer(int candidate) {",
            "        try { spawnLayerImpl(candidate); }",
            "        catch (Throwable error) {",
            "            trace(\"SPAWN EXCEPTION: \" + error);",
            "            CodexConsole.PrintError(\"RCM spawn: \" + error);",
            "            KillTimer(9001);", "        }", "    }",
            "    private void spawnLayerImpl(int candidate) {",
            "        if (NetIsClient()) return;",
            "        int playerGuid = localPlayer(candidate);",
            "        if (spawnRetries == 0 || spawnRetries == 10 || spawnRetries == 120) trace(\"spawn attempt=\" + spawnRetries + \" player=\" + playerGuid + \" location=\" + CodexSequence.GetCurrentLocation());",
            "        boolean pending = false;"]
    if gated_spawns:
        code.insert(1, f"    private boolean[] sceneEnabled = new boolean[{len(scene_events)}];")
    if p.triggers:
        code[1:1] = [f'    private boolean[] spawnEnabled = new boolean[{len(p.entities)}];',
                     f'    private boolean[] triggerInside = new boolean[{len(p.triggers)}];',
                     f'    private boolean[] triggerFired = new boolean[{len(p.triggers)}];']
    for eid in p.spawns:
        i, e = entities[eid]
        template = prefix + "_" + eid
        gate = (f' && spawnEnabled[{i}]' if p.triggers else '') + (f" && sceneEnabled[{gated_spawns[eid]}]" if eid in gated_spawns else '')
        code += [f"        if (!isLocal(things[{i}])) things[{i}] = CodexThing.GuidFromCastID({java_string(template)});",
                 f"        if (!isLocal(things[{i}])" + gate + ") {"]
        if e.transform.placement == "near_player":
            code += ["            if (playerGuid != 0) {",
                     f"                things[{i}] = new CodexThing(playerGuid).SpawnThingNear({java_string(template)}, 0.0f, 0);",
                     f"                if (spawnRetries == 0 || spawnRetries == 10 || spawnRetries == 120 || things[{i}] != 0) trace({java_string(template + ' SpawnThingNear GUID=')} + things[{i}]);",
                     f"                if (isLocal(things[{i}])) new CodexThing(things[{i}]).SetOrientation({java_vector(e.transform.orientation)});", "            }"]
        else:
            code += [f"            things[{i}] = new CodexWorld(WORLD_CURRENT).CreateThing({java_string(template)}, {java_vector(e.transform.position)}, {java_vector(e.transform.orientation)});"]
        notice = 'RCM: ' + e.name + ' creada. Acercate y habla con ella.' if e.conversation or e.id in interactive else 'RCM: creado ' + e.name + '.'
        code += [f"            if (isLocal(things[{i}])) CodexConsole.Print(0, 0, {java_string(notice)});",
                 "        }",
                 f"        if (!isLocal(things[{i}])" + gate + ") pending = true;",
                 f"        if (isLocal(things[{i}])) {{",
                 f"            CodexThing thing{i} = new CodexThing(things[{i}]);",
                 # Keep restored position: the source transform is applied on creation only.
                 f"            thing{i}.ClearThingFlags(THING_FLAG_SAVENEVER | THING_FLAG_SAVESUSPEND);",
                 f"            thing{i}.SetThingFlags(THING_FLAG_SAVEALWAYS);"]
        if e.kind == "actor":
            code += [f"            CodexActor actor{i} = new CodexActor(things[{i}]);",
                     f"            actor{i}.SetActorFlags(THING_AF_AIPAUSED | THING_AF_NEUTRAL | THING_AF_NOFEED" + (" | THING_AF_TALKTO);" if e.conversation or e.id in interactive else ");"),
                     f"            actor{i}.SetActorTeam(TEAM_PEDESTRIANS);"]
        if e.conversation or e.id in interactive:
            code += [f"            if (!CaptureThing(things[{i}], {i + 1})) CodexConsole.PrintError({java_string('RCM: callback capture failed for ' + eid)});"]
        code += ["        }"]
    code += ["        if (pending && spawnRetries++ < 120) {",
             "            if (!SetTimer(0.5f, 9001)) CodexConsole.PrintError(\"RCM: spawn retry timer failed\");",
             "        } else {", "            KillTimer(9001);",
             "            if (pending) { trace(\"SPAWN FAILED after retries\"); CodexConsole.PrintError(\"RCM: no se pudo crear la capa tras esperar al jugador\"); }", "        }", "    }",
             "    public void beginscene(int playerGuid, int captureID) {",
             "        trace(\"beginscene player=\" + playerGuid + \" capture=\" + captureID + \" client=\" + NetIsClient());",
             "        if (NetIsClient()) return;", "        active = -1;", "        starter = 0;",
             "        spawnRetries = 0;"]
    if p.triggers:
        for i, e in enumerate(p.entities):
            code += [f'        if (!restoredState) spawnEnabled[{i}] = {"false" if e.id in spatial_spawns else "true"};']
        code += ['        SetTimer(0.15f, 9002);']
    for j, event in enumerate(scene_events):
        if event.conditions or any(a.kind in {"set_flag", "clear_flag"} for a in event.actions):
            gate = f"sceneEnabled[{j}]" if gated_spawns else condition(event)
            if gated_spawns:
                code += [f"        sceneEnabled[{j}] = {condition(event)};"]
            code += [f"        if ({gate}) {{", *flag_actions(event, "            "), "        }"]
    code += ["        spawnLayer(playerGuid);", "        restoredState = false;", "    }",
             "    public void timer(int id, float a, float b, float c, float d) {",
             "        if (id == 9001) spawnLayer(0);", "    }",
             "    public void clicked(int targetGuid, int clickerGuid, int captureID) {",
             "        if (NetIsClient() || active != -1 || !IsPlayerGuid(clickerGuid)) return;",
             "        int selected = -1;"]
    if p.triggers:
        timer_end = code.index('        if (id == 9001) spawnLayer(0);')
        code.insert(timer_end + 1, '        if (id == 9002 && !NetIsClient()) { checkTriggers(); SetTimer(0.15f, 9002); }')
    for i, e in enumerate(p.entities):
        if not e.conversation:
            continue
        code += [f"        if (targetGuid == things[{i}]) {{"]
        if e.when_flag:
            code += [f"            selected = CodexSequence.GetChronicleFlag({p.flags[e.when_flag]}) ? {convs[e.after_conversation]} : {convs[e.conversation]};"]
        else:
            code += [f"            selected = {convs[e.conversation]};"]
        code += ["        }"]
    for event in clicked_events:
        index = entities[event.actor][0]
        cid = next(a.target for a in event.actions if a.kind == "start_conversation")
        code += [f"        if (selected == -1 && targetGuid == things[{index}] && ({condition(event)})) {{",
                 *flag_actions(event, "            "), f"            selected = {convs[cid]};", "        }"]
    code += ["        if (selected == -1) return;", "        starter = clickerGuid;", "        active = selected;", "        boolean started = false;", "        switch (selected) {"]
    for i, c in enumerate(p.conversations):
        cid = prefix + "_" + c.id
        code += [f"        case {i}: started = ExecuteConversation(clickerGuid, 0, {java_string(cid)}, {java_string(cid + '.nco')}, CONV_XFLAG_WANTFEEDBACK | CONV_XFLAG_ALLOWABORT); break;"]
    code += ["        }", "        if (!started) {", "            active = -1;", "            starter = 0;",
             "            CodexConsole.PrintError(\"RCM: conversation failed to start\");", "        }", "    }",
             "    public void convreached(int playerGuid, int event, int line, int speakerGuid, int captureID) {",
             "        if (active == -1 || playerGuid != starter) return;",
             "        int speaker = 0;", "        switch (active) {"]
    for i, c in enumerate(p.conversations):
        if c.nodes:
            code += [f"        case {i}: speaker = isLocal(speakerGuid) ? speakerGuid : things[{entities[c.speaker][0]}]; break;"]
        else:
            code += [f"        case {i}: speaker = things[{entities[c.speaker][0]}]; break;"]
    code += ["        }", "        if (speaker != 0) CodexCamera.SetupCutscene(playerGuid, speaker, 0);", "    }",
             "    public void convended(int playerGuid, boolean aborted, int result) {",
             "        if (active == -1 || playerGuid != starter) return;",
             "        int completed = active;", "        active = -1;", "        starter = 0;",
             "        CodexCamera.Release(playerGuid);", "        if (aborted || NetIsClient()) return;",
             "        switch (completed) {"]
    for i, c in enumerate(p.conversations):
        code += [f"        case {i}:", "            switch (result) {"]
        for ch in c.choices:
            if ch.flag:
                method = "SetChronicleFlag" if ch.value else "ClearChronicleFlag"
                code += [f"            case {ch.result}: CodexSequence.{method}({p.flags[ch.flag]}); break;"]
        code += ["            }", "            break;"]
    code += ["        }"]
    for event in end_events:
        test = f"completed == {convs[event.conversation]}" + (f" && result == {event.result}" if event.result is not None else "") + f" && ({condition(event)})"
        known = " || ".join(f"result == {ch.result}" for ch in p.conversations[convs[event.conversation]].choices)
        code += [f"        if ({test} && ({known})) {{", *flag_actions(event, "            "), "        }"]
    code += ["    }", "    public void save(int captureID) {"]
    for i in range(len(p.entities)):
        code += [f"        CodexSequence.SaveInt(things[{i}]);"]
    if p.triggers:
        for i in range(len(p.entities)):
            code += [f'        CodexSequence.SaveInt(spawnEnabled[{i}] ? 1 : 0);']
        for i in range(len(p.triggers)):
            code += [f'        CodexSequence.SaveInt(triggerFired[{i}] ? 1 : 0);']
    code += ["    }", "    public void restore(int captureID) {"]
    for i in range(len(p.entities)):
        code += [f"        things[{i}] = CodexSequence.RestoreInt();"]
    if p.triggers:
        for i in range(len(p.entities)):
            code += [f'        spawnEnabled[{i}] = CodexSequence.RestoreInt() != 0;']
        for i in range(len(p.triggers)):
            code += [f'        triggerFired[{i}] = CodexSequence.RestoreInt() != 0;', f'        triggerInside[{i}] = false;']
    code += ["        active = -1;", "        starter = 0;", "        restoredState = true;", "    }",
             "    public void restored(int captureID) {",
             "        if (restoredState) beginscene(0, captureID);", "    }", "}"]
    if p.triggers:
        extra = ['    private boolean playerInVolume(int index) {',
                 '        for (int i = -1; i < CodexPlayer.GetNumMPPlayers(); i++) {',
                 '            int guid = i == -1 ? CodexPlayer.GetCurrentPlayer() : CodexPlayer.GetMPPlayer(i);',
                 '            if (!IsPlayerGuid(guid) || !isLocal(guid)) continue;',
                 '            float[] pos = new CodexThing(guid).GetPosition();',
                 '            if (pos == null || pos.length < 3) continue;']
        for i, t in enumerate(p.triggers):
            x, y, z = t.transform.position
            extra += [f'            if (index == {i}) {{', f'                double dx = pos[0] - {x}, dy = pos[1] - {y}, dz = pos[2] - {z};']
            if t.shape == 'sphere':
                extra += [f'                if (dx*dx + dy*dy + dz*dz <= {t.radius*t.radius}) return true;']
            else:
                angle = t.transform.orientation[2] * 3.141592653589793 / 180
                import math
                c, s = math.cos(angle), math.sin(angle)
                extra += [f'                double lx = dx*{c} + dy*{s}, ly = -dx*{s} + dy*{c};',
                          f'                if (Math.abs(lx) <= {t.size[0]/2} && Math.abs(ly) <= {t.size[1]/2} && Math.abs(dz) <= {t.size[2]/2}) return true;']
            extra += ['            }']
        extra += ['        }', '        return false;', '    }', '    private void checkTriggers() {', '        if (active != -1) return;', '        boolean needsSpawn = false;']
        for i, t in enumerate(p.triggers):
            extra += [f'        boolean inside{i} = playerInVolume({i});',
                      f'        if (inside{i} && !triggerInside[{i}]' + (f' && !triggerFired[{i}]' if t.once else '') + ') {']
            for event in spatial_events:
                if event.trigger != t.id:
                    continue
                extra += [f'            if ({condition(event)}) {{', *flag_actions(event, '                '), f'                triggerFired[{i}] = true;']
                for a in event.actions:
                    if a.kind == 'spawn':
                        extra += [f'                spawnEnabled[{entities[a.target][0]}] = true;', '                needsSpawn = true;']
                extra += [f'                trace({java_string("trigger_enter: " + t.id)});', '            }']
            extra += ['        }', f'        triggerInside[{i}] = inside{i};']
        extra += ['        if (needsSpawn) { spawnRetries = 0; spawnLayer(0); }', '    }']
        code[-1:-1] = extra
    return cname, "\n".join(code) + "\n"


def zip_bytes(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as z:
        for path, data in sorted(files.items()):
            info = zipfile.ZipInfo(path, (2000, 1, 1, 0, 0, 0))
            info.create_system = 0
            info.external_attr = 0
            z.writestr(info, data)
    return out.getvalue()


def build(ws: Workspace, p: Project, levels, resources, hints, compile_java=True, progress=None, runtime_factory=None):
    progress = progress or (lambda message: None)
    progress("Generando la escena y sus actores…")
    prefix = p.prefix
    root = Path("build") / p.id
    runtime = root / "runtime"
    old_report_path = ws.output(root / "build_report.json")
    old_report = json.loads(old_report_path.read_text(encoding="utf8")) if old_report_path.is_file() else {}
    ws.write(root / "build_report.json", json.dumps({"status": "building", "native_engine_test": False}, indent=2))
    # Final packages from a previous build cannot represent an incomplete rebuild.
    for filename in [p.id + ".nob", p.id + "_distribution.zip"]:
        previous = ws.output(root / filename)
        if previous.is_file():
            previous.unlink()
    level = levels[p.level]
    # Derive the invisible controller anchor and original environment from evidence.
    origin = next((hints[s.casefold()] for s in level["scenes"] if s.casefold() in hints and hints[s.casefold()]["entities"]), None)
    if origin is None:
        raise ValueError("El level no ofrece un anchor NSD estudiado; no se inventa su sector")
    anchor = next((e for e in origin["entities"] if e["template"] == "ghost"), origin["entities"][0])
    source = origin["source"]
    from .scene_profiles import environment as scene_environment
    environment, environment_record = scene_environment(ws, level, hints, p.environment_scene)
    if p.sky:
        environment = environment[:-64] + fixed(p.sky[0]) + fixed(p.sky[1])
    controller, java = (runtime_factory or runtime_java)(p)
    scene = Scene(prefix + "S", prefix + "L", [[Tag.text(0, "ghost"), Tag.vector(1, anchor["orientation"]), Tag.vector(2, anchor["position"]), Tag.integer(3, anchor["sector"]), Tag.text(11, controller)]], environment).encode()
    assert Scene.read(scene).encode() == scene
    templates = []
    custom_scripts={t['id']:t.get('custom_script') for t in resources['templates'] if t.get('custom_script')}
    for e in p.entities:
        template_name = prefix + "_" + e.id
        templates.append(Template(template_name, [Tag.text(0, e.template), Tag.text(11, custom_scripts.get(e.template) or prefix + "_Passive"), Tag.text(81, template_name), Tag.text(82, template_name)], b"RCM generated layer\0"))
    not_file = NotFile(templates).encode()
    assert NotFile.read(not_file).encode() == not_file
    ref = level["references"][0]
    original_chronicle = parse_chronicle(ws.output(Path("research/original/Chronicles") / ref["chronicle"]).read_bytes())
    meta_name = original_chronicle["settings"].get("metafile", [])
    metadata_lines = []
    if meta_name:
        meta_path = next((f for f in ws.output("research/original/Chronicles").iterdir() if f.name.casefold() == meta_name[0].casefold()), None)
        if meta_path:
            metadata_lines = [tokens for _, tokens in rows(meta_path.read_text(encoding="cp1252"))]
    # Keep the original map strings and currency references, without importing
    # original conversations, quests, scene sequence, player or chronicle script.
    retained_meta = [" ".join(tokens) for tokens in metadata_lines if tokens[0].lower() in {"nls", "cash"}]
    payload = {
        # CLEARBUFFER is part of the original location's rendering contract.
        f"chronicles/{p.id}.nsc": f"# Generated by Redemption Chronicle Maker\r\nlocation {p.level} {level['nil']} {prefix}.nsd {ref['map_ui']} {ref['map_label']} {hex(0x0020 | (int(ref['flags'], 0) & 0x0040))}\r\nmetafile {prefix}.nmf\r\nreviveloc {p.level} 0\r\nflags 0x3\r\n".encode("cp1252"),
        # Non-underscore NOT libraries require an explicit load. Native NMF
        # parser handles NOT via the same library loader as the NSD import list.
        f"chronicles/{prefix}.nmf": ("\r\n".join([*retained_meta, f"NOT {prefix}.not", f"NLS _{prefix}.nls", f"NVO {prefix}.nvo"]) + "\r\n").encode("cp1252"),
        f"scenes/{prefix}.nsd": scene,
        f"misc/templates/{prefix}.not": not_file,
    }
    title = p.level_name or p.name
    nls = [f"{p.id} {p.name}", f"{prefix}S {title}", f"{prefix}L {title}"] + [f"{prefix}_{e.id} {e.name}" for e in p.entities]
    # Native startup loads underscore-prefixed NLS after registering -user.
    # Menu labels must be available before the selected chronicle's NMF loads.
    nvo = []
    progress("Generando conversaciones…")
    for c in p.conversations:
        cid = prefix + "_" + c.id
        if c.nodes:
            commands = [f"CONVERSATION: {cid} 0"]
            order = [n for n in c.nodes if n.id == c.entry] + [n for n in c.nodes if n.id != c.entry]
            indices = {n.id: i for i, n in enumerate(c.nodes)}
            for node in order:
                stem = f"{cid}_n{indices[node.id]}"
                commands.append(f"EVENT: ev_{node.id}")
                for i, line in enumerate(node.lines):
                    key = f"{stem}_l{i}"
                    commands.append(f"LINE: {key} {prefix}_{line.speaker}")
                    nvo.append(f"{key} {prefix}_silence {line.text}")
                for i, ch in enumerate(node.choices):
                    key = f"{stem}_a{i}"
                    commands.append(f"ANSWERGOTO: {key} ev_{ch.target}" if ch.target else f"ANSWERRETURN: {key} {ch.result}")
                    nvo.append(f"{key} {prefix}_silence {ch.text}")
        else:
            prompt = cid + "_line"
            commands = [f"CONVERSATION: {cid} 0", "EVENT: ev_0", f"LINE: {prompt} {prefix}_{c.speaker}"]
            nvo.append(f"{prompt} {prefix}_silence {c.prompt}")
            for i, ch in enumerate(c.choices):
                key = cid + "_a" + str(i)
                commands.append(f"ANSWERRETURN: {key} {ch.result}")
                nvo.append(f"{key} {prefix}_silence {ch.text}")
        payload[f"conversations/{cid}.nco"] = ("\r\n".join(commands) + "\r\n").encode("cp1252")
    payload[f"strings/_{prefix}.nls"] = ("\r\n".join(nls) + "\r\n").encode("cp1252")
    payload[f"strings/{prefix}.nvo"] = ("\r\n".join(nvo) + "\r\n").encode("cp1252")
    # Independent 4-second PCM silence: referenced voice resource exists, no fake
    # original voice keys. Subtitle display and timing still require engine testing.
    sound = io.BytesIO()
    with wave.open(sound, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        w.writeframes(bytes(22050 * 2 * 4))
    payload[f"sounds/voice/{prefix}_silence.wav"] = sound.getvalue()
    for path, data in payload.items():
        ws.write(runtime / path, data)
    java_dir = root / "generated/java"
    source_path = ws.write(java_dir / (controller + ".java"), java)
    passive = ws.write(java_dir / (prefix + "_Passive.java"), f"public class {prefix}_Passive extends Codex {{}}\n")
    ws.write(root / "model.json", json.dumps(asdict(p), ensure_ascii=False, indent=2))
    class_versions = {}
    if compile_java:
        progress("Compilando los scripts…")
        compiler = ws.output("cache/toolchain/ecj-3.26.0.jar")
        if not compiler.is_file() or hashlib.sha256(compiler.read_bytes()).hexdigest() != ECJ_SHA256:
            raise ValueError("ECJ 3.26.0 ausente o hash incorrecto: ejecutar tools/bootstrap.ps1")
        class_dir = ws.output(runtime / "codex")
        class_dir.mkdir(parents=True, exist_ok=True)
        command = ["java", "-jar", str(compiler), "-1.3", "-proc:none", "-g:lines,source", "-encoding", "UTF-8", "-bootclasspath", str(ws.output("cache/toolchain/classes.zip")), "-classpath", str(ws.output("research/original/Codex.nob")), "-d", str(class_dir), str(source_path), str(passive)]
        result = subprocess.run(command, capture_output=True, text=True)
        ws.write(root / "compiler.log", result.stdout + result.stderr)
        if result.returncode:
            raise ValueError(f"Compilación Java fallida: ver {root / 'compiler.log'}")
        for name in [controller, prefix + "_Passive"]:
            path = class_dir / (name + ".class")
            data = path.read_bytes()
            if data[:8] != bytes.fromhex("cafebabe0003002d"):
                raise ValueError("El compilador no produjo classfile 45.3")
            class_versions[name] = "45.3"
            payload[f"codex/{name}.class"] = data
    # Resource NOB omits Java classes: the real JVM searches codex/ and Codex.nob,
    # so the distribution ZIP includes codex/*.class as loose files.
    progress("Empaquetando la crónica…")
    nob = {path: data for path, data in payload.items() if not path.startswith("codex/")}
    for path in old_report.get("files", {}):
        relative = Path(path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Ruta insegura en informe de build anterior")
        previous = ws.output(runtime / relative)
        if path not in payload and previous.is_file():
            previous.unlink()
    nob_data = zip_bytes(nob)
    ws.write(root / (p.id + ".nob"), nob_data)
    # The native multiplayer file enumerator searches registered NOB indices.
    # Its loose-file search uses the original directory argument instead of the
    # user-prefixed path it computed. A loose-only -user folder is insufficient
    # for a new NSC to appear in the selector (Vampire.exe 0x4cae60).
    # Bundle resources in a root NOB; Java remains under the user JVM classpath.
    distribution = {p.id + ".nob": nob_data}
    distribution.update({path: data for path, data in payload.items() if path.startswith("codex/")})
    bundle = root / "bundle"
    for name in [controller, prefix + "_Passive"]:
        old_class = ws.output(bundle / "codex" / (name + ".class"))
        if not compile_java and old_class.is_file():
            old_class.unlink()
    for path, data in distribution.items():
        ws.write(bundle / path, data)
    if compile_java:
        ws.write(root / (p.id + "_distribution.zip"), zip_bytes(distribution))
    report = {"chronicle": p.id, "status": "compiled-unverified-in-game" if compile_java else "generated-uncompiled", "distribution_layout": "user-directory: root resource NOB + codex classes", "distribution_files": {path: {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()} for path, data in sorted(distribution.items())}, "geometry": level["geometry"][0], "geometry_in_package": False, "original_scene_entities_imported": False, "controller_anchor_evidence": {"scene": source["path"], **anchor}, "environment_strategy": "four empty global counts + original 176-byte environment metadata; optional sky model/animation references", "class_versions": class_versions, "files": {path: {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()} for path, data in sorted(payload.items())}, "native_engine_test": "NOT RUN BY BUILDER: root resource NOB + codex classes await native confirmation", "limitations": ["Only one base level per build", "NSD writer handles tags with empty variable entity blocks", "Chronicle entry 0, scene loading, NOT discovery and callback dispatch await engine test", "World positioning/collision and subtitle behaviour await engine test", "Save/restore ordering and multiplayer replication await engine test"]}
    report['environment_profile'] = environment_record
    report['sky_override'] = p.sky is not None
    ws.write(root / "build_report.json", json.dumps(report, ensure_ascii=False, indent=2))
    progress("Crónica compilada. Paquete disponible en build/.")
    return report

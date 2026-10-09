import argparse
import json
from pathlib import Path
import sys
import yaml
import subprocess

from .catalogue import discover, verify_sources
from .service import Backend
from .paths import Workspace


def main(argv=None):
    parser = argparse.ArgumentParser(description="Redemption Chronicle Maker — backend independiente del editor")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--game", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Leer la instalación y generar catálogos y evidencia")
    scan.add_argument("--no-disassemble", action="store_true")
    sub.add_parser("verify-originals", help="Comparar hashes de las fuentes originales")
    sub.add_parser('diagnostics',help='Informe local de instalación, catálogos y dependencias')
    for command in ['package','uninstall-package']:
        cmd=sub.add_parser(command);cmd.add_argument('chronicle')
        if command=='package':cmd.add_argument('destination',type=Path)
    for command in ['inspect-package','install-package','import-project']:
        cmd=sub.add_parser(command);cmd.add_argument('archive',type=Path)
        if command=='install-package':cmd.add_argument('--accept-custom-code',action='store_true')
        if command=='import-project':cmd.add_argument('directory',type=Path)
    cmd=sub.add_parser('export-project');cmd.add_argument('project',type=Path);cmd.add_argument('destination',type=Path)
    for command in ['deploy','run','clean']:
        cmd=sub.add_parser(command,help='Desplegar en RCM' if command=='deploy' else 'Abrir Redemption con la crónica desplegada')
        cmd.add_argument('chronicle')
    for command in ["validate", "build"]:
        cmd = sub.add_parser(command)
        cmd.add_argument("project", type=Path)
        if command == "build":
            cmd.add_argument("--no-compile", action="store_true")
    args = parser.parse_args(argv)
    from .deployment import default_game
    try:
        args.game = args.game or default_game(args.workspace)
        ws = Workspace(args.workspace, args.game)
        if args.command == "scan":
            result = discover(ws, args.game, not args.no_disassemble)
        elif args.command == "verify-originals":
            result = verify_sources(ws, args.game)
        elif args.command=='diagnostics':
            from .diagnostics import diagnostic_report
            result=diagnostic_report(ws)
        elif args.command in {'package','inspect-package','install-package','uninstall-package','export-project','import-project'}:
            from . import packages
            if args.command=='package':result=packages.create_package(ws,args.chronicle,args.destination)
            elif args.command=='inspect-package':result=packages.inspect_package(args.archive)[0]
            elif args.command=='install-package':result=packages.install_package(ws,args.archive,args.accept_custom_code)
            elif args.command=='uninstall-package':result=packages.uninstall_package(ws,args.chronicle)
            elif args.command=='export-project':
                from .input_limits import parse_source
                data=parse_source(ws.output(args.project).read_text(encoding='utf-8-sig'))
                result={'archive':str(packages.export_project(ws,data,args.destination))}
            else:result={'project':str(packages.import_project(ws,args.archive,args.directory).path)}
        elif args.command == 'deploy':
            from .deployment import deploy
            result=deploy(ws,args.chronicle)
        elif args.command == 'run':
            from .deployment import run_game
            result={'process':run_game(ws,args.chronicle).pid,'native_engine_test':False}
        elif args.command=='clean':
            from .build_transaction import clean_build
            result={'removed':clean_build(ws,args.chronicle)}
        else:
            project_file = ws.output(args.project)
            if getattr(sys,'frozen',False):
                from .startup import prepare_workspace
                prepare_workspace(ws)
            backend = Backend(ws)
            source = project_file.read_text(encoding="utf-8-sig")
            validation = backend.validate(source)
            if not validation.valid and args.command=='validate':
                raise ValueError("\n".join(p.message for p in validation.problems if p.severity == "ERROR"))
            project = validation.project
            if args.command == "validate":
                from .campaign import Campaign
                scenes=[p for s,p in project.scenes] if isinstance(project,Campaign) else [project]
                result = {"valid": True, "chronicle": project.id, "levels": [p.level for p in scenes], "entities": sum(len(p.entities) for p in scenes), "conversations": sum(len(p.conversations) for p in scenes), "runtime_verified": False, "problems": [{"severity": p.severity, "message": p.message} for p in validation.problems]}
            else:
                report = backend.build(source, not args.no_compile)
                project = validation.project
                result = {"status": report["status"], "output": str(ws.output(Path("build") / project.id)), "files": len(report["files"]), "class_versions": report["class_versions"], "game_modified": False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, yaml.YAMLError, subprocess.CalledProcessError) as e:
        print(f"RCM: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

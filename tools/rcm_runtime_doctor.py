"""Inspect and optionally clean stale RCM folders used by the game test."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = Path(r"H:\GOG\Vampire The Masquerade - Redemption")
KEEP = "east_demo"
STALE = {"rcm_circuit", "rcm_mini", "rcm_tutor"}


def main():
    parser = argparse.ArgumentParser(description="Comprueba RCM y limpia restos antiguos de prueba")
    parser.add_argument("--game", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--apply", action="store_true", help="respalda y elimina solo carpetas RCM obsoletas")
    parser.add_argument("--only", metavar="CHRONICLE", help="al aplicar, conserva solo esta crónica dentro de east_demo")
    args = parser.parse_args()
    rcm = (args.game / "RCM").resolve()
    if not rcm.is_dir():
        raise SystemExit(f"No existe: {rcm}")
    if not (rcm / KEEP).is_dir():
        raise SystemExit(f"Falta la carpeta conservada: {rcm / KEEP}")
    entries = []
    for name in sorted(STALE):
        path = rcm / name
        if not path.exists():
            continue
        files = [p for p in path.rglob("*") if p.is_file()]
        entries.append({
            "path": str(path),
            "files": len(files),
            "bytes": sum(p.stat().st_size for p in files),
            "sha256": hashlib.sha256(b"".join(p.read_bytes() for p in sorted(files))).hexdigest() if files else None,
        })
    manifest_path = rcm / KEEP / ".rcm_deployment.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf8")) if manifest_path.is_file() else None
    if args.only and (not manifest or args.only not in manifest.get("owners", {})):
        raise SystemExit(f"La crónica no pertenece al manifiesto: {args.only}")
    result = {"rcm": str(rcm), "kept": KEEP, "stale": entries, "only": args.only, "applied": False}
    owned_remove = []
    if args.only and manifest:
        for owner, files in manifest.get("owners", {}).items():
            if owner != args.only:
                owned_remove.extend((rcm / KEEP / file).resolve() for file in files)
    if args.apply and (entries or owned_remove):
        stamp = str(time.time_ns())
        backup = ROOT / "research/runtime_test/backups" / f"rcm_stale_{stamp}.zip"
        backup.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(backup, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(result, indent=2))
            for row in entries:
                path = Path(row["path"])
                for file in path.rglob("*"):
                    if file.is_file():
                        archive.write(file, str(Path(file.parent.name) / file.relative_to(path)))
            if manifest:
                archive.writestr("east_demo/.rcm_deployment.before.json", manifest_path.read_bytes())
                for file in owned_remove:
                    if file.is_file():
                        archive.write(file, str(Path("east_demo") / file.relative_to(rcm / KEEP)))
        for row in entries:
            shutil.rmtree(row["path"])
        for file in owned_remove:
            if file.is_file():
                file.unlink()
        if args.only and manifest:
            manifest["chronicles"] = [args.only]
            manifest["owners"] = {args.only: manifest["owners"][args.only]}
            manifest["files"] = {file: digest for file, digest in manifest["files"].items() if file in manifest["owners"][args.only]}
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf8")
        result.update({"applied": True, "backup": str(backup)})
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

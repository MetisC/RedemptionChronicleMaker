"""Workspace-local CLI entry point; does not run or install the game."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]
from rcm.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["--workspace", str(ROOT), *sys.argv[1:]]))

"""Desktop entry point. Build CLI remains tools/rcm.py and needs no Qt."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]

if __name__ == "__main__":
    try:
        from rcm.editor.app import main
        raise SystemExit(main())
    except ImportError as error:
        raise SystemExit("Falta una dependencia del editor (PySide6, NumPy o Pillow). Ejecuta: python -m pip install --target cache/vendor -r requirements.txt -r requirements-editor.txt") from error

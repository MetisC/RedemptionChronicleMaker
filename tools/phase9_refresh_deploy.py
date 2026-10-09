"""Refresh only the unified circuit in the authorized RCM directory."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'cache/vendor')]
from rcm.deployment import default_game, deploy
from rcm.document import Document
from rcm.paths import Workspace

if __name__ == '__main__':
    ws = Workspace(ROOT, default_game(ROOT))
    document = Document.load(ws, ROOT / 'chronicles/circuit/project.yaml')
    result = deploy(ws, 'rcm_circuit', directory='east_demo', current_source=document.snapshot())
    ws.write('research/phase9/final_deployment.json', json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

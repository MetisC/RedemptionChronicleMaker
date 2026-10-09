"""Frozen entry point; workspace and JVM live beside the executable."""
from pathlib import Path
import os
import sys

if getattr(sys,'frozen',False):
    base=Path(sys.executable).parent
    runtime=base/'runtime/bin'
    os.environ['PATH']=str(runtime)+os.pathsep+os.environ.get('PATH','')
    if '--workspace' not in sys.argv:sys.argv[1:1]=['--workspace',str(base/'workspace')]
    log=base/'portable_console.log'
    if sys.stdout is None:sys.stdout=log.open('a',encoding='utf8')
    if sys.stderr is None:sys.stderr=sys.stdout
if '--cli' in sys.argv:
    sys.argv.remove('--cli')
    from rcm.cli import main
else:
    from rcm.editor.app import main
raise SystemExit(main())

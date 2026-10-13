"""Frozen entry point; bundled JVM, user data outside the replaceable program."""
from pathlib import Path
import os
import sys

if getattr(sys,'frozen',False):
    base=Path(sys.executable).parent
    runtime=base/'runtime/bin'
    os.environ['PATH']=str(runtime)+os.pathsep+os.environ.get('PATH','')
    from rcm.app_settings import settings_directory
    directory=Path(sys.argv[sys.argv.index('--settings-directory')+1]) if '--settings-directory' in sys.argv else settings_directory()
    try:
        directory.mkdir(parents=True,exist_ok=True)
        if sys.stdout is None:sys.stdout=(directory/'application.log').open('a',encoding='utf8')
    except OSError:
        import io
        if sys.stdout is None:sys.stdout=io.StringIO()
    if sys.stderr is None:sys.stderr=sys.stdout
if '--product-probe' in sys.argv:
    sys.argv.remove('--product-probe')
    from rcm.editor.product_probe import main
elif '--cli' in sys.argv:
    sys.argv.remove('--cli')
    from rcm.cli import main
else:
    from rcm.editor.app import main
raise SystemExit(main())

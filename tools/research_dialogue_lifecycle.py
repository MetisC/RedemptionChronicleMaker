"""Read-only lifecycle evidence from the copied original executable."""
from pathlib import Path
import sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cache/vendor'))
from native_disassembly import disassemble
out=ROOT/'research/round0/dialogue_journal_fix';out.mkdir(parents=True,exist_ok=True)
header='Original PE SHA256 '+hashlib.sha256((ROOT/'research/user_directory/Vampire.exe').read_bytes()).hexdigest()+'\n'
for file,rows in [('native_methods.txt',[(0x46ed60,32,'BeginCutscene JNI table offset 0x10dc7c'),(0x46ed80,32,'EndCutscene JNI table offset 0x10dc88'),(0x46e0e0,57,'SetupCutscene JNI table offset 0x10d928'),(0x46e180,23,'Release JNI')]),('native_lifecycle.txt',[(0x42f580,336,'Begin cutscene'),(0x42f6d0,390,'End cutscene and camera release'),(0x431e10,336,'Setup cutscene calls begin'),(0x458fd0,620,'Conversation start')]),('native_end_order.txt',[(0x458e40,400,'Conversation cleanup clears global pointer at end')])]:
 (out/file).write_text(header+'\n\n'.join(label+'\n'+disassemble(address,size) for address,size,label in rows),encoding='utf8')
print('Saved original lifecycle evidence; no native executable launched')

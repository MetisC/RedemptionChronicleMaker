"""Focused native evidence; reads the copied PE, never runs the game."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cache/vendor'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

data = (ROOT / 'research/user_directory/Vampire.exe').read_bytes()
pe = struct.unpack_from('<I', data, 0x3c)[0]
base = struct.unpack_from('<I', data, pe + 52)[0]
table = pe + 24 + struct.unpack_from('<H', data, pe + 20)[0]
sections = [struct.unpack_from('<IIII', data, table + i * 40 + 8)
            for i in range(struct.unpack_from('<H', data, pe + 6)[0])]
md = Cs(CS_ARCH_X86, CS_MODE_32)
lines = []
for va, size, label in [(0x42848e, 160, 'User registration and underscore NLS autoload'),
                         (0x4a7de0, 1550, 'NSD reader including sky model and animation'),
                         (0x473b70, 280, 'SpawnThingNear JNI'),
                         (0x4b0d00, 1500, 'Placement near owner helper'),
                         (0x4dce14, 130, 'Original NOT libraries and underscore-only autoload'),
                         (0x4979cd, 54, 'Explicit NMF NOT directive calls library loader'),
                         (0x4a7f04, 125, 'NSD optional NOT library imports'),
                         (0x4a8560, 1110, 'NSD entity reader')]:
    for _, rva, rawsize, raw in sections:
        if base + rva <= va < base + rva + rawsize:
            offset = raw + va - base - rva
            break
    else:
        raise ValueError(hex(va))
    lines.append('\n' + label)
    lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}'
                 for i in md.disasm(data[offset:offset + size], va))
(ROOT / 'research/user_directory/scene_runtime.txt').write_text('\n'.join(lines), encoding='utf8')
print('Saved focused scene/runtime disassembly in workspace')

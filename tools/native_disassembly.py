"""Read-only disassembler of the local research copy, never an authoring tool."""
import sys
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cache/vendor'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

def disassemble(address, length):
    data = (ROOT / 'research/user_directory/Vampire.exe').read_bytes()
    pe = struct.unpack_from('<I', data, 60)[0]
    base = struct.unpack_from('<I', data, pe + 52)[0]
    table = pe + 24 + struct.unpack_from('<H', data, pe + 20)[0]
    for i in range(struct.unpack_from('<H', data, pe + 6)[0]):
        _, rva, size, raw = struct.unpack_from('<IIII', data, table + i * 40 + 8)
        if base + rva <= address < base + rva + size:
            off = raw + address - base - rva
            return '\n'.join(f'{x.address:08x}: {x.mnemonic} {x.op_str}' for x in Cs(CS_ARCH_X86, CS_MODE_32).disasm(data[off:off+length], address))
    raise ValueError('Address outside PE sections')

if __name__ == '__main__':
    print(disassemble(int(sys.argv[1], 0), int(sys.argv[2], 0)))

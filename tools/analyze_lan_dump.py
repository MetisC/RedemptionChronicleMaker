"""Read x86 Windows minidumps without executing or changing the game."""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[1]


class Dump:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        count, directory = struct.unpack_from('<II', self.data, 8)
        self.streams = {kind: (size, rva) for kind, size, rva in
                        (struct.unpack_from('<III', self.data, directory + i * 12) for i in range(count))}
        self.ranges = []
        if 9 in self.streams:
            _, rva = self.streams[9]
            count, offset = struct.unpack_from('<QQ', self.data, rva)
            for i in range(count):
                address, size = struct.unpack_from('<QQ', self.data, rva + 16 + i * 16)
                self.ranges.append((address, size, offset))
                offset += size
        if 5 in self.streams:
            _, rva = self.streams[5]
            count = struct.unpack_from('<I', self.data, rva)[0]
            for i in range(count):
                self.ranges.append(struct.unpack_from('<QII', self.data, rva + 4 + i * 16))

    def memory(self, address, size):
        for start, length, offset in self.ranges:
            if start <= address and address + size <= start + length:
                return self.data[offset + address - start:offset + address - start + size]
        return b''

    def analyze(self):
        _, rva = self.streams[6]
        thread, code = struct.unpack_from('<II', self.data, rva)[0], struct.unpack_from('<I', self.data, rva + 8)[0]
        address = struct.unpack_from('<Q', self.data, rva + 24)[0]
        parameters = struct.unpack_from('<15Q', self.data, rva + 40)
        context_size, context_rva = struct.unpack_from('<II', self.data, rva + 160)
        context = self.data[context_rva:context_rva + context_size]
        registers = {name: struct.unpack_from('<I', context, offset)[0] for name, offset in
                     [('edi',156),('esi',160),('ebx',164),('edx',168),('ecx',172),('eax',176),('ebp',180),('eip',184),('esp',196)]}
        stack = self.memory(registers['esp'], 512)
        result = dict(thread=thread, exception=hex(code), address=hex(address),
                      access_type=parameters[0], access_address=hex(parameters[1]),
                      registers={k:hex(v) for k,v in registers.items()},
                      stack=[hex(v[0]) for v in struct.iter_unpack('<I',stack)])
        for key in ('edi','esi','ebx'):
            raw = self.memory(registers[key], 1024)
            result[key+'_memory_hex'] = raw.hex()
        return result


def main():
    folder = ROOT / 'research/runtime_test/lan_crash'
    folder.mkdir(parents=True, exist_ok=True)
    paths = sorted((Path.home()/'AppData/Local/CrashDumps').glob('Vampire*.dmp'), key=lambda p:p.stat().st_mtime, reverse=True)[:4]
    results = []
    for path in paths:
        result = Dump(path).analyze()
        result['dump'] = str(path)
        results.append(result)
    (folder/'dump_analysis.json').write_text(json.dumps(results,indent=2),encoding='utf8')
    print(json.dumps([{k:v for k,v in r.items() if not k.endswith('_memory_hex')} for r in results],indent=2))


if __name__ == '__main__':
    main()

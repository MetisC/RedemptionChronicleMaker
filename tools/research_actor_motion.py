"""Read native animation/action bindings; never execute the original engine."""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'cache/vendor'),str(ROOT/'cache/devtools')]
import capstone
import pefile


def main():
    game = Path(r'H:\GOG\Vampire The Masquerade - Redemption')
    data = (game/'Vampire.exe').read_bytes()
    pe = pefile.PE(data=data)
    base = pe.OPTIONAL_HEADER.ImageBase
    decoder = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    def disassemble(address,limit=200):
        rows=[]
        for op in decoder.disasm(pe.get_data(address-base,limit),address):
            rows.append(dict(address=hex(op.address),instruction=op.mnemonic+' '+op.op_str))
            if op.mnemonic=='ret':break
        return rows
    bindings={}
    for name in ['StopActorMotion','StopActorAction']:
        offset=data.index(name.encode('ascii')+b'\0')
        pointer=base+pe.get_rva_from_offset(offset)
        matches=list(re.finditer(re.escape(struct.pack('<I',pointer)),data))
        assert len(matches)==1
        address=struct.unpack_from('<I',data,matches[0].start()+8)[0]
        rows=disassemble(address)
        calls=[int(r['instruction'].split()[1],16) for r in rows if r['instruction'].startswith('call 0x')]
        target=calls[-1]
        bindings[name]=dict(native_binding=hex(address),body=rows,
                            final_call=hex(target),callee=disassemble(target))
    result=dict(executable_sha256=hashlib.sha256(data).hexdigest(),bindings=bindings,
                source='Read-only native registration table and x86 disassembly',
                engine_executed=False,native_visual_verification=False)
    folder=ROOT/'research/round0/dialogue_motion_camera_fix'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'native_motion_bindings.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:dict(native_binding=v['native_binding'],final_call=v['final_call']) for k,v in bindings.items()}))


if __name__=='__main__':
    main()

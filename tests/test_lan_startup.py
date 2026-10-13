"""Player-profile resource lifetime regression from the native LAN crash."""
import struct
import unittest
from pathlib import Path

from rcm.formats import NotFile, Tag, Template

ROOT = Path(__file__).resolve().parents[1]
import lan_fixture_helpers as repair


class LANStartupTests(unittest.TestCase):
    def test_saved_inventory_resolves_before_chronicle_selection(self):
        # This is a resource-resolution check, not a simulation of the engine.
        wrapper = NotFile([Template('R_demo_s0_reward', [Tag.text(0, 'GarinolJournal')])]).encode()
        old = {'misc/templates/R_demo_s0.not': wrapper,
               'chronicles/R_demo.nmf': b'NOT R_demo_s0.not\r\nNLS _R_demo.nls\r\n',
               'scenes/R_demo.nsd': b'unchanged scene bytes',
               'conversations/R_demo.nco': b'unchanged conversation bytes'}
        saved = struct.pack('<II', 0x1e, 123) + b'r_demo_s0_reward\0'.ljust(32, b'\0')
        name = repair.saved_templates(saved)[0]['template']
        self.assertNotIn(name, repair.startup_templates(old))
        patched, changes = repair.promote(old)
        self.assertIn(name, repair.startup_templates(patched))
        self.assertEqual(changes, {'misc/templates/R_demo_s0.not': 'misc/templates/_R_demo_s0.not'})
        self.assertEqual(patched['misc/templates/_R_demo_s0.not'], wrapper)
        self.assertEqual(patched['chronicles/R_demo.nmf'], b'NOT _R_demo_s0.not\r\nNLS _R_demo.nls\r\n')
        for path in ('scenes/R_demo.nsd', 'conversations/R_demo.nco'):
            self.assertEqual(old[path], patched[path])
        again, changes = repair.promote(patched)
        self.assertEqual(again, patched)
        self.assertEqual(changes, {})

    def test_collision_refused_and_unknown_libraries_preserved(self):
        data = NotFile([Template('thing', [])]).encode()
        with self.assertRaisesRegex(ValueError, 'collision'):
            repair.promote({'misc/templates/R_demo.not': data, 'misc/templates/_R_demo.not': data})
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            repair.promote({'misc/templates/original.not': data})


if __name__ == '__main__':
    unittest.main()

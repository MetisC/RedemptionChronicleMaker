"""Real NSD points, original evidence and native entry IDs; no game automation."""
import copy
from pathlib import Path
import struct
from unittest import TestCase
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.formats import Scene,Tag
from rcm.native_arrivals import planes,sector_at,records,validate_record
from rcm.campaign_generator import runtime
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]


class NativeArrivals(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')))
    def test_original_tenebrae_point_and_inward_sector_planes(self):
        source=self.backend.hints['l1_ten1.nsd']['source'];data=(ROOT/'research/original'/source['archive']/source['path']).read_bytes()
        point=struct.pack('<3f',365,-976,-512);at=data.index(point);record=validate_record(data[at-40:at+20]);row=struct.unpack('<I12fII',record)
        self.assertEqual(row[0],21);self.assertEqual(row[-2:],(0,0))
        sectors=planes(self.backend.ws,self.backend.levels['RaveClub']);self.assertEqual(sector_at(sectors,[365,-976,-512]),21);self.assertEqual(sector_at(sectors,[724.1906,-338.02884,-512]),19)
        with self.assertRaisesRegex(ValueError,'fuera'):sector_at(sectors,[1e6,1e6,1e6])
    def test_generated_points_roundtrip_and_corrupt_or_truncated_records_reject(self):
        source=blank()['scenes'][0];source['entries'].append(copy.deepcopy(source['entries'][0]));source['entries'][1]['id']='other';source['default_entry']='other'
        points=records(self.backend.ws,self.backend.levels['EastLondon'],source)
        encoded=Scene('S','L',[[Tag.text(0,'ghost')]],entrances=points).encode();decoded=Scene.read(encoded)
        self.assertEqual(decoded.encode(),encoded);self.assertEqual(decoded.entrances,points)
        self.assertEqual(struct.unpack_from('<II',points[0],52),(0,0));self.assertEqual(struct.unpack_from('<II',points[1],52),(1,0))
        for data in [points[0][:-1],struct.pack('<I',100000)+points[0][4:],points[0][:4]+struct.pack('<f',float('nan'))+points[0][8:]]:
            with self.assertRaises(ValueError):validate_record(data)
        with self.assertRaises(ValueError):Scene.read(encoded[:-1])
    def test_runtime_uses_native_teleport_and_default_point_is_zero_without_changing_format9(self):
        root=blank();root['project_format']=10;s=root['scenes'][0];s['entries'].append(copy.deepcopy(s['entries'][0]));s['entries'][1]['id']='default';s['default_entry']='default'
        result=self.backend.validate(root);self.assertTrue(result.valid,[p.message for p in result.problems]);java=runtime(result.project,*result.project.scenes[0])[1]
        arrive=java[java.index('private boolean arrive()'):java.index('private int patrolActor')]
        self.assertIn('case 0: ok=CodexPlayer.TeleportPartyToEntrance(player,1)',arrive);self.assertIn('case 1: ok=CodexPlayer.TeleportPartyToEntrance(player,0)',arrive);self.assertNotIn('SetPosition',arrive)
        old=self.backend.validate(blank()).project;old_java=runtime(old,*old.scenes[0])[1];self.assertNotIn('TeleportPartyToEntrance',old_java)

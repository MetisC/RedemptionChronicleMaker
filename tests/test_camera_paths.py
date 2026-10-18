"""NCP read/write against all originals and independently evaluated polynomials."""
import math,struct,zipfile
from pathlib import Path
from unittest import TestCase
from rcm.camera_paths import CameraPath,authored


class CameraPaths(TestCase):
    def points(self,n):return [dict(position=[i*10,0,5],orientation=[10,0,i*5]) for i in range(n)]
    def test_one_two_three_and_native_maximum(self):
        for n in (1,2,3,4,128):
            with self.subTest(n=n):
                path=authored(self.points(n));self.assertEqual(len(path.encode()),8+104*n)
                self.assertEqual(CameraPath.read(path.encode()).encode(),path.encode())
                self.assertEqual(path.sample(path.total)[0],self.points(n)[-1]['position'])
    def test_all_originals_byte_exact_roundtrip(self):
        with zipfile.ZipFile(Path(r'H:\GOG\Vampire The Masquerade - Redemption')/'Resource.nob') as archive:
            names=[n for n in archive.namelist() if n.lower().endswith('.ncp')]
            self.assertEqual(len(names),174)
            for name in names:
                with self.subTest(name=name):data=archive.read(name);self.assertEqual(CameraPath.read(data).encode(),data)
    def test_linear_polynomial_and_shortest_angle(self):
        points=self.points(2);points[0]['orientation']=[350,0,0];points[1]['orientation']=[10,0,0]
        path=authored(points);position,orientation=path.sample(5)
        for a,b in zip(position,[5,0,5]):self.assertAlmostEqual(a,b,places=5)
        for a,b in zip(orientation,[360,0,0]):self.assertAlmostEqual(a,b,places=5)
        self.assertEqual(path.records[0][8:14],(0,)*6);self.assertEqual(path.total,10)
    def test_malformed_counts_truncation_trailing_and_nonfinite(self):
        data=authored(self.points(1)).encode()
        for bad in (b'',data[:7],data[:-1],data+b'0',struct.pack('<I',0)+data[4:],struct.pack('<I',129)+data[4:]):
            with self.subTest(size=len(bad)),self.assertRaises(ValueError):CameraPath.read(bad)
        for value in (math.nan,math.inf,-math.inf):
            with self.assertRaises(ValueError):CameraPath.read(data[:8]+struct.pack('<f',value)+data[12:])
    def test_authored_input_bounds_and_zero_segments(self):
        for points in ([],self.points(129),[dict(position=[0,0,0],orientation=[0,0,0])]*2):
            with self.assertRaises(ValueError):authored(points)
        for value in (True,math.nan,math.inf,1e9):
            points=self.points(1);points[0]['position'][0]=value
            with self.assertRaises(ValueError):authored(points)
        points=self.points(1);points[0]['fov']=80
        with self.assertRaises(ValueError):authored(points)

"""Distribution accepts bounded project NCPs, never geometry or invalid paths."""
import json,tempfile
from pathlib import Path
from unittest import TestCase
from rcm.camera_paths import authored
from rcm.generator import zip_bytes
from rcm.packages import inspect_package,records

ROOT=Path(__file__).resolve().parents[1]


class CameraPathPackages(TestCase):
    def test_native_path_distribution_and_malformed_rejection(self):
        data=authored([dict(position=[0,0,100],orientation=[0,0,90])]).encode()
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            path=Path(folder)/'camera.rcmpack'
            for name,payload,valid in [('paths/camera1.ncp',data,True),('paths/camera1.ncp',data[:-1],False),('misc/camera1.ncp',data,False),('paths/camera1.nil',data,False)]:
                files={'camera_test.nob':zip_bytes({name:payload})}
                manifest=dict(format=1,kind='chronicle',id='camera_test',version='1.0.0',custom_code=False,files=records(files))
                files['manifest.json']=json.dumps(manifest).encode('utf8');path.write_bytes(zip_bytes(files))
                with self.subTest(name=name,valid=valid):
                    if valid:self.assertEqual(inspect_package(path)[0]['id'],'camera_test')
                    else:
                        with self.assertRaises(ValueError):inspect_package(path)

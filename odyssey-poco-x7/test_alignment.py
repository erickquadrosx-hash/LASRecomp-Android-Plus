import tempfile
import unittest
import zipfile
import struct
from pathlib import Path
from zipalign_raw import align_zip

class ZipAlignmentTests(unittest.TestCase):
    def test_uncompressed_resources_aligned_and_bytes_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            before=Path(folder)/'source.apk'
            after=Path(folder)/'aligned.apk'
            with zipfile.ZipFile(before,'w') as z:
                z.writestr('classes.dex',b'dex\\n035\\0',compress_type=zipfile.ZIP_DEFLATED)
                z.writestr('resources.arsc',b'RESOURCES',compress_type=zipfile.ZIP_STORED)
                z.writestr('res/example.png',b'IMAGEBYTES',compress_type=zipfile.ZIP_STORED)
            align_zip(before,after)
            with zipfile.ZipFile(before) as a,zipfile.ZipFile(after) as b:
                self.assertEqual(a.namelist(),b.namelist())
                self.assertIsNone(b.testzip())
                for name in a.namelist():
                    self.assertEqual(a.read(name),b.read(name))
                for member in b.infolist():
                    if member.compress_type!=0:continue
                    with open(after,'rb') as stream:
                        stream.seek(member.header_offset)
                        local=stream.read(30)
                    name_len,extra=struct.unpack_from('<HH',local,26)
                    self.assertEqual((member.header_offset+30+name_len+extra)%4,0)
if __name__=='__main__':
    unittest.main()

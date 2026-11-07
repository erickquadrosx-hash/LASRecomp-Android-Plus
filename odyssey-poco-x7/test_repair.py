import importlib.util
import pathlib
import tempfile
import unittest
import zipfile

MODULE = pathlib.Path(__file__).parent / "repair.py"
spec = importlib.util.spec_from_file_location("odyssey_repair", MODULE)
repair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repair)

class RepackTests(unittest.TestCase):
    def test_preserves_original_code_and_changes_only_package(self):
        with tempfile.TemporaryDirectory() as root:
            original = pathlib.Path(root) / "input.apk"
            modified = pathlib.Path(root) / "modified.apk"
            contents = {
                "AndroidManifest.xml": ("prefix" + repair.OLD + "\0suffix").encode("utf-16le"),
                "resources.arsc": repair.OLD.encode("utf-16le"),
                "lib/arm64-v8a/libsmo.so": ("xx" + repair.OLD + "\0yy").encode("ascii"),
                "classes.dex": b"dex\\n035\\0 untouched original code",
                "assets/data.txt": b"unchanged assets",
                "META-INF/OLD.RSA": b"old signature should be removed",
            }
            with zipfile.ZipFile(original, "w") as z:
                for key, value in contents.items():
                    z.writestr(key, value)
            repair.patch_apk(original, modified)
            with zipfile.ZipFile(modified) as result:
                self.assertEqual(result.read("classes.dex"), contents["classes.dex"])
                self.assertEqual(result.read("assets/data.txt"), contents["assets/data.txt"])
                self.assertNotIn("META-INF/OLD.RSA", result.namelist())
                self.assertEqual(result.testzip(), None)
                self.assertIn(repair.NEW.encode("utf-16le"), result.read("resources.arsc"))


    def test_binary_manifest_version_code_becomes_two(self):
        import struct

        def string(s):
            return struct.pack('<H', len(s)) + s.encode('utf-16le') + b'\x00\x00'

        s0, s1 = string('manifest'), string('versionCode')
        # Android binary XML string-pool (UTF-16) with two strings.
        pool = (struct.pack('<HHI', 1, 28, 36 + len(s0) + len(s1))
                + struct.pack('<5I', 2, 0, 0, 36, 0)
                + struct.pack('<2I', 0, len(s0)) + s0 + s1)
        attr = struct.pack('<IIIHBBI', 0xffffffff, 1, 0xffffffff, 8, 0, 0x10, 1)
        start = (struct.pack('<HHI', 0x102, 16, 56)
                 + struct.pack('<4I', 0, 0xffffffff, 0xffffffff, 0)
                 + struct.pack('<3H', 20, 20, 1)
                 + struct.pack('<3H', 0, 0, 0) + attr)
        doc = struct.pack('<HHI', 3, 8, 8 + len(pool) + len(start)) + pool + start
        changed = repair.bump_version_code(doc)
        self.assertEqual(len(doc), len(changed))
        self.assertNotEqual(doc, changed)
        self.assertEqual(struct.unpack_from('<I', changed, len(changed)-4)[0], 2)

if __name__ == "__main__":
    unittest.main()

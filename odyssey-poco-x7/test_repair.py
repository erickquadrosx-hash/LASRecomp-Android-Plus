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

if __name__ == "__main__":
    unittest.main()

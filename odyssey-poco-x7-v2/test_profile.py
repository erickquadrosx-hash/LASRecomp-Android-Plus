import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("patch_launcher", Path(__file__).with_name("patch_launcher.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class LauncherPresetTests(unittest.TestCase):
    def test_insertion_and_defaults(self):
        s = '        config.mkdirs();\n        c.addView(header("Performance"));\n    void graphicsPage() {\n'
        changed = mod.patch(s)
        for mark in ("installPocoProfile(false)", "installPocoProfile(true)", "frame_rate = 30",
                     "console_mode = handheld", "driver = system", "diagnostics = off",
                     "graphics_before_poco_v2.ini"):
            self.assertIn(mark, changed)
        with self.assertRaises(AssertionError):
            mod.patch(changed)

if __name__ == "__main__":
    unittest.main()

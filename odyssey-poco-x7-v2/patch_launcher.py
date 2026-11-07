#!/usr/bin/env python3
"""Minimal, reversible stable profile injection into official Odyssey B0.2 Java UI."""
from pathlib import Path
import sys

NEW_METHOD = r'''
    /** POCO X7 Pro launch profile. Leave existing files alone without user input. */
    void installPocoProfile(boolean userInitiated) {
        File graphics = new File(config, "graphics.ini");
        if (!userInitiated && graphics.exists()) return;
        if (userInitiated && graphics.exists()) {
            File backup = new File(config, "graphics_before_poco_v2.ini");
            if (!backup.exists()) {
                try (FileInputStream in = new FileInputStream(graphics);
                     FileOutputStream out = new FileOutputStream(backup)) { pipe(in, out); }
                catch (java.io.IOException e) { toast("Backup failed: " + e.getMessage()); return; }
            }
        }
        String settings = "; POCO X7 Pro V2 30 FPS stable profile\r\n"
            + "renderer = vulkan\r\nvsync = mailbox\r\ngpu = auto\r\nconsole_mode = handheld\r\n"
            + "resolution_scale = 0.85\r\nframe_rate = 30\r\nfps_cap = 60\r\nboost = auto\r\n"
            + "anti_aliasing = off\r\nsharpening = 0\r\nanisotropic_filtering = game\r\n"
            + "shader_wait = hold\r\nframe_time_overlay = off\r\ndriver = system\r\n"
            + "diagnostics = off\r\nprofile = custom\r\nfps_counter = on\r\n";
        try (FileOutputStream out = new FileOutputStream(graphics)) {
            out.write(settings.getBytes(StandardCharsets.UTF_8));
        } catch (java.io.IOException e) { toast("Profile setup failed: " + e.getMessage()); }
    }
'''

def patch(content):
    assert content.count('        config.mkdirs();') == 1, 'unexpected onCreate structure'
    assert content.count('    void graphicsPage() {') == 1
    assert 'installPocoProfile(boolean userInitiated)' not in content
    content = content.replace('        config.mkdirs();', '        config.mkdirs();\n        installPocoProfile(false);', 1)
    anchor = '        c.addView(header("Performance"));'
    assert content.count(anchor) == 1
    replacement = '''        c.addView(header("Performance"));
        Button pocoPreset = button("Apply POCO X7 Pro stable 30 FPS profile", ACCENT2);
        pocoPreset.setOnClickListener(v -> confirm("Apply POCO X7 Pro graphics settings? Existing settings will be backed up before changing them.", () -> {
            installPocoProfile(true);
            show(1);
        }));
        c.addView(pocoPreset, new LinearLayout.LayoutParams(-1, dp(52)));'''
    content = content.replace(anchor, replacement, 1)
    return content.replace('    void graphicsPage() {', NEW_METHOD + '\n    void graphicsPage() {', 1)

if __name__ == '__main__':
    p=Path(sys.argv[1]); p.write_text(patch(p.read_text(encoding='utf8')),encoding='utf8')
    print('Rebuilt Android launcher with reversible POCO X7 Pro 30 FPS profile')

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Integra o launcher BPD no Lemon Android Lite, sem incluir arquivos de jogos."""
from pathlib import Path

root = Path("lemon-src")
manifest = root / "src/android/app/src/main/AndroidManifest.xml"
build = root / "src/android/app/build.gradle.kts"
src = Path("projects/bpd-embedded-engine/BpdPocoLauncherActivity.java")
target = root / "src/android/app/src/main/java/dev/lemon/lemon_emu/activities/BpdPocoLauncherActivity.java"

m = manifest.read_text(encoding="utf-8")
old_category = '<category android:name="android.intent.category.LAUNCHER" />'
assert m.count(old_category) == 1, "O filtro de lancamento do Lemon mudou"
m = m.replace(old_category, '<category android:name="android.intent.category.DEFAULT" />', 1)
anchor = '        <activity\n            android:name="dev.lemon.lemon_emu.ui.main.MainActivity"'
assert m.count(anchor) == 1, "A atividade principal do Lemon nao foi localizada"
insertion = '''        <activity
            android:name="dev.lemon.lemon_emu.activities.BpdPocoLauncherActivity"
            android:exported="true"
            android:theme="@android:style/Theme.Material.NoActionBar">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

'''
m = m.replace(anchor, insertion + anchor, 1)
manifest.write_text(m, encoding="utf-8")

g = build.read_text(encoding="utf-8")
old_id = 'applicationId = "dev.lemon.lemon_emulator.lite"'
assert g.count(old_id) == 1, "O ID de pacote Lemon Lite mudou"
g = g.replace(old_id, 'applicationId = "br.com.bdpmobile.pocoembedded"')
old_label = 'manifestPlaceholders += mapOf("appNameBase" to "Lemon Lite")'
assert g.count(old_label) == 1, "O nome do aplicativo mudou"
g = g.replace(old_label, 'manifestPlaceholders += mapOf("appNameBase" to "BPD POCO Core (Lemon)")')
g = g.replace(
    'resValue("string", "app_name_suffixed", "Lemon Lite")',
    'resValue("string", "app_name_suffixed", "BPD POCO Core (Lemon)")'
)
build.write_text(g, encoding="utf-8")

target.write_bytes(src.read_bytes())
assert target.exists()
print("Launcher BPD integrado ao projeto Android do Lemon Lite.")

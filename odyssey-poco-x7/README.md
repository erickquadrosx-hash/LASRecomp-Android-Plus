# Odyssey / POCO X7 Pro — crash-safe packaging (2026-11-07)

Isolated experimental work on branch `odyssey-poco-x7-crashfix-20261107`. The main LASRecomp branch and its approved builds are **untouched**.

## Symptom
The earlier `Odyssey_POCO_X7_Pro_INSTALL_FIX.apk` installed but was reported to crash on opening (Android 16, Dimensity 8400 Ultra, Mali-G720 MC7). There is no logcat yet, so the root cause is **not confirmed**.

## Changes compared to earlier experiment
- Use the **original, byte-for-byte unchanged** `classes.dex`; undo the earlier edits to frame rate, resolution, and shader dropdown strings.
- For side-by-side installation, patch only the installed package string in AndroidManifest, resources table, and the same embedded package-name literal in the native game binary.
- Retain all original native shader/compiler code and the device's system Mali Vulkan driver.
- Re-sign the APK using Android SDK Build Tools. A preexisting signing key is essential for installing as an update.

## To rebuild locally
Use your *own* `Super Mario Odyssey.apk` as the input, along with a compatible signing keystore. Never commit the APK, dumps, keys, keystore, or game assets to GitHub.

```bash
export ODYSSEY_KS_PASS='your-keystore-password'
python odyssey-poco-x7/repair.py \
  --input '/path/to/Super Mario Odyssey.apk' \
  --output 'Odyssey_POCO_X7_Pro_CRASH_SAFE.apk' \
  --keystore '/path/to/your-signing.keystore' \
  --alias poco_x7
```

Required on PATH: Android SDK Build Tools `zipalign` and `apksigner`.

A different certificate **cannot** update a previously installed copy; Android will require backup/uninstall/reinstall. The locally supplied chat APK uses the same local certificate as the earlier INSTALL FIX, but **that private key is not published to GitHub**.

## GitHub Actions validation
`.github/workflows/odyssey-x7-verify.yml` verifies the patch script and tests a synthetic APK. It **does not compile or publish a playable game APK**, because the user's original private executable is not in GitHub.

## What to test
1. Install over the earlier **INSTALL FIX**, if still installed (same package and signing identity in the local chat output).
2. Launch and confirm the graphics tab and game menu are accessible.
3. Before playing, choose 30 fps full speed, handheld, 0.5-0.75 scale, and system Vulkan (not Turnip).
4. If Android still reports a crash, capture the real exception: `adb logcat -d -b crash -v time`, or use Advanced → Export logs when the menu can be opened.

No claims about a working launch or measured FPS are made until tested on the actual POCO X7 Pro.

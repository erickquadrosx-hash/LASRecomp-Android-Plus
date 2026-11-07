# POCO X7 Pro / Mali-G720: stability-first final candidate

**Candidate, not verified on the phone.** Original pipeline branch stays unchanged.

- The owner-provided generated main ARM64 objects are recompiled with `-O1`. Large functions can use per-function optnone; on compilation failure all original objects are restored. The build summary reports whether optimization succeeded.
- New-install defaults: 30 FPS full-speed (not an FPS cap that slows gameplay), handheld 1280x720 base, 0.75 internal scale, Vulkan/system driver, FXAA off, sharpening 20, CPU boost auto and diagnostics off.
- Existing `graphics.ini` is **not overwritten**. To use the new preset on an existing installation, open Graphics and press the POCO X7 Pro stable profile button; the original `graphics.ini` is backed up.
- The explicit preset disables experimental Mali exact-key shader look-ahead, reducing possible background CPU contention.
- Preserve previous BC4/BC5 optimization, allocation/overflow protection and ADPF adjustment. Depth tests, Vulkan barriers, API game code and saved game data are not patched.

The APK produced by GitHub Actions has a newly created release signing key unless a stable key is restored separately; do not uninstall the existing app without backing up saves, cache and game files. Building or signing does not prove playable frame times. Device testing is required.

Do not publish proprietary game data, console keys or dumps.

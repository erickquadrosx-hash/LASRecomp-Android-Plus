#!/usr/bin/env python3
"""Regressions for POCO X7 Pro's first-run video profile (no game files)."""
from pathlib import Path

settings = Path("runtime/settings.c").read_text()
initial = settings.split("Settings g_settings = {", 1)[1].split("\n};", 1)[0]
android = initial.rsplit("#ifdef __ANDROID__", 1)[1].split("#endif", 1)[0]
aspect = initial.split("#ifdef __ANDROID__", 1)[1].split("#else", 1)[0]
bilinear = initial.split("#ifdef __ANDROID__", 2)[2].split("#else", 1)[0]
expected = {
    "16:9 original": (".aspect = ASPECT_ORIGINAL", aspect),
    "Upscaler bilinear": (".upscaler = UPSCALE_BILINEAR", bilinear),
    "Native 60 FPS": (".frame_rate = FRAME_RATE_NATIVE_60", android),
    "Frame generation off": (".frame_gen = 0", android),
    "Fixed 1x": (".res_mode = 1", android),
    "Balanced power": (".power_mode = 0", android),
    "Fullscreen off": (".fullscreen = false", initial),
}
for key, (needle, source) in expected.items():
    assert needle in source, f"{key}: {needle} missing"
assert "g_default_upscaler = UPSCALE_BILINEAR;" in settings
assert "g_default_res_mode = 1;" in settings
assert "if (g_settings.upscaler_auto) g_settings.upscaler = g_default_upscaler;" in settings
assert "if (g_settings.res_auto) g_settings.res_mode = g_default_res_mode;" in settings
assert 'else if (!strcmp(key, "frame_rate")) g_settings.frame_rate' in settings
assert 'else if (!strcmp(key, "aspect")) g_settings.aspect' in settings
assert 'else if (!strcmp(key, "fullscreen")) g_settings.fullscreen' in settings
hooks = Path("runtime/hle/hooks.c").read_text()
assert "if (GA_AT(hook_field[i]) == site)" in hooks, "Shield freeze hook fix missing"
delegate = Path("runtime/hle/delegate_null.c").read_text()
assert "vt != GA(DELEGATE_JOB_VTABLE_BASE)" in delegate, "Shield frame job fix missing"
patch = Path("tools/android/apply_poco_x7_pro.py").read_text()
assert "const bool use_fp16 = !e || !*e || atoi(e) != 0;" in patch
print(f"{len(expected)} Android profile checks + user overrides + preserved shield/FP16 fixes passed")

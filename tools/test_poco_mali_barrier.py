#!/usr/bin/env python3
"""Guard experimental Mali split barriers + approved baseline behavior.

Source-level checks: the Android CMake build compiles the actual Vulkan code.
The Android GPU/frame presentation must still be checked on the device.
"""
from pathlib import Path
import re

src = Path("runtime/nvn/vulkan/exec.c").read_text(encoding="utf8")
def check(condition, msg):
    assert condition, msg

start = src.index("static int split_barrier = -1;")
end = src.index("static void ring_retire(void);", start)
body = src[start:end]
tests = [
    ("opt-out environment variable", '"LARECOMP_VK_SPLIT_BARRIER"' in body),
    ("ARM GPU vendor detection", "g_vk.props.vendorID == 0x13B5" in body),
    ("Android-specific default", "#ifdef __ANDROID__" in body),
    ("other targets default disabled", "split_barrier = e && *e ? atoi(e) != 0 : 0;" in body),
    ("fragment stage for per-pixel shaders", "VK_PIPELINE_STAGE_2_FRAGMENT_SHADER_BIT" in body),
    ("depth-attachment stages", "VK_PIPELINE_STAGE_2_EARLY_FRAGMENT_TESTS_BIT" in body and "VK_PIPELINE_STAGE_2_LATE_FRAGMENT_TESTS_BIT" in body),
    ("colour output stage", "VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT" in body),
    ("compute shader consumer", "frag | VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT" in body),
    ("transfer consumer", "VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT" in body),
    ("split into two barriers", "memoryBarrierCount = 2" in body),
    ("original full barrier retained", "memoryBarrierCount = 1" in body and "VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT" in body),
    ("vertex excluded from fragment dependencies", "dstStageMask = frag | VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT" in body),
    ("Vulkan commands use recorder", body.count("rec_CmdPipelineBarrier2(cb, &di)") == 2),
]
for title, success in tests:
    check(success, title)

shader = Path("runtime/nvn/vulkan/shaders.c").read_text(encoding="utf8")
check("stage != STAGE_VERTEX" in shader, "vertex shader compilation changed")
check("g_vk.props.vendorID == 0x13B5" in shader, "Mali shader optimization missing")
default = Path("runtime/settings.c").read_text(encoding="utf8")
for value in [".frame_rate = FRAME_RATE_NATIVE_60", ".frame_gen = 0",
              ".res_mode = 1", ".power_mode = 0", ".aspect = ASPECT_ORIGINAL",
              ".upscaler = UPSCALE_BILINEAR"]:
    check(value in default, "approved video default changed: " + value)
hooks = Path("runtime/hle/hooks.c").read_text(encoding="utf8")
check("GA_AT(hook_field[i]) == site" in hooks, "shield freeze hook regression")
delegate = Path("runtime/hle/delegate_null.c").read_text(encoding="utf8")
check("vt != GA(DELEGATE_JOB_VTABLE_BASE)" in delegate, "shield freeze frame-job regression")
build = Path("android/app/build.gradle").read_text(encoding="utf8")
check("applicationIdSuffix '.pocoperf2'" in build, "previous APK install is not isolated")
print(f"{len(tests) + 10} Mali barrier / approved-profile / rollback checks passed")

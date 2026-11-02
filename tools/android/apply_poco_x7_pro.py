#!/usr/bin/env python3
"""POCO X7 Pro / ARM Mali-G720 compatibility patch for LASRecomp Android 1.2.0.
Run from the repository root before the Android build.
"""
from pathlib import Path

def replace_once(file, old, new):
    p = Path(file)
    data = p.read_text(encoding="utf-8")
    n = data.count(old)
    if n != 1:
        raise SystemExit(f"Expected exactly one match in {file}, found {n}: {old[:80]!r}")
    p.write_text(data.replace(old, new, 1), encoding="utf-8")
    print("Patched", file)

cm = "android/app/CMakeLists.txt"
anchor = "add_subdirectory(${ROOT}/build/android/SDL3 ${CMAKE_BINARY_DIR}/SDL3)"
replace_once(cm, anchor, anchor +
    '\n# 16 KiB Android page compatibility for dynamically linked SDL3.\n'
    'target_link_options(SDL3-shared PRIVATE "-Wl,-z,max-page-size=16384" "-Wl,-z,common-page-size=16384")')
replace_once(cm,
    'target_link_options(${t} PRIVATE "-Wl,-z,max-page-size=16384")',
    'target_link_options(${t} PRIVATE "-Wl,-z,max-page-size=16384" "-Wl,-z,common-page-size=16384")')
replace_once(cm,
    'target_link_options(main PRIVATE "-Wl,-z,max-page-size=16384" "-Wl,-Bsymbolic"',
    'target_link_options(main PRIVATE "-Wl,-z,max-page-size=16384" "-Wl,-z,common-page-size=16384" "-Wl,-Bsymbolic"')

dev = "runtime/nvn/vulkan/device.c"
replace_once(dev,
    '            const char *e = getenv("LARECOMP_HALF_NATIVE");\n'
    '            if (h12.shaderFloat16 && (!e || atoi(e))) f12.shaderFloat16 = VK_TRUE, maxwell_half_native = 1;',
    '            // Diagnostic: use native FP16 for Mali when supported by the driver.\n'
    '            // LARECOMP_HALF_NATIVE=0 disables it for A/B comparison.\n'
    '            const bool arm_mali = g_vk.props.vendorID == 0x13B5 &&\n'
    '                (strstr(g_vk.props.deviceName, "Mali") || strstr(g_vk.props.deviceName, "mali"));\n'
    '            const char *e = getenv("LARECOMP_HALF_NATIVE");\n'
    '            const bool use_fp16 = !e || !*e || atoi(e) != 0;\n'
    '            if (h12.shaderFloat16 && use_fp16) f12.shaderFloat16 = VK_TRUE, maxwell_half_native = 1;\n'
    '            if (arm_mali) LOG("[vk] ARM Mali: guest half math %s\\n",\n'
    '                              maxwell_half_native ? "native FP16" : "conservative FP32");')
print("POCO X7 Pro patches successfully applied")

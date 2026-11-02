#!/usr/bin/env python3
"""Guarded PanVK v26.3.1 AHardwareBuffer compatibility experiment.
Only run after upstream prepare-rc5-tree.sh on pinned Mesa."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: apply_fix.py <prepared Mesa source>")
root = Path(sys.argv[1])

def fix(filename, old, new, count=1):
    path = root / filename
    s = path.read_text()
    if s.count(old) != count:
        raise RuntimeError(f"Upstream drift: {filename}, expected {count} matches, found {s.count(old)}")
    path.write_text(s.replace(old, new, count))
    print("Patched", filename)

wsi = "src/panfrost/vulkan/panvk_wsi.c"
fix(wsi,
    "      { VK_FORMAT_R8G8B8A8_UNORM, VK_COLOR_SPACE_SRGB_NONLINEAR_KHR },\n"
    "      { VK_FORMAT_B8G8R8A8_UNORM, VK_COLOR_SPACE_SRGB_NONLINEAR_KHR },\n"
    "      { VK_FORMAT_R8G8B8A8_SRGB,  VK_COLOR_SPACE_SRGB_NONLINEAR_KHR },",
    "      { VK_FORMAT_R8G8B8A8_UNORM, VK_COLOR_SPACE_SRGB_NONLINEAR_KHR },",
    count=2)
fix(wsi,
    "         .usage = AHARDWAREBUFFER_USAGE_GPU_COLOR_OUTPUT |\n"
    "                  AHARDWAREBUFFER_USAGE_GPU_SAMPLED_IMAGE |\n"
    "                  AHARDWAREBUFFER_USAGE_CPU_READ_OFTEN,",
    "         .usage = AHARDWAREBUFFER_USAGE_GPU_COLOR_OUTPUT |\n"
    "                  AHARDWAREBUFFER_USAGE_GPU_SAMPLED_IMAGE |\n"
    "                  AHARDWAREBUFFER_USAGE_CPU_READ_OFTEN |\n"
    "                  AHARDWAREBUFFER_USAGE_CPU_WRITE_OFTEN,")
fix("src/vulkan/runtime/vk_android.c",
    "   for (int i = 0; i < h->numFds && size <= 0; i++) {\n"
    "      fd = h->data[i];\n"
    "      size = fd >= 0 ? lseek(fd, 0, SEEK_END) : -1;\n"
    "   }",
    "   for (int i = 0; i < h->numFds && size <= 0; i++) {\n"
    "      fd = h->data[i];\n"
    "      struct stat st;\n"
    "      size = (fd >= 0 && fstat(fd, &st) == 0 && st.st_size > 0) ? st.st_size : -1;\n"
    "      if (size <= 0 && fd >= 0)\n"
    "         size = lseek(fd, 0, SEEK_END);\n"
    "   }")
fix(wsi, '#include "panvk_android.h"', '#include "panvk_android.h"\n#include <stdio.h>')
fix(wsi,
    "      result = panvk_GetAndroidHardwareBufferPropertiesANDROID(device, chain->images[i].ahb, &ahb_props);\n"
    "      if (result != VK_SUCCESS) {\n"
    "         panvk_android_swapchain_destroy(&chain->base, pAllocator);\n"
    "         return result;\n"
    "      }",
    "      result = panvk_GetAndroidHardwareBufferPropertiesANDROID(device, chain->images[i].ahb, &ahb_props);\n"
    "      if (result != VK_SUCCESS) {\n"
    '         fprintf(stderr, "[POCO-G720-AHB] GetAndroidHardwareBufferProperties failed: image=%u result=%d\\n", i, result);\n'
    "         panvk_android_swapchain_destroy(&chain->base, pAllocator);\n"
    "         return result;\n"
    "      }")
print("Source patched successfully; device functionality NOT validated.")

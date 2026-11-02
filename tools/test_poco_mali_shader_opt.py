#!/usr/bin/env python3
"""Tests actual SPIR-V opt policy (extracted C) without Android, a GPU or game files."""
import os
import pathlib
import re
import subprocess
import tempfile

source = pathlib.Path("runtime/nvn/vulkan/shaders.c").read_text()
start = source.index("static int spv_flags(void) {")
end = source.index("\nstatic uint64_t src_hash(", start)
policy = source[start:end]
assert 'g_vk.props.vendorID == 0x13B5' in policy, "Only ARM Mali should opt in automatically"
assert 'getenv("LARECOMP_VK_OPT_FS")' in policy, "A/B override missing"
assert 'h ^= (uint64_t)spv_flags() << 40;' in source, "Shader cache not partitioned"
assert 'stage != STAGE_VERTEX' in source, "Vertex opt would cause depth-prepass foliage holes"
assert "shaderc_optimization_level_performance" in source
assert "shaderc_optimization_level_zero" in source

test_c = """
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
struct { struct { uint32_t vendorID; } props; } g_vk;
#define LOG(...) ((void)0)
""" + policy + """
int main(int argc, char **argv) {
    g_vk.props.vendorID = (uint32_t)strtoul(argv[1], NULL, 0);
    printf("%d\\n", spv_flags());
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="poco-shader-opt-") as td:
    p = pathlib.Path(td)
    (p / "test.c").write_text(test_c)
    for android in (True, False):
        exe = p / ("android" if android else "desktop")
        cmd = ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter"]
        if android: cmd.append("-D__ANDROID__")
        subprocess.run(cmd + [str(p/"test.c"), "-o", str(exe)], check=True)
        cases = [
            (0x13B5, None, 2 if android else 0),
            (0x13B5, "0", 0),
            (0x13B5, "1", 2),
            (0x5143, None, 0),
            (0x5143, "1", 2),
        ]
        for vendor, override, expected in cases:
            env = dict(os.environ)
            env.pop("LARECOMP_VK_OPT_FS", None)
            if override is not None:
                env["LARECOMP_VK_OPT_FS"] = override
            proc = subprocess.run([str(exe), hex(vendor)], env=env, capture_output=True, text=True, check=True)
            actual = int(proc.stdout.strip())
            assert actual == expected, (android, hex(vendor), override, actual, expected)
        print(f"{'Android' if android else 'desktop'}: {len(cases)} shader optimisation policy cases passed")
print("Vertex stages remain non-optimised; shader cache flag verified")

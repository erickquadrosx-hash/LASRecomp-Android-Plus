#!/usr/bin/env python3
"""Regression guard for the Vulkan fishing-water copy-alias fix.

A static guard: the actual fishing minigame still requires an on-device test.
"""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "runtime/nvn/vulkan/exec.c"
source = p.read_text(encoding="utf-8")
draw = source.split("static void alias_draw_check(Prog *pr) {", 1)[1].split("static void resolve_feedback(", 1)[0]
compute = source.split("static void dispatch_compute(uint32_t gx, uint32_t gy, uint32_t gz) {", 1)[1].split("// ================================================================== draws", 1)[0]
assert "if (pr && (nstale || (naliases && copy_lazy())))" in draw
assert "if (nstale) alias_catch_up(t);" in draw
assert "if (aliases[k].dst == t) aliases[k].read = true;" in draw
assert draw.index("if (aliases[k].dst == t) aliases[k].read = true;") < draw.index("alias_before_write(st.rt.color[i]")
assert 'alias_before_write(t, 0, "compute image");' in compute
assert compute.index('alias_before_write(t, 0, "compute image");') < compute.index("vk_end_pass();")
print("Fishing water Vulkan alias regression guards: OK")

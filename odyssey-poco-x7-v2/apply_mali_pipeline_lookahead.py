#!/usr/bin/env python3
"""Patch B0.2 NVN/Vulkan with opt-in exact-state pipeline look-ahead on Mali.
Only changes public runtime code, never game code or proprietary binaries.
"""
import argparse
from pathlib import Path

EDITS = [
(
'typedef struct { Prog *prog[2], *gprog /* SMO: a geometry stage is bound (its draws are not followed: gs_pipe_get) */; int ncol, nattr, sig_ok, attr_new; TargetRef col[8], depth; uint32_t vattr[32], ints, sints, sig_tag; uint8_t logic; PKey sig; } Scan;',
'''typedef struct { Prog *prog[2], *gprog /* SMO: a geometry stage is bound (its draws are not followed: gs_pipe_get) */; int ncol, nattr, sig_ok, attr_new; TargetRef col[8], depth; uint32_t vattr[32], ints, sints, sig_tag; uint8_t logic; PKey sig;
    uint32_t chanmask, sample_mask;
    uint8_t poly, a2c, dclamp, blend_on, blend[8][8];
} Scan;'''
),
(
'    s->nattr = R.nattr; memcpy(s->vattr, R.vattr, sizeof s->vattr); s->attr_new = 1; s->logic = R.logic;\n    scan_sig(s);',
'''    s->nattr = R.nattr; memcpy(s->vattr, R.vattr, sizeof s->vattr); s->attr_new = 1; s->logic = R.logic;
    s->chanmask = R.chanmask; s->sample_mask = R.sample_mask;
    s->poly = R.poly[2]; s->a2c = R.ms[1] != 0;
    s->dclamp = R.depth_clamp && D.f2.features.depthClamp;
    s->blend_on = R.blend_on; memcpy(s->blend, R.blend, sizeof s->blend);
    scan_sig(s);'''
),
(
'    uint64_t w[6] = {(uint64_t)(uintptr_t)p0->st[0].code',
'''    /* Complete the exact static pipeline key before queuing compilation. */
    PKey k = s->sig;
    k.topo_class = tclass[prim]; k.logic = s->logic;
    k.sshade = p1 ? (uint8_t)p1->sample_shading : 0;
    if (!D.has_eds3) {
        k.chanmask = s->chanmask; k.sample_mask = s->sample_mask;
        k.poly = s->poly < 3 ? s->poly : 2;
        k.a2c = s->a2c; k.dclamp = s->dclamp;
        k.blend_on = s->blend_on; memcpy(k.blend, s->blend, sizeof k.blend);
    }
    uint64_t w[6] = {(uint64_t)(uintptr_t)p0->st[0].code'''
),
(
's->sig_tag, tclass[prim] | (uint64_t)s->logic << 8',
'fnv(0xcbf29ce484222325ULL, &k, sizeof k), tclass[prim] | (uint64_t)s->logic << 8'
),
(
'''    PKey k = s->sig;
    k.topo_class = tclass[prim]; k.logic = s->logic; k.sshade = p1 ? (uint8_t)p1->sample_shading : 0;
    if (vs_made && fs_made) {''',
'''    if (vs_made && fs_made) {'''
),
(
'''        case OP_COLOR: s->logic = ((const uint8_t *)&a[0])[1]; break;
        case OP_DRAW_ARRAYS: case OP_DRAW_ELEMENTS: scan_draw(s, (unsigned)a[0]); break;''',
'''        /* Track the same non-dynamic state consumed by draw_prepare. */
        case OP_BLEND: { const uint8_t *b = (const uint8_t *)&a[0]; memcpy(s->blend[b[0] & 7], b + 1, 6); break; }
        case OP_COLOR: { const uint8_t *b = (const uint8_t *)&a[0]; s->blend_on = b[0]; s->logic = b[1]; break; }
        case OP_CHANMASK: s->chanmask = (uint32_t)a[0]; break;
        case OP_MULTISAMPLE: s->a2c = ((const uint8_t *)&a[0])[1] != 0; break;
        case OP_POLYGON: s->poly = ((const uint8_t *)&a[0])[2]; break;
        case OP_SAMPLEMASK: s->sample_mask = (uint32_t)a[0]; break;
        case OP_DEPTHCLAMP: s->dclamp = (a[0] & 1) && D.f2.features.depthClamp; break;
        case OP_DRAW_ARRAYS: case OP_DRAW_ELEMENTS: scan_draw(s, (unsigned)a[0]); break;'''
),
(
'    if (!D.has_eds3 || !D.has_vids) return;        /* the key holds blend state (or the vertex layout) the look-ahead does not follow */',
'    if (!D.has_vids) return;    /* the exact blend/raster state is captured by scan_list */'
),
(
'    g_scan_on = D.has_eds3 && !(getenv("SMO_VK_LOOKAHEAD") && !atoi(getenv("SMO_VK_LOOKAHEAD")));',
'''    /* Opt-in for Mali without EDS3; only if dynamic vertex input exists. */
    const char *mali_la = getenv("SMO_VK_MALI_LOOKAHEAD");
    int mali_exact_la = V.props.vendorID == 0x13b5 && !D.has_eds3 && D.has_vids &&
                        mali_la && atoi(mali_la) != 0;
    g_scan_on = (D.has_eds3 || mali_exact_la) &&
                !(getenv("SMO_VK_LOOKAHEAD") && !atoi(getenv("SMO_VK_LOOKAHEAD")));
    if (mali_exact_la) printf("nvn_vk: Mali exact-key look-ahead enabled (SMO_VK_MALI_LOOKAHEAD=1)\\n");'''
),
]


def patch(src):
    if "Mali exact-key look-ahead enabled (SMO_VK_MALI_LOOKAHEAD=1)" in src:
        raise ValueError("already applied; refusing double patch")
    result = src
    for i, (old, new) in enumerate(EDITS, 1):
        count = result.count(old)
        if count != 1:
            raise ValueError(f"beta 0.2 mismatch at edit {i}: {count} matches; expected exactly 1")
        result = result.replace(old, new, 1)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="Root of pinned SMO Android B0.2 checkout")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    path = args.source / "runtime/nvn_vk_m4.c"
    original = path.read_text(encoding="utf8")
    updated = patch(original)
    if args.check:
        print("PASS: eight exact source anchors found in pinned upstream B0.2")
        return
    backup = path.with_suffix(".c.pipeline-original.bak")
    if not backup.exists():
        backup.write_text(original, encoding="utf8")
    path.write_text(updated, encoding="utf8")
    print("Mali look-ahead source patch applied:", path)


if __name__ == "__main__":
    main()

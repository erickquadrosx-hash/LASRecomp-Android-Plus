#!/usr/bin/env python3
"""Apply POCO X7 Pro V2 native improvements to the pinned B0.2 source checkout.

This script never handles a game dump or changes the depth-test semantics.
No native game library is created without the owner's own 1.0.0 executable.
"""
from pathlib import Path
import argparse

BC45 = r'''/* POCO X7 Pro: decode BC4/BC5 straight into R8/RG8 to avoid RGBA/float temporaries. */
static inline int bc45_snorm8(int v) {
    return v < 0 ? -((-v + 17) / 35) : (v + 17) / 35;
}
static int bc45_decode_direct(int nf, int kind, const void *src, int w, int h, void *dst) {
    const TexFormat *f = tex_format(nf);
    int channels = (kind == TEX_DEC_RG8 || kind == TEX_DEC_RG8_SNORM) ? 2 : 1;
    int snorm = kind == TEX_DEC_R8_SNORM || kind == TEX_DEC_RG8_SNORM;
    if (!src || !dst || !f || w <= 0 || h <= 0 ||
        (channels == 1 ? f->codec != TEX_CODEC_BC4 : f->codec != TEX_CODEC_BC5) ||
        (int)f->snorm != snorm) return -1;
    int wb = (w + 3) / 4, hb = (h + 3) / 4;
    const uint8_t *blocks = (const uint8_t *)src;
    uint8_t *out = (uint8_t *)dst;
    for (int by = 0; by < hb; by++) for (int bx = 0; bx < wb; bx++) {
        const uint8_t *blk = blocks + ((size_t)by * wb + bx) * f->bpb;
        int rv[16], gv[16];
        bc4_block(blk, rv, snorm);
        if (channels == 2) bc4_block(blk + 8, gv, snorm);
        for (int y = 0; y < 4 && by * 4 + y < h; y++)
            for (int x = 0; x < 4 && bx * 4 + x < w; x++) {
                int i = y * 4 + x;
                size_t off = ((size_t)(by * 4 + y) * (size_t)w + (size_t)(bx * 4 + x)) * channels;
                out[off] = (uint8_t)(snorm ? (int8_t)bc45_snorm8(rv[i]) : rv[i]);
                if (channels == 2)
                    out[off + 1] = (uint8_t)(snorm ? (int8_t)bc45_snorm8(gv[i]) : gv[i]);
            }
    }
    return 0;
}
int tex_decode_to(int nf, int kind, const void *src, int w, int h, void *dst) {
    const TexFormat *f = tex_format(nf);
    size_t n = (size_t)w * h, i;
    if (!f || !f->codec) return -1;
    if (kind == TEX_DEC_RGBA8) return tex_decode_rgba8(nf, src, w, h, (uint8_t *)dst);
    if (kind == TEX_DEC_R8 || kind == TEX_DEC_RG8 ||
        kind == TEX_DEC_R8_SNORM || kind == TEX_DEC_RG8_SNORM)
        return bc45_decode_direct(nf, kind, src, w, h, dst);
    if (kind != TEX_DEC_RGBA16F) return -1;
    float *v = malloc(n * 16);
    if (!v) return -1;
    tex_decode_rgba32f(nf, src, w, h, v);
    {   /* BC6H: unchanged precision and output */
        uint16_t *o = dst;
        for (i = 0; i < n * 4; i++) o[i] = tex_float_to_half(v[i]);
    }
    free(v);
    return 0;
}'''

def one(s, old, new, name):
    if s.count(old) != 1:
        raise ValueError(f"{name}: expected one occurrence; found {s.count(old)}")
    return s.replace(old, new, 1)

def transform(paths):
    out = {}
    p = paths / "runtime/tex_decode.c"
    s = p.read_text(encoding="utf8")
    start = s.index("int tex_decode_to(")
    end = s.index("\n}\n", start) + 3
    original = s[start:end]
    if "TEX_DEC_R8_SNORM" not in original or "float *v = malloc(n * 16)" not in original:
        raise ValueError("Unexpected BC4/5 decoder; abort")
    out[p] = s[:start] + BC45 + s[end:]

    p = paths / "runtime/nvn_gl.c"
    s = p.read_text(encoding="utf8")
    old = "if (need > tmp_cap) { tmp_cap = need * 2; tmp = realloc(tmp, tmp_cap); }"
    new = """if (need > tmp_cap) {
                size_t grown = need > (size_t)-1 / 2 ? need : need * 2;
                uint8_t *next = realloc(tmp, grown);
                if (!next) return 0;
                tmp = next; tmp_cap = grown;
            }"""
    s = one(s, old, new, p)
    old = """size_t lin = L.lvl_linear_size[l], slice_in = lin / (size_t)(L.lvl_d[l] > 0 ? L.lvl_d[l] : 1);
            size_t slice_out = decode ? (size_t)L.lvl_w[l] * L.lvl_h[l] * (size_t)tex_decode_bytes_per_texel(decode) : 0;
            size_t need = lin + slice_out * (size_t)(L.lvl_d[l] > 0 ? L.lvl_d[l] : 1);"""
    new = """size_t lin = L.lvl_linear_size[l], depth = (size_t)(L.lvl_d[l] > 0 ? L.lvl_d[l] : 1);
            size_t slice_in = lin / depth, slice_out = 0;
            if (decode) {
                int bytes = tex_decode_bytes_per_texel(decode);
                size_t w = (size_t)L.lvl_w[l], h = (size_t)L.lvl_h[l];
                if (bytes <= 0 || !w || !h || w > (size_t)-1 / h / (size_t)bytes) return 0;
                slice_out = w * h * (size_t)bytes;
            }
            if (slice_out && depth > ((size_t)-1 - lin) / slice_out) return 0;
            size_t need = lin + slice_out * depth;"""
    out[p] = one(s, old, new, p)

    p = paths / "runtime/android/android_perf.c"
    s = p.read_text(encoding="utf8")
    old = '    if ((e = getenv("SMO_PERF_TARGET_US")) && atoll(e) > 0) g_target_ns = atoll(e) * 1000;'
    new = '    g_target_ns = gfx_options()->fps30 ? 33333333 : 16666667;\n' + old
    out[p] = one(s, old, new, p)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    changes = transform(args.source)
    for path, updated in changes.items():
        original = path.read_text(encoding="utf8")
        print(f"{path}: {'patch needed' if original != updated else 'unchanged'}")
    if not args.write:
        print("Preflight only: no source modified")
        return
    for path, updated in changes.items():
        backup = path.with_suffix(path.suffix + ".x7backup")
        if not backup.exists():
            backup.write_text(path.read_text(encoding="utf8"), encoding="utf8")
        path.write_text(updated, encoding="utf8")
    print("Applied native BC4/BC5, buffer overflow/OOM and ADPF patches. Depth rules unchanged.")

if __name__ == "__main__":
    main()

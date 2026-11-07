#!/usr/bin/env python3
"""8,000 deterministic BC4/BC5 tests: real unpatched B0.2 decoder vs native V2."""
import ctypes
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "upstream"

def run():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        baseline_source = subprocess.check_output(
            ["git", "-C", str(UPSTREAM), "show", "HEAD:runtime/tex_decode.c"])
        (tmp / "original.c").write_bytes(baseline_source)
        original = tmp / "original.so"
        patched = tmp / "patched.so"
        include = str(UPSTREAM / "runtime")
        for source, target in [(tmp / "original.c", original),
                               (UPSTREAM / "runtime/tex_decode.c", patched)]:
            subprocess.run(["clang", "-std=gnu11", "-O2", "-fPIC", "-shared",
                            "-I", include, str(source), "-lm", "-o", str(target)],
                           check=True)
        libs = [ctypes.CDLL(str(original)), ctypes.CDLL(str(patched))]
        fn = []
        for library in libs:
            method = library.tex_decode_to
            method.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p,
                               ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
            method.restype = ctypes.c_int
            fn.append(method)
        rng = random.Random(20261107)
        cases = [(0x49, 2, 1), (0x4A, 3, 1), (0x4B, 4, 2), (0x4C, 5, 2)]
        for nf, kind, channels in cases:
            for case in range(2000):
                w = rng.randrange(1, 81)
                h = rng.randrange(1, 73)
                nblocks = ((w + 3) // 4) * ((h + 3) // 4)
                compressed = bytes(rng.getrandbits(8) for _ in range(nblocks * 8 * channels))
                src = ctypes.create_string_buffer(compressed)
                a = ctypes.create_string_buffer(w * h * channels)
                b = ctypes.create_string_buffer(w * h * channels)
                ra = fn[0](nf, kind, src, w, h, a)
                rb = fn[1](nf, kind, src, w, h, b)
                if ra != rb or a.raw != b.raw:
                    raise AssertionError(
                        f"BC45 mismatch format {nf:x} case {case} dimensions {w}x{h}")
        print("PASS: 8,000 real-decoder BC4/BC5 pixel-equivalence tests")

if __name__ == "__main__":
    run()

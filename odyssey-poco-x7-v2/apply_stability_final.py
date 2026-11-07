#!/usr/bin/env python3
"""Strict B0.2 stability patch. Edits public source, never the game's proprietary data."""
from pathlib import Path
import argparse

def replace_one(text, old, new):
    count = text.count(old)
    if count != 1:
        raise ValueError(f"B0.2 mismatch: expected 1, found {count} for {old[:80]!r}")
    return text.replace(old, new, 1)

def graphics(text):
    replacements = [
        ('#define DEF_SCALE "1.00"', '#define DEF_SCALE "0.75"'),
        ('#define DEF_BOOST "on"', '#define DEF_BOOST "auto"'),
        ('#define DEF_AA "fxaa"', '#define DEF_AA "off"'),
        ('#define DEF_SHARPEN "75"', '#define DEF_SHARPEN "20"'),
        ('"console_mode = docked\\r\\n"', '"console_mode = handheld\\r\\n"'),
        ('"frame_rate = 60\\r\\n"', '"frame_rate = 30\\r\\n"'),
        ('"driver = custom\\r\\n"', '"driver = system\\r\\n"'),
        ('o->present = 3; o->scale = 1.0f; o->boost = 2; o->fxaa = 1; o->sharpen = 0.75f;',
         'o->present = 3; o->scale = 0.75f; o->boost = 1; o->fxaa = 0; o->sharpen = 0.20f; o->fps30 = 1; o->handheld = 1; o->driver_system = 1;'),
    ]
    for old, new in replacements:
        text = replace_one(text, old, new)
    return text

def compiler(text):
    return replace_one(text,
        "        subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)\n        p.communicate()\n        return None, '', time.time() - t",
        "        p.kill()\n        out, _ = p.communicate()\n        return None, out.decode('latin-1')[-3000:], time.time() - t")

def run(root, write):
    for path, transform in [('runtime/gfx_options.c', graphics), ('tools/lifter/build_main.py', compiler)]:
        full = root / path
        source = full.read_text(encoding='utf8')
        changed = transform(source)
        if write: full.write_text(changed, encoding='utf8')
        print(('PATCHED' if write else 'CHECKED') + ' ' + path)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=Path)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    run(args.source, args.write and not args.check)

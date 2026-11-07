#!/usr/bin/env python3
"""Repackage official B0.2 with a freshly compiled Java DEX only.
Native libsmo.so, binary manifest, and resources remain byte-identical.
"""
from pathlib import Path
import argparse
import hashlib
import zipfile

OFFICIAL_SHA256 = "9a55846029e233521d6e8ff405a3cbc62541aff0859d25ddc5b5af4fbf07b7bb"

def repack(original, dex, unsigned):
    original, dex = Path(original), Path(dex)
    found = hashlib.sha256(original.read_bytes()).hexdigest()
    if found != OFFICIAL_SHA256:
        raise ValueError("Unexpected source APK hash: " + found)
    code = dex.read_bytes()
    if not code.startswith(b"dex\n"):
        raise ValueError("Invalid classes.dex")
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(unsigned, "w") as dst:
        for item in src.infolist():
            if item.filename.upper().startswith("META-INF/"):
                continue
            dst.writestr(item, code if item.filename == "classes.dex" else src.read(item.filename))
        assert "classes.dex" in src.namelist()
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(unsigned) as dst:
        for name in ("lib/arm64-v8a/libsmo.so", "AndroidManifest.xml", "resources.arsc"):
            assert src.read(name) == dst.read(name), "Binary changed: " + name
        assert dst.testzip() is None
    print("Repacked APK: Java DEX replaced, original native render library UNMODIFIED")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True)
    p.add_argument("--dex",required=True)
    p.add_argument("--unsigned",required=True)
    a=p.parse_args()
    repack(a.original,a.dex,a.unsigned)

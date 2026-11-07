#!/usr/bin/env python3
"""Crash-safe Odyssey repacker. Input APK and signing key stay local; never push them."""
import argparse
import os
import pathlib
import shutil
import subprocess
import tempfile
import zipfile
import hashlib

OLD = "com.mobileodyssey.game"
NEW = "com.mobileodyssey.x7pr"
assert len(OLD) == len(NEW)


def bump_version_code(manifest: bytes) -> bytes:
    """Use versionCode 2 to avoid same-version update ambiguity on Android 16."""
    import struct
    if manifest[:4] != b'\x03\x00\x08\x00':
        return manifest  # synthetic test fixture, not Android binary XML
    buf = bytearray(manifest)
    strings = []
    offset = 8
    while offset < len(buf):
        typ, head, size = struct.unpack_from('<HHI', buf, offset)
        if size < head or size == 0:
            raise ValueError('Invalid Android manifest chunk')
        if typ == 1:
            count = struct.unpack_from('<I', buf, offset + 8)[0]
            flags = struct.unpack_from('<I', buf, offset + 16)[0]
            start = struct.unpack_from('<I', buf, offset + 20)[0]
            if flags & 0x100:
                raise ValueError('Unexpected UTF-8 string pool')
            for i in range(count):
                pos = offset + start + struct.unpack_from('<I', buf, offset + head + i*4)[0]
                n = struct.unpack_from('<H', buf, pos)[0]
                if n & 0x8000:
                    raise ValueError('Long AXML string not supported')
                strings.append(buf[pos+2:pos+2+n*2].decode('utf-16le'))
        elif typ == 0x102 and strings:
            element_idx = struct.unpack_from('<I', buf, offset + 20)[0]
            if strings[element_idx] == 'manifest':
                start, step, count = struct.unpack_from('<HHH', buf, offset + 24)
                found = 0
                for i in range(count):
                    pos = offset + 16 + start + i*step
                    name = strings[struct.unpack_from('<I', buf, pos + 4)[0]]
                    if name == 'versionCode':
                        if buf[pos+15] != 0x10 or struct.unpack_from('<I', buf, pos+16)[0] != 1:
                            raise ValueError('Expected versionCode 1')
                        struct.pack_into('<I', buf, pos+16, 2)
                        found += 1
                if found != 1:
                    raise ValueError('versionCode missing or duplicated')
                return bytes(buf)
        offset += size
    raise ValueError('Android manifest root missing')

def patch_apk(original, unsigned):
    changes = set()
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(unsigned, "w") as target:
        for item in source.infolist():
            if item.filename.upper().startswith("META-INF/"):
                continue
            data = source.read(item.filename)
            if item.filename == "AndroidManifest.xml":
                before, after = (OLD + "\0").encode("utf-16le"), (NEW + "\0").encode("utf-16le")
            elif item.filename == "resources.arsc":
                before, after = OLD.encode("utf-16le"), NEW.encode("utf-16le")
            elif item.filename == "lib/arm64-v8a/libsmo.so":
                before, after = OLD.encode("ascii"), NEW.encode("ascii")
            else:
                target.writestr(item, data)
                continue
            if data.count(before) != 1:
                raise RuntimeError(f"Unexpected package bytes in {item.filename}")
            patched = data.replace(before, after)
            if item.filename == "AndroidManifest.xml":
                patched = bump_version_code(patched)
            target.writestr(item, patched)
            changes.add(item.filename)
    expected = {"AndroidManifest.xml", "resources.arsc", "lib/arm64-v8a/libsmo.so"}
    if changes != expected:
        raise RuntimeError(f"Unexpected patch set: {changes}")
    with zipfile.ZipFile(original) as a, zipfile.ZipFile(unsigned) as b:
        if a.read("classes.dex") != b.read("classes.dex") or b.testzip():
            raise RuntimeError("DEX preservation or ZIP CRC check failed")

def build(args):
    for tool in ("zipalign", "apksigner"):
        if not shutil.which(tool):
            raise RuntimeError(f"Android SDK Build Tools required: {tool}")
    password = os.environ.get("ODYSSEY_KS_PASS")
    if not password:
        raise RuntimeError("Set ODYSSEY_KS_PASS; signing key is never committed to GitHub")
    with tempfile.TemporaryDirectory() as temp:
        unsigned = pathlib.Path(temp) / "unsigned.apk"
        aligned = pathlib.Path(temp) / "aligned.apk"
        patch_apk(pathlib.Path(args.input), unsigned)
        subprocess.run(["zipalign", "-f", "-P", "16", "4", str(unsigned), str(aligned)], check=True)
        subprocess.run([
            "apksigner", "sign", "--ks", args.keystore,
            "--ks-key-alias", args.alias, "--ks-pass", "env:ODYSSEY_KS_PASS",
            "--key-pass", "env:ODYSSEY_KS_PASS", "--out", args.output, str(aligned)
        ], check=True)
        subprocess.run(["apksigner", "verify", "--verbose", args.output], check=True)
    with zipfile.ZipFile(args.input) as a, zipfile.ZipFile(args.output) as b:
        if a.read("classes.dex") != b.read("classes.dex"):
            raise RuntimeError("DEX was not preserved")
    print("Repacked; SHA256:", hashlib.sha256(pathlib.Path(args.output).read_bytes()).hexdigest())
    print("Physical Android startup and FPS are not yet validated.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Your original, owned APK")
    p.add_argument("--output", required=True)
    p.add_argument("--keystore", required=True)
    p.add_argument("--alias", default="poco_x7")
    build(p.parse_args())

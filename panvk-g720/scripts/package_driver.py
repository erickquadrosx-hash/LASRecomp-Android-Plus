#!/usr/bin/env python3
"""Fail closed: only zip a genuine Android ARM64 ELF with >=16KiB PT_LOAD alignment."""
import hashlib, json, struct, sys, zipfile
from pathlib import Path
if len(sys.argv) != 3:
    raise SystemExit("usage: package_driver.py <real .so> <output.zip>")
b = Path(sys.argv[1]).read_bytes()
if len(b) < 65536 or b[:4] != b"\x7fELF" or b[4] != 2 or b[5] != 1:
    raise SystemExit("NOT A 64-bit ELF library")
if struct.unpack_from("<H",b,16)[0] != 3 or struct.unpack_from("<H",b,18)[0] != 183:
    raise SystemExit("NOT an AArch64 ELF shared object")
off=struct.unpack_from("<Q",b,32)[0]
entsize=struct.unpack_from("<H",b,54)[0]
count=struct.unpack_from("<H",b,56)[0]
align=[]
for i in range(count):
    p=off+i*entsize
    if p+56>len(b):raise SystemExit("invalid ELF program header")
    if struct.unpack_from("<I",b,p)[0]==1:
        align.append(struct.unpack_from("<Q",b,p+48)[0])
if not align or min(align)<16384:
    raise SystemExit("ELF is not 16KiB-page compatible: "+str(align))
meta={"name":"Mesa PanVK G720 AHB experimental (unverified)","driverVersion":"26.3.1 AHB compatibility test 2026-11-02","libraryName":"libvulkan_panfrost.so"}
dest=Path(sys.argv[2])
info={"build_sha256":hashlib.sha256(b).hexdigest(),"size":len(b),"load_alignment":align,"tested_on_poco":False}
with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("meta.json",json.dumps(meta,indent=2))
    z.writestr("libvulkan_panfrost.so",b)
    z.writestr("VALIDATION.json",json.dumps(info,indent=2))
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    assert json.loads(z.read("meta.json"))["libraryName"] in z.namelist()
print("PACKAGED but not device-tested:",dest,info)

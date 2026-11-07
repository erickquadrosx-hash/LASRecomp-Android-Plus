#!/usr/bin/env python3
"""Local-only complete source-to-APK build using the owner's own Odyssey 1.0.0 ELF files.

Never commits, uploads or prints game code or prod.keys. Run on Windows or Linux
with Python 3, Android SDK 35, NDK 28.2.13676358 and required Python packages.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "upstream"

def call(cmd, env):
    print("Running:", " ".join(str(s) for s in cmd[:3]), "...")
    subprocess.run([str(s) for s in cmd], cwd=UPSTREAM, env=env, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owned-elf-dir", required=True, type=Path,
                    help="Local directory containing main.elf, sdk.elf, subsdk0.elf (your own 1.0.0 dump)")
    ap.add_argument("--owned-exefs-dir", type=Path,
                    help="Optional ExeFS data from your own game extraction; never uploaded")
    ap.add_argument("--jobs", default="6", type=str)
    ap.add_argument("--skip-shaderc", action="store_true",
                    help="Already built ~/smo-shaderc for NDK 28")
    args = ap.parse_args()
    if not (UPSTREAM / "tools/android/build_runtime.py").exists():
        sys.exit("Missing source submodule. Run: git submodule update --init --recursive")
    incoming = args.owned_elf_dir.expanduser().resolve()
    required = ["main.elf", "sdk.elf"]
    missing = [f for f in required if not (incoming / f).is_file()]
    if missing:
        sys.exit("Missing OWN game ELF files: " + ", ".join(missing))
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk or not (Path(sdk) / "platforms/android-35/android.jar").exists():
        sys.exit("Configure ANDROID_HOME with Android SDK platform 35")
    ndk = os.environ.get("ANDROID_NDK")
    if not ndk or not (Path(ndk) / "ndk-build").exists() and not (Path(ndk) / "ndk-build.cmd").exists():
        sys.exit("Configure ANDROID_NDK with NDK 28.2.13676358")
    env = dict(os.environ, SMO_LAYOUT="android")
    # All copied executable data stays in a local ignored build/ folder.
    out = UPSTREAM / "build/dump/base/elf"
    out.mkdir(parents=True, exist_ok=True)
    for file in incoming.glob("*.elf"):
        shutil.copy2(file, out / file.name)
    if args.owned_exefs_dir:
        exefs = args.owned_exefs_dir.expanduser().resolve()
        if not exefs.is_dir(): sys.exit("Missing own ExeFS directory")
        dest = UPSTREAM / "build/dump/base/exefs"
        dest.mkdir(parents=True, exist_ok=True)
        for file in exefs.iterdir():
            if file.is_file(): shutil.copy2(file, dest / file.name)
    # Fails closed if source changes, before any game object compilation.
    call([sys.executable, ROOT / "apply_native_v2.py", UPSTREAM, "--write"], env)
    call([sys.executable, "tools/extract/functions.py"], env)
    call([sys.executable, "tools/lifter/recomp.py", "full"], env)
    call([sys.executable, "tools/lifter/gen_tables.py"], env)
    call([sys.executable, "tools/lifter/gen_sdktest.py"], env)
    call([sys.executable, "tools/lifter/sdklift.py", "gen"], env)
    if not args.skip_shaderc:
        call([sys.executable, "tools/android/build_shaderc.py"], env)
    call([sys.executable, "tools/android/build_game.py", args.jobs, "--abi", "arm64-v8a"], env)
    call([sys.executable, "tools/android/build_runtime.py", "--abi", "arm64-v8a"], env)
    call([sys.executable, "tools/android/build_apk.py", "--abi", "arm64-v8a"], env)
    result = UPSTREAM / "build/android/smo-arm64-v8a.apk"
    print("Build complete:", result, "exists:", result.is_file())
    if not result.is_file():
        raise SystemExit("Build returned without an APK")

if __name__ == "__main__":
    main()

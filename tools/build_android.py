#!/usr/bin/env python3
"""Build the Android app: dist/arthurs-arena.apk

    python3 tools/build_android.py            # package the game, then build the APK
    python3 tools/build_android.py --skip-html   # reuse dist/arthurs-arena.html

What it does:

1. tools/package_html.js turns projects/arthurs-arena-legends.sb3 into one
   offline HTML file (TurboWarp packager): dist/arthurs-arena.html.
2. aapt2 packs android/AndroidManifest.xml, the icon and that HTML file.
3. smali turns android/smali/.../MainActivity.smali into classes.dex.
   The app is a single full-screen WebView, so no Android SDK is needed.
4. apksig signs it with android/debug.keystore (v2 signature, Android 7+).

The tools come from Maven Central the first time and are cached in
~/.cache/arthurs-arena-android (or $ARENA_TOOLS):
  aapt2 and the Android framework file from org.apktool:apktool-lib,
  org.smali:smali and its libraries, com.android.tools.build:apksig.
Needs java, javac, node, and @turbowarp/packager on NODE_PATH.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android"
BUILD = ROOT / "build" / "android"
DIST = ROOT / "dist"
HTML = DIST / "arthurs-arena.html"
APK = DIST / "arthurs-arena.apk"
TOOLS = Path(os.environ.get("ARENA_TOOLS", Path.home() / ".cache" / "arthurs-arena-android"))

VERSION_CODE = 4
VERSION_NAME = "1.3"
MIN_SDK = 24  # Android 7.0 and newer
TARGET_SDK = 34

# A debug key, committed on purpose so every build can update the app that is
# already installed (and keep the saved Best score). Fine for installing at
# home; make a private key before putting the game on the Play Store.
KEYSTORE = ANDROID / "debug.keystore"
KEY_PASS = "arthursarena"
KEY_ALIAS = "arena"

CENTRAL = "https://repo1.maven.org/maven2/"
JARS = {
    "apktool-lib.jar": "org/apktool/apktool-lib/3.0.3/apktool-lib-3.0.3.jar",
    "apksig.jar": "com/android/tools/build/apksig/2.3.0/apksig-2.3.0.jar",
    "smali.jar": "org/smali/smali/2.5.2/smali-2.5.2.jar",
    "dexlib2.jar": "org/smali/dexlib2/2.5.2/dexlib2-2.5.2.jar",
    "smali-util.jar": "org/smali/util/2.5.2/util-2.5.2.jar",
    "antlr-runtime.jar": "org/antlr/antlr-runtime/3.5.2/antlr-runtime-3.5.2.jar",
    "antlr3.jar": "org/antlr/antlr/3.5.2/antlr-3.5.2.jar",
    "antlr2.jar": "antlr/antlr/2.7.7/antlr-2.7.7.jar",
    "stringtemplate.jar": "org/antlr/stringtemplate/3.2.1/stringtemplate-3.2.1.jar",
    "st4.jar": "org/antlr/ST4/4.0.8/ST4-4.0.8.jar",
    "guava.jar": "com/google/guava/guava/27.1-android/guava-27.1-android.jar",
    "failureaccess.jar": "com/google/guava/failureaccess/1.0.1/failureaccess-1.0.1.jar",
    "jcommander.jar": "com/beust/jcommander/1.64/jcommander-1.64.jar",
    "jsr305.jar": "com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar",
}


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:160])
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def fetch_tools():
    TOOLS.mkdir(parents=True, exist_ok=True)
    for name, path in JARS.items():
        target = TOOLS / name
        if target.exists():
            continue
        for attempt in range(5):
            try:
                print(f"  downloading {path.split('/')[-1]}")
                with urllib.request.urlopen(CENTRAL + path, timeout=120) as r:
                    target.write_bytes(r.read())
                break
            except Exception as e:  # Maven Central rate-limits now and then
                if attempt == 4:
                    raise SystemExit(f"could not download {path}: {e}")
                time.sleep(2 ** attempt)
    aapt2 = TOOLS / "aapt2"
    framework = TOOLS / "android-framework.jar"
    if not aapt2.exists() or not framework.exists():
        with zipfile.ZipFile(TOOLS / "apktool-lib.jar") as z:
            aapt2.write_bytes(z.read("prebuilt/linux/aapt2"))
            framework.write_bytes(z.read("prebuilt/android-framework.jar"))
        aapt2.chmod(0o755)
    return aapt2, framework


def ensure_keystore():
    if KEYSTORE.exists():
        return
    run(["keytool", "-genkeypair", "-keystore", KEYSTORE, "-storetype", "PKCS12", "-storepass", KEY_PASS,
         "-keypass", KEY_PASS, "-alias", KEY_ALIAS, "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
         "-dname", "CN=Arthur's Arena debug, O=arthurs-arena"])


def aligned_copy(src: Path, dst: Path, extra: dict[str, bytes]):
    """Rewrite the zip so stored files start on 4-byte boundaries (zipalign)."""
    with zipfile.ZipFile(src) as zin, open(dst, "wb") as raw:
        zout = zipfile.ZipFile(raw, "w")
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
        items += [(zipfile.ZipInfo(name, (2026, 11, 5, 0, 0, 0)), data) for name, data in extra.items()]
        for info, data in items:
            new = zipfile.ZipInfo(info.filename, info.date_time)
            stored = info.filename == "resources.arsc" or info.filename.endswith(".png") or (
                info.compress_type == zipfile.ZIP_STORED and info.filename not in extra)
            new.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
            new.external_attr = info.external_attr
            if stored:
                header = 30 + len(new.filename.encode())
                pad = (4 - (raw.tell() + header) % 4) % 4
                new.extra = b"\0" * pad
            zout.writestr(new, data)
        zout.close()


def check_alignment(apk: Path):
    with zipfile.ZipFile(apk) as z, open(apk, "rb") as f:
        for i in z.infolist():
            if i.compress_type != zipfile.ZIP_STORED:
                continue
            f.seek(i.header_offset + 26)
            n, m = int.from_bytes(f.read(2), "little"), int.from_bytes(f.read(2), "little")
            start = i.header_offset + 30 + n + m
            if start % 4:
                raise SystemExit(f"{i.filename} is not 4-byte aligned")


def main():
    skip_html = "--skip-html" in sys.argv
    print("1. game page")
    if not skip_html or not HTML.exists():
        run(["node", ROOT / "tools" / "package_html.js", HTML])
    print("2. tools")
    aapt2, framework = fetch_tools()
    ensure_keystore()

    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "assets").mkdir(parents=True)
    shutil.copy(HTML, BUILD / "assets" / "index.html")

    print("3. manifest, icon and game page (aapt2)")
    run([aapt2, "compile", "--dir", ANDROID / "res", "-o", BUILD / "res.zip"])
    run([aapt2, "link", "-o", BUILD / "base.apk", "-I", framework, "--manifest", ANDROID / "AndroidManifest.xml",
         "-A", BUILD / "assets", "--min-sdk-version", MIN_SDK, "--target-sdk-version", TARGET_SDK,
         "--version-code", VERSION_CODE, "--version-name", VERSION_NAME, "-0", "html", BUILD / "res.zip"])

    print("4. app code (smali)")
    cp = os.pathsep.join(str(TOOLS / j) for j in JARS if j not in ("apktool-lib.jar", "apksig.jar"))
    run(["java", "-cp", cp, "org.jf.smali.Main", "assemble", "--api", MIN_SDK, "-o", BUILD / "classes.dex",
         ANDROID / "smali"])

    print("5. align and sign")
    aligned_copy(BUILD / "base.apk", BUILD / "unsigned.apk", {"classes.dex": (BUILD / "classes.dex").read_bytes()})
    run(["javac", "-cp", TOOLS / "apksig.jar", "-d", BUILD, ANDROID / "signer" / "ApkSign.java"])
    DIST.mkdir(exist_ok=True)
    # apksig 2.3.0 touches a JDK-internal class even for v2; allow it on new Java.
    run(["java", "--add-exports=java.base/sun.security.x509=ALL-UNNAMED",
         "-cp", os.pathsep.join([str(TOOLS / "apksig.jar"), str(BUILD)]), "ApkSign",
         BUILD / "unsigned.apk", APK, KEYSTORE, KEY_PASS, KEY_ALIAS])
    check_alignment(APK)
    print(f"wrote {APK.relative_to(ROOT)} ({APK.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

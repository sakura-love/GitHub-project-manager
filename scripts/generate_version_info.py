#!/usr/bin/env python3
"""CI 构建时从 git tag 读取版本号，生成 version_info.txt 供 PyInstaller 使用。"""
import argparse, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "version_info.txt"

def get_version():
    ref = os.environ.get("GITHUB_REF", "")
    if ref.startswith("refs/tags/"):
        return ref[len("refs/tags/"):].lstrip("v")
    try:
        r = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True, cwd=ROOT)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().lstrip("v")
    except: pass
    return "0.0.0"

def parse(v):
    return tuple(int(p) if p.isdigit() else 0 for p in (v.split(".") + ["0","0","0","0"])[:4])

def generate(version):
    v = parse(version)
    return f"""# 此文件由 scripts/generate_version_info.py 自动生成，请勿手动编辑。
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v},
    prodvers={v},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [
          StringStruct(u'CompanyName', u'sakura-love'),
          StringStruct(u'FileDescription', u'GitHub Project Manager'),
          StringStruct(u'FileVersion', u'{version}'),
          StringStruct(u'InternalName', u'GitHubProjectManager'),
          StringStruct(u'LegalCopyright', u'Copyright (c) 2026 sakura-love'),
          StringStruct(u'OriginalFilename', u'GitHubProjectManager.exe'),
          StringStruct(u'ProductName', u'GitHub Project Manager'),
          StringStruct(u'ProductVersion', u'{version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--print", action="store_true")
    args = a.parse_args()
    version = get_version()
    content = generate(version)
    if args.print:
        print(content)
    else:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"version_info.txt generated (v{version})")

if __name__ == "__main__":
    main()

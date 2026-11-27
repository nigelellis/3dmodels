"""Snapshot the current revision into revisions/rev<REVISION>/ before starting the next one.

    python3 tools/archive_revision.py          # archive the current REVISION
    python3 tools/archive_revision.py --force  # overwrite an existing archive of it

Copies lonewolf_head.py, README.md, models/ and renders/ so each printed revision
keeps its own STL/STEP files and pictures. Afterwards, bump REVISION in
lonewolf_head.py, make the changes, and run tools/build_all.py.
"""
import os, sys, shutil, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

src = open("lonewolf_head.py").read()
m = re.search(r"^REVISION\s*=\s*(\d+)", src, re.M)
if not m:
    sys.exit("REVISION not found in lonewolf_head.py")
rev = int(m.group(1))
dest = os.path.join("revisions", f"rev{rev}")

if os.path.exists(dest) and "--force" not in sys.argv:
    sys.exit(f"{dest} already exists. Bump REVISION for a new revision, or pass --force to overwrite it.")

os.makedirs(dest, exist_ok=True)
for f in ("lonewolf_head.py", "README.md"):
    shutil.copy2(f, os.path.join(dest, f))
for d in ("models", "renders"):
    shutil.copytree(d, os.path.join(dest, d), dirs_exist_ok=True)

n = sum(len(files) for _, _, files in os.walk(dest))
size = sum(os.path.getsize(os.path.join(p, f)) for p, _, fs in os.walk(dest) for f in fs) / 1e6
print(f"archived revision {rev} -> {dest} ({n} files, {size:.1f} MB)")
print(f"next: set REVISION = {rev + 1} in lonewolf_head.py, make the changes, then run tools/build_all.py")

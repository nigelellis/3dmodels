"""Regenerate every model and render for the project.

    python3 tools/build_all.py            # models + sheets + diagrams
    python3 tools/build_all.py --video    # also the +5 mm turntable MP4 (needs ffmpeg)

Versions built: see EXTENSIONS below.
"""
import os, sys, subprocess, shutil, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTENSIONS = [0, 3, 5]
PY = sys.executable


def run(*args):
    print("->", " ".join(args), flush=True)
    subprocess.run([PY, *args], cwd=ROOT, check=True)


for e in EXTENSIONS:
    run("lonewolf_head.py", str(e))
for tool in ("diagram.py", "variants.py", "contact.py", "overlay_front.py", "overlay_revision.py", "render_detail.py"):
    run(os.path.join("tools", tool))

if "--video" in sys.argv:
    run(os.path.join("tools", "turntable.py"), "5")
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30",
                        "-i", "build/frames/f%03d.png", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        "renders/lonewolf_head_turntable.mp4"], cwd=ROOT, check=True)
        print("-> renders/lonewolf_head_turntable.mp4")
    else:
        print("ffmpeg not found: frames are in build/frames/")
print("done")

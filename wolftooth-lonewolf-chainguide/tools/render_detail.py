import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont
EXT = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0      # which version to show
m = trimesh.load(f"models/lonewolf_head_ext{EXT:g}mm.stl")
def rot(yaw, pitch):
    a, b = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    return Rx @ Rz
def view(yaw, pitch, size=700, title=""):
    R = rot(yaw, pitch); V = m.vertices @ R.T; N = m.face_normals @ R.T
    # fit the projected part into the cell (below the title), same margins for every version
    lo, hi = V.min(0), V.max(0); c = (lo + hi) / 2
    s = min((size * 0.86) / (hi[0] - lo[0]), (size * 0.80) / (hi[2] - lo[2]))
    uv = np.c_[(V[:, 0] - c[0]) * s + size / 2, -(V[:, 2] - c[2]) * s + size / 2 + 22]
    img = Image.new("RGB", (size, size), "white"); d = ImageDraw.Draw(img)
    L1 = np.array([-0.4, -1, 0.6]); L1 /= np.linalg.norm(L1); L2 = np.array([0.6, -0.5, -0.2]); L2 /= np.linalg.norm(L2)
    depth = V[m.faces][:, :, 1].mean(1)
    for f in np.argsort(-depth):
        if N[f, 1] > 0: continue
        sh = 0.22 + 0.62 * max(0, N[f] @ L1) + 0.22 * max(0, N[f] @ L2)
        k = min(1, sh); col = (int(255 * k * .52), int(255 * k * .53), int(255 * k * .58))
        d.polygon([tuple(q) for q in uv[m.faces[f]]], fill=col)
    try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except: font = ImageFont.load_default()
    d.text((14, 10), title, fill=(160, 0, 0), font=font)
    return img
views = [view(-25, 18, title="Front 3/4 — chamfers on fin edge, bottom, steep side"),
         view(20, -35, title="From below — bottom chamfer"),
         view(-90, 5, title="Fin side"),
         view(150, 20, title="Back face (against arm)")]
out = Image.new("RGB", (1400, 1400), "white")
for i, im in enumerate(views): out.paste(im, ((i % 2) * 700, (i // 2) * 700))
out.save("renders/render_detail_views.png")

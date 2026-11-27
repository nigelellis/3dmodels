import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import numpy as np, trimesh
from render_mesh import render_mesh
from PIL import Image, ImageDraw, ImageFont
EXTS = [0, 3, 5]
CW, CH, SS = 520, 520, 2          # cell size, supersample
SCALE = 10.0                      # px per mm (same for every cell)
try:
    F = lambda s, b=True: ImageFont.truetype("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf", s)
    title, big, mid, small = F(44), F(34), F(24, False), F(20, False)
except Exception:
    title = big = mid = small = ImageFont.load_default()
key = np.array([-0.45, -0.75, 0.5]); key /= np.linalg.norm(key)
rim = np.array([0.7, 0.3, 0.4]); rim /= np.linalg.norm(rim)
h = key + np.array([0, -1, 0]); h /= np.linalg.norm(h)

def render(m, yaw, pitch, anchor):
    """Shaded render; model anchored at its hole centre (0,0,0) so sizes line up."""
    W, Hh = CW * SS, CH * SS
    yaw, pitch = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
    R = Rx @ Rz
    V = (m.vertices - [0, 7.0, 0]) @ R.T
    FN = m.face_normals.copy()
    try:
        VN = trimesh.geometry.mean_vertex_normals(len(m.vertices), m.faces, m.face_normals)
        sm = VN[m.faces].mean(1); sm /= np.linalg.norm(sm, axis=1)[:, None]
        ok = (sm * FN).sum(1) > np.cos(np.radians(12))   # only smooth where nearly flat-continuous
        FN[ok] = sm[ok]
    except Exception:
        pass
    N = FN @ R.T; TN = m.face_normals @ R.T
    s = SCALE * SS
    uv = np.c_[V[:, 0] * s + anchor[0] * SS, -V[:, 2] * s + anchor[1] * SS]
    img = Image.new("RGB", (W, Hh), (255, 255, 255)); d = ImageDraw.Draw(img)
    depth = V[m.faces][:, :, 1].mean(1)
    for f in np.argsort(-depth):
        if TN[f, 1] > 0.05: continue
        n = N[f]
        k = min(1.0, 0.18 + 0.72 * max(0, n @ key) + 0.22 * max(0, n @ rim))
        sp = max(0, n @ h) ** 40 * 0.45
        d.polygon([tuple(q) for q in uv[m.faces[f]]],
                  fill=tuple(int(min(255, 255 * (k * c + sp))) for c in (0.36, 0.37, 0.41)))
    return img.resize((CW, CH), Image.LANCZOS)

import lonewolf_head as L
TC = np.array([np.cos(np.radians(L.CHAIN_ANGLE)), np.sin(np.radians(L.CHAIN_ANGLE))])
NCH = np.array([TC[1], -TC[0]]); NCH = -NCH if NCH[1] > 0 else NCH
YB = L.TOTAL_DEPTH - L.SKIRT_DEPTH / 2
def lead(e):
    m = trimesh.load(f"models/lonewolf_head_ext{e}mm.stl")
    return max((q[:, [0, 2]] @ NCH).max() for q in m.section(plane_origin=[0, YB, 0], plane_normal=[0, 1, 0]).discrete)
CHN = lead(0) + L.CHAIN_GAP_STOCK
GAPS = {e: CHN - lead(e) for e in EXTS}
cols = []
for e in EXTS:
    m = trimesh.load(render_mesh(e))
    b = m.bounds; w, hgt = b[1, 0] - b[0, 0], b[1, 2] - b[0, 2]
    a = render(m, -28, 20, (CW * 0.54, CH * 0.38))
    f = render(m, 0, 0, (CW * 0.58, CH * 0.33))
    cols.append((e, a, f, w, hgt, -b[0, 2]))

PAD, HEAD = 20, 150
sheet = Image.new("RGB", (len(EXTS) * CW + 2 * PAD, HEAD + 2 * CH + 150), "white")
d = ImageDraw.Draw(sheet)
d.text((PAD + 10, 22), "Wolf Tooth LoneWolf head — extension options", fill=(30, 30, 40), font=title)
d.text((PAD + 12, 82), "Same scale in every cell · 14.07 mm thick (9.31 pad + 4.76 base) · oval hole 10.21 × 11.6 mm · "
       "2.2 mm chamfers · 1 mm rounded square edges, 0.5 mm hole rims", fill=(95, 95, 105), font=small)
for i, (e, a, f, w, hgt, hb) in enumerate(cols):
    x = PAD + i * CW
    sheet.paste(a, (x, HEAD)); sheet.paste(f, (x, HEAD + CH))
    lab = "0 mm · stock" if e == 0 else f"+{e} mm"
    col = (30, 30, 40) if e == 0 else (25, 90, 190)
    tw = d.textlength(lab, font=big); d.text((x + (CW - tw) / 2, HEAD + 6), lab, fill=col, font=big)
    info = f"{w:.1f} wide × {hgt:.1f} tall"
    tw = d.textlength(info, font=mid); d.text((x + (CW - tw) / 2, HEAD + 2 * CH + 14), info, fill=(60, 60, 70), font=mid)
    info2 = f"gap to chain ≈ {GAPS[e]:.1f} mm"
    tw = d.textlength(info2, font=small); d.text((x + (CW - tw) / 2, HEAD + 2 * CH + 48), info2, fill=(110, 110, 120), font=small)
    if i: d.line([(x, HEAD + 10), (x, HEAD + 2 * CH + 80)], fill=(225, 225, 230), width=2)
d.text((PAD + 10, HEAD + CH - 30), "3/4 view", fill=(150, 150, 160), font=small)
d.text((PAD + 10, HEAD + 2 * CH - 30), "front view (looking down the hole)", fill=(150, 150, 160), font=small)
# 10 mm scale bar
bx, by = sheet.width - PAD - 10 * SCALE - 110, sheet.height - 30
d.line([(bx, by), (bx + 10 * SCALE, by)], fill=(30, 30, 30), width=5)
d.text((bx + 10 * SCALE + 10, by - 14), "10 mm", fill=(30, 30, 30), font=small)
sheet.save("renders/lonewolf_contact_sheet.png")
print(sheet.size)

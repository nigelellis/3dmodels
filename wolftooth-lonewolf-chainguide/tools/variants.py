import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import json, numpy as np, trimesh, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import lonewolf_head as L
YB = L.TOTAL_DEPTH - L.SKIRT_DEPTH / 2   # section through the base plate
TC = np.array([np.cos(np.radians(L.CHAIN_ANGLE)), np.sin(np.radians(L.CHAIN_ANGLE))])
NCH = np.array([TC[1], -TC[0]]); NCH = -NCH if NCH[1] > 0 else NCH
CHAIN_D = None
EXTS = [0, 3, 5]; NC = len(EXTS)
m0 = trimesh.load("models/lonewolf_head_ext0mm.stl")
CHAIN_D = None
def sec(m, o, n, ix, iy):
    s = m.section(plane_origin=o, plane_normal=n); return [e[:, [ix, iy]] for e in s.discrete]
CHAIN_D = max((q @ NCH).max() for q in sec(m0, [0, YB, 0], [0, 1, 0], 0, 2)) + L.CHAIN_GAP_STOCK
BLUE, ORG, PUR, RED, GRY = "#1f5fbf", "#e65100", "#6a1b9a", "#c62828", "#9e9e9e"
def dim(ax, a, b, txt, c, off=(0, 0), ha="center", va="center", rot=0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="<|-|>", mutation_scale=10, color=c, lw=1.3))
    m = (np.array(a) + np.array(b)) / 2
    ax.text(m[0] + off[0], m[1] + off[1], txt, color=c, fontsize=9.5, fontweight="bold", ha=ha, va=va, rotation=rot)

fig = plt.figure(figsize=(17, 15))
hc = np.array(L.HOLE_CENTRE); T, Sk = L.TOTAL_DEPTH, L.SKIRT_DEPTH
b0 = m0.bounds
for i, e in enumerate(EXTS):
    m = trimesh.load(f"models/lonewolf_head_ext{e}mm.stl"); b = m.bounds
    # --- 3D view
    ax = fig.add_subplot(3, NC, i + 1, projection="3d")
    V = m.vertices.copy(); Lt = np.array([0.35, -0.75, 0.55]); Lt /= np.linalg.norm(Lt)
    sh = 0.2 + 0.75 * np.clip(m.face_normals @ Lt, 0, 1)
    ax.add_collection3d(Poly3DCollection(V[m.faces], facecolors=[(s*.42, s*.42, s*.47) for s in sh], edgecolor="none"))
    ax.set_xlim(-20, 14); ax.set_ylim(-12, 22); ax.set_zlim(-26, 8); ax.set_box_aspect((1, 1, 1))
    ax.view_init(22, -62); ax.axis("off")
    ax.set_title("0 mm — stock" if e == 0 else f"+{e} mm extension", fontsize=15, fontweight="bold", color=BLUE)
    # --- front view
    ax = fig.add_subplot(3, NC, i + 1 + NC)
    for c in sec(m0, [0, YB, 0], [0, 1, 0], 0, 2): ax.plot(*c.T, color=GRY, ls="--", lw=1.1)
    for c in sec(m, [0, YB, 0], [0, 1, 0], 0, 2): ax.fill(*c.T, color="#e8eaf0"); ax.plot(*c.T, "k", lw=1.6)
    for c in sec(m, [0, 2, 0], [0, 1, 0], 0, 2): ax.plot(*c.T, color="#37474f", lw=1.2)
    xr = b[1, 0] + 2
    dim(ax, (xr, b[0, 2]), (xr, b[1, 2]), f"{b[1,2]-b[0,2]:.1f}", "k", (0.6, 0), "left")
    if e: dim(ax, (xr + 6, b0[0, 2]), (xr + 6, b[0, 2]), f"+{e}", ORG, (0.6, 0), "left")
    ax.plot([b[1, 0], xr + 7], [b0[0, 2]] * 2, color=GRY, lw=0.7, ls=":")
    zb = b[0, 2] - 2
    dim(ax, (b[0, 0], zb), (b[1, 0], zb), f"{b[1,0]-b[0,0]:.1f}", "k", (0, -1.2))
    # hole centre to lowest point
    dim(ax, (hc[0] - 9.5, hc[1]), (hc[0] - 9.5, b[0, 2]), "", PUR)
    ax.text(hc[0] - 10.3, (hc[1] + b[0, 2]) / 2, f"hole ctr\nto bottom\n{hc[1]-b[0,2]:.1f}", color=PUR,
            fontsize=8.5, ha="right", va="center", fontweight="bold")
    ax.plot([hc[0] - 10.5, hc[0]], [hc[1]] * 2, color=PUR, lw=0.6, ls=":")
    ax.plot(*hc, "+", color=RED, ms=9)
    c0 = CHAIN_D * NCH; ax.plot(*np.c_[c0 - 26 * TC, c0 + 26 * TC], color="#7b1fa2", lw=3, alpha=0.75, zorder=0)
    gap = CHAIN_D - max((q @ NCH).max() for q in sec(m, [0, YB, 0], [0, 1, 0], 0, 2))
    ax.text(c0[0] - 22 * TC[0], c0[1] - 22 * TC[1] - 3.2, f"chain · gap {gap:.1f}", color="#7b1fa2", fontsize=9, fontweight="bold")
    ax.set_aspect("equal"); ax.set_xlim(-30, 26); ax.set_ylim(-40, 13); ax.axis("off")
    ax.set_title("Front view  (dashed = stock, purple = chain top)", fontsize=11)
    # --- side section (thickness)
    ax = fig.add_subplot(3, NC, i + 1 + 2 * NC)
    xcut = -9
    for c in sec(m0, [xcut, 0, 0], [1, 0, 0], 1, 2): ax.plot(*c.T, color=GRY, ls="--", lw=1.1)
    cs = sec(m, [xcut, 0, 0], [1, 0, 0], 1, 2)
    for c in cs: ax.fill(*c.T, color="#e8eaf0"); ax.plot(*c.T, "k", lw=1.6)
    zl = min(c[:, 1].min() for c in cs); zt = max(c[:, 1].max() for c in cs)
    # pad bottom z at this section (block only)
    zp = min(c[:, 1].min() for c in sec(m, [xcut, 2, 0], [1, 0, 0], 1, 2) for c in [c[c[:, 0] < T - Sk - 0.3]] if len(c))
    dim(ax, (0, zt + 2), (T, zt + 2), f"total {T:g}", BLUE, (0, 0.9))
    dim(ax, (0, zl - 2), (T - Sk, zl - 2), f"pad\n{T-Sk:g}", PUR, (0, -1.6))
    dim(ax, (T - Sk, zl - 2), (T, zl - 2), f"base\n{Sk:g}", ORG, (0, -1.6))
    for y in (0, T - Sk, T): ax.plot([y, y], [zl - 2.6, zt + 2.6], color="#ccc", lw=0.7, zorder=0)
    dim(ax, (T + 2, zl), (T + 2, zt), f"{zt-zl:.1f}", "k", (0.6, 0), "left")
    dim(ax, (-2, zp), (-2, zt), f"{zt-zp:.1f}", PUR, (-0.6, 0), "right")
    ax.set_aspect("equal"); ax.set_xlim(-12, 26); ax.set_ylim(-30, 12); ax.axis("off")
    ax.set_title(f"Thickness — side section at x = {xcut}", fontsize=11)
fig.suptitle("LoneWolf head — extension options (mm)   ·   thickness 14.07 = 9.31 raised pad + 4.76 base (caliper-measured)",
             fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.99)
plt.tight_layout(rect=(0, 0, 1, 0.97)); plt.savefig("renders/lonewolf_extensions.pdf")

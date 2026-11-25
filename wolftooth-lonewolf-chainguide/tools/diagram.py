import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import numpy as np, trimesh, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import lonewolf_head as L
YB = L.TOTAL_DEPTH - L.SKIRT_DEPTH / 2   # section through the base plate

m0 = trimesh.load("models/lonewolf_head_ext0mm.stl"); m6 = trimesh.load(f"models/lonewolf_head_ext{L.EXTENSION:g}mm.stl")
def sec(m, origin, normal, ix, iy):
    s = m.section(plane_origin=origin, plane_normal=normal)
    return [e[:, [ix, iy]] for e in s.discrete]

BLUE, RED, GRN, ORG, PUR, GRY = "#1f5fbf", "#c62828", "#2e7d32", "#e65100", "#6a1b9a", "#757575"
fig = plt.figure(figsize=(17, 10.5))
ax = fig.add_axes([0.02, 0.05, 0.60, 0.86]); sx = fig.add_axes([0.64, 0.40, 0.34, 0.51])
nx = fig.add_axes([0.64, 0.04, 0.34, 0.33]); nx.axis("off")

# ---------------- FRONT VIEW ----------------
for e in sec(m6, [0, YB, 0], [0, 1, 0], 0, 2): ax.plot(*e.T, color=GRY, ls="--", lw=1.2)
for e in sec(m6, [0, 2, 0], [0, 1, 0], 0, 2): ax.plot(*e.T, color=GRY, ls="--", lw=1.0)
for e in sec(m0, [0, YB, 0], [0, 1, 0], 0, 2): ax.fill(*e.T, color="#e8eaf0", zorder=0); ax.plot(*e.T, "k", lw=1.8)
for e in sec(m0, [0, 2, 0], [0, 1, 0], 0, 2): ax.plot(*e.T, color="#37474f", lw=1.4)
ax.text(-26.5, -24.4, f"- - -  dashed = extended outline (EXTENSION = {L.EXTENSION:g})", color=GRY, fontsize=9)

def dot(p, c, label, off, ha="left", fs=9.5):
    ax.plot(*p, "o", color=c, ms=6, zorder=5)
    ax.annotate(label, p, xytext=(p[0] + off[0], p[1] + off[1]), color=c, fontsize=fs, ha=ha,
                fontweight="bold", arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
def radius(c, r, ang, col, label, loff=(0.3, 0.3)):
    e = (c[0] + r * np.cos(ang), c[1] + r * np.sin(ang))
    ax.add_patch(FancyArrowPatch(c, e, arrowstyle="-|>", mutation_scale=12, color=col, lw=1.4, zorder=6))
    ax.text((c[0] + e[0]) / 2 + loff[0], (c[1] + e[1]) / 2 + loff[1], label, color=col, fontsize=9.5, fontweight="bold")

hc, dc = np.array(L.HOLE_CENTRE), np.array(L.DOME_CENTRE)
# origin
ax.plot(0, 0, "+", color="k", ms=12, mew=1.5); ax.text(-0.4, -0.9, "(0,0)", fontsize=8.5, ha="right")
ax.annotate("", (2, 0), (0, 0), arrowprops=dict(arrowstyle="->", lw=1)); ax.text(2.1, -0.2, "X", fontsize=9)
ax.annotate("", (0, 2), (0, 0), arrowprops=dict(arrowstyle="->", lw=1)); ax.text(-0.2, 2.2, "Z", fontsize=9)
# hole
t = np.radians(L.HOLE_TILT)
ax_maj = np.array([np.sin(t), np.cos(t)]); ax_min = np.array([np.cos(t), -np.sin(t)])
ax.add_patch(FancyArrowPatch(hc - ax_maj * L.HOLE_H / 2, hc + ax_maj * L.HOLE_H / 2, arrowstyle="<|-|>",
                             mutation_scale=12, color=RED, lw=1.4, zorder=6))
ax.add_patch(FancyArrowPatch(hc - ax_min * L.HOLE_W / 2, hc + ax_min * L.HOLE_W / 2, arrowstyle="<|-|>",
                             mutation_scale=12, color=RED, lw=1.4, zorder=6))
ax.text(hc[0] + 2.3, hc[1] + 6.4, f"HOLE_H {L.HOLE_H}", color=RED, fontsize=9.5, fontweight="bold")
ax.text(hc[0] + 0.6, hc[1] - 3.0, f"HOLE_W {L.HOLE_W}", color=RED, fontsize=9.5, fontweight="bold")
ax.plot([hc[0], hc[0]], [hc[1] + 3.5, hc[1] + 6.6], color=RED, lw=0.8, ls=":")
ax.text(hc[0] - 3.2, hc[1] + 6.9, f"HOLE_TILT {L.HOLE_TILT:g}°", color=RED, fontsize=9, fontweight="bold", ha="center")
dot(hc, "#ad1457", f"HOLE_CENTRE = DOME_CENTRE {L.HOLE_CENTRE}\n(pad top concentric with oval hole)", (7.0, 11.5))
# dome
radius(dc, L.TOP_R, np.radians(135), BLUE, f"TOP_R\n{L.TOP_R}", (-3.8, 0.4))

# corners
dot(L.CORNER_L, PUR, f"CORNER_L {L.CORNER_L}\nPAD_CORNER_R = {L.PAD_CORNER_R}", (-4, 5.5), "right")
dot(L.CORNER_R, PUR, f"CORNER_R {L.CORNER_R}\nPAD_CORNER_R = {L.PAD_CORNER_R}", (1.5, 4.5))
# U
uc = np.array(L.U_CENTRE)


# base corners
dot(L.FIN_TIP, ORG, f"FIN_TIP {L.FIN_TIP}", (-1, 4.5), "center")
dot(L.SKIRT_BL, ORG, f"SKIRT_BL {L.SKIRT_BL}", (-6.5, -3.0), "center")
dot(L.SKIRT_BR, ORG, f"SKIRT_BR {L.SKIRT_BR}", (4, -3.4), "center")
ax.text(-26.5, 12.5, f"BASE_CORNER_R = {L.BASE_CORNER_R}\n(rounds FIN_TIP, SKIRT_BL, SKIRT_BR)",
        color=ORG, fontsize=9.5, fontweight="bold")
# chamfers on the base plate's front edges (draw the inset front-face line)
for e in sec(m0, [0, L.TOTAL_DEPTH - L.SKIRT_DEPTH + 0.05, 0], [0, 1, 0], 0, 2):
    ax.plot(*e.T, color=BLUE, lw=0.9, ls="-.")
ax.text(9.0, -9.0, f"chamfers (dash-dot = front edge)\nCHAMFER_TRAIL {L.CHAMFER_TRAIL}", color=BLUE, fontsize=9, fontweight="bold")
ax.text(-27.5, -12.5, f"CHAMFER_LEAD\n{L.CHAMFER_LEAD}", color=BLUE, fontsize=9, fontweight="bold")
ax.text(-9.5, -15.0, f"CHAMFER_BOTTOM {L.CHAMFER_BOTTOM}", color=BLUE, fontsize=9, fontweight="bold", ha="center")
# bottom arch
bl, br = np.array(L.SKIRT_BL), np.array(L.SKIRT_BR); mid = (bl + br) / 2
ax.plot(*np.c_[bl, br], color=ORG, ls=":", lw=1)
ax.annotate("", mid + [0, L.BOTTOM_ARCH + 0.05], mid, arrowprops=dict(arrowstyle="->", color=ORG, lw=1.4))
ax.text(mid[0] - 1, mid[1] - 2.2, f"BOTTOM_ARCH {L.BOTTOM_ARCH}", color=ORG, fontsize=9.5, fontweight="bold", ha="center")
# extension (perpendicular to the chain) + chain line
TC = np.array([np.cos(np.radians(L.CHAIN_ANGLE)), np.sin(np.radians(L.CHAIN_ANGLE))])
NC = np.array([TC[1], -TC[0]]); NC = -NC if NC[1] > 0 else NC
c0 = (max((q @ NC).max() for q in sec(m0, [0, YB, 0], [0, 1, 0], 0, 2)) + L.CHAIN_GAP_STOCK) * NC
ax.plot(*np.c_[c0 - 30 * TC, c0 + 26 * TC], color="#7b1fa2", lw=3, alpha=0.6, zorder=0)
ax.text(*(c0 + 12 * TC + [0.5, -2.2]), f"chain top (CHAIN_ANGLE {L.CHAIN_ANGLE:g}°)\nstock gap {L.CHAIN_GAP_STOCK} → {L.CHAIN_GAP_STOCK - L.EXTENSION:g} at EXTENSION {L.EXTENSION:g}",
        color="#7b1fa2", fontsize=9, fontweight="bold")
for s0 in (-6.0, 1.0):
    p0 = (L.TOP_R) * NC + s0 * TC
    ax.add_patch(FancyArrowPatch(tuple(p0), tuple(p0 + L.EXTENSION * NC), arrowstyle="-|>", mutation_scale=14, color=GRY, lw=2))
ax.text(-3, -23.2, "EXTENSION (mm): leading edge kept parallel to the chain, moved this much closer",
        color="#424242", fontsize=10, fontweight="bold", ha="center")
# scale bar
ax.plot([15, 20], [-24.4, -24.4], "k", lw=3); ax.text(17.5, -24.0, "5 mm", ha="center", fontsize=8.5)
ax.set_aspect("equal"); ax.set_xlim(-28, 24); ax.set_ylim(-34, 16); ax.axis("off")
ax.set_title("FRONT VIEW (looking down the hole)  —  outline coordinates are (x, z) mm, scaled by SCALE",
             fontsize=12, fontweight="bold", loc="left")

# ---------------- SIDE VIEW ----------------
xcut = -9.0
for e in sec(m6, [xcut, 0, 0], [1, 0, 0], 1, 2): sx.plot(*e.T, color=GRY, ls="--", lw=1.1)
for e in sec(m0, [xcut, 0, 0], [1, 0, 0], 1, 2): sx.fill(*e.T, color="#e8eaf0"); sx.plot(*e.T, "k", lw=1.8)
T, Sk = L.TOTAL_DEPTH, L.SKIRT_DEPTH
z0 = min(e[:, 1].min() for e in sec(m0, [xcut, 0, 0], [1, 0, 0], 1, 2))
zt = max(e[:, 1].max() for e in sec(m0, [xcut, 0, 0], [1, 0, 0], 1, 2))
zlo = min(e[:, 1].min() for e in sec(m6, [xcut, 0, 0], [1, 0, 0], 1, 2))
def hdim(a, b, z, txt, c, below=False):
    sx.add_patch(FancyArrowPatch((a, z), (b, z), arrowstyle="<|-|>", mutation_scale=11, color=c, lw=1.4))
    sx.text((a + b) / 2, z + (-0.6 if below else 0.5), txt, color=c, ha="center",
            va="top" if below else "bottom", fontsize=9.5, fontweight="bold")
hdim(0, T, zt + 2.6, f"TOTAL_DEPTH = {T:g} (measured)", BLUE)
hdim(0, T - Sk, zlo - 1.2, f"raised pad\n= {T - Sk:g}", PUR, True)
hdim(T - Sk, T, zlo - 1.2, f"SKIRT_DEPTH\n= {Sk:g}\n(measured)", ORG, True)
for y in (0, T - Sk, T): sx.plot([y, y], [zlo - 1.6, zt + 3], color="#bbb", lw=0.7, zorder=0)
sx.text(-0.4, zt - 1, "front\n(pad face)", ha="right", fontsize=8.5)
sx.text(T + 0.4, zt - 1, "back\n(against arm)", ha="left", fontsize=8.5)
sx.set_aspect("equal"); sx.set_xlim(-7, 22); sx.set_ylim(zlo - 6.5, zt + 4.5); sx.axis("off")
sx.set_title(f"SIDE SECTION at x = {xcut:g}  (Y = along the hole)", fontsize=12, fontweight="bold", loc="left")

# ---------------- NOTES ----------------
notes = [("Global settings", "k"),
         (f"SCALE = {L.SCALE}   outline measured from photo (43.5 px/mm via the oval hole)", "k"),
         (f"EXTENSION = {L.EXTENSION} mm   CLI: python3 lonewolf_head.py <mm>", GRY),
         (f"Thickness {L.TOTAL_DEPTH} overall, base {L.SKIRT_DEPTH} (caliper-measured)", BLUE),
         (f"MIRROR = {L.MIRROR}   flips the fin to the other side", "k"),
         (f"EDGE_FILLET = {L.EDGE_FILLET} mm   rounds every edge;  CHAMFER_DEPTH = {L.CHAMFER_DEPTH}", "k"),
         ("Absolute (not scaled): hole, depths, corner radii, EXTENSION", RED),
         ("Hole 10.21 x 11.6 caliper-measured; outline fit rms 0.19 mm", RED)]
for i, (t, c) in enumerate(notes):
    nx.text(0, 1 - i * 0.12, t, color=c, fontsize=11 if i else 12.5, fontweight="bold" if i in (0, 6, 7) else None,
            transform=nx.transAxes, va="top")
fig.suptitle("Wolf Tooth LoneWolf head — parametric model (lonewolf_head.py)", fontsize=15, fontweight="bold", x=0.02, ha="left")
plt.savefig("renders/lonewolf_parameters.png", dpi=130); plt.savefig("renders/lonewolf_parameters.pdf")

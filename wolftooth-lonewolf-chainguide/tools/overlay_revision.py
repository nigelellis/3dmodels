"""Overlay the current +5 mm design on a photo of the last print, as it will seat.

The as-printed model is registered to the photo with the landmarks in
reference/fit/first_print.json (hole centre and the pad's two top corners, a
similarity fit). The current design is drawn turned by HOLE_TILT_EXT about the
hole: the cam is fixed, so tilting the oval by -N° turns the part N° clockwise.

Writes renders/overlay_revision<REVISION>.png. Run by tools/build_all.py.
"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)
os.makedirs("renders", exist_ok=True)

import numpy as np, trimesh, cadquery as cq
from PIL import Image, ImageOps, ImageDraw, ImageFont
import lonewolf_head as L

REF = json.load(open("reference/fit/first_print.json"))
EXT = REF["extension"]


def pad_outline(**settings):
    """Front-face (raised pad) outline of the +EXT part with temporary settings."""
    old = {k: getattr(L, k) for k in settings}
    for k, v in settings.items():
        setattr(L, k, v)
    try:
        part = L.build(EXT)
    finally:
        for k, v in old.items():
            setattr(L, k, v)
    path = os.path.join("build", "overlay_tmp.stl"); os.makedirs("build", exist_ok=True)
    cq.exporters.export(part, path, tolerance=0.01, angularTolerance=0.1)
    m = trimesh.load(path)
    y = max(L.EDGE_FILLET, 0.2) + 0.2                    # just behind the front rounding
    return [q[:, [0, 2]] for q in m.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0]).discrete]


printed = pad_outline(**REF["printed_settings"])
current = pad_outline()

# similarity fit, model (x + i z) -> image (u - i v)
M = np.array([complex(*lm["model"]) for lm in REF["landmarks"]])
I = np.array([complex(lm["image"][0], -lm["image"][1]) for lm in REF["landmarks"]])
A = np.c_[M, np.ones(len(M))]
(a, b), *_ = np.linalg.lstsq(A, I, rcond=None)
resid = np.abs(A @ np.array([a, b]) - I)
to_img = lambda P: (lambda w: np.c_[w.real, -w.imag])(a * (P[:, 0] + 1j * P[:, 1]) + b)

turn = L.HOLE_TILT_EXT - REF["printed_settings"]["HOLE_TILT_EXT"]   # deg CCW the part turns vs the print
th = np.radians(turn); R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])

img = ImageOps.exif_transpose(Image.open(REF["photo"])).convert("RGBA")
ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)


def draw(loops, colour, rot=None):
    for q in loops:
        q = q @ rot.T if rot is not None else q
        p = to_img(q)
        d.line([tuple(x) for x in np.vstack([p, p[:1]])], fill=colour, width=4, joint="curve")


draw(printed, (255, 215, 0, 255))
draw(current, (0, 215, 255, 255), R)
d.line([tuple(p) for p in REF["chain_top"]], fill=(255, 60, 200, 230), width=4)

out = Image.alpha_composite(img, ov).convert("RGB").crop(tuple(REF["crop"]))
try:
    f = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
except OSError:
    f = ImageFont.load_default()
dd = ImageDraw.Draw(out)
dd.rectangle([0, 0, out.width, 104], fill=(255, 255, 255))
dd.text((12, 6), f"yellow  = +{EXT:g} as printed, registered on the front-face edges", fill=(150, 120, 0), font=f)
dir_txt = "CW" if turn < 0 else "CCW"
dd.text((12, 38), f"cyan    = revision {L.REVISION} as it will seat (oval tilt {L.HOLE_TILT_EXT:+g}° → part {abs(turn):g}° {dir_txt})",
        fill=(0, 120, 160), font=f)
dd.text((12, 70), "magenta = chain top (approx.)", fill=(170, 0, 120), font=f)
name = f"renders/overlay_revision{L.REVISION}.png"
out.save(name)
print(f"-> {name}  (scale {abs(a):.2f} px/mm, landmark residuals {np.round(resid, 1)} px)")

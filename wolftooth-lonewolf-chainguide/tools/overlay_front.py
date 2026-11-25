import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import json, numpy as np, trimesh, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import lonewolf_head as L
f = json.load(open("reference/fit/front_fit.json")); PX = f["px_per_mm"]; HC = np.array([1456,1485])
im = ImageOps.exif_transpose(Image.open("reference/photos/05_front_straight_on.jpg"))
m = trimesh.load("models/lonewolf_head_ext0mm.stl")
toimg = lambda Q: np.c_[Q[:,0]*PX+HC[0], HC[1]-Q[:,1]*PX]
fig, axs = plt.subplots(1, 2, figsize=(15, 6.6))
for ax, show in zip(axs, (True, False)):
    if show: ax.imshow(im)
    else: ax.imshow(np.full((im.height, im.width, 3), 255, np.uint8))
    for y, c, lw, lab in [(L.TOTAL_DEPTH-0.3, "cyan", 2, "base, back face"), (L.TOTAL_DEPTH-L.SKIRT_DEPTH+0.3, "deepskyblue", 1.2, "base, front face (sloped right side)"),
                          (0.3, "orange", 2, "raised pad")]:
        for i, e in enumerate(m.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0]).discrete):
            ax.plot(*toimg(e[:, [0, 2]]).T, color=c, lw=lw, label=lab if i == 0 else None)
    ax.set_xlim(420, 1960); ax.set_ylim(2290, 1080); ax.axis("off")
axs[0].set_title("Stock model (0 mm) drawn on your photo, scaled by the 10.21 x 11.6 mm hole", fontsize=11)
axs[1].set_title("Stock model outlines alone", fontsize=11); axs[1].legend(loc="lower left", fontsize=9)
plt.tight_layout(); plt.savefig("renders/compare_front_photo.png", dpi=95)

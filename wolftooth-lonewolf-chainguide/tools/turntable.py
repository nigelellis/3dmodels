import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import numpy as np, trimesh, sys
from PIL import Image, ImageDraw, ImageFont
m = from render_mesh import render_mesh
os.makedirs("build/frames", exist_ok=True)
m = trimesh.load(render_mesh(0))
V0 = m.vertices - m.bounding_box.centroid
F = m.faces; VN = m.vertex_normals
FN = VN[F].mean(1); FN /= np.linalg.norm(FN, axis=1)[:, None]       # smoothed face normals
OUT, SS = 720, 2; W = OUT * SS
scale = W * 0.023
bg = Image.new("RGB", (W, W)); g = np.linspace(250, 222, W).astype(np.uint8)
bg = Image.fromarray(np.repeat(np.repeat(g[:, None], W, 1)[:, :, None], 3, 2))
try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34); small = ImageFont.truetype("DejaVuSans.ttf", 26)
except: font = small = ImageFont.load_default()
key = np.array([-0.45, -0.75, 0.5]); key /= np.linalg.norm(key)
rim = np.array([0.7, 0.3, 0.4]); rim /= np.linalg.norm(rim)
N = 180
for i in range(N):
    yaw = np.radians(-30 + 360 * i / N); pitch = np.radians(18 + 6 * np.sin(2 * np.pi * i / N))
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
    R = Rx @ Rz
    V = V0 @ R.T; N_ = FN @ R.T; TN = m.face_normals @ R.T
    uv = np.c_[V[:, 0] * scale + W / 2, -V[:, 2] * scale + W / 2 + W * 0.02]
    img = bg.copy(); d = ImageDraw.Draw(img)
    depth = V[F][:, :, 1].mean(1)
    vis = TN[:, 1] < 0.05
    for f in np.argsort(-depth):
        if not vis[f]: continue
        n = N_[f]
        h = key + np.array([0, -1, 0]); h /= np.linalg.norm(h)
        lam = 0.18 + 0.72 * max(0, n @ key) + 0.22 * max(0, n @ rim)
        spec = max(0, n @ h) ** 40 * 0.45
        k = min(1.0, lam)
        col = tuple(int(min(255, 255 * (k * c + spec))) for c in (0.36, 0.37, 0.41))
        d.polygon([tuple(q) for q in uv[F[f]]], fill=col)
    d.text((28, 22), "Wolf Tooth LoneWolf head — stock (0 mm)", fill=(40, 40, 50), font=font)
    d.text((28, 66), "31.5 × 25.0 × 14.1 mm  ·  oval 10.21 × 11.6  ·  2.2 mm chamfers, 0.5 mm edges", fill=(90, 90, 100), font=small)
    img.resize((OUT, OUT), Image.LANCZOS).save(f"build/frames/f{i:03d}.png")

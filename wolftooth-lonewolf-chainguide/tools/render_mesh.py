"""Lightweight render meshes (coarser than the print STLs) cached in build/."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def render_mesh(ext):
    path = os.path.join(ROOT, "build", f"render{ext:g}.stl")
    model = os.path.join(ROOT, "lonewolf_head.py")
    if not os.path.exists(path) or os.path.getmtime(path) < os.path.getmtime(model):
        import cadquery as cq
        import lonewolf_head as L
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cq.exporters.export(L.build(ext), path, tolerance=0.03, angularTolerance=0.2)
    return path

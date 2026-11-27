"""
Parametric Wolf Tooth LoneWolf chainguide head (recreation from photos).

All dimensions in mm. Values were ESTIMATED FROM PRODUCT PHOTOS -- measure your
original head with calipers and update the parameters before final printing.

Coordinate frame (front view = the product photo, looking down the hole):
  X = width   (+X = the steep straight side, -X = the thin fin side)
  Z = height  (0 = hole centre, -Z = down toward the chain)
  Y = hole axis (Y=0 is the front pad face, toward the viewer;
               Y=TOTAL_DEPTH is the back face against the arm)

Shape:
  * HEAD BLOCK  - full depth. Rounded top around the hole, sharp corner on each
                  side, U-shaped bottom edge.
  * SKIRT/FIN   - shallower plate at the back. Shows as a step below the U,
                  a long sloping fin edge on the -X side and a side that leans
                  inward on the +X side. The underside is slightly concave.

EXTENSION moves the body's bottom toward the chain (perpendicular to the chain
line, CHAIN_ANGLE) and squares it off parallel to the chain; the thin base plate
moves the same way. The hole, top, corners and fin tip stay put.
Outline values were fitted to the product photo (silhouette, pad edge, bore).

Run:  python3 lonewolf_head.py        -> uses EXTENSION below
      python3 lonewolf_head.py 3      -> 3 mm extension
Files are written to models/.
"""
import os
import sys
import numpy as np
import cadquery as cq
from scipy.spatial import ConvexHull

# ---------------- PARAMETERS (edit these) ----------------
REVISION      = 2      # bump for each printed revision; names renders/overlay_revision<N>.png
# Measured from a straight-on photo of the real part, scaled by the oval
# hole (10.21 x 11.6 mm, caliper-measured): 43.5 px/mm, outline fit rms 0.19 mm
# over 273 auto-traced edge points.
# SCALE resizes the front-view outline only (not thickness, hole, radii,
# extension). Leave at 1.0 unless a caliper check of the width disagrees.
SCALE         = 1.0

EXTENSION     = 5.0    # move the body's bottom this far toward the chain, mm (0 = stock)
BASE_EXTENSION = None  # how far the thin base plate moves; None = same as EXTENSION
CHAIN_ANGLE   = -17.5  # chain line direction in the front view, deg (measured, mounted photo)
CHAIN_GAP_STOCK = 7.4  # measured gap from the stock base's nearest corner to the chain
MIRROR        = False  # True = fin on the other side (left/right-hand head)

# oval GuideLock hole (caliper-measured)
HOLE_W        = 10.21  # width
HOLE_H        = 11.6   # height (long axis)
HOLE_TILT     = 16.0   # long axis leans this many degrees from vertical, top toward +X (OEM)
HOLE_TILT_EXT = -4.0   # extra tilt on extended versions (+ = clockwise, - = top toward the
                       # rear). The bushing (cam) is fixed, so tilting the oval back 4° turns the
                       # part 4° clockwise and levels its bottom with the chain (first +5 print)
HOLE_CLEARANCE = 0.1   # added to both hole axes: covers ASA shrinkage. Keep small: the oval is only
                       # 1.4 mm elongated, so 0.1 mm already allows ~±4° twist on the bushing (0.2 = ±8°)
HOLE_CENTRE   = (0.0, 0.0)

TOP_R         = 8.22    # radius of the raised pad's rounded top (concentric with hole)
DOME_CENTRE   = (0.0, 0.0)

TOTAL_DEPTH   = 14.07   # overall thickness along the hole (caliper-measured)
SKIRT_DEPTH   = 4.76    # thin base plate / fin (caliper-measured); raised pad = 9.31

# raised pad outline, front view (hole centre = 0,0)
CORNER_L      = (-12.12, -0.2)    # pad corner on the fin side (x, z)
CORNER_R      = (9.23, -0.1)     # pad corner on the steep side
U_CENTRE      = (0.0, 0.0)       # centre of the pad's lower curve (stock = same as top)
U_R           = 8.22              # radius of the pad's lower curve

# base / fin outline, front view (full outline, behind the chamfers)
FIN_TIP       = (-21.49, -8.24)   # point of the fin
SKIRT_BL      = (-18.57, -14.48)  # bottom corner on the fin side
SKIRT_BR      = (4.5, -16.4)    # bottom corner on the steep side
BOTTOM_ARCH   = 0.76               # underside curves up by this much in the middle
# chamfers on the base plate's front edges (width measured on the front face)
CHAMFER_LEAD   = 2.2   # fin's lower edge (fin tip -> bottom corner)
CHAMFER_BOTTOM = 2.2   # underside edge
CHAMFER_TRAIL  = 2.2   # steep side (measured 2.2 from the photo)
CHAMFER_DEPTH  = 2.2   # how far back into the 5.3 mm base the chamfer runs (45 deg when = width)

PAD_CORNER_R  = 2.0             # rounding of the raised pad's side corners
PAD_END_R     = 5.0             # extended pad bottom: radius of the curved leading/trailing
                                # ends where the chain enters and leaves (OEM U ~ TOP_R)
BASE_CORNER_R = 1.5             # rounding of the base's fin tip and bottom corners
# raised text on the back face (the face against the arm)
TEXT_LINES    = ()      # e.g. ("BushpigLab", "LLC") to add raised text
TEXT_SIZE     = 3.0    # cap height-ish, mm
TEXT_HEIGHT   = 0.5    # how far the letters stand proud, mm (negative = engraved)
TEXT_CENTRE   = (-6.5, -10.0)  # front-view (x, z) of the text block on the stock part
TEXT_FONT     = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EDGE_FILLET   = 1.0            # rounding of the square edges: pad front edge and back outline (0 = off)
HOLE_FILLET   = 0.5            # rounding of both hole rims (0 = off)
# ----------------------------------------------------------


def _hull_order(elems):
    """Order in which circles/points appear on the convex hull (CCW)."""
    pts, ids = [], []
    for k, (c, r, a0, a1) in enumerate(elems):
        if r == 0:
            pts.append(c); ids.append(k); continue
        for t in np.linspace(a0, a1, 720):
            pts.append((c[0] + r * np.cos(t), c[1] + r * np.sin(t))); ids.append(k)
    h = ConvexHull(np.array(pts)).vertices
    seq = []
    for v in h:
        if not seq or seq[-1] != ids[v]:
            seq.append(ids[v])
    if len(seq) > 1 and seq[0] == seq[-1]:
        seq.pop()
    return seq


def _tangent(c1, r1, c2, r2):
    """Outer tangent from element 1 to element 2 for a CCW outline."""
    d = np.subtract(c2, c1); L = np.linalg.norm(d); u = d / L
    v = np.array([u[1], -u[0]])                     # right-hand side = outside
    a = (r1 - r2) / L
    n = a * u + np.sqrt(max(0.0, 1 - a * a)) * v
    return np.add(c1, r1 * n), np.add(c2, r2 * n), n


def outline(elems, y0, concave=None, seq=None):
    """Closed XZ outline at Y=y0: convex hull of circles/points as true arcs
    and tangent lines. elems: list of (centre, radius, a0, a1); radius 0 = sharp.
    concave: optional (i, j, sag) - the edge from element i to j curves inward.
    seq: optional element order (reuse it so two outlines share topology)."""
    seq = _hull_order(elems) if seq is None else seq
    n = len(seq)
    tans = [_tangent(elems[seq[k]][0], elems[seq[k]][1],
                     elems[seq[(k + 1) % n]][0], elems[seq[(k + 1) % n]][1])
            for k in range(n)]
    wp = cq.Workplane("XZ", origin=(0, y0, 0))
    start = tans[-1][1]
    wp = wp.moveTo(*start)
    for k in range(n):
        c, r = elems[seq[k]][0], elems[seq[k]][1]
        p_in, (p_out, p_next, nrm) = tans[k - 1][1], tans[k]
        if r > 0:                                  # arc around this circle
            a_in = np.arctan2(p_in[1] - c[1], p_in[0] - c[0])
            a_out = np.arctan2(p_out[1] - c[1], p_out[0] - c[0])
            sweep = (a_out - a_in) % (2 * np.pi)
            if sweep > 1e-4:
                am = a_in + sweep / 2
                wp = wp.threePointArc((c[0] + r * np.cos(am), c[1] + r * np.sin(am)),
                                      tuple(p_out))
        last = (k == n - 1)
        if concave and (seq[k], seq[(k + 1) % n]) == concave[:2]:
            mid = (np.array(p_out) + np.array(p_next)) / 2 - nrm * concave[2]
            wp = wp.threePointArc(tuple(mid), tuple(p_next)) if not last else \
                wp.threePointArc(tuple(mid), tuple(start))
        elif not last:
            wp = wp.lineTo(*p_next)
    return wp.close()


def profile(elems, y0, depth, concave=None):
    """Extrude outline() from Y=y0 to Y=y0+depth."""
    return outline(elems, y0, concave).extrude(-depth)


def edge_normals(elems, seq):
    """Outward normal of the hull edge leaving each element, keyed (i, j)."""
    n = len(seq); out = {}
    for k in range(n):
        i, j = seq[k], seq[(k + 1) % n]
        out[(i, j)] = _tangent(elems[i][0], elems[i][1], elems[j][0], elems[j][1])[2]
    return out



def round_all_edges(part, r, skip=None):
    """Round every edge that will take radius r, then step down (0.75r, 0.5r,
    0.3r) for edges too tight for it, e.g. where the bevels meet the base
    plate's front face. Smooth seams (arc meeting tangent line) are skipped."""
    for rad in (r, r * 0.75, r * 0.5, r * 0.3):
        cand = []
        for e in part.edges().vals():
            if skip is not None and skip(e):
                continue
            try:
                if part.newObject([e]).fillet(rad).val().isValid():
                    cand.append(e)
            except Exception:
                pass
        # add edges in groups; drop any group that makes the combined fillet fail
        def try_set(edges):
            try:
                q = part.newObject(edges).fillet(rad)
                return q if q.val().isValid() else None
            except Exception:
                return None
        done = try_set(cand) if cand else None
        if done is None and cand:
            good = []
            for e in cand:
                if try_set(good + [e]) is not None:
                    good.append(e)
            done = try_set(good) if good else None
        if done is not None:
            part = done
    return part

def build(ext=EXTENSION):
    S = SCALE
    sc = lambda p: (p[0] * S, p[1] * S)
    t_chain = np.array([np.cos(np.radians(CHAIN_ANGLE)), np.sin(np.radians(CHAIN_ANGLE))])
    n_chain = np.array([t_chain[1], -t_chain[0]])            # toward the chain
    if n_chain[1] > 0:
        n_chain = -n_chain
    ext_b = ext if BASE_EXTENSION is None else BASE_EXTENSION * (ext > 0)
    down = lambda p: tuple(np.array(p) * S + ext_b * n_chain)
    hc = np.array(sc(HOLE_CENTRE))

    def corner(p, r):
        """Rounded corner: circle of radius r pulled in toward the hole so the
        rounded outline stays close to the original sharp point."""
        p = np.array(p); d = hc - p; d /= np.linalg.norm(d)
        return (tuple(p + d * r * 0.8), r, 0, 2 * np.pi)

    dome = (sc(DOME_CENTRE), TOP_R * S, 0, 2 * np.pi)
    block_elems = [dome, corner(sc(CORNER_L), PAD_CORNER_R),
                   corner(sc(CORNER_R), PAD_CORNER_R)]
    if ext > 0:
        # flat bottom parallel to the chain, `ext` closer to it than the stock
        # rounded bottom; sides drop straight from the rounded top
        R, rf = TOP_R * S, min(PAD_END_R, TOP_R * S)
        base_pt = np.array(dome[0]) + (R + ext - rf) * n_chain
        for sgn in (-1, 1):
            block_elems.insert(1, (tuple(base_pt + sgn * (R - rf) * t_chain), rf, 0, 2 * np.pi))
    block = profile(block_elems, 0, TOTAL_DEPTH)

    bl, br = np.array(sc(SKIRT_BL)), np.array(sc(SKIRT_BR))
    concave_on = BOTTOM_ARCH > 0
    if ext_b > 0:
        # leading edge parallel to the chain: put both bottom corners on a line
        # parallel to the chain, ext_b closer than the stock part's nearest corner
        lead = max(bl @ n_chain, br @ n_chain) + ext_b
        bl = bl + (lead - bl @ n_chain) * n_chain
        br = br + (lead - br @ n_chain) * n_chain
        # keep the original's slight inward curve; the chord stays parallel to the chain
    skirt_elems = block_elems + [corner(sc(FIN_TIP), BASE_CORNER_R),
                                 corner(tuple(bl), BASE_CORNER_R),
                                 corner(tuple(br), BASE_CORNER_R)]
    ifin, ibl, ibr = len(skirt_elems) - 3, len(skirt_elems) - 2, len(skirt_elems) - 1
    icr = block_elems.index(corner(sc(CORNER_R), PAD_CORNER_R))
    concave = (ibl, ibr, BOTTOM_ARCH) if concave_on else None
    yf = TOTAL_DEPTH - SKIRT_DEPTH                     # base plate's front face
    seq = _hull_order(skirt_elems)
    insets = {(ifin, ibl): CHAMFER_LEAD, (ibl, ibr): CHAMFER_BOTTOM, (ibr, icr): CHAMFER_TRAIL}
    d = min(CHAMFER_DEPTH, SKIRT_DEPTH - 0.5)

    if d > 0 and any(w > 0 for w in insets.values()):
        # Chamfer = ruled loft from an inset outline on the front face to the
        # full outline CHAMFER_DEPTH behind it. Each corner circle is moved so
        # every hull edge shifts inward by exactly its own chamfer width (0 for
        # the fin's top edge and the pad side), so the chamfer starts and stops
        # cleanly at the fin tip and the pad corner.
        nrm = edge_normals(skirt_elems, seq)
        pos = {e: k for k, e in enumerate(seq)}
        inset_elems = list(skirt_elems)
        for i in (ifin, ibl, ibr, icr):
            if i not in pos:
                continue
            k = pos[i]; prv, nxt = seq[k - 1], seq[(k + 1) % len(seq)]
            n1, n2 = nrm[(prv, i)], nrm[(i, nxt)]
            w1, w2 = insets.get((prv, i), 0.0), insets.get((i, nxt), 0.0)
            if w1 == 0 and w2 == 0:
                continue
            v = np.linalg.solve(np.array([n1, n2]), -np.array([w1, w2]))
            c, r, a0, a1 = inset_elems[i]
            inset_elems[i] = (tuple(np.add(c, v)), r, a0, a1)
        w_front = outline(inset_elems, yf, concave, seq).val()
        w_full = outline(skirt_elems, yf + d, concave, seq).val()
        bevel = cq.Workplane("XY").newObject([cq.Solid.makeLoft([w_front, w_full], True)])
        rest = outline(skirt_elems, yf + d, concave).extrude(-(SKIRT_DEPTH - d))
        skirt = bevel.union(rest, clean=True)
    else:
        skirt = profile(skirt_elems, yf, SKIRT_DEPTH, concave=concave)

    if TEXT_LINES and TEXT_HEIGHT != 0:            # text goes on the base plate's back face
        skirt = add_back_text(skirt, ext_b, n_chain)
    part = skirt.union(block, clean=True)

    hole = (cq.Workplane("XZ", origin=(0, -1, 0)).center(*hc)
            .ellipse((HOLE_W + HOLE_CLEARANCE) / 2, (HOLE_H + HOLE_CLEARANCE) / 2, -(HOLE_TILT + (HOLE_TILT_EXT if ext > 0 else 0))).extrude(-(TOTAL_DEPTH + 2)))
    part = part.cut(hole)

    if EDGE_FILLET > 0:
        # Round only the square (90 deg) edges: the pad's front outline and the
        # back outline at EDGE_FILLET, both hole rims at HOLE_FILLET. Bevels, the base plate's front-face edges
        # and the pad/base inside corner stay crisp.
        has_text = bool(TEXT_LINES) and TEXT_HEIGHT != 0
        def in_plane(e, y):
            bb = e.BoundingBox()
            return abs(bb.ymin - y) < 1e-3 and abs(bb.ymax - y) < 1e-3
        def hole_rim(e):
            return (in_plane(e, 0.0) or in_plane(e, TOTAL_DEPTH)) and \
                np.hypot(e.Center().x - hc[0], e.Center().z - hc[1]) < 1.0
        def outer_edge(e):
            if hole_rim(e):
                return False
            # with text on the back, leave the back face alone (letters sit on it)
            return in_plane(e, 0.0) or (in_plane(e, TOTAL_DEPTH) and not has_text)
        part = round_all_edges(part, EDGE_FILLET, skip=lambda e: not outer_edge(e))
        if HOLE_FILLET > 0:
            part = round_all_edges(part, HOLE_FILLET, skip=lambda e: not hole_rim(e))

    if MIRROR:
        part = part.mirror("YZ")

    return part


def add_back_text(part, ext_b, n_chain):
    """Raised (or engraved) text on the back face, reading correctly when you
    look at the back. Moves halfway with the extension to stay centred."""
    cx, cz = np.array(TEXT_CENTRE) + 0.5 * ext_b * n_chain
    y = TOTAL_DEPTH - (0.2 if TEXT_HEIGHT > 0 else 0)   # sink raised letters in so they fuse
    # looking at the back (from +Y) the reader's right is -X, up is +Z
    plane = cq.Plane(origin=(cx, y, cz), xDir=(-1, 0, 0), normal=(0, 1, 0))
    gap = TEXT_SIZE * 1.35
    n = len(TEXT_LINES)
    depth = abs(TEXT_HEIGHT) + (0.2 if TEXT_HEIGHT > 0 else 0)
    solids = None
    for i, line in enumerate(TEXT_LINES):
        dz = (n - 1) / 2 * gap - i * gap
        kw = dict(halign="center", valign="center", kind="bold")
        try:
            t = cq.Workplane(plane).center(0, dz).text(line, TEXT_SIZE, depth if TEXT_HEIGHT > 0 else -depth,
                                                       fontPath=TEXT_FONT, combine=False, **kw)
        except Exception:
            t = cq.Workplane(plane).center(0, dz).text(line, TEXT_SIZE, depth if TEXT_HEIGHT > 0 else -depth,
                                                       combine=False, **kw)
        solids = t if solids is None else solids.union(t)
    if TEXT_HEIGHT < 0:
        return part.cut(solids)
    fused = part.union(solids, clean=True, tol=0.01)   # fuzzy boolean: letters crossing face seams
    shells = fused.val().Solids()
    if len(shells) > 1:                      # glue any stragglers
        fused = cq.Workplane("XY").newObject([shells[0].fuse(*shells[1:], tol=0.02).clean()])
    return fused


if __name__ == "__main__":
    ext = float(sys.argv[1]) if len(sys.argv) > 1 else EXTENSION
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.join(out_dir, f"lonewolf_head_ext{ext:g}mm")
    p = build(ext)
    assert p.val().isValid(), "generated solid is invalid - check parameters"
    cq.exporters.export(p, f"{name}.step")
    cq.exporters.export(p, f"{name}.stl", tolerance=0.01, angularTolerance=0.1)
    try:                                   # close any tessellation slivers
        import trimesh
        m = trimesh.load(f"{name}.stl")
        if not m.is_watertight:
            m.merge_vertices(digits_vertex=4)
            m.update_faces(m.nondegenerate_faces()); m.update_faces(m.unique_faces())
            trimesh.repair.fill_holes(m); trimesh.repair.fix_normals(m)
            if not m.is_watertight:
                try:                       # pip install pymeshfix
                    import pymeshfix
                    v, f = pymeshfix.clean_from_arrays(
                        np.ascontiguousarray(m.vertices, dtype=np.float64),
                        np.ascontiguousarray(m.faces, dtype=np.int32))
                    m = trimesh.Trimesh(v, f)
                except ImportError:
                    pass
            m.export(f"{name}.stl")
        print("watertight:", m.is_watertight)
    except ImportError:
        pass
    bb = p.val().BoundingBox()
    print(f"{os.path.basename(name)}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")

# Wolf Tooth LoneWolf chainguide head — extended replacement

A parametric recreation of the Wolf Tooth LoneWolf chainguide head, made so the body
can be lengthened toward the chain. The stock head sits 7.4 mm from the chain on a
36T SDM8 ring; the +5 mm version closes that to about 2.5 mm.

**Print this:** `models/lonewolf_head_ext5mm.stl` (or the `.step` to edit in CAD).

## Layout

| Path | What's there |
|---|---|
| `lonewolf_head.py` | The parametric model (CadQuery). All dimensions are at the top. |
| `models/` | Printable STL + editable STEP for 0 mm (stock), +3 mm and +5 mm |
| `renders/` | Contact sheet, extension comparison, parameter diagram, photo overlay, turntable |
| `reference/photos/` | The photos and caliper readings the model was measured from |
| `reference/fit/` | Outline fit result from the straight-on photo (scale, fitted points) |
| `tools/` | Render, diagram and fitting scripts; `build_all.py` regenerates everything |

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 lonewolf_head.py 5             # one version -> models/lonewolf_head_ext5mm.stl/.step
python3 tools/build_all.py             # all versions + sheets + diagrams
python3 tools/build_all.py --video     # also renders/lonewolf_head_turntable.mp4 (needs ffmpeg)
blender -b -P tools/blender_turntable.py -- models/lonewolf_head_ext0mm.stl renders/lonewolf_turntable_blender.mp4
```

`build/` holds temporary render meshes and frames and is not tracked.

## Measurements

Caliper-measured on the original part:

- Overall thickness along the hole: **14.07 mm**
- Thin base plate / fin: **4.76 mm** (raised pad = 9.31 mm)
- GuideLock hole: **oval 10.21 wide × 11.6 tall**
- Stock gap, base plate's nearest corner to the chain: **7.4 mm**

From the straight-on photo (`reference/photos/05_front_straight_on.jpg`), scaled by the
oval hole at 43.5 px/mm. The outline fit is within 0.19 mm RMS:

- Stock outline: 31.5 wide × 25.0 tall, looking down the hole
- Oval's long axis leans about 16° from vertical (`HOLE_TILT`)
- Raised pad: rounded top R 8.22 concentric with the hole; side corners R 2.0
- Base: fin tip at (-21.49, -8.24); bottom corners at (-18.57, -14.48) and (4.5, -16.4); corner R 1.5
- Bottom edge curves inward slightly, 0.76 mm at mid-span (`BOTTOM_ARCH`)
- Chain line runs at about -17.5° in the front view (`CHAIN_ANGLE`, from the mounted photo)

Coordinates are (x, z) mm from the hole centre, looking down the hole, with the fin on the -x side.

## Extension design

- **Leading edge:** this is the base plate's edge nearest the chain. Its ends sit on a line parallel to the chain, `EXTENSION` mm closer than the stock part's nearest corner. The edge keeps the original's slight inward curve.
- **Raised pad:** its bottom is squared off parallel to the chain and moved `EXTENSION` mm toward it.
- **Unchanged:** the hole, the top, the pad side corners and the fin tip.

| Version | Front-view height | Gap to chain |
|---|---|---|
| 0 (stock) | 25.0 | 7.4 |
| +3 | 32.7 | 4.4 |
| +5 (target) | 34.6 | 2.5 |

## Finishing details

- **Chamfers:** on the base plate's front edges (fin lower edge, leading edge and steep side), 2.2 mm wide × 2.2 mm deep. Only the steep-side width is confirmed from the photo.
- **Rounding:** every other edge is rounded 0.5 mm.
- **Back face:** flat, with no text. `TEXT_LINES` can add raised or engraved text if you want it later.

## Open items

- Confirm the chamfer depth on the original (`CHAMFER_DEPTH`).
- Confirm the oval tilt. Set `HOLE_TILT = 0` if the oval should be upright.
- Confirm the chain angle by test-fitting the +5 print. If one end of the leading edge is tighter, adjust `CHAIN_ANGLE`.
- Print in nylon, ASA or PETG, not PLA.

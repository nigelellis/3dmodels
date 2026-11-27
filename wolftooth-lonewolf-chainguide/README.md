# Wolf Tooth LoneWolf chainguide head — extended replacement

A dropin replacement for the stock WolfTooth LoneWolf head that extends the bottom face of the guide by 5mm for 36T chainrings.  A 5mm drop gets the face of the guide to the 2mm gap recommended by WolfTooth.

https://github.com/user-attachments/assets/209d09b5-f683-4fde-ae39-525db8d50e29

**Print this:** <a href="./models/lonewolf_head_ext5mm.stl">`models/lonewolf_head_ext5mm.stl`</a> (or the `.step` to edit in CAD).

## Layout

| Path | What's there |
|---|---|
| `lonewolf_head.py` | The parametric model (CadQuery). All dimensions are at the top. |
| `models/` | Printable STL + editable STEP for 0 mm (stock), +3 mm and +5 mm |
| `renders/` | Contact sheet, extension comparison, parameter diagram, photo overlay, turntable |
| `reference/photos/` | The photos and caliper readings the model was measured from |
| `reference/fit/` | Outline fit result from the straight-on photo (scale, fitted points) |
| `tools/` | Render, diagram and fitting scripts; `build_all.py` regenerates everything |
| `revisions/` | Earlier printed revisions, one folder each (`rev1/`, …) |

## Version log

| Rev | Date | Changes |
|---|---|---|
| 2 | 2026-11-27 | After test-fitting the first +5 mm print (ASA): oval tilted 4° back so the bottom sits parallel to the chain; curved pad ends (R 5); hole clearance +0.1 mm; 1 mm rounding on square edges and 0.5 mm on the hole rims; photo overlay check (`renders/overlay_revision2.png`) added to every build; turntable and detail views show +5 mm; MIT license. |
| 1 | 2026-11-25 | First printed version (+5 mm): outline measured from photos and calipers, leading edge parallel to the chain, 2.2 mm bevels on the base plate, 0/3/5 mm variants. Archived in `revisions/rev1/`. |

The current revision lives at the top level (`lonewolf_head.py`, `models/`, `renders/`). Earlier revisions are kept in full under `revisions/rev<N>/`: the model script, README, STL/STEP files and renders as they were printed.

**Starting a new revision:** run `python3 tools/archive_revision.py` to copy the current revision into `revisions/rev<REVISION>/`, then bump `REVISION` in `lonewolf_head.py`, make the changes and run `python3 tools/build_all.py`. Add a row to the version log above.

A parametric recreation of the Wolf Tooth LoneWolf chainguide head, made so the body
can be lengthened toward the chain. The stock head sits 7.4 mm from the chain on a
36T SDM8 ring; the +5 mm version closes that to about 2.5 mm.

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 lonewolf_head.py 5             # one version -> models/lonewolf_head_ext5mm.stl/.step
python3 tools/build_all.py             # all versions + sheets + diagrams
python3 tools/build_all.py --video     # also renders/lonewolf_head_turntable.mp4 (needs ffmpeg)
blender -b -P tools/blender_turntable.py -- models/lonewolf_head_ext0mm.stl renders/lonewolf_turntable_blender.mp4
```

`build/` holds temporary render meshes and frames and is not tracked.

Every build also writes `renders/overlay_revision<N>.png` (`tools/overlay_revision.py`). It draws the current +5 mm design on the photo of the last print, registered with the landmarks in `reference/fit/first_print.json`, so each new version can be checked against the chain before printing. Bump `REVISION` in `lonewolf_head.py` for each new printed revision.

## Measurements

Caliper-measured on the original part:

- Overall thickness along the hole: **14.07 mm**
- Thin base plate / fin: **4.76 mm** (raised pad = 9.31 mm)
- GuideLock hole: **oval 10.21 wide × 11.6 tall**
- Stock gap, base plate's nearest corner to the chain: **7.4 mm**

From the straight-on photo (`reference/photos/05_front_straight_on.jpg`), scaled by the
oval hole at 43.5 px/mm. The outline fit is within 0.19 mm RMS:

- Stock outline: 31.5 wide × 25.0 tall, looking down the hole
- Oval's long axis leans about 16° from vertical on the OEM part (`HOLE_TILT`)
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

## Revision 2: after the first +5 print (ASA)

- **Curved pad ends:** the extended pad's bottom now ends in R 5 curves (`PAD_END_R`) instead of R 2 corners, like the OEM's U-shaped bottom, to soften chain slap at the entry and exit. The point nearest the chain is unchanged.
- **Oval tilted back:** the bushing (cam) is fixed and elongated, so the oval sets how the part sits. On the first print the pad's bottom sat about 4° counter-clockwise of the chain under it, with the left end closer. Extended versions now tilt the oval 4° back, top toward the rear (`HOLE_TILT_EXT = -4`), which turns the part 4° clockwise and levels its bottom with the chain. `renders/overlay_revision2.png` shows the printed and revised outlines registered on the photo. The 0 mm version keeps the OEM 16°.
- **Hole clearance:** both oval axes are 0.1 mm larger (`HOLE_CLEARANCE`). The first print was tight on the bushing. Keep this small: the bushing is fixed and the oval is only 1.4 mm longer than it is wide, so 0.1 mm already allows the part to twist about ±4° on it (0.2 mm would allow about ±8°).

## Finishing details

- **Chamfers:** on the base plate's front edges (fin lower edge, leading edge and steep side), 2.2 mm wide × 2.2 mm deep. Only the steep-side width is confirmed from the photo.
- **Rounding:** only the square (90°) edges are rounded: the raised pad's front edge and the back face's outer edge at 1 mm (`EDGE_FILLET`), and both hole rims at 0.5 mm (`HOLE_FILLET`), which keeps more of the bore bearing on the cam. The bevels, the base plate's front-face edges and the inside corner where the pad meets the base stay crisp.
- **Back face:** flat, with no text. `TEXT_LINES` can add raised or engraved text if you want it later.

## Open items

- Confirm the chamfer depth on the original (`CHAMFER_DEPTH`).
- Check the revised +5 print: the bottom should sit parallel to the chain. If it's still off, adjust `HOLE_TILT_EXT`. Negative tilts the oval back and turns the part clockwise, one degree for one degree.
- If the bushing is still tight, raise `HOLE_CLEARANCE` in 0.05 mm steps. Every 0.1 mm adds about ±4° of twist.
- Confirm the chain angle by test-fitting the +5 print. If one end of the leading edge is tighter, adjust `CHAIN_ANGLE`.
- Print in nylon, ASA or PETG, not PLA.

## License

MIT. See `LICENSE`.

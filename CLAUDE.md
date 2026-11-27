# CLAUDE.md — ~/src/3dmodels

3D-printable models with parametric CAD sources (CadQuery). One folder per project.
Owner: Nigel Ellis <nigel@dooger.org>. Printer: Prusa CoreOne.

| Project | Folder |
|---|---|
| Wolf Tooth LoneWolf chainguide head (extended) | `wolftooth-lonewolf-chainguide/` |

## Committing

- **Preview the commit message and the file list before committing to `main`.** Commit only after Nigel approves.
- Author: `Nigel Ellis <nigel@dooger.org>`.
- If git can't run in Claude's shell on Nigel's Mac (deleting lock files needs permission that hasn't been granted), don't keep asking for it. Give Nigel the exact `git add` / `git rm` / `git commit -F - <<'EOF' … EOF` commands to run himself.
- After amending a commit that's already pushed, remind him to use `git push --force-with-lease`.

## New revisions: archive first, automatically

A **new revision** is any change Nigel intends to print and commit as the next version. Before committing one, always do these steps, without waiting to be asked:

1. **Archive the current revision** before changing `REVISION`:
   `python3 tools/archive_revision.py`. This copies `lonewolf_head.py`, `README.md`, `models/` and `renders/` into `revisions/rev<REVISION>/`.
   - If `REVISION` was already bumped and the previous revision was never archived, rebuild the archive from the last commit with `git show <commit>:<path>`, as was done for `revisions/rev1/`.
   - Never overwrite an existing `revisions/rev<N>/` without asking (`--force`).
2. **Bump `REVISION`** in `lonewolf_head.py`.
3. Make the design changes.
4. **Rebuild everything:** `python3 tools/build_all.py --video`. This regenerates the models, sheets, diagrams, turntable and `renders/overlay_revision<REVISION>.png`.
5. **Check the overlay** (`renders/overlay_revision<N>.png`) against the chain before calling the revision done.
6. **Add a row to the version log** at the top of the project README, with the date and a one-line summary per change.
7. Preview the commit (see above).

## Render and output conventions

- Only these versions: **0, +3 and +5 mm**. +5 mm is the one Nigel prints.
- **One format per render:** the parameter diagram and extensions sheet are PDF only. Never save the same render as both PNG and PDF.
- **Always render the overlay** (`tools/overlay_revision.py`) whenever a version is generated. `build_all.py` does this.
- The turntable (`renders/lonewolf_head_turntable.mp4`) and detail views show the **+5 mm** version.
- Keep one current copy of each generated file at the top level; older copies live only in `revisions/`.

## LoneWolf design rules (learned from test fits)

- **The cam is fixed and elongated**, so the oval alone sets how the part sits on the bike.
  - `HOLE_TILT_EXT` is negative when the oval tilts back (top toward the rear), which turns the part clockwise, one degree for one degree.
  - Rev 2 uses −4° on the extended versions; the 0 mm version keeps the OEM 16°.
- **Hole clearance stays small** (`HOLE_CLEARANCE = 0.1`). The oval is only 1.4 mm longer than it is wide, so every 0.1 mm adds about ±4° of twist on the cam.
- **Rounding only on square (90°) edges:**
  - 1 mm (`EDGE_FILLET`) on the pad's front edge and the back outline
  - 0.5 mm (`HOLE_FILLET`) on both hole rims
  - Bevels, the base plate's front-face edges and the pad/base inside corner stay crisp.
- **Leading edge:** stays parallel to the chain (`CHAIN_ANGLE`). The extended pad ends are curved (`PAD_END_R = 5`).
- **Measurements** (calipers and the photo fit) are in the project README. Don't change them without a new measurement from Nigel.
- **Material:** ASA (rev 1 printed in ASA); PETG is the alternative.

## Gotchas

- After an STL or STEP export, CadQuery's `isValid()` can report False on the same in-memory shape. Check validity *before* exporting, or re-import the STEP file to confirm.
- `tools/*` scripts change into the project folder themselves, so run them from anywhere. Temporary files go in `build/` (git-ignored).
- Claude's shell on the Mac has no CadQuery. Do builds in the cloud workspace and copy the results back.

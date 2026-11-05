# Stage 3 mask proposals

Run from the repository root with `.venv\Scripts\python.exe dataset\refine_all_masks.py`.
This writes separate `dataset/masks_proposed/*.png` masks and `proposals.json`.
It does not update the human review log. Protected inputs are checked by SHA-256
before and after processing, including originals, drafts, split files and existing
verified outputs. Raw and training photographs were also checked for byte equality.

The method uses warm saturated cover pixels, a convex support envelope, GrabCut,
connected components, texture-hole filling and substantial dark-object exclusions.
003 and 070 use image-guided corner seeds from the displayed photographs to replace
their incorrect bounding boxes. Those seeds remain unverified proposals.

`statistics.csv` contains pixel area, area change relative to the draft, image-edge
support within a neighborhood of the proposed boundary, dark foreground fraction,
and diagnostic flags. Edge support and area change are QC heuristics, not segmentation
accuracy. No ground-truth IoU or Dice was calculated. Large area changes can reflect
correction of a bad draft rather than a bad proposal. See `summary.json` for totals.

69 cases require human review; notebook_003 has an existing saved human approval. Contact-sheet inspection found particular risks
from missing pale/glare regions, clipped corners and excessive removal around mice.
Inspect 001, 007, 008, 010, 012, 014, 016, 018, 022, 027, 028, 031, 033, 034,
037, 044, 047, 053, 063-070 especially closely, in addition to machine-flagged cases.
Mouse flags are candidates, not a reliable object detector. Border contact is only
a truncation candidate; absence of contact does not establish that an object is complete.
Convex support initializes visible segmentation and does not extend beyond the frame.

Each `notebook_XXX_comparison.jpg` shows photograph, original draft mask, proposal,
and proposal overlay. Four `contact_sheet_*.jpg` pages cover all 70 overlays;
seven `comparison_sheet_*.jpg` pages show all four views for every photograph.

Start `.venv\Scripts\python.exe annotation_tool\server.py --port 8080` and visit
http://localhost:8080/?image=notebook_003 . The tool loads proposal polygons for
untouched records, retaining saved human work and verified annotations. Redraw no
longer automatically selects manually verified. Saving to masks_verified requires
explicit selection of Manually Verified after human review.

Drag green vertices, click edges to insert vertices, Alt-click/right-click to remove
vertices. Add Mouse Occlusion Cutout and trace the visible overlap, then press Enter.
Check frame truncation and reviewer notes. Only after full review select Manually
Verified and Save & Verify Mask (Ctrl+S). This writes masks_verified and updates the
existing review log/QC sheet. Originals and drafts are untouched. Unsaved edits are
in browser memory; complete review and save before navigating away.

No training, calibration, commits, pushes or split changes were performed.


## Latest review preparation

The 69 unapproved proposal masks were regenerated; the approved notebook_003 was protected with simplified outer boundaries of 4-24
vertices. The mask PNGs match the editable polygons and cutouts exactly. The 69 pending images remain
uncertain: no structural diagnostic establishes accurate human ground truth.
`statistics.csv` now includes status, structural validity, vertex count, warnings,
and recommended corrections. Re-run `dataset/refine_all_masks.py` to regenerate.

The annotation app now records explicit inspections separately from approvals.
Enter a reviewer name and check the inspection confirmation after reviewing.
Save inspected work without approval to resume corrections later. Approve only
when complete by selecting Manually Verified and Save & Verify Mask. The header
shows approved and inspected counts; filters include Not Approved, Critical and
Uncertain. Cutouts preserve visibility of the original photograph. Existing saved
human edits and approvals take precedence over new proposals.

Training code and configuration are prepared in models/, with a mandatory
verification gate. No training was run. See models/README.md and
unet_smoke_test.json for synthetic inference validation.


Publication note: browser/server work backups remain local and ignored. Final approval records and the single saved verified mask are included without modification. Duplicate inspection/debug files are omitted.

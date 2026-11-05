# Stage 3 fast human review workflow

Current audit: **70 images, 1 manually approved, 69 remaining, 0 invalid saved
verified masks**. The protected approval is `notebook_003`. Its PNG and approval
record are unchanged. Original photographs, original drafts and committed 49/14/7
split files are unchanged. Automatic proposals are not human-approved ground truth.

The OpenCV pipeline reprocessed the 69 unapproved photographs and skipped the
verified annotation. Per-image random seeds make refinement reproducible without
changing other images when another approval is added. Conservative long-edge fits
were accepted in 35 cases where the edge-support heuristic improved. These are
candidate boundary updates, not measured segmentation-accuracy improvements.
All 70 proposal files pass binary/dimension checks; 69 still require inspection.

QC observations across the remaining images: all 69 need pale-corner, glare and
mouse-edge review; 21 have large area changes relative to the old draft; 11 touch
the frame and require truncation checks; one has an internal mouse/dark-print
cutout candidate; notebook_070 retains an image-guided corner seed requiring review.
Cutouts and edge notches may remove printed or pale notebook pixels; correct those
against the photograph. These warnings are heuristics, not accuracy scores.

Evidence:

- [Validation counts and warnings](../dataset/refinement_qc/review_workflow_validation.json)
- [Per-image QC and recommended corrections](../dataset/refinement_qc/statistics.csv)
- [Updated contact and comparison sheets](../dataset/refinement_qc/)
- [Full current approval audit](stage3_verification_report.md)

Both requested commands were executed using the existing `.venv`:

```powershell
.\.venv\Scripts\python.exe annotation_tool\refine_cli.py qc
.\.venv\Scripts\python.exe dataset\audit_stage3.py
```

QC reports one saved verified mask, valid dimensions/binary values and no errors.
The audit reports 69 missing approvals, intact splits and not ready for training.
No new genuine approval save was performed by automation. Nine backend/data safety
tests pass; isolated browser-logic tests cover navigation, reviewer persistence,
autosave separation, checkbox reset and save success/failure behavior. Approval
success tests use mock storage, never production approval records. No saving error
was observed in these checks; existing verified files are intentionally protected.

## Exact next action

Open http://localhost:8080/?image=notebook_001 (or refresh the existing app).
The default filter is **Not Approved**. Enter your reviewer name once; it persists
in this browser. Inspect the full visible boundary using Fit/zoom and opacity.
Drag green vertices, click edges to add points, or Alt-click/right-click to remove
points. Add mouse overlap cutouts and press Enter to close them. Correct frame
truncation flags and add notes where needed.

Your work backs up automatically without approval. Autosave does not mark an image
inspected and does not write an approval timestamp. Editing clears the inspection
checkbox. After finishing corrections, check **I inspected this image and mask**,
select **Manually Verified**, then press **Ctrl+S** or **Save & Verify Mask**.
A successful explicit save advances to the next unapproved image. A failed save
shows the error and stays on the current image. There is no approve-all action.

Shortcuts: Left/Right or A/D or [/] navigate; N goes to the next unapproved image;
F fits; +/- zoom; Tab hides/shows the sidebar for a larger image view. Wheel zoom,
Space-drag and middle-drag pan remain available. Ctrl+S requires explicit approval
conditions; it is not an unconditional save/verification shortcut.

## Training

The existing CPU U-Net configuration and verified-only loaders remain prepared.
Preflight currently exits 2 for the 69 missing approvals. No training was started.
After all labels are approved and audits pass, use the conditional commands in
[models/README.md](../models/README.md). Training never reads proposed masks as
final ground truth and is never started automatically by the review tool.

No commits or pushes were made.

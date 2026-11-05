# Stage 3: Interactive Annotation & Ground-Truth Refinement Tool

This tool provides an interactive browser-based annotation environment for reviewing and refining notebook segmentation masks for the xis.ai *Measure It — Segmentation and Metric Measurement* project.

## How to Launch

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe annotation_tool\server.py --port 8080
```

Then open your browser to:
**[http://localhost:8080/](http://localhost:8080/)**

*(Or inside VS Code: Press `Ctrl+Shift+P` &rarr; type `Simple Browser: Show` &rarr; enter `http://localhost:8080/`)*

---

## Workflow & Features

### 1. Priority Filtering
- **High / Critical Priority (`notebook_003` and `notebook_070`):** Draft masks were naive axis-aligned boxes that erroneously included background table surface.
- **Held-Out Test Set (`notebook_002`, `008`, `018`, `043`, `052`, `068`, `069`):** Must have pristine ground truth for benchmark evaluation.
- **Border Truncated Images (32 images):** Inspect and check truncation flags (Top, Bottom, Left, Right).
- **Mouse Occlusion Images:** Dark mouse occludes or touches the notebook cover.

### 2. Boundary & Mouse Occlusion Editing
- **Edit Vertices:** Click and drag any green handle to position corners precisely along the notebook edges.
- **Insert Vertex:** Click anywhere along a polygon edge to insert a new corner handle.
- **Delete Vertex:** Alt+Click or Right-Click an existing vertex.
- **Redraw Boundary:** Click "Redraw Notebook Boundary" &rarr; click points along the perimeter &rarr; double-click or press Enter to close.
- **Mouse Occlusion Cutouts (Requirement 6):** Click "+ Add Mouse Occlusion Cutout" &rarr; click points tracing the mouse boundary overlapping the notebook &rarr; press Enter. The tool punches a hole in the notebook mask, guaranteeing mouse pixels are labeled as 0 (background).

### 3. Truncation Recording (Requirement 7)
- When a notebook extends beyond the image frame, check the corresponding border boxes (`Top`, `Bottom`, `Left`, `Right`). Only the visible notebook surface is annotated.

### 4. Verification & Save
- Set Status to **Manually Verified (Human Approved)**.
- Add reviewer notes if applicable.
- Click **Save & Verify Mask** (or `Ctrl+S`).
- **Automated Actions on Save:**
  1. Renders a full-resolution binary PNG (values strictly `{0, 255}`) matching image dimensions.
  2. Saves directly to `dataset/masks_verified/notebook_XXX.png`.
  3. Updates `dataset/annotation_review_log.json` and regenerates `docs/annotation_review_log.md`.
  4. Regenerates the Quality Control contact sheet `dataset/masks_verified/qc_contact_sheet.jpg`.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `[` or `A` | Previous image |
| `]` or `D` | Next image |
| `Ctrl + S` | Save verified mask |
| `F` | Fit image to viewport |
| `Wheel` | Zoom in / out |
| `Middle-Click Drag` or `Space + Drag` | Pan canvas |
| `Enter` | Close and finish drawing polygon |
| `Escape` | Cancel active drawing mode |
| `Alt + Click` or `Right-Click` | Delete vertex |


## Human review tracking

The latest proposal geometry is loaded for untouched images; existing human edits
and approvals take precedence. The header counts approved and explicitly inspected
images. Filters include Not Approved, Critical and Uncertain. Notebook 003 is the
default starting image.

Enter your reviewer name and check **I inspected this image and mask** only after
inspection. **Save inspected work (without approval)** stores work in
`dataset/annotation_review_drafts.json`, without creating ground truth or approval
timestamps. Saved work can be resumed after navigation or reload. Unchecked images
are never recorded as inspected merely by opening them.

For final approval, complete the boundary and mouse cutouts, explicitly choose
**Manually Verified**, and click **Save & Verify Mask** (Ctrl+S). The server requires
the inspection checkbox and reviewer name. Only this explicit save records human
approval and writes `dataset/masks_verified/`. Opening images never approves them.

Generated QC: `dataset/refinement_qc/statistics.csv` and contact/comparison sheets.
The CSV includes status, structural checks, boundary/area diagnostics, uncertainty
and recommended corrections. The geometric diagnostics are not accuracy metrics.


## Fast review and automatic work preservation

The default filter is Not Approved and the starting image is the first unapproved
record. The header shows the image index, identifier, and approved/inspected totals.
After a successful explicit approval, the tool advances to the next unapproved
image, wrapping around the list. A failed save stays on the current image.

Your reviewer name persists in browser local storage. Geometry, cutouts, notes,
truncation flags and unfinished drawing points are backed up automatically in the
browser and to `dataset/annotation_review_drafts.json`. Autosave uses a work-save
timestamp only; it never records inspection or approval. Editing invalidates the
inspection checkbox. Check it after completing your corrections. Existing verified
mask files are protected from overwrite, including via autosave.

Shortcuts: Left/Right arrows or A/D or [/] navigate; N finds the next unapproved
image; F fits; +/- zoom; Tab toggles the sidebar for a large image view; Ctrl+S
attempts explicit approval and requires the reviewer name, inspection checkbox
and Manually Verified status. Wheel zoom and middle/Space-drag pan remain available.
Ctrl+S also works when notes or the reviewer input has focus. Save feedback reports
failures without advancing. A browser backup remains available if server autosave
fails. Opening an image is not an inspection or approval.

Tests: `node tests/test_review_ui.cjs` and
`.venv\Scripts\python.exe -m unittest discover -s tests -v`.

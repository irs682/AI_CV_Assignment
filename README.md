# Measure It — Segmentation and Metric Measurement

**Submission status: partial, as of 2026-11-05.** Branch: `dev-test01`.
Calibration experiments, dataset tooling and the annotation interface work.
**1/70 masks are manually approved. No model training, segmentation scores or
physical measurement results are available.**

| Component | Status | Evidence |
|---|---|---|
| Provisional calibration | Implemented and reproduced on 24/24 supplied checkerboard photos; independent accuracy/scale unvalidated | [Reproduction](docs/submission_evidence/calibration_verification.json), [calibration guide](calibration/README.md) |
| Dataset preparation/integrity | 70 photos, 70 drafts, 70 proposals; dimensions/binary checks pass; committed 49/14/7 split unchanged | [Read-only audit](docs/submission_evidence/dataset_audit.json) |
| Annotation | Review UI works; **1/70 approved**, 69 require human review | [Approval audit](docs/stage3_verification_report.md), [QC CSV](dataset/refinement_qc/statistics.csv) |
| U-Net | Small CPU model, config, verified-only loaders and training gate prepared; untrained | [Configuration](models/unet_laptop.json), [guide](models/README.md) |
| Inference / metric measurement | Unfinished; relevant source files are empty stubs | [Definition of Done](docs/Definition_of_Done.md) |
| Test performance | Not evaluated; no Dice, IoU or physical accuracy results | [Objectives](docs/Objectives.md) |
| Loom demonstration | Outline only; no recording/share URL yet | [Outline](docs/loom_outline.md) |

## Reproduce the working checks

Run these PowerShell commands from the repository root using the existing `.venv`:

```powershell
.\.venv\Scripts\python.exe submission_check.py
```

This runs the read-only dataset/approval audits, verified-mask QC, nine safety/data tests, package
consistency checks, isolated review UI logic tests when Node.js is available, and a live annotation HTTP check. Training preflight is expected
to exit **2** while approvals are missing; the wrapper records that as a successful
safety check, not successful training. It never invokes the training entry point.
Start the app below first if it is not already running. Results are written to
`docs/submission_evidence/`; checks do not create approvals or regenerate splits.

Individual checks:

```powershell
.\.venv\Scripts\python.exe dataset\audit_dataset.py
.\.venv\Scripts\python.exe dataset\audit_stage3.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node tests/test_review_ui.cjs
.\.venv\Scripts\python.exe models\training_pipeline.py --check-only
```

Safe calibration reproduction, writing a new timestamped directory:

```powershell
.\.venv\Scripts\python.exe calibration\verify_calibration.py
.\.venv\Scripts\python.exe calibration\compare_outlier.py
```

The first command calls the existing calibration implementation with separate
output paths and checks preservation hashes. Do not use the historical baseline
`calibration/calibration.py` command to reproduce over archived parameters.
Likewise, `dataset/verify_and_prepare_dataset.py` rebuilds image copies and splits;
use the non-mutating audit commands above for the finalized submission dataset.

## Human annotation

If the server is not running:

```powershell
.\.venv\Scripts\python.exe annotation_tool\server.py --port 8080
```

Open [the first pending review](http://localhost:8080/?image=notebook_001). Drag vertices, click
edges to insert points, and Alt-click/right-click to remove them. Trace overlapping
mouse pixels using **Add Mouse Occlusion Cutout**, then Enter. Zoom and opacity
controls help inspect pale edges, glare, occlusion and frame truncation.

After inspection, enter your reviewer name and check the inspection confirmation.
Use **Save inspected work (without approval)** for unfinished corrections. For
complete masks explicitly select **Manually Verified** and **Save & Verify Mask**
(Ctrl+S). Only that human action writes a verified mask and approval timestamp.
The reviewer name persists, work autosaves without approval, and successful approval advances to the next unapproved image. The header shows inspected/approved progress; viewing a photo does not approve it.
All automatic proposals remain unverified; saved human work takes precedence.

## Measured calibration results and limits

| Fit | Images | RMS reprojection error |
|---|---:|---:|
| 1500x1125 baseline | 9 | 0.318996 px |
| 1500x2000 baseline | 15 | 1.527988 px |
| 1500x2000 excluding only checkerboard_002 | 14 | 0.501806 px |

These are fitted corner residuals, not independent camera or physical measurement
accuracy. Original and trial artifacts are preserved. Photos came through a PDF;
prior processing and physical checkerboard square size are unverified. Unit-square
calibration does not establish millimetres. Calibration has not been applied to
the notebook dataset. No physical notebook dimensions have been assumed.

## Environment and continuation

The checked Windows environment is recorded in
[environment.txt](docs/submission_evidence/environment.txt) and
[environment-lock.txt](docs/submission_evidence/environment-lock.txt). A fresh
environment installation has not been revalidated by this audit. On a fresh copy,
create a venv if needed and install the recorded packages; the CPU PyTorch wheel
requires the official CPU package index:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r docs\submission_evidence\environment-lock.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

Do not recreate an existing working `.venv` unnecessarily. The CPU U-Net has
488,705 parameters, 256-pixel letterboxed inputs, batch size 2, fixed seed 224,
binary loss and validation early stopping. Its synthetic forward-pass smoke check
is not training or an accuracy evaluation. Final loaders use only saved human-
verified masks, with a mandatory all-image approval and integrity gate.

Before a complete submission: approve all required masks, pass preflight, train
and evaluate, implement inference/metric conversion with independently verified
reference geometry, and record an actual demonstration. No training is authorized
by these reproduction instructions while labels remain unverified.

See [submission readiness](docs/submission_readiness_report.md),
[Plan](docs/Plan.md), [Objectives](docs/Objectives.md), and
[Definition of Done](docs/Definition_of_Done.md).


Latest review workflow: [1 approved / 69 remaining, autosave and fast navigation](docs/stage3_review_workflow.md). Older dated readiness reports are historical snapshots.

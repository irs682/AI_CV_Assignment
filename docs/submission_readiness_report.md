# Submission readiness report

Audit date: 2026-11-05 (Asia/Shanghai). Branch: `dev-test01`.

**Ready for an honest partial submission review; not a complete end-to-end
assessment implementation.** This report does not guarantee assessment acceptance.
This report records implementation readiness. Commit, push and pull-request disposition are checked separately during publication; no merge or submission email is part of this task.

## Annotation and dataset result

| Check | Actual result |
|---|---:|
| Supplied notebook photographs | 70 |
| Raw/training photograph byte matches | 70/70 |
| Structurally valid original draft masks | 70/70 |
| Structurally valid automatic proposals | 70/70 |
| Saved verified PNG masks | **1 (notebook_003)** |
| Complete human-approval records | **1** |
| Required human reviews remaining | **69** |
| Committed train/validation/test counts | **49 / 14 / 7**, unchanged |
| Exact duplicate photograph groups | 0 |

On-disk review records contain 68 unresolved, 1 automatically proposed and 1 manually verified status;
the app merges the separate 70-proposal manifest for review. Neither proposed nor
unresolved status constitutes manual approval. A complete approval requires an
explicit manually_verified record, reviewer, timestamp and saved mask. One such
record/file pair exists for notebook_003, saved by the human reviewer. It has been preserved unchanged. Structural dimension/binary checks establish
file integrity, not accurate object boundaries or verified ground truth. The latest fast-review workflow supports persistent reviewer name, work-only autosave and next-unapproved navigation after explicit approval.

All images except `notebook_003` remain unverified (69 pending). Pale/glare corners,
mouse exclusion boundaries and visible cropped regions need human inspection.
The [per-image QC CSV](../dataset/refinement_qc/statistics.csv) provides warnings and
recommended corrections; [the approval audit](stage3_verification_report.md) lists
every blocked image. Existing near-duplicate split grouping was preserved; this
audit does not independently establish absence of visual near-duplicate leakage.

Evidence: [dataset audit](submission_evidence/dataset_audit.json),
[preservation hashes](submission_evidence/dataset_preservation_sha256.json),
[approval audit JSON](../dataset/stage3_final_qc/verification_report.json).

## Calibration implementation and measured evidence

The existing implementation was executed on all 24 checkerboard photographs using
`calibration/verify_calibration.py`, which redirects outputs to a new timestamped
directory. All 24 detected 63 internal corners; no failures occurred. Both
resolution-cohort fits reproduced the archive within approximately 3e-15 px RMS.
Original images, parameters and prior comparison artifacts passed SHA-256
preservation checks. The separate outlier experiment was also rerun successfully.

| Calibration fit | Images | RMS reprojection error |
|---|---:|---:|
| 1500x1125 baseline | 9 | 0.318996 px |
| 1500x2000 baseline | 15 | 1.527988 px |
| Excluding only checkerboard_002 from 1500x2000 | 14 | 0.501806 px |
| Original model on those same retained images | 14 | 0.536554 px |

These are fitted corner residuals, not independent calibration or measurement
accuracy. The 67.1590% outlier-fit reduction is not a claim of physical accuracy.
PDF image processing history, matching phone settings and checkerboard square
dimensions remain unverified. There is no established millimetre scale.

Evidence: [baseline reproduction](submission_evidence/calibration_verification.json),
[outlier reproduction](submission_evidence/outlier_verification.json),
[preserved calibration explanation](../calibration/README.md).
New full outputs are under `calibration/reproductions/20261105T081036331500Z/`
and `calibration/comparisons/exclude_002_20261105T081203267236Z/`.

## Runtime and reproducibility checks

The documented `.venv\Scripts\python.exe submission_check.py` command passed:

| Command / check | Result |
|---|---|
| `dataset/audit_dataset.py` | Exit 0: 70 photos and both mask inventories valid; raw/training copies identical; committed splits unchanged |
| `dataset/audit_stage3.py` | Exit 0: reports one valid approval, 69 pending and not ready for training |
| `python -m unittest discover -s tests -v` | Nine tests pass: approval rejection, human-work preservation, binary/aspect-preserving loading, polygon QC, training gate |
| `models/training_pipeline.py --check-only` | Expected exit 2: blocks the 69 missing approvals before model initialization |
| `python -m pip check` | Exit 0: no broken package requirements |
| Annotation page and `/api/images` | HTTP reachable at localhost:8080; 70 records, one approved, review controls present |
| `calibration/verify_calibration.py` | Exit 0: both baseline cohorts reproduced and archived files preserved |
| `calibration/compare_outlier.py` | Exit 0: baseline/outlier comparison reproduced; originals unchanged |

The historical dataset preparation command was inspected, not rerun against the
final dataset: it copies images and regenerates splits. A read-only audit was
added instead. HTTP checks do not exercise every browser interaction. A fresh
machine/clean-environment install has not been revalidated. The checked Windows
environment is Python 3.13.7, OpenCV 5.0.0, NumPy 2.5.4 and CPU PyTorch 2.15.0+cpu.

Evidence: [exact command outputs](submission_evidence/command_checks.json),
[environment](submission_evidence/environment.txt),
[package lock](submission_evidence/environment-lock.txt).

## Training, inference and measurement status

The inspected laptop configuration uses a 488,705-parameter U-Net, 256-pixel
letterboxing, batch size 2, four CPU threads, seed 224, BCE-with-logits plus soft
Dice loss, AdamW, validation-loss early stopping and zero loader workers.
Split hashes are pinned. Final training/evaluation loaders read only
`dataset/masks_verified/`, and preflight requires all 70 approvals before model
initialization. Configuration exists; training has not started. `models/weights/`
contains only `.gitkeep`, with no checkpoint or history.

The preserved [synthetic forward-pass check](../dataset/refinement_qc/unet_smoke_test.json)
is an implementation smoke test, not training or accuracy evaluation. No new
training or optimization was performed during this readiness audit.

`inference/predict.py`, `inference/measure.py`, `measurement/accuracy.py`, and
standalone `calibration/undistort.py` are empty. Calibration's own preview generation
does work inside `calibration.py`; it does not constitute an end-to-end inference
or metric measurement pipeline. Model evaluation code is prepared but unexecuted.
There are no model Dice/IoU scores, physical reference dimensions or measurement
accuracy results to submit.

## Documents and demonstration

[README](../README.md), [Plan](Plan.md), [Objectives](Objectives.md), and
[Definition of Done](Definition_of_Done.md) now explicitly separate completed
tooling/experiments, partial annotation/training preparation, and unfinished
outcomes, with evidence links. Earlier blanket near-duplicate-leakage and image
integrity wording was qualified to match what the audit actually establishes.
Planning targets of <=2 mm MAE and >=0.90 Dice remain unevaluated objectives,
not achieved results or independently confirmed assessment thresholds.

[The three-minute Loom outline](loom_outline.md) covers only calibration evidence,
data audits, the annotation UI and the training gate. A recording/share URL does
not yet exist; this task did not record, upload or email a demonstration.

## Git changes suitable for a partial-submission commit

The submission includes the implementation/evidence groups below, with private working drafts, caches and redundant debug artifacts excluded. Existing user changes and the genuine approval are preserved. `git diff --check` passes. Review and commit the following logical groups
only as a documented partial implementation:

1. **Documents and evidence:** root README; Plan/Objectives/Definition of Done;
   updated calibration/dataset documentation; Stage 3 reports; this report;
   Loom outline; `docs/submission_evidence/` JSON/text evidence and package lock.
2. **Audits and calibration reproducibility:** `submission_check.py`,
   `dataset/audit_dataset.py`, `dataset/audit_stage3.py`, and
   `calibration/verify_calibration.py`. The original calibration implementation
   and archived measured outputs are unchanged.
3. **Annotation/refinement implementation:** `annotation_tool/` changes,
   `dataset/refine_all_masks.py`, `dataset/masks_proposed/`, and selected
   `dataset/refinement_qc/` / `dataset/stage3_final_qc/` reports, CSVs and sheets.
   Automatic proposal assets must remain labelled unverified.
4. **Training preparation and tests:** `models/train.py`, `models/evaluate.py`,
   `models/training_pipeline.py`, `models/unet_laptop.json`, training requirements,
   model README and `tests/test_stage3_safety.py`. Commit as prepared, untrained code.
5. **Optional full reproduction artifacts:** new calibration reproduction and
   comparison folders support the compact JSON evidence. Include the cited
   parameter/metadata/preview artifacts if distributing the full evidence bundle.

Leave out `.venv/`, caches and server logs (already ignored). The redundant
`dataset/inspection_1.jpg`, `dataset/inspection_2.jpg` and generated
`dataset/refinement_qc/app_syntax_check.js` are not required in a curated submission.
Do not add a placeholder QC image as evidence that verified masks exist. Do not
use a blanket staging command without reviewing the untracked artifacts.

## Remaining blockers

1. 69 masks need genuine human correction/approval; training preflight fails.
2. Training, validation checkpoint selection and held-out model evaluation are unrun.
3. Inference, physical scale/reference validation and metric measurement are unfinished.
4. Independent camera/measurement accuracy has not been established.
5. Loom recording and its actual share URL remain missing.

The project can be presented honestly as a reproducible partial implementation.
It cannot be presented as a completed segmentation-and-metric-measurement solution.


Publication prerequisites observed: GitHub CLI is unavailable on PATH and in standard installation locations. The remote currently advertises only dev-test01, with no main base branch. Do not create main or merge anything implicitly; PR creation into main remains blocked unless the repository owner establishes the intended base branch.

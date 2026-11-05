# Dataset: Notebook & Mouse Segmentation

This directory contains the dataset for the xis.ai *Measure It — Segmentation and Metric Measurement* project.

## Directory Structure

- `raw_images/`: 70 original photographs of a floral notebook and mouse (`notebook_001.jpg` to `notebook_070.jpg`), preserved unaltered.
- `images/`: 70 training-ready copies, verified via SHA-256 against `raw_images/`. No unverified camera calibration distortion correction has been applied.
- `masks/`: 70 draft segmentation masks (`notebook_001.png` to `notebook_070.png`). Values are strictly 0 (background) and 255 (notebook). **These are unverified draft masks requiring manual annotation review before model training.**
- `splits/`: Fixed train/validation/test partitions:
  - `train.txt`: 49 images (6 portrait, 43 landscape)
  - `val.txt`: 14 images (2 portrait, 12 landscape)
  - `test.txt`: 7 images (1 portrait, 6 landscape)
- `verification_previews/`:
  - `contact_sheet_part1.jpg`: Cards 1–35 overlay previews.
  - `contact_sheet_part2.jpg`: Cards 36–70 overlay previews.
  - `contact_sheet_master.jpg`: Full $10 \times 7$ grid of all 70 images with mask boundaries and split labels.
- `verify_and_prepare_dataset.py`: Fully reproducible verification and preparation script.
- `dataset_verification_metadata.json`: Machine-readable audit records, SHA-256 hashes, and split metadata.

## Provenance and Limitations

1. **PDF Extraction:** All photographs were extracted from a user-uploaded PDF document. The original full-resolution Android RAW/JPEG files have not been verified. Prior resampling, downscaling, or compression cannot be ruled out.
2. **Camera Calibration:** Camera parameters fitted in Stage 1 were derived from PDF checkerboard views without physical scale ground truth. In accordance with task requirements, no camera calibration undistortion has been applied to dataset images.
3. **Reproducibility:** Splits were generated using Python random seed `224`, with resolution stratification and an intended grouping of similar photo bursts. The current audit confirms unchanged split membership and no exact duplicate photographs; it does not independently establish zero near-duplicate leakage.

For the complete verification audit and per-image defect catalog, see [`docs/dataset_verification_report.md`](../docs/dataset_verification_report.md).


Current non-mutating audits: `.venv\Scripts\python.exe dataset\audit_dataset.py` and `.venv\Scripts\python.exe dataset\audit_stage3.py`. The historical `verify_and_prepare_dataset.py` rebuilds image copies and split lists; do not run it against the finalized submission dataset. There are 70 separate automatic proposals and 1 saved human-approved mask (notebook_003), with 69 pending reviews as of the submission readiness audit.

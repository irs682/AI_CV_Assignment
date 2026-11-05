# Stage 3 automated refinement and review preparation

70 photographs processed; 70 separate proposals generated; 70 passed structural checks; 0 processing failures; 1 manually verified mask (notebook_003). The remaining 69 require human review.

Current proposal boundaries are summarized per image in the QC CSV; preserving visible cutouts and frame clipping where detected. Binary PNGs and editable polygons match exactly for all 70. Color anchors, GrabCut, dark-object exclusions and contour simplification are heuristic proposals, not ground truth. Pale corners, glare and mouse edges remain review risks.

## Deliverables

- Masks: dataset/masks_proposed/
- Per-image QC with recommended corrections: dataset/refinement_qc/statistics.csv
- Four overlay contact sheets and seven four-view comparison sheets: dataset/refinement_qc/
- Approval audit: docs/stage3_verification_report.md
- Training configuration: models/unet_laptop.json
- CPU U-Net, verified-only loaders and mandatory preflight: models/training_pipeline.py

## Human review

Open http://localhost:8080/?image=notebook_001 . The application defaults to the first unapproved image and currently reports Approved 1/70. Viewing an image never records inspection or approval.

Drag green handles, click edges to insert vertices, and Alt-click/right-click to delete. Add Mouse Occlusion Cutout and trace only the overlap; Enter closes the polygon. Use wheel zoom, Fit, opacity and next/previous controls. Check frame-contact flags against the photo.

Enter your reviewer name and check I inspected this image and mask after inspection. Save inspected work without approval stores resumable edits separately. For completed masks explicitly select Manually Verified, then Save & Verify Mask (Ctrl+S). Only that human action writes an approval timestamp and verified mask. Existing human work takes precedence over regenerated proposals.

## Validation and training readiness

Nine safety/data tests pass; isolated interface logic tests also pass. Model smoke test: {"torch_version": "2.15.0+cpu", "parameters": 488705, "input_shape": [2, 3, 256, 256], "output_shape": [2, 1, 256, 256], "finite": true, "mode": "synthetic inference only; no optimization or training"}. The model was evaluated on synthetic zero inputs only, without optimization or project-image training. CPU PyTorch is installed. CLI preflight was run and correctly rejected the 69 missing approvals before model initialization.

The laptop configuration uses a 488,705-parameter U-Net, 256-pixel aspect-preserving letterboxing, batch 2, CPU threads 4, seed 224, BCE-with-logits plus soft Dice loss, AdamW and validation-loss early stopping. Test data is reserved for explicit post-training evaluation. No accuracy, IoU, Dice evaluation result or physical measurement is claimed.

Committed train/validation/test content and counts remain 49/14/7. All raw and training photo copies are byte-identical; protected photos, original draft masks, review logs and verified artifacts passed SHA-256 preservation checks. No training or fabricated accuracy results are included. Calibration evidence and publication status are documented separately.

## Remaining corrections

All images except the protected notebook_003 require visual review; the CSV gives per-image warnings and recommended corrections. Highest-risk examples observed on contact sheets include 001, 007, 008, 010, 012, 014, 016, 018, 022, 027, 028, 031, 033, 034, 037, 044, 047, 053 and 063-070. Inspect cutouts for removed printed areas and recover visible pale/glare corners where necessary.

| Image | Vertices | Additional QC warnings |
|---|---:|---|
| notebook_001 | 20 | Visual boundary and occlusion review |
| notebook_002 | 22 | Visual boundary and occlusion review |
| notebook_003 | 4 | image_guided_corner_seed_requires_review, large_area_change |
| notebook_004 | 21 | large_area_change |
| notebook_005 | 21 | large_area_change |
| notebook_006 | 23 | Visual boundary and occlusion review |
| notebook_007 | 24 | large_area_change |
| notebook_008 | 21 | large_area_change, frame_contact_check_truncation |
| notebook_009 | 24 | large_area_change |
| notebook_010 | 24 | Visual boundary and occlusion review |
| notebook_011 | 19 | Visual boundary and occlusion review |
| notebook_012 | 24 | Visual boundary and occlusion review |
| notebook_013 | 23 | large_area_change, frame_contact_check_truncation |
| notebook_014 | 19 | large_area_change |
| notebook_015 | 24 | Visual boundary and occlusion review |
| notebook_016 | 14 | Visual boundary and occlusion review |
| notebook_017 | 17 | Visual boundary and occlusion review |
| notebook_018 | 20 | Visual boundary and occlusion review |
| notebook_019 | 22 | large_area_change |
| notebook_020 | 24 | Visual boundary and occlusion review |
| notebook_021 | 18 | Visual boundary and occlusion review |
| notebook_022 | 24 | large_area_change |
| notebook_023 | 16 | Visual boundary and occlusion review |
| notebook_024 | 23 | Visual boundary and occlusion review |
| notebook_025 | 21 | Visual boundary and occlusion review |
| notebook_026 | 24 | Visual boundary and occlusion review |
| notebook_027 | 23 | Visual boundary and occlusion review |
| notebook_028 | 24 | large_area_change |
| notebook_029 | 24 | Visual boundary and occlusion review |
| notebook_030 | 24 | Visual boundary and occlusion review |
| notebook_031 | 11 | large_area_change |
| notebook_032 | 23 | Visual boundary and occlusion review |
| notebook_033 | 24 | frame_contact_check_truncation |
| notebook_034 | 24 | Visual boundary and occlusion review |
| notebook_035 | 21 | Visual boundary and occlusion review |
| notebook_036 | 22 | frame_contact_check_truncation |
| notebook_037 | 24 | Visual boundary and occlusion review |
| notebook_038 | 15 | Visual boundary and occlusion review |
| notebook_039 | 19 | Visual boundary and occlusion review |
| notebook_040 | 23 | Visual boundary and occlusion review |
| notebook_041 | 24 | frame_contact_check_truncation |
| notebook_042 | 19 | Visual boundary and occlusion review |
| notebook_043 | 24 | Visual boundary and occlusion review |
| notebook_044 | 24 | frame_contact_check_truncation |
| notebook_045 | 18 | Visual boundary and occlusion review |
| notebook_046 | 12 | Visual boundary and occlusion review |
| notebook_047 | 23 | frame_contact_check_truncation |
| notebook_048 | 24 | large_area_change |
| notebook_049 | 11 | Visual boundary and occlusion review |
| notebook_050 | 16 | large_area_change |
| notebook_051 | 17 | large_area_change |
| notebook_052 | 21 | Visual boundary and occlusion review |
| notebook_053 | 23 | Visual boundary and occlusion review |
| notebook_054 | 23 | Visual boundary and occlusion review |
| notebook_055 | 14 | Visual boundary and occlusion review |
| notebook_056 | 16 | large_area_change |
| notebook_057 | 15 | large_area_change |
| notebook_058 | 24 | Visual boundary and occlusion review |
| notebook_059 | 22 | Visual boundary and occlusion review |
| notebook_060 | 24 | frame_contact_check_truncation |
| notebook_061 | 23 | large_area_change, frame_contact_check_truncation |
| notebook_062 | 20 | Visual boundary and occlusion review |
| notebook_063 | 19 | large_area_change |
| notebook_064 | 23 | large_area_change |
| notebook_065 | 24 | large_area_change, frame_contact_check_truncation |
| notebook_066 | 24 | Visual boundary and occlusion review |
| notebook_067 | 22 | large_area_change |
| notebook_068 | 20 | Visual boundary and occlusion review |
| notebook_069 | 23 | Visual boundary and occlusion review |
| notebook_070 | 13 | image_guided_corner_seed_requires_review, mouse_or_dark_print_cutout_candidate |
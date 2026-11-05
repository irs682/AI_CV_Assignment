# Objectives, targets and measured evidence

Status date: 2026-11-05. Targets are planning objectives retained from the original
project documents, not achieved results or independently confirmed assessment thresholds.

| Objective | Target | Current result / status |
|---|---|---|
| MO-1: measurement accuracy | Mean absolute error <=2 mm on at least 20 independently referenced held-out measurements | Unfinished: no reference dimensions or measurement results. |
| MO-2: segmentation accuracy | Mean per-image test Dice >=0.90 | Unfinished: no trained checkpoint, predictions or approved test masks. |
| Dataset integrity | Preserve 70 supplied photos and fixed 49/14/7 membership | Completed structural checks: copies match, draft/proposal masks are binary and dimension-matched, splits unchanged. |
| Human annotation | 70 manually corrected and approved masks | Partial workflow; labels unfinished: **1/70 approved; 69 pending**. |
| Calibration reproducibility | Reproduce archived fits without overwriting them | Completed experiment: 24/24 detected; cohort RMS reproduced to numerical precision. Camera accuracy remains unvalidated. |

| Calibration experiment | Images | RMS reprojection error |
|---|---:|---:|
| 1500x1125 baseline | 9 | 0.318996 px |
| 1500x2000 baseline | 15 | 1.527988 px |
| 1500x2000 excluding only checkerboard_002 | 14 | 0.501806 px |
| Original model on the same 14 retained views | 14 | 0.536554 px |

The 67.1590% reduction compares fitted corner residuals on different fit sets;
it is not independent camera or measurement accuracy. Checkerboard 002's archived
per-image RMS is 5.566935 px. All 63 corners were detected using the classic fallback;
localization concerns are plausible, but the cause is not established.

The photographs came through a PDF. Prior geometric processing and camera settings
are not independently verified. Checkerboard square size is unmeasured; object
coordinates use arbitrary unit squares. No millimetre scale, physical object size,
segmentation accuracy or end-to-end measurement accuracy is claimed.

Evidence: [calibration verification](submission_evidence/calibration_verification.json),
[archived calibration details](../calibration/README.md),
[dataset audit](submission_evidence/dataset_audit.json),
[approval audit](stage3_verification_report.md).

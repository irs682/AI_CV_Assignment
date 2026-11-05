# Plan and actual delivery status

Status date: 2026-11-05. Overall: partial submission. The original eight-hour
workflow was a proposed time box; actual elapsed effort was not tracked.

| Work item | Original allocation | Status and evidence |
|---|---:|---|
| Calibration | 1 h | Partial: implementation reproduces on 24/24 images; independent accuracy and physical scale unvalidated. [Evidence](submission_evidence/calibration_verification.json). |
| Image collection/preparation | 1 h | Partial: 70 supplied PDF-extracted photos prepared; raw/training copies match; committed 49/14/7 splits preserved. Original phone settings/reference dimensions unverified. [Audit](submission_evidence/dataset_audit.json). |
| Annotation | 1.5 h | Partial: 70 proposals and working review/QC tooling; **1/70 approved; 69 pending**. [Blockers](stage3_verification_report.md). |
| Segmentation training | 1.5 h | Prepared, not trained: CPU U-Net/config and verified-only loaders; approval gate blocks training. [Guide](../models/README.md). |
| Pixel-to-mm conversion | 1 h | Unfinished: no verified physical scale; measurement code is empty. |
| Accuracy evaluation | 0.75 h | Unfinished: no model predictions, test Dice/IoU or physical measurement errors. |
| Documentation | 0.75 h | Partial-submission documents complete; final trained-system documentation conditional on future work. |
| Demonstration | 0.5 h | Outline prepared; recording unfinished. [Loom outline](loom_outline.md). |

Deadline plan: submit only the demonstrated partial scope, preserve measured
calibration artifacts, label automatic masks unverified, and disclose blockers.
Record the working-feature demonstration if time permits; an outline is not a video.

Completion plan: manually approve corrected masks; rerun audits and training
preflight; then train and select a checkpoint using validation data. Implement
inference and metric conversion with independently verified in-plane reference
geometry, evaluate on held-out data, and record actual results. Do not infer
reference sizes or performance numbers to fill missing evidence.

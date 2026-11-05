# Definition of Done and current acceptance status

Status date: 2026-11-05. Overall: **partial submission**. A checked item applies
only to its stated limited deliverable, not completion of the entire assessment.

Completed with evidence:

- [x] Provisional calibration runs on 24 supplied checkerboard photographs, with separate resolution models. [Reproduction](submission_evidence/calibration_verification.json).
- [x] Original calibration parameters, residuals, previews and outlier experiment preserved; preservation hashes pass.
- [x] PDF provenance, unknown prior processing and unverified physical square size disclosed. [Calibration README](../calibration/README.md).
- [x] 70 photos decode; raw/training copies match. All draft/proposal masks pass dimension and binary checks. [Dataset audit](submission_evidence/dataset_audit.json).
- [x] Committed split content stays 49/14/7, with no overlapping names or exact duplicate photos. Visual near-duplicate leakage is not independently certified.
- [x] Automatic proposals, QC sheets and human-review UI are available and labelled unverified. [Preparation report](stage3_preparation_report.md).
- [x] U-Net configuration, verified-only loaders and approval gate implemented; safety/data tests pass. This is not completed training. [Command evidence](submission_evidence/command_checks.json).
- [x] Partial-submission documents and working-feature demo outline prepared. [README](../README.md), [outline](loom_outline.md).

Partial or unfinished requirements:

- [ ] Final camera accuracy independently validated on separate images and known geometry at matching camera settings.
- [ ] Physical scale established from independently verified reference dimensions.
- [ ] All notebook annotations manually inspected, corrected and approved: **1/70 approved; 69 pending**. [Full blocker list](stage3_verification_report.md).
- [ ] Model trained; training history and validation-selected checkpoint recorded. No checkpoint exists.
- [ ] Standalone inference produces notebook masks: `inference/predict.py` is empty.
- [ ] Metric conversion produces physical measurements: `inference/measure.py` and `measurement/accuracy.py` are empty. Standalone `calibration/undistort.py` is also empty; calibration previews run inside `calibration.py`.
- [ ] Segmentation and measurement performance evaluated on held-out data. No test Dice, IoU or measurement-error results exist.
- [ ] Working end-to-end demonstration recorded and linked. An outline does not meet this condition.

Training remains blocked until required human approvals and structural checks pass.
No automatic approvals, invented timestamps, dimensions or model scores may fill
missing evidence.

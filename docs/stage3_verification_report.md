# Stage 3 verification report

Dataset ready for U-Net training: **NO**.

Photographs: 70. Verified PNG files: 1. Complete manual approval records: 1. Approval records with corresponding files: 1.

Structurally valid verified masks: 1. Unverified or problematic cases: 69.

Approval evidence means status manually_verified plus nonempty verified_at and verified_by, and a corresponding saved PNG. Metadata records approval; it cannot independently prove a human performed the review. Proposed masks are never counted as approvals.

Validation checks single-channel uint8, matching image dimensions, values limited to 0 and 255, and nonempty/non-full foreground. These checks do not establish segmentation accuracy. With no verified mask, dimension/binary and boundary validation cannot pass for that image.

Splits: {"train": {"count": 49, "matches_committed_content": true}, "val": {"count": 14, "matches_committed_content": true}, "test": {"count": 7, "matches_committed_content": true}}. Protected photographs, draft masks, verified artifacts, split files and review log unchanged by SHA-256.

Final contact sheets are in dataset/stage3_final_qc/. Missing verified masks are explicitly labelled; proposals are not displayed as approved ground truth.

## Remaining cases

| Image | Split | Review status | Blockers |
|---|---|---|---|
| notebook_001 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_002 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_004 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_005 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_006 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_007 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_008 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_009 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_010 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_011 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_012 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_013 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_014 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_015 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_016 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_017 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_018 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_019 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_020 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_021 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_022 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_023 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_024 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_025 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_026 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_027 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_028 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_029 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_030 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_031 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_032 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_033 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_034 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_035 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_036 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_037 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_038 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_039 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_040 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_041 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_042 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_043 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_044 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_045 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_046 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_047 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_048 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_049 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_050 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_051 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_052 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_053 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_054 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_055 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_056 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_057 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_058 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_059 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_060 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_061 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_062 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_063 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_064 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_065 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_066 | val | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_067 | train | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_068 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_069 | test | unresolved | missing_complete_human_approval_record, missing_verified_mask |
| notebook_070 | train | automatically_proposed | missing_complete_human_approval_record, missing_verified_mask |

## Next steps

Review each mask in http://localhost:8080/?image=notebook_003 . Correct notebook edges, exclude overlapping mouse pixels, and check visible truncation. Explicitly select Manually Verified only after completing review, then Save & Verify Mask (Ctrl+S). Re-run `.venv\Scripts\python.exe dataset\audit_stage3.py` after saving approvals.

The lightweight U-Net configuration and verified-only loaders are prepared in models/. Training remains blocked until all required masks are approved and valid. No training was started, and no commits or pushes were performed.
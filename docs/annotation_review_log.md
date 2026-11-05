# Ground-Truth Segmentation Annotation Review Log

**Assessment:** xis.ai *Measure It — Segmentation and Metric Measurement*  
**Stage:** Stage 3 — Segmentation Ground-Truth Refinement  
**Directory for Verified Ground Truth:** `dataset/masks_verified/`  

## Annotation Status Taxonomy
- **`unresolved`**: Initial draft mask imported. Has not undergone boundary correction or manual verification.
- **`automatically_proposed`**: Machine-assisted boundary proposal generated (e.g. GrabCut/edge fitting), but pending human inspection.
- **`manually_verified`**: Inspected, boundary-corrected, mouse occlusion excluded, and confirmed by reviewer.

## Summary Metrics
- **Total Images:** 70
- **Manually Verified:** 1 / 70
- **Automatically Proposed:** 1 / 70
- **Unresolved:** 68 / 70
- **High / Critical Priority Images:** 9

## Detailed Image Review Register

| Image | Split | Priority | Dimensions | Status | Truncation | Mouse Occlusion | Notes |
|---|---|---|---|---|---|---|---|
| `notebook_001` | TRAIN | MEDIUM | 1500x2000 | `unresolved` | None | Yes | - |
| `notebook_002` | TEST | HIGH | 1500x2000 | `unresolved` | None | Yes | - |
| `notebook_003` | TRAIN | CRITICAL | 1500x1125 | `manually_verified` | None | Yes | Automatic OpenCV proposal; inspect all boundaries, glare and mouse exclusions before approval. |
| `notebook_004` | TRAIN | MEDIUM | 1500x2000 | `unresolved` | None | Yes | - |
| `notebook_005` | VAL | MEDIUM | 1500x2000 | `unresolved` | None | Yes | - |
| `notebook_006` | TRAIN | MEDIUM | 1500x2000 | `unresolved` | right | Yes | - |
| `notebook_007` | TRAIN | MEDIUM | 1500x2000 | `unresolved` | None | Yes | - |
| `notebook_008` | TEST | HIGH | 1500x1125 | `unresolved` | top, bottom, left, right | Yes | - |
| `notebook_009` | TRAIN | MEDIUM | 1500x2000 | `unresolved` | top, right | Yes | - |
| `notebook_010` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom, right | Yes | - |
| `notebook_011` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_012` | VAL | MEDIUM | 1500x2000 | `unresolved` | right | Yes | - |
| `notebook_013` | TRAIN | MEDIUM | 1500x2000 | `unresolved` | top, left, right | Yes | - |
| `notebook_014` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | left | Yes | - |
| `notebook_015` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_016` | VAL | MEDIUM | 1500x1125 | `unresolved` | top | Yes | - |
| `notebook_017` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_018` | TEST | HIGH | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_019` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_020` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | top | Yes | - |
| `notebook_021` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_022` | VAL | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_023` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_024` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_025` | VAL | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_026` | VAL | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_027` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_028` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | left | Yes | - |
| `notebook_029` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_030` | VAL | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_031` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | top, bottom | Yes | - |
| `notebook_032` | VAL | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_033` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | left | Yes | - |
| `notebook_034` | VAL | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_035` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_036` | VAL | MEDIUM | 1500x1125 | `unresolved` | left | Yes | - |
| `notebook_037` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | left | Yes | - |
| `notebook_038` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_039` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_040` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | left | Yes | - |
| `notebook_041` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_042` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_043` | TEST | HIGH | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_044` | VAL | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_045` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_046` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_047` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_048` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_049` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_050` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_051` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom, left, right | Yes | - |
| `notebook_052` | TEST | HIGH | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_053` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_054` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_055` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_056` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | right | Yes | - |
| `notebook_057` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom, right | Yes | - |
| `notebook_058` | VAL | NORMAL | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_059` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_060` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom | Yes | - |
| `notebook_061` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | bottom, right | Yes | - |
| `notebook_062` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_063` | VAL | MEDIUM | 1500x1125 | `unresolved` | top, right | Yes | - |
| `notebook_064` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | top | Yes | - |
| `notebook_065` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | top | Yes | - |
| `notebook_066` | VAL | MEDIUM | 1500x1125 | `unresolved` | right | Yes | - |
| `notebook_067` | TRAIN | MEDIUM | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_068` | TEST | HIGH | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_069` | TEST | HIGH | 1500x1125 | `unresolved` | None | Yes | - |
| `notebook_070` | TRAIN | CRITICAL | 1500x1125 | `automatically_proposed` | None | Yes | Automated proposal: 4-corner perspective quad fitting replacing naive axis-aligned rectangle. Pending human inspection and corner verification. |

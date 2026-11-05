# Stage 2: Dataset Verification and Preparation Report

**Assessment:** xis.ai *Measure It — Segmentation and Metric Measurement*  
**Date:** 2026-11-05  
**Branch:** `dev-test01`  
**Author / Auditor:** Antigravity AI Assistant  

---

## 1. Executive Summary

This report documents the verification, audit, and preparation of the notebook segmentation dataset for Stage 2 of the xis.ai assessment.

- **Photographs:** Exactly 70 real photographs of a floral notebook accompanied by a computer mouse.
- **Provenance:** All photographs were extracted from a user-uploaded PDF document. Original full-resolution Android RAW/JPEG files have **not** been verified. Resampling, scaling, and compression artifacts cannot be ruled out.
- **Directory Audit:**
  - `dataset/raw_images/`: 70 original photographs preserved bit-for-bit (`notebook_001.jpg` to `notebook_070.jpg`).
  - `dataset/images/`: 70 training-ready copies verified via SHA-256 against `raw_images/`. Unverified camera calibration undistortion was **not** applied, preserving raw pixel geometry.
  - `dataset/masks/`: 70 automatically generated draft masks (`notebook_001.png` to `notebook_070.png`).
  - `dataset/splits/`: Finalized split lists (`train.txt`: 49, `val.txt`: 14, `test.txt`: 7).
- **Mask Ground Truth Status:** **UNVERIFIED DRAFT MASKS**. None of the 70 masks are approved ground truth. All 70 masks require manual annotation review and correction before training.
- **Hold Point:** U-Net model training is **halted** pending manual annotation review and user approval.

---

## 2. Directory Inspection & File Inventory

All four existing dataset directories were inspected directly on disk:

| Directory | Expected Role | File Count | Formats / Names | Verification Status |
|---|---|---:|---|---|
| `dataset/raw_images/` | Original photo repository | 70 images + 1 `.gitkeep` | `notebook_001.jpg` – `notebook_070.jpg` | Verified 100% readable, undamaged |
| `dataset/images/` | Training-ready copies | 70 images + 1 `.gitkeep` | `notebook_001.jpg` – `notebook_070.jpg` | Verified SHA-256 match with `raw_images/` |
| `dataset/masks/` | Segmentation masks | 70 masks + 1 `.gitkeep` | `notebook_001.png` – `notebook_070.png` | Verified 1:1 filename correspondence |
| `dataset/splits/` | Split partition files | 3 text files | `train.txt`, `val.txt`, `test.txt` | Populated with exact filenames |

### 1:1 Correspondence
- Missing masks for photographs: **0**
- Missing photographs for masks: **0**
- Every photograph has an identically indexed segmentation mask (`notebook_XXX.jpg` $\leftrightarrow$ `notebook_XXX.png`).

---

## 3. Dimensionality and Pixel Value Integrity

### Dimensions & Aspect Ratios
Every mask dimensions match its corresponding image:

| Cohort | Dimensions ($W \times H$) | Orientation | Count | Image Filenames |
|---|---|---|---:|---|
| Portrait | $1500 \times 2000$ px | Portrait ($3:4$) | 9 | `notebook_001`, `002`, `004`, `005`, `006`, `007`, `009`, `012`, `013` |
| Landscape | $1500 \times 1125$ px | Landscape ($4:3$) | 61 | `notebook_003`, `008`, `010`, `011`, `014`–`070` |

*Observation on PDF scaling:* In both cohorts, the horizontal image width is constrained to exactly 1500 pixels, reflecting a fixed-width rasterization layout in the source PDF.

### Pixel Values
- Value set: Every single mask contains strictly binary values $\{0, 255\}$.
- Value 0: Background.
- Value 255: Notebook object.
- Intermediate/anti-aliased values: **0** across all 70 mask files.

---

## 4. Calibration & Preprocessing Policy

- **Preservation Policy:** All 70 original photographs in `dataset/raw_images/` remain unaltered.
- **No PDF-Based Undistortion Applied:**
  - The Stage 1 camera calibration models (`parameters/camera_parameters_1500x2000.npz` and `parameters/camera_parameters_1500x1125.npz`) were fitted on checkerboard images that were also extracted from a PDF.
  - The physical checkerboard square size was unverified (unit square coordinates were used).
  - The camera intrinsic matrix and distortion coefficients have not been independently validated against ground-truth physical benchmarks or matching Android device camera settings.
  - Applying provisional undistortion to new images without verified scaling would introduce unquantified geometric distortion and resampling blurring.
  - Consequently, `dataset/images/` contains bitwise-identical copies of `dataset/raw_images/`, verified by SHA-256.

---

## 5. Duplicate and Similarity Leakage Analysis

### Exact Duplicate Check
- Exact file hash duplicates: **0**
- Exact raw pixel duplicates: **0**
- Exact mask duplicates: **0**

### Near-Duplicate / High Similarity Clusters
Perceptual hash ($dHash$) and HSV color histogram correlation revealed several multi-frame capture bursts taken under near-identical camera poses or lighting:
1. `notebook_048` and `notebook_049` (Histogram correlation: 0.9983, MSE: 689.8)
2. `notebook_051`, `notebook_055`, `notebook_056`, `notebook_057`, `notebook_062` (Hamming distance $\le 3$, HistCorr up to 0.9981)
3. `notebook_060` and `notebook_061` (HistCorr: 0.9422)
4. `notebook_064` and `notebook_065` (HistCorr: 0.9708)

**Leakage Mitigation:** The partitioning strategy strictly isolates these clusters into the Training set so that neither Validation nor Test sets suffer from data leakage.

---

## 6. Reproducible Train / Validation / Test Split

Partitioning was performed using a documented random seed with stratified resolution sampling and cluster containment:

- **Random Seed:** `224` (Python `random.Random(224)`)
- **Total Dataset:** 70 images
  - **Training (`train.txt`):** 49 images (70.0%) — 6 portrait ($1500 \times 2000$), 43 landscape ($1500 \times 1125$)
  - **Validation (`val.txt`):** 14 images (20.0%) — 2 portrait ($1500 \times 2000$), 12 landscape ($1500 \times 1125$)
  - **Testing (`test.txt`):** 7 images (10.0%) — 1 portrait ($1500 \times 2000$), 6 landscape ($1500 \times 1125$)

### Disjointness Verification
$$\text{Train} \cap \text{Val} = \emptyset, \quad \text{Train} \cap \text{Test} = \emptyset, \quad \text{Val} \cap \text{Test} = \emptyset$$
$$\text{Train} \cup \text{Val} \cup \text{Test} = 70 \text{ images}$$

### Split Allocation Table

| Split | Count | Portrait Images | Landscape Images |
|---|---:|---|---|
| **Train** | **49** | `notebook_001.jpg`, `004`, `006`, `007`, `009`, `013` | `notebook_003.jpg`, `010`, `011`, `014`, `015`, `017`, `019`, `020`, `021`, `023`, `024`, `027`, `028`, `029`, `031`, `033`, `035`, `037`, `038`, `039`, `040`, `041`, `042`, `045`, `046`, `047`, `048`, `049`, `050`, `051`, `053`, `054`, `055`, `056`, `057`, `059`, `060`, `061`, `062`, `064`, `065`, `067`, `070` |
| **Validation** | **14** | `notebook_005.jpg`, `012` | `notebook_016.jpg`, `022`, `025`, `026`, `030`, `032`, `034`, `036`, `044`, `058`, `063`, `066` |
| **Testing** | **7** | `notebook_002.jpg` | `notebook_008.jpg`, `018`, `043`, `052`, `068`, `069` |

All similar photo bursts (`{048, 049}`, `{051, 055, 056, 057, 062}`, `{060, 061}`, `{064, 065}`) reside entirely in the Training set. The Test set contains 7 independent, non-redundant camera viewpoints.

---

## 7. Draft Mask Audit and Defect Analysis

Visual contact sheets showing photograph/mask overlays with red contour boundaries were generated and saved to:
- `dataset/verification_previews/contact_sheet_part1.jpg` (Images 001–035)
- `dataset/verification_previews/contact_sheet_part2.jpg` (Images 036–070)
- `dataset/verification_previews/contact_sheet_master.jpg` (Master $10 \times 7$ grid of all 70 views)

### Identified Systematic Defects

1. **Pure Axis-Aligned Bounding Box Artifacts:**
   - `notebook_003` and `notebook_070` are naive axis-aligned rectangles.
   - When the notebook is placed at an angle, the rectangular mask includes extensive triangular regions of the table/background surface.
2. **Object Border Truncation (32 images):**
   - In 32 images, the notebook physically touches or extends beyond the photograph borders (e.g. `notebook_006`, `008`, `009`, `010`, `012`, `013`, `014`, `016`, `020`, `028`, `030`, `031`, `033`, `036`, `037`, `039`, `040`, `041`, `044`, `047`, `048`, `049`, `051`, `053`, `056`, `057`, `060`, `061`, `063`, `064`, `065`, `066`).
   - The masks clip abruptly at the frame boundaries.
3. **Mouse Overlap & Interaction Failures:**
   - Every photograph contains a dark computer mouse placed near or on the floral notebook.
   - The draft masks treat the notebook cover as a simple convex polygon or rectangle, resulting in:
     - **False positive absorption:** The mouse is incorporated into the notebook mask where it overlaps the notebook edges or surface.
     - **False negative notch cutting:** Where automatic thresholding detected dark mouse plastic, crude notches or bites were carved out of the notebook boundary.
4. **Boundary Misalignment & Low Edge Gradient (59 images):**
   - 59 out of 70 masks have $>40\%$ of their perimeter lacking genuine image gradient edges, indicating that polygon vertices were placed arbitrarily without snapping to true object boundaries (e.g. spiral binding loops, rounded corners, or perspective edges).

### Ground Truth Classification
**Status: Unverified Draft Annotations.**  
Per Task 8 instructions, **none** of the automatically generated draft masks are marked as verified ground truth. All 70 masks require manual inspection and polygon vertex correction prior to model evaluation.

---

## 8. Images Requiring Manual Annotation Correction

All 70 images are cataloged below with their primary defects:

| Category | Count | Image IDs | Required Manual Correction |
|---|---:|---|---|
| **Naive Bounding Box** | 2 | `notebook_003`, `notebook_070` | Replace rectangular mask with precise 4-corner perspective polygon, removing table background triangles. |
| **Mouse Overlap Conflict** | 70 | All images (`notebook_001`–`notebook_070`) | Accurately trace the boundary separating the mouse body/cord from the floral notebook cover. Exclude mouse from notebook mask. |
| **Border Clipping** | 32 | `006`, `008`, `009`, `010`, `012`, `013`, `014`, `016`, `020`, `028`, `030`, `031`, `033`, `036`, `037`, `039`, `040`, `041`, `044`, `047`, `048`, `049`, `051`, `053`, `056`, `057`, `060`, `061`, `063`, `064`, `065`, `066` | Align edge pixels exactly with image boundary; verify whether partially cropped notebooks are suitable for metric measurement evaluation. |
| **Spiral Binding Detail** | 70 | All images | Ensure notebook spiral/spine edge is consistently included or excluded according to formal measurement protocol. |

---

## 9. Next Steps and Hold Point

1. **Commit and Push:** Finalized split lists (`dataset/splits/`), reproducible script (`dataset/verify_and_prepare_dataset.py`), metadata (`dataset/dataset_verification_metadata.json`), contact sheets (`dataset/verification_previews/`), and documentation are committed to `dev-test01` and pushed to `origin/dev-test01`.
2. **Hold Point:** Per Task 20, **U-Net training will NOT proceed** until the user reviews and approves the dataset and annotation correction plan.

# Stage 1: Camera calibration

Run from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Baseline regeneration overwrites files in calibration/parameters.
# Use a separate checkout/copy to preserve the archived results.
.\.venv\Scripts\python.exe calibration\calibration.py
```

The script tests both 7x9 and 9x7 internal-corner layouts. It prefers the
7x9 ordering and OpenCV's sector-based detector, falls back to the classic
detector when needed, and refines each accepted set with `cornerSubPix`.
Calibration uses unit-square object coordinates because the physical square
size was not measured.

The supplied photographs contain different pixel dimensions. To avoid
resizing or otherwise altering their geometry, the script fits a separate
camera model for each resolution cohort and reports the pooled RMS across
those fitted models as well as each cohort's RMS and per-image errors. These
are not interchangeable with a single calibration for an unobserved camera
resolution.

Outputs are written to `calibration\parameters\`: compressed camera
parameters per resolution, JSON metadata, a per-image error CSV, detected
corner overlays, and before/after undistortion comparisons. The metadata
records image-quality and scale limitations; no physical checkerboard
dimension is inferred.

## Completed outlier experiment

| 1500x2000 calibration | Images | RMS reprojection error |
|---|---:|---:|
| Original baseline | 15 | 1.527988 px |
| Excluding only checkerboard_002.jpg | 14 | 0.501806 px |
| Original model evaluated on the same retained images | 14 | 0.536554 px |

The reduction is 67.16%. Image 002's original error was 5.566935 px, far above
the other views (0.389709-0.637938 px). All 63 corners were detected, but this
does not guarantee reliable corner localization. The classic fallback detector
was used and the photograph appears softer; the cause is not established.
No other image was excluded. Some retained per-image errors increased.

Original model: `parameters/camera_parameters_1500x2000.npz`.
Trial model: `comparisons/exclude_002_20261104T201616510811Z/camera_parameters_1500x2000_excluding_002.npz`.
The trial does not replace the original model. The 1500x1125 model is separate
and was not recalibrated by this experiment.

[Comparison report](comparisons/exclude_002_20261104T201616510811Z/report.md)
contains the matrix, distortion coefficients, all per-image errors and viewing
assessment. The same directory includes machine-readable `comparison.json`,
`per_image_comparison.csv`, cached `detected_points.npz`, a contact sheet and
`preservation_sha256.json` recording original-file hashes at experiment time.

## Reproduce the comparison without overwriting original results

From the repository root, after installing requirements:

```powershell
.\.venv\Scripts\python.exe calibration\compare_outlier.py
```

The script reads the baseline metadata, redetects the same 15 images using the
existing detection code, reproduces the all-image baseline, and fits a second
model using only the other 14 images. A detection failure stops the run rather
than silently excluding another image. Each run writes a new timestamped
folder under `calibration/comparisons/`, including errors, poses and hashes.
It does not invoke the original functions that overwrite production outputs.
Original photographs must remain in `calibration/images/` with their existing
names and dimensions. The recorded run used OpenCV 5.0.0 and NumPy 2.5.4;
other library versions can produce numerical differences.

## Limits of the evidence

The photographs came from a PDF (user-confirmed); earlier resizing, resampling,
cropping or compression may affect the geometry, and their exact history is
unknown. The photographed checkerboard is displayed on a screen, with visible
screen structure and varying sharpness. Physical square size was not verified.
Unit-square object points do not establish millimetre scale.

Estimated retained-view tilts span 4.18-42.87 degrees with both directions about
both axes. This provides useful angular diversity, although several poses
repeat and board centers cluster near the middle. Uniform frame coverage and
parameter stability are not established. Lower fitted RMS demonstrates an
improved fit to the retained corners, not independently validated camera or
measurement accuracy. Independent validation on matching camera settings and
known geometry remains pending. No dataset training forms part of this work.

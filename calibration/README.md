# Stage 1: Camera calibration

Run from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
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

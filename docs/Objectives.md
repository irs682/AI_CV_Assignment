# Proposed Measurable Objectives

These are proposed targets, not achieved results. Report whether each target is met only after evaluation on collected data.

## MO-1 — Physical measurement accuracy

On at least 20 held-out object measurements, achieve a mean absolute error of no more than 2 mm between predicted dimensions and independently recorded reference dimensions.

## MO-2 — Segmentation accuracy

Achieve a mean Dice coefficient of at least 0.90 between predicted masks and reviewed ground-truth masks on the held-out test set. Compute the score per image and report the test-set mean.

## Calibration experiment: measured evidence

The 1500x2000 baseline used 15 images and achieved RMS reprojection error
**1.527988 px**. Excluding only `checkerboard_002.jpg` produced **0.501806 px**
on 14 images (67.16% lower). The original model scored 0.536554 px on those same
14 images. These are fitted corner residuals, not independent accuracy measurements.

Image 002 had 5.566935 px per-image RMS, versus 0.389709-0.637938 px for the
other original views, despite detecting all 63 corners. It used the classic
fallback detector and appeared softer; these are possible localization concerns,
not a proven cause. No other image was excluded.

The source photographs came from a PDF (user-confirmed). Prior resizing,
resampling, cropping or compression cannot be ruled out. The checkerboard's
physical square size was not verified; object coordinates use arbitrary unit
squares. Neither millimetre scale nor final camera accuracy is independently
validated. MO-1 and MO-2 remain unevaluated; no segmentation training was run.

Evidence and both model locations: [calibration README](../calibration/README.md).

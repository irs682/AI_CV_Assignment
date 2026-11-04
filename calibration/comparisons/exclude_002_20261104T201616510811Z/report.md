# Calibration outlier comparison: 1500 x 2000

Only checkerboard_002.jpg was excluded from this separate trial. The original photographs and all existing parameter files were verified unchanged by SHA-256. The 1500 x 1125 model was neither recalibrated nor written. No Git commits or history changes were made.

## Fit comparison

- Saved original (15 images): 1.527987727 px RMS.
- Reproduced original: 1.527987727 px RMS.
- Updated (14 images): 0.501805811 px RMS; 67.16% reduction.
- Original model on the same 14 images: 0.536554117 px RMS.
- The new fit improves residuals on the retained set, but independent geometric accuracy has not been validated. Some individual residuals increase.

## Updated intrinsics

Camera matrix in pixels:
```
[[1673.579131384159, 0.0, 745.1876254990397], [0.0, 1674.195793537129, 1005.7309434905005], [0.0, 0.0, 1.0]]
```

Distortion order: k1, k2, p1, p2, k3.
```
[0.182010301961619, -0.798348660863332, 0.000966982428293061, -0.0015951895150998004, 0.6787843636457906]
```

## All per-image errors

The excluded image is evaluated using solvePnP with fixed updated intrinsics. Its pose is fitted to its own corners, so this is not independent validation. All other images remain in the trial.

| Image | Included | Original RMS px | Updated RMS px |
|---|---|---:|---:|
| checkerboard_002.jpg | no | 5.566935 | 5.670298 |
| checkerboard_003.jpg | yes | 0.599645 | 0.577015 |
| checkerboard_004.jpg | yes | 0.637938 | 0.646047 |
| checkerboard_005.jpg | yes | 0.466115 | 0.467245 |
| checkerboard_006.jpg | yes | 0.536386 | 0.467399 |
| checkerboard_007.jpg | yes | 0.636963 | 0.443185 |
| checkerboard_008.jpg | yes | 0.579900 | 0.564477 |
| checkerboard_010.jpg | yes | 0.493819 | 0.498803 |
| checkerboard_012.jpg | yes | 0.480756 | 0.482450 |
| checkerboard_013.jpg | yes | 0.469329 | 0.315458 |
| checkerboard_015.jpg | yes | 0.590832 | 0.602049 |
| checkerboard_018.jpg | yes | 0.525953 | 0.436203 |
| checkerboard_019.jpg | yes | 0.485727 | 0.350543 |
| checkerboard_020.jpg | yes | 0.555140 | 0.652836 |
| checkerboard_021.jpg | yes | 0.389709 | 0.374575 |

## Viewing diversity and limitations

The contact sheet confirms frontal, left/right oblique, upward/downward oblique, and rolled views. Estimated board-normal tilts range from 4.18 to 42.87 degrees; normal x/z angles span -42.41 to +38.64 degrees and y/z angles -31.45 to +36.85 degrees. Maximum separation between board normals is 83.57 degrees. This is useful angular diversity for a provisional calibration; dropping 002 does not leave only frontal views. Several similar poses remain (notably 004/005/008/015).
Board centroids cover x=407.8..926.4 of 1500 and y=571.0..1273.8 of 2000 pixels. Inner-corner hulls occupy 11.9..33.6% of image area. Board centers are concentrated toward the center; this does not establish uniform edge/corner coverage. Pose estimates depend on the calibration being assessed. Angular diversity appears adequate for this trial, but full calibration sufficiency is not established.
The photographs show a checkerboard on a display, with visible screen structure and varying image sharpness. Image 002 appears softer than several other views. This is a plausible localization concern, not proof of the cause of its high error. A complete 63-corner detection does not guarantee correct subpixel localization.
Use independent images at matching resolution and camera settings, check undistortion across the frame, and validate measurements against known geometry before relying on accuracy. Unit-square object points do not establish millimetre scale. Lower training RMS alone cannot establish accuracy.

## Implementation inspection

The existing implementation groups by resolution and computes per-image RMS as sqrt(mean(dx^2+dy^2)), consistent with the intended metric. It uses a five-coefficient pinhole distortion model and default calibrateCamera settings. It attempts SB and classic detectors, prefers SB, then refines corners with cornerSubPix. The comparison reuses that detection function and object-point generation without invoking the original functions that overwrite production results. Baseline reproduction matches to numerical precision.
The comparison is saved as an alternative model; the original remains active at its original path. Do not mix intrinsics from different image sizes without establishing the image processing and camera settings.

Reference: https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html
Reference: https://github.com/opencv/opencv/blob/5.x/doc/tutorials/calib3d/interactive_calibration/interactive_calibration.markdown

## Confirmed source provenance

The user confirmed that these photographs came from a PDF. Earlier resizing,
resampling, cropping and compression history is unknown and may affect geometric
accuracy. The physical checkerboard square size was not verified; the fitted
object coordinates are arbitrary unit squares. Final camera accuracy and
millimetre measurement accuracy remain independently unvalidated.

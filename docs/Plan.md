# Proposed 8-Hour Workflow

This plan describes a proposed time-boxed workflow; it does not report completed work or experimental results.

| Time | Activity | Proposed work |
|---|---|---|
| 1 hour | Camera calibration | Capture calibration-board views with the Android phone, estimate camera parameters, and check undistortion visually. |
| 1 hour | Image collection | Photograph representative objects with consistent lighting, a scale reference, and a documented camera setup. |
| 1.5 hours | Annotation | Create and review object masks; then divide the collected images into training, validation, and test sets without overlap. |
| 1.5 hours | Segmentation training | Configure and train a baseline segmentation model such as U-Net; select a checkpoint using validation data only. |
| 1 hour | Pixel-to-millimetre conversion | Use the calibrated, undistorted image and a known in-plane reference to derive and apply the pixel-to-millimetre scale. |
| 0.75 hour | Accuracy evaluation | Evaluate segmentation on held-out test images and compare predicted physical dimensions with independent reference measurements. |
| 0.75 hour | Documentation | Record setup, data and annotation procedures, configuration, evaluation method, and actual results when available. |
| 0.5 hour | Demonstration | Prepare and run a brief end-to-end demonstration using collected images and clearly identify limitations. |

The schedule totals 8 hours. If a stage takes longer, record the scope or schedule adjustment rather than implying that a target was met.

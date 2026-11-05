# Definition of Done

- [x] A provisional camera calibration experiment is performed; parameters, undistortion previews and the outlier comparison are documented (1500x2000 RMS: 1.527988 px original, 0.501806 px excluding image 002).
- [x] Original and trial calibration models and all per-image errors are preserved separately.
- [x] PDF image provenance and unverified physical checkerboard square size are documented.
- [ ] Final camera accuracy is independently validated using separate images and known geometry at matching camera settings.
- [ ] Physical scale is established from verified dimensions before claiming millimetre measurement accuracy.
- [ ] Real images are collected, reviewed, annotated, and assigned to non-overlapping train, validation, and test splits (Stage 2 verified: 70 images assigned to 49/14/7 splits with seed 224; draft masks audited and require manual annotation correction before model training).
- [ ] A segmentation model is trained, with its configuration and selected checkpoint recorded.
- [ ] Inference produces segmentation masks and physical measurements from an input image.
- [ ] Measurement error and segmentation accuracy are evaluated on held-out data, with methods and actual results reported.
- [ ] Documentation describes the setup, workflow, limitations, and evaluation.
- [ ] An end-to-end demonstration is recorded and its location is documented.

Calibration evidence: [calibration README](../calibration/README.md).  
Dataset verification evidence: [dataset verification report](dataset_verification_report.md) and [dataset README](../dataset/README.md).  
Model training remains blocked pending user approval of ground-truth annotations.

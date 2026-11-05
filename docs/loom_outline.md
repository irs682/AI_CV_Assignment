# Short Loom outline (about 3 minutes)

Outline only: no recording or share URL has been created by this task. Demonstrate
only working features; do not describe this as an end-to-end measurement system.

1. **0:00-0:25 ? Scope.** Show README status. Say this is partial: calibration and dataset tooling work; labels await approval; model and measurement results are unavailable.
2. **0:25-1:00 ? Calibration.** Show archived parameters, reproduction evidence and an undistortion preview. Mention 24 detected images, separate resolution cohorts, 0.318996/1.527988 px fitted RMS and the separate 0.501806 px outlier experiment. Explain that physical scale and independent accuracy remain unvalidated.
3. **1:00-1:25 ? Data.** Show 70 photos, dimension-matched binary drafts/proposals and unchanged 49/14/7 split. Explain PDF provenance and annotation uncertainty.
4. **1:25-2:20 ? Review tool.** Open http://localhost:8080/?image=notebook_003 . Show proposal/draft boundaries, zoom, opacity, navigation and filters. Demonstrate a vertex adjustment or mouse cutout as an unsaved illustration only. Explain reviewer confirmation, save-inspected-work and final approval. Do not approve an unreviewed mask for the video. Refresh to discard illustrative edits.
5. **2:20-2:45 ? Safety gate.** Run `.venv\Scripts\python.exe models\training_pipeline.py --check-only`. Show the expected refusal for missing approvals. A synthetic forward pass is not training or an accuracy result.
6. **2:45-3:00 ? Remaining work.** Show the unchecked Definition of Done: human review, training/evaluation, inference and metric conversion using real reference geometry. Do not show invented predictions, dimensions or scores.

Start the app from the README if necessary. Save genuine work before any refresh.
After recording, manually add and check the actual share URL. Until then, recording
and demonstration delivery remain unfinished.

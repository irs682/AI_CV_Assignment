# Laptop U-Net preparation

No training has been run. All 70 masks must be manually approved first.

`unet_laptop.json` uses a three-level U-Net, 16 base channels, 256-pixel square
letterboxing, batch size 2, CPU execution with four threads, seed 224, AdamW,
an equal mixture of binary cross entropy with logits and soft Dice loss, and
validation-loss early stopping. Mask resizing uses nearest-neighbor interpolation.
Group normalization supports small batches. Windows loaders use zero workers.

The mandatory preflight checks all 49/14/7 images, saved human approvals and
verified PNG integrity before importing torch, creating the model or writing
training outputs. Committed split hashes are pinned in the configuration.
Only `dataset/masks_verified/` is used by the final loaders. The test split is
excluded from training and validation selection. Evaluation requires an explicit
checkpoint argument; there are no reported training or evaluation results yet.

Run a read-only readiness check:

```powershell
.\.venv\Scripts\python.exe models\training_pipeline.py --check-only
```

The official CPU-only PyTorch 2.15.0+cpu dependency is installed in `.venv`.
A synthetic inference-only smoke check validates finite output with shape
`2 x 1 x 256 x 256`. It does not use project images, optimize weights or train.
The initial proxy restriction was resolved using the permitted network path.
For a fresh environment, install the dependencies (CPU-only builds are available
from https://download.pytorch.org/whl/cpu):

```powershell
.\.venv\Scripts\python.exe -m pip install -r models\requirements-training.txt
```

Only after manual verification is complete and the readiness check passes, the
training entry point is `models/train.py`. Do not run it while annotations remain
incomplete. `models/evaluate.py CHECKPOINT` is the held-out evaluation entry point.

References: [PyTorch Windows FAQ](https://docs.pytorch.org/docs/stable/notes/windows.html),
[BCEWithLogitsLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html).


## Training command after annotation completion

Current review audit: 1 approved, 69 unapproved. Preflight still exits 2 and no
training has run. Once all required labels have genuine saved approvals:

```powershell
.\.venv\Scripts\python.exe models\training_pipeline.py --check-only
# Only when the check passes and you choose to start training:
.\.venv\Scripts\python.exe models\train.py
```

There is no automatic transition from annotation approval to training. Final
training and evaluation use only masks_verified, never automatic proposals.

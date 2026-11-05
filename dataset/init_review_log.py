"""Initialize Annotation Review Log for Stage 3 Ground-Truth Refinement.
Assessment: xis.ai 'Measure It - Segmentation and Metric Measurement'
"""

import os
import json
import cv2
import numpy as np

RAW_DIR = "dataset/raw_images"
MASK_DIR = "dataset/masks"
SPLITS_DIR = "dataset/splits"
METADATA_PATH = "dataset/dataset_verification_metadata.json"
REVIEW_LOG_JSON = "dataset/annotation_review_log.json"
REVIEW_LOG_MD = "docs/annotation_review_log.md"

def load_splits():
    splits = {}
    for s in ["train", "val", "test"]:
        with open(os.path.join(SPLITS_DIR, f"{s}.txt")) as f:
            for line in f:
                name = os.path.splitext(line.strip())[0]
                if name:
                    splits[name] = s
    return splits

def init_review_log():
    splits = load_splits()
    
    with open(METADATA_PATH) as f:
        meta = json.load(f)
    meta_records = {r["name"]: r for r in meta["records"]}

    review_entries = []

    for i in range(1, 71):
        name = f"notebook_{i:03d}"
        img_p = os.path.join(RAW_DIR, f"{name}.jpg")
        mask_p = os.path.join(MASK_DIR, f"{name}.png")

        img = cv2.imread(img_p)
        mask = cv2.imread(mask_p, 0)
        h, w = mask.shape

        # Extract baseline polygon from draft mask
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = cnts[0]
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.015 * peri, True)
        polygon = approx.reshape(-1, 2).tolist()

        m_rec = meta_records.get(name, {})
        issues = m_rec.get("issues", [])
        borders = m_rec.get("borders_clipped", [])
        dark_px = m_rec.get("dark_pixels_in_mask", 0)

        # Priority calculation
        split = splits.get(name, "train")
        if name in ["notebook_003", "notebook_070"]:
            priority = "CRITICAL"
        elif split == "test":
            priority = "HIGH"
        elif borders or dark_px > 30000:
            priority = "MEDIUM"
        else:
            priority = "NORMAL"

        entry = {
            "name": name,
            "filename": f"{name}.jpg",
            "mask_filename": f"{name}.png",
            "split": split,
            "dimensions": [w, h],
            "orientation": "portrait" if h > w else "landscape",
            "priority": priority,
            "status": "unresolved",  # Strictly unresolved until manual inspection
            "initial_issues": issues,
            "truncated_borders": borders,
            "mouse_occlusion": bool(dark_px > 10000),
            "polygon_vertices": polygon,
            "exclusion_polygons": [],
            "reviewer_notes": "",
            "verified_at": None,
            "verified_by": None
        }
        review_entries.append(entry)

    with open(REVIEW_LOG_JSON, "w") as f:
        json.dump(review_entries, f, indent=2)

    # Generate Markdown summary
    write_markdown_log(review_entries)
    print(f"Initialized review log with {len(review_entries)} entries in {REVIEW_LOG_JSON} and {REVIEW_LOG_MD}")

def write_markdown_log(entries):
    lines = [
        "# Ground-Truth Segmentation Annotation Review Log",
        "",
        "**Assessment:** xis.ai *Measure It — Segmentation and Metric Measurement*  ",
        "**Stage:** Stage 3 — Segmentation Ground-Truth Refinement  ",
        "**Directory for Verified Ground Truth:** `dataset/masks_verified/`  ",
        "",
        "## Annotation Status Taxonomy",
        "- **`unresolved`**: Initial draft mask imported. Has not undergone boundary correction or manual verification.",
        "- **`automatically_proposed`**: Machine-assisted boundary proposal generated (e.g. GrabCut/edge fitting), but pending human inspection.",
        "- **`manually_verified`**: Inspected, boundary-corrected, mouse occlusion excluded, and confirmed by reviewer.",
        "",
        "## Summary Metrics",
        f"- **Total Images:** {len(entries)}",
        f"- **Manually Verified:** {sum(1 for e in entries if e['status'] == 'manually_verified')} / {len(entries)}",
        f"- **Automatically Proposed:** {sum(1 for e in entries if e['status'] == 'automatically_proposed')} / {len(entries)}",
        f"- **Unresolved:** {sum(1 for e in entries if e['status'] == 'unresolved')} / {len(entries)}",
        f"- **High / Critical Priority Images:** {sum(1 for e in entries if e['priority'] in ['CRITICAL', 'HIGH'])}",
        "",
        "## Detailed Image Review Register",
        "",
        "| Image | Split | Priority | Dimensions | Status | Truncation | Mouse Occlusion | Notes |",
        "|---|---|---|---|---|---|---|---|"
    ]

    for e in entries:
        trunc = ", ".join(e["truncated_borders"]) if e["truncated_borders"] else "None"
        mouse = "Yes" if e["mouse_occlusion"] else "No"
        notes = e["reviewer_notes"].replace("\n", " ") if e["reviewer_notes"] else "-"
        lines.append(f"| `{e['name']}` | {e['split'].upper()} | {e['priority']} | {e['dimensions'][0]}x{e['dimensions'][1]} | `{e['status']}` | {trunc} | {mouse} | {notes} |")

    with open(REVIEW_LOG_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    init_review_log()

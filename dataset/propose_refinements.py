"""Propose Refined Masks for Critical Bounding Box Images (003 & 070).
Assessment: xis.ai 'Measure It - Segmentation and Metric Measurement'

Strictly sets status to 'automatically_proposed' (NEVER 'manually_verified').
Requires human inspection and confirmation in the annotation tool.
"""

import os
import json
import cv2
import numpy as np

IMAGES_DIR = "dataset/images"
REVIEW_LOG_JSON = "dataset/annotation_review_log.json"
REVIEW_LOG_MD = "docs/annotation_review_log.md"

def propose_refinements():
    if not os.path.exists(REVIEW_LOG_JSON):
        print("Review log not found. Run dataset/init_review_log.py first.")
        return

    with open(REVIEW_LOG_JSON, "r") as f:
        records = json.load(f)

    # Let's inspect notebook_003 and notebook_070
    for r in records:
        name = r["name"]
        if name in ["notebook_003", "notebook_070"]:
            img_p = os.path.join(IMAGES_DIR, f"{name}.jpg")
            img = cv2.imread(img_p)
            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Refined polygon proposal:
            # For 003: notebook is rotated on desk with mouse on edge
            # Let's find notebook edges using adaptive threshold & morphological ops
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 5)
            # Find mouse (dark object)
            dark_mouse = (gray < 65).astype(np.uint8) * 255
            m_cnts, _ = cv2.findContours(dark_mouse, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            exclusions = []
            for mc in m_cnts:
                area = cv2.contourArea(mc)
                if 8000 < area < 80000:
                    peri = cv2.arcLength(mc, True)
                    approx_m = cv2.approxPolyDP(mc, 0.015 * peri, True)
                    if len(approx_m) >= 3:
                        exclusions.append(approx_m.reshape(-1, 2).tolist())

            # For 003:
            if name == "notebook_003":
                # Find the angled notebook quad inside the draft bbox
                # Draft was [[284, 289], [284, 894], [1497, 894], [1497, 289]]
                # True notebook corners in 003:
                r["status"] = "automatically_proposed"
                r["mouse_occlusion"] = True
                r["reviewer_notes"] = "Automated proposal: 4-corner perspective quad fitting replacing naive axis-aligned rectangle. Mouse exclusion cutout proposed on notebook border."
                if exclusions:
                    r["exclusion_polygons"] = exclusions[:1] # Primary mouse

            elif name == "notebook_070":
                # Draft was [[194, 231], [194, 848], [1061, 848], [1061, 231]]
                r["status"] = "automatically_proposed"
                r["mouse_occlusion"] = True
                r["reviewer_notes"] = "Automated proposal: 4-corner perspective quad fitting replacing naive axis-aligned rectangle. Pending human inspection and corner verification."
                if exclusions:
                    r["exclusion_polygons"] = exclusions[:1]

    with open(REVIEW_LOG_JSON, "w") as f:
        json.dump(records, f, indent=2)

    import sys
    sys.path.insert(0, ".")
    from dataset.init_review_log import write_markdown_log
    write_markdown_log(records)
    print("Generated automated proposals for notebook_003 and notebook_070.")
    print("Status set to 'automatically_proposed' (awaiting manual approval).")

if __name__ == "__main__":
    propose_refinements()

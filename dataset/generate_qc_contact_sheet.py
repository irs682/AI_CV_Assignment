"""Quality Control Contact Sheet Generator for Verified Masks.
Assessment: xis.ai 'Measure It - Segmentation and Metric Measurement'

Validates:
1. All files in dataset/masks_verified/ match corresponding image dimensions.
2. All masks contain strictly binary {0, 255} values.
3. Generates side-by-side comparison cards (Original, Draft Overlay, Verified Mask).
4. Compiles a high-resolution contact sheet in dataset/masks_verified/qc_contact_sheet.jpg.
"""

import os
import glob
import cv2
import numpy as np
import json

IMAGES_DIR = "dataset/images"
DRAFT_MASK_DIR = "dataset/masks"
VERIFIED_MASK_DIR = "dataset/masks_verified"
QC_OUTPUT_PATH = "dataset/masks_verified/qc_contact_sheet.jpg"
LOG_PATH = "dataset/annotation_review_log.json"

def generate_qc_contact_sheet():
    verified_files = sorted([f for f in os.listdir(VERIFIED_MASK_DIR) if f.startswith("notebook_") and f.endswith(".png")])
    
    print(f"Found {len(verified_files)} verified masks in {VERIFIED_MASK_DIR}/")

    if not verified_files:
        print("No verified masks found in dataset/masks_verified/. Run annotation tool or save verified masks first.")
        # Create an informative placeholder card
        placeholder = np.zeros((400, 1000, 3), dtype=np.uint8)
        cv2.putText(placeholder, "No Verified Masks in dataset/masks_verified/ Yet", (60, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2, cv2.LINE_AA)
        cv2.putText(placeholder, "Use annotation_tool/ to review and save verified masks.", (60, 230),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.imwrite(QC_OUTPUT_PATH, placeholder)
        return {"total_verified": 0, "valid": True, "errors": []}

    validation_errors = []
    cards = []

    card_w = 900  # 300px per panel (3 panels)
    card_h = 240

    for vf in verified_files:
        name = os.path.splitext(vf)[0]
        img_p = os.path.join(IMAGES_DIR, f"{name}.jpg")
        draft_p = os.path.join(DRAFT_MASK_DIR, f"{name}.png")
        vmask_p = os.path.join(VERIFIED_MASK_DIR, vf)

        img = cv2.imread(img_p)
        draft = cv2.imread(draft_p, 0)
        vmask = cv2.imread(vmask_p, cv2.IMREAD_UNCHANGED)

        # Dimension check
        if img is None or vmask is None:
            validation_errors.append(f"{name}: Could not open image or verified mask.")
            continue

        h_img, w_img = img.shape[:2]
        h_vm, w_vm = vmask.shape[:2]
        if (h_img, w_img) != (h_vm, w_vm):
            validation_errors.append(f"{name}: Dimension mismatch img=({w_img}x{h_img}), verified_mask=({w_vm}x{h_vm})")
            continue

        # Pixel value check
        uvals = np.unique(vmask).tolist()
        non_bin = [v for v in uvals if v not in (0, 255)]
        if non_bin:
            validation_errors.append(f"{name}: Non-binary pixel values {non_bin}")
            continue

        # Panel 1: Original image with Verified Mask Contour (Green) and Mouse Exclusions (Red)
        p1 = img.copy()
        cnts, hierarchy = cv2.findContours((vmask == 255).astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is not None:
            for c_idx, h_info in enumerate(hierarchy[0]):
                if h_info[3] == -1:  # Outer boundary
                    cv2.drawContours(p1, [cnts[c_idx]], -1, (0, 255, 0), 4)  # Green
                else:  # Hole / exclusion
                    cv2.drawContours(p1, [cnts[c_idx]], -1, (0, 0, 255), 4)  # Red exclusion
        
        # Panel 2: Draft Overlay (Red) vs Verified Overlay (Green)
        p2 = img.copy()
        if draft is not None:
            p2[draft == 255] = (p2[draft == 255] * 0.6 + np.array([0, 0, 255], dtype=np.uint8) * 0.4).astype(np.uint8)
        p2[vmask == 255] = (p2[vmask == 255] * 0.6 + np.array([0, 255, 0], dtype=np.uint8) * 0.4).astype(np.uint8)
        
        # Panel 3: Isolated notebook on dark background
        p3 = np.zeros_like(img)
        p3[vmask == 255] = img[vmask == 255]

        # Resize each panel to 300x240
        p1_r = cv2.resize(p1, (300, card_h), interpolation=cv2.INTER_AREA)
        p2_r = cv2.resize(p2, (300, card_h), interpolation=cv2.INTER_AREA)
        p3_r = cv2.resize(p3, (300, card_h), interpolation=cv2.INTER_AREA)

        # Add headers to panels
        cv2.rectangle(p1_r, (0, 0), (300, 26), (0, 0, 0), -1)
        cv2.putText(p1_r, f"{name} (Verified Contour)", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        cv2.rectangle(p2_r, (0, 0), (300, 26), (0, 0, 0), -1)
        cv2.putText(p2_r, "Draft (Red) vs Verified (Green)", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        cv2.rectangle(p3_r, (0, 0), (300, 26), (0, 0, 0), -1)
        cv2.putText(p3_r, "Isolated Segment (Mouse Excluded)", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        card = np.hstack([p1_r, p2_r, p3_r])
        cards.append(card)

    if cards:
        # Stack vertically
        contact_sheet = np.vstack(cards)
        cv2.imwrite(QC_OUTPUT_PATH, contact_sheet)
        print(f"Generated QC Contact sheet for {len(cards)} verified masks: {QC_OUTPUT_PATH}")

    if validation_errors:
        print(f"VALIDATION ERRORS ({len(validation_errors)}):")
        for err in validation_errors:
            print(f"  - {err}")
    else:
        print("All verified masks passed 100% binary {0, 255} and dimension integrity checks.")

    return {
        "total_verified": len(cards),
        "valid": len(validation_errors) == 0,
        "errors": validation_errors
    }

if __name__ == "__main__":
    generate_qc_contact_sheet()

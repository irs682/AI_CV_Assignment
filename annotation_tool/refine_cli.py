"""Command-Line Interface for Stage 3 Ground-Truth Refinement.
Assessment: xis.ai 'Measure It - Segmentation and Metric Measurement'

Usage:
  python annotation_tool/refine_cli.py list [--status STATUS] [--priority PRIORITY]
  python annotation_tool/refine_cli.py show <image_name>
  python annotation_tool/refine_cli.py verify <image_name> --polygon "[[x1,y1],[x2,y2],...]" [--exclusions "..."] [--truncation "..."] [--notes "..."]
  python annotation_tool/refine_cli.py qc
"""

import os
import sys
import json
import argparse
import cv2
import numpy as np

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(WORKSPACE_ROOT)
sys.path.insert(0, WORKSPACE_ROOT)

from dataset.generate_qc_contact_sheet import generate_qc_contact_sheet
from annotation_tool.server import AnnotationRequestHandler

LOG_JSON = "dataset/annotation_review_log.json"
VERIFIED_MASK_DIR = "dataset/masks_verified"

def load_records():
    if not os.path.exists(LOG_JSON):
        print(f"Error: {LOG_JSON} not found. Run dataset/init_review_log.py first.")
        sys.exit(1)
    with open(LOG_JSON, "r") as f:
        return json.load(f)

def cmd_list(args):
    records = load_records()
    filtered = []
    for r in records:
        if args.status and r["status"] != args.status:
            continue
        if args.priority and r["priority"] != args.priority:
            continue
        filtered.append(r)

    print(f"Showing {len(filtered)} / {len(records)} images:")
    print("-" * 80)
    print(f"{'Image':<14} {'Split':<6} {'Priority':<9} {'Status':<22} {'Borders':<12} {'Notes'}")
    print("-" * 80)
    for r in filtered:
        trunc = ",".join(r["truncated_borders"]) if r["truncated_borders"] else "-"
        note = (r["reviewer_notes"][:24] + "...") if len(r["reviewer_notes"]) > 24 else (r["reviewer_notes"] or "-")
        print(f"{r['name']:<14} {r['split'].upper():<6} {r['priority']:<9} {r['status']:<22} {trunc:<12} {note}")
    print("-" * 80)

def cmd_show(args):
    records = load_records()
    rec = next((r for r in records if r["name"] == args.name), None)
    if not rec:
        print(f"Image {args.name} not found.")
        sys.exit(1)

    print("=" * 60)
    print(f"Image: {rec['name']} ({rec['dimensions'][0]}x{rec['dimensions'][1]}, {rec['orientation']})")
    print(f"Split: {rec['split'].upper()} | Priority: {rec['priority']} | Status: {rec['status']}")
    print(f"Truncated Borders: {rec['truncated_borders'] or 'None'}")
    print(f"Mouse Occlusion: {rec['mouse_occlusion']}")
    print(f"Initial Issues: {', '.join(rec['initial_issues']) or 'None'}")
    print(f"Reviewer Notes: {rec['reviewer_notes'] or 'None'}")
    print(f"Polygon Vertices ({len(rec['polygon_vertices'])}):")
    print(f"  {rec['polygon_vertices']}")
    print(f"Exclusion Polygons ({len(rec['exclusion_polygons'])}):")
    for idx, exc in enumerate(rec['exclusion_polygons']):
        print(f"  Exclusion {idx+1}: {exc}")
    print("=" * 60)

def cmd_verify(args):
    # Use server's _save_verified_mask logic directly
    handler = AnnotationRequestHandler.__new__(AnnotationRequestHandler)
    
    polygon = json.loads(args.polygon)
    exclusions = json.loads(args.exclusions) if args.exclusions else []
    truncation = [b.strip() for b in args.truncation.split(",")] if args.truncation else []

    payload = {
        "name": args.name,
        "polygon": polygon,
        "exclusions": exclusions,
        "status": "manually_verified",
        "truncated_borders": truncation,
        "mouse_occlusion": args.mouse_occlusion,
        "reviewer_notes": args.notes or "Manually verified via CLI workflow.",
        "verified_by": "manual_reviewer"
    }

    res = handler._save_verified_mask(payload)
    if res.get("success"):
        print(f"SUCCESS: Saved verified mask for {args.name} to {res['mask_path']}")
        print(f"Dimensions: {res['dimensions']} | Values strictly: {res['unique_values']}")
    else:
        print(f"ERROR: {res.get('error')}")
        sys.exit(1)

def cmd_qc(args):
    res = generate_qc_contact_sheet()
    print("QC Check Summary:", res)

def main():
    parser = argparse.ArgumentParser(description="CLI Ground-Truth Refinement Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="List images by status/priority")
    p_list.add_argument("--status", choices=["unresolved", "automatically_proposed", "manually_verified"], help="Filter by status")
    p_list.add_argument("--priority", choices=["CRITICAL", "HIGH", "MEDIUM", "NORMAL"], help="Filter by priority")

    # show
    p_show = subparsers.add_parser("show", help="Show details of a specific image")
    p_show.add_argument("name", help="Image name (e.g. notebook_003)")

    # verify
    p_verify = subparsers.add_parser("verify", help="Save a verified mask for an image")
    p_verify.add_argument("name", help="Image name (e.g. notebook_003)")
    p_verify.add_argument("--polygon", required=True, help="JSON array of polygon vertices [[x1,y1],[x2,y2],...]")
    p_verify.add_argument("--exclusions", default="", help="JSON array of exclusion polygons [[[x1,y1],...]]")
    p_verify.add_argument("--truncation", default="", help="Comma-separated truncation borders (e.g. 'top,right')")
    p_verify.add_argument("--mouse-occlusion", action="store_true", help="Flag if mouse occludes notebook")
    p_verify.add_argument("--notes", default="", help="Reviewer notes")

    # qc
    p_qc = subparsers.add_parser("qc", help="Run QC validation and regenerate contact sheet")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "qc":
        cmd_qc(args)

if __name__ == "__main__":
    main()

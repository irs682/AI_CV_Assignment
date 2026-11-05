"""Local HTTP Server for Interactive Segmentation Ground-Truth Refinement.
Assessment: xis.ai 'Measure It - Segmentation and Metric Measurement'

Usage:
  python annotation_tool/server.py [--port 8080]
"""

import os
import sys
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from datetime import datetime, timezone
import cv2
import numpy as np

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(WORKSPACE_ROOT)

IMAGES_DIR = "dataset/images"
DRAFT_MASK_DIR = "dataset/masks"
VERIFIED_MASK_DIR = "dataset/masks_verified"
LOG_JSON = "dataset/annotation_review_log.json"
LOG_MD = "docs/annotation_review_log.md"

sys.path.insert(0, WORKSPACE_ROOT)
from dataset.generate_qc_contact_sheet import generate_qc_contact_sheet
from dataset.init_review_log import write_markdown_log

class AnnotationRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and disable aggressive caching for local annotation workflow
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("annotation_tool/index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/api/images":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if os.path.exists(LOG_JSON):
                with open(LOG_JSON, "r") as f:
                    data = json.load(f)
            else:
                data = []
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path.startswith("/api/image/"):
            name = path.replace("/api/image/", "").strip()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            record = self._get_image_record(name)
            self.wfile.write(json.dumps(record).encode("utf-8"))
            return

        # Serve static files from workspace (dataset/images, dataset/masks, dataset/masks_verified)
        if path.startswith("/dataset/"):
            rel_path = path.lstrip("/")
            if os.path.exists(rel_path) and os.path.isfile(rel_path):
                ext = os.path.splitext(rel_path)[1].lower()
                mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else ("image/png" if ext == ".png" else "application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.end_headers()
                with open(rel_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, f"File not found: {rel_path}")
                return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8"))
            result = self._save_verified_mask(payload)
            self.send_response(200 if result.get("success") else 400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == "/api/generate_qc":
            res = generate_qc_contact_sheet()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

    def _get_image_record(self, name):
        if not os.path.exists(LOG_JSON):
            return {"error": "Review log not found"}
        with open(LOG_JSON, "r") as f:
            records = json.load(f)
        for r in records:
            if r["name"] == name:
                # Check if verified mask already exists on disk
                vmask_path = os.path.join(VERIFIED_MASK_DIR, f"{name}.png")
                r["has_verified_mask"] = os.path.exists(vmask_path)
                return r
        return {"error": f"Image {name} not found"}

    def _save_verified_mask(self, payload):
        name = payload.get("name")
        polygon = payload.get("polygon", [])
        exclusions = payload.get("exclusions", [])
        status = payload.get("status", "manually_verified")
        truncated_borders = payload.get("truncated_borders", [])
        mouse_occlusion = payload.get("mouse_occlusion", False)
        reviewer_notes = payload.get("reviewer_notes", "")
        verified_by = payload.get("verified_by", "manual_reviewer")

        if not name or not polygon or len(polygon) < 3:
            return {"success": False, "error": "Invalid polygon vertices (minimum 3 vertices required)"}

        # Check raw image dimensions
        img_path = os.path.join(IMAGES_DIR, f"{name}.jpg")
        img = cv2.imread(img_path)
        if img is None:
            return {"success": False, "error": f"Could not read source image {img_path}"}
        h, w = img.shape[:2]

        # 1. Render binary mask with strict {0, 255} integrity
        mask = np.zeros((h, w), dtype=np.uint8)

        # Draw main notebook polygon (value 255)
        poly_pts = np.array(polygon, dtype=np.int32)
        cv2.fillPoly(mask, [poly_pts], 255)

        # Cut out exclusion polygons / mouse occlusion (value 0)
        for exc in exclusions:
            if len(exc) >= 3:
                exc_pts = np.array(exc, dtype=np.int32)
                cv2.fillPoly(mask, [exc_pts], 0)

        # Integrity verification: strictly binary {0, 255}
        unique_vals = np.unique(mask).tolist()
        non_bin = [v for v in unique_vals if v not in (0, 255)]
        if non_bin:
            return {"success": False, "error": f"Generated mask contains non-binary values: {non_bin}"}

        # 2. Save PNG to dataset/masks_verified/
        os.makedirs(VERIFIED_MASK_DIR, exist_ok=True)
        out_mask_path = os.path.join(VERIFIED_MASK_DIR, f"{name}.png")
        cv2.imwrite(out_mask_path, mask)

        # 3. Update Review Log
        if os.path.exists(LOG_JSON):
            with open(LOG_JSON, "r") as f:
                records = json.load(f)
        else:
            records = []

        now_iso = datetime.now(timezone.utc).isoformat()
        updated = False
        for r in records:
            if r["name"] == name:
                r["status"] = status
                r["polygon_vertices"] = polygon
                r["exclusion_polygons"] = exclusions
                r["truncated_borders"] = truncated_borders
                r["mouse_occlusion"] = mouse_occlusion
                r["reviewer_notes"] = reviewer_notes
                r["verified_at"] = now_iso if status == "manually_verified" else None
                r["verified_by"] = verified_by if status == "manually_verified" else None
                updated = True
                break

        if not updated:
            records.append({
                "name": name,
                "filename": f"{name}.jpg",
                "mask_filename": f"{name}.png",
                "dimensions": [w, h],
                "status": status,
                "polygon_vertices": polygon,
                "exclusion_polygons": exclusions,
                "truncated_borders": truncated_borders,
                "mouse_occlusion": mouse_occlusion,
                "reviewer_notes": reviewer_notes,
                "verified_at": now_iso,
                "verified_by": verified_by
            })

        with open(LOG_JSON, "w") as f:
            json.dump(records, f, indent=2)

        write_markdown_log(records)

        # 4. Refresh QC Contact Sheet
        qc_res = generate_qc_contact_sheet()

        return {
            "success": True,
            "name": name,
            "status": status,
            "mask_path": out_mask_path,
            "unique_values": unique_vals,
            "dimensions": [w, h],
            "qc_summary": qc_res
        }

def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AnnotationRequestHandler)
    print("=" * 70)
    print(f"Stage 3 Annotation Server running at http://localhost:{port}/")
    print(f"Dataset root: {WORKSPACE_ROOT}")
    print(f"Target verified masks dir: {os.path.join(WORKSPACE_ROOT, VERIFIED_MASK_DIR)}")
    print("Press Ctrl+C to stop server.")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nAnnotation server stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 3 Annotation Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind server (default: 8080)")
    args = parser.parse_args()
    run_server(args.port)

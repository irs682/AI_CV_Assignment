"""Local HTTP Server for Interactive Segmentation Ground-Truth Refinement.
Assessment: xis.ai 'Measure It - Segmentation and Metric Measurement'

Usage:
  python annotation_tool/server.py [--port 8080]
"""

import os
import sys
import json
import argparse
import re
import hashlib
import socket
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
EDITS_JSON = 'dataset/annotation_review_drafts.json'

def atomic_json(path, data):
    temporary=path+'.tmp'
    with open(temporary,'w') as f:
        json.dump(data,f,indent=2)
    os.replace(temporary,path)

def with_proposals(records):
    """Offer proposals without writing over review records or human work."""
    path = 'dataset/masks_proposed/proposals.json'
    proposals = {}
    if os.path.exists(path):
        with open(path) as f:
            proposals = {r['name']: r for r in json.load(f)}
    edits = json.load(open(EDITS_JSON)) if os.path.exists(EDITS_JSON) else {}
    for record in records:
        human_work = (record.get('status') == 'manually_verified'
                      or record.get('verified_at') or record.get('verified_by')
                      or (record.get('reviewer_notes') and not
                          (record.get('status') == 'automatically_proposed' and
                           record['reviewer_notes'].startswith('Automated proposal:')))
                      or os.path.exists(os.path.join(VERIFIED_MASK_DIR, record['name']+'.png')))
        if record['name'] in proposals and not human_work:
            record['draft_polygon_vertices'] = record.get('polygon_vertices', [])
            proposal = proposals[record['name']]
            for key in ['status','polygon_vertices','exclusion_polygons','truncated_borders','mouse_occlusion','reviewer_notes']:
                record[key] = proposal[key]
            record['proposal_flags'] = proposal['flags']
        record['uncertain'] = proposals.get(record['name'], {}).get('uncertain', True)
        record['proposal_flags'] = proposals.get(record['name'], {}).get('flags', [])
        approved = (record.get('status') == 'manually_verified' and record.get('verified_at')
                    and record.get('verified_by') and os.path.exists(os.path.join(VERIFIED_MASK_DIR, record['name']+'.png')))
        record['approved'] = bool(approved)
        edit = edits.get(record['name'])
        if edit and not approved:
            for key in ['polygon_vertices','exclusion_polygons','truncated_borders','mouse_occlusion','reviewer_notes','inspected_at','inspected_by','work_saved_at','draft_drawing_points','draft_mode']:
                if key in edit: record[key] = edit[key]
    return records

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
            self.wfile.write(json.dumps(with_proposals(data)).encode("utf-8"))
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
            try:
                result = self._save_verified_mask(payload)
            except (ValueError,TypeError,OSError,cv2.error) as error:
                result = {'success':False,'error':'Save failed: '+str(error)}
            self.send_response(200 if result.get("success") else 400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == '/api/review':
            payload = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
            name = payload.get('name', '')
            reviewer = str(payload.get('verified_by', '')).strip()
            if not re.fullmatch(r'notebook_\d{3}', name) or not os.path.exists(os.path.join(IMAGES_DIR, name+'.jpg')):
                result = {'success': False, 'error': 'Unknown image'}
            elif os.path.exists(os.path.join(VERIFIED_MASK_DIR,name+'.png')):
                result = {'success':False,'error':'Existing verified annotation is protected.'}
            elif payload.get('inspected') is not True or not reviewer:
                result = {'success': False, 'error': 'Enter your reviewer name and explicitly confirm inspection.'}
            else:
                edits = json.load(open(EDITS_JSON)) if os.path.exists(EDITS_JSON) else {}
                edits[name] = {'polygon_vertices':payload.get('polygon', []), 'exclusion_polygons':payload.get('exclusions', []),
                    'truncated_borders':payload.get('truncated_borders', []), 'mouse_occlusion':payload.get('mouse_occlusion', False),
                    'reviewer_notes':payload.get('reviewer_notes', ''), 'inspected_by':reviewer,
                    'inspected_at':datetime.now(timezone.utc).isoformat()}
                atomic_json(EDITS_JSON,edits)
                result = {'success': True, 'inspection': edits[name]}
            self.send_response(200 if result['success'] else 400)
            self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps(result).encode()); return

        if path == '/api/autosave':
            try:
                payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))))
                result=self._save_work(payload)
            except (ValueError,TypeError,OSError) as error:
                result={'success':False,'error':str(error)}
            self.send_response(200 if result['success'] else 400)
            self.send_header('Content-Type','application/json');self.end_headers()
            self.wfile.write(json.dumps(result).encode());return

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
        for r in with_proposals(records):
            if r["name"] == name:
                # Check if verified mask already exists on disk
                vmask_path = os.path.join(VERIFIED_MASK_DIR, f"{name}.png")
                r["has_verified_mask"] = os.path.exists(vmask_path)
                return r
        return {"error": f"Image {name} not found"}

    def _save_work(self, payload):
        name=payload.get('name','')
        if not re.fullmatch(r'notebook_\d{3}',name) or not os.path.exists(os.path.join(IMAGES_DIR,name+'.jpg')):
            return {'success':False,'error':'Unknown image'}
        if os.path.exists(os.path.join(VERIFIED_MASK_DIR,name+'.png')):
            return {'success':False,'error':'Verified annotation is protected; autosave did not change it.'}
        polygon=np.asarray(payload.get('polygon',[]))
        if polygon.ndim!=2 or polygon.shape[1]!=2 or len(polygon)<3 or not np.isfinite(polygon).all():
            return {'success':False,'error':'Invalid work polygon'}
        edits=json.load(open(EDITS_JSON)) if os.path.exists(EDITS_JSON) else {}
        # Work timestamps describe file saves, never human inspection/approval.
        edit={'polygon_vertices':payload['polygon'],'exclusion_polygons':payload.get('exclusions',[]),
            'truncated_borders':payload.get('truncated_borders',[]),'mouse_occlusion':payload.get('mouse_occlusion',False),
            'reviewer_notes':payload.get('reviewer_notes',''),'draft_drawing_points':payload.get('draft_drawing_points',[]),
            'draft_mode':payload.get('draft_mode','edit'),'work_saved_at':datetime.now(timezone.utc).isoformat()}
        edits[name]=edit
        atomic_json(EDITS_JSON,edits)
        return {'success':True,'work_saved_at':edit['work_saved_at'],'approved':False}

    def _save_verified_mask(self, payload):
        name = payload.get("name")
        polygon = payload.get("polygon", [])
        exclusions = payload.get("exclusions", [])
        status = payload.get("status", "automatically_proposed")
        truncated_borders = payload.get("truncated_borders", [])
        mouse_occlusion = payload.get("mouse_occlusion", False)
        reviewer_notes = payload.get("reviewer_notes", "")
        verified_by = str(payload.get("verified_by", "")).strip()

        if payload.get('inspected') is not True or not verified_by:
            return {'success': False, 'error': 'Enter your reviewer name and explicitly confirm you inspected this mask.'}
        if not re.fullmatch(r'notebook_\d{3}', str(name)):
            return {'success': False, 'error': 'Invalid image identifier'}
        if os.path.exists(os.path.join(VERIFIED_MASK_DIR,name+'.png')):
            return {'success':False,'error':'Existing verified annotation is protected. It was not overwritten.'}

        if status != 'manually_verified':
            return {'success': False, 'error': 'Finish human review and explicitly select Manually Verified before saving to masks_verified. Unapproved proposals remain in masks_proposed.'}

        if not name or not polygon or len(polygon) < 3:
            return {"success": False, "error": "Invalid polygon vertices (minimum 3 vertices required)"}

        # Check raw image dimensions
        img_path = os.path.join(IMAGES_DIR, f"{name}.jpg")
        img = cv2.imread(img_path)
        if img is None:
            return {"success": False, "error": f"Could not read source image {img_path}"}
        h, w = img.shape[:2]
        for points in [polygon] + exclusions:
            arr = np.asarray(points)
            if arr.ndim != 2 or arr.shape[1] != 2 or len(arr)<3 or not np.isfinite(arr).all() or np.any(arr<0) or np.any(arr[:,0]>=w) or np.any(arr[:,1]>=h):
                return {'success':False, 'error':'Polygons require at least three finite vertices inside the image.'}

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
        if not np.any(mask) or np.all(mask):
            return {'success':False, 'error':'Empty or full-image masks cannot be approved.'}
        non_bin = [v for v in unique_vals if v not in (0, 255)]
        if non_bin:
            return {"success": False, "error": f"Generated mask contains non-binary values: {non_bin}"}

        # 2. Save PNG to dataset/masks_verified/
        os.makedirs(VERIFIED_MASK_DIR, exist_ok=True)
        out_mask_path = os.path.join(VERIFIED_MASK_DIR, f"{name}.png")
        temporary_mask=out_mask_path+'.tmp.png'
        if not cv2.imwrite(temporary_mask, mask):
            return {'success':False,'error':'Could not write verified PNG; approval was not recorded.'}
        check=cv2.imread(temporary_mask,cv2.IMREAD_UNCHANGED)
        if check is None or not np.array_equal(check,mask):
            os.remove(temporary_mask)
            return {'success':False,'error':'PNG readback failed; approval was not recorded.'}
        os.replace(temporary_mask,out_mask_path)

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
                r['inspected_at'] = now_iso
                r['inspected_by'] = verified_by
                r['verified_mask_sha256'] = hashlib.sha256(open(out_mask_path,'rb').read()).hexdigest()
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

        try:
            atomic_json(LOG_JSON,records)
        except OSError as error:
            os.remove(out_mask_path) # Newly created file only; existing files are protected above.
            return {'success':False,'error':'Approval log failed; new mask rolled back: '+str(error)}

        try:
            write_markdown_log(records)
            qc_res = generate_qc_contact_sheet()
        except Exception as error:
            qc_res={'warning':'Mask and approval saved; secondary QC/log refresh failed: '+str(error)}

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
    class LocalServer(HTTPServer):
        allow_reuse_address = False
        def server_bind(self):
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            super().server_bind()
    server_address = ("127.0.0.1", port)
    httpd = LocalServer(server_address, AnnotationRequestHandler)
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

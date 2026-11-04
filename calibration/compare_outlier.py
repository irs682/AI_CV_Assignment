"""Non-destructive, single-outlier calibration comparison; no production writes."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from calibration import detect_corners, make_object_points


def main():
    base = Path(__file__).resolve().parent
    protected = sorted(p for folder in (base / 'images', base / 'parameters')
                       for p in folder.rglob('*') if p.is_file())
    hashes = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in protected}
    out = base / 'comparisons' / datetime.now(timezone.utc).strftime('exclude_002_%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True, exist_ok=False)
    metadata = json.loads((base / 'parameters/calibration_metadata.json').read_text())
    original = next(g for g in metadata['calibrations_by_resolution']
                    if g['image_size_px'] == {'width': 1500, 'height': 2000})
    detections = []
    for record in original['individual_image_errors']:
        detection, failure = detect_corners(base / 'images' / record['image'])
        if detection is None:
            raise RuntimeError(f"{record['image']}: {failure}; no silent exclusions")
        if detection.image.shape[:2] != (2000, 1500):
            raise RuntimeError('Unexpected image size')
        detections.append(detection)
        print(f'Detected {record["image"]}: {detection.method}', flush=True)
    objects = [make_object_points(d.pattern_size) for d in detections]
    points = [d.corners for d in detections]
    baseline = cv2.calibrateCamera(objects, points, (1500, 2000), None, None)
    keep = [i for i, d in enumerate(detections) if d.image_path.name != 'checkerboard_002.jpg']
    if len(keep) != 14:
        raise RuntimeError('Expected exactly 14 retained images')
    updated = cv2.calibrateCamera([objects[i] for i in keep], [points[i] for i in keep],
                                (1500, 2000), None, None)
    rms, matrix, distortion, rotations, translations = updated
    rows = []
    normals = []
    thumbs = []
    for i, d in enumerate(detections):
        retained = i in keep
        if retained:
            j = keep.index(i)
            rotation, translation = rotations[j], translations[j]
        else:
            ok, rotation, translation = cv2.solvePnP(objects[i], points[i], matrix, distortion)
            if not ok:
                raise RuntimeError('Excluded-image pose fit failed')
        projected, _ = cv2.projectPoints(objects[i], rotation, translation, matrix, distortion)
        error = float(np.sqrt(np.mean(np.sum((points[i].reshape(-1, 2) - projected.reshape(-1, 2)) ** 2, axis=1))))
        rot, _ = cv2.Rodrigues(rotation)
        normal = rot[:, 2]
        if normal[2] < 0:
            normal = -normal
        tilt = float(np.degrees(np.arccos(np.clip(normal[2], -1, 1))))
        tx = float(np.degrees(np.arctan2(normal[0], normal[2])))
        ty = float(np.degrees(np.arctan2(normal[1], normal[2])))
        xy = points[i].reshape(-1, 2)
        area = float(cv2.contourArea(cv2.convexHull(xy)) / (1500 * 2000))
        row = dict(image=d.image_path.name, retained=retained, detector=d.method,
                   original_error_px=original['individual_image_errors'][i]['reprojection_error_px'],
                   updated_error_px=error, tilt_deg=tilt, normal_x_angle_deg=tx,
                   normal_y_angle_deg=ty, centroid_x_px=float(xy[:, 0].mean()),
                   centroid_y_px=float(xy[:, 1].mean()), corner_hull_image_fraction=area)
        rows.append(row)
        if retained:
            normals.append(normal)
        thumb = cv2.resize(d.image, (225, 300))
        cv2.putText(thumb, d.image_path.stem, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 0, 255), 1)
        cv2.putText(thumb, f'tilt {tilt:.1f} deg', (5, 38), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 0, 255), 1)
        thumbs.append(thumb)
    cv2.imwrite(str(out / 'view_contact_sheet.jpg'), np.vstack([np.hstack(thumbs[i:i+5]) for i in range(0, 15, 5)]))
    angles = np.degrees(np.arccos(np.clip(np.array(normals) @ np.array(normals).T, -1, 1)))
    retained_rows = [r for r in rows if r['retained']]
    diversity = {key: [min(r[key] for r in retained_rows), max(r[key] for r in retained_rows)]
                 for key in ('tilt_deg', 'normal_x_angle_deg', 'normal_y_angle_deg',
                             'centroid_x_px', 'centroid_y_px', 'corner_hull_image_fraction')}
    diversity['max_pairwise_normal_angle_deg'] = float(angles.max())
    diversity['note'] = 'Pose estimates depend on the fitted intrinsics. Angular diversity and spatial coverage are diagnostics, not an accuracy certificate.'
    old_shared = float(np.sqrt(np.mean([r['original_error_px'] ** 2 for r in retained_rows])))
    np.savez_compressed(out / 'camera_parameters_1500x2000_excluding_002.npz',
                        camera_matrix=matrix, distortion_coefficients=distortion,
                        rms_reprojection_error_px=rms, image_size_wh=[1500, 2000],
                        rotation_vectors=rotations, translation_vectors=translations,
                        included_images=[detections[i].image_path.name for i in keep],
                        square_size_units='unit square')
    np.savez_compressed(out / 'detected_points.npz', image_points=np.array(points),
                        object_points=np.array(objects), images=[d.image_path.name for d in detections])
    unchanged = all(hashlib.sha256((base / name).read_bytes()).hexdigest() == digest
                    for name, digest in hashes.items())
    result = dict(opencv_version=cv2.__version__, original_saved_rms_px=original['rms_reprojection_error_px'],
                  reproduced_baseline_rms_px=float(baseline[0]), updated_rms_px=float(rms),
                  original_model_rms_on_same_14_images_px=old_shared,
                  rms_reduction_percent=100 * (1 - rms / original['rms_reprojection_error_px']),
                  original_image_count=15, updated_image_count=14,
                  excluded_images=['checkerboard_002.jpg'], camera_matrix=matrix.tolist(),
                  distortion_coefficients_order=['k1', 'k2', 'p1', 'p2', 'k3'],
                  distortion_coefficients=distortion.reshape(-1).tolist(), viewing_diversity=diversity,
                  per_image_results=rows, original_files_unchanged=unchanged,
                  caveats=['Excluded-image error uses pose fitted with fixed updated intrinsics; it is not independent validation.',
                           'Photographs came from a PDF (user-confirmed); prior geometric processing is unknown.',
                           'Physical checkerboard square size was not verified; unit-square coordinates do not establish millimetre scale.',
                           'Lower training RMS does not prove calibration accuracy or metric measurement accuracy.',
                           'No other images excluded; 1500x1125 model not recalibrated or written.'])
    (out / 'comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (out / 'preservation_sha256.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    with (out / 'per_image_comparison.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if not unchanged:
        raise RuntimeError('Original file preservation check failed')
    print(json.dumps(result, indent=2), flush=True)
    print(f'OUTPUT_DIRECTORY={out}', flush=True)


if __name__ == '__main__':
    main()

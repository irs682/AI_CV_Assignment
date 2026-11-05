"""Re-run existing calibration safely, preserving all archived measurements."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import calibration as implementation

def main():
    base=Path(__file__).resolve().parent
    protected=[p for folder in ['images','parameters','comparisons'] for p in (base/folder).rglob('*') if p.is_file()]
    hashes={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    output=base/'reproductions'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    implementation.OUTPUT_DIR=output
    implementation.DETECTED_DIR=output/'detected_corners'
    implementation.main()
    archived=json.loads((base/'parameters/calibration_metadata.json').read_text())
    reproduced=json.loads((output/'calibration_metadata.json').read_text())
    comparisons=[]
    for current in reproduced['calibrations_by_resolution']:
        old=next(r for r in archived['calibrations_by_resolution'] if r['image_size_px']==current['image_size_px'])
        comparisons.append({'resolution':current['image_size_px'],'images':current['image_count'],
            'archived_rms_px':old['rms_reprojection_error_px'],'reproduced_rms_px':current['rms_reprojection_error_px'],
            'rms_absolute_difference_px':abs(old['rms_reprojection_error_px']-current['rms_reprojection_error_px']),
            'camera_matrix_finite':bool(np.isfinite(current['camera_matrix']).all())})
    preserved=all(hashlib.sha256((base/p).read_bytes()).hexdigest()==digest for p,digest in hashes.items())
    summary={'detected_images':reproduced['detected_image_count'],'input_images':reproduced['input_image_count'],
        'failed_images':reproduced['failed_images'],'cohorts':comparisons,'archived_files_unchanged':preserved,
        'limitations':'Reprojection fit residuals only; no independent camera accuracy or physical scale validation.',
        'output_directory':str(output.relative_to(base.parent))}
    (output/'preservation_sha256.json').write_text(json.dumps(hashes,indent=2))
    (output/'verification_summary.json').write_text(json.dumps(summary,indent=2))
    evidence=base.parent/'docs/submission_evidence';evidence.mkdir(parents=True,exist_ok=True)
    (evidence/'calibration_verification.json').write_text(json.dumps(summary,indent=2))
    assert preserved,'Archived calibration data changed'
    assert reproduced['detected_image_count']==24 and not reproduced['failed_images'],'Detection incomplete'
    print('VERIFICATION_SUMMARY='+json.dumps(summary),flush=True)

if __name__=='__main__': main()

"""Read-only dataset audit; never copies photos, regenerates splits or approves masks."""
from pathlib import Path
import hashlib
import json
import subprocess
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    data=ROOT/'dataset'; expected={f'notebook_{i:03d}' for i in range(1,71)}
    errors=[];rows=[];protected={}
    for folder,extension in [('raw_images','jpg'),('images','jpg'),('masks','png'),('masks_proposed','png')]:
        files=list((data/folder).glob('*.'+extension))
        if {p.stem for p in files}!=expected: errors.append(f'{folder}: unexpected inventory')
        for p in files:
            if folder!='masks_proposed':protected[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    for name in sorted(expected):
        row={'name':name,'errors':[]}
        image=cv2.imread(str(data/'images'/f'{name}.jpg'))
        raw=cv2.imread(str(data/'raw_images'/f'{name}.jpg'))
        if image is None or raw is None: row['errors'].append('unreadable_photo')
        else:
            row['image_dimensions_wh']=[image.shape[1],image.shape[0]]
            if (data/'images'/f'{name}.jpg').read_bytes()!=(data/'raw_images'/f'{name}.jpg').read_bytes():row['errors'].append('raw_training_bytes_differ')
        for folder in ['masks','masks_proposed']:
            mask=cv2.imread(str(data/folder/f'{name}.png'),cv2.IMREAD_UNCHANGED)
            valid=bool(mask is not None and image is not None and mask.ndim==2 and mask.dtype==np.uint8 and mask.shape==image.shape[:2] and set(np.unique(mask))=={0,255})
            row[folder+'_structural_pass']=valid
            if not valid:row['errors'].append(folder+'_invalid_dimensions_or_binary_values')
        rows.append(row)
    splits={};seen=set()
    for split,count in [('train',49),('val',14),('test',7)]:
        path=data/'splits'/f'{split}.txt';content=path.read_bytes()
        protected[str(path.relative_to(ROOT))]=hashlib.sha256(content).hexdigest()
        names=[Path(line).stem for line in path.read_text().splitlines() if line.strip()]
        committed=subprocess.run(['git','show',f'HEAD:dataset/splits/{split}.txt'],cwd=ROOT,capture_output=True,check=True).stdout
        same=content.replace(b'\r\n',b'\n')==committed.replace(b'\r\n',b'\n')
        overlaps=sorted(seen.intersection(names));seen.update(names)
        splits[split]={'count':len(names),'sha256':hashlib.sha256(content).hexdigest(),'matches_committed_content':same,'overlaps':overlaps}
        if len(names)!=count or not same or overlaps:errors.append(f'{split}: split integrity failed')
    if seen!=expected:errors.append('split coverage differs from 70-image inventory')
    duplicate_groups={}
    for name in sorted(expected):
        digest=hashlib.sha256((data/'images'/f'{name}.jpg').read_bytes()).hexdigest()
        duplicate_groups.setdefault(digest,[]).append(name)
    duplicates=[names for names in duplicate_groups.values() if len(names)>1]
    if duplicates:errors.append('exact duplicate photographs')
    errors += [r['name']+': '+', '.join(r['errors']) for r in rows if r['errors']]
    preserved=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in protected.items())
    result={'images':len(rows),'draft_structural_pass':sum(r['masks_structural_pass'] for r in rows),'proposal_structural_pass':sum(r['masks_proposed_structural_pass'] for r in rows),'split_checks':splits,'exact_duplicate_groups':duplicates,'near_duplicate_note':'Existing committed grouping preserved; this audit does not independently validate visual near-duplicate separation.','errors':errors,'protected_files_unchanged':preserved,'records':rows}
    output=ROOT/'docs/submission_evidence';output.mkdir(parents=True,exist_ok=True)
    (output/'dataset_audit.json').write_text(json.dumps(result,indent=2))
    (output/'dataset_preservation_sha256.json').write_text(json.dumps(protected,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
    if errors or not preserved:raise SystemExit(1)

if __name__=='__main__':main()

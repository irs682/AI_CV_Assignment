"""Read-only annotation audit; writes reports and QC previews, never approvals."""
from pathlib import Path
import collections
import hashlib
import json
import subprocess
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dataset'

def run():
    out=DATA/'stage3_final_qc'; out.mkdir(exist_ok=True)
    protected=[p for folder in ['raw_images','images','masks','masks_verified','splits'] for p in (DATA/folder).glob('*') if p.is_file()]
    protected.append(DATA/'annotation_review_log.json')
    hashes=lambda: {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    before=hashes()
    records=json.loads((DATA/'annotation_review_log.json').read_text())
    grouped=collections.defaultdict(list)
    for r in records: grouped[r['name']].append(r)
    splits={}; split_checks={}; issues=[]
    for split in ['train','val','test']:
        path=DATA/'splits'/f'{split}.txt'
        names=[Path(x.strip()).stem for x in path.read_text().splitlines() if x.strip()]
        for name in names:
            if name in splits: issues.append(f'{name}: duplicate split membership')
            splits[name]=split
        rel=path.relative_to(ROOT).as_posix()
        committed=subprocess.run(['git','show',f'HEAD:{rel}'],cwd=ROOT,capture_output=True)
        split_checks[split]={'count':len(names),'matches_committed_content':committed.returncode==0 and committed.stdout.replace(b'\r\n',b'\n')==path.read_bytes().replace(b'\r\n',b'\n')}
    names=sorted(set(splits)|{p.stem for p in (DATA/'images').glob('*.jpg')}|{p.stem for p in (DATA/'masks_verified').glob('*.png')})
    rows=[]; cards=[]
    for name in names:
        photo=cv2.imread(str(DATA/'images'/f'{name}.jpg'))
        path=DATA/'masks_verified'/f'{name}.png'
        record=grouped[name][0] if len(grouped[name])==1 else {}
        problems=[]; evidence=record.get('status')=='manually_verified' and bool(record.get('verified_at')) and bool(record.get('verified_by'))
        if len(grouped[name])!=1: problems.append('missing_or_duplicate_review_record')
        if not evidence: problems.append('missing_complete_human_approval_record')
        if not path.exists(): problems.append('missing_verified_mask')
        mask=cv2.imread(str(path),cv2.IMREAD_UNCHANGED) if path.exists() else None
        values=None; valid=False
        if photo is None: problems.append('missing_or_unreadable_photo')
        if path.exists():
            if mask is None: problems.append('unreadable_verified_mask')
            else:
                values=np.unique(mask).tolist()
                if mask.ndim!=2 or mask.dtype!=np.uint8: problems.append('mask_not_single_channel_uint8')
                if photo is not None and mask.shape[:2]!=photo.shape[:2]: problems.append('dimension_mismatch')
                if not set(values)<={0,255}: problems.append('nonbinary_pixels')
                if not np.any(mask==255): problems.append('empty_foreground')
                if np.all(mask==255): problems.append('entire_image_foreground')
                valid=not any(p in problems for p in ['unreadable_verified_mask','mask_not_single_channel_uint8','dimension_mismatch','nonbinary_pixels','empty_foreground','entire_image_foreground','missing_or_unreadable_photo'])
        row=dict(name=name,split=splits.get(name),review_status=record.get('status','missing'),verified_file_exists=path.exists(),approval_record_complete=bool(evidence),structurally_valid=valid,counted_as_manually_verified=bool(evidence and path.exists()),pixel_values=values,problems=problems)
        rows.append(row)
        tile=np.full((210,240,3),25,np.uint8)
        if photo is not None:
            view=photo.copy()
            if valid:
                contours,_=cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(view,contours,-1,(0,255,0),3)
            h,w=view.shape[:2]; factor=min(240/w,165/h); resized=cv2.resize(view,(round(w*factor),round(h*factor)))
            y=(165-resized.shape[0])//2;x=(240-resized.shape[1])//2;tile[y:y+resized.shape[0],x:x+resized.shape[1]]=resized
        cv2.putText(tile,name+' '+str(row['split']),(4,181),0,.43,(240,240,240),1)
        label='APPROVED - CHECK CONTOUR' if evidence and valid else 'UNVERIFIED / BLOCKED'
        cv2.putText(tile,label,(4,201),0,.39,(0,230,0) if evidence and valid else (0,180,255),1)
        cards.append(tile)
    for page in range((len(cards)+19)//20):
        sheet=np.full((840,1200,3),25,np.uint8)
        for j,card in enumerate(cards[page*20:(page+1)*20]):
            y,x=divmod(j,5);sheet[y*210:(y+1)*210,x*240:(x+1)*240]=card
        cv2.imwrite(str(out/f'final_contact_sheet_{page+1:02d}.jpg'),sheet)
    master=np.full((7*210,10*240,3),25,np.uint8)
    for j,card in enumerate(cards):
        if j>=70: break
        y,x=divmod(j,10);master[y*210:(y+1)*210,x*240:(x+1)*240]=card
    cv2.imwrite(str(out/'final_contact_sheet_all.jpg'),master)
    ready=bool(rows) and all(r['counted_as_manually_verified'] and r['structurally_valid'] for r in rows) and not issues and [split_checks[s]['count'] for s in ['train','val','test']]==[49,14,7] and all(s['matches_committed_content'] for s in split_checks.values())
    summary=dict(images=len(rows),verified_png_files=sum(r['verified_file_exists'] for r in rows),complete_manual_approval_records=sum(r['approval_record_complete'] for r in rows),manually_verified_with_file=sum(r['counted_as_manually_verified'] for r in rows),structurally_valid_verified_masks=sum(r['structurally_valid'] for r in rows),unverified_or_problematic=sum(bool(r['problems']) for r in rows),review_status_counts=dict(collections.Counter(r.get('status','missing') for r in records)),split_checks=split_checks,split_issues=issues,ready_for_training=ready,protected_files_unchanged=hashes()==before)
    assert summary['protected_files_unchanged']
    (out/'verification_report.json').write_text(json.dumps({'summary':summary,'records':rows},indent=2))
    lines=['# Stage 3 verification report','','Dataset ready for U-Net training: **'+('YES' if ready else 'NO')+'**.','',f"Photographs: {len(rows)}. Verified PNG files: {summary['verified_png_files']}. Complete manual approval records: {summary['complete_manual_approval_records']}. Approval records with corresponding files: {summary['manually_verified_with_file']}.",'',f"Structurally valid verified masks: {summary['structurally_valid_verified_masks']}. Unverified or problematic cases: {summary['unverified_or_problematic']}.",'','Approval evidence means status manually_verified plus nonempty verified_at and verified_by, and a corresponding saved PNG. Metadata records approval; it cannot independently prove a human performed the review. Proposed masks are never counted as approvals.','', 'Validation checks single-channel uint8, matching image dimensions, values limited to 0 and 255, and nonempty/non-full foreground. These checks do not establish segmentation accuracy. With no verified mask, dimension/binary and boundary validation cannot pass for that image.','', 'Splits: '+json.dumps(split_checks)+'. Protected photographs, draft masks, verified artifacts, split files and review log unchanged by SHA-256.','', 'Final contact sheets are in dataset/stage3_final_qc/. Missing verified masks are explicitly labelled; proposals are not displayed as approved ground truth.','', '## Remaining cases','', '| Image | Split | Review status | Blockers |','|---|---|---|---|']
    lines += [f"| {r['name']} | {r['split']} | {r['review_status']} | {', '.join(r['problems'])} |" for r in rows if r['problems']]
    lines += ['', '## Next steps','', 'Review each mask in http://localhost:8080/?image=notebook_003 . Correct notebook edges, exclude overlapping mouse pixels, and check visible truncation. Explicitly select Manually Verified only after completing review, then Save & Verify Mask (Ctrl+S). Re-run `.venv\\Scripts\\python.exe dataset\\audit_stage3.py` after saving approvals.','', 'The lightweight U-Net configuration and verified-only loaders are prepared in models/. Training remains blocked until all required masks are approved and valid. No training was started, and no commits or pushes were performed.']
    (ROOT/'docs'/'stage3_verification_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': run()

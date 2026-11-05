"""Conservative OpenCV proposals; never changes originals or human review records."""
from pathlib import Path
import json, hashlib, csv
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'dataset'

def digest(paths):
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def editable_contour(contour, limit=24):
    perimeter=cv2.arcLength(contour,True)
    for fraction in np.linspace(.002,.008,25):
        points=cv2.approxPolyDP(contour,max(1.,fraction*perimeter),True).reshape(-1,2)
        if len(points)<=limit: break
    return points.tolist()

def self_intersects(poly):
    def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    n=len(poly)
    for i in range(n):
        a,b=poly[i],poly[(i+1)%n]
        for j in range(i+2,n):
            if (j+1)%n==i: continue
            c,d=poly[j],poly[(j+1)%n]
            if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0: return True
    return False

def snap_long_edges(image, polygon, exclusions, shape):
    """Conservative image-edge fitting; accepted only when edge support improves."""
    h,w=shape; factor=min(1.,800/max(h,w))
    small=cv2.resize(image,(round(w*factor),round(h*factor)))
    edges=cv2.Canny(cv2.cvtColor(small,cv2.COLOR_BGR2GRAY),50,140)
    ys,xs=np.nonzero(edges); points=np.column_stack([xs,ys]).astype(np.float32)
    poly=np.asarray(polygon,np.float32)*factor; lines=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]; delta=b-a; length=np.linalg.norm(delta)
        direction=delta/max(length,1); normal=np.array([-direction[1],direction[0]])
        line=(normal,float(normal@a))
        if length>60:
            relative=points-a; along=relative@direction; distance=np.abs(relative@normal)
            selected=points[(along>length*.1)&(along<length*.9)&(distance<4)]
            if len(selected)>length*.4:
                vx,vy,cx,cy=cv2.fitLine(selected,cv2.DIST_WELSCH,0,.01,.01).reshape(-1)
                fitted=np.array([-vy,vx]); center=np.array([cx,cy]); offset=float(fitted@center)
                if abs(fitted@normal)>.995 and max(abs(fitted@a-offset),abs(fitted@b-offset))<4:
                    line=(fitted,offset)
        lines.append(line)
    refined=[]
    for i,original in enumerate(poly):
        normals=np.stack([lines[i-1][0],lines[i][0]]); offsets=np.array([lines[i-1][1],lines[i][1]])
        point=np.linalg.solve(normals,offsets) if abs(np.linalg.det(normals))>.15 else original
        if np.linalg.norm(point-original)>6:point=original
        refined.append(np.rint(np.clip(point/factor,[0,0],[w-1,h-1])).astype(int).tolist())
    def support(vertices):
        mask=np.zeros(edges.shape,np.uint8)
        cv2.fillPoly(mask,[np.rint(np.array(vertices)*factor).astype(np.int32)],255)
        for hole in exclusions:cv2.fillPoly(mask,[np.rint(np.array(hole)*factor).astype(np.int32)],0)
        boundary=cv2.morphologyEx(mask,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
        aligned=cv2.dilate(edges,np.ones((5,5),np.uint8))>0
        return float(np.mean(aligned[boundary])) if boundary.any() else 0
    if not self_intersects(refined) and support(refined)>support(polygon)+.015:
        return refined,True
    return polygon,False

def run():
    cv2.setRNGSeed(17)
    protected = list((DATA/'raw_images').glob('*')) + list((DATA/'images').glob('*')) + list((DATA/'masks').glob('*')) + list((DATA/'splits').glob('*')) + list((DATA/'masks_verified').glob('*')) + [DATA/'annotation_review_log.json']
    protected = [p for p in protected if p.is_file()]
    before = digest(protected)
    out = DATA/'masks_proposed'; out.mkdir(exist_ok=True)
    qc = DATA/'refinement_qc'; qc.mkdir(exist_ok=True)
    records = []
    thumbs = []
    review=json.loads((DATA/'annotation_review_log.json').read_text())
    approved={r['name'] for r in review if r.get('status')=='manually_verified' or (DATA/'masks_verified'/f"{r['name']}.png").exists()}
    previous={r['name']:r for r in json.loads((out/'proposals.json').read_text())} if (out/'proposals.json').exists() else {}
    changed_previous=0;edge_updates=0;processed=0
    for path in sorted((DATA/'images').glob('*.jpg')):
        name = path.stem
        image = cv2.imread(str(path)); old = cv2.imread(str(DATA/'masks'/f'{name}.png'),0)
        if image is None or old is None: raise ValueError(f'Unreadable input: {name}')
        h,w = image.shape[:2]
        if old.shape != (h,w): raise ValueError(f'Dimension mismatch: {name}')
        if name in approved:
            if name not in previous:raise ValueError(f'Missing protected proposal metadata: {name}')
            records.append(previous[name])
            mask=cv2.imread(str(DATA/'masks_verified'/f'{name}.png'),0)
            overlay=image.copy();overlay[mask>0]=(overlay[mask>0]*.65+np.array([0,220,0])*.35).astype(np.uint8)
            thumb=cv2.resize(overlay,(240,180));cv2.putText(thumb,name+' APPROVED',(5,20),0,.45,(0,255,0),1);thumbs.append(thumb)
            print(name,'protected: skipped refinement',flush=True)
            continue
        processed+=1
        cv2.setRNGSeed(17+int(name.rsplit('_',1)[-1]))
        previous_mask=cv2.imread(str(out/f'{name}.png'),0) if (out/f'{name}.png').exists() else None
        scale = min(1., 800/max(h,w)); sw,sh = round(w*scale),round(h*scale)
        im = cv2.resize(image,(sw,sh)); draft = cv2.resize(old,(sw,sh),interpolation=cv2.INTER_NEAREST)
        hsv = cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        # Warm/pink/yellow ink anchors avoid neutral desk and blue upholstery.
        warm = (((hsv[:,:,0]<40)|(hsv[:,:,0]>135)) & (hsv[:,:,1]>125) & (hsv[:,:,2]>95)).astype('uint8')*255
        roi = cv2.dilate(draft,np.ones((41,41),np.uint8))
        warm &= roi
        n,lab,stats,_ = cv2.connectedComponentsWithStats(warm)
        clean = np.zeros_like(warm)
        for k in range(1,n):
            if stats[k,cv2.CC_STAT_AREA] > 30: clean[lab==k]=255
        points = cv2.findNonZero(clean)
        flags=[]
        if points is None or len(points)<100:
            result=draft.copy(); flags.append('color_initialization_failed')
        else:
            hull=cv2.convexHull(points)
            support=np.zeros_like(draft); cv2.fillPoly(support,[hull],255)
            support=cv2.dilate(support,np.ones((5,5),np.uint8))
            labels=np.full(draft.shape,cv2.GC_BGD,np.uint8)
            labels[cv2.dilate(support,np.ones((17,17),np.uint8))>0]=cv2.GC_PR_BGD
            labels[support>0]=cv2.GC_PR_FGD
            labels[clean>0]=cv2.GC_FGD
            # Mouse interiors are dark and mostly neutral; avoid subtracting red print.
            dark=((hsv[:,:,2]<85)&(hsv[:,:,1]<145)).astype('uint8')*255
            dark=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
            labels[dark>0]=cv2.GC_BGD
            try:
                cv2.grabCut(im,labels,None,np.zeros((1,65)),np.zeros((1,65)),4,cv2.GC_INIT_WITH_MASK)
                result=np.isin(labels,[cv2.GC_FGD,cv2.GC_PR_FGD]).astype('uint8')*255
                result &= support
                n,lab,stats,_=cv2.connectedComponentsWithStats(result)
                if n<2: raise ValueError('Empty foreground')
                result=(lab==(1+np.argmax(stats[1:,cv2.CC_STAT_AREA]))).astype('uint8')*255
                # Fill texture holes; retain only substantial dark-object cutouts.
                outer,_=cv2.findContours(result,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(result,outer,-1,255,-1)
                nd,dl,ds,_=cv2.connectedComponentsWithStats(dark)
                for di in range(1,nd):
                    if ds[di,cv2.CC_STAT_AREA] > .003*sw*sh:
                        result[dl==di]=0
            except (cv2.error,ValueError) as error:
                result=draft.copy(); flags.append('grabcut_failed: '+str(error))
        proposed=cv2.resize(result,(w,h),interpolation=cv2.INTER_NEAREST)
        # Image-guided seed corners for the two known bounding-box failures.
        # These are proposals from displayed photographs, never human approval.
        critical = {
            'notebook_003': (360,270, [[128,82],[329,88],[342,217],[120,211]]),
            'notebook_070': (720,540, [[104,125],[493,98],[514,333],[94,363]])}
        if name in critical:
            rw,rh,corners=critical[name]
            pts=np.rint(np.array(corners)*np.array([w/rw,h/rh])).astype(np.int32)
            proposed[:]=0; cv2.fillPoly(proposed,[pts],255)
            if name=='notebook_070':
                dh=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
                dark_full=((dh[:,:,2]<100)&(dh[:,:,1]<150)).astype('uint8')*255
                nc,lc,sc,_=cv2.connectedComponentsWithStats(dark_full)
                for ci in range(1,nc):
                    if sc[ci,cv2.CC_STAT_AREA]>.004*w*h:
                        proposed[lc==ci]=0
            result=cv2.resize(proposed,(sw,sh),interpolation=cv2.INTER_NEAREST)
            flags.append('image_guided_corner_seed_requires_review')
        contours,hierarchy=cv2.findContours(proposed,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        external=[i for i in range(len(contours)) if hierarchy[0,i,3]<0]
        main=max(external,key=lambda i:cv2.contourArea(contours[i]))
        # Simplify in pixel space, retaining occlusion notches and clipped edges.
        poly=editable_contour(contours[main])
        holes=[editable_contour(c,20) for i,c in enumerate(contours) if hierarchy[0,i,3]==main and cv2.contourArea(c)>25]
        poly,edge_refined=snap_long_edges(image,poly,holes,(h,w))
        edge_updates+=int(edge_refined)
        # Saved PNG and editable geometry must describe the same mask.
        smooth=np.zeros_like(proposed)
        cv2.fillPoly(smooth,[np.asarray(poly,np.int32)],255)
        for hole in holes:
            if len(hole)>=3: cv2.fillPoly(smooth,[np.asarray(hole,np.int32)],0)
        simplification_change=float(np.mean(smooth!=proposed))
        proposed=smooth
        changed_previous+=int(previous_mask is None or not np.array_equal(previous_mask,proposed))
        result=cv2.resize(proposed,(sw,sh),interpolation=cv2.INTER_NEAREST)
        contours,_=cv2.findContours(proposed,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        borders=[side for side,edge in [('top',proposed[0]),('bottom',proposed[-1]),('left',proposed[:,0]),('right',proposed[:,-1])] if np.count_nonzero(edge)>2]
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); edges=cv2.Canny(gray,50,140)
        boundary=cv2.morphologyEx(result,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
        aligned=cv2.dilate(edges,np.ones((5,5),np.uint8))>0
        alignment=float(np.mean(aligned[boundary])) if boundary.any() else 0.
        ratio=float(np.count_nonzero(proposed)/max(1,np.count_nonzero(old)))
        dark_fraction=float(np.mean((hsv[:,:,2][result>0]<65))) if np.any(result) else 1.
        if alignment<.65: flags.append('weak_boundary_alignment')
        if ratio<.65 or ratio>1.3: flags.append('large_area_change')
        if dark_fraction>.035: flags.append('dark_foreground_requires_inspection')
        if borders: flags.append('frame_contact_check_truncation')
        if len(poly)>24: flags.append('complex_boundary_check_occlusion_and_corners')
        if self_intersects(poly) or any(self_intersects(hole) for hole in holes): flags.append('self_intersection_requires_redraw')
        if holes: flags.append('mouse_or_dark_print_cutout_candidate')
        flags.append('pale_corners_glare_and_mouse_need_visual_review')
        flags.append('human_review_required')
        cv2.imwrite(str(out/f'{name}.png'),proposed)
        check=cv2.imread(str(out/f'{name}.png'),0)
        assert check.shape==(h,w) and check.dtype==np.uint8 and set(np.unique(check))=={0,255}
        overlay=image.copy(); overlay[proposed>0]=(overlay[proposed>0]*.65+np.array([0,220,0])*.35).astype(np.uint8)
        cv2.drawContours(overlay,contours,-1,(0,255,255),2)
        panels=[]
        for title,panel in [('Photograph',image),('Draft mask',cv2.cvtColor(old,cv2.COLOR_GRAY2BGR)),('Automatic proposal',cv2.cvtColor(proposed,cv2.COLOR_GRAY2BGR)),('Proposal overlay',overlay)]:
            thumb=cv2.resize(panel,(360,270)); cv2.putText(thumb,title,(8,23),0,.6,(255,100,40),2); panels.append(thumb)
        comparison=np.concatenate(panels,axis=1)
        cv2.imwrite(str(qc/f'{name}_comparison.jpg'),comparison)
        thumb=cv2.resize(overlay,(240,180)); cv2.putText(thumb,name,(5,20),0,.5,(0,0,255),2); thumbs.append(thumb)
        records.append(dict(name=name,status='automatically_proposed',structural_checks='pass',recommended_corrections='Inspect pale corners and glare; straighten visible edges; trace only visible notebook pixels; check mouse cutouts and frame contact.',vertex_count=len(poly),simplification_changed_fraction=simplification_change,polygon_vertices=poly,exclusion_polygons=holes,truncated_borders=borders,mouse_occlusion=bool(holes) or ratio<.9,mouse_detection='candidate_only',area_pixels=int(np.count_nonzero(proposed)),draft_area_pixels=int(np.count_nonzero(old)),area_ratio_to_draft=ratio,boundary_edge_support=alignment,dark_foreground_fraction=dark_fraction,changed_pixels=int(np.count_nonzero(proposed!=old)),uncertain=True,flags=flags,reviewer_notes='Automatic OpenCV proposal; inspect all boundaries, glare and mouse exclusions before approval.'))
        print(name, 'area ratio',round(ratio,3),'edge support',round(alignment,3),flush=True)
    for page in range((len(thumbs)+19)//20):
        sheet=np.full((4*180,5*240,3),230,np.uint8)
        for j,thumb in enumerate(thumbs[page*20:(page+1)*20]):
            y,x=divmod(j,5); sheet[y*180:(y+1)*180,x*240:(x+1)*240]=thumb
        cv2.imwrite(str(qc/f'contact_sheet_{page+1:02d}.jpg'),sheet)
    (out/'proposals.json').write_text(json.dumps(records,indent=2))
    for page in range((len(records)+9)//10):
        cards=[cv2.resize(cv2.imread(str(qc/f"{r['name']}_comparison.jpg")),(960,180)) for r in records[page*10:(page+1)*10]]
        cv2.imwrite(str(qc/f'comparison_sheet_{page+1:02d}.jpg'),np.concatenate(cards,axis=0))
    with (qc/'statistics.csv').open('w',newline='') as f:
        fields=['name','status','structural_checks','vertex_count','simplification_changed_fraction','area_pixels','draft_area_pixels','area_ratio_to_draft','boundary_edge_support','dark_foreground_fraction','changed_pixels','uncertain','flags','recommended_corrections']
        writer=csv.DictWriter(f,fields,extrasaction='ignore'); writer.writeheader(); writer.writerows(records)
    assert digest(protected)==before, 'Protected input changed'
    (qc/'protected_files_sha256.json').write_text(json.dumps(before,indent=2))
    summary=dict(processed=processed,protected_verified=len(approved),proposals_generated=processed,total_proposals=len(records),edge_refined_candidates=edge_updates,changed_from_previous_proposals=changed_previous,structural_checks_passed=len(records),uncertain=sum(r['uncertain'] for r in records if r['name'] not in approved),failed=sum(any('failed' in flag for flag in r['flags']) for r in records if r['name'] not in approved),requiring_manual_review=len(records)-len(approved),protected_files_unchanged=True)
    (qc/'summary.json').write_text(json.dumps(summary,indent=2)); print(summary)

if __name__=='__main__': run()

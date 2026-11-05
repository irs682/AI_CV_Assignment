"""Lightweight U-Net with a mandatory, read-only human-verification gate."""
from pathlib import Path
import hashlib
import json
import random
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def preflight(config, root=ROOT):
    records=json.loads((root/'dataset/annotation_review_log.json').read_text())
    by_name={r['name']:r for r in records}
    errors=[]; splits={}; seen=set()
    if len(by_name)!=len(records): errors.append('Duplicate review records')
    for split,expected in [('train',49),('val',14),('test',7)]:
        path=root/'dataset/splits'/f'{split}.txt'
        if hashlib.sha256(path.read_bytes()).hexdigest()!=config['split_sha256'][split]: errors.append(f'{split}: split hash changed')
        names=[Path(line.strip()).stem for line in path.read_text().splitlines() if line.strip()]
        if len(names)!=expected: errors.append(f'{split}: expected {expected} images')
        splits[split]=names
        for name in names:
            if name in seen: errors.append(f'{name}: split overlap')
            seen.add(name); r=by_name.get(name,{})
            mask_path=root/'dataset/masks_verified'/f'{name}.png'
            if r.get('status')!='manually_verified' or not r.get('verified_at') or not r.get('verified_by') or not mask_path.exists():
                errors.append(f'{name}: human approval and verified mask required'); continue
            image=cv2.imread(str(root/'dataset/images'/f'{name}.jpg'))
            mask=cv2.imread(str(mask_path),cv2.IMREAD_UNCHANGED)
            if image is None or mask is None or mask.ndim!=2 or mask.dtype!=np.uint8 or mask.shape!=image.shape[:2] or not set(np.unique(mask))<={0,255} or not np.any(mask) or np.all(mask):
                errors.append(f'{name}: invalid verified image/mask pair')
            if r.get('verified_mask_sha256') and hashlib.sha256(mask_path.read_bytes()).hexdigest()!=r['verified_mask_sha256']:
                errors.append(f'{name}: mask changed since approval')
    if errors: raise RuntimeError('Training blocked before model initialization:\n'+'\n'.join(errors))
    return splits

def load_pair(name, size, root=ROOT):
    image=cv2.imread(str(root/'dataset/images'/f'{name}.jpg'))
    mask=cv2.imread(str(root/'dataset/masks_verified'/f'{name}.png'),0)
    if image is None or mask is None: raise ValueError(f'Missing verified pair: {name}')
    h,w=image.shape[:2]; scale=min(size/w,size/h); rw,rh=round(w*scale),round(h*scale)
    x=(size-rw)//2; y=(size-rh)//2
    rgb=np.zeros((size,size,3),np.float32); target=np.zeros((size,size),np.float32)
    rgb[y:y+rh,x:x+rw]=cv2.cvtColor(cv2.resize(image,(rw,rh)),cv2.COLOR_BGR2RGB)/255.
    target[y:y+rh,x:x+rw]=cv2.resize(mask,(rw,rh),interpolation=cv2.INTER_NEAREST)/255.
    return rgb.transpose(2,0,1).copy(),target[None].copy()

class VerifiedDataset:
    def __init__(self,names,size,root=ROOT): self.names,self.size,self.root=names,size,root
    def __len__(self): return len(self.names)
    def __getitem__(self,index):
        import torch
        image,mask=load_pair(self.names[index],self.size,self.root)
        return torch.from_numpy(image),torch.from_numpy(mask)

def build_unet(base=16):
    import torch
    from torch import nn
    def block(a,b): return nn.Sequential(nn.Conv2d(a,b,3,padding=1),nn.GroupNorm(4,b),nn.ReLU(),nn.Conv2d(b,b,3,padding=1),nn.GroupNorm(4,b),nn.ReLU())
    class SmallUNet(nn.Module):
        def __init__(self):
            super().__init__(); self.e1=block(3,base); self.e2=block(base,base*2); self.e3=block(base*2,base*4)
            self.b=block(base*4,base*8); self.d3=block(base*12,base*4); self.d2=block(base*6,base*2); self.d1=block(base*3,base); self.out=nn.Conv2d(base,1,1); self.pool=nn.MaxPool2d(2)
        def forward(self,x):
            a=self.e1(x); b=self.e2(self.pool(a)); c=self.e3(self.pool(b)); d=self.b(self.pool(c))
            def up(x,skip): return torch.cat([nn.functional.interpolate(x,size=skip.shape[-2:],mode='bilinear',align_corners=False),skip],1)
            return self.out(self.d1(up(self.d2(up(self.d3(up(d,c)),b)),a)))
    return SmallUNet()

def run(config_path, evaluate=None, check_only=False):
    config=json.loads(Path(config_path).read_text())
    splits=preflight(config)  # Mandatory before torch import, loader/model setup or output writes.
    if check_only: print('All 70 human-approved masks passed preflight.'); return
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    random.seed(config['seed']); np.random.seed(config['seed']); torch.manual_seed(config['seed'])
    torch.use_deterministic_algorithms(True); torch.set_num_threads(config['cpu_threads'])
    device=torch.device(config['device']); model=build_unet(config['base_channels']).to(device)
    loaders={s:DataLoader(VerifiedDataset(names,config['image_size']),batch_size=config['batch_size'],shuffle=s=='train',num_workers=0) for s,names in splits.items()}
    bce=nn.BCEWithLogitsLoss()
    def loss(logits,target):
        p=logits.sigmoid(); dims=(1,2,3)
        dice=1-((2*(p*target).sum(dims)+1)/(p.sum(dims)+target.sum(dims)+1)).mean()
        return .5*bce(logits,target)+.5*dice
    def validation(loader):
        model.eval(); total=0.
        with torch.no_grad():
            for images,masks in loader:
                images,masks=images.to(device),masks.to(device);total+=float(loss(model(images),masks))*len(images)
        return total/len(loader.dataset)
    if evaluate:
        model.load_state_dict(torch.load(evaluate,map_location=device,weights_only=True))
        print(json.dumps({'held_out_test_loss':validation(loaders['test'])})); return
    optimizer=torch.optim.AdamW(model.parameters(),lr=config['learning_rate'],weight_decay=config['weight_decay'])
    output=ROOT/config['output_dir'];output.mkdir(parents=True,exist_ok=True)
    (output/'config.json').write_text(json.dumps(config,indent=2)); history=[]; best=float('inf'); stale=0
    for epoch in range(config['epochs']):
        model.train(); total=0.
        for images,masks in loaders['train']:
            images,masks=images.to(device),masks.to(device);optimizer.zero_grad(set_to_none=True)
            value=loss(model(images),masks);value.backward();optimizer.step();total+=float(value.detach())*len(images)
        score=validation(loaders['val']); row={'epoch':epoch+1,'train_loss':total/49,'val_loss':score};history.append(row); print(row,flush=True)
        (output/'history.json').write_text(json.dumps(history,indent=2))
        if score<best:
            best=score;stale=0;torch.save(model.state_dict(),output/'best.pt')
        else: stale+=1
        if stale>=config['early_stopping_patience']: break

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(ROOT/'models/unet_laptop.json'))
    parser.add_argument('--check-only',action='store_true');parser.add_argument('--evaluate',metavar='CHECKPOINT')
    args=parser.parse_args()
    try: run(args.config,args.evaluate,args.check_only)
    except RuntimeError as error: parser.exit(2,str(error)+'\n')

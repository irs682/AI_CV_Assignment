"""Reproduce quick submission checks without training, approval or split generation."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys
import shutil
import urllib.request

ROOT=Path(__file__).resolve().parent

def main():
    output=ROOT/'docs/submission_evidence';output.mkdir(parents=True,exist_ok=True)
    checks=[]
    commands=[(['dataset/audit_dataset.py'],0),(['dataset/audit_stage3.py'],0),(['annotation_tool/refine_cli.py','qc'],0),
              (['-m','unittest','discover','-s','tests','-v'],0),
              (['models/training_pipeline.py','--check-only'],2),(['-m','pip','check'],0)]
    for args,expected in commands:
        if '--check-only' in args:
            audit=json.loads((ROOT/'dataset/stage3_final_qc/verification_report.json').read_text())
            expected=0 if audit['summary']['ready_for_training'] else 2
        result=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)
        passed=result.returncode==expected
        checks.append({'command':[str(Path(sys.executable).relative_to(ROOT)),*args],
            'expected_exit_code':expected,'actual_exit_code':result.returncode,'passed':passed,
            'stdout':result.stdout,'stderr':result.stderr})
        print(('PASS' if passed else 'FAIL')+' '+' '.join(args)+f' (exit {result.returncode})',flush=True)
    if shutil.which('node'):
        result=subprocess.run(['node','tests/test_review_ui.cjs'],cwd=ROOT,capture_output=True,text=True)
        checks.append({'command':['node','tests/test_review_ui.cjs'],'expected_exit_code':0,
            'actual_exit_code':result.returncode,'passed':result.returncode==0,'stdout':result.stdout,'stderr':result.stderr})
        print(('PASS' if result.returncode==0 else 'FAIL')+' isolated review UI logic tests',flush=True)
    try:
        with urllib.request.urlopen('http://localhost:8080/api/images',timeout=10) as response:
            records=json.load(response)
        with urllib.request.urlopen('http://localhost:8080/?image=notebook_003',timeout=10) as response:
            html=response.read().decode()
        web={'reachable':True,'records':len(records),'approved':sum(bool(r.get('approved')) for r in records),
            'review_controls_present':all(x in html for x in ['review-progress','inspection-confirm','btn-save-review'])}
    except Exception as error:web={'reachable':False,'error':str(error)}
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'annotation_http':web,
        'note':'Expected preflight exit 2 means training was blocked; no training command was run. HTTP checks do not exercise all browser interactions.'}
    (output/'command_checks.json').write_text(json.dumps(result,indent=2))
    freeze=subprocess.run([sys.executable,'-m','pip','freeze'],cwd=ROOT,capture_output=True,text=True,check=True)
    (output/'environment-lock.txt').write_text(freeze.stdout)
    versions=subprocess.run([sys.executable,'-c','import sys,cv2,numpy,torch; print(sys.version); print("OpenCV",cv2.__version__,"NumPy",numpy.__version__,"PyTorch",torch.__version__)'],capture_output=True,text=True,check=True)
    (output/'environment.txt').write_text(versions.stdout)
    print(json.dumps(web),flush=True)
    if not all(c['passed'] for c in checks) or not web.get('reachable'):raise SystemExit(1)

if __name__=='__main__':main()

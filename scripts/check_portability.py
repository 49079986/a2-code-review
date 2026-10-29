"""Create an isolated moved copy for subpath/browser QA; never alter source folders."""
from pathlib import Path
import shutil, subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'reports/qa/relocated/A2 study'
assert DEST.resolve().is_relative_to(ROOT/'reports/qa')
if DEST.exists():raise SystemExit('QA copy already exists; inspect it before choosing a fresh destination.')
shutil.copytree(ROOT,DEST,ignore=shutil.ignore_patterns('qa','__pycache__','.git','extracted'))
result=subprocess.run([sys.executable,str(DEST/'scripts/verify.py')],cwd=DEST,check=False)
print('Moved copy:',DEST)
raise SystemExit(result.returncode)

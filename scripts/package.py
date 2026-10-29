"""Create a clean transferable source bundle without caches, runtime trees or QA copies."""
from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'A2-code-review.zip'
SKIP={'__pycache__','.git','.venv','venv','node_modules','.build-deps'}
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(ROOT)
    if any(x in SKIP for x in rel.parts):continue
    if rel.parts[:2] in [('reports','qa'),('data','extracted')]:continue
    if p.suffix.lower() in {'.zip','.pyc','.tmp','.bak'} or p.name.startswith('.env'):continue
    if rel.as_posix()=='reports/delivery.json':continue
    files.append((p,rel))
with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p,rel in files:z.write(p,'A2-code-review/'+rel.as_posix())
with zipfile.ZipFile(TARGET) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert 'A2-code-review/index.html' in names
    assert not any('/qa/' in x or '/extracted/' in x or '__pycache__' in x for x in names)
result={'archive':TARGET.name,'files':len(files),'bytes':TARGET.stat().st_size,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'excluded':['reports/qa','data/extracted','__pycache__','.git','.venv','node_modules','*.zip','*.pyc','.env*'],'crc_check':'passed'}
(ROOT/'reports/delivery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))

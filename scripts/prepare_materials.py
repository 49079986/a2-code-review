"""Copy a reviewed allowlist, extract original embedded images, render source pages.
Run only to import/update sources. Ordinary site generation uses bundled data only.
"""
from pathlib import Path
import json, hashlib, shutil, re
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
A2=ROOT.parent/'A2'; STUDY=ROOT.parent/'Study'
def put(src,dst):
    target=ROOT/dst; target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
    return {'source':str(src.relative_to(ROOT.parent)).replace('\\','/'),'path':dst,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}
manifest=[]
for src,dst in [
 (A2/'a2-2026-v1.pdf','materials/assignment.pdf'),
 (A2/'a2-2026-fleetdb.sql','materials/setup.sql'),
 (A2/'原生截图更新版/49079984_A2.pdf','materials/report-native.pdf'),
 (A2/'原生截图更新版/49079984_A2.docx','materials/report-native.docx'),
 (A2/'49079984_A2.pdf','materials/report-root.pdf'),
 (A2/'49079984_A2.docx','materials/report-root.docx'),
 (A2/'补齐版/49079984_A2.pdf','materials/report-supplemented.pdf'),
 (A2/'completed/49079984_A2.pdf','materials/report-completed.pdf'),
 (A2/'Wait-for.jpg','assets/images/wait-for-original.jpg'),
 (STUDY/'source/a2-special/original-tasks.json','data/original-tasks.json'),
 (STUDY/'source/a2-special/line-explanations.json','data/study-lines.json'),
 (STUDY/'source/a2-study-notes.json','data/study-notes.json')]:
    if src.exists():manifest.append(put(src,dst))
for p in sorted(A2.glob('49079984_A2_*.sql')):manifest.append(put(p,'materials/sql/'+p.name))
for p in sorted((A2/'completed/evidence').glob('*.txt')):manifest.append(put(p,'materials/logs/completed/'+p.name))
for p in sorted((A2/'screenshots').iterdir()):
    if p.suffix.lower() in {'.png','.svg','.md'}:manifest.append(put(p,('assets/images/native/' if p.suffix.lower()!='.md' else 'materials/notes/')+p.name))
# Replayed result cards/logs are retained explicitly as a separate run.
for p in sorted((STUDY/'assignments/a2/evidence').glob('*.txt')):manifest.append(put(p,'materials/logs/study-replay/'+p.name))

pages={};figures=[]
for kind,file in [('assignment','materials/assignment.pdf'),('report','materials/report-native.pdf')]:
    doc=pymupdf.open(ROOT/file)
    out=ROOT/'assets/images'/kind;out.mkdir(parents=True,exist_ok=True)
    pages[kind]=[]
    for i,page in enumerate(doc):
        imagepath=f'assets/images/{kind}/page-{i+1:02}.jpg'
        pix=page.get_pixmap(matrix=pymupdf.Matrix(1.65,1.65))
        pix.save(ROOT/imagepath,jpg_quality=86)
        text=page.get_text()
        pages[kind].append({'page':i+1,'text':text,'image':imagepath,'pdf':file})
        if kind=='report':
            for j,img in enumerate(page.get_images(full=True)):
                xref=img[0];raw=doc.extract_image(xref);digest=hashlib.sha256(raw['image']).hexdigest()
                rel=f'assets/images/report/embedded-{digest[:16]}.{raw["ext"]}'
                (ROOT/rel).write_bytes(raw['image'])
                rects=page.get_image_rects(xref)
                caption=''
                if rects:
                    y=rects[0].y0
                    blocks=[b for b in page.get_text('blocks') if b[3]<=y+4 and b[4].strip()]
                    caption=blocks[-1][4].strip() if blocks else ''
                figures.append({'id':f'r{i+1:02}-{j+1}','page':i+1,'index':j+1,'image':rel,'width':raw['width'],'height':raw['height'],'caption':caption})
    print(kind,len(doc),'pages')
(ROOT/'data/materials.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/source-pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/figures.json').write_text(json.dumps(figures,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(figures),'embedded figures; material files',len(manifest))

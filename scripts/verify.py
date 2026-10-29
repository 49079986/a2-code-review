"""Offline structural checks: links, anchors, source bytes, required lesson sections."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.scripts=[];self.code='';self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ['href','src']:
            if attrs.get(key):self.links.append((tag,key,attrs[key]))
def main():
    files=sorted(ROOT.glob('*.html'))+sorted((ROOT/'pages').glob('*.html'))
    parsed={p:Page(p.read_text(encoding='utf-8')) for p in files};errors=[];links=0
    for p,doc in parsed.items():
        duplicates={id for id in doc.ids if doc.ids.count(id)>1}
        if duplicates:errors.append(f'{p.name}: duplicate ids {duplicates}')
        for tag,attr,link in doc.links:
            u=urlsplit(link)
            if u.scheme in ['http','https','mailto','tel','data']:continue
            if u.scheme or link.startswith(('/', '\\')):errors.append(f'{p.name}: absolute/nonportable {link}');continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p
            links+=1
            if not target.is_relative_to(ROOT):errors.append(f'{p.name}: escapes project {link}');continue
            if not target.exists():errors.append(f'{p.name}: missing {link}');continue
            # Check every component spelling for case-sensitive GitHub Pages.
            rel=target.relative_to(ROOT);base=ROOT
            for part in rel.parts:
                if part not in {x.name for x in base.iterdir()}:errors.append(f'{p.name}: case mismatch {link}');break
                base=base/part
            if u.fragment and target.suffix=='.html':
                dest=parsed.get(target)
                if dest is None:dest=Page(target.read_text(encoding='utf-8'))
                if unquote(u.fragment) not in dest.ids:errors.append(f'{p.name}: missing anchor {link}')
    originals=json.loads((ROOT/'data/original-tasks.json').read_text(encoding='utf-8'))
    lines=json.loads((ROOT/'data/current-lines.json').read_text(encoding='utf-8'))
    source_pages=json.loads((ROOT/'data/source-pages.json').read_text(encoding='utf-8'))
    original_text=' '.join(' '.join(re.sub(r'^\s*\d+\s*','',p['text']).split()) for p in source_pages['assignment'])
    for q,o in originals.items():
        for field in ['context','text']:
            if ' '.join(o[field].split()) not in original_text:errors.append(q+': original English differs from assignment extraction')
    from lesson_content import LESSONS
    from figure_notes import FIGURE_NOTES
    for q in LESSONS:
        p=ROOT/'pages'/('q'+q.replace('.','-')+'.html');text=p.read_text(encoding='utf-8');doc=parsed[p]
        for id in ['original','translation','task','background','code','lines','terms','evidence','derive','practice']:
            if id not in doc.ids:errors.append(q+': missing section '+id)
        if q not in originals:errors.append(q+': no original')
        if q in lines:
            source=(ROOT/'materials/sql'/f'49079984_A2_{q}.sql').read_text(encoding='utf-8-sig').splitlines()
            if source != [x['code'] for x in lines[q]]:errors.append(q+': SQL changed')
            if [x['number'] for x in lines[q]] != list(range(1,len(source)+1)):errors.append(q+': wrong line numbers')
            if any(not x['zh'] or not x['en'] for x in lines[q]):errors.append(q+': empty line teaching')
    manifest=json.loads((ROOT/'data/materials.json').read_text(encoding='utf-8'))
    for item in manifest:
        file=ROOT/item['path']
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=item['sha256']:errors.append('source hash changed '+item['path'])
    for p in files:
        text=p.read_text(encoding='utf-8')
        if re.search(r'(?:href|src)=[\"\'][A-Za-z]:',text):errors.append(p.name+': local machine path')
        for marker in ['TODO','待补充占位','互动演示正在准备','lorem ipsum']:
            if marker in text:errors.append(p.name+': placeholder '+marker)
    figures=json.loads((ROOT/'data/figures.json').read_text(encoding='utf-8'))
    if set(FIGURE_NOTES)!={x['id'] for x in figures}:errors.append('figure annotation coverage mismatch')
    result={'date':'2026-10-29','html_pages':len(files),'lessons':len(LESSONS),'sql_files':len(lines),'sql_physical_lines':sum(map(len,lines.values())),'report_embedded_figures':len(figures),'local_links_and_resources':links,'preserved_source_hashes':len(manifest),'errors':errors,'passed':not errors}
    (ROOT/'reports/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));return bool(errors)
if __name__=='__main__':sys.exit(main())

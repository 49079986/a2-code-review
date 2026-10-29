"""Rebuild every static page from project-local editorial data. Python stdlib only."""
from pathlib import Path
from html import escape as E
import json, re, sys, posixpath
from urllib.parse import urlsplit, urlunsplit
from lesson_content import LESSONS, CONTEXT, GROUP_PREREQ, SCAN_ROWS, SUGGESTIONS
from glossary import TERMS
from figure_notes import FIGURE_NOTES
from teaching_examples import EXAMPLES, EXTRA_QUIZZES

ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
ORIGINALS=read('original-tasks.json'); LINES=read('current-lines.json'); FIGURES=read('figures.json'); SOURCE_PAGES=read('source-pages.json'); MATERIALS=read('materials.json')
IDS=list(LESSONS)
assert set(IDS)==set(ORIGINALS)-{'_q4_background'}
assert len(IDS)==24 and len(LINES)==20 and sum(map(len,LINES.values()))==395
assert {x['id'] for x in FIGURES}==set(FIGURE_NOTES)
for q,lines in LINES.items():
    sql=(ROOT/'materials/sql'/f'49079984_A2_{q}.sql').read_text(encoding='utf-8-sig')
    assert sql.splitlines()==[x['code'] for x in lines],q
GROUPS=[('1','视图与账户责任','Views & recursion'),('2','索引与性能','Indexes & performance'),('3','查询与执行计划','Queries & plans'),('4','事务与死锁','Transactions & locks')]
SECTIONS=[('original','01','英文原题'),('translation','02','忠实翻译'),('task','03','题目要我做什么'),('background','04','前置知识'),('code','05','完整原始代码'),('lines','06','分段与逐行解释'),('terms','07','函数、语法与符号'),('evidence','08','截图与执行结果'),('derive','09','完整解题推导'),('practice','10','自测与口头讲解')]
def path(q):return 'q'+q.replace('.','-')+'.html'
def para(value,cls=''):
    if isinstance(value,list):return ''.join(para(x,cls) for x in value)
    return f'<p class="{cls}">{E(value)}</p>'
def badge(text,cls=''):return f'<span class="badge {cls}">{E(text)}</span>'
def table(headers,rows):return '<div class="table-wrap" tabindex="0" role="region" aria-label="数据表格，窄窗口可横向滚动"><table><thead><tr>'+''.join('<th>'+E(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(str(x))+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def highlight(text):
    pattern=r"(--.*$|'(?:''|[^'])*'|\\\w+|\b(?:CREATE|OR|REPLACE|VIEW|MATERIALIZED|AS|WITH|RECURSIVE|SELECT|DISTINCT|ON|FROM|JOIN|LEFT|RIGHT|WHERE|AND|NOT|EXISTS|NULL|IS|GROUP|BY|ORDER|DESC|ASC|LIMIT|UNION|ALL|OVER|PARTITION|INDEX|EXPLAIN|ANALYZE|BUFFERS|SET|SHOW|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|INSERT|INTO|VALUES|UPDATE|RETURNING|REFRESH|TIMESTAMP|INTERVAL|IF|THEN|ELSIF|END|RETURN|DECLARE|RETURNS|TRIGGER|FUNCTION|BEFORE|FOR|EACH|ROW|EXECUTE|LANGUAGE|RAISE|EXCEPTION)\b|\b(?:COUNT|SUM|COALESCE|LOWER|SPLIT_PART|ROW_NUMBER|RANK|NOW|PG_BACKEND_PID|CURRENT_DATABASE)\b|\b\d+(?:\.\d+)?\b)"
    out=[];pos=0
    for m in re.finditer(pattern,text,re.I):
        out.append(E(text[pos:m.start()]));v=m[0]
        cls='comment' if v.startswith('--') else 'string' if v.startswith("'") else 'number' if v[0].isdigit() else 'keyword'
        out.append(f'<span class="sql-{cls}">{E(v)}</span>');pos=m.end()
    out.append(E(text[pos:]));return ''.join(out)
def codeblock(sql,q='example',label='教学示例 · 未执行',download=None):
    safe=q.replace('.','-')
    raw=json.dumps(sql,ensure_ascii=False).replace('<','\\u003c')
    return f'''<div class="code-block" data-code-id="{safe}"><div class="code-toolbar"><span>{E(label)}</span><div><button type="button" data-copy>复制代码</button><button type="button" data-manual-copy>手动复制</button>{f'<a href="{download}" download>下载 SQL ↓</a>' if download else ''}</div></div><pre tabindex="0" aria-label="{E(label)}"><code>{''.join(f'<span class="code-line" id="q-{safe}-L{i}"><a class="line-no" href="#q-{safe}-L{i}" aria-label="第{i}行">{i}</a><span class="code-text">{highlight(line) or " "}</span></span>' for i,line in enumerate(sql.splitlines(),1))}</code></pre><script type="application/json" class="raw-code">{raw}</script><div class="line-jump"><label>定位行号 <input type="number" min="1" max="{len(sql.splitlines())}" value="1" aria-label="定位行号"></label><button type="button" data-line-jump>跳转</button><span>横向滚动读长行 · 原始缩进与注释完整保留</span></div></div>'''

def nav(prefix,active):
    utilities=[('index.html','学习路线','00 / START'),('pages/foundations.html','从零开始','DATABASE BASICS'),('pages/glossary.html','术语与函数','REFERENCE'),('pages/evidence.html','截图与结果','EVIDENCE'),('pages/materials.html','原始资料与版本','SOURCES'),('complete.html','连续阅读 / 打印','FULL BOOK')]
    s='<a class="brand" href="'+prefix+'index.html"><span class="brand-icon">a<span>2</span></span><span>A2 / Code Review<small>INFS 7903 · 学习手册</small></span></a><div class="sidebar-inner"><p class="nav-label">YOUR LEARNING SPACE</p><nav aria-label="学习导航">'
    for url,label,en in utilities:
        s+=f'<a class="nav-link {"active" if active==url else ""}" href="{prefix+url}" {"aria-current=page" if active==url else ""}><span>{label}</span><small>{en}</small></a>'
    for g,zh,en in GROUPS:
        s+=f'<p class="nav-label">0{g} / {zh}</p>'
        for q,item in LESSONS.items():
            if q[0]!=g:continue
            url='pages/'+path(q)
            s+=f'<a class="question-link {"active" if active==url else ""}" data-progress-link="{q}" href="{prefix+url}" {"aria-current=page" if active==url else ""}><span class="nav-q">{q}</span><span>{E(item["title"])}</span><i aria-hidden="true"></i></a>'
    return s+'</nav><div class="sidebar-bottom"><div><span>学习进度</span><strong data-progress-count>0 / 24</strong></div><progress data-progress-bar max="24" value="0">0 / 24</progress><small>保存在此浏览器 · 支持离线阅读</small></div></div>'

def shell(title,body,active='index.html',depth=0,toc='',description='从原题到代码、截图与数据库原理的双语学习手册'):
    p='../'*depth
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{E(description)}"><meta name="color-scheme" content="dark light"><title>{E(title)} · A2 Code Review</title><link rel="icon" href="{p}assets/images/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{p}assets/css/site.css"><script src="{p}data/search-index.js" defer></script><script src="{p}assets/js/app.js" defer></script></head><body data-root="{p}" data-page="{E(active)}"><a class="skip-link" href="#main">跳到正文</a><aside class="sidebar" id="sidebar">{nav(p,active)}</aside><div class="workspace"><header class="topbar"><button type="button" class="menu-button" aria-controls="sidebar" aria-expanded="false">☰ <span>目录</span></button><span class="top-label">A2 LEARNING STUDIO <span class="muted">/ 从理解开始</span></span><div class="top-actions"><button type="button" class="search-trigger" aria-haspopup="dialog">搜索题目、函数或关键词 <kbd>⌘ / Ctrl K</kbd></button><label class="language"><span class="sr-only">对照阅读方式</span><select id="language" title="只切换中英对照区域；核心中文讲解始终可读"><option value="both">中英对照</option><option value="zh">中文重点</option><option value="en">英文原题</option></select></label><button type="button" class="print-button" data-print>打印</button></div></header><div class="reading-layout"><main id="main" tabindex="-1">{body}</main>{toc}</div><footer>INFS 7903 / A2 CODE REVIEW <span>原题 · 原代码 · 证据 · 理解</span><a href="{p}pages/materials.html">资料来源与已知限制 ↗</a></footer></div><dialog id="search-dialog" aria-labelledby="search-title"><div class="dialog-head"><h2 id="search-title">找到一个知识点</h2><button type="button" data-close aria-label="关闭搜索">✕</button></div><label class="sr-only" for="search-input">搜索内容</label><input id="search-input" type="search" placeholder="试试：3.2、ROW_NUMBER、死锁、NULL…" autocomplete="off"><p class="muted" id="search-status" aria-live="polite">输入题号、函数或中英文关键词。</p><div id="search-results"></div></dialog><dialog id="image-dialog" aria-labelledby="image-title"><div class="dialog-head"><strong id="image-title">原始证据</strong><div><button type="button" data-image-size>原尺寸 / 适应</button><a id="image-original" target="_blank" rel="noopener">单独打开 ↗</a><button type="button" data-close aria-label="关闭图片">✕</button></div></div><div class="image-viewport"><img id="zoom-image" alt=""></div><p id="image-caption"></p></dialog><dialog id="copy-dialog" aria-labelledby="copy-title"><div class="dialog-head"><h2 id="copy-title">手动复制代码</h2><button type="button" data-close aria-label="关闭复制">✕</button></div><p>已选中完整原代码，请按 Command+C（Mac）或 Ctrl+C（Windows）。</p><textarea spellcheck="false" aria-label="待复制代码"></textarea></dialog><div id="toast" role="status" aria-live="polite"></div><noscript><style>@media(max-width:800px){{.sidebar{{position:relative;left:0;visibility:visible;width:100%;max-height:360px;overflow:auto;box-shadow:none}}.sidebar-inner{{overflow:visible}}.menu-button{{display:none}}}}body{{padding-bottom:65px}}</style><div class="no-js">JavaScript未开启：全部教材、原图链接、SQL/PDF下载与导航仍可阅读；搜索、自动复制和进度记录不可用。</div></noscript></body></html>'''

def section(id,title,content):return f'<section class="lesson-section" id="{id}"><div class="section-heading"><span>{dict((x[0],x[1]) for x in SECTIONS).get(id,"LEARN")}</span><h2>{title}</h2></div>{content}</section>'
def termcard(term,prefix='',full=True):
    d=term
    body=f'<p class="term-syntax"><code>{E(d["syntax"])}</code></p>'+para(d['meaning'])
    if full:body+=f'<dl><dt>本作业中的作用</dt><dd>{E(d["role"])}</dd><dt>输入与输出示例</dt><dd>{E(d["example"])}</dd><dt>边界与常见错误</dt><dd>{E(d["edge"])}</dd></dl>'
    return f'<article class="term-card" id="term-{d["key"]}">{badge(d["kind"])}<h3>{E(d["name"])}</h3>{body}<div class="related">相关题目：'+ ' · '.join(f'<a href="{prefix}{path(q)}">Q{q}</a>' for q in d['questions'])+'</div></article>'

def figure(fig,prefix='../',cross=False):
    n=FIGURE_NOTES[fig['id']];src=prefix+fig['image']
    return f'''<figure class="evidence-figure" id="fig-{fig['id']}"><div class="figure-heading">{badge(n['kind'],'evidence-kind')}<span>{fig['id']} · 答案报告 p{fig['page']}</span></div><a class="zoomable" href="{src}" data-image data-caption="{E(n['title'])} · {E(n['kind'])} · 答案报告 p{fig['page']}" aria-label="放大：{E(n['title'])}"><img src="{src}" alt="{E(n['title'])}" width="{fig['width']}" height="{fig['height']}" loading="lazy"></a><figcaption><h3>{E(n['title'])}</h3><p>{E(n['note'])}</p><p class="evidence-limit"><strong>能证明什么 / 限制：</strong>{E(n['limit'])}</p><div class="source-links"><a href="{prefix}materials/report-native.pdf#page={fig['page']}" target="_blank" rel="noopener">答案报告原页 ↗</a><a href="{prefix}assets/images/report/page-{fig['page']:02}.jpg" data-image data-caption="答案报告p{fig['page']}完整页面">看完整页面</a><a href="{src}" target="_blank" rel="noopener">原图 {fig['width']} × {fig['height']} ↗</a>{f'<a href="{prefix}pages/{path(n["q"])}#evidence">回到 Q{n["q"]}</a>' if cross else ''}</div></figcaption></figure>'''

def timeline(kind):
    if kind=='race':
        rows=[['1','BEGIN；最新Return，可用','—','T1第一次检查只读，不预留'],['2','保持事务打开','BEGIN；同车仍Return','T1未提交并不阻止T2检查'],['3','仍打开','写member2未来Reserve；COMMIT','新预约对后续命令可见'],['4','member1尝试Collect；触发器报错','已提交','T1后续命令看到Reserve'],['5','COMMIT→ROLLBACK；核对事件','—','只留下本次Reserve，Collect未提交']]
        return '<div class="callout">记录轮次时间线 · VEH-0004 · 默认 READ COMMITTED</div>'+table(['步骤','T1 / LEFT','T2 / RIGHT','含义'],rows)
    return '''<div class="wait-graph" role="img" aria-label="检测前的等待环：T1持0401等待T2的0501，T2持0501等待T1的0401"><div><strong>T1 / LEFT</strong><span>PID 8668 · 持有 VEH-0401</span></div><p>等待 VEH-0501 →<br><b>循环等待</b><br>← 等待 VEH-0401</p><div><strong>T2 / RIGHT</strong><span>PID 40916 · 持有 VEH-0501</span></div></div>'''+table(['阶段','T1 / LEFT','T2 / RIGHT'],[['各持一行','0401 +10 →149110，未提交','0501 +20 →122170，未提交'],['请求第二行','等待0501，保留0401锁','请求0401，形成环'],['检测后','等待解除；0501 +10 →122160','本轮被中止；先前+20撤销'],['结束','COMMIT；最终149110 / 122160','COMMIT实际输出ROLLBACK']])

def question(q,depth=1,complete=False):
    d=LESSONS[q];o=ORIGINALS[q];p='../'*depth; safe=q.replace('.','-');idx=IDS.index(q)
    top=f'<article class="lesson" data-question="{q}" id="lesson-{safe}"><div class="eyebrow">QUESTION {q} <span>/ {"原始SQL + 证据" if q in LINES else "分析与解释题"}</span></div><h1>Q{q}<span>{E(d["title"])}</span></h1><div class="lesson-meta">{badge("原题 PDF p"+"–".join(map(str,[o['pages'][0],o['pages'][-1]])) if len(o['pages'])>1 else "原题 PDF p"+str(o['page']))}{badge(str(len(LINES.get(q,[])))+' 行原代码' if q in LINES else '无独立 SQL · 必须理解')}{badge('10 个学习步骤')}</div><p class="lede">先看懂题目在要求什么，再跟随数据、代码和真实证据，练习用自己的话解释。</p>'
    if not complete:top+='<nav class="part-nav" aria-label="本题学习步骤">'+''.join(f'<a href="#{id}">{n} {zh}</a>' for id,n,zh in SECTIONS)+'</nav>'
    orig='<div class="source-label">作业要求 PDF · a2-2026-v1.pdf · '+E(o['heading'])+'</div><blockquote class="original-text english" lang="en">'+para(o['context'])+para(o['text'])+'</blockquote><div class="source-links"><a href="'+p+f'materials/assignment.pdf#page={o["page"]}" target="_blank" rel="noopener">打开作业要求 PDF p{o["page"]} ↗</a>' + ''.join(f'<a href="{p}assets/images/assignment/page-{i:02}.jpg" data-image data-caption="作业要求 PDF p{i} · 原页（含代码/图示/表格）">原页图 p{i}</a>' for i in o['pages'])+f'<a href="{p}pages/materials.html#common">公共背景与提交要求</a></div><p class="fine">英文只合并PDF版式换行；提示、给定代码、分值均保留。原页图是版式及图示核对依据。答案报告是另一份文件，见第08节。</p>'
    if q.startswith('4.'):
        orig+=f'<div class="callout">本题依赖PDF p7公共事务背景：<a href="{p}pages/foundations.html#q4-background">完整英文与忠实中文对照</a>。初学时先读该段，再理解每条语句的新快照。</div>'
    top+=section('original','英文原题 · Original task',orig)
    ctx=next((v for k,v in CONTEXT.items() if q.startswith(k+'.')),'')
    translation=(para(ctx,'translation') if ctx else '')+para(d['translation'],'translation')+'<p class="fine">以上为原题对照翻译；下一节开始为本站补充教学解释。给定SQL的对象名和字面值不翻译。</p>'
    top+=section('translation','中文对照翻译',translation)
    deliver='完整SQL、相关输出/计划截图，以及报告中的解释。' if q in LINES else '报告中的文字、推理；等待图题还需图。本小问没有单独SQL文件。'
    top+=section('task','这道题究竟要我做什么',para(d['task'])+table(['核对项','本题要求'],[['输入 / 已有条件', 'FleetDB初始化脚本，以及前序题创建的对象；按题号顺序学习和实验。'],['交付内容',deliver],['原题限制与分值',o['heading']+'；具体小问分值以第01节英文原文为准。'],['学习建议（非新增评分项）','能够解释为什么这样写、结果怎样支持题意、改变关键条件会怎样。']]))
    top+=section('background','前置知识与数据库背景',para(GROUP_PREREQ[q[0]])+f'<p>先补基础：<a href="{p}pages/foundations.html#schema">五张表与全部字段</a> · <a href="{p}pages/foundations.html#logical">SQL逻辑顺序</a> · <a href="{p}pages/foundations.html#trigger">原始触发器逐段读</a></p>')
    if q in LINES:
        file='49079984_A2_'+q+'.sql';sql=(ROOT/'materials/sql'/file).read_text(encoding='utf-8-sig')
        top+=section('code','完整原始 SQL',f'<p>来源：A2 根目录 / {file}。完整保留原逻辑、注释、空行和语句顺序。下方行号按可下载文件的物理行计算。</p>'+codeblock(sql,q,'原始代码 · '+file,p+'materials/sql/'+file))
        linehtml=''.join(f'<li id="ex-{safe}-{x["number"]}"><div class="line-ex-head"><a href="#q-{safe}-L{x["number"]}">L{x["number"]}</a><code>{highlight(x["code"]) or "（空行）"}</code></div><p>{E(x["zh"])}</p><p class="english line-en" lang="en">{E(x["en"])}</p></li>' for x in LINES[q])
        top+=section('lines','先读整体，再逐行理解',para(d['derive'][0])+f'<ol class="line-explanations">{linehtml}</ol>')
    else:
        refs={'2.2.3':['2.2.1','2.2.4'],'4.1.4':['4.1.1','4.1.2','4.1.3'],'4.2.2':['4.2.1'],'4.2.3':['4.2.1']}[q]
        top+=section('code','本题没有独立 SQL 文件',para('原题PDF p9明确列出本小问只需解释。为核对分析，完整关联代码在：')+'<div class="source-links">'+''.join(f'<a href="{p}pages/{path(r)}#code">Q{r} 原始代码</a>' for r in refs)+'</div>')
        top+=section('lines','把解释落实到代码步骤',para(d['derive'])+('<div class="timeline">'+timeline('race' if q.startswith('4.1') else 'deadlock')+'</div>' if q.startswith('4.') else ''))
    relevant=[t for t in TERMS if q in t['questions']]
    top+=section('terms','特殊函数、语法与符号','<p>先区分函数、关键字、运算符和语句；下面的输入输出例子均是教学示例，未在网页连接数据库执行。</p><div class="term-list">'+''.join(termcard(t,p+'pages/').replace('id="term-','id="q-'+safe+'-term-') for t in relevant)+f'</div><p><a href="{p}pages/glossary.html">查看全部 {len(TERMS)} 个函数与术语 →</a></p>')
    ev=para(d['evidence'],'evidence-summary')
    if q=='3.2':ev+=table(['计划','会话设置','扫描方式','cost','估计 / 实际行数','Planning ms','Execution ms','Buffers'],SCAN_ROWS)
    if q.startswith('4.1'):
        ev+=timeline('race')
        ev+='<p class="fine">原生截图含用于防错窗口的psql交互辅助命令（\\if、\\endif、\\r、\\echo）；根SQL已整理为连接标签清单，两者并非逐字相同的回显。截图中的Return事件193434、Reserve196446及历史Collect193396需按时间区分；失败插入不在最终记录中。</p>'
    if q.startswith('4.2'):
        ev+=timeline('deadlock')
        if q in ('4.2.1','4.2.2'):
            raw=SOURCE_PAGES['report'][43]['text'].split('错误:',1)[1].split('Technical references',1)[0].strip()
            ev+='<h3>完整死锁诊断 · 原报告p44的已有转录</h3><pre class="raw-report">'+E('错误: '+raw)+'</pre><p class="fine">以原生错误图核对诊断文字与空格。ShareLock on transaction表示等待冲突行版本的事务结束；元组(2,129)是内部物理位置，不是vehicle_id或永久业务编号。</p>'
    chosen=[f for f in FIGURES if FIGURE_NOTES[f['id']]['q']==q]
    if not chosen:
        parent='4.2.1' if q.startswith('4.2') else '4.1.3' if q=='4.1.4' else '1.3.2' if q=='1.3.1' else '2.2.2'
        ev+=f'<p class="callout">本小问复用关联证据，未制造新实验：<a href="{p}pages/{path(parent)}#evidence">Q{parent} 截图与记录</a>。解释题的论据来自结构、代码和前面操作结果。</p>'
    ev+=''.join(figure(f,p) for f in chosen)
    # Raw report text and original source pages remain available for every selected page.
    ev+='<details class="source-detail"><summary>核对原答案报告文字与页码（与作业要求PDF区分）</summary>'
    for i in d['pages']:
        item=SOURCE_PAGES['report'][i-1]
        ev+=f'<h3>答案报告 p{i}</h3><div class="source-links"><a href="{p}materials/report-native.pdf#page={i}" target="_blank" rel="noopener">PDF原页</a><a href="{p}{item["image"]}" data-image data-caption="答案报告p{i}">原页图</a></div><pre class="raw-report" lang="en">{E(item["text"])}</pre>'
    ev+='</details>'
    logs=[x for x in MATERIALS if x['path'].startswith('materials/logs/') and (Path(x['path']).stem==q or Path(x['path']).stem.startswith(q+'_'))]
    if logs:ev+='<details class="source-detail"><summary>另一个轮次的文本日志（保留独立来源）</summary><p>以下来自completed或Study归档，数值可能与本页主报告不同，不作同一次实验拼接。</p>'+''.join(f'<p><a href="{p+x["path"]}" target="_blank" rel="noopener">{E(x["source"])} ↗</a></p>' for x in logs)+'</details>'
    top+=section('evidence','截图、计划与执行结果',ev)
    examples=''
    if q in EXAMPLES:
        examples='<div class="callout">以下小表全部为教学数据，用来推导中间结果；不是课程数据库实测输出。</div>'+''.join('<h3>'+E(title)+'</h3>'+table(headers,rows) for title,headers,rows in EXAMPLES[q])
    derive=para(d['derive'])+examples+'<div class="reason-chain"><span>题目条件</span>→<span>表与关系</span>→<span>代码步骤</span>→<span>可见证据</span>→<span>有边界的结论</span></div>'+f'<div class="correction"><strong>原答案核对 / 常见误区 / 边界</strong>{para(d["pitfall"])}</div>'
    if q in SUGGESTIONS:
        label,sql=SUGGESTIONS[q];derive+=codeblock(sql,'suggestion-'+q,label)
    top+=section('derive','从要求推到结论',derive)
    speech='我对题目的理解是：'+d['task']+' 实现时，'+d['derive'][0]+' 从证据看，'+d['evidence']+' 我还会说明这个边界：'+d['pitfall']
    practice='<div class="key-points"><h3>核心知识点</h3>'+para(' · '.join(t['name'] for t in relevant[:5]))+'</div><h3>检查理解</h3><p>'+E(d['quiz'][0])+'</p><details class="quiz-answer"><summary>展开参考答案</summary>'+para(d['quiz'][1])+'</details><p>再练一次：选一行代码说明输入、处理、输出；找一张截图说明它能证明什么、还不能证明什么。</p><h3>向老师讲解的练习稿</h3>'+para(speech,'speech')+'<p class="fine">练习稿为学习辅助，先理解再用自己的表达说明；其中数字均保留其来源轮次。</p>'
    extra_q,extra_a=EXTRA_QUIZZES[q]
    practice=practice.replace('<p>再练一次：','<h3>再检查一个关键点</h3>'+para(extra_q)+'<details class="quiz-answer"><summary>展开参考答案</summary>'+para(extra_a)+'</details><p>再练一次：')
    top+=section('practice','自测与口头讲解',practice)
    top+=f'<label class="completion"><input type="checkbox" data-complete="{q}"><span>我已能独立解释 Q{q} 的题意、代码与证据</span></label>'
    if not complete:
        top+='<nav class="prev-next" aria-label="前后题目">'+(f'<a href="{path(IDS[idx-1])}"><small>← 上一题</small><strong>Q{IDS[idx-1]} {E(LESSONS[IDS[idx-1]]["title"])}</strong></a>' if idx else '<a href="foundations.html"><small>← 回到基础</small><strong>读懂FleetDB</strong></a>')+(f'<a href="{path(IDS[idx+1])}"><small>下一题 →</small><strong>Q{IDS[idx+1]} {E(LESSONS[IDS[idx+1]]["title"])}</strong></a>' if idx+1<len(IDS) else '<a href="../index.html"><small>完成一轮 →</small><strong>回到学习路线</strong></a>')+'</nav>'
    return top+'</article>'

def foundations():
    fields={
     'station_id':'站点文本主键，唯一非空；车辆以此引用站点。','station_name':'站名非空，但未声明唯一；同名站点需由ID区分。','suburb':'城区名称，NOT NULL不保证拼写在某清单内。','bays':'整数车位数；未声明正数CHECK。',
     'model_code':'车型文本主键；VEHICLES.model_code外键引用它。','make':'品牌/制造商，非空、可重复。','model_name':'车型名称，不同于实体车或主键。','body_type':'车身类别如SUV、Sedan，是Q1分区单位，不是每个model_code。','seats':'整数座位数；没有额外正数CHECK。','replacement_value':'整数重置价值，不是Return/Incident收费。',
     'vehicle_id':'一辆实体车的文本主键；事件和行锁实验用它定位。','in_service':'DATE投入使用日期，不是当前可用状态。','odometer':'非空整数里程；Q4.2修改的是车辆这行。',
     'member_id':'SERIAL主键；默认序列供号，回滚不保证回收序号。','member_name':'姓名非空、可同名，不能只凭姓名分组。','email':'非空且完整值唯一，自动有唯一索引；不保证合法邮箱格式。','joined':'DATE加入日期；收费窗口用event_time，不用joined。','plan':'会员方案文本，没有枚举CHECK限制。','sponsor_id':'可空的MEMBERS自引用外键；NULL是自付根，多层可存在，外键不防环。',
     'event_id':'SERIAL事件主键；同event_time时按更大ID取最新。','event_type':'非空事件类型文本；给定数据有Reserve/Collect/Return/Cancel/Incident，未用CHECK枚举。','event_time':'无时区TIMESTAMP，记录事件时间；简化状态取最大时间，所以未来Reserve也排前。','amount':'NUMERIC(8,2)精确十进制，6位整数2位小数，可NULL；Return票价与Incident损坏费用。'}
    setup=(ROOT/'materials/setup.sql').read_text(encoding='utf-8')
    schema=setup[setup.index('CREATE TABLE STATIONS'):setup.index('--- Data')].strip()
    trigger=setup[setup.index('CREATE OR REPLACE FUNCTION'):setup.index('\nCOMMIT;',setup.index('CREATE OR REPLACE FUNCTION'))].strip()
    s='<div class="eyebrow">00 / START FROM ZERO</div><h1>先读懂数据库<span>再读懂你的 A2</span></h1><p class="lede">把数据库当成有明确规则、可以关联和计算的表格系统。从一行数据开始，不要求你预先懂SQL。</p>'
    s+=section('start','一行、一列、一张表',para(['表（table）是一类事物的集合；行（row）是一件具体记录；列（column）是记录的属性。VEHICLES一行是一辆实体车，MODELS一行是一种规格，BOOKING_EVENTS一行是一次事件。不要把“一辆车”和“一次取车”当同一计数单位。','教学例：VEHICLES(V1,MD1,S1)、MODELS(MD1,Sedan)、STATIONS(S1,南站)。一条事件(V1,Collect)只有车辆ID，经两次关联才知道它属于Sedan、南站。这些简化数据只用于教学，不是课程真实输出。'])+table(['BOOKING_EVENTS 教学行','vehicle_id','event_type','amount'],[['E1','V1','Collect','NULL'],['E2','V1','Return','20.00'],['E3','V1','Collect','NULL']])+para('V1只有一辆，但有两次Collect。主键（primary key）像唯一编号，唯一且非空；外键（foreign key）像有检查的引用，保证目标ID存在。它不自动表示业务合理或数据无环。'))
    s+=section('schema','五张表、全部字段与关系','<div class="schema-graph"><span>STATIONS</span>←<span>VEHICLES</span>→<span>MODELS</span><br><span>VEHICLES</span>←<span>BOOKING_EVENTS</span>→<span>MEMBERS ↻ sponsor_id</span></div><p>箭头表示当前表外键指向被引用表。一个车型/站点可以有多辆车，一个会员/车辆可以有多次事件；MEMBERS.sponsor_id又指向同表member_id。</p>'+codeblock(schema,'schema','原始 setup.sql · CREATE TABLE 段','../materials/setup.sql'))
    for match in re.finditer(r'CREATE TABLE (\w+) \((.*?)\);',schema,re.S):
        name,body=match.groups();rows=[]
        for line in body.splitlines():
            line=line.strip().rstrip(',')
            if not line:continue
            key=line.split()[0];desc=fields[key]
            if key=='member_id' and name=='BOOKING_EVENTS':desc='非空外键→MEMBERS.member_id，是事件责任会员，非最终根账号。'
            if key=='vehicle_id' and name=='BOOKING_EVENTS':desc='非空外键→VEHICLES.vehicle_id；Q3以IS NULL辨识外连接未匹配。'
            if key=='model_code' and name=='VEHICLES':desc='非空外键→MODELS主键；外键本身不自动给引用列建立查询索引。'
            if key=='station_id' and name=='VEHICLES':desc='非空外键→STATIONS主键，是车辆记录的所属站点；事件未存历史取车位置。'
            rows.append([key,line,desc])
        s+='<h3>'+name+'</h3>'+table(['字段','原始定义','实际含义与边界'],rows)
    s+=section('logical','第一条SELECT：书写顺序与逻辑顺序',codeblock("SELECT vehicle_id, event_type\nFROM BOOKING_EVENTS\nWHERE event_type = 'Collect'\nORDER BY event_time DESC, event_id DESC\nLIMIT 3;",'first-select')+para(['书写先SELECT输出列，再FROM数据来源、WHERE条件、ORDER BY顺序、LIMIT数量。理解时先问从哪张表读→哪些行留下→取哪些列→怎样排序→留几行。该例取最新三个Collect事件，而不是取每辆车最新事件，二者不同。','复杂查询的逻辑阶段为FROM/JOIN→WHERE→GROUP BY/聚合→HAVING→窗口→SELECT→ORDER BY→LIMIT。HAVING是补充知识，当前原答案未使用。优化器可重排物理工作，在不改变语义前提下选择hash、bitmap、并行等；不能把逻辑顺序当实际节点顺序。','单引号\'Collect\'是文字；e.vehicle_id中的e是别名、点号取列；AS给结果起名；分号结束SQL；--直到行末为注释；圆括号可能是函数参数、子查询或CTE。NULL是未知/缺失，不能写= NULL，应写IS NULL。']))
    s+=section('plan','执行计划先读哪几件事',para(['从叶扫描向父节点追踪行如何变化：扫描哪些表、条件留几行、连接是否放大、聚合成几组、最终输出多少。再看cost预测、actual实测、loops、buffers及最终Planning/Execution。','cost的startup..total是相对成本单位；actual time单位ms；rows有估计/实际两套。loops>1时节点actual rows通常为每轮平均。父节点含子树工作，不要把所有节点时间或buffers相加当总计。','shared hit表示共享缓冲命中；read表示读进共享缓冲，仍可能命中OS缓存。Sort Method/quicksort与Memory、Hash Batches等帮助判断是否溢盘。一次时间差不能证明某写法永远更快。'])+f'<p><a href="{path("3.2")}">用六个真实计划练习 → Q3.2</a></p>')
    s+=section('trigger','已有BI_COLLECT：先懂规则，再懂报错',para('以下代码逐字来自setup.sql末尾，不是新写的作业答案。FOR EACH ROW让每个插入候选行先运行函数；NEW表示候选行。仅Collect进入检查，读取该车最大event_time、同时间最大event_id的事件。')+codeblock(trigger,'trigger','原始 setup.sql · UDF_BI_COLLECT / BI_COLLECT 段','../materials/setup.sql'))
    s+=table(['原始语句/段','逐段解释'],[
      ['CREATE OR REPLACE FUNCTION ... RETURNS TRIGGER AS $$','定义返回trigger的PL/pgSQL函数。$$包住函数正文，正文内的单引号无需为外层SQL反复转义。替换函数定义，不是立刻执行一次Collect。'],
      ['DECLARE last_type VARCHAR; last_member INTEGER;','声明局部变量保存上一事件类型和会员；它们不是永久表列。'],['BEGIN / END','函数代码块；不启动另一笔数据库事务。'],["IF NEW.event_type = 'Collect' THEN",'只对拟插入Collect检查，Reserve/Incident等跳过此分支，最后仍RETURN NEW。'],
      ['SELECT E.event_type, E.member_id INTO last_type,last_member','把最近一行的两个值依次存局部变量；这里INTO是PL/pgSQL赋值，不是创建表。'],['FROM ... WHERE E.vehicle_id = NEW.vehicle_id','只看这辆候选车已有事件，不混入其他车辆。'],['ORDER BY E.event_time DESC,E.event_id DESC LIMIT 1','按时间最新优先，ID打破同时间并列，取一行；未来预约也可能最大。'],
      ["IF last_type='Incident' / ELSIF ...='Collect'",'事故待修或已经租出均抛异常拒绝Collect。'],["ELSIF last_type='Reserve' AND last_member <> NEW.member_id",'同会员预约允许、其他会员预约拒绝。<>为不等，AND要求两条件都真。'],['RAISE EXCEPTION ... %','异常模板%按顺序替换车辆/会员值。异常会让当前事务失败，除非通过异常处理或保存点恢复。'],['END IF; / RETURN NEW;','关闭分支；没有拒绝则把候选行交回INSERT继续。没有历史事件时SELECT INTO变量为NULL，相等判断不为true，当前函数会放行。'],['$$ LANGUAGE plpgsql;','函数正文结束，声明解释语言。'],['CREATE OR REPLACE TRIGGER ... BEFORE INSERT ... FOR EACH ROW','将函数绑定到BOOKING_EVENTS每行插入之前；EXECUTE FUNCTION指定要调用的函数，不是每次调用都新建它。']])
    s+=table(['上一事件','含义','新Collect'],[['Return / Cancel','可用','允许'],['Reserve，同会员','为你保留','允许'],['Reserve，其他会员','为别人保留','拒绝'],['Collect','已租出','拒绝'],['Incident','待修','拒绝']])
    s+=section('sessions','两个连接：可见性与等待',para(['连接是独立服务器会话，可用pg_backend_pid核对。BEGIN后改动在提交前属于该事务；COMMIT成功才提交。错误后事务可能进入失败状态，COMMIT结果实际ROLLBACK。SAVEPOINT仅建恢复点，原Q4未ROLLBACK TO。','READ COMMITTED每条命令取新快照；快照是已提交内容的一致视图，不是车的预留锁。普通SELECT仍拿兼容ACCESS SHARE表锁，与另一会话插入不冲突。UPDATE对冲突行加锁持有到事务结束。','一个等待者仍可能等到对方提交；两者各持对方所需的锁形成有向环才是死锁。数据库会中止某受害事务，受害者先前修改也撤销。'])+timeline('deadlock'))
    bg=ORIGINALS['_q4_background']
    s+=section('q4-background','Q4公共背景 · 完整中英对照','<div class="source-label">作业要求PDF p7 · Q4 Transactions (9 marks total)</div><blockquote class="original-text english" lang="en">'+para(bg['text'])+'</blockquote><div class="source-links"><a href="../materials/assignment.pdf#page=7" target="_blank" rel="noopener">作业要求p7</a><a href="../assets/images/assignment/page-07.jpg" data-image data-caption="作业要求p7完整原页">原页图</a></div>'+para([
      '在PostgreSQL中，用BEGIN和COMMIT包围一组SQL命令来建立事务。例如银行事务先BEGIN，再执行UPDATE accounts SET balance = balance - 100.00 WHERE name = \'Alice\';，可含更多语句，最后COMMIT。原文给出PostgreSQL事务教程链接。本题考察两个事务并发时会怎样。',
      '背景：PostgreSQL如何读取。你已学过两种使并发调度可串行化的方法：两阶段锁等加锁协议，以及时间戳排序。PostgreSQL的普通读取并不采用上述两者之一，所以接下来的观察不能直接从它们推导。本节提供必要背景，不要求你已学过。',
      'PostgreSQL查询读取一个快照（snapshot），即数据库的一致图像，包含在快照取得之前已提交的那些变化，而不是通过取得读锁读取。原题接着说：因为读取不加锁，读者不会阻塞写者，写者也不会阻塞读者。',
      '在PostgreSQL默认隔离级别READ COMMITTED下，每条语句开始时都会取得新快照。因此，同一事务的两条语句可能读到不同数据：另一事务可能在两者之间已经提交。',
      '处理本题时记住两个推论：触发器在引发它的事务中运行，其发出的查询由该事务当前快照回答；它没有特殊或特权视角。快照不是锁：读取一行不会记录或预留任何东西，不能阻止另一事务改变你刚读到的内容。'
    ],'translation')+'<div class="correction"><strong>补充解释，与忠实翻译分开</strong><p>上面保留了原题“读取不加锁”的教学简化。普通SELECT仍拿ACCESS SHARE表锁，但不因此取得预留车辆的冲突行锁；某些DDL表锁仍可能与读取相互阻塞。快照的完整规则还包括可见的自身修改，不能将原题简化描述理解为忽略自己的写入。</p></div>')
    s+=section('setup','阅读与实验要分清',para(['本网站从不连接数据库、不运行SQL；交互只是教学状态演示。打开网站无需安装PostgreSQL。要做真实实验，使用课程测试环境和psql，原setup.sql会DROP并重建assignment2；它用于初始化测试库，不应为恢复窗口反复运行。','按PDF p9–10的20脚本顺序依赖前题对象，脚本不重复初始化。Q4需两个独立连接人工交错。psql反斜杠命令不能直接粘贴进pgAdmin SQL编辑器。'])+codeblock('\\i a2-2026-fleetdb.sql\n\\conninfo\nSHOW transaction_isolation;','setup-commands','课程初始化命令示意 · 网页不会执行')+'<p>第一行执行本地文件，第二行检查连接信息，第三行只读取隔离设置。看到DONE! All data has been inserted.才表示初始化脚本执行到结束。</p>')
    return s+'<div class="actions"><a class="button primary" href="'+path('1.1.1')+'">开始 Q1.1.1 →</a><a class="button" href="materials.html">核对资料来源</a></div>'

def home():
    s='''<div class="eyebrow">INFS 7903 / ASSIGNMENT 02</div><section class="hero"><div><div class="hero-note"><i></i> 一份可以慢慢读懂的代码学习手册</div><h1>不止看懂答案。<br>读懂<span class="accent">为什么。</span></h1><p class="hero-en" lang="en">From the question to the code.<br>From the evidence to understanding.</p><p class="hero-copy">从零补齐数据库基础，按原题读英文、拆 SQL、看计划和截图。把每一步变成你能向老师解释的知识。</p><div class="actions"><a class="button primary" href="pages/foundations.html">从零开始学习 <span>↗</span></a><a class="button" data-resume href="pages/q1-1-1.html">继续阅读 →</a></div></div><div class="hero-notebook" aria-label="学习过程示意"><div class="notebook-top"><span>YOUR A2 / READ · REASON · EXPLAIN</span><span>● ● ●</span></div><p class="mini-label">01 / 先问：这一行处理谁？</p><pre><span class="sql-keyword">SELECT</span> body_type, station_name,
       collections
<span class="sql-keyword">FROM</span> ranked_stations
<span class="sql-keyword">WHERE</span> rn = <span class="sql-number">1</span>;</pre><div class="notebook-annotation"><span>rn = 1</span><p>每个车身类别，<br>只留下一个获胜站点。</p></div><div class="mini-flow"><span>原题</span>→<span>代码</span>→<span>证据</span>→<strong>理解</strong></div><small>教学阅读示意 · 非数据库执行结果</small></div></section><div class="stat-row"><div><b>24</b><span>完整学习单元</span></div><div><b>395</b><span>原始 SQL 逐行讲解</span></div><div><b>53</b><span>报告嵌图逐张解读</span></div><div><b>10</b><span>每题固定学习步骤</span></div></div>'''
    s+='<div class="section-title"><div><p class="eyebrow">YOUR LEARNING PATH</p><h2>沿着问题，一步一步学。</h2></div><a href="complete.html">连续阅读全部内容 ↗</a></div><a class="foundation-card" href="pages/foundations.html"><span>00 / BEFORE YOU START</span><h3>先认识五张表，再打开第一道题。</h3><p>表与字段 · 主外键 · NULL · 逻辑顺序 · 触发器 · 两个连接</p><b>从零开始 →</b></a><div class="module-grid">'
    descriptions={'1':'从分组到每组第一，沿赞助链找到最终付款人，再比较现算与保存结果。','2':'为什么建了索引也不用？用选择率、列覆盖和heap页解释规划器的选择。','3':'两种SQL如何成为同一个反连接？逐格比较两条查询的六份扫描计划。','4':'跟随两个会话的时间线，分清快照、业务拒绝、锁等待与死锁。'}
    for g,zh,en in GROUPS:
        qs=[q for q in IDS if q[0]==g]
        s+=f'<a class="module-card" href="pages/{path(qs[0])}"><span class="module-number">0{g} <span>↗</span></span><h3>{zh}</h3><p class="module-en">{en}</p><p>{descriptions[g]}</p><div>{len(qs)} 个单元 <span>Q{qs[0]} — Q{qs[-1]}</span></div></a>'
    s+='</div><section class="how-to"><div><p class="eyebrow">HOW TO USE THIS BOOK</p><h2>把“看过”变成“能解释”。</h2><p>每题先看题意与推导，再按行号回到代码，最后让截图回答“它证明了什么”。</p></div><ol><li><span>01</span><div><b>读原题与中文对照</b><p>保留条件、限制和原题页码。</p></div></li><li><span>02</span><div><b>用小数据推导，再拆代码</b><p>教学例与真实实验结果明确分开。</p></div></li><li><span>03</span><div><b>核对图、计划和结论</b><p>不同轮次的数字不混用。</p></div></li><li><span>04</span><div><b>合上答案，练习口头说明</b><p>解释得清楚，再记录为已掌握。</p></div></li></ol></section>'
    s+='<section class="version-note"><div><span class="status-dot"></span> 已核对原题、当前代码与资料版本</div><p>原题以12页作业要求PDF为准；主要答案证据选用45页原生截图更新报告。Q4采用VEH-0004完整轮次和RIGHT死锁受害轮次。早期重放单独标注，未冒充当前结果。</p><a href="pages/materials.html">查看版本选择、覆盖说明和全部下载 →</a></section><p class="fine">学习进度'+ '<strong data-progress-count>0 / 24</strong> · <button class="text-button" type="button" data-reset-progress>清除学习记录</button> · 浏览器存储不可用时仍可完整阅读。</p>'
    return s

def sources():
    s='<div class="eyebrow">SOURCES / PROVENANCE</div><h1>每一处解释，都能找到来处。</h1><p class="lede">作业要求PDF定义题目；答案报告记录已做实验；SQL是当前原始文件；本站文字是对照翻译、教学解释与明确标注的建议。</p>'
    downloads=[('assignment.pdf','作业要求 · 12页','原题、schema、提示、分值、20脚本清单'),('report-native.pdf','主要答案报告 · 45页','原生图、补充重放、Q3.2六图、Q4完整轮次'),('report-native.docx','主要答案 Word','检查嵌入媒体与报告文字'),('report-root.pdf','根目录答案报告 · 33页','保留原版对照'),('report-root.docx','根目录答案 Word','保留原内容'),('report-supplemented.pdf','补齐版报告 · 47页','完整重放的其他版本'),('report-completed.pdf','completed报告 · 36页','另一轮独立实验，Q4结果不同'),('setup.sql','FleetDB初始化脚本 v1.0','保留表、数据、触发器与初始化命令')]
    s+='<div class="download-grid">'+''.join(f'<a href="../materials/{file}" download><span>↓</span><strong>{title}</strong><small>{desc}</small></a>' for file,title,desc in downloads)+'</div>'
    s+=section('versions','版本选择：看内容和证据，不按修改时间',table(['来源','采用方式','原因 / 影响'],[['作业要求a2-2026-v1.pdf','题号、英文、页码与覆盖基准','PDF内部Assignment Version1.0，文件名v1；不自行改成新版本。'],['A2根20份SQL','完整代码主线','根SQL.zip逐文件hash一致；395物理行重新对齐。'],['原生截图更新版45页PDF','主要答案证据','53嵌图；保留原生截断和独立重放说明；原生Q4更完整。'],['补齐版47页PDF','下载保留，供版本比较','较多重放输出；不是当前所有原生实验的同次结果。'],['completed36页PDF与日志','单独归档','Q4采用VEH-0001、另一死锁受害者；不能混配根代码。'],['Study旧专项与逐行解释','核对后复用概念、排版和原题提取','旧SQL265行；当前395行，Q4有实质变化，重新写行号与讲解。']])+para('SHA-256清单见data/materials.json与data/audit-versions.json；报告详细审计见下方链接。所有导入文件均复制到此项目，无需原A2或Study文件夹运行。'))
    s+=section('corrections','原内容保留；问题与建议另外说明',table(['核对问题','原内容/版本','本站处理'],[['死锁受害会话不同','completed/旧Study：T1失败，T2+20；原生：RIGHT/T2失败','主线按原生最终149110/122160；旧149120/122170仅在独立下载中。'],['D2强制bitmap不一定更慢','原生D2 22.959ms < D1 24.116ms','保留实测，说明成本更高不等于单次时间必更长。'],['Q1.3计划截断/不同阶段','原生长条件截断，原生30276条，早期重放30275条','两套计划分别标明；不给出受控倍速比。'],['原题“普通读无锁”的简化','PDF p7背景措辞','补充普通SELECT兼容ACCESS SHARE表锁；没有预留车辆的冲突行锁。'],['赞助环/零次类别/邮箱格式','约束没有防环或邮箱格式CHECK','逐题注明边界；不伪造课程数据有这些错误。'],['固定实验车辆与SAVEPOINT','根Q4固定VEH-0004，建立保存点但未恢复','说明重跑可能无可用结果；异常后仍按整事务ROLLBACK。'],['图片可读性','原生长过滤右端截断，小结果裁图像素少','保留原图和报告页；缺字不猜，重放仅补充语义结构。']]))
    s+=section('common','公共要求、完整原页与提交范围',para(['原题PDF p1–3给出FleetDB业务、全部表、触发器规则与初始化方式；p7给出事务快照背景；p9列20份SQL，四道解释题不单交SQL；p10要求按题号在新初始化库通过psql的\\i重现，Q4人工切换连接。','原题p10说明报告应含全部回答、所需SQL及执行输出截图；普通结果超过20行可展示前10末10，不跨行拆元组，计划须完整。明确评分为功能/理解/解释28分与展示2分。本站额外自测、口头稿、学习检查点是学习建议，不是新增评分项。','本地保留完整原题，以下12页可直接阅读。原图含ER图、表格、代码和评分清单，未用文字提取猜测图示。'])+'<div class="source-page-grid">'+''.join(f'<a href="../{page["image"]}" data-image data-caption="作业要求 PDF p{page["page"]}"><img src="../{page["image"]}" alt="作业要求原页p{page["page"]}" loading="lazy"><span>作业要求 p{page["page"]}</span></a>' for page in SOURCE_PAGES['assignment'])+'</div><details class="source-detail"><summary>完整公共背景英文原文（PDF p1–3、7、9–12）</summary>'+''.join('<h3>作业要求PDF p'+str(i)+'</h3><pre class="raw-report english">'+E(SOURCE_PAGES['assignment'][i-1]['text'])+'</pre>' for i in [1,2,3,7,9,10,11,12])+'</details>')
    s+=section('coverage','24个单元的对应清单',coverage_table('../')+'<div class="source-links"><a href="../reports/coverage.md">内容覆盖表</a><a href="../reports/source-audit.md">版本审计</a><a href="../reports/study-reuse.md">Study复用记录</a><a href="../reports/checks.md">检查记录与环境</a><a href="../data/materials.json">文件SHA清单</a></div>')
    s+=section('sql-downloads','20份原始SQL下载','<div class="file-list">'+''.join(f'<a href="../materials/sql/49079984_A2_{q}.sql" download><b>Q{q}</b>49079984_A2_{q}.sql <span>{len(LINES[q])}行 ↓</span></a>' for q in LINES)+'</div>')
    native=[x for x in MATERIALS if x['path'].startswith('assets/images/native/') and x['path'].endswith('.png')]
    notes=[x for x in MATERIALS if x['path'].startswith('materials/notes/')]
    s+=section('additional','独立截图与原始说明版本索引',para('这些原生截图多与报告嵌图重复，保留用于核对原文件。Q4.1早期VEH-0001/0002/0003轮次含粘贴语法错误或错窗口，不作为完整并发主线；notes是按时间追加的原记录，早段“后续待补充”须结合其后完整VEH-0004段阅读。')+'<details class="source-detail"><summary>展开独立原生截图文件列表</summary><div class="file-list">'+''.join(f'<a href="../{x["path"]}" data-image data-caption="独立原始截图：{E(Path(x["path"]).name)}">{E(Path(x["path"]).name)}</a>' for x in native)+'</div></details><div class="source-links">'+''.join(f'<a href="../{x["path"]}">{E(Path(x["path"]).name)}</a>' for x in notes)+'</div>')
    s+=section('limits','来源与已知限制',para(['本站未重新连接或运行数据库实验。所有“实际输出”均来源于用户已有报告、截图或日志；小数据与交互均明确为教学示例。缺失的独立创建截图、截断条件和裁图像素限制在对应题注明。','所有资料均保留原来源，不擅自为课程PDF、数据、第三方材料指定开源许可证。用户已确认公开仓库并发布GitHub Pages，任何人可访问本站。','本轮实际浏览器与路径检查结果记录在reports/checks.md。未在真实Mac Safari上运行，不宣称已实测。中文/英文/代码采用系统字体栈，无外部字体或CDN依赖。'])+'<p>概念核对使用 <a href="https://www.postgresql.org/docs/17/using-explain.html" target="_blank" rel="noopener">PostgreSQL 17 EXPLAIN</a>、<a href="https://www.postgresql.org/docs/17/transaction-iso.html" target="_blank" rel="noopener">事务隔离</a>、<a href="https://www.postgresql.org/docs/17/runtime-config-query.html" target="_blank" rel="noopener">规划开关</a>。文档版本随原题Q3.2链接选择；不据此推断本机数据库服务器版本。发布说明核对 <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site">GitHub Pages 官方文档</a>（2026-10-29）。</p>')
    return s

def coverage_table(prefix):
    return '<div class="table-wrap"><table><thead><tr><th>题号 / 网站</th><th>原题PDF</th><th>主答案报告</th><th>SQL</th><th>截图/日志</th></tr></thead><tbody>'+''.join(f'<tr><td><a href="{prefix}pages/{path(q)}">Q{q} {E(d["title"])}</a></td><td>p{",".join(map(str,ORIGINALS[q]["pages"]))}</td><td>原生版p{",".join(map(str,d["pages"]))}</td><td>{str(len(LINES[q]))+"行" if q in LINES else "解释题"}</td><td>'+(', '.join(f['id'] for f in FIGURES if FIGURE_NOTES[f['id']]['q']==q) or '复用关联题证据')+'</td></tr>' for q,d in LESSONS.items())+'</tbody></table></div>'

def write(rel,html):
    dst=ROOT/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(html,encoding='utf-8')

def main():
    write('index.html',shell('学习路线',home()))
    write('pages/foundations.html',shell('从零开始',foundations(),'pages/foundations.html',1))
    for q in IDS:
        toc='<aside class="page-toc"><span>本题 / ON THIS PAGE</span>'+''.join(f'<a href="#{id}">{n} {zh}</a>' for id,n,zh in SECTIONS)+'</aside>'
        write('pages/'+path(q),shell('Q'+q+' '+LESSONS[q]['title'],question(q),'pages/'+path(q),1,toc))
    gloss='<div class="eyebrow">REFERENCE / '+str(len(TERMS))+' KNOWLEDGE CARDS</div><h1>遇见术语，随时回来查。</h1><p class="lede">分类、语法、输入输出、当前代码作用、教学小例子与边界条件，放在同一处。这里的例子均非真实数据库执行。</p><nav class="term-index" aria-label="术语索引">'+''.join(f'<a href="#term-{t["key"]}">{E(t["name"].split(" · ")[0])}</a>' for t in TERMS)+'</nav><div class="glossary-grid">'+''.join(termcard(t) for t in TERMS)+'</div>'
    write('pages/glossary.html',shell('术语与函数',gloss,'pages/glossary.html',1))
    evidence='<div class="eyebrow">EVIDENCE / 53 FIGURES</div><h1>从截图，读到有根据的结论。</h1><p class="lede">全部53个报告嵌图逐张保留原分辨率。点击放大，再切换原尺寸；每张图标明报告页码、操作、读法和证据边界。</p><div class="evidence-filters" role="group" aria-label="筛选截图"><button type="button" data-filter="all" aria-pressed="true">全部 53</button>'+''.join(f'<button type="button" data-filter="{g}" aria-pressed="false">Q{g} {zh}</button>' for g,zh,en in GROUPS)+'</div><div class="evidence-index">'+''.join('<div data-figure-group="'+FIGURE_NOTES[f['id']]['q'][0]+'">'+figure(f,'../',True)+'</div>' for f in FIGURES)+'</div>'
    write('pages/evidence.html',shell('截图与结果',evidence,'pages/evidence.html',1))
    write('pages/materials.html',shell('原始资料与版本',sources(),'pages/materials.html',1))
    # Section IDs are namespaced in the book, including hrefs, to keep every anchor unique.
    complete='<div class="book-intro"><div class="eyebrow">FULL BOOK / PRINT EDITION</div><h1>完整连续阅读</h1><p>本页包含从零基础教材、全部24题、原代码逐行讲解和证据。使用浏览器打印可保存PDF。原尺寸截图可从链接单独查看，纸张缩小后文字可能较小。</p><div class="actions"><button class="button primary" type="button" data-print>打印 / 保存 PDF</button><a class="button" href="index.html">返回学习路线</a></div></div>'
    def root_link(m):
        attr,url=m.groups();u=urlsplit(url)
        if u.scheme or url.startswith('#'):return m[0]
        return attr+'="'+urlunsplit(('', '', posixpath.normpath(posixpath.join('pages',u.path)),u.query,u.fragment))+'"'
    complete+='<article class="book-foundations">'+re.sub(r'(href|src)="([^"]+)"',root_link,foundations())+'</article>'
    for q in IDS:
        fragment=question(q,0,True);safe=q.replace('.','-')
        for id,n,zh in SECTIONS:
            fragment=fragment.replace('id="'+id+'"','id="'+safe+'-'+id+'"').replace('href="#'+id+'"','href="#'+safe+'-'+id+'"')
        # Same source figure can appear once only in the full book; our per-question ownership is unique.
        complete+=fragment
    write('complete.html',shell('完整连续阅读',complete,'complete.html'))
    search=[{'title':'Q'+q+' '+d['title'],'url':'pages/'+path(q),'tag':'题目 / '+str(len(LINES.get(q,[])))+'行','text':' '.join([d['title'],d['task'],ORIGINALS[q]['text'],*d['translation'],*d['derive'],d['evidence'],d['pitfall']])} for q,d in LESSONS.items()]
    search += [{'title':t['name'],'url':'pages/glossary.html#term-'+t['key'],'tag':t['kind'],'text':' '.join(str(t[k]) for k in ['syntax','meaning','role','example','edge'])} for t in TERMS]
    search += [{'title':'从零开始：五张表、主外键与触发器','url':'pages/foundations.html','tag':'基础','text':'数据库 表 字段 primary key foreign key 主键 外键 schema 触发器 BI_COLLECT NULL 关系 最新事件'}]
    write('data/search-index.js','window.A2_SEARCH='+json.dumps(search,ensure_ascii=False).replace('<','\\u003c')+';\n')
    write('data/lessons.json',json.dumps(LESSONS,ensure_ascii=False,indent=2))
    write('data/terms.json',json.dumps(TERMS,ensure_ascii=False,indent=2))
    report='# 内容覆盖与资料对应清单\n\n生成日期：2026-10-29（Australia/Brisbane）。24单元全部包含十节固定结构；20SQL共395物理行。\n\n|题号|原题PDF页|主答案报告页|SQL|截图/日志|网站位置|\n|---|---|---|---|---|---|\n'
    for q,d in LESSONS.items():
        figures=', '.join(f['id'] for f in FIGURES if FIGURE_NOTES[f['id']]['q']==q) or '复用关联题证据（页面明确链接）'
        report+='|Q'+q+'|'+','.join(map(str,ORIGINALS[q]['pages']))+'|'+','.join(map(str,d['pages']))+'|'+('49079984_A2_'+q+'.sql' if q in LINES else '原题明确为解释题')+'|'+figures+'|pages/'+path(q)+'|\n'
    report+='\n## 实际资料缺口与限制\n\n- Q1.3.1主报告p7提供定义，独立创建成功消息图不足；后续成功查询物化关系为间接证据。\n- Q1.3.2原生两处长过滤条件右端截断，早期完整重放分开保留，未伪装成同次执行。\n- Q1.1.2原始结果截图未完整露出六行，主报告文字列出六组，保留该限制。\n- Q3.1原生结果只显示前10末10及总数75，中间55行未显示；另轮EXCEPT校验不冒充本轮证明。\n- 原生死锁错误在报告p44完整转录，截图与转录均可核对。\n- 本轮没有重新执行数据库；所有教学小数据和建议代码均标注未执行。\n- Mac Safari未在真实设备实测；实际环境见checks.md。\n'
    write('reports/coverage.md',report)
    print('Built 30 HTML pages; 24 lessons; 395 SQL lines; 53 report figures; '+str(len(TERMS))+' glossary cards.')
if __name__=='__main__':main()

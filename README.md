# A2 Code Review 学习手册

## GitHub仓库与打开网页

仓库：[49079986/a2-code-review](https://github.com/49079986/a2-code-review)。当前为私有仓库，需要登录49079986账号或获得仓库访问权限。

在GitHub点击 **Code → Download ZIP**，解压后打开项目内的 **index.html**。Mac和Windows都可使用；在GitHub直接点击index.html显示的是源代码，下载后才是本地网页。也可以按下文使用本地HTTP预览。

在线公开网页需另启用GitHub Pages；在获得公开发布选择前，本项目保持私有。

独立、离线可读的 INFS7903 Assignment 2 学习网站。参考原 Study 的深色阅读界面，按原题编号覆盖全部24个学习单元，包括4道没有独立SQL的解释题。每题包含英文原题、忠实中文对照、题意、前置知识、原始代码、逐行分析、函数/语法、截图证据、推导、自测与讲解练习稿。

项目含20份原始SQL的395物理行讲解、53个主要答案报告嵌图的逐张解读、38张术语卡，以及可连续阅读/打印的完整版本。教学例子与建议代码均标注未执行；网站不连接数据库。

## 首页与本地阅读

直接双击 **index.html**。这是纯HTML/CSS/JavaScript网站，阅读无需安装依赖，无CDN、在线字体或构建工具。核心文字已经写在HTML中，不依赖fetch加载，所以双击、离线和禁用JavaScript仍能阅读与下载。搜索、图片弹窗、复制、进度等增强功能需要JavaScript。

需要搬到Mac或另一台电脑时，可复制整个项目，或解压已提供的 **A2-code-review.zip**。压缩包包含完整339个项目文件，排除了中间提取文本、浏览器检查副本、缓存和运行环境；解压后从A2-code-review/index.html进入。

Windows：在资源管理器打开项目文件夹，双击index.html，用Edge或Chrome打开。Mac：把**整个文件夹**复制到Mac，在Finder双击index.html，用Safari或Chrome打开。不能只复制首页一个文件。

如需要HTTP预览（例如避免浏览器对file://的存储/剪贴板限制），已有Python时在项目根运行：

Windows PowerShell：

```powershell
Set-Location '你的路径\A2-code review'
python -m http.server 8000 --bind 127.0.0.1
```

Mac终端：

```sh
cd '/你的路径/A2-code review'
python3 -m http.server 8000 --bind 127.0.0.1
```

浏览器打开 http://127.0.0.1:8000/ ，关闭预览时在终端按Ctrl+C。Python只用于可选预览/生成，不是网站阅读依赖。

## 阅读功能

- 侧栏按原题编号导航，窄窗口用“目录”按钮打开；宽屏题内导航显示当前阅读位置。
- 顶栏搜索题号、函数与中英文关键词；Command+K / Ctrl+K打开，Esc关闭，向下键进入结果。
- 中英对照/中文重点/英文原题切换只作用于对照阅读区域；核心教学解释仍以中文为主，并非整站专业英文译本。
- 原SQL带真实物理行号、语法高亮、行号定位、完整复制与下载。自动复制失败后提供可选中全文的手动复制窗口，Mac按Command+C、Windows按Ctrl+C。
- 点击截图放大，切换“原尺寸/适应”，触控板可横向/纵向滚动，Esc返回。来源PDF和原页图始终有直接链接。
- 勾选每题掌握后记进度；仅保存在当前浏览器，换浏览器或清理网站数据会失去进度。存储不可用不影响阅读。
- complete.html含基础教材与24题连续教材。使用顶栏或页面“打印/保存PDF”；纸张上的长计划会缩小，细节可单开原图。浏览器原始证据转录默认不打印，以免重复；核心解释、原题、代码、逐行注释、截图和自测答案会打印。

## 目录

```text
index.html                 首页与学习路线
complete.html              24题连续阅读与打印
pages/                     基础、24题、术语、截图索引、资料页
assets/css/site.css        本地响应式/打印样式
assets/js/app.js           本地搜索、复制、进度、放大等增强
assets/images/             12页原题图、45页答案图、报告嵌图、原生截图
materials/                 必要原题PDF、四版报告PDF、两份Word、setup、20SQL、日志
data/                      原题、逐行、来源hash、截图映射、搜索索引等
scripts/                   教学内容与生成/检查程序
reports/                   版本审计、内容覆盖、结构检查、浏览器验证记录
.nojekyll                  GitHub Pages直接按静态文件发布
.gitignore                 排除缓存、数据库运行目录、凭据和临时文件
```

## 资料来源与版本选择

原始资料来自用户提供的A2与Study文件夹，原文件保留。本网站只复制必要资料，不复制数据库内部数据目录、运行时或虚拟环境。

1. 原题以a2-2026-v1.pdf（12页，内部版本1.0）确定范围；网站存为materials/assignment.pdf。
2. 原始代码采用A2根目录20份SQL，和根SQL.zip逐个hash一致。Study旧归档为265行，当前395行，重新对齐，未套用旧行号。
3. 主要答案采用“原生截图更新版”45页报告，存为report-native.pdf。它保留原生图和较早完整重放的区分。
4. 根33页、补齐47页、completed36页PDF分别存档；不只凭修改时间认定正确版本。
5. Q4采用完整VEH-0004轮次；原生死锁为RIGHT/T2受害、LEFT/T1提交，最终149110/122160。completed旧轮次的相反受害者及+20结果不混用。
6. 原生Q3.2 D2=22.959ms低于D1=24.116ms，已修正旧“强制bitmap必然更慢”讲法；成本预测与单次耗时分开解释。

详见reports/source-audit.md、reports/study-reuse.md、reports/coverage.md、data/materials.json（SHA-256与来源相对路径）。课程PDF、原SQL及第三方材料**没有被擅自指定开源许可证**。项目已建立独立GitHub仓库，公开网页是否发布以仓库当前状态和用户选择为准。

## 如何修改与重新生成

阅读网站不需要生成。已提交的HTML和所有资源即可部署。需要改教材时，用Python 3.10+：

```sh
python scripts/build.py
python scripts/verify.py
```

Mac将python改为python3即可。build.py和verify.py仅使用Python标准库，完全从项目内资料生成，不依赖A2/Study原文件夹。

重新生成干净交付包：`python scripts/package.py`。它会更新A2-code-review.zip并执行ZIP的CRC检查，记录文件数与SHA到reports/delivery.json；不会删除本地中间工作。

- 题意、忠实翻译、推导、证据摘要、自测：scripts/lesson_content.py。
- 38个函数/术语的分类、语法、输入输出、例子、边界：scripts/glossary.py。
- 53个嵌图的每图说明：scripts/figure_notes.py。
- 完整原题与页码：data/original-tasks.json，须核对原PDF。
- 原SQL：materials/sql/。修改教学讲解用data/current-lines.json；**若要改原答案，另存建议代码，不覆盖原SQL**。
- 添加题目需同时补齐LESSONS、ORIGINALS、来源映射、行号注释和证据；build.py当前断言24题/20SQL/395行用于防漏，改变范围须更新断言和覆盖表。

prepare_materials.py与extract_sources.py是本次一次性导入工具，读取父目录A2/Study，只在重新导入源资料时使用，非运行/普通生成依赖；需要额外安装PyMuPDF和python-docx（extract_sources）。普通读者无需安装。导入工具会更新项目内副本，执行前应保留自己修改的教材数据；不修改原A2/Study。

## Git提交步骤（手动执行）

在网站项目根目录运行：

```sh
git init
git add .
git status
git commit -m "Add complete A2 code review learning website"
git branch -M main
```

在GitHub手动创建一个空仓库（例如a2-code-review），再把下面YOUR-NAME替换为自己的账号：

```sh
git remote add origin https://github.com/YOUR-NAME/a2-code-review.git
git push -u origin main
```

已有origin时先用git remote -v核对，不重复添加。未配置姓名邮箱时按Git提示设置自己的信息，本项目没有写入虚构身份。无需提交数据库运行目录、临时截图检查目录或压缩包。单个文件均小于100MB。

## GitHub Pages部署步骤

1. 先推送含index.html的main分支。
2. 仓库Settings → Pages → Build and deployment → Source选择 **Deploy from a branch**。
3. Branch选择 **main**，Folder选 **/ (root)**，保存。
4. 等GitHub完成Pages部署，打开其返回的网站地址，通常为https://YOUR-NAME.github.io/a2-code-review/ 。
5. 全部站内资源使用相对路径，没有写死域名或根路径；可放在仓库子路径。.nojekyll使它直接作为静态站点发布，无需npm install或Actions构建。

更新教材后重新运行build.py/verify.py，git add、commit、push即可触发更新。以仓库当前Pages设置与GitHub实际提示为准。[官方发布来源说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 已知限制与实际验证

- 本次没有重新运行PostgreSQL实验，数字来自已有实际记录；不同轮次并未拼接成受控性能测量。
- 原生普通视图长过滤条件两处截断，补充早期完整重放；原始六行结果图有可见范围限制；Q3.1首末结果裁图有原生像素限制。逐题如实标明。
- 浏览器file://行为存在差异，复制与存储均提供降级，原图和文件直接链接始终可用。
- **未在真实Mac Safari设备实测**，也未公开部署到GitHub Pages。实际浏览器、宽度、路径迁移与检查结果见reports/checks.md。

阅读入口：[index.html](index.html) · 连续教材：[complete.html](complete.html) · 覆盖表：[reports/coverage.md](reports/coverage.md)。

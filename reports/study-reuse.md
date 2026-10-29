# Study 内容复用核对

核对日期：2026-10-29（Australia/Brisbane）。只读检查 Study 与 A2 原目录，本报告及 current-lines.json 写入独立新项目。

## 可复用的来源与范围

| 来源 | 已核对内容 | 复用条件 |
|---|---|---|
| Study/source/a2-special/original-tasks.json | 24 个小问及 `_q4_background`，包含 heading/context/text/page/pages | 全部 context 和 text 都逐段存在于 A2/a2-2026-v1.pdf 的规范化提取文本；可复用原文，但页图需保留版式和给定代码 |
| Study/assignments/a2/input/a2-2026-v1.pdf | 12 页原题 PDF | SHA256 与 A2 根目录原题 PDF 完全相同 |
| Study/source/a2-special/line-explanations.json | 20 份 SQL、265 物理行的 number/code/zh/en | 与 Study/assignments/a2/sql 逐行一致，与 A2 根目录 395 行不一致；不能直接套用旧行号 |
| Study/source/a2-study-notes.json | chinese_explanations、script_parts、evidence | 可作为旧版本解释与证据索引，但含旧版实测数字、VEH-0001 与旧死锁受害者 |
| Study/review/a2.html | 完整 24 小问讲义，含解释题 | 可按题号提取 `.a2-part`，重新核对和明确来源版本 |
| Study/specials/a2/preparation.html | 五表基础、触发器、术语、初始化说明 | 可复用教学逻辑，必须核对 A2 初始化 SQL 的真实结构 |
| Study/specials/a2/q1.html 至 q4.html | 按单元归并的原文、旧 SQL、逐行和实验证据 | 不宜原样复制，解答默认折叠和旧版证据不满足新站要求 |
| Study/assignments/a2/evidence/*.txt | 每题计划、结果、会话记录及独立验证 | 对应归档实验，有 manifest.json SHA256；先与 A2 相同文件核对，再作为旧版证据保留 |
| Study/assets/studio.css | 主要屏幕样式 | 可参考色彩、字体、双语层级及目录布局；独立新站需重新限制正文宽度和窄窗布局 |

## 精确提取方式

使用 BeautifulSoup 的 `soup.find(id="A2-" + qid)` 获取一题，或 CSS `[id="A2-1.1.2"]`。ID 中有点号，不能直接用 `#A2-1.1.2`，否则点号会被当成 class 分隔。

每题结构为 `.a2-part-head`、`.original-question`、`.task-translation-label`、题意 `.pair`、外层 `details` 内 `.answer-body`、`.mastery-control`。`.answer-body` 中含中文/英文解释 `.pair`、原始 `.code-block`、`.line-guide-panel`、`.part-links`、`.evidence-details`。优先提取直接子 `.pair` 作为旧说明，避免把逐行面板中的 `.pair` 重复提取。四个无 SQL 的题 2.2.3、4.1.4、4.2.2、4.2.3 也有 `.answer-body`，不能仅依 SQL 文件生成题目列表。

旧 `.line-guide-panel`、代码、链接相对路径和证据版本须重新构建。旧页面核心解答在默认收起的 details 内，新站应默认展示核心教学，补充证据可折叠。

## 发现的实质版本差异

1. 根目录 Q4.1.1 使用 `DISTINCT ON (vehicle_id)` 和 `VEH-0004`，旧 Study 使用 `CROSS JOIN LATERAL` 和 `VEH-0001`。两个查询均先找最新事件后判 Return，但操作车辆和物理语法不同，逐行说明不能共用。
2. 根目录 Q4.1.1 加了 `SAVEPOINT collect_attempt`，Q4.1.3 没有 `ROLLBACK TO`。保存点并未恢复 Collect 异常后的事务，`COMMIT` 仍结束为回滚；不能把保存点存在误写为已恢复事务。
3. 根 Q4.1.2 含 psql 的 `\connect assignment2`、`\set`、`\pset`、`\timing` 和 `RETURNING`；GUI 查询工具通常不能直接执行反斜杠元命令。重连必须只在连接2进行，重连连接1会丢失原事务。
4. 根 Q4.2.1 的注释记录连接2为死锁受害者，连接1幸存，条件推导应为两车均只提交 +10；Study Q4.2.2 的旧实测说明是连接1受害、连接2提交 +20，旧最终里程为149120/122170。受害者本来就可能变化，两个版本分别可以成立，但绝不能混成一组证据。
5. 根 Q3.2 将 EXPLAIN 与 SELECT 分行，并显式给 C1/D1/C2/D2/C3/D3 标签，共六个计划；Study 有相同实验思想但旧行数和耗时，不能把归档耗时标为本轮重新执行。
6. 其他大量变化为排版展开、注释、psql证据辅助命令。判断差异需按 SQL 语义和证据，不以文件日期单独选择版本。

## 旧教学内容本身的限制

- `.task-translation-label` 后的中文多数是题意摘要，未完整翻译原文全部提示、限制和评分条目；新站仍需忠实逐段翻译。
- 4.1.4 的旧英文辅助段落多次重复同一句概括，并非每段中文的完整对照，不应拿来当逐段翻译。
- 相同代码文字在不同上下文中不能共用同一条说明。例如 `AND e.event_type = 'Collect'` 在 NOT EXISTS 内属于 WHERE，在 LEFT JOIN 中属于 ON。旧逐行 JSON 对某些重复行沿用了 ON 说法，新 current-lines.json 已按出现位置纠正。
- 旧内容的具体耗时、行数、受害事务、车号必须保留版本标签；教学实验明确标为模拟，不能充当真实执行。
- Q4 原题的“不加锁”及描述 Q4.1 阻塞的语言是教学简化；普通 SELECT 仍有兼容 ACCESS SHARE 表锁，观察到触发器业务异常不等于锁等待或死锁。

## 视觉与学习方式参考

Study 主背景 `#0a0a0a`、正文 `#f3f3f3`、次文字 `#a1a1a1`、边线 `#282828`、强调色 `#ff8833`。界面字体使用 Inter/Apple/Segoe UI/PingFang SC/Microsoft YaHei，代码使用 SFMono-Regular/Menlo/Monaco/Consolas。正文约15px、行距1.85，双语英文较小较灰并配左侧细线。顶部 sticky 工具栏、左侧约232px目录、右侧 minmax(0,1fr) 正文，代码横向滚动，窄窗会改为单列。新站宜延续这些视觉关系，而非复制其他课程全部导航。

## 本次新增逐行数据

`data/current-lines.json` 含20份A2根目录SQL的全部395物理行，结构 `{qid: [{number, code, zh, en}]}`。已逐题验证 `code` 序列与根 SQL 的 UTF-8-sig `splitlines()` 完全一致，`number` 从1连续递增。Q4共128行全部重新按当前代码解释；其他部分精确复用后补充拆分语义、注释、空行、EXPLAIN上下文，并移除容易被误认为本轮实测的旧数字。

新逐行数据不运行 SQL；实际结果需结合各版本原始报告、截图及日志。此次研究未实际连接数据库，也未生成新实验结果。

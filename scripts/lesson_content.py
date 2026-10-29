"""Editorial teaching layer. Numbers refer to explicitly named recorded runs."""
CONTEXT = {
 '1.1': '合作社的规划人员希望知道，各类车实际最常在哪个站点被取走，以决定在哪里增加停车位。',
 '2.2': '合作社希望了解会员使用哪些电子邮件服务商，以调查新闻简报被部分服务商拒收的原因。服务商域名是邮箱中 @ 之后的部分。会员填写的大小写不一致，因此域名必须按不区分大小写的方式比较：Bigpond.com 与 bigpond.com 是同一个服务商。',
 '3.1': '车队中有些车辆从未真正被会员驾驶过：它们可能是新车，也可能只有预约后取消的记录。',
 '4.1': '两名会员同时争取同一辆车。会话1的会员在停车站准备开走，先检查可用，再记录 Collect；会话2的会员在网站检查同车可用，记录三天后的 Reserve 并提交，此时会话1仍然打开。需要并排打开两个 psql 连接，均使用默认隔离级别。可以使用 now() 提供时间戳。须包含两个连接的截图。',
 '4.2': 'Q4.1 中两个事务的业务意图不能同时满足，但只涉及一方受阻。死锁（deadlock）是对称的情况：两事务各持有对方等待的资源，因此双方都不能前进。单独看每个事务都没有做错，陷阱来自执行交错。两名员工维修后修正相同两辆车的里程，操作顺序恰好相反。'
}

# title, faithful translation, plain-language task, derivation, recorded evidence,
# misconception/correction, self-test question, reference answer, report pages
LESSONS = {}
def add(k,title,translation,task,derive,evidence,pitfall,q,a,pages):
    LESSONS[k]=dict(title=title,translation=translation,task=task,derive=derive,evidence=evidence,pitfall=pitfall,quiz=[q,a],pages=pages)

add('1.1.1','每种车身类别最繁忙的站点',
 ['（1）创建视图 V_BUSIEST_BAYS：对于每种车身类别（body type），报告该类别车辆取车次数最多的单个站点。视图应显示车身类别、站点名称和取车次数，并按取车次数从多到少排序。（1分）','提示：这是“每个组内找第一名”的问题。考虑使用带 PARTITION BY 子句的 RANK() 或 ROW_NUMBER() 窗口函数，并使用公共表表达式（Common Table Expressions，CTE），按有意义的语义步骤组织查询。'],
 '输入是事件、车辆、车型和站点四张表；输出是一个名为 V_BUSIEST_BAYS 的普通视图。每个出现过取车的 body_type 只留一个获胜站点，不是每种车型 model_code 一行，也不是找全车队唯一最忙站点。报告放代码与创建消息，后续小问展示结果和计划。',
 ['先从 BOOKING_EVENTS 中找 Collect。一次取车是一条事件；同一辆车取走十次就贡献十次，而不是 COUNT(DISTINCT vehicle_id)。经 e.vehicle_id=v.vehicle_id 得到车辆，经 v.model_code=m.model_code 得到 body_type，经 v.station_id=s.station_id 得到站名。目标主键唯一，所以这些连接不会把一条事件随意放大。','第一层 CTE 按 body_type、station_id、station_name 分组得到 collections。第二层对每个 body_type 单独按次数降序编号；station_id 打破并列。外层 WHERE rn=1 挑冠军，再对各类别冠军排序。窗口结果在 WHERE 之后产生，因此需要外层过滤；直接在同层 WHERE 写 ROW_NUMBER() 不成立。','教学示例：Sedan 在 S1 的三条 Collect 和 S2 的两条 Collect 汇总成 (Sedan,S1,3)、(Sedan,S2,2)；SUV 在 S2 有四条，成为 (SUV,S2,4)。编号后保留 Sedan/S1/3 与 SUV/S2/4，最终 SUV 在前。若改用 RANK 且只按次数排序，两个并列冠军可能同时留下，不再是 single station。'],
 '主报告 p2 的创建截图支持“对象创建成功”。完整六行结果和实际执行计划在 Q1.1.2；创建成功本身不证明排名逻辑正确。原始事件没有记录取车地点，这个解答使用 VEHICLES 的所属站点，不能推断历史站点迁移。',
 '缺少 Collect 的类别不会进入当前 INNER JOIN/计数结果；这是原解答的边界。若要求连零次类别也出现，需要另行约定零次冠军，原题没有提供该约定。普通视图读取若严格要求顺序，调用方也应写 ORDER BY。',
 '为什么 station_id 既出现在 GROUP BY 又出现在窗口排序中？',
 '分组时区分同名站点；排序时为相同次数提供稳定的胜出规则。它不会改变“先比较取车次数”的主目标。',[2])

add('1.1.2','从六行结果读到完整执行树',
 ['（2）查询视图（SELECT * FROM V_BUSIEST_BAYS;）并报告结果。报告并解释查询计划（query plan）。说明应参考报告出的时间、成本、取回行数、查询规划知识，以及你认为相关的其他因素。（0.5分）'],
 '提交 SELECT 的结果截图、完整 EXPLAIN 计划及解释。只说“查出了六行”不够：要说明数据库怎样从事件日志加工出六个冠军，以及估计值和实测值是否一致。',
 ['代码第一条 SELECT 展示普通结果；第二条 EXPLAIN (ANALYZE, BUFFERS) 再真实执行一次查询并显示计划。两次执行不是同一计时样本。书写从 SELECT 开始，但逻辑先 FROM/JOIN、WHERE、GROUP BY，再做窗口和外层过滤；物理计划又可能用并行扫描、hash 连接等实现这些逻辑。','原生计划的底层 Parallel Seq Scan 筛 Collect，经过 Hash Join 补属性，部分聚合再 Finalize GroupAggregate 汇成279组，Incremental Sort 与 WindowAgg 完成分区排名，最上面排序输出6行。读树先从最深缩进的输入向父节点追踪，不能把每层时间相加当作总时间。','原生计划 actual rows=29769.5、loops=2 意味着该节点每次循环的平均输出，合计59539条；并行节点的时间和行数要结合 loops 和 worker 信息读。顶层估计2行、实际6行是估计误差，并不是少显示4行。'],
 '主报告 p3–5：Sedan 973、SUV 838、Hatchback 794、People Mover 510、Van 384、Ute 333。原生无复合索引重测顶层 cost=4786.08..4786.08，Planning 7.797ms、Execution 52.686ms。p4 的上下两张原生图合起来覆盖68行计划。不要用 Study 旧轮次31.959ms替代此数字。',
 'cost 是规划器的相对成本单位，不是毫秒；Execution Time 才是本次测量。输出6行仍可能扫描近20万行。完整计划须读到最后的 Planning/Execution，只有顶部截图不能支持全流程解释。',
 '为什么结果只有6行，仍需要处理59539条 Collect？',
 '必须先知道每种类别、每站的取车总数，才能确定冠军。最终过滤压缩输出，却不会消除为计算冠军所需的底层工作。',[3,4,5])

add('1.2','沿赞助链找到最终付款账号',
 ['会员产生的每笔费用最终记到账户赞助链（sponsorship chain）顶端。没有赞助人的会员自行付费；有赞助人的会员将费用传给赞助人；若该赞助人也有赞助人，则继续向上传递，直到没有赞助人的账户。','创建视图 V_ACCOUNT_LIABILITY，找出对2026年1月1日至6月30日（含两端）期间费用总额承担责任最多的十个账户。显示账户 member id、member name 和应付总金额。','提示：赞助链可能超过一层，所以 COALESCE(sponsor_id, member_id) 这样的表达式会得到错误答案。考虑使用 WITH RECURSIVE CTE。'],
 '不是列出直接付费最多的十个驾驶员，而是把每个驾驶员的 Return/Incident 收费归给最终无 sponsor 的根账号，再取金额最大的十个。输入为 MEMBERS 自引用树和 BOOKING_EVENTS，输出为普通视图，报告应解释多层递归与日期范围。',
 ['根层 SELECT member_id, member_id AS account_id WHERE sponsor_id IS NULL，把根映射给自己。递归层用 child.sponsor_id=parent.member_id 找孩子，让孩子继承 parent.account_id。UNION ALL 每轮扩展一层，直到没有新孩子；这一步建立“每名会员→根账号”的映射，不是对费用反复累加。','教学数据：A(1,NULL)、B(2,1)、C(3,2)、D(4,NULL)。根轮输出1→1、4→4；下一轮2→1；再下一轮3→1。若C的Return收费80、B的Incident收费20、D收费15，映射后根1共100，根4共15。一层 COALESCE 会把C的80错算给B。','连接映射到 e.member_id，把事件连到最终根；按根ID与姓名分组 SUM(e.amount)。只选 Return/Incident，日期 >= 2026-01-01 且 < 2026-07-01，包含6月30日23:59:59，而不把上界误写成6月30日00:00。ORDER BY 金额降序、ID稳定打破并列，再 LIMIT 10。'],
 '主报告 p5–6 解释递归；原始10行结果复用于 p8/Q1.3.2。Ana Lopez（14881）6214.77居首。报告说明独立向上遍历得到同十行；这属于原报告校验陈述，网站没有重新运行数据库。',
 '外键只保证 sponsor_id 指向存在会员，不防止自环或多节点环。当前从根向下的算法会漏掉无根环成员；给定数据是森林时成立。学习建议：生产环境检测环/保证层级规则，不要声称 REFERENCES 自动保证无环。原代码SUM(e.amount)忽略NULL，某组全NULL时结果仍为NULL；并未使用COALESCE把空金额改为0。',
 '为什么不在递归每一层都把同一笔费用加给当前 sponsor？',
 '题目只要最终责任账户。先建立一名会员唯一对应一个根的映射，再汇总每条事件一次，能避免中间账号重复计费。',[5,6,8])

add('1.3.1','用同一查询保存物化结果',
 ['（1）使用与 V_ACCOUNT_LIABILITY 相同的查询，创建名为 MV_ACCOUNT_LIABILITY 的物化视图（materialised view）。（0分）'],
 '虽然本小问标0分，它仍是下一步对比必需的准备。创建语句应与普通视图使用同一递归、收费筛选和top10逻辑；不是创建另一张会自动保持同步的表。',
 ['CREATE MATERIALIZED VIEW ... AS 后复制整个账户责任查询。创建时执行查询并保存当时结果，因此当前保存的是10行冠军账户，不是24000个会员的完整中间映射。','普通视图保存“怎么算”，物化视图还保存“上次算出的行”。教学示例：原查询算得A=100、B=15，物化后保存这两行。后来A增加20，普通视图读出120，物化结果仍是100，直到刷新。'],
 '主报告 p7 展示完整物化定义；p12 的 Seq Scan 实际10行验证保存结果的读取路径。此小问没有独立的创建消息截图可单凭p7确认成功，后续成功读取是间接证据。',
 '不要把物化视图当成自动缓存失效系统；普通 INSERT 不会自动 REFRESH。重复执行同名CREATE会报对象已存在，原脚本按作业顺序在新初始化数据库执行。',
 '物化结果里为什么不是24000行？',
 'AS 查询含最终 GROUP BY、ORDER BY 和 LIMIT 10，保存的是该查询最终返回的十个根账号。',[7,12])

add('1.3.2','比较现算视图与已保存结果',
 ['（2）报告、比较并解释下面两个查询，它们分别读取普通视图和物化视图。（0.5分）','Query A: SELECT * FROM V_ACCOUNT_LIABILITY;  Query B: SELECT * FROM MV_ACCOUNT_LIABILITY;','说明应参考时间、成本、取回行数、查询规划知识及其他相关因素。'],
 '两个结果相同还要解释工作量为何不同，提供两个完整计划。将“显示哪些账户”和“读取时计算多少工作”分开。',
 ['Query A 被展开为普通查询：构建24000人的递归映射、过滤收费事件、连接、HashAggregate、top-N排序。Query B 直接扫物化关系的10行，不必重复递归和聚合；这才是潜在快的原因。','原生Query A是后来的数据库阶段，处理30276条符合条件的事件；早先重放计划为30275条。Q1.3.3会增加一条90000费用，所以不能把阶段差异当成优化器逻辑错误。','在主报告p12，Seq Scan on mv_account_liability 的 cost=0..18.50、估计850、actual10、loops1、shared hit1。850是规划估计，不是物化视图保存850行。读关系默认没有保证顺序，若展示榜单需要在调用查询再加ORDER BY。'],
 '主报告 p8–12 保留原结果、原生截图和较早重放完整计划。原生A顶层370929.67..370929.69、Planning0.384ms、Execution45.543ms；B Planning1.373ms、Execution0.236ms。A原生长过滤条件有截断，p10–11补完整重放计划，属于不同轮次；不能拼接成同一次执行或计算严格加速倍数。',
 '相同10行不代表计算路径相同；反过来，不同阶段/缓存的45.543÷0.236也不是受控性能实验。保留数字、解释结构性差别，避免宣称稳定加速若干倍。',
 '估计850行但实际10行，是否说明SELECT漏了840行？',
 '不是。估计用于规划，并非应返回行数约束。新物化关系的统计可能尚未更新，actual才是该次输出。',[8,9,10,11,12])

add('1.3.3','新增费用、陈旧榜单与刷新',
 ['（3）一名会员记录一笔大额损坏费用。运行给定 INSERT，再运行Query A与Query B，报告各自结果并解释差异；然后执行 REFRESH MATERIALIZED VIEW MV_ACCOUNT_LIABILITY;，再次运行Query B。用一至两句说明选择物化视图而非普通视图时，设计者接受了什么权衡。（0.5分）','给定INSERT向 BOOKING_EVENTS 写入：选择 sponsor_id 非空且 member_id 最大的一人，为 VEH-0001 记录2026-05-04 09:15:00的Incident，金额90000.00；ORDER BY member_id DESC LIMIT 1。完整英文与SQL以左侧原题及下面原文件为准。'],
 '按题目顺序展示：插入成功→A改变→B未刷新仍旧→刷新→B与A一致。不能只提供刷新后的同一结果；题目考查的正是未刷新的差异。',
 ['INSERT ... SELECT 从MEMBERS选一个有赞助人的账号。本数据选到24000，沿24000→22086→18148→13943把费用归给Tuan Haddad，而不是归给直接赞助人22086。事件时间落在上半年范围，因此会影响该视图。','原先Tuan是673.75，加90000得到90673.75，进入第一；原第10名397被挤出。普通视图在下一条读取时重新计算，所以立即反映；物化关系不因事件表改变而自行修改，仍保留Ana居首的旧十行。','REFRESH重新执行定义并替换已保存结果。教学例：A保存100，底表变120时A普通读120、B物化读100，刷新后B读120。刷新既有计算代价，也有并发/锁方面的取舍；原文件使用普通REFRESH，没有CONCURRENTLY。'],
 '主报告p13–15的五张图按“INSERT、Query A、旧Query B、REFRESH、刷新后Query B”阅读。它们支持陈旧与更新的可观察差异，而非证明所有业务场景下都能自动保持一致。',
 '不要重复执行INSERT来重现截图却不记录重复金额；它不是幂等操作。建议改进代码可以把测试安排在可回滚的专用实验里，但本页原脚本原样保留。',
 '如果新增费用的event_time在2026年7月2日，刷新会把它计入当前榜单吗？',
 '不会。物化刷新仍执行原定义，日期谓词排除7月1日及之后的事件；刷新并不改变查询范围。',[13,14,15])

add('2.1.1','按事件类型、时间建立复合索引',
 ['（1）在BOOKING_EVENTS的event_type、event_time字段上（按此顺序），创建名为IDX_EVENT_TYPE_TIME的索引。（0.5分）'],
 '提交CREATE INDEX和创建证据，字段顺序是题目明确限制。不是两个独立索引，也不是把时间放前面。',
 ['默认B-tree键可想成电话簿的“姓、名”：先分event_type，再在相同类型内按event_time排序。教学例：(Incident,3月1日)、(Incident,3月2日)、(Return,3月1日)。要找Incident整个3月可以定位该类型的一段连续时间区间。','索引叶项帮助定位heap中的记录；它没有自动把vehicle_id或amount变成索引返回列。创建增加存储和写入维护工作，下一题会看到它并不强迫规划器采用索引。'],
 '主报告p16创建截图与根SQL的CREATE INDEX一致；后续EXPLAIN中出现idx_event_type_time可进一步确认索引用于某些查询。未指定USING时PostgreSQL默认B-tree。',
 '“建了索引就一定快”不成立。索引仅增加访问候选路径，是否使用取决于选择率、列覆盖、页分布与成本估计。',
 '为什么 (event_time,event_type) 不能当作完全相同的答案？',
 '键排列不同，题目明确要求event_type先。类型等值、时间范围可利用按类型分区后的连续时间段，调换顺序会改变访问特点。',[16])

add('2.1.2','有索引却仍然顺序扫描',
 ['（2）重新运行Q1.1查询（SELECT * FROM V_BUSIEST_BAYS;）。报告查询计划，与Q1.1计划比较，解释差异（如有）。（1.5分）'],
 '对照建索引前后同一视图查询。没有使用新索引也可以是正确结果，重点是用计划节点和数据比例解释，而不是期待计划必须变化。',
 ['该查询只筛全部历史Collect，没有event_time范围。59539次Collect分布很广，还需vehicle_id连接车辆，复合索引没有vehicle_id，读取索引后仍需很多heap访问。顺序扫描配合并行处理可能更合算。','原生前后计划同为Parallel Seq Scan→Hash Join→聚合→窗口排名→最终Sort。两次top cost都4786.08..4786.08。输出仍6行，所以逻辑语义没有改变；节点未变却毫秒下降，不能归因于索引被使用。'],
 '主报告p16–18：原生恢复索引后Planning1.633ms、Execution40.538ms；无索引重测7.797ms/52.686ms。原生p17两图覆盖68行；该轮恢复索引的上下文必须保留。',
 '这些是独立测量，缓存变暖或系统负载都能影响时间。不要把“40.538<52.686”写成新索引使查询加速的证据。',
 '从哪个证据可以判断新索引没有被用来读取事件表？',
 '看扫描节点名称和对象：出现Parallel Seq Scan on booking_events，而没有对idx_event_type_time的Index/Bitmap Index Scan。',[16,17,18])

add('2.1.3','三月事故：高选择性的索引范围',
 ['（3）报告并解释给定查询的查询计划，该查询统计2026年3月记录的事故。解释此处规划器为何与（2）不同地使用IDX_EVENT_TYPE_TIME。（1分）','给定查询：SELECT count(*), sum(amount) FROM BOOKING_EVENTS WHERE event_type = \'Incident\' AND event_time >= TIMESTAMP \'2026-03-01\' AND event_time < TIMESTAMP \'2026-04-01\';'],
 '输出只有一行，但需要解释底层匹配的116条事故、金额总和、两列索引范围和bitmap访问。与统计全时段Collect相比，条件更有选择性。',
 ['固定第一键Incident，再把第二键限制到[3月1日,4月1日)，因此可定位很短的一段索引。Bitmap Index Scan先产生匹配行位置，Bitmap Heap Scan按页批量访问，取出amount，Aggregate再COUNT/SUM。','教学例：三月Incident金额10、NULL、20，COUNT(*)=3、SUM(amount)=30；COUNT(amount)=2。没有任何事故时COUNT(*)=0，但SUM(amount)=NULL，不能把两者混淆。当前数据返回116与86382.67。','116/196441≈0.059%，只访问79个exact heap blocks，远小于全部事件；选择率低不保证匹配数据只占很少连续页，但本轮确实比广泛Collect有利。'],
 '主报告p19明确为完整重放证据：Aggregate cost388.48..388.49，实际1行；索引估计123、实际116，Execution0.390ms、heap exact79。Study旧轮次0.292ms/估计132不能代入。',
 '输出聚合1行与底层匹配116行是两个节点的行数。索引不含amount，所以这里不是Index Only Scan。',
 '为什么不能用 event_time <= TIMESTAMP \'2026-03-31\'？',
 'TIMESTAMP只有日期时是当天00:00；这样的上界会排除3月31日白天。小于4月1日准确包含整个3月。',[18,19])

add('2.2.1','从邮箱提取域名再数人数',
 ['（1）编写识别每位会员邮箱服务商域名的表达式，并报告每个不同域名及其会员数，最受欢迎的在前。可以使用字符串处理函数，包括正则表达式函数。（1分）'],
 '只用一条SQL输出规范化域名及人数。先取@后部分、再转小写、再分组，不能先按原邮箱分组或遗漏大小写合并。',
 ['SPLIT_PART(email,\'@\',2)按分隔符@切开，字段号从1开始，取第二段；LOWER再小写化。教学例：a@Bigpond.com→Bigpond.com→bigpond.com；b@bigpond.com→同一个键，所以合计2。','GROUP BY表达式令同域名归组，COUNT(*)计成员。ORDER BY member_count DESC, provider_domain先按人数，人数相同按域名字母顺序。AS仅给输出起名，不会修改MEMBERS列。'],
 '主报告p20域名原生截图：12个域名共24000人，gmail.com=8164，exemail.com.au=248。总和24000可检查是否漏计，但不单独证明域名提取正确。',
 'email为NOT NULL UNIQUE但没有邮箱格式CHECK：无@时split_part第二段为空字符串，多@时只取第二段。原解答依赖给定数据格式；生产应用应验证邮箱，不能把唯一约束当邮箱格式验证。',
 'LOWER必须在分组前吗？',
 '分组键必须是规范化后的域名。先按原大小写分组再只在显示时LOWER，会得到多个显示相同但未合并计数的行。',[20])

add('2.2.2','读懂全体会员的域名聚合计划',
 ['（2）报告并解释（1）中查询的查询计划。应参考时间、成本、取回行数、查询规划知识及其他相关因素。（1分）'],
 '展示未建表达式索引时的完整EXPLAIN。需要明确24000输入会员与12输出域名之间的区别，并解释估计组数偏差。',
 ['Seq Scan逐行取得24000个email并计算域名；HashAggregate为每个键维护计数器；Sort只排序12个聚合组。它不是排序24000个最终结果。','教学例：三人邮件归两个域名，扫描3行→哈希表两项→计数2与1→排序两组。没有过滤条件，每个会员都必须贡献计数，完整扫描合理。','重放计划HashAggregate Batches=1，Sort quicksort Memory25kB，说明该次没有聚合/最终排序溢盘；不能仅因cost大就声称磁盘排序。'],
 '主报告p21完整重放：顶层cost2864.09..2924.09，估计24000组、实际12组，Execution6.997ms。派生表达式的有效不同值统计不足会使估计偏大；估计不改变正确输出。',
 '不要套用Study旧轮次4.736ms。统计估计与实测结果分栏阅读，判断内存是否溢出应看Batches、Disk或排序方法等真实节点。',
 '为什么顶层估计24000而实际12，不等于数据库计算了24000种邮箱服务商？',
 '估计由规划阶段统计推算；实际HashAggregate把相同规范化域名合在一起，这次只产生12组。',[21])

add('2.2.3','完整邮箱唯一索引为何不是域名索引',
 ['（3）MEMBERS.email已有UNIQUE约束，因此其上已有索引。用一至两句解释为什么该索引不能回答关于服务商域名的查询。（1分）'],
 '这是文字解释题，没有独立SQL。必须解释索引键的排序含义，不要简单说“函数让索引失效”。',
 ['教学地址：amy@x.com、bob@y.com、zoe@x.com。按完整邮箱排序时两个x.com被bob隔开，因为先比较用户名。按LOWER(SPLIT_PART(...))建立的键则是x.com、x.com、y.com。','因此完整email索引不能直接给出某域名的一段连续键，也不能直接给出规范化域名分组。数据库理论上可以全扫email索引再计算域名；这仍不是靠域名键精准定位，也没有免去全体统计。'],
 '主报告p21–22保留原答案文字；没有独立执行截图是符合此小问性质的。关联证据是初始化脚本email VARCHAR NOT NULL UNIQUE和Q2.2.2全扫描计划。',
 '原题“cannot answer”应解释为不能直接按域名键定位/完成该统计，不能扩大成“任何查询绝不可能扫描这个email索引”。',
 'UNIQUE(email) 会把 a@Bigpond.com 与 b@bigpond.com 视为同一个地址吗？',
 '不会。它约束完整email值唯一，不替代规范化域名的分组，也不是邮箱格式验证。',[21,22])

add('2.2.4','把规范化域名变成索引键',
 ['（4）创建名为IDX_MEMBER_DOMAIN的函数索引（function-based index），以便可能加快针对（1）中表达式的查询。（0.5分）'],
 '索引对象建在MEMBERS上，键是LOWER(SPLIT_PART(email,\'@\',2))的计算结果。题目说potentially，意味着不是保证每种相关查询都加速。',
 ['CREATE INDEX ... ON MEMBERS ((...)) 把表达式包为索引键。额外括号用于表达式索引语法，不是又调用一层函数。插入/修改email时需要重新计算并维护键，所以读取收益伴随写入和存储代价。','教学例：a@X.COM保存键x.com；查WHERE LOWER(SPLIT_PART(email,\'@\',2))=\'x.com\'可定位。若只写SPLIT_PART而去掉LOWER，语义不同，不能假定原索引能直接服务相同查找。'],
 '主报告p22创建截图；p24稀有域名计划出现idx_member_domain说明后续确实被采用。创建本身不改变会员数或域名大小写规则。',
 '表达式索引使用的函数须满足索引表达式所要求的不可变性等条件。LOWER/SPLIT_PART的该用法可以建立，不应泛化到NOW()等随时间变化的函数。',
 '把LOWER从查询去掉，为什么不是简单的“少算一步更快”？',
 '它会让Bigpond.com和bigpond.com不再等价，同时表达式与索引键不匹配；先保证题目要求的语义。',[22])

add('2.2.5','同一个表达式，两种完全不同的读取量',
 ['（5）在函数索引已建立的情况下，报告以下两者的查询计划：第一，（1）中编写的统计查询；第二，查询某个特定且稀有服务商的会员：SELECT member_id, member_name, email FROM MEMBERS WHERE <your expression> = \'exemail.com.au\';','解释与之前计划的差异（如有），以及索引为何对其中一种帮助大得多。说明应参考时间、成本、取回行数、查询规划知识和其他相关因素。（1.5分）','补充内容：表达式上的索引只有在查询包含相同表达式时才有帮助。因此生产系统常把派生值（如规范化域名）保存为独立列，方便直接索引、约束和查询。'],
 '同一文件需要两个EXPLAIN，不能只展示有利的稀有查找。比较全体聚合与选择性查找，不是比较“有函数”与“没有函数”。',
 ['全体计数仍需读24000人，仍Seq Scan→HashAggregate→Sort。按域名排序的键也不能预先知道哪个域名COUNT最大，因此不能直接满足ORDER BY COUNT(*) DESC。','稀有查询只需要248/24000≈1.03%。Bitmap Index Scan按exemail.com.au找到位置，Bitmap Heap Scan访问164个exact块取id、name、email；表达式索引没有覆盖这些输出列，所以还需heap。','教学例：1000人归10域名，统计仍要每人贡献；某域只有3人则可从索引直达3个位置。是否获益取决于工作量而不是函数名字。'],
 '主报告p23–24完整重放：聚合cost2864.09..2924.09、实际12组、5.274ms（索引前6.997ms）；稀有查找cost5.22..226.08、估计120实际248、0.510ms。保留单次计时，不推断稳定比例。',
 '根SQL不再有旧completed版独立打印248行的SELECT，而保留两个ANALYZE计划；ANALYZE本身执行了查询，其rows可以证明行数，但报告普通结果应按原题展示约定说明。',
 '为什么域名索引有序仍不能直接返回“人数最多在前”？',
 '索引顺序是域名字符串顺序；人数是汇总后才产生的值。必须先统计，再按COUNT排序。',[23,24])

add('3.1.1','找出从未被取走的车辆',
 ['（1）写两条不同SQL，都报告从未出现Collect事件的所有车辆的vehicle_id：（A）用NOT EXISTS；（B）不使用NOT EXISTS或NOT IN，例如使用外连接。两者必须返回相同的行。（1.5分）'],
 '起点必须是VEHICLES，以便连完全没有任何事件的新车也能出现。“从未Collect”不等于“目前最新不是Collect”，也不等于“没有任何事件”。',
 ['A对每辆v检查是否存在e.vehicle_id=v.vehicle_id且event_type=Collect的事件。子查询SELECT 1只是存在性占位，找到匹配就足够；NOT EXISTS保留一个也没有的车辆。','B把Collect限制放进LEFT JOIN的ON，让每辆车尝试连接取车事件；没匹配时右侧列填NULL，再WHERE e.vehicle_id IS NULL。该字段在事件schema中NOT NULL，因此NULL可靠表示未匹配，不会误把真实事件判成无事件。','教学三车：V1有Collect+Return，V2有Reserve+Cancel，V3无事件。答案为V2、V3。V1虽现在已归还，仍曾取过车，所以不在结果。若把Collect条件移到WHERE，会滤掉右侧NULL行，破坏题意。'],
 '主报告p25–26原生图：A与B均75行，各展示前10和末10，省略中间55行。截图首尾相同不能严格证明所有行相同；原有独立双向EXCEPT ALL检查可作为另一个轮次的校验证据，不冒充本轮截图。',
 'NOT IN遇到子查询NULL会产生UNKNOWN，这也是不能随意替换NOT EXISTS的原因。B的Collect谓词属于匹配条件，不能错误移到结果过滤。',
 '一辆只有Return事件且没有Collect事件的车是否输出？',
 '输出。题目只问是否曾有Collect；不能用业务直觉替代明确的存在性条件。',[25,26])

add('3.1.2','两种写法汇合为反连接',
 ['（2）报告并比较（A）与（B）的执行计划。它们是否为相同计划？解释规划器做了什么以及原因。（1.5分）'],
 '比较实际节点结构而非SQL字符。两条看似不同的SQL可被优化成相同关系运算，计划相同是有意义的发现。',
 ['重放计划都使用Hash Right Anti Join。Anti Join输出一侧中找不到匹配的记录；Right描述规划器安排的物理输入方向，不是原SQL必须写RIGHT JOIN。','规划器可以将相关NOT EXISTS去相关，也识别LEFT JOIN加非空键IS NULL的模式，化为同一反连接。它对900辆车建立hash，读59539条Collect，经bitmap路径筛选，留下75辆未匹配车，再排序ID。','SQL逻辑上逐辆问“有没有”不代表数据库物理上要把约20万事件扫描900次。优化器选择集合处理是关系数据库的重要价值。'],
 '主报告p28–29完整重放：两者cost4576.31..4576.43，估计49、实际75；A17.320ms，B14.630ms。计划结构相同，小时间差不能建立稳定快慢结论。',
 '仅比较顶层Sort不足以说计划相同；应逐节点比较连接类型、输入对象、扫描谓词、估计/实际行数。不同版本/统计下也可能选别的合法路径。',
 'Hash Right Anti Join中的Right是否表示返回“有Collect”的车？',
 '不是。Anti表示保留无匹配者；Right只是物理保留输入的方向。仍需结合输入表确认车辆是被保留的一侧。',[27,28,29])

add('3.2','两条查询 × 三组开关：六份计划',
 ['PostgreSQL允许通过psql运行时配置参数影响规划器。本节抑制几种扫描方式以比较查询；生产环境不建议靠抑制计划类型工作，但它有助理解计划为何被选择。原题给出PostgreSQL17查询规划配置文档链接。','报告并解释C、D两个查询在三组条件下的执行计划：（原PDF编号3）索引与顺序扫描均启用；（4）索引启用、顺序扫描受抑制；（5）索引受抑制、顺序扫描启用。说明选择原因，参考时间、成本、行数与查询规划知识。','注意：本题bitmap与index-only也算索引扫描；Q2.1的IDX_EVENT_TYPE_TIME须仍存在。Query C: SELECT * FROM BOOKING_EVENTS WHERE event_type < \'Collect\'; Query D: SELECT * FROM BOOKING_EVENTS WHERE event_type >= \'Collect\';','解释最多六种计划占2分，解释规划器选择占2分。C与D合起来让表中每行恰好出现一次，两者仅在Collect的哪一侧不同；说明为何足以改变计划。下一题前须将index、bitmap、index-only、sequential四种开关全部恢复on。'],
 '这是完整的六个实验格，虽然原题没有编号3.2.1等SQL文件，评分又区分计划解释和规划选择；本页同时覆盖两部分。记录C1/D1/C2/D2/C3/D3、实际开关和全部计划。',
 ['event_type比较是文本排序，不是事件时间或业务阶段。记录轮次中C只有Cancel的8158行，D为其余188283行，共196441行。低选择率C≈4.15%，D≈95.85%，分界方向改变工作量。具体排序依赖collation，不要泛化到任意数据库。','设置1四个开关on；设置2只抑制seqscan；设置3抑制indexscan、indexonlyscan、bitmapscan，保留seqscan。只关闭enable_indexscan仍允许bitmap，不符合题目把它也算索引的要求。off是抑制路径，不是所有情形的硬禁止。','C1/C2同bitmap计划，同cost1937.08，C2全缓存命中而C1有31 reads，计时12.443降到2.095ms不能归因为新路径。C3需扫全表并剔188283行，20.725ms。D1/D3顺扫适合几乎全表；D2被迫bitmap，读全部1636heap块还处理大量索引项，成本8357.69更高，但本次22.959ms仍略低于D1的24.116ms。'],
 '主报告p30–33六图及恢复开关图；p34–35逐字转录完整原生计划，p35–36分析。六格数值单独列在本页表格。C1 exact1625/total shared hit1628 read31；C2 shared hit1659；D2 shared hit1868 read493。buffers包含子节点访问，不能重复累加当唯一物理页数。',
 '原有旧说明“强制D bitmap更慢”与本轮数据冲突，已保留原来源并修正结论：成本预测更贵，单次测量略快，两者并不矛盾。不能把成本8357.69写成8357.69ms。',
 'C只返回4.15%，为什么仍访问1625/1636个heap页？',
 '行选择率和页覆盖率不同。少量匹配行可能分散在几乎所有页；bitmap仍可减少处理的行并批量按页访问，但不是只读4.15%的数据页。',[30,31,32,33,34,35,36])

add('4.1.1','会话1：找到最新事件为Return的车',
 ['（1）在第一个psql连接中开始事务，查询一辆当前可用的车，即最近一次事件是Return的车辆。暂时不要提交。（2分）'],
 '使用真正独立的连接，BEGIN后保持打开。先找到最新事件再判断Return；原文件固定到完整记录轮次选定的VEH-0004，重新初始化或实验后状态不同可能查不到，不能凭空认定永远可用。',
 ['先pg_backend_pid/current_database确认身份，BEGIN开启事务，SHOW确认read committed。SAVEPOINT collect_attempt只建立可回退点；原文件没有ROLLBACK TO，所以后面错误仍以整个事务ROLLBACK结束。','DISTINCT ON(vehicle_id)配ORDER BY vehicle_id,event_time DESC,event_id DESC，为每辆车取第一条，即时间最新、同时间最大ID。外层WHERE再筛vehicle_id=VEH-0004与event_type=Return。若先WHERE Return再挑最新，会忽略更新的Reserve或Collect。','教学事件：V1 09:00 Return、10:00 Reserve。正确最新为Reserve不可用；先过滤Return会错误显示09:00可用。普通SELECT不会因你看过这辆车就为你预留。'],
 '主报告p37与Q4.1_VEH0004_connection1.png是完整原生轮次。使用LEFT/RIGHТ或PID标记区分连接；本页不用Study的VEH-0001/LATERAL旧轮次充当当前代码。',
 'WITH并非新建永久表；DISTINCT ON是PostgreSQL特有语法。当前固定车辆是重现记录的选择，学习通用查找可以移除vehicle_id筛选，但必须随后把实际选中ID带入两连接。',
 '为什么ORDER BY的第一项必须是vehicle_id？',
 'DISTINCT ON表达式必须与ORDER BY最左项对应；之后的时间和ID决定每个vehicle组内哪一行成为第一行。',[37])

add('4.1.2','会话2：未来预约先提交',
 ['（2）在第二个连接中开始另一个事务。对会话1选中的同一辆车执行相同的可用性检查，为另一个会员记录三天后的Reserve，然后提交。（0.5分）'],
 '会话1仍打开时在会话2完成BEGIN、重查、INSERT Reserve、COMMIT。选择不同member，并保持相同vehicle_id。截图必须能够证明两个连接独立以及会话2已提交。',
 ['文件先连接assignment2并显示PID。psql的\\connect/\\c是客户端命令，不是SQL；重新连接会替换当前会话，所以只能在第2个窗口运行，不能误关仍打开的连接1。','子查询先ORDER BY event_time DESC,event_id DESC LIMIT1，再外层检查Return。随后给member2插入Reserve，用NOW()+INTERVAL \'3 days\'表示事务起点时间加三天，RETURNING显示实际插入字段，COMMIT使其他事务的新语句可见。','NOW()在同一事务内稳定，不是每次调用都重新读墙钟。Reserve不会触发Collect拒绝分支，记录未来时间也没有表达预约结束区间；该简化模型把最新事件当当前状态。'],
 '主报告p38与Q4.1_VEH0004_connection2.png显示第二连接记录并提交同车Reserve。原始练习VEH0002/0003有语法错误或错窗口记录，不与此轮拼接。',
 '把整份Q4脚本顺序喂给同一个连接无法展示并发；必须人工按连接标签交错执行。Future reserve的业务问题在4.1.4解释。',
 '会话1开着事务，为何没挡住会话2INSERT？',
 '会话1先前普通查询未持有预留这辆车的冲突行锁；其兼容表锁不阻止新增事件。快照只是可见性规则。',[38])

add('4.1.3','会话1：Collect被触发器拒绝',
 ['（3）回到第一个连接，尝试为另一个会员在当前时间对同车记录Collect，然后提交。报告每一步发生了什么，以及最终哪些事件被记录到该车上。（1分）'],
 '继续原连接1的打开事务，不重连或重新BEGIN。尝试member1的Collect，记录错误、COMMIT的实际结果，再检查最近事件。要区分历史Collect与本次失败新增。',
 ['INSERT执行前BI_COLLECT触发器读取该车最新事件。会话2已提交，当前语句可看到Reserve；最新事件按event_time排，三天后的Reserve排在现在的Collect前。last_member=2与NEW.member_id=1不同，RAISE EXCEPTION拒绝插入。','错误使事务进入失败状态；普通COMMIT在这种状态实际结束为ROLLBACK。原文件虽早有SAVEPOINT，但没有ROLLBACK TO来局部恢复。其后SELECT在新语句中检查历史，确认本次竞争只留下Reserve。','SERIAL序列值可能已分配，即使插入回滚也不保证回收。看到event_id跳号不能据此认定存在一条成功Collect。历史Collect仍可能出现在LIMIT3里，必须结合member、time和event_id区分。'],
 '主报告p39与Q4.1_VEH0004_collect_result.png保留原生错误和最后事件。根SQL使用\\set ON_ERROR_STOP off，使psql在预期错误后仍继续执行COMMIT与核验查询；它不使数据库忽略错误或自动提交失败插入。',
 '这次是业务规则异常，并非死锁；没有两会话互相等待的环。不得把报错后COMMIT按字面写成成功提交。',
 '为什么未来Reserve会阻止现在Collect，难道NOW()错了？',
 '不是时间函数错误。触发器把event_time最大的事件当当前状态，没有用预约有效区间区分“现在可用、未来已订”。',[39])

add('4.1.4','快照、陈旧检查与业务含义',
 ['（4）同时从数据库与共享汽车业务的角度解释结果。如有助于解释，可加入事务事件调度表或优先图。（2.5分）','提示：步骤（1）的查询答案到步骤（3）时还真实吗？BI_COLLECT运行时用了哪个快照？有什么（如果有）阻止会话2在会话1不知情时改变答案？'],
 '这是解释题，没有新SQL。串起两连接时间线、READ COMMITTED可见性和触发器规则；不能只说“发生了race condition”。',
 ['时间线：T1 BEGIN→查到Return；T2 BEGIN→同车Return→写未来Reserve→COMMIT；T1 INSERT Collect→触发器看到已提交Reserve→异常→ROLLBACK。第一次检查结果已过时。','READ COMMITTED通常每条命令取新快照，事务打开不等于固定起始快照。触发器在发起操作的事务内部执行，没有神奇的全局最新特权；此处命令发生于T2提交之后，足以看到Reserve。UDF中的BEGIN是PL/pgSQL代码块，不会再开独立SQL事务。','业务结果是停车站会员被拒绝，因为另一会员三天后预约已成为最新状态。协调检查与写入能减少竞争窗口；若要合理支持未来预约，还需记录起止时间并校验区间冲突。仅加锁不能修复“未来等于现在”的模型。'],
 '主报告p40原说明与p37–39操作图对应。普通SELECT仍会拿兼容ACCESS SHARE表锁；原题p7说读取不加锁是教学简化，应理解为普通读取没有替车辆预留冲突行锁。',
 '增加SELECT FOR UPDATE是学习建议，不是本作业原答案；要有效，所有预约与取车路径都应锁同一VEHICLES行并在锁后重新检查，不能只锁一条旧事件。',
 '把BEGIN留着是否保证后续语句都读到最初Return？',
 '在默认READ COMMITTED下不会。后续语句可看到另一事务在两语句之间已经提交的变化。',[37,38,39,40])

add('4.2.1','反向更新两行，亲眼看到死锁',
 ['（1）在两个psql连接中各开始一个事务。第一连接先更新VEH-0401里程，再更新VEH-0501；第二连接以相反顺序更新相同两车。逐条运行以观察哪条阻塞。报告每一步发生的情况，完整引用所有错误消息。（1.5分）'],
 '根文件是一份交错执行清单，必须按Connection标签分配给两个窗口。先让双方各持一行，再互相请求，才能形成环；一次在一个连接运行不会产生同样死锁。',
 ['初始149100/122150。T1更新0401加10，暂时149110但未提交，持锁；T2更新0501加20，暂时122170但未提交，持锁。T1请求0501等待，这时只有T1→T2，仍不是死锁。','T2再请求0401，T2→T1闭合成环。PostgreSQL检测后中止本轮T2，撤销它先前成功的+20并释放锁；T1等待语句继续，使0501变122160。T2 COMMIT显示ROLLBACK，T1 COMMIT成功，最后149110/122160。','UPDATE RETURNING显示的是当前事务看到的新值，不等于已经提交。原生T1等待116906.993ms包含人切窗口输入命令的等待，不能解释为更新两辆车要算116秒；T2报错1019.158ms也不是普通扫描速度。'],
 '主报告p41–44及Q4.2_01..05截图。PID8668是LEFT/T1，40916是RIGHT/T2；本轮RIGHT为受害者。完整中文诊断在p44逐字保留。completed旧轮次T1受害、T2提交+20，最终149120/122170，单独归档，不能与当前图混用。',
 '死锁受害者不保证永远是第二个请求的会话，也不是固定PID。重跑选择可能改变；本页只报告这一轮证据。不要仅回滚出错的第二句而保留受害事务第一次更新。',
 'T1第一次等待时为什么还不能叫死锁？',
 '只有单向等待时T2仍可提交释放锁。直到T2也等待T1资源，双方形成环才没有一方能自行前进。',[41,42,43,44])

add('4.2.2','等待图、受害事务与最终值',
 ['（2）画出DBMS介入前一刻的等待图（wait-for graph），并标记环。说明DBMS如何处理死锁，以及两个事务分别怎样结束。（1分）'],
 '这是图与分析题，没有独立SQL。箭头应从等待者指向阻塞者，并标明等待哪辆车；图对应检测前，不是回滚后的状态。',
 ['T1持0401，等T2的0501，所以T1→T2标VEH-0501。T2持0501，等T1的0401，所以T2→T1标VEH-0401。两条边就是有向环。','检测器打破环的方法是中止一个事务。本轮T2的整个事务失败，+20撤销；T1继续并提交两个+10。图中的ShareLock on transaction是行版本冲突所表现出的事务等待，不要把它误读成共享读锁可以互相兼容所以不可能死锁。','教学核算：0401初149100+T1的10=149110；0501初122150+T1的10=122160。T2曾显示122170但没提交，回滚后不进入最终账。'],
 '主报告p43手绘等待图、p44原错误；独立Q4.2_wait_for_graph.png/svg同样表达检测前的环。重复图在本题与4.2.1共用，描述和版本一致。',
 '原Study死锁图可复用拓扑，但其T1受害叙述与本轮不符。本站新图采用当前LEFT/RIGHT与当前资源，不重用旧受害者标签。',
 '若图只画“0401→0501→0401”，有什么问题？',
 '等待图的节点应是事务/会话，资源写在边上或另作资源分配图。必须能读出哪个事务在等待哪个事务。',[41,42,43,44])

add('4.2.3','用一致顺序预防等待环',
 ['（3）指出一种在死锁发生前就可预防它的策略，并说明合作社要为该策略付出什么代价。（0.5分）','提示：UPDATE对被修改的行加锁并一直持有到事务结束。错误出现时每个会话的哪条语句仍在等待？'],
 '给出一条可执行的预防规则，并解释等待/协调成本。检测后重试是恢复措施，不算这里要求的预防策略。',
 ['统一按vehicle_id升序取得行锁或更新：两个事务都先0401再0501。若T1先拿0401，T2会在第一辆就等待；T2尚未持有0501，所以T1能继续拿0501并提交，等待环不能形成。','代价是重叠车辆的修正排队、代码所有路径必须遵守顺序、可能降低同资源吞吐。不是把整个数据库锁死，操作无关车辆仍可并行。事务尽量短也有利，但仅“动作快一点”不能从原则上排除反向拿锁环。'],
 '主报告p44明确给出一致升序策略与代价。下方建议SQL是教学建议、未经本次数据库执行，不替换原始反向顺序脚本。',
 '若一个后台流程仍先0501再0401，一致顺序保证就被破坏。策略必须覆盖所有可能同时修改这些资源的代码路径。',
 '死锁发生后自动重试，是预防还是恢复？',
 '是恢复。统一加锁顺序通过消除循环等待来预防；重试是在数据库已检测并中止事务后再尝试。',[44])

GROUP_PREREQ = {
 '1':'本组用事件日志描述车辆行为。BOOKING_EVENTS通过vehicle_id连VEHICLES，再由model_code、station_id连MODELS与STATIONS。账户题改用member_id连MEMBERS，sponsor_id再指向同表member_id。主键唯一非空、外键引用存在的目标；这些约束由setup.sql核对，不是按字段名字推测。',
 '2':'heap是表的实际行页，B-tree索引是另一套键到记录位置的结构。索引不自动含所有输出列。选择率是匹配行数/输入总行数；页覆盖率是涉及多少数据页，两者不同。BOOKING_EVENTS索引为(event_type,event_time)，MEMBERS表达式索引为规范化域名。',
 '3':'反连接回答“找不到任何匹配者”，而非普通内连接。扫描实验改变访问方法，但不能改变结果语义。BOOKING_EVENTS.event_type是NOT NULL文本，因此C/D两个相反不等式在同一排序规则下合起来恰好覆盖全表。',
 '4':'一个连接是一个独立服务器会话，用pg_backend_pid辨认。BEGIN到COMMIT/ROLLBACK是一笔事务；未提交写入通常不对其他会话可见。默认READ COMMITTED每条命令取得新快照。行锁协调冲突写入；快照回答可见性，不能代替锁。'
}

SCAN_ROWS=[
 ['C1','全部 on','Bitmap Heap + Bitmap Index','196.97..1937.08','8329 / 8158','4.423','12.443','1628 hit + 31 read'],
 ['D1','全部 on','Seq Scan','0.00..4091.51','188112 / 188283','0.937','24.116','1636 hit'],
 ['C2','seqscan off，其余 on','Bitmap Heap + Bitmap Index','196.97..1937.08','8329 / 8158','0.103','2.095','1659 hit'],
 ['D2','seqscan off，其余 on','Bitmap Heap + Bitmap Index','4370.29..8357.69','188112 / 188283','0.099','22.959','1868 hit + 493 read'],
 ['C3','三种index off，seq on','Seq Scan','0.00..4091.51','8329 / 8158','0.108','20.725','1636 hit'],
 ['D3','三种index off，seq on','Seq Scan','0.00..4091.51','188112 / 188283','0.095','21.383','1636 hit']
]

SUGGESTIONS={
 '1.1.1':("严格展示顺序的调用写法（学习建议；未重新执行）","SELECT * FROM V_BUSIEST_BAYS\nORDER BY collections DESC, body_type;"),
 '1.2':('生产数据先检查赞助环（学习建议，不更改作业原答案）',"WITH RECURSIVE paths AS (\n  SELECT member_id AS start_id, member_id, sponsor_id,\n         ARRAY[member_id] AS seen, false AS cycle\n  FROM MEMBERS\n  UNION ALL\n  SELECT p.start_id, m.member_id, m.sponsor_id,\n         p.seen || m.member_id, m.member_id = ANY(p.seen)\n  FROM paths p JOIN MEMBERS m ON m.member_id = p.sponsor_id\n  WHERE NOT p.cycle\n)\nSELECT DISTINCT start_id FROM paths WHERE cycle;"),
 '4.2.3':('一致顺序示意（教学建议；所有修改路径都须遵守）',"-- Run in each independent session; use the appropriate increment.\nBEGIN;\nSELECT vehicle_id FROM VEHICLES\nWHERE vehicle_id IN ('VEH-0401', 'VEH-0501')\nORDER BY vehicle_id FOR UPDATE;\nUPDATE VEHICLES SET odometer = odometer + 10\nWHERE vehicle_id IN ('VEH-0401', 'VEH-0501');\nCOMMIT;")
}

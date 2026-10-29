# A2 截图恢复记录

2026 年 10 月 28 日，从 `C:\Users\yuyan\Pictures\Screenshots` 找回并复制了以下 6 张原始截图。原文件保留，复制文件已逐一通过 SHA-256 一致性校验，没有编辑图片内容。

| 备份文件 | 内容 | 后续处理 |
| --- | --- | --- |
| 00_setup_complete.png | 数据初始化成功、五张表 | 环境记录 |
| 00_assignment2_connection.png | pgAdmin 当前数据库为 assignment2 | 环境记录 |
| Q1.1.1_create_view.png | V_BUSIEST_BAYS 定义及 CREATE VIEW 成功消息 | 可作为 Q1.1（1）证据 |
| Q1.1.2_result_partial.png | V_BUSIEST_BAYS 查询结果，状态栏显示共 6 行 | 第 6 行未显示，需要扩大结果区后补截 |
| Q1.1.2_plan_partial.png | 执行计划截图，状态栏显示共 68 行 | 仅显示开头几行；需要补齐完整计划及 Planning Time、Execution Time |
| Q1.2_create_view.png | V_ACCOUNT_LIABILITY 定义及 CREATE VIEW 成功消息 | 可作为 Q1.2 创建视图证据 |
| Q1.2_result.png | V_ACCOUNT_LIABILITY 的完整 10 行查询结果 | 后续补充保存；原图来自本次聊天附件，复制后通过 SHA-256 一致性校验 |

本次保存的 3 个 SQL 文件也仍在 A2 文件夹中：

- 49079984_A2_1.1.1.sql
- 49079984_A2_1.1.2.sql
- 49079984_A2_1.2.sql

恢复后连接现有 assignment2 数据库继续。初始化脚本 a2-2026-fleetdb.sql 会删除并重建 assignment2 数据库，不应为了恢复 pgAdmin 窗口而重跑它。

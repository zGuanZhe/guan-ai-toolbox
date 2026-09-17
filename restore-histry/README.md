# 通用历史会话管理与恢复中心 (restore-histry)

**“观的 AI 工具箱” 核心模块**。遵循“**分工具独立管理，严禁全量恢复，单会话精准受控**”的核心铁律，吸收开源知名项目（如 `ccswitch`、ZCode 官方恢复引擎）在会话管理与恢复上的优秀设计。

---

## 🚫 为什么彻底废除“一键全部恢复”？

在多工具、多账号、多工作区并行的复杂 AI 编程环境中，“一键全部恢复”会导致：
1. **会话串号与数据污染**：跨账号、跨工具的数据混淆；
2. **意外覆盖破坏**：将当前正常专注编码的活跃状态强行冲掉；
3. **不可逆风险**：缺乏细粒度审计与撤销机制。

**本模块核心准则**：
- **工具物理隔离**：各大 AI 编程工具拥有各自独立的适配器驱动与管理空间；
- **工作区层级过滤**：支持按工程路径精准收敛会话范围；
- **细粒度单会话透视**：清晰呈现会话 ID、首条 Prompt 标题、消息条数、数据体积、最后活跃时间；
- **两阶段安全操作**：仅对用户**明确单选指定的会话**创建独立快照并执行恢复/导出，绝不波及其他会话！

---

## 🛠️ 6 大编程工具适配矩阵（实测 100% 连通）

| 工具标识 | 对应 AI 编程工具 | 底层存储架构 | 支持的单会话操作 |
| :--- | :--- | :--- | :--- |
| **`workbuddy`** | **腾讯 WorkBuddy AI** | SQLite + WAL + JSONL 消息流 | 单会话跨账号绑定挂载、软删除撤销、Markdown 导出 |
| **`trae`** | **字节跳动 Trae / Trae CN** | `workspaceStorage` + `state.vscdb` (SQLite) | 工作区分组扫描、单工程会话状态提取与安全备份 |
| **`zcode`** | **腾讯 ZCode / CodeBuddy** | 遵循官方 `scan-legacy-sessions` 插件规范 | 分任务独立恢复与历史状态重置 |
| **`claudecode`** | **Anthropic Claude Code CLI** | 遵循开源 `ccswitch` 规范，解析 `history.jsonl` | 按 Project 聚合 70+ 会话，单会话独立提取与 Markdown 导出 |
| **`antigravity`**| **Google Antigravity (AGY)** | `brain/<id>` (task.md + transcript.jsonl) | 索引 37+ 历史 Brain 会话，单会话完整报告导出与状态查看 |
| **`gpt`** | **OpenAI Codex / CLI / GPT** | `legacy_archive` 与 `~/.codex` | 历史对话流单项提取与归档 |

---

## 🚀 启动与使用方式

### 方式一：双击运行交互控制台（推荐）
直接双击运行本目录下的：
```
一键历史恢复中心.bat
```
或在终端执行：
```bash
python restore_manager.py
```
交互流程：
1. 选择要管理的工具（1~6）；
2. 选择工作区/项目（或查看全部）；
3. 浏览带时间、大小、标题的会话清单；
4. **单选输入具体会话序号**；
5. 选择：`[1] 仅恢复并激活该单条会话` / `[2] 导出为 Markdown` / `[3] 单会话独立快照`。

### 方式二：命令行 CLI 精准调用（严禁不带 session 参数执行恢复）
```bash
# 列出 Claude Code 的所有历史会话 (包含原汁原味的 Prompt 标题)
python restore_manager.py --tool claudecode --list

# 仅对 Claude Code 的指定单会话导出为 Markdown 归档
python restore_manager.py --tool claudecode --session e3c10929-20f2-48bb-a83b-5cc0507b7464 --export

# 仅对 WorkBuddy 的指定单会话执行精准恢复与激活
python restore_manager.py --tool workbuddy --session 3a40a451-bc1d-4d2b-83bd-48855854b8ac --restore

# 查看 Antigravity 的 37 个历史 Brain 会话清单
python restore_manager.py --tool antigravity --list
```

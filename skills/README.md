# 观的 AI 工具箱 · 技能与协议生态中枢 (Skills Hub & MCP Ecosystem)

欢迎来到 **观的 AI 工具箱 · Skills 模块**。本项目旨在打通现代化 AI 编程助手（WorkBuddy、Claude Code、Cursor、Trae、Antigravity、OpenAI Codex 等）的核心扩展能力，整合全网主流技能规范（`SKILL.md`）、顶级前端设计系统规范（`DESIGN.md`）以及模型上下文协议（`MCP`），构建统一、工程化、开箱即用的智能化开发环境。

本模块全面引入了 **`ccswitch` (Claude Code Switcher)** 的激活状态机管理思想，支持技能的 **按需激活 (Active) / 休眠 (Inactive)** 动态切换、场景预设 (Profiles) 一键置换，以及全网线上技能平台的检索与一键拉取。

---

## 目录架构一览

```plaintext
skills/
├── hub/                     # 【精选即用】按领域整理的高频生产级 Agent Skills (本地池)
│   ├── document_media/      # 办公文档处理 (Word/PDF/PPT/Excel/协同撰写)
│   ├── engineering/         # 现代工程规范 (TDD测试驱动、API设计、Git流、MCP构建)
│   ├── ui_ux_design/        # 现代前端设计与交互原型 (UI/UX 指南、Web Artifacts)
│   └── security_analysis/   # 安全审计与敏感配置扫描
├── design_systems/          # 【设计系统】整合 getdesign.md 的 74+ 国际顶级品牌规范
│   ├── brands/              # 包含 Apple, Stripe, Linear, Vercel, Supabase 等完整规范
│   ├── template/            # 通用标准化 DESIGN.md 模板
│   └── README.md            # 设计规范注入指南与避坑经验
├── mcp/                     # 【协议中枢】Model Context Protocol 接入套件与 14 款精选服务
│   ├── configs/             # 14 款核心 MCP 机器配置 (全端 JSON/TOML 及各客户端预置)
│   ├── templates/           # Python 标准 stdio FastMCP Server 模板脚手架
│   ├── 14_MCPS_GUIDE.md     # 14 款生产级 MCP 核心服务器完整集成与认证指南
│   └── README.md            # MCP 协议标准与各 IDE 配置实战
├── tools/                   # 【CLI 工具链】CCSwitch 风格多宿主管理 CLI
│   └── skill_manager.py     # 核心管理 CLI（状态机检测、开关切换、Profile应用、网络导入）
├── references/              # 【权威参考源】全网顶级开源项目克隆与灵感库
│   ├── ECC/                 # affaan-m/ECC (292个技能, 68个Agent, 7大宿主适配器)
│   ├── awesome-design-md/   # VoltAgent/awesome-design-md (getdesign.md 官方规范库)
│   ├── anthropics-skills/   # anthropics/skills (Anthropic 官方技能标准)
│   └── addyosmani-agent-skills/ # addyosmani/agent-skills (Google 大佬工程技能库)
├── NETWORK_PLATFORMS.md     # 【全网汇编】全球 AI Agent Skills 与 MCP 生态平台大全
├── network_platforms.json   # 机器可读的全网技能与 MCP 平台结构化数据集
└── README.md                # Skills 模块说明 (本文档)
```

---

## 核心设计理念

### 1. 参考 CCSwitch 的状态机管理 (Active / Inactive 状态机)
- **上下文纯净原则**：在 AI 编程中，无节制加载数十个技能会导致 Context Window 极度臃肿并引发模型指令混乱。
- **本地池与活体分离**：`hub/` 作为中央储备池（Pool），目标工作区或指定宿主目录仅保留当前任务所需的技能。
- **状态追踪**：
  - `[ACTIVE 激活中]`：已部署至目标宿主，智能体当前可以直接调度。
  - `[INACTIVE 休眠]`：存在于本地池中，未注入上下文，保持环境清爽。
  - `[CUSTOM 自定义]`：用户自建或项目特有的本地专属技能。

### 2. 场景化预设组合 (Workflow Profiles)
参考 `ccswitch` 的配置切换模式，支持一键切换整套技能组合：
- `fullstack`: 全栈开发（前端设计 + REST API + TDD 测试 + Git 流）
- `frontend`: 现代 Web 前端（前端设计规范 + Web Artifacts 部件）
- `python-dev`: 后端工程（API 架构 + TDD 测试 + Git 流 + MCP 开发）
- `office-docs`: 办公文档处理（Word + PDF + PPT + Excel + 协同撰写）
- `security`: 安全合规（安全评审 + 敏感配置扫描）

### 3. 全网平台打通与生态包管理 (Network Registries)
- 汇总全网核心平台（`skills.sh`、`Smithery.ai`、`getdesign.md`、`awesome-agent-skills` 等），提供从网络 Git 仓库直接拉取技能到本地池的能力。

---

## 快速上手与 CLI 工具使用指南 (`tools/skill_manager.py`)

### 1. 状态机诊断 (诊断当前工作区或宿主技能激活状态)
```bash
# 诊断当前工作区的激活状态
python tools/skill_manager.py --status

# 诊断指定项目或指定宿主 (workbuddy, claudecode, cursor 等)
python tools/skill_manager.py --status --target "D:/MyProjects/DemoApp" --host workbuddy
```

### 2. 精准激活与休眠开关 (CCSwitch Toggle)
```bash
# 激活指定技能到目标项目
python tools/skill_manager.py --enable tdd-workflow --target "D:/MyProjects/DemoApp"

# 停用并归档指定技能 (从活体上下文移除，Hub池中完整保留)
python tools/skill_manager.py --disable tdd-workflow --target "D:/MyProjects/DemoApp"
```

### 3. 场景预设一键切换 (Profile Switch)
```bash
# 查看所有可用 Profile
python tools/skill_manager.py --profiles

# 将目标项目一键切换为全栈开发环境
python tools/skill_manager.py --profile fullstack --target "D:/MyProjects/DemoApp"

# 一键切换为后端开发环境
python tools/skill_manager.py --profile python-dev --target "D:/MyProjects/DemoApp"
```

### 4. 浏览与检索全网在线平台 (Network Registries)
```bash
# 列出全网权威平台清单 (包含 skills.sh, Smithery.ai, Anthropic Skills 等)
python tools/skill_manager.py --platforms

# 关键词搜索全网平台 (如 mcp, registry, design)
python tools/skill_manager.py --platforms-search mcp
```

### 5. 从网络一键导入开源技能
```bash
# 从任意合规 GitHub 仓库拉取技能至本地 Hub 社区库
python tools/skill_manager.py --import-git https://github.com/owner/repo --category community
```

### 6. 查看与注入 74+ 品牌设计系统
```bash
# 查看所有支持的 74 套国际品牌设计系统
python tools/skill_manager.py --brands

# 将 Stripe 或 Linear 规范注入当前前端项目
python tools/skill_manager.py --copy-design stripe --target "D:/MyProjects/DemoApp"
```

### 7. 14 款核心生产级 MCP 服务管理与全端同步 (Curated MCP Hub)
本项目原生整合了 14 款覆盖逆向调试、云端治理、端到端测试与数据库的生产级 MCP 服务：
```bash
# 查看 14 款核心 MCP 服务器清单与协议参数
python tools/skill_manager.py --mcp-list

# 巡检 CC-Switch、Claude Code、Codex、WorkBuddy 各客户端挂载状态
python tools/skill_manager.py --mcp-status

# 一键强刷并同步 14 款 MCP 服务至全端所有客户端
python tools/skill_manager.py --mcp-sync all

# 单独同步指定客户端 (支持: ccswitch, claude, codex, workbuddy)
python tools/skill_manager.py --mcp-sync ccswitch
python tools/skill_manager.py --mcp-sync codex
```

### 8. 14 款 MCP 服务器矩阵
| 序号 | 服务标识 (ID) | 协议类型 | 功能领域 | 官方/标准命令或端点 |
| :---: | :--- | :---: | :--- | :--- |
| 1 | `chrome-devtools` | `stdio` | 浏览器远程 DevTools 调试 | `npx -y chrome-devtools-mcp@latest` |
| 2 | `cloudflare` | `HTTP SSE` | Cloudflare 控制台管理 (需 OAuth) | `https://mcp.cloudflare.com/mcp` |
| 3 | `cloudflare-bindings` | `HTTP SSE` | Workers KV/D1/R2 资源绑定 (需 OAuth) | `https://bindings.mcp.cloudflare.com/mcp` |
| 4 | `cloudflare-builds` | `HTTP SSE` | Workers 部署构建流水线 (需 OAuth) | `https://builds.mcp.cloudflare.com/mcp` |
| 5 | `cloudflare-docs` | `HTTP SSE` | Cloudflare 官方最新开发文档 (公开免鉴权) | `https://docs.mcp.cloudflare.com/mcp` |
| 6 | `cloudflare-observability` | `HTTP SSE` | 性能实时观测与错误追踪 (需 OAuth) | `https://observability.mcp.cloudflare.com/mcp` |
| 7 | `context7` | `HTTP SSE` | 实时检索开发库与框架最新技术文档 | `https://mcp.context7.com/mcp` |
| 8 | `figma` | `HTTP SSE` | Figma Dev Mode 设计规范与组件读取 | `https://figma.mcp.run/mcp` |
| 9 | `ida-pro-mcp` | `stdio` | IDA Pro 逆向工程与反编译联动 | `python -m ida_pro_mcp` |
| 10 | `js-reverse` | `stdio` | Agent 前端 JS 逆向调试与网络拦截 | `npx -y js-reverse-mcp@latest` |
| 11 | `mysql-local` | `stdio` | 本地 MySQL 数据库安全查询与架构探测 | `npx -y mysql-mcp-server` |
| 12 | `node_repl` | `stdio` | Codex CUA Node / 原生 Node REPL 运行沙箱 | `node_repl.exe` |
| 13 | `playwright` | `stdio` | 端到端浏览器自动化与页面快照测试 | `npx -y @executeautomation/playwright-mcp-server` |
| 14 | `redis` | `stdio` | Redis 内存缓存与键值空间分析 | `npx -y @modelcontextprotocol/server-redis redis://localhost:6379` |

> 📖 详细使用手册与各平台 OAuth 授权指南参见：[`skills/mcp/14_MCPS_GUIDE.md`](mcp/14_MCPS_GUIDE.md)

---

## 配合各 AI IDE 使用指南

- **WorkBuddy**:
  - 指定 `--host workbuddy`，工具会自动将激活技能同步至 `.workbuddy/skills/` 或 `.skills/` 目录。
  - 在前端项目注入 `DESIGN.md`，并在聊天中输入 `@DESIGN.md` 进行精准视觉对齐。
- **Claude Code**:
  - 指定 `--host claudecode`，自动同步至 `.claude/skills/`。
- **Cursor**:
  - 指定 `--host cursor`，自动同步至项目的 `.skills/` 目录。
- **Google Antigravity / Gemini CLI**:
  - 指定 `--host antigravity`，直接同步至工作区 `.skills/` 目录，由 Antigravity 框架原生读取。

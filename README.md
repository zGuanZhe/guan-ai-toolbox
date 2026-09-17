# 观的 AI 工具箱 (Guan's AI Toolbox)

欢迎使用 **观的 AI 工具箱**！本项目是一个模块化、工业级的通用 AI 编程助手效率工具与大模型生态工程套件。

> 🌟 **核心设计哲学**：**通用架构，专属适配，物理隔离（Universal Architecture, Dedicated Adapters, Isolated Control）**。  
> 本工具箱覆盖开发者日常使用的各类 AI 编程客户端与开发生态（**WorkBuddy、Trae、ZCode、Qoder、Claude Code、Antigravity、ChatGPT / OpenAI、xAI Grok** 等），为不同工具提供深度的会话恢复、指纹反检测批量注册、多账号池管理与秒级切换支持。

---

## 📂 项目四大支柱模块架构

```plaintext
观的ai工具箱/
│
├── 📁 restore-histry/          # 跨工具会话记录管理与独立恢复中枢
│   ├── core/                   # 抽象基类 (BaseRestoreAdapter) 与调度管线
│   ├── adapters/               # 6 大主流编程工具专属适配器 (物理隔离，禁止一键全部混合恢复)
│   │   ├── workbuddy_adapter.py    # [WorkBuddy] 跨 UID 迁移、解除软删除、WAL 强刷
│   │   ├── trae_adapter.py         # [Trae / Trae CN] state.vscdb 与工作区会话恢复
│   │   ├── zcode_adapter.py        # [ZCode] 本地历史持久化与恢复
│   │   ├── claudecode_adapter.py   # [Claude Code] 参考 ccswitch 的会话日志提取
│   │   ├── antigravity_adapter.py  # [Antigravity] 任务记录与会话历史恢复
│   │   └── chatgpt_adapter.py      # [ChatGPT] 离线备份会话解析与导入
│   ├── cli/                    # 专属交互控制台
│   ├── main.py                 # 会话恢复总入口 (python main.py)
│   ├── 启动会话恢复中心.bat     # Windows 桌面一键双击启动
│   └── README.md
│
├── 📁 register/                # 多厂家自动注册与智能账号池一键切换中枢
│   ├── core/                   # 核心通用设施
│   │   ├── browser_camoufox.py     # 驱动 "D:\Test\Sub2\camoufox\camoufox.exe" 反检测指纹浏览器
│   │   ├── base_account_pool.py    # 账号池持久化与状态机抽象模型
│   │   └── base_register.py        # 注册引擎标准协议
│   ├── switchers/              # 多厂家账号池一键置换 (参考 Antigravity-Manager)
│   │   ├── workbuddy_switcher.py   # WorkBuddy 多账号热切换 (自动备份与平滑重启)
│   │   ├── trae_switcher.py        # Trae 多账号凭据管理
│   │   └── antigravity_switcher.py # Gemini / Antigravity 账号快速轮换
│   ├── engines/                # 多厂家自动化注册流程调度
│   │   ├── workbuddy_reg.py        # WorkBuddy 自动化开户
│   │   ├── qoder_reg.py            # Qoder 注册与 Token 捕获
│   │   ├── openai_reg.py           # OpenAI / ChatGPT 批量注册
│   │   ├── tavily_reg.py           # Tavily Search API 批量开户
│   │   └── grok_reg.py             # xAI Grok 注册 (YesCaptcha 对接)
│   ├── modules/                # 底层独立注册脚本库 (grok, openai, tavily, email_browser)
│   ├── references/             # 官方克隆知名开源参考
│   │   ├── any-auto-register/      # 多平台自动注册权威参考
│   │   └── Antigravity-Manager/    # 账号池与会话切换权威参考
│   ├── main.py                 # 注册中心主入口 (python main.py)
│   ├── 启动账号与注册中心.bat   # Windows 桌面一键双击启动
│   └── README.md
│
├── 📁 skills/                  # 通用 Skills 技能生态、顶级设计系统与 MCP 中台
│   ├── hub/                    # 【精选即用】按领域整理的高频生产级 Agent Skills
│   │   ├── document_media/     # 办公文档处理 (Word/PDF/PPT/Excel/协同撰写)
│   │   ├── engineering/        # 现代工程规范 (TDD测试驱动、API设计、Git流、MCP构建)
│   │   ├── ui_ux_design/       # 现代前端设计与交互原型 (UI/UX 指南、Web Artifacts)
│   │   └── security_analysis/  # 安全审计与敏感配置扫描
│   ├── design_systems/         # 【设计系统】整合 getdesign.md 74+ 国际顶级品牌规范
│   │   ├── brands/             # 74 套国际顶级品牌规范 (Apple, Stripe, Linear, Vercel 等)
│   │   ├── template/           # 标准化可复用 DESIGN.md 设计模板
│   │   └── README.md           # 前端视觉防漂移指南与注入说明
│   ├── mcp/                    # 【协议中枢】Model Context Protocol 接入套件与 14 款核心服务
│   │   ├── configs/            # 14 款核心 MCP 全端配置 (JSON/TOML) 及各 IDE 预置
│   │   ├── templates/          # Python FastMCP stdio Server 模板脚手架
│   │   ├── 14_MCPS_GUIDE.md    # 14 款核心生产级 MCP 服务器完整指南与 OAuth 认证手册
│   │   └── README.md           # 协议标准与配置指南
│   ├── tools/                  # 【CLI 工具链】CCSwitch 风格多宿主管理 CLI
│   │   └── skill_manager.py    # 核心管理 CLI (状态机检测、激活/休眠开关、场景Profile、网络导入)
│   ├── references/             # 【权威参考源】全网顶级开源项目克隆与灵感库
│   │   ├── ECC/                # affaan-m/ECC (292个技能, 68个Agent, 7大宿主适配器)
│   │   ├── awesome-design-md/  # VoltAgent/awesome-design-md (getdesign.md 官方规范库)
│   │   ├── anthropics-skills/  # anthropics/skills (Anthropic 官方技能标准)
│   │   └── addyosmani-agent-skills/ # addyosmani/agent-skills (Google 大佬工程技能库)
│   ├── NETWORK_PLATFORMS.md    # 【全网汇编】全球 AI Agent Skills 与 MCP 生态平台大全
│   ├── network_platforms.json  # 机器可读的全网技能与 MCP 平台结构化数据集
│   └── README.md               # Skills 模块完整指南
│
├── 📁 instruct/                # 智能体指令工程与认知编译器体系
│   ├── HOW_TO_WRITE_INSTRUCT.md# 认知编译器设计理论与规范开发指南 (20KB)
│   ├── antigravity-instruct/   # [Google Antigravity] 任务规则与 Doctor 自检
│   ├── claude-instruct/        # [Claude Code] 确定性沙箱与 CLAUDE.md
│   ├── gpt-instruct/           # [OpenAI Codex] 免杀安全契约 (100% 免疫误杀)
│   ├── upstream_sources/       # 上游权威开源参考 (已清除杀软诱因日志)
│   ├── workbuddy_presets/      # WorkBuddy AI 客户端专属配置与预设
│   ├── system_prompts/         # 跨平台通用系统级别 Prompt
│   ├── task_templates/         # 复杂任务标准化拆解与执行模板
│   └── README.md
│
├── 📁 others/                  # 扩展工具与前沿实验中枢
│   ├── ModelTrace/             # [xqy2006/ModelTrace] 模型路由检测与主动指纹归因系统
│   ├── modeltrace_cli.py       # 模型路由检测与指纹库管理 CLI
│   ├── useful_tools.json       # 实用云端接码与凭据转换工具元数据库
│   ├── 启动模型路由检测.bat     # Windows 桌面一键双击启动 Web 控制台 (http://127.0.0.1:7860)
│   ├── 打开实用云端工具.bat     # Windows 桌面一键打开邮箱接码与凭据转换网站
│   └── README.md               # 扩展中心说明文档
│
├── 📁 web/                     # 【可视化中台】Letters.app 风格全功能单页控制台
│   ├── index.html              # 沉浸式渐变画布、Bento Grid、14款MCP与实时测谎交互
│   ├── server.py               # 本地轻量 Web 服务与全功能 RESTful API (Port: 5050)
│   └── README.md               # Web 控制台设计规范与接口说明
│
├── 🚀 一键启动工具箱.bat        # Windows 快捷总控交互菜单 (主入口，选项 [1-6])
├── 🌐 启动工具箱Web控制台.bat   # Windows 桌面一键双击拉起 Letters 风格仪表盘
├── 📄 requirements.txt         # 统一 Python 依赖包声明
└── 📄 README.md                # 项目总览文档 (本文档)
```

---

## 🛠️ 模块核心能力矩阵

### 1. `restore-histry` (会话记录管理与独立恢复)
* **严格隔离准则**：各个工具独立管理，严禁无差别一键全部恢复，防止跨工具存储混乱。
* **参考 ccswitch 思想**：各工具独立索引会话元数据（会话 ID、时间戳、所属账号/UID、状态），提供可视化的选单恢复与回滚保障。

### 2. `register` (多厂家注册与账号池中枢)
* **参考 any-auto-register**：分厂家解耦，模块化支持邮件验证码抓取、Turnstile 突破与并发调度。
* **参考 Antigravity-Manager**：实现客户端登录态热替换，如 WorkBuddy 的 `account-snapshot.json` 快照置换机制，支持账号池添加、查看、秒切与客户端自动优雅重启。
* **集成 Camoufox 指纹浏览器**：使用本地专用反检测浏览器（`D:\Test\Sub2\camoufox\camoufox.exe`），实现反爬与反指纹追踪环境。

### 3. `instruct` (智能体指令工程与认知编译器)
* **认知编译器架构**：彻底消除大模型客套废话、软拒绝与破坏性覆写，贯彻单通道输入锁定、四级分流路由与四原语审计账本。
* **三大主流工具专注对齐**：针对 Google Antigravity、Anthropic Claude Code、OpenAI Codex 原生配置通道深度适配，彻底消除杀毒软件误杀隐患，完全绿色可逆。

### 4. `skills` (技能生态、顶级设计系统与 MCP 中台)
* **参考 CCSwitch 状态机管理**：独创 Active / Inactive 动态切换与 Profile 场景预设机制（`fullstack`, `frontend`, `python-dev`, `office-docs`, `security`），保持活体上下文纯净，杜绝 Token 浪费。
* **渐进式披露技能库 (Progressive Disclosure)**：精选 13+ 高频生产级技能，通过 `SKILL.md` 的 YAML 元数据实现零冗余 Token 消耗，被调用时按需展开。
* **74+ 国际品牌设计系统 (getdesign.md)**：彻底根治前端生成中的色彩与样式漂移，支持将 Apple、Stripe、Linear、Vercel 等 74 套顶级规范一键复制注入项目根目录 (`DESIGN.md`)。
* **打通全网生态 (NETWORK_PLATFORMS)**：系统收录并整合全网 16+ 核心技能平台（`skills.sh`, `Smithery.ai`, `Anthropic Skills` 等），支持通过 Git 一键拉取网络开源技能至本地池。
* **标准 MCP 协议支持与 14 款核心服务集成**：深度收录 14 款涵盖 Chrome DevTools、Cloudflare 全套生态（控制台/绑定/构建/文档/可观测）、Context7 最新技术文档、Figma Dev Mode、IDA Pro 逆向工程、JS 逆向调试、本地 MySQL、Node REPL、Playwright 浏览器自动化与 Redis 缓存的生产级服务。
* **全端环境一键秒级同步**：通过 `python skills/tools/skill_manager.py --mcp-sync all`，可一键将 14 款 MCP 服务双向强刷写入 `CC-Switch` (SQLite 数据库及活跃 Provider)、`Claude Code` (`~/.claude.json`)、`OpenAI Codex` (`~/.codex/config.toml`) 与 `WorkBuddy` (`~/.workbuddy/connectors/default/mcp.json`)。
* **多宿主适配 CLI 与总控中心**：内置 `python skills/tools/skill_manager.py` 与根目录 `一键启动工具箱.bat`，无缝支持 Skills/MCP 状态诊断、全端强刷与切换。

### 5. `others` (扩展工具与前沿实验室)
* **ModelTrace 模型路由检测与主动指纹归因**：
  - **核心痛点**：严防第三方中转 API / 聚合网关“狸猫换太子”（用便宜低质模型套壳冒充顶尖模型）。
  - **算法机制**：通过 3 组无语义长整数生成挑战，结合 Hellinger 距离去除环境偏置，计算全局 Softmax 概率，科学鉴定实际运行模型。
  - **内置 13 款主流模型指纹库**：覆盖 Claude 系列（Haiku 4.5、Sonnet 4.6/5、Opus 4.6/4.7/4.8/5）与 GPT 系列（GPT-5.4、5.5、5.6-luna/terra/sol、GPT-6 astra）。
  - **开箱即用体验**：双击 `others/启动模型路由检测.bat` 或通过总控 `[5]` 即可唤出 Web UI (`http://127.0.0.1:7860`)，支持自动 API 测谎、手动 Prompt 测谎与 Codex 后台监控插件 (`ModelTrace Guard`)。
* **常用云端效率与接码工具导航**：
  - **自动化邮箱 API** (`https://email.manageh.shop/`)：提供 Edu 教育邮箱、Gmail、iCloud、长效苹果隐私邮箱及全新 Google 邮箱接码与批量开户 API。
  - **Outlook 快速取件平台** (`https://mail.chatai.codes/`)：支持 IMAP OAuth2 + Graph API 双协议并行取件与令牌刷新，按 `账号----密码----clientid----刷新令牌` 批量导入。
  - **ChatGPT Session 转 sub2api / Codex 工具** (`https://convert.13916454.xyz/`)：一键将 ChatGPT 会话凭据批量转换为 sub2api、CPA、Cockpit、Codex、AxonHub 格式，无缝注入 CC-Switch 账号池。
  - **快捷启动**：直接双击 `others/打开实用云端工具.bat` 即可一键在浏览器中唤起。

### 6. `web` (全功能可视化 Web 控制台)
* **参考 Letters.app 顶奢美学**：
  - **环境渐变画布 (Ambient Canvas)**：外围 12px 视口间距搭配 28px 圆角与淡天蓝紫罗兰渐变，极具高级感。
  - **晶莹磨砂玻璃态与 Bento Grid 架构**：半透明 `backdrop-filter: blur(20px)` 玻璃卡片、微交互悬浮动效。
  - **全功能一站式整合**：涵盖 6 大 IDE 独立会话恢复、账号池快照切换、14 款生产级 MCP 全端一键强刷、74 套顶级品牌设计系统一键注入、免杀指令工程规范，以及 ModelTrace 原地在线测谎控制台。

---

## 🚀 极速上手

### 1. 可视化 Web 控制台（最推荐 🌟）
在根目录下双击运行：
```plaintext
启动工具箱Web控制台.bat
```
或在浏览器中访问：`http://127.0.0.1:5050`

### 2. 终端总控中心
在根目录下双击运行：
```plaintext
一键启动工具箱.bat
```

### 3. 单独启动各子中心
* **会话恢复中心**：双击 `restore-histry/启动会话恢复中心.bat` 或运行 `python restore-histry/main.py`
* **账号与注册中心**：双击 `register/启动账号与注册中心.bat` 或运行 `python register/main.py`
* **模型路由检测中心**：双击 `others/启动模型路由检测.bat` 或运行 `python others/modeltrace_cli.py --status`



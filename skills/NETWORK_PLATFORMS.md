# 全网 AI Agent 技能与 MCP 生态平台大全 (Global Agent Skills & MCP Registries)

> 🌐 **定位**：打通全网 AI Agent 技能库（Skills）、前端视觉防漂移规范（Design Systems）与模型上下文协议（MCP），打破本地工具孤岛，提供全球领先平台的权威索引与直达渠道。

---

## 一、 AI Agent 技能注册表与包管理器 (Agent Skills Registries & Repositories)

基于开放的 **`SKILL.md`** 规范（包含 YAML Frontmatter 元数据与渐进式披露执行脚本），以下是全球最具影响力、处于活跃维护状态的线上技能注册与分发生态：

| 平台 / 仓库 | 类型与定位 | 访问链接 | 核心能力与安装指令 | 推荐场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`skills.sh`** | **事实标准包管理器** (npm for Skills) | [skills.sh](https://skills.sh) | `npx skills find <query>`<br>`npx skills add <owner/repo>` | 跨 40+ 智能体一键安装网络技能 |
| **`Anthropic Official Skills`** | **官方标准参考库** (Anthropic 官方维护) | [github.com/anthropics/skills](https://github.com/anthropics/skills) | `git clone` 或直接提取子目录<br>内置 docx, pdf, pptx, xlsx, mcp-builder | 生产级文档处理与官方规范示范 |
| **`VoltAgent/awesome-agent-skills`** | **社区旗舰聚合目录** (1000+ 技能收录) | [github.com/VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 覆盖主流开发场景的社区技能聚合 | 寻找长尾、特定框架或小众技能 |
| **`affaan-m/ECC`** | **全能工程架构套件** (Everything Claude Code) | [github.com/affaan-m/ECC](https://github.com/affaan-m/ECC) | 292 个技能、68 个专业 Agent，7 宿主适配器 | 企业级编码规约与重度项目开发 |
| **`Tech-Leads-Club/agent-skills`** | **企业级安全加固库** (安全审计与静态扫描) | [github.com/tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) | 每一项技能均经静态代码扫描，防恶意提权 | 对代码安全、数据外泄敏感的企业环境 |
| **`addyosmani/agent-skills`** | **Google 架构师 SDLC 套件** (端到端研发流程) | [github.com/addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 覆盖 Spec、Plan、Build、Test、Review、Ship | 追求严密工程交付与 TDD 规范团队 |
| **`TerminalSkills/skills`** | **终端与 CLI 辅助跨工具库** | [github.com/terminal-skills/skills](https://github.com/terminal-skills/skills) | 专为命令行环境（Claude CLI, Gemini CLI）定制 | 终端重度开发者、远程服务器运维 |
| **`SkillsMP` / `OpenAgentSkill`** | **技能搜索引擎与市场** | [skillsmp.com](https://skillsmp.com) | 全文检索、热度排名、在线预览与一键复制 | 网页端快速检索与版本趋势追踪 |
| **`SkillHub (iFlytek)`** | **企业私有化技能注册中心** | [github.com/iflytek/skillhub](https://github.com/iflytek/skillhub) | Docker / K8s 私有化部署，细粒度权限管控 | 团队内部私有技能管理与内网开发 |

---

## 二、 前端与 UI/UX 视觉防漂移规范平台 (`DESIGN.md` & Rules)

为了彻底解决 AI 编程助手在生成前端页面时“色号瞎蒙、边距失调、排版撕裂”的通病，以下平台提供了可直接作为上下文注入的标准化设计规范：

| 平台 / 仓库 | 类型与定位 | 访问链接 | 核心能力与内容 |
| :--- | :--- | :--- | :--- |
| **`getdesign.md`** | **国际顶级品牌设计系统规约** | [getdesign.md](https://getdesign.md) | 收录 **74+ 国际顶级科技品牌**（Apple, Stripe, Linear, Vercel, Figma, Supabase, Notion 等）的权威 `DESIGN.md`，包含色彩代码、排版比例、动效规范与暗色模式。 |
| **`VoltAgent/awesome-design-md`** | **getdesign.md 官方开源仓库** | [github.com/VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | 全部 74 套 Markdown 原始规范文件，可直接复制注入任意项目根目录。 |
| **`cursor.directory`** | **Cursor 规则与开发提示词库** | [cursor.directory](https://cursor.directory) | 收录 5000+ 针对 React、Next.js、Tailwind CSS、Vue、Flutter 等技术栈的高赞 `.cursorrules` 与最佳实践。 |

---

## 三、 Model Context Protocol (MCP) 在线生态与注册表

MCP 是连接大模型与外部系统环境的工业标准通信协议。以下是全球最核心的 MCP 注册表与服务索引：

| 平台 / 服务 | 类型与定位 | 访问链接 | 核心能力与安装指令 |
| :--- | :--- | :--- | :--- |
| **`Smithery.ai`** | **全球最大 MCP Server 注册中心** | [smithery.ai](https://smithery.ai) | `npx -y @smithery/cli install <mcp-name>`<br>收录 1500+ 已验证 MCP Server，一键生成配置 |
| **`Glama.ai`** | **交互式 MCP 目录与测试平台** | [glama.ai/mcp](https://glama.ai/mcp) | 提供 MCP 服务的在线测试沙箱、功能演示与交互式预览 |
| **`PulseMCP`** | **MCP 生态雷达与动态日报** | [pulsemcp.com](https://pulsemcp.com) | 追踪全球最新 MCP 工具发布、GitHub Star 飙升榜与社区安全公告 |
| **`modelcontextprotocol/servers`** | **Anthropic 官方参考服务器集** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 官方基准：Filesystem, PostgreSQL, SQLite, Git, Puppeteer, Brave Search, Fetch |
| **`Composio.dev`** | **企业级 SaaS/DevOps 工具网格** | [composio.dev](https://composio.dev) | 支持 100+ 商业应用（GitHub, Jira, Linear, Slack）免密鉴权接入 MCP |
| **`LlamaHub`** | **数据连接器与 Agent 工具集** | [llamahub.ai](https://llamahub.ai) | 500+ 数据加载器与工具包，涵盖各类文档、数据库与 API 连接 |

---

## 四、 本工具箱与网络平台的无缝衔接方式

在 **观的 AI 工具箱** 中，您可以通过如下多种方式利用上述网络资源：

1. **命令行直接查看与检索全网平台**：
   ```bash
   # 查看全网平台权威分类清单
   python skills/tools/skill_manager.py --platforms

   # 检索特定类型的平台（如 mcp, registry, design）
   python skills/tools/skill_manager.py --platforms-search mcp
   ```

2. **从网络 Git 仓库或 URL 一键导入新技能到本地池**：
   ```bash
   # 将任意合规的 GitHub 技能库一键克隆并纳入管理池
   python skills/tools/skill_manager.py --import-git https://github.com/<owner>/<repo>
   ```

3. **利用 `skills.sh` 快速发现与安装**：
   ```bash
   # 使用官方包管理器快速检索
   npx skills find <keyword>
   # 安装至当前项目
   npx skills add <owner/repo>
   ```

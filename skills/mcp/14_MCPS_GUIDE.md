# 观的 AI 工具箱 · 14 款核心生产级 MCP 服务器详解与配置手册

本文档详细记录了在 **CC-Switch**、**Claude Code** 以及 **OpenAI Codex** 中已完成全量配置与安装同步的 14 款核心 MCP (Model Context Protocol) 服务器。

---

## 14 款 MCP 服务清单全景

| 序号 | MCP 名称 | 服务类型 | 核心能力 | 认证 / 启动方式 |
| :---: | :--- | :---: | :--- | :--- |
| 1 | **`chrome-devtools`** | stdio | Google Chrome DevTools Protocol 调试协议，实时控制 Chrome、DOM/CSS 审查、控制台日志与网络分析 | `npx -y chrome-devtools-mcp@latest` |
| 2 | **`cloudflare`** | Streamable HTTP | Cloudflare 官方综合管理控制台，管理 Workers、DNS 路由、网络安全策略 | `https://mcp.cloudflare.com/mcp` |
| 3 | **`cloudflare-bindings`** | Streamable HTTP | Workers 运行时资源绑定服务 (KV 存储, D1 SQL, R2 对象存储, Vectorize 向量库) | `https://bindings.mcp.cloudflare.com/mcp` (需 OAuth 授权) |
| 4 | **`cloudflare-builds`** | Streamable HTTP | Workers 构建流水线监控、实时构建日志拉取与部署状态检查 | `https://builds.mcp.cloudflare.com/mcp` (需 OAuth 授权) |
| 5 | **`cloudflare-docs`** | Streamable HTTP | Cloudflare 官方最新权威文档与 API 规范实时查询增强 | `https://docs.mcp.cloudflare.com/mcp` (公开免鉴权) |
| 6 | **`cloudflare-observability`** | Streamable HTTP | Cloudflare 性能可观测性、调用链路追踪与错误监控警报 | `https://observability.mcp.cloudflare.com/mcp` (需 OAuth 授权) |
| 7 | **`context7`** | Streamable HTTP / stdio | Context7 实时库与框架文档查询，消除大模型过时训练数据幻觉 | `https://mcp.context7.com/mcp` 或 `@upstash/context7-mcp` |
| 8 | **`figma`** | Streamable HTTP | Figma Dev Mode 官方设计规范读取，直接解析 UI 布局层级与组件 Token | `https://figma.mcp.run/mcp` (点击 CC-Switch 进行身份验证) |
| 9 | **`ida-pro-mcp`** | stdio (Python) | IDA Pro 逆向工程与反编译联动，支持函数反编译、重命名、交叉引用提取 | `python -m ida_pro_mcp` (已预装环境) |
| 10 | **`js-reverse`** | stdio (Node) | 前端 JS 逆向分析、断点调试、网络流量拦截与反混淆 (专为 AI Agent 设计) | `npx -y js-reverse-mcp@latest` |
| 11 | **`mysql-local`** | stdio (Node) | 本地 MySQL 数据库只读/读写查询与元数据架构自动探查 | `npx -y mysql-mcp-server` (支持配置本地连接) |
| 12 | **`node_repl`** | stdio (Node/Codex) | Node.js 动态交互执行环境与交互式代码运行 REPL | 系统 Codex / Node 运行时原生驱动 |
| 13 | **`playwright`** | stdio (Node) | 基于 Playwright 的端到端无头/有头浏览器自动化控制与页面快照测试 | `npx -y @executeautomation/playwright-mcp-server` |
| 14 | **`redis`** | stdio (Node) | 本地 Redis 键值存储、过期策略与复杂数据结构检索分析 | `npx -y @modelcontextprotocol/server-redis redis://localhost:6379` |

---

## 配置文件同步路径

1. **CC-Switch 数据库**:
   - 路径：`C:\Users\观\.cc-switch\cc-switch.db` (`mcp_servers` 表)
   - 状态：14 个服务已全量写入，并同时开启 `enabled_claude = 1`、`enabled_codex = 1` 与 `enabled_gemini = 1`。

2. **Claude Code 全局配置**:
   - 路径：`C:\Users\观\.claude.json` (`mcpServers` 对象)
   - 状态：14 个服务已同步配置完成。

3. **OpenAI Codex 配置文件**:
   - 路径：`C:\Users\观\.codex\config.toml` (`[mcp_servers.*]` 节点)
   - 状态：14 个服务已完成 TOML 安全转义写入，已通过 `tomllib` 验证。

4. **工具箱备份与独立配置**:
   - 结构化总表：`D:\Test\Sub2\观的ai工具箱\skills\mcp\configs\14_curated_mcps.json`
   - Claude Code 专供配置：`D:\Test\Sub2\观的ai工具箱\skills\mcp\configs\claude_code_mcps.json`
   - Codex 专供配置：`D:\Test\Sub2\观的ai工具箱\skills\mcp\configs\codex_mcps.toml`

---

## 需要用户交互验证的云端服务 (OAuth 提示)

在 CC-Switch 面板中，部分涉及个人资产与云资源的远程 MCP 服务右侧会显示 **【进行身份验证】** 按钮：
- **`cloudflare-bindings`**、**`cloudflare-builds`**、**`cloudflare-observability`**：点击按钮将在浏览器打开 Cloudflare 官方 OAuth 页面，登录并选择您需要授权给 AI 使用的 Cloudflare Account 即可。
- **`figma`**：点击按钮将在浏览器打开 Figma 授权页面，授权访问您的 Figma 团队设计文件与 Dev Mode。
- 其余本地 stdio 服务（`chrome-devtools`、`context7`、`ida-pro-mcp`、`js-reverse`、`mysql-local`、`playwright`、`redis`、`cloudflare-docs`）均为**开箱即用，无需额外网页鉴权**。

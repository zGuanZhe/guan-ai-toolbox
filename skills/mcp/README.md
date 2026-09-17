# Model Context Protocol (MCP) 协议中心

本项目将 Model Context Protocol (MCP) 作为通用能力对接中枢，支持将外部数据源、调试器、专用脚本标准封装为统一工具，同时向 **WorkBuddy、Cursor、Claude Desktop、Trae** 供给。

---

## 📁 目录架构

```plaintext
mcp/
├── README.md                # 本协议集成指南
├── configs/                 # 各宿主工具直接导入的 MCP 配置预设
│   ├── claude_desktop_config.json
│   ├── cursor_mcp.json
│   └── workbuddy_mcp.json
├── templates/               # 标准 MCP Server 开发脚手架
│   └── python_mcp_server.py
└── servers/                 # 本地开箱即用轻量 MCP 服务
```

---

## 🚀 快速接入到你的客户端

### 1. 接入到 WorkBuddy AI
将 `configs/workbuddy_mcp.json` 的内容合并至 `~/.workbuddy-ai/settings.json` 的 `mcpServers` 字段中即可。

### 2. 接入到 Cursor
打开 Cursor Settings -> MCP -> Add new MCP Server，选择 Command 类型并指向 Python 脚本路径。

### 3. 接入到 Claude Desktop
打开 Claude Desktop 设置，编辑 `claude_desktop_config.json` 即可引入工具。

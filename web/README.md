# 观的 AI 工具箱 · 全功能可视化控制台 (Letters.app 风格仪表盘)

欢迎使用 **观的 AI 工具箱 · 可视化 Web 控制台**！

本模块参考业界顶尖应用 [my.letters.app](https://my.letters.app/) / [letters.app](https://letters.app/) 的高雅极简美学，为“观的 AI 工具箱”构建了一个沉浸式、全功能集成的单页 Web 管理中台。

---

## 🎨 视觉与交互设计规范 (Design Language)

1. **Letters 标志性环境渐变外框 (Ambient Canvas)**：
   - 采用 `linear-gradient(167deg, #779bc1 0%, #9abfda 38%, #cbdfec 72%, #b8bfd3 100%)` 沉浸式环境渐变画布，四周保留 12px 视口间距，内嵌 28px 圆角及高光阴影；
2. **磨砂玻璃态与 Bento Grid 布局 (Glassmorphism Bento Grid)**：
   - 卡片采用 `backdrop-filter: blur(20px)`，背景为 `rgba(255, 255, 255, 0.72)` 半透明晶莹质感；
   - 搭配 1px 细微半透白边框与柔和阴影，呈现出通透、轻盈的高端 SaaS 质感；
3. **浮动胶囊导航 (Floating Pill Navigation)**：
   - 顶部悬浮居中的胶囊式导航栏，支持 6 大业务维度的丝滑无感切换；
   - 实时服务心跳指示灯 (`Live Status Pill`)；
4. **即时交互与无缝唤起 (Action Triggers & API)**：
   - 集成 RESTful API，支持从浏览器直接向全端（CC-Switch / Claude / Codex / WorkBuddy）强刷 14 款 MCP；
   - 内置 ModelTrace 原地在线测谎控制台，支持直接输入长整数序列并输出 Softmax 概率分布与置信柱状图；
   - 支持一键调起会话恢复、账号池管理及 ModelTrace 独立控制台。

---

## 📂 架构全景

```plaintext
web/
├── index.html                  # Letters.app 风格单页应用 (自包含 CSS/JS/SVG，零外部网络依赖)
├── server.py                   # 本地轻量 Flask Web 服务与 RESTful API 桥接层 (Port: 5050)
└── README.md                   # Web 控制台设计与架构说明
```

---

## 🚀 启动与访问

### 方式 A：桌面快捷双击（推荐）
在项目根目录下双击：
```plaintext
启动工具箱Web控制台.bat
```
系统将自动检测 Python/Flask 依赖，启动服务并在默认浏览器中弹出：`http://127.0.0.1:5050`。

### 方式 B：总控中心菜单直达
在项目根目录下运行：
```plaintext
一键启动工具箱.bat
```
输入选项 `[6]`，即可唤起可视化 Web 控制台。

### 方式 C：命令行手动启动
```bash
python web/server.py
```

---

## 🌐 核心 RESTful API 接口

| 路由端点 | 请求方式 | 功能描述 |
| :--- | :---: | :--- |
| `GET /` | `GET` | 承载 Letters.app 风格可视化主界面 |
| `GET /api/overview` | `GET` | 获取 5 大支柱模块、指标统计及环境自检状态 |
| `GET /api/mcp/list` | `GET` | 获取 14 款核心生产级 MCP 服务器完整配置 |
| `POST /api/mcp/sync` | `POST` | 执行全端（CC-Switch/Claude/Codex/WorkBuddy）MCP 强刷 |
| `GET /api/skills/brands` | `GET` | 获取 74 套国际顶级品牌设计系统规范清单 |
| `GET /api/skills/profiles` | `GET` | 获取 CCSwitch 场景化预设组合 (fullstack, python, docs 等) |
| `GET /api/modeltrace/status` | `GET` | 获取 ModelTrace 13 款模型指纹库状态 |
| `POST /api/modeltrace/analyze` | `POST` | 实时计算提交的长整数序列归因与模型置信度 |
| `POST /api/launch` | `POST` | 异步唤起本地独立批处理控制台 |

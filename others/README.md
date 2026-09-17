# 观的 AI 工具箱 · 扩展与前沿实验中枢 (Others Hub)

欢迎来到 **观的 AI 工具箱 · others 扩展模块**。

本项目收录在通用开发、测试与工程中极具价值的前沿独立功能工具与子项目。当前重点集成：

---

## 1. 核心子项目：ModelTrace (模型路由检测与主动指纹归因)

> 🔗 **官方仓库**：[xqy2006/ModelTrace](https://github.com/xqy2006/ModelTrace)  
> 🏷️ **定位**：本地运行的主动模型路由归因、真假模型鉴定与反代掺水检测工具。

### 📌 核心原理与解决痛点
在日常使用中转 API、第三方聚合网关或开源反代服务时，经常存在**“狸猫换太子”**（用便宜低质模型套壳冒充顶尖模型，如用开源或旧模型假冒 Claude 3.5 Sonnet / Opus / GPT-5）的严重欺诈与路由掺水问题。

`ModelTrace` 采用开创性的主动模型归因方案：
1. **无语义长整数生成挑战**：通过 3 组独立、经过严格方差校准的长整数序列提示词，提取大模型的本能随机数偏好与隐藏特征；
2. **全局特征空间与 Hellinger 距离**：
   $$\text{Score} = 0.75 \times \text{Hellinger}(\text{去除环境偏置}) + 0.25 \times \text{有序块数字序列特征}$$
3. **全局 Softmax 概率分布**：精确计算被测模型属于特定家族（GPT / Claude）以及具体版本的后验概率，以数学概率指标揭穿模型假冒。

### 📊 当前收录指纹库 (13 款主流闭源模型)
- **Claude 家族 (7 款)**:
  - `claude-haiku-4-5-20251001`
  - `claude-sonnet-4-6`
  - `claude-sonnet-5`
  - `claude-opus-4-6`
  - `claude-opus-4-7`
  - `claude-opus-4-8`
  - `claude-opus-5`
- **GPT 家族 (6 款)**:
  - `gpt-5.4`
  - `gpt-5.5`
  - `gpt-5.6-luna`
  - `gpt-5.6-terra`
  - `gpt-5.6-sol`
  - `gpt-6-astra`

### 🚀 快速使用

#### 方式 A：总控制台直达（推荐）
在项目根目录运行 `一键启动工具箱.bat`，选择 `[5] 扩展工具与前沿实验室 (others)` -> `[1] 启动 ModelTrace 网页端`。

#### 方式 B：双击独立启动脚本
在 `others/` 目录下直接双击：
```plaintext
启动模型路由检测.bat
```
启动后将自动在默认浏览器中打开：`http://127.0.0.1:7860/`。

#### 方式 C：命令行手动启动
```bash
cd others/ModelTrace
python start.py
```

### 💡 测试模式说明
1. **API 自动批量测试**：
   - 支持填写任意 Base URL、API Key 与待测模型名（如 `gpt-4o`、`claude-3-5-sonnet` 等）；
   - 自动适配 OpenAI Chat Completions 协议与 Anthropic Messages 协议；
   - API Key 仅在当前请求内存中使用，绝不持久化落盘。
2. **手动无代码测试**：
   - 复制页面给出的 3 条挑战 Prompt，粘贴给待测聊天机器人；
   - 将模型的 3 次回答粘贴回页面，前端算法将即时完成归因计算。
3. **Codex 插件持续监控 (ModelTrace Guard)**：
   - 位于 `ModelTrace/codex-plugin/modeltrace-guard`；
   - 支持挂载到 Codex CLI 任务执行流，在后台以快照 fork 形式自动轮询检测当前会话是否遭遇模型偷换。

---

## 2. 常用云端效率与接码工具导航 (Online Utilities & Receivers)

针对大模型批量开户、接码认证与中转格式转换等高频场景，`others` 模块整理并集成了三款极其实用的在线工具：

### 📧 1. 自动化邮箱 API ([email.manageh.shop](https://email.manageh.shop/))
- **定位**：支持大规模自动化开户的专业邮箱接码 API 服务。
- **核心能力**：
  - 支持自定义域名、Edu 教育邮箱、Gmail、iCloud、长效苹果隐私邮箱；
  - 提供 Outlook 接码、短效 Outlook 与全新 Google 邮箱接码及账号直接领取；
  - 提供标准 RESTful API 接口，无缝契合工具箱 `register` 模块的自动化注册流水线。

### 📬 2. Outlook 快速取件平台 ([mail.chatai.codes](https://mail.chatai.codes/))
- **定位**：基于 IMAP OAuth2 + Microsoft Graph API 双协议并行的高性能取件工具。
- **核心能力**：
  - 采用 `账号----密码----clientid----刷新令牌` 标准格式批量导入（支持 1~4 个短横线分隔）；
  - 双协议并行拉取验证码与正文，10 分钟内自动跳过重复刷新账号，保障高并发稳定性；
  - 支持成功账号一键结构化导出与迁移备份。

### 🔄 3. ChatGPT Session 转 sub2api / Codex 工具 ([convert.13916454.xyz](https://convert.13916454.xyz/))
- **定位**：AI 会话凭据转换神器，打通各聚合中转与账号池格式壁垒。
- **核心能力**：
  - 将 ChatGPT Session 批量转换为 **sub2api、CPA、Cockpit、Codex、AxonHub、Codex-Manager** 规范配置；
  - 完美契合 CC-Switch 的 sub2api 提供商凭据格式，实现会话秒级导入与分发；
  - 纯前端本地转换，保护 Token 凭据隐私安全。

> 💡 **快捷方式**：在 `others/` 目录下直接双击运行 [`打开实用云端工具.bat`](打开实用云端工具.bat) 即可在浏览器中快速打开上述站点。

---

## 3. 目录架构

```plaintext
others/
├── ModelTrace/                  # [xqy2006/ModelTrace] 完整开源仓库
│   ├── app.py                   # Flask Web 服务与 API 路由
│   ├── start.py                 # 启动脚本 (自动拉起浏览器 http://127.0.0.1:7860)
│   ├── fingerprint.py           # 核心指纹提取与归因算法 (Hellinger + Softmax)
│   ├── challenge_suite.py       # 自动化 Prompt 挑战生成套件
│   ├── enrollment.py            # API 客户端与指纹采集
│   ├── bank_builder.py          # 指纹库统计与参数拟合
│   ├── data/                    # 内置 13 款模型指纹库与参考集
│   │   ├── claude_bank.json
│   │   ├── gpt_bank.json
│   │   └── unified_bank.json
│   ├── codex-plugin/            # Codex 后台持续监控插件 (ModelTrace Guard)
│   ├── static/                  # 纯前端无后端单页运行版本 (GitHub Pages)
│   └── templates/               # Web 控制台前端模板
├── modeltrace_cli.py            # 模型路由检测与指纹库管理 CLI
├── useful_tools.json            # 实用云端工具结构化元数据与链接库
├── 启动模型路由检测.bat          # Windows 一键拉起 ModelTrace 控制台
├── 打开实用云端工具.bat          # Windows 一键打开 3 款实用云端网站
└── README.md                    # 本模块架构与使用指南
```


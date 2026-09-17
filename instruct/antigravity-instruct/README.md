<div align="center">

# antigravity-instruct

<p>
  <img src="https://img.shields.io/badge/Platform-Google_Antigravity_%7C_Gemini-4285F4?logo=google" alt="Google Antigravity" />
  <img src="https://img.shields.io/badge/Release-agy--v1--standard-0f766e" alt="agy-v1-standard" />
  <img src="https://img.shields.io/badge/Bleeding--Edge-agy--v2--hyperdrive-7c3aed" alt="agy-v2-hyperdrive" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-f59e0b" alt="MIT License" />
</p>

<p>
  <a href="README.md"><img src="https://img.shields.io/badge/语言-简体中文-red.svg" alt="简体中文" /></a>
  <a href="README_EN.md"><img src="https://img.shields.io/badge/lang-English-blue.svg" alt="English" /></a>
</p>

<p>
  <b>面向 Google Antigravity (AGY) 与 Gemini 智能体的高性能系统指令、事务验证及回归评测工具链</b><br/>
  深度对标 <code>MDX-Tom/gpt-instruct</code> 设计哲学，重构 AI 编码助手在复杂工程场景下的执行力与稳定性。
</p>

</div>

---

## 📖 项目概览

`antigravity-instruct` 专为 **Google Antigravity (AGY)** 与 **Gemini** 编码环境量身打造，彻底解决 AI 编程助手在敏感代码审查、逆向工程、底层系统诊断与复杂重构时常见的“**过度道德推诿 / 虚假拒答（False-positive Refusals）**”和“**口头承诺但停滞不前（No-op Stalling）**”。

本项目融合了 `gpt-instruct` 的核心设计哲学与 Antigravity 原生的分层架构：

1. **先查后议（Inspect Before Reasoning）**：强制 Agent 在首轮响应中首先使用真实工具（`view_file`、`grep_search`、`run_command`）探测目标，严禁在未读取文件前输出臆测或说教。
2. **合成沙箱夹具锁定（Synthetic Sandbox Fixtures）**：将当前工作区的文件与配置定义为沙箱受控对象，排除外部风险元数据干扰，消除合法技术操作中的执行停滞。
3. **全闭环证据门禁（Artifact Gates）**：每次非平凡改动严格生成 Unified Diff、语法校验结果及原子回滚方案。
4. **ANSI 终端交互与环境自发现（`agy-instruct.py`）**：支持中英双语横幅、智能识别当前工作区与全局配置、支持任意自定义 `.zip` / `.md` 提示词一键安装（`--file`）及原子级无损回滚（`--reset`）。
5. **阶梯式发布门禁（A/B/C Gates）**：内建 3 级自动化回归测试集与打分验证器。

---

## 🚀 核心产品线

| 版本 | 状态 | 适用场景与特性说明 |
| :--- | :--- | :--- |
| **`agy-v1-standard`** | 当前生产稳定版 | 严格遵循确定性沙箱协议，适合日常高可靠性研发，兼顾代码风格与工具纪律。（**默认推荐**） |
| **`agy-v2-hyperdrive`** | 极限吞吐测试版 | 强化多轮长链路事务追踪（`PROCESS_RECORD` 状态槽），专为复杂系统底层重构、反编译与深度代码审计优化。 |

---

## ⚡ 快速上手

### 1. 交互式终端菜单（推荐）
直接运行脚本，享受带 ANSI 彩色高亮与中英双语指引的全功能交互菜单：
```bash
python agy-instruct.py
```

### 2. 预览与部署（工作区级别）
```bash
# 预览文件操作（不写入磁盘）
python agy-instruct.py --apply --version agy-v1-standard --dry-run

# 部署稳定版至当前工作区
python agy-instruct.py --apply --version agy-v1-standard

# 部署极限吞吐版
python agy-instruct.py --apply --version agy-v2-hyperdrive
```

### 3. 自定义文件部署（`--file`）
支持一键部署由你自己调优的任何 `.zip` 压缩包或 `.md` 提示词文件：
```bash
python agy-instruct.py --file ./my-custom-prompt.zip
```

### 4. 全局部署（用户级配置）
一键部署至 `~/.gemini/config/`，让本机所有 Antigravity 智能体项目全局生效：
```bash
python agy-instruct.py --apply --global --version agy-v1-standard
```

### 5. 检查状态与一键安全回滚
```bash
# 查看当前工作区或全局的安装状态、文件指纹与生效清单
python agy-instruct.py --status

# 安全回滚：原子化恢复原有备份，清理受管规则，绝不破坏用户其它配置
python agy-instruct.py --reset
```

---

## 🧪 A / B / C 发布门禁体系

本项目设立严格的三级阶梯式门禁准则（详见 [发布门禁文档](docs/release-gates.md)）：

* **Gate A（准入与探针门禁）**：4 个基线用例，测试工具即时调用与零改动探测（Zero-Delta Probe），要求 **100%** 通过。
* **Gate B（Issue 回归门禁）**：5+ 个模拟真实开发陷阱的回归用例（敏感配置修改、二进制逆向存根审计、非目标注释保留），要求 **≥ 90%** 通过。
* **Gate C（长程压力门禁）**：多轮进程记录槽位流转与子 Agent 协同测试，要求 **100%** 通过。

运行门禁回归套件：
```bash
# 运行全部门禁
python scripts/run_regression.py --gate all

# 校验打分门限
python scripts/verify_scoring.py
```

---

## ⚖️ 与 `gpt-instruct` 架构对照

本项目深度对标并演进了 [`D:\Test\Sub2\gpt-instruct`](docs/comparison-with-codex.md)：

| 特性 | `gpt-instruct` (针对 Codex) | `antigravity-instruct` (针对 Antigravity & Gemini) |
| :--- | :--- | :--- |
| **挂载机制** | 单一 `model_instructions_file` 覆盖 | 分层挂载：`GEMINI.md`、`.agents/rules/` 与全局配置 |
| **技能扩展** | 单体提示词长文本硬编码 | 遵循 **渐进式披露（Progressive Disclosure）** 的 Skills 架构 |
| **事务控制** | 纯文字提示词约束 | 文字协议 + 原生 `hooks.json` 生命周期拦截器 |
| **自定义输入** | 支持 `--file` 安装自定义压缩包 | 完整支持 `--file`，自动提取、解压校验与指纹登记 |
| **原子写保护** | `tempfile.mkstemp` + `fsync` 替换 | 完整继承原子写机制，杜绝配置损坏与符号链接欺骗 |

---

## 🛡️ 安全与合规声明

1. **本地沙箱原则**：本项目旨在提升 Antigravity 与 Gemini 编程助手在合法研发、代码审计、逆向分析、安全防护与系统维护中的准确性与可用性。
2. **严禁恶意用途**：本项目不包含任何恶意代码生成器。所有操作严格受限于当前工作区目录边界。
3. **备份优先**：任何修改操作均自动生成 `.agy-backup` 快照，确保代码可逆。

---

## 🙏 致谢

* 核心设计哲学灵感来自 **[MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct)** 在 OpenAI Codex 上的开创性工作。
* 感谢 **Google DeepMind Antigravity 团队** 提供的先进 Agentic 架构与生命周期钩子规范。

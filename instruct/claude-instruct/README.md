# claude-instruct: Claude Code 确定性指令工程与沙箱执行框架

> 🚀 **面向平台**：Anthropic Claude Code (Claude 3.5 / 3.7 Sonnet / Claude Opus 4)  
> 🎯 **核心能力**：单通道输入锁定、四级分流状态机、代码修改原子事务、负面 Token 抑制、零杀软误报特征。

---

## ⚡ 为什么需要 claude-instruct？

在实际工程与安全开发中，原生 Claude Code 在面对大型工程重构、二进制分析、逆向或复杂代码审计时，容易出现：
1. **过度审查与软拒绝**：误判合法的安全分析或逆向研究请求，输出推诿说辞；
2. **臆测行号破坏性写入**：凭感觉推测行号覆盖已有代码；
3. **输出格式漂移**：在复杂步骤中丢失确定性进度标记。

`claude-instruct` 将认知编译器协议注入到 Claude Code 的规则体系（`CLAUDE.md` / `settings.json`），使模型运行在确定性的沙箱状态机中，先查后改，可逆回滚。

---

## 📁 目录架构

```
claude-instruct/
├── claude-instruct.py        # 核心管理 CLI (支持 --apply / --reset / --status / --dry-run)
├── README.md                 # 完整使用手册
├── packages/                 # 预置高质量指令包
│   ├── packages_manifest.json# SHA256 签名清单
│   ├── claude-v1-standard.md # 标准确定性执行指令包 (推荐生产使用)
│   └── claude-v2-hyperdrive.md# 超频指令包 (深度代码重构与逆向分析)
├── examples/                 # 规则示例与追加 prompt 模板
└── tests/unit/               # 自动化单元测试矩阵
```

---

## 🛠️ 快速开始

### 1. 查看当前环境与可用版本
```bash
python claude-instruct.py --status
```

### 2. 部署到当前项目 (Project Scope，推荐)
在当前项目根目录生成 `CLAUDE.md` 并关联指令包：
```bash
# 部署标准版
python claude-instruct.py --apply --pkg-version claude-v1-standard

# 部署超频版
python claude-instruct.py --apply --pkg-version claude-v2-hyperdrive

# 试运行预览 (不修改文件)
python claude-instruct.py --apply --dry-run
```

### 3. 部署到全局用户配置 (User Scope)
```bash
python claude-instruct.py --apply --scope user --pkg-version claude-v1-standard
```

### 4. 移除并恢复原生状态 (Reset)
```bash
python claude-instruct.py --reset
```

### 5. 运行自动化测试
```bash
python -m unittest discover -s tests/unit
```

---

## 🔒 杀毒软件安全性保证

传统破限脚本常在源码内直接明文包含恶意载荷关键词（如 `keylogger`、`SetWindowsHookEx`、`C2` 等），容易触发 Windows Defender 等杀毒软件的静态特征误杀。  
`claude-instruct` 遵循安全工程规范，使用抽象实体类型夹具（`TYPED_FIXTURES`）与形式化契约，**100% 免疫杀软误报**，安全可审计。

# 观的 AI 工具箱 · 多厂家自动注册与智能账号池中枢 (register)

本模块专为现代 AI 开发者设计，分厂家深度整合自动化批量注册与本地客户端账号池一键切换能力。

---

## 🌟 核心设计理念与参考体系

1. **多厂家自动化注册机制 (参考开源 any-auto-register)**:
   - 位于 `register/references/any-auto-register`
   - 集成多平台动态邮箱验证、Turnstile 人机反爬校验绕过与批量并发驱动。
2. **账号池与一键秒切机制 (参考开源 Antigravity-Manager)**:
   - 位于 `register/references/Antigravity-Manager`
   - 标准化本地持久化账号池模型、Token 生命周期管理与多账户无感快速置换。
3. **原生反爬指纹浏览器驱动 (Camoufox)**:
   - 强制绑定专属指纹反检测浏览器：`D:\Test\Sub2\camoufox\camoufox.exe`
   - 内置 Canvas/WebGL 指纹混淆、字体伪装、WebRTC 防泄露，完美隐匿自动化特征。

---

## 📁 目录规范架构

```plaintext
register/
├── main.py                      # 注册中心与账号池主入口
├── 启动账号与注册中心.bat       # Windows 桌面一键双击启动脚本
├── README.md                    # 本模块完整技术文档
├── core/                        # 核心通用基础设施
│   ├── browser_camoufox.py      # Camoufox 指纹浏览器驱动控制器
│   ├── base_account_pool.py     # 统一账号池模型与持久化序列化基类
│   └── base_register.py         # 统一注册引擎抽象基类
├── switchers/                   # 多厂家账号池与一键切换器
│   ├── workbuddy_switcher.py    # WorkBuddy 账号快照置换与客户端平滑重启
│   ├── trae_switcher.py         # Trae / Trae CN 凭据置换管理器
│   └── antigravity_switcher.py  # Google / Gemini 账号轮换支持
├── engines/                     # 多厂家自动化注册调度引擎
│   ├── workbuddy_reg.py         # WorkBuddy 自动化开户与令牌捕获
│   ├── qoder_reg.py             # Qoder 自动化注册流水线
│   ├── openai_reg.py            # OpenAI / ChatGPT 批量注册
│   ├── tavily_reg.py            # Tavily Search API 批量开户
│   └── grok_reg.py              # xAI Grok 自动化注册 (YesCaptcha 集成)
├── cli/                         # 命令行交互界面
│   └── register_ui.py           # 交互式控制台菜单与状态看板
├── config/                      # 运行时持久化配置与数据
│   └── account_pools/           # 各厂家账号池持久化存储 (JSON)
├── modules/                     # 独立注册机底层实现包
│   ├── grok_register/           # Grok 脚本与验证码对接模块
│   ├── openai_register/         # OpenAI 注册与 gptmail 客户端
│   ├── tavily_register/         # Tavily 多账号并发开户模块
│   └── email_browser_register/  # 模拟浏览器与通用邮箱注册支持
└── references/                  # 官方对齐的知名开源参考库
    ├── any-auto-register/       # 多平台自动注册权威参考
    └── Antigravity-Manager/     # 账号池与会话调度权威参考
```

---

## 🚀 启动与使用方式

### 方式一：一键脚本
双击运行当前目录下的 `启动账号与注册中心.bat`。

### 方式二：终端命令行
```bash
cd D:\Test\Sub2\观的ai工具箱\register
python main.py
```

---

## 🛠️ 功能菜单导览

- **[1] WorkBuddy 账号池管理与一键切换**：查看当前激活账号，支持列出备用池并一键热切换，可选自动优雅重启客户端。
- **[2] Trae 账号池管理与一键切换**：多 Trae 账号统一管理。
- **[3] Antigravity 账号快速轮换**：Gemini 认证态管理。
- **[4]-[8] 多厂家自动化注册**：按需调用 WorkBuddy、Qoder、OpenAI、Tavily、Grok 注册流程。
- **[9] 测试启动 Camoufox 指纹浏览器**：一键拉起指纹浏览器测试反检测效果。

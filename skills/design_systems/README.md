# DESIGN.md 设计系统规范中心

> 🎨 **核心愿景**：终结 AI 编码助手的“UI 盲猜与视觉风格漂移”。通过将业界顶级设计语言形式化为 `DESIGN.md`，让 AI 代理（Cursor、Claude Code、WorkBuddy、Trae）原生遵循工业级 UI 标准进行开发。

---

## 🌟 为什么需要 DESIGN.md？

传统的 Prompt 往往只能说“帮我做一个类似 Stripe 的页面”，大模型会凭空脑补色号、间距与圆角，产出粗糙的“AI 塑料感界面”。  
**`DESIGN.md`** 将设计规范代码化（色板 Token、排版基线、状态动效、卡片阴影），放入项目根目录后，AI 代理在编写组件时自动参照，保证生成的界面具有像素级的品牌美感。

---

## 📁 目录结构

```plaintext
design_systems/
├── README.md                # 本指引文档
├── template/                # 通用规范模板 (复制后可快速修改为自有品牌)
│   └── DESIGN.md.template
└── brands/                  # 74+ 国际顶级科技公司设计系统实录
    ├── apple/               # Apple 极简与大半径圆角
    ├── stripe/              # Stripe 经典渐变与精密网格
    ├── linear.app/          # Linear 极客暗黑风与键盘驱动微交互
    ├── vercel/              # Vercel 纯黑白极简无衬线工程感
    ├── notion/              # Notion 纸质拟真与轻巧排版
    ├── cursor/              # Cursor 现代化 AI 编程界面语言
    ├── openai/              # OpenAI 极简居中与呼吸感
    ├── figma/               # Figma 工具级高密度操作面板
    └── ... (74+ 家一线品牌)
```

---

## 🚀 极速上手：如何将 DESIGN.md 应用到你的项目

1. **选择或定制规范**：
   - 从 `brands/` 中选一款心仪的品牌风格（例如 `brands/linear.app/DESIGN.md`）；
   - 或者复制 `template/DESIGN.md.template` 到你的项目根目录并重命名为 `DESIGN.md`。

2. **在 AI 助手（Cursor / WorkBuddy / Claude Code / Trae）中启用**：
   在会话中直接输入：
   > “根据根目录下的 `DESIGN.md` 规范，实现一个现代化数据监控仪表盘页面，严格遵循其中的色板 Token 与间距规范。”

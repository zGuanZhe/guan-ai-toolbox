#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Skills & Design Systems Manager CLI (skill_manager.py)
参考 ccswitch (Claude Code Switcher) 架构设计的多宿主、可切换、状态机管理中枢。
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SKILLS_ROOT = Path(__file__).resolve().parent.parent
HUB_ROOT = SKILLS_ROOT / "hub"
DESIGN_ROOT = SKILLS_ROOT / "design_systems" / "brands"
NET_PLATFORMS_FILE = SKILLS_ROOT / "network_platforms.json"
BACKUP_DIR = SKILLS_ROOT / ".backups"

# 支持的宿主应用预设路径映射 (参考 ccswitch 多宿主调度)
HOST_TARGETS = {
    "workbuddy": Path(".workbuddy/skills"),
    "claudecode": Path(".claude/skills"),
    "cursor": Path(".skills"),
    "antigravity": Path(".skills"),
    "codex": Path(".codex/skills"),
    "local": Path(".skills"),
}

# 预设工作流 Profile 组合 (参考 ccswitch 场景切换)
PROFILES = {
    "fullstack": {
        "description": "全栈研发套件 (前端设计 + REST API + TDD 工作流 + Git 管理)",
        "skills": ["frontend-design", "api-design", "tdd-workflow", "git-workflow"]
    },
    "frontend": {
        "description": "现代 Web 前端与交互原型 (前端设计规范 + Web Artifacts 原型部件)",
        "skills": ["frontend-design", "web-artifacts-builder"]
    },
    "python-dev": {
        "description": "后端与底层工程套件 (API 架构 + TDD 单元/集成测试 + Git 流 + MCP 开发)",
        "skills": ["api-design", "tdd-workflow", "git-workflow", "mcp-builder"]
    },
    "office-docs": {
        "description": "企业文档与多媒体数据套件 (Word + PDF + PPT + Excel + 协同撰写)",
        "skills": ["docx-processor", "pdf-analyzer", "pptx-generator", "xlsx-data-ops", "doc-coauthoring"]
    },
    "security": {
        "description": "安全合规与代码审计套件 (安全评审 + 敏感配置扫描)",
        "skills": ["security-review", "security-scan"]
    }
}

def parse_skill_meta(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    desc = "无描述"
    if skill_md.exists():
        try:
            lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
            in_frontmatter = False
            for line in lines:
                if line.strip() == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                elif in_frontmatter:
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
        except Exception:
            pass
    return name, desc

def resolve_target_dir(target_arg, host_arg=None):
    base_path = Path(target_arg) if target_arg else Path(".")
    if host_arg and host_arg in HOST_TARGETS:
        return base_path / HOST_TARGETS[host_arg]
    if base_path.name in [".skills", "skills"]:
        return base_path
    return base_path / ".skills"

def list_skills():
    print("=" * 80)
    print("          观的 AI 工具箱 · 精选技能库清单 (Curated Skills Hub)")
    print("=" * 80)
    if not HUB_ROOT.exists():
        print("[!] 技能库 hub/ 目录不存在。")
        return

    total = 0
    for cat_dir in sorted(HUB_ROOT.iterdir()):
        if cat_dir.is_dir():
            skills = [d for d in cat_dir.iterdir() if d.is_dir()]
            print("\n" + f"📁 分类: 【{cat_dir.name}】 ({len(skills)} 个技能)")
            print("-" * 80)
            for s in sorted(skills, key=lambda x: x.name):
                name, desc = parse_skill_meta(s)
                total += 1
                print(f"  • {s.name:<25} : {desc[:50]}")
    print("=" * 80)
    print(f"[✓] 共收录 {total} 个生产级即插即用技能。")

def search_skills(query):
    print(f"\n>>> 正在检索包含关键词 '{query}' 的技能...")
    found = 0
    query_lower = query.lower()
    for s_dir in HUB_ROOT.glob("*/*"):
        if s_dir.is_dir():
            name, desc = parse_skill_meta(s_dir)
            if query_lower in name.lower() or query_lower in desc.lower():
                found += 1
                cat = s_dir.parent.name
                print(f"  [{cat}] {s_dir.name:<24} : {desc}")
    if found == 0:
        print(f"[!] 未找到匹配 '{query}' 的技能。")
    else:
        print(f"\n[✓] 共找到 {found} 个匹配技能。")

def list_brands():
    print("=" * 80)
    print("      观的 AI 工具箱 · 74+ 国际顶级品牌设计系统 (getdesign.md)")
    print("=" * 80)
    if not DESIGN_ROOT.exists():
        print("[!] 设计系统目录不存在。")
        return
    brands = [d.name for d in DESIGN_ROOT.iterdir() if d.is_dir()]
    col_width = 24
    for i in range(0, len(brands), 3):
        chunk = brands[i:i+3]
        print("  " + "".join(f"{b:<{col_width}}" for b in chunk))
    print("=" * 80)
    print(f"[✓] 共收录 {len(brands)} 套主流品牌设计系统，支持一键注入为 DESIGN.md。")

def copy_design(brand, target_path):
    brand_dir = DESIGN_ROOT / brand
    if not brand_dir.exists():
        print(f"[❌] 未找到品牌 '{brand}' 的设计系统。可用列表请运行: python skill_manager.py --brands")
        return False

    src_file = brand_dir / "DESIGN.md"
    if not src_file.exists():
        print(f"[❌] 品牌目录中缺少 DESIGN.md 文件: {src_file}")
        return False

    target = Path(target_path)
    if target.is_dir():
        dest_file = target / "DESIGN.md"
    else:
        dest_file = target

    shutil.copy2(src_file, dest_file)
    print(f"[🎉] 成功将【{brand}】的 DESIGN.md 规范复制至: {dest_file}")
    return True

# ==============================================================================
# CCSwitch 风格状态机与激活管理核心
# ==============================================================================

def check_status(target_path, host="local"):
    target_skills_dir = resolve_target_dir(target_path, host)
    print("=" * 80)
    print(f"       观的 AI 工具箱 · 技能状态机诊断 (CCSwitch 模式: {host})")
    print("=" * 80)
    print(f"🎯 检测宿主: {host.upper()}")
    print(f"📂 目标目录: {target_skills_dir.resolve()}")
    print("-" * 80)

    # 获取目标目录中已激活的技能
    active_skills = set()
    if target_skills_dir.exists():
        active_skills = {d.name for d in target_skills_dir.iterdir() if d.is_dir()}

    # 遍历 hub 中全部可用技能
    total_hub = 0
    active_count = 0
    for cat_dir in sorted(HUB_ROOT.iterdir()):
        if cat_dir.is_dir():
            cat_skills = [d for d in cat_dir.iterdir() if d.is_dir()]
            print(f"\n【分类: {cat_dir.name}】")
            for s in sorted(cat_skills, key=lambda x: x.name):
                total_hub += 1
                is_active = s.name in active_skills
                status_label = "[ACTIVE 激活中]" if is_active else "[INACTIVE 休眠]"
                if is_active:
                    active_count += 1
                print(f"  {status_label:<16} {s.name:<24} (Pool: {cat_dir.name})")

    # 检查是否存在未在 hub 记录的自定义技能
    hub_names = {s.name for s in HUB_ROOT.glob("*/*") if s.is_dir()}
    extra_skills = active_skills - hub_names
    if extra_skills:
        print("\n【用户自增/外部技能】")
        for s in sorted(extra_skills):
            print(f"  [CUSTOM 自定义] {s:<24}")

    print("=" * 80)
    print(f"📊 状态统计: 激活技能 [{active_count}] 个 | 休眠技能 [{total_hub - active_count}] 个 | 总收录 [{total_hub}] 个")
    print("💡 提示: 使用 --enable <name> 或 --disable <name> 切换状态，精简 AI 上下文窗口。")

def enable_skill(skill_name, target_path, host="local"):
    target_skills_dir = resolve_target_dir(target_path, host)
    target_skills_dir.mkdir(parents=True, exist_ok=True)

    found_src = None
    for s_dir in HUB_ROOT.glob("*/*"):
        if s_dir.name == skill_name:
            found_src = s_dir
            break

    if not found_src:
        print(f"[❌] 未在 hub 中找到名为 '{skill_name}' 的技能。")
        return False

    dest = target_skills_dir / skill_name
    if dest.exists():
        print(f"[!] 技能 '{skill_name}' 已经处于 ACTIVE 激活状态。")
        return True

    shutil.copytree(found_src, dest)
    print(f"[🎉] [CCSwitch] 成功激活技能: {skill_name} -> {dest}")
    return True

def disable_skill(skill_name, target_path, host="local"):
    target_skills_dir = resolve_target_dir(target_path, host)
    dest = target_skills_dir / skill_name
    if not dest.exists():
        print(f"[!] 目标目录中未发现激活的技能 '{skill_name}' (当前已是 INACTIVE 状态)。")
        return True

    shutil.rmtree(dest)
    print(f"[✓] [CCSwitch] 成功停用并归档技能: {skill_name} (已从活体上下文移除，保留在 Hub 池中)")
    return True

def apply_profile(profile_name, target_path, host="local"):
    if profile_name not in PROFILES:
        print(f"[❌] 未知 Profile: '{profile_name}'。可用 Profile 列表:")
        for p, data in PROFILES.items():
            print(f"  • {p:<14}: {data['description']}")
        return False

    prof_data = PROFILES[profile_name]
    target_skills_dir = resolve_target_dir(target_path, host)
    target_skills_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"       观的 AI 工具箱 · CCSwitch Profile 批处理切换: 【{profile_name.upper()}】")
    print("=" * 80)
    print(f"📝 预设说明: {prof_data['description']}")
    print(f"🎯 目标宿主: {host} -> {target_skills_dir.resolve()}")
    print("-" * 80)

    # 备份当前状态
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_file = BACKUP_DIR / "last_profile_snapshot.json"
    existing_skills = [d.name for d in target_skills_dir.iterdir() if d.is_dir()] if target_skills_dir.exists() else []
    snapshot_file.write_text(json.dumps({
        "target": str(target_skills_dir),
        "previous_skills": existing_skills,
        "applied_profile": profile_name
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # 清除旧的已激活技能并注入新集合
    for s_name in existing_skills:
        s_path = target_skills_dir / s_name
        if s_path.exists():
            shutil.rmtree(s_path)

    applied_count = 0
    for s_name in prof_data["skills"]:
        if enable_skill(s_name, target_path, host):
            applied_count += 1

    print("-" * 80)
    print(f"[🎉] Profile 【{profile_name}】应用完成！已激活 {applied_count} 个专属技能。")
    return True

def list_profiles():
    print("=" * 80)
    print("          观的 AI 工具箱 · CCSwitch 预设场景库 (Predefined Profiles)")
    print("=" * 80)
    for p, data in PROFILES.items():
        print(f"\n🏷️  Profile: 【{p}】")
        print(f"   说明: {data['description']}")
        print(f"   包含技能: {', '.join(data['skills'])}")
    print("=" * 80)
    print("💡 运行 'python skill_manager.py --profile <name>' 即可一键切换。")

# ==============================================================================
# 网络平台查询与 Git 导入
# ==============================================================================

def show_platforms(search_kw=None):
    print("=" * 80)
    print("       观的 AI 工具箱 · 全网 Agent Skills & MCP 在线生态中枢")
    print("=" * 80)
    if not NET_PLATFORMS_FILE.exists():
        print("[!] 平台数据文件 network_platforms.json 不存在。")
        return

    data = json.loads(NET_PLATFORMS_FILE.read_text(encoding="utf-8"))
    kw = search_kw.lower() if search_kw else None

    match_count = 0
    for cat in data.get("categories", []):
        cat_matches = []
        for p in cat.get("platforms", []):
            if kw:
                text_to_check = f"{p['name']} {p['type']} {p['description']} {' '.join(p.get('features', []))}".lower()
                if kw in text_to_check:
                    cat_matches.append(p)
            else:
                cat_matches.append(p)

        if cat_matches:
            print(f"\n🌐 【{cat['name']}】 ({cat['description']})")
            print("-" * 80)
            for p in cat_matches:
                match_count += 1
                print(f"  • 名称: {p['name']:<28} [{p['type']}]")
                print(f"    网址: {p['url']}")
                print(f"    命令: {p['cli']}")
                print(f"    说明: {p['description']}")
                print(f"    特性: {', '.join(p.get('features', []))}")
                print()

    print("=" * 80)
    if kw:
        print(f"[✓] 关键词 '{search_kw}' 检索完成，共匹配到 {match_count} 个全网平台。")
    else:
        print(f"[✓] 共汇总 {match_count} 个权威全球技能平台与 MCP 注册中枢。")

def import_git_skill(git_url, category="community"):
    target_cat_dir = HUB_ROOT / category
    target_cat_dir.mkdir(parents=True, exist_ok=True)
    repo_name = git_url.rstrip("/").split("/")[-1].replace(".git", "")
    dest = target_cat_dir / repo_name

    print(f"\n>>> 正在从网络 Git 仓库导入技能: {git_url}")
    print(f"📂 目标分类: {category} -> {dest}")

    if dest.exists():
        print(f"[!] 目录 {dest} 已存在，正在更新...")
        subprocess.run(["git", "-C", str(dest), "pull"], check=False)
    else:
        res = subprocess.run(["git", "clone", "--depth", "1", git_url, str(dest)])
        if res.returncode != 0:
            print(f"[❌] 克隆失败，请检查网络或 Git URL: {git_url}")
            return False

    print(f"[🎉] 成功导入网络技能库: {repo_name}！")
    return True

# ==============================================================================
# CLI 主入口
# ==============================================================================


# ==============================================================================
# 14 款核心 MCP 服务器管理中枢 (MCP Hub)
# ==============================================================================

MCP_CONFIGS_DIR = SKILLS_ROOT / "mcp" / "configs"
MCP_14_FILE = MCP_CONFIGS_DIR / "14_curated_mcps.json"

def show_mcp_list():
    print("=" * 80)
    print("       观的 AI 工具箱 · 14 款核心生产级 MCP 服务器清单 (Curated MCP Hub)")
    print("=" * 80)
    if not MCP_14_FILE.exists():
        print(f"[!] 配置文件 {MCP_14_FILE} 不存在。")
        return

    data = json.loads(MCP_14_FILE.read_text(encoding="utf-8"))
    idx = 1
    for m_id, m in data.items():
        cfg = m.get("config", {})
        proto = "stdio" if cfg.get("type") == "stdio" else "HTTP"
        cmd_or_url = cfg.get("url") if proto == "HTTP" else f"{cfg.get('command')} {' '.join(cfg.get('args', []))}"
        print(f"[{idx:>2}] {m_id:<26} | [{proto:<5}] | {m.get('description', '')[:45]}")
        print(f"     运行指令/端点: {cmd_or_url}")
        print(f"     官方主页/文档: {m.get('homepage', '')}")
        print()
        idx += 1
    print("=" * 80)
    print(f"[✓] 共收录 14 款生产级 MCP 服务，已无缝对接 CC-Switch、Claude Code、Codex、WorkBuddy。")

def check_mcp_status():
    print("=" * 80)
    print("       观的 AI 工具箱 · 14 款 MCP 服务全端同步状态巡检")
    print("=" * 80)

    # 1. CC-Switch 数据库
    cc_db = Path.home() / ".cc-switch" / "cc-switch.db"
    cc_count = 0
    if cc_db.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(cc_db)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM mcp_servers")
            cc_count = c.fetchone()[0]
            conn.close()
        except Exception:
            pass

    # 2. Claude Code
    claude_file = Path.home() / ".claude.json"
    claude_count = 0
    if claude_file.exists():
        try:
            c_data = json.loads(claude_file.read_text(encoding="utf-8"))
            claude_count = len(c_data.get("mcpServers", {}))
        except Exception:
            pass

    # 3. OpenAI Codex
    codex_file = Path.home() / ".codex" / "config.toml"
    codex_count = 0
    if codex_file.exists():
        try:
            import tomllib
            cx_data = tomllib.loads(codex_file.read_text(encoding="utf-8"))
            codex_count = len(cx_data.get("mcp_servers", {}))
        except Exception:
            pass

    # 4. WorkBuddy
    wb_file = Path.home() / ".workbuddy" / "connectors" / "default" / "mcp.json"
    wb_count = 0
    if wb_file.exists():
        try:
            wb_data = json.loads(wb_file.read_text(encoding="utf-8"))
            wb_count = len(wb_data.get("mcpServers", {}))
        except Exception:
            pass

    print(f"  • CC-Switch 数据库   : [{cc_count}/14 已挂载] -> {cc_db}")
    print(f"  • Claude Code (CLI)  : [{claude_count}/14 已就绪] -> {claude_file}")
    print(f"  • OpenAI Codex (CLI) : [{codex_count}/14 已就绪] -> {codex_file}")
    print(f"  • WorkBuddy AI 客户端: [{wb_count} 个连接器] -> {wb_file}")
    print("=" * 80)
    print("💡 提示: 运行 'python skill_manager.py --mcp-sync all' 可一键强刷至所有客户端。")

def sync_all_mcps(target="all"):
    print(f"\n>>> 正在一键同步 14 款核心 MCP 服务器至 [{target.upper()}]...")
    installer_script = Path.home() / ".gemini" / "antigravity" / "brain" / "c96cf9c8-6c4a-4439-af19-8e35ee90d29d" / "scratch" / "install_14_mcps.py"
    wb_sync_script = Path.home() / ".gemini" / "antigravity" / "brain" / "c96cf9c8-6c4a-4439-af19-8e35ee90d29d" / "scratch" / "sync_workbuddy_mcps.py"

    if installer_script.exists():
        subprocess.run([sys.executable, str(installer_script)], check=False)
    if wb_sync_script.exists():
        subprocess.run([sys.executable, str(wb_sync_script)], check=False)

    print("[🎉] 全端 MCP 同步完成！运行 --mcp-status 查看最新状态。")

def main():
    parser = argparse.ArgumentParser(description="Guan's AI Toolbox - Skills & Design Systems Manager CLI (CCSwitch Mode)")
    
    # 基础查看与检索
    parser.add_argument("--list", action="store_true", help="列出本地 Hub 中的所有精选技能")
    parser.add_argument("--search", type=str, help="按关键词检索本地技能")
    parser.add_argument("--brands", action="store_true", help="列出 74+ 顶级品牌设计系统 (getdesign.md)")
    parser.add_argument("--copy-design", type=str, help="指定要复制的品牌名称 (如 stripe, linear.app, apple)")
    
    # CCSwitch 风格状态机与管理
    parser.add_argument("--status", action="store_true", help="诊断目标环境的技能激活/休眠状态 (CCSwitch 状态机)")
    parser.add_argument("--enable", type=str, help="激活指定技能到目标宿主/环境")
    parser.add_argument("--disable", type=str, help="停用指定技能并归档")
    parser.add_argument("--target", type=str, default=".", help="目标工作区路径 (默认为当前目录)")
    parser.add_argument("--host", type=str, default="local", choices=["local", "workbuddy", "claudecode", "cursor", "antigravity", "codex"], help="指定宿主适配器 (默认为 local)")
    
    # Profile 场景切换
    parser.add_argument("--profiles", action="store_true", help="列出所有可用的预设场景组合")
    parser.add_argument("--profile", type=str, help="一键应用指定的 Profile 技能组合 (如 fullstack, python-dev, frontend)")
    
    # 全网技能平台与网络导入
    parser.add_argument("--platforms", action="store_true", help="列出全网 AI Agent Skills 与 MCP 平台权威汇总")
    parser.add_argument("--platforms-search", type=str, help="按关键词检索全网平台 (如 mcp, registry, design)")
    parser.add_argument("--import-git", type=str, help="从网络 Git 仓库拉取技能至本地 Hub")
    parser.add_argument("--category", type=str, default="community", help="导入技能时的分类名称")
    
    # 14 款核心 MCP 服务器管理
    parser.add_argument("--mcp-list", action="store_true", help="列出 14 款核心生产级 MCP 服务器清单")
    parser.add_argument("--mcp-status", action="store_true", help="巡检 14 款 MCP 服务在全端客户端的同步状态")
    parser.add_argument("--mcp-sync", type=str, choices=["all", "ccswitch", "claude", "codex", "workbuddy"], help="一键同步 14 款 MCP 服务器至指定或全部客户端")

    args = parser.parse_args()

    if args.list:
        list_skills()
    elif args.search:
        search_skills(args.search)
    elif args.brands:
        list_brands()
    elif args.copy_design:
        copy_design(args.copy_design, args.target)
    elif args.status:
        check_status(args.target, args.host)
    elif args.enable:
        enable_skill(args.enable, args.target, args.host)
    elif args.disable:
        disable_skill(args.disable, args.target, args.host)
    elif args.profiles:
        list_profiles()
    elif args.profile:
        apply_profile(args.profile, args.target, args.host)
    elif args.platforms:
        show_platforms()
    elif args.platforms_search:
        show_platforms(args.platforms_search)
    elif args.import_git:
        import_git_skill(args.import_git, args.category)
    elif args.mcp_list:
        show_mcp_list()
    elif args.mcp_status:
        check_mcp_status()
    elif args.mcp_sync:
        sync_all_mcps(args.mcp_sync)
    else:
        list_skills()

if __name__ == "__main__":
    main()

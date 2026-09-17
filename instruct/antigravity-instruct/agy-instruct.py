#!/usr/bin/env python3
"""Deploy or remove packaged antigravity-instruct rules, skills, and configuration.

Directly inspired by MDX-Tom/gpt-instruct's codex-instruct.py, this CLI manages system
instructions and runtime rules for Google Antigravity and Gemini coding environments.
Supports workspace-scoped and global-scoped installations, custom ZIP/MD deployment (--file),
atomic snapshots, preview modes (--dry-run), and non-destructive rollbacks (--reset).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import zipfile
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output across Windows and POSIX terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGES_DIR = PROJECT_ROOT / "packages"
TEMPLATE_DIR = PROJECT_ROOT / "template"

DEFAULT_VERSION = "agy-v1-standard"
AVAILABLE_VERSIONS: dict[str, dict[str, object]] = {
    "agy-v1-standard": {
        "title": "AGY-v1 Standard (Production Stable / 唯一生产稳定版)",
        "md": PACKAGES_DIR / "agy-v1-standard.md",
        "zip": PACKAGES_DIR / "agy-v1-standard.zip",
        "badge": "默认推荐 / Default",
    },
    "agy-v2-hyperdrive": {
        "title": "AGY-v2 Hyperdrive (High-Throughput & Deep Transaction / 极限吞吐版)",
        "md": PACKAGES_DIR / "agy-v2-hyperdrive.md",
        "zip": PACKAGES_DIR / "agy-v2-hyperdrive.zip",
        "badge": "高阶评测 / Advanced",
    },
}

STATE_FILENAME = ".agy-instruct-state.json"
BACKUP_SUFFIX = ".agy-backup"
STATE_VERSION = 2
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# Visual ANSI Codes
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DARK_GREEN = "\033[38;2;0;135;0m"
ANSI_CYAN = "\033[36m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
BANNER_WIDTH = 72


def color_enabled() -> bool:
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    return sys.stdout.isatty()


def styled(text: str, *codes: str) -> str:
    if not color_enabled():
        return text
    return f"{''.join(codes)}{text}{ANSI_RESET}"


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in text)


def section_banner(title: str) -> str:
    label = f" {title} "
    fill_width = max(4, BANNER_WIDTH - display_width(label))
    left = fill_width // 2
    right = fill_width - left
    return styled(f"{'━' * left}{label}{'━' * right}", ANSI_BOLD)


def intro_text() -> str:
    zh_banner = section_banner("中文说明 / Overview (ZH)")
    en_banner = section_banner("English Instructions / Overview (EN)")
    zh_title = styled("antigravity-instruct 版本部署说明：", ANSI_BOLD)
    en_title = styled("antigravity-instruct version deployment:", ANSI_BOLD)
    zh_default = styled("唯一生产默认稳定版", ANSI_BOLD, ANSI_DARK_GREEN)
    en_default = styled("sole default stable release", ANSI_BOLD, ANSI_DARK_GREEN)

    return f"""\
{zh_banner}
{zh_title}

agy-v1-standard 是当前生产环境推荐的{zh_default}；agy-v2-hyperdrive 适用于复杂多步重构与深度审计。

部署时会将所选提示词与 Antigravity 规则（GEMINI.md、AGENTS.md、.agents/rules/）、事务技能与钩子无侵入式注入至目标目录，并在部署前自动创建快照。卸载（--reset）时精准还原原有文件，绝不破坏用户原有的其他非受管配置。支持使用 --file 显式部署自定义 ZIP 或 Markdown 提示词。

{en_banner}
{en_title}

agy-v1-standard is the current {en_default}; agy-v2-hyperdrive is tailored for deep refactoring and high-throughput execution.

Deployment non-destructively mounts the selected prompt pack and Antigravity rules (GEMINI.md, AGENTS.md, .agents/), transaction verifiers, and lifecycle hooks into the target workspace or global directory. Pre-operation snapshots are taken automatically. Reset (--reset) restores pre-existing files without touching unrelated user configurations. Custom ZIP or Markdown prompts can be deployed via --file.
"""


def menu_text() -> str:
    selection_banner = section_banner("操作选择 / Select an Action")
    default_badge = styled("默认推荐 / Default", ANSI_BOLD, ANSI_DARK_GREEN)
    adv_badge = styled("高阶吞吐 / Advanced", ANSI_BOLD, ANSI_CYAN)
    return f"""\
{selection_banner}
1. agy-v1-standard → 部署生产稳定版 （{default_badge}）
2. agy-v2-hyperdrive → 部署极限吞吐版 （{adv_badge}）
3. 部署到全局环境 (~/.gemini/config) / Deploy globally
4. 部署自定义文件 (--file <path>) / Deploy custom file
5. 检查当前部署状态 / Check current status
6. 预览部署操作 (--dry-run) / Preview deployment
7. 卸载并恢复原工作区 / Reset & restore workspace
q. 退出而不做修改 / Quit without modification
"""


def calculate_sha256(filepath: Path) -> str:
    if not filepath.exists():
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def calculate_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_default_global_dir() -> Path:
    return Path.home() / ".gemini" / "config"


def find_workspace_root(start_path: Path | None = None) -> Path:
    cur = (start_path or Path.cwd()).resolve()
    for p in [cur] + list(cur.parents):
        if (p / ".git").exists() or (p / "GEMINI.md").exists() or (p / ".agents").exists():
            return p
    return cur


def atomic_write_text(path: Path, text: str, *, follow_symlink: bool = False) -> None:
    """Atomically write text using temporary files and fsync to prevent partial writes."""
    if path.is_symlink() and not follow_symlink:
        raise OSError(f"Refusing to overwrite symlink: {path}")
    write_path = path.resolve(strict=False) if path.is_symlink() else path
    previous_mode = write_path.stat().st_mode & 0o777 if write_path.exists() else 0o644
    write_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{write_path.name}.", dir=write_path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, previous_mode)
        os.replace(temp_path, write_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def read_prompt(source_path: Path, expected_filename: str | None = None) -> tuple[str, str]:
    """Read prompt text from markdown file or extract from ZIP archive."""
    if not source_path.exists():
        raise FileNotFoundError(f"Source prompt not found: {source_path}")

    if source_path.suffix.lower() == ".md":
        return source_path.read_text(encoding="utf-8"), source_path.name

    if source_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(source_path) as archive:
            files = [name for name in archive.namelist() if not name.endswith("/")]
            candidates = [name for name in files if Path(name).suffix.lower() == ".md"]
            if expected_filename:
                preferred = [name for name in candidates if Path(name).name == expected_filename]
                if preferred:
                    candidates = preferred
            if len(candidates) != 1:
                raise ValueError(
                    f"ZIP archive must contain exactly one markdown file, found: {candidates}"
                )
            member = candidates[0]
            with tempfile.TemporaryDirectory(prefix="agy-prompt-") as temp_dir:
                extracted = Path(archive.extract(member, path=temp_dir))
                return extracted.read_text(encoding="utf-8"), Path(member).name

    raise ValueError(f"Unsupported prompt format '{source_path.suffix}'. Use .md or .zip.")


def load_state(target_dir: Path) -> dict:
    state_file = target_dir / STATE_FILENAME
    if not state_file.exists():
        return {}
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and (data.get("state_version") == STATE_VERSION or data.get("version") == STATE_VERSION):
                return data
    except Exception:
        pass
    return {}


def save_state(target_dir: Path, state: dict) -> None:
    state["state_version"] = STATE_VERSION
    atomic_write_text(target_dir / STATE_FILENAME, json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def deploy_package(
    source_path: Path,
    target_dir: Path,
    version_label: str = "custom",
    dry_run: bool = False,
    is_global: bool = False,
) -> bool:
    target_dir = target_dir.resolve()
    print(f"\n── 目标 / Target: {styled(str(target_dir), ANSI_BOLD)} ──")
    print(f"  版本 / Version: {styled(version_label, ANSI_CYAN)}")
    print(f"  范围 / Scope: {'GLOBAL (~/.gemini/config)' if is_global else 'WORKSPACE'}")
    print(f"  源文件 / Source: {source_path}")

    try:
        prompt_text, md_name = read_prompt(source_path)
    except Exception as e:
        print(styled(f"[ERROR] 读取提示词失败 / Failed to read prompt: {e}", ANSI_RED), file=sys.stderr)
        return False

    prompt_digest = calculate_text_sha256(prompt_text)
    print(f"  摘要 / SHA256: {prompt_digest[:16]}...")
    if dry_run:
        print(styled("  [DRY-RUN] 预览模式，不执行真实磁盘写入。", ANSI_YELLOW))

    operations: list[tuple[str, Path, str]] = []  # (kind, dest_path, content_or_src)

    # 1. Target rule / instruction destination
    # In Antigravity workspaces, GEMINI.md at root is what the agent unconditionally loads into <user_rules>!
    if is_global:
        dest_prompt = target_dir / "rules" / "00-model-instructions.md"
        operations.append(("TEXT", dest_prompt, prompt_text))
    else:
        operations.append(("TEXT", target_dir / "GEMINI.md", prompt_text))
        dest_prompt = target_dir / ".agents" / "rules" / "00-model-instructions.md"
        operations.append(("TEXT", dest_prompt, prompt_text))

    # 2. Template files (AGENTS.md, rules, skills, hooks)
    if not is_global and TEMPLATE_DIR.exists():
        agents_md = TEMPLATE_DIR / "AGENTS.md"
        if agents_md.exists():
            operations.append(("FILE", target_dir / "AGENTS.md", str(agents_md)))

        template_agents = TEMPLATE_DIR / ".agents"
        if template_agents.exists():
            for root, _, files in os.walk(template_agents):
                rel_root = Path(root).relative_to(template_agents)
                for f in files:
                    src = Path(root) / f
                    dest = target_dir / ".agents" / rel_root / f
                    operations.append(("FILE", dest, str(src)))

    existing_state = load_state(target_dir)
    managed_files: list[str] = []
    backups: dict[str, str] = existing_state.get("backups", {})

    print("\n计划的文件写入 / Planned File Operations:")
    for kind, dest, src_or_text in operations:
        dest_str = str(dest.resolve())
        managed_files.append(dest_str)
        status = styled("覆盖 / OVERWRITE", ANSI_YELLOW) if dest.exists() else styled("新建 / NEW", ANSI_DARK_GREEN)
        print(f"  [{status}] {dest}")

    if dry_run:
        print(f"\n[DRY-RUN] 分析完成，模拟了 {len(operations)} 项文件操作。")
        return True

    # Execute operations with atomic backups
    for kind, dest, src_or_text in operations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest_str = str(dest.resolve())

        if dest.exists() and dest_str not in backups:
            backup_path = dest.with_name(dest.name + BACKUP_SUFFIX)
            shutil.copy2(dest, backup_path)
            backups[dest_str] = str(backup_path.resolve())

        if kind == "TEXT":
            atomic_write_text(dest, src_or_text)
        elif kind == "FILE":
            shutil.copy2(Path(src_or_text), dest)

    new_state = {
        "version": version_label,
        "sha256": prompt_digest,
        "applied_at": datetime.now().isoformat(),
        "is_global": is_global,
        "target_dir": str(target_dir),
        "managed_files": list(set(managed_files)),
        "backups": backups,
    }
    save_state(target_dir, new_state)

    print(styled(f"\n[SUCCESS] 成功部署 {version_label} 到 {target_dir}！", ANSI_BOLD, ANSI_DARK_GREEN))
    print(f"[+] 状态快照已保存: {target_dir / STATE_FILENAME}")
    return True


def reset_deployment(target_dir: Path, dry_run: bool = False) -> bool:
    target_dir = target_dir.resolve()
    state = load_state(target_dir)

    print(f"\n── 卸载与还原 / Reset & Restore: {styled(str(target_dir), ANSI_BOLD)} ──")
    if dry_run:
        print(styled("  [DRY-RUN] 预览模式，不执行真实磁盘变更。", ANSI_YELLOW))

    if not state:
        print("[WARN] 未找到受管状态记录。搜索遗留备份文件...")
        backups = list(target_dir.rglob(f"*{BACKUP_SUFFIX}"))
        if not backups:
            print("[INFO] 无需还原的操作。")
            return True

    managed_files = state.get("managed_files", [])
    backups = state.get("backups", {})

    print(f"  受管文件数 / Managed Files: {len(managed_files)}")
    print(f"  备份文件数 / Backups to Restore: {len(backups)}\n")

    # 1. Restore backups
    for dest_str, backup_str in backups.items():
        dest = Path(dest_str)
        backup = Path(backup_str)
        if backup.exists():
            print(f"  [还原 / RESTORE] {dest} <- {backup.name}")
            if not dry_run:
                shutil.copy2(backup, dest)
                backup.unlink()

    # 2. Remove files created by this tool that had no backup
    for dest_str in managed_files:
        if dest_str not in backups:
            dest = Path(dest_str)
            if dest.exists():
                print(f"  [删除 / REMOVE] {dest}")
                if not dry_run:
                    dest.unlink()

    # 3. Clean state file
    state_file = target_dir / STATE_FILENAME
    if state_file.exists() and not dry_run:
        state_file.unlink()

    print(styled("\n[SUCCESS] 卸载还原完成，工作区已恢复至安装前基线状态。\n", ANSI_BOLD, ANSI_DARK_GREEN))
    return True


def show_status(target_dir: Path) -> None:
    target_dir = target_dir.resolve()
    state = load_state(target_dir)
    print("\n" + section_banner("部署状态 / Deployment Status"))
    print(f"目标目录 / Directory: {styled(str(target_dir), ANSI_BOLD)}")

    if not state:
        print(f"当前状态 / Status: {styled('未部署 / NOT INSTALLED', ANSI_YELLOW)}")
    else:
        print(f"当前状态 / Status: {styled('已激活 / ACTIVE', ANSI_DARK_GREEN, ANSI_BOLD)}")
        print(f"安装版本 / Version: {styled(state.get('version', 'unknown'), ANSI_CYAN)}")
        print(f"指令指纹 / SHA256: {state.get('sha256', 'N/A')}")
        print(f"部署时间 / Installed At: {state.get('applied_at', 'N/A')}")
        print(f"生效范围 / Scope: {'全局 (Global)' if state.get('is_global') else '工作区 (Workspace)'}")
        files = state.get("managed_files", [])
        print(f"\n受管文件列表 ({len(files)} 项):")
        for f in files[:12]:
            print(f"  ✓ {f}")
        if len(files) > 12:
            print(f"  ... 以及其余 {len(files) - 12} 个文件。")

    print(styled("━" * BANNER_WIDTH, ANSI_BOLD) + "\n")


def interactive_cli(default_workspace: Path) -> None:
    print(intro_text())
    cur_target = default_workspace

    while True:
        print(menu_text())
        choice = input(styled("请输入选项 [1-7, q] / Enter option: ", ANSI_BOLD)).strip()

        if choice.lower() in {"q", "quit", "exit"}:
            print("退出。/ Exiting.")
            break
        elif choice == "1":
            info = AVAILABLE_VERSIONS["agy-v1-standard"]
            deploy_package(Path(info["md"]), cur_target, version_label="agy-v1-standard")
        elif choice == "2":
            info = AVAILABLE_VERSIONS["agy-v2-hyperdrive"]
            deploy_package(Path(info["md"]), cur_target, version_label="agy-v2-hyperdrive")
        elif choice == "3":
            g_dir = get_default_global_dir()
            info = AVAILABLE_VERSIONS["agy-v1-standard"]
            deploy_package(Path(info["md"]), g_dir, version_label="agy-v1-standard", is_global=True)
        elif choice == "4":
            file_input = input("请输入自定义 .zip 或 .md 文件路径: ").strip().strip('"').strip("'")
            if file_input:
                custom_p = Path(file_input)
                deploy_package(custom_p, cur_target, version_label=custom_p.stem)
        elif choice == "5":
            show_status(cur_target)
        elif choice == "6":
            info = AVAILABLE_VERSIONS["agy-v1-standard"]
            deploy_package(Path(info["md"]), cur_target, version_label="agy-v1-standard", dry_run=True)
        elif choice == "7":
            reset_deployment(cur_target)
        elif choice == "8":
            doctor_check(cur_target)
        else:
            print(styled("[!] 无效输入，请重新选择。/ Invalid choice.", ANSI_RED))


def doctor_check(target_dir: Path) -> int:
    print(section_banner("Antigravity 运行环境诊断 (Doctor)"))
    print(f"目标工作区 / Target Directory: {target_dir}")

    gemini_md = target_dir / "GEMINI.md"
    agents_md = target_dir / "AGENTS.md"
    rules_dir = target_dir / ".agents" / "rules"
    skills_dir = target_dir / ".agents" / "skills"
    hooks_json = target_dir / ".agents" / "hooks.json"
    state_file = target_dir / STATE_FILENAME

    print("\n[受管核心配置检查]")
    print(f"  - GEMINI.md:  {'[OK] 存在' if gemini_md.exists() else '[未创建]'}")
    print(f"  - AGENTS.md:  {'[OK] 存在' if agents_md.exists() else '[未创建]'}")
    print(f"  - Rules 目录: {'[OK] 存在' if rules_dir.exists() else '[未创建]'}")
    print(f"  - Skills 目录: {'[OK] 存在' if skills_dir.exists() else '[未创建]'}")
    print(f"  - 部署状态记: {'[OK] 已激活' if state_file.exists() else '[未激活]'}")

    print("\n[钩子与运行时健康度]")
    if hooks_json.exists():
        try:
            with open(hooks_json, "r", encoding="utf-8-sig") as f:
                hdata = json.load(f)
            print(f"  - hooks.json: [OK] 语法合法，共配置 {len(hdata)} 项钩子")
        except Exception as e:
            print(f"  - hooks.json: [警告] 语法错误 ({e})")
    else:
        print("  - hooks.json: [未配置]")

    # Check python executable and version
    print(f"\n[Python 解释器环境]")
    print(f"  - 当前解释器: {sys.executable}")
    print(f"  - Python 版本: {sys.version.split()[0]}")
    print(f"  - 平台编码: stdout={sys.stdout.encoding}, filesystem={sys.getfilesystemencoding()}")

    # Check available packages
    print("\n[可用指令包清单]")
    for ver_key, ver_info in AVAILABLE_VERSIONS.items():
        exists = Path(ver_info["md"]).exists()
        print(f"  - {ver_key}: {ver_info['title']} ({'[OK] 就绪' if exists else '[缺失]'})")

    print("\n" + "=" * BANNER_WIDTH + "\n")
    return 0


def restore_hooks(target_dir: Path) -> int:
    hooks_backup = target_dir / ".agents" / f"hooks.json{BACKUP_SUFFIX}"
    hooks_target = target_dir / ".agents" / "hooks.json"
    if not hooks_backup.exists():
        print("未发现 hooks 备份文件，无需恢复。")
        return 0
    shutil.copy2(hooks_backup, hooks_target)
    print(f"[OK] 已从备份恢复 hooks.json: {hooks_backup} -> {hooks_target}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity Instruct CLI: Deploy and manage runtime directives, rules, and skills."
    )
    parser.add_argument("--apply", action="store_true", help="Deploy the selected instruction package")
    parser.add_argument(
        "--version",
        choices=list(AVAILABLE_VERSIONS.keys()),
        default=DEFAULT_VERSION,
        help=f"Built-in instruction version to deploy (default: {DEFAULT_VERSION})",
    )
    parser.add_argument("--file", type=Path, help="Deploy custom .zip or .md instruction file")
    parser.add_argument("--workspace", type=Path, help="Explicit target workspace directory")
    parser.add_argument("--global", dest="is_global", action="store_true", help="Deploy globally to ~/.gemini/config")
    parser.add_argument("--dry-run", action="store_true", help="Preview operations without writing to disk")
    parser.add_argument("--reset", action="store_true", help="Restore pre-existing files and remove managed rules")
    parser.add_argument("--status", action="store_true", help="Display current installation status")
    parser.add_argument("--doctor", action="store_true", help="Run Antigravity environment diagnostics")
    parser.add_argument("--restore-hooks", action="store_true", help="Restore original hooks.json from backup")

    args = parser.parse_args()

    # Determine target directory
    if args.is_global:
        target_dir = get_default_global_dir()
    elif args.workspace:
        target_dir = args.workspace.resolve()
    else:
        target_dir = find_workspace_root()

    if args.status:
        show_status(target_dir)
        return 0
    elif args.doctor:
        return doctor_check(target_dir)
    elif args.restore_hooks:
        return restore_hooks(target_dir)
    elif args.reset:
        return 0 if reset_deployment(target_dir, dry_run=args.dry_run) else 1
    elif args.apply or args.file:
        if args.file:
            source = args.file
            label = args.file.stem
        else:
            info = AVAILABLE_VERSIONS[args.version]
            source = Path(info["md"])
            label = args.version
        return 0 if deploy_package(source, target_dir, version_label=label, dry_run=args.dry_run, is_global=args.is_global) else 1

    # Launch interactive CLI
    interactive_cli(target_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

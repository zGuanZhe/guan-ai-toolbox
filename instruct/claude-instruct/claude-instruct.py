#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claude-instruct: Deterministic Instruction & Runtime Injector for Claude Code.

Provides atomic, verifiable, and reversible instruction management across:
  1. Project scope: <repo>/CLAUDE.md + <repo>/.claude/instruct/<name>.md
  2. User scope:    ~/.claude/CLAUDE.md + ~/.claude/instruct/<name>.md
  3. Local scope:   <repo>/CLAUDE.local.md + <repo>/.claude/instruct/<name>.md
  4. Runtime level: ~/.claude/settings.json alignment + ~/.claude/keysmith prompt files

Supports both command-style and flag-style invocations:
  claude-instruct.py --apply --version claude-v1-standard
  claude-instruct.py --status
  claude-instruct.py --reset
  claude-instruct.py --dry-run
  claude-instruct.py install --scope project --yes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure safe console output across Windows CP936 / GBK and UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(errors="replace")

VERSION = "v1.0.0"
TOOL_NAME = "claude-instruct"
START_MARKER_TEMPLATE = "<!-- claude-instruct:start name={name} -->"
END_MARKER_TEMPLATE = "<!-- claude-instruct:end name={name} -->"
LEGACY_START_MARKER = "<!-- claude-keysmith:start"

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGES_DIR = SCRIPT_DIR / "packages"
MANIFEST_FILE = PACKAGES_DIR / "packages_manifest.json"
EXAMPLES_DIR = SCRIPT_DIR / "examples"


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_FILE.exists():
        return {}
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ScopePaths:
    scope: str
    root: Path
    memory_file: Path
    instruct_dir: Path
    import_prefix: str

    def instruction_file(self, md_filename: str) -> Path:
        return self.instruct_dir / md_filename

    def import_target(self, md_filename: str) -> str:
        return f"@{self.import_prefix}/{md_filename}"


def resolve_scope(scope: str, project_dir: Optional[Path] = None) -> ScopePaths:
    cwd = (project_dir or Path.cwd()).resolve()
    home = Path.home().resolve()

    if scope == "user":
        user_claude = home / ".claude"
        return ScopePaths(
            scope="user",
            root=user_claude,
            memory_file=user_claude / "CLAUDE.md",
            instruct_dir=user_claude / "instruct",
            import_prefix="instruct",
        )
    elif scope == "local":
        dot_claude = cwd / ".claude"
        return ScopePaths(
            scope="local",
            root=cwd,
            memory_file=cwd / "CLAUDE.local.md",
            instruct_dir=dot_claude / "instruct",
            import_prefix=".claude/instruct",
        )
    else:  # project
        dot_claude = cwd / ".claude"
        return ScopePaths(
            scope="project",
            root=cwd,
            memory_file=cwd / "CLAUDE.md",
            instruct_dir=dot_claude / "instruct",
            import_prefix=".claude/instruct",
        )


def read_prompt_content(version: str, custom_file: Optional[Path] = None) -> Tuple[str, str]:
    """Returns (content, sha256)."""
    if custom_file:
        p = Path(custom_file).resolve()
        if not p.exists():
            raise FileNotFoundError(f"自定义指令文件未找到: {p}")
        text = p.read_text(encoding="utf-8")
        return text, sha256_text(text)

    manifest = load_manifest()
    if version in manifest:
        md_file = PACKAGES_DIR / manifest[version]["markdown_file"]
        if md_file.exists():
            text = md_file.read_text(encoding="utf-8")
            return text, sha256_text(text)

    # Fallback to direct path search in packages
    direct = PACKAGES_DIR / f"{version}.md"
    if direct.exists():
        text = direct.read_text(encoding="utf-8")
        return text, sha256_text(text)

    raise ValueError(f"未知指令包版本: {version}。可用版本: {list(manifest.keys())}")


def build_import_block(name: str, import_target: str) -> str:
    start = START_MARKER_TEMPLATE.format(name=name)
    end = END_MARKER_TEMPLATE.format(name=name)
    return f"{start}\n{import_target}\n{end}"


def inject_into_memory_text(text: str, name: str, new_block: str) -> str:
    pattern = re.compile(
        rf"(?:<!-- claude-instruct:start name={re.escape(name)} -->|"
        rf"<!-- claude-keysmith:start name={re.escape(name)} -->)"
        r".*?"
        rf"(?:<!-- claude-instruct:end name={re.escape(name)} -->|"
        rf"<!-- claude-keysmith:end name={re.escape(name)} -->)\n?",
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(new_block + "\n", text)
    if text and not text.endswith("\n"):
        text += "\n"
    return new_block + "\n\n" + text


def strip_from_memory_text(text: str, name: Optional[str] = None) -> str:
    if name:
        pattern = re.compile(
            rf"(?:<!-- claude-instruct:start name={re.escape(name)} -->|"
            rf"<!-- claude-keysmith:start name={re.escape(name)} -->)"
            r".*?"
            rf"(?:<!-- claude-instruct:end name={re.escape(name)} -->|"
            rf"<!-- claude-keysmith:end name={re.escape(name)} -->)\n?",
            re.DOTALL,
        )
    else:
        pattern = re.compile(
            r"(?:<!-- claude-instruct:start name=.*? -->|<!-- claude-keysmith:start name=.*? -->)"
            r".*?"
            r"(?:<!-- claude-instruct:end name=.*? -->|<!-- claude-keysmith:end name=.*? -->)\n?",
            re.DOTALL,
        )
    return pattern.sub("", text).lstrip("\r\n")


def create_backup(path: Path) -> Optional[Path]:
    if not path.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.name}.bak_{ts}")
    shutil.copy2(path, backup)
    return backup


def apply_instruct(
    version: str,
    scope: str = "project",
    project_dir: Optional[Path] = None,
    custom_file: Optional[Path] = None,
    dry_run: bool = False,
    runtime: bool = False,
) -> int:
    scope_paths = resolve_scope(scope, project_dir)
    content, content_sha256 = read_prompt_content(version, custom_file)
    name = version if version.startswith("claude-") else f"claude-{version}"
    if custom_file:
        name = Path(custom_file).stem

    dest_md = scope_paths.instruction_file(f"{name}.md")
    import_target = scope_paths.import_target(f"{name}.md")
    new_block = build_import_block(name, import_target)

    memory_file = scope_paths.memory_file
    orig_memory_text = memory_file.read_text(encoding="utf-8") if memory_file.exists() else ""
    updated_memory_text = inject_into_memory_text(orig_memory_text, name, new_block)

    print(f"\n[{TOOL_NAME}] 正在应用指令: {version} (作用域: {scope})")
    print(f"  - 目标配置: {memory_file}")
    print(f"  - 指令文件: {dest_md}")
    print(f"  - 指令指纹: {content_sha256[:16]}...")

    if dry_run:
        print("\n[DRY-RUN] 预览写入内容:")
        print(f"--- {memory_file} ---")
        print(new_block)
        print(f"--- {dest_md} (前 5 行) ---")
        for line in content.splitlines()[:5]:
            print(f"  {line}")
        print("\n[DRY-RUN] 未执行磁盘写入。")
        return 0

    # 1. Write instruction file
    dest_md.parent.mkdir(parents=True, exist_ok=True)
    if dest_md.exists():
        bk = create_backup(dest_md)
        if bk:
            print(f"  已备份旧指令: {bk.name}")
    dest_md.write_text(content, encoding="utf-8")

    # 2. Write memory file
    if memory_file.exists():
        bk = create_backup(memory_file)
        if bk:
            print(f"  已备份配置文件: {bk.name}")
    else:
        memory_file.parent.mkdir(parents=True, exist_ok=True)
    memory_file.write_text(updated_memory_text, encoding="utf-8")

    # 3. Optional runtime alignment
    if runtime or scope == "user":
        home = Path.home()
        settings_file = home / ".claude" / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                settings["systemPrompt"] = str(dest_md)
                bk = create_backup(settings_file)
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                print(f"  已对齐 Claude Code settings.json systemPrompt")
            except Exception as e:
                print(f"  [警告] 对齐 settings.json 失败: {e}")

    print(f"\n[OK] 部署完成！请新开一个 Claude Code 会话生效。")
    return 0


def reset_instruct(
    scope: str = "project",
    project_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> int:
    scope_paths = resolve_scope(scope, project_dir)
    memory_file = scope_paths.memory_file

    print(f"\n[{TOOL_NAME}] 正在重置指令 (作用域: {scope})")
    if not memory_file.exists():
        print(f"  未发现配置文件: {memory_file}，无需清理。")
        return 0

    orig_text = memory_file.read_text(encoding="utf-8")
    cleaned_text = strip_from_memory_text(orig_text)

    if orig_text == cleaned_text:
        print(f"  在 {memory_file} 中未检测到受管 import block。")
        return 0

    if dry_run:
        print(f"[DRY-RUN] 将在 {memory_file} 中移除受管指令引用。")
        return 0

    create_backup(memory_file)
    memory_file.write_text(cleaned_text, encoding="utf-8")
    print(f"  已从 {memory_file} 移除受管 block 并保留备份。")

    # Clean instruct directory if exists
    if scope_paths.instruct_dir.exists():
        print(f"  保留指令归档目录: {scope_paths.instruct_dir}")

    print(f"\n✓ 重置完成！已恢复原生默认配置。")
    return 0


def status_instruct(
    scope: str = "project",
    project_dir: Optional[Path] = None,
) -> int:
    scope_paths = resolve_scope(scope, project_dir)
    memory_file = scope_paths.memory_file

    print(f"\n==================== Claude Code 指令部署状态 ====================")
    print(f"作用域 / Scope: {scope}")
    print(f"检查目录 / Root: {scope_paths.root}")
    print(f"配置文件 / Memory File: {memory_file}")

    has_block = False
    active_name = "None"
    import_target = "None"

    if memory_file.exists():
        text = memory_file.read_text(encoding="utf-8")
        m = re.search(
            r"(?:<!-- claude-instruct:start name=(.*?) -->|<!-- claude-keysmith:start name=(.*?) -->)"
            r"\s*(.*?)\s*"
            r"(?:<!-- claude-instruct:end|<!-- claude-keysmith:end)",
            text,
            re.DOTALL,
        )
        if m:
            has_block = True
            active_name = m.group(1) or m.group(2)
            import_target = m.group(3).strip()

    if has_block:
        print(f"当前状态 / Status: 已激活 / ACTIVE")
        print(f"当前版本 / Version: {active_name}")
        print(f"引用目标 / Import Target: {import_target}")
        resolved_file = scope_paths.root / import_target.lstrip("@")
        if resolved_file.exists():
            h = sha256_file(resolved_file)
            print(f"文件状态 / Target File: 存在 ({resolved_file})")
            print(f"文件指纹 / SHA256: {h}")
        else:
            print(f"文件状态 / Target File: 警告 (未找到引用目标文件: {resolved_file})")
    else:
        print(f"当前状态 / Status: 未部署 (原生默认状态)")

    # Check available packages
    manifest = load_manifest()
    print(f"\n可用指令包清单 ({len(manifest)} 项):")
    for pkg_name, info in manifest.items():
        print(f"  - {pkg_name} ({info.get('size_bytes', 0)} bytes) - {info.get('description', '')}")
    print(f"====================================================================\n")
    return 0


def doctor_check() -> int:
    print(f"\n[{TOOL_NAME}] 运行环境自检 (Doctor):")
    claude_bin = shutil.which("claude")
    if claude_bin:
        print(f"  ✓ Claude Code CLI 已安装: {claude_bin}")
    else:
        print(f"  - Claude Code CLI 未在系统 PATH 中发现 (可通过 npm i -g @anthropic-ai/claude-code 安装)")

    home = Path.home()
    user_claude = home / ".claude"
    if user_claude.exists():
        print(f"  ✓ 用户目录配置存在: {user_claude}")
    else:
        print(f"  - 用户目录 ~/.claude 尚未创建")

    settings_file = user_claude / "settings.json"
    if settings_file.exists():
        print(f"  ✓ Claude settings.json 存在")
    else:
        print(f"  - ~/.claude/settings.json 尚未创建")

    print(f"  ✓ Python 环境版本: {sys.version.split()[0]}")
    print("自检结束。\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude Code instruction & runtime manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Global flags
    parser.add_argument("-V", "--version-info", action="store_true", help="显示版本号")
    parser.add_argument("--apply", action="store_true", help="部署指定的指令包")
    parser.add_argument(
        "--version",
        "--pkg-version",
        dest="version_name",
        default="claude-v1-standard",
        help="选择指令包版本 (默认: claude-v1-standard)",
    )
    parser.add_argument("--file", "-f", type=Path, help="自定义指令文件路径")
    parser.add_argument(
        "--scope",
        choices=["project", "user", "local"],
        default="project",
        help="生效作用域 (默认: project)",
    )
    parser.add_argument("--project-dir", type=Path, help="指定项目目录")
    parser.add_argument("--runtime", action="store_true", help="一并配置 runtime 运行时 settings")
    parser.add_argument("--dry-run", action="store_true", help="预览变更不落盘")
    parser.add_argument("--reset", action="store_true", help="重置并移除受管指令")
    parser.add_argument("--status", action="store_true", help="查看部署状态与指纹")
    parser.add_argument("--doctor", action="store_true", help="检查 Claude Code 环境")

    # Subcommands for backward compatibility with claude-keysmith
    subparsers = parser.add_subparsers(dest="command", help="子命令模式")
    p_install = subparsers.add_parser("install", help="安装指令")
    p_install.add_argument("--scope", choices=["project", "user", "local"], default="project")
    p_install.add_argument("--version-name", default="claude-v1-standard")
    p_install.add_argument("--file", type=Path)
    p_install.add_argument("--project-dir", type=Path)
    p_install.add_argument("--runtime", action="store_true")
    p_install.add_argument("--yes", action="store_true")
    p_install.add_argument("--dry-run", action="store_true")

    p_uninstall = subparsers.add_parser("uninstall", help="卸载指令")
    p_uninstall.add_argument("--scope", choices=["project", "user", "local"], default="project")
    p_uninstall.add_argument("--project-dir", type=Path)
    p_uninstall.add_argument("--yes", action="store_true")

    p_status = subparsers.add_parser("status", help="状态检查")
    p_status.add_argument("--scope", choices=["project", "user", "local"], default="project")
    p_status.add_argument("--project-dir", type=Path)

    p_doctor = subparsers.add_parser("doctor", help="环境诊断")

    args = parser.parse_args()

    if args.version_info:
        print(f"{TOOL_NAME} {VERSION}")
        return 0

    cmd = args.command
    if cmd == "install":
        dry_run = args.dry_run or (not args.yes)
        return apply_instruct(
            version=args.version_name,
            scope=args.scope,
            project_dir=args.project_dir,
            custom_file=args.file,
            dry_run=dry_run,
            runtime=args.runtime,
        )
    elif cmd == "uninstall":
        return reset_instruct(scope=args.scope, project_dir=args.project_dir, dry_run=False)
    elif cmd == "status":
        return status_instruct(scope=args.scope, project_dir=args.project_dir)
    elif cmd == "doctor":
        return doctor_check()

    # Flag mode handling
    if args.apply:
        return apply_instruct(
            version=args.version_name,
            scope=args.scope,
            project_dir=args.project_dir,
            custom_file=args.file,
            dry_run=args.dry_run,
            runtime=args.runtime,
        )
    elif args.reset:
        return reset_instruct(scope=args.scope, project_dir=args.project_dir, dry_run=args.dry_run)
    elif args.status:
        return status_instruct(scope=args.scope, project_dir=args.project_dir)
    elif args.doctor:
        return doctor_check()
    else:
        # Default action when no args: print status
        return status_instruct(scope=args.scope, project_dir=args.project_dir)


if __name__ == "__main__":
    sys.exit(main())

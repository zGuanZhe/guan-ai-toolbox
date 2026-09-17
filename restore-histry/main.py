#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Restore Manager (通用历史对话恢复总控)
严格分工具独立管理，彻底杜绝一键全量恢复。
涵盖: trae, zcode, workbuddy, gpt, claudecode, antigravity.
"""

import os
import sys
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 保证能加载当前目录下的模块
cur_dir = os.path.dirname(os.path.abspath(__file__))
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from core.restore_engine import RestoreEngine
from adapters import get_registered_adapters
from cli.interactive_ui import InteractiveRestoreUI

def build_engine():
    engine = RestoreEngine()
    for a in get_registered_adapters():
        engine.register_adapter(a)
    return engine

def main():
    parser = argparse.ArgumentParser(description="观的 AI 工具箱 · 通用历史会话管理与恢复中心 (严格分工具单会话管理)")
    parser.add_argument("--tool", type=str, help="指定工具标识 (workbuddy, trae, zcode, claudecode, antigravity, gpt)")
    parser.add_argument("--workspace", type=str, help="按工作区过滤")
    parser.add_argument("--list", action="store_true", help="列出指定工具的会话清单")
    parser.add_argument("--session", type=str, help="必须明确指定单会话 session_id")
    parser.add_argument("--restore", action="store_true", help="对 --session 指定的单条会话执行恢复")
    parser.add_argument("--export", action="store_true", help="对 --session 指定的单条会话执行 Markdown 导出")
    args = parser.parse_args()

    engine = build_engine()

    # CLI 模式
    if args.tool:
        adapter = engine.get_adapter(args.tool)
        if not adapter:
            print(f"[!] 未知工具: {args.tool}")
            print(f"支持的工具标识: {[a.tool_id for a in engine.list_all_adapters()]}")
            sys.exit(1)

        if args.list:
            sessions = adapter.list_sessions(workspace=args.workspace)
            print(f"\n[*] {adapter.name} 共检索到 {len(sessions)} 个会话:")
            for s in sessions[:30]:
                print(f"  [{s.session_id}] {s.title} ({s.size_human} | {s.time_human})")
            return

        if args.session:
            if args.restore:
                print(f"[*] 正在为 {adapter.name} 恢复指定会话: {args.session}")
                ok = adapter.restore_session(args.session)
                print(f"[✓] 恢复结果: {'成功' if ok else '失败'}")
                return
            if args.export:
                p = adapter.export_session(args.session)
                print(f"[✓] 会话已导出至: {p}")
                return
            detail = adapter.get_session_detail(args.session)
            print(f"会话详情: {detail}")
            return

        print("[!] CLI 模式下请结合 --list 或配合 --session <id> 使用。")
        print("[安全拦截] 本系统杜绝无脑全量恢复！必须通过 --session 指定具体单会话 ID！")
    else:
        # 默认启动现代交互菜单
        ui = InteractiveRestoreUI(engine)
        ui.run()

if __name__ == "__main__":
    main()

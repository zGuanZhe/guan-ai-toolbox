# -*- coding: utf-8 -*-
"""
Guan's AI Toolbox - Restore CLI Interactive UI
严格分工具独立管理，彻底禁止全量盲恢复。
支持: 工作区分流 -> 单会话透视 -> 选定会话恢复/导出。
"""

import sys
from typing import Optional
from core.restore_engine import RestoreEngine
from core.base_adapter import BaseRestoreAdapter

class InteractiveRestoreUI:
    def __init__(self, engine: RestoreEngine):
        self.engine = engine

    def run(self):
        while True:
            print("\n" + "=" * 80)
            print("          观的 AI 工具箱 · 通用历史会话管理与恢复中心")
            print("         【严格按工具独立管理 · 严禁无差别全量恢复 · 精准受控】")
            print("=" * 80)
            
            adapters = self.engine.list_all_adapters()
            print(f"{'序号':^4} | {'支持的编程工具':<26} | {'检测状态':^10} | {'特性说明'}")
            print("-" * 80)
            for idx, a in enumerate(adapters, 1):
                status_str = "✅ 已就绪" if a.is_installed() else "⚪ 未安装"
                desc_short = a.description[:32] + "..." if len(a.description) > 32 else a.description
                print(f"{idx:^4} | {a.name:<26} | {status_str:^10} | {desc_short}")
            print("-" * 80)
            print("  [0] 退出程序")
            print("=" * 80)

            choice = input("请选择要管理的工具序号 [0-6]: ").strip()
            if choice == "0":
                print("[*] 退出会话恢复中心。")
                break
            try:
                idx = int(choice)
                if 1 <= idx <= len(adapters):
                    self._handle_tool(adapters[idx - 1])
                else:
                    print("[!] 序号无效，请重新输入。")
            except ValueError:
                print("[!] 输入无效，请重新输入。")

    def _handle_tool(self, adapter: BaseRestoreAdapter):
        if not adapter.is_installed():
            print(f"\n[!] 警告: 本机未检测到 {adapter.name} 的数据存储目录 ({adapter.get_data_dir()})。")
            cont = input("是否仍尝试强制扫描？(y/N): ").strip().lower()
            if cont not in ["y", "yes"]:
                return

        while True:
            print(f"\n>>> 进入工具管理: {adapter.name}")
            print(f"数据源根路径: {adapter.get_data_dir()}")
            
            # 1. 查询工作区
            workspaces = adapter.list_workspaces()
            selected_workspace = None
            if workspaces and len(workspaces) > 1:
                print("\n检测到该工具关联了多个项目/工作区：")
                for w_idx, w in enumerate(workspaces[:10], 1):
                    print(f"  [{w_idx}] {w}")
                print(f"  [A] 查看全部工作区会话")
                print(f"  [0] 返回上级工具菜单")
                w_choice = input("请选择工作区 [默认 A]: ").strip().upper()
                if w_choice == "0":
                    break
                elif w_choice in ["", "A"]:
                    selected_workspace = None
                else:
                    try:
                        w_num = int(w_choice)
                        if 1 <= w_num <= len(workspaces):
                            selected_workspace = workspaces[w_num - 1]
                    except: pass
            
            # 2. 列出会话
            sessions = adapter.list_sessions(workspace=selected_workspace)
            if not sessions:
                print("[*] 当前工作区未检索到任何历史会话记录。")
                input("\n按回车键返回...")
                break

            print(f"\n检索到 {len(sessions)} 条独立历史会话记录（按最后活跃时间倒序）：")
            print("=" * 95)
            print(f"{'序号':^4} | {'会话标题 / 摘要':<38} | {'消息数':^6} | {'体积':^8} | {'更新时间':^18} | {'状态'}")
            print("-" * 95)
            for s_idx, s in enumerate(sessions[:20], 1):
                title = s.title[:35] if s.title else "无标题"
                lines = str(s.message_count) if s.message_count > 0 else "-"
                print(f"{s_idx:^4} | {title:<38} | {lines:^6} | {s.size_human:^8} | {s.time_human:^18} | {s.status}")
                if s.workspace:
                    ws_short = s.workspace if len(s.workspace) <= 55 else "..." + s.workspace[-52:]
                    print(f"     | 工作区: {ws_short} | ID: {s.session_id}")
                print("-" * 95)

            print("\n[安全准则] 本系统禁止全量恢复，请单选具体需要操作的会话序号！")
            target_idx_str = input("请输入要操作的会话序号 (1~N, 输入 0 返回): ").strip()
            if target_idx_str in ["0", ""]:
                break
            try:
                target_idx = int(target_idx_str)
                if not (1 <= target_idx <= len(sessions)):
                    print("[!] 序号超出范围。")
                    continue
            except ValueError:
                print("[!] 输入无效。")
                continue

            target_session = sessions[target_idx - 1]
            self._handle_single_session(adapter, target_session)

    def _handle_single_session(self, adapter: BaseRestoreAdapter, session):
        print("\n" + "=" * 70)
        print("                 选定单会话详情确认 (Session Detail)")
        print("=" * 70)
        print(f"所属工具:   {session.tool_name}")
        print(f"会话 ID:    {session.session_id}")
        print(f"会话标题:   {session.title}")
        print(f"关联工作区: {session.workspace}")
        print(f"更新时间:   {session.time_human}")
        print(f"消息/步数:  {session.message_count}")
        print(f"物理体积:   {session.size_human}")
        print(f"当前状态:   {session.status}")
        print(f"数据源路径: {session.raw_path}")
        print("=" * 70)

        print("\n请选择对该会话执行的动作:")
        print("  [1] 仅恢复并激活该单条会话 (自动做独立快照并挂载到当前用户/工作区)")
        print("  [2] 导出该会话为独立 Markdown 归档文件 (保存至桌面备查)")
        print("  [3] 仅对该单条会话执行独立备份快照")
        print("  [0] 取消并返回")
        act = input("请输入动作序号 [默认 1]: ").strip()

        if act in ["", "1"]:
            confirm = input(f"\n⚠️ 确认恢复单条会话 [{session.session_id}] 吗？(y/N): ").strip().lower()
            if confirm in ["y", "yes"]:
                print("[*] 正在执行单会话精准恢复...")
                ok = adapter.restore_session(session.session_id)
                if ok:
                    print(f"\n🎉 成功！会话 [{session.session_id}] 已激活恢复！")
                    if adapter.tool_id == "workbuddy":
                        print("💡 提示: 请刷新 WorkBuddy (按 Ctrl+R) 或重启客户端即可在左侧看到该会话！")
                else:
                    print("[!] 恢复操作未完全成功，请检查状态或日志。")
            else:
                print("[*] 操作已取消。")
        elif act == "2":
            print("[*] 正在导出为 Markdown...")
            try:
                out_path = adapter.export_session(session.session_id)
                print(f"\n🎉 导出成功！文件已生成至:\n   {out_path}")
            except Exception as e:
                print(f"[!] 导出失败: {e}")
        elif act == "3":
            print("[*] 正在创建独立快照...")
            bak = adapter.backup_session(session.session_id)
            print(f"[✓] 独立会话快照已保存至: {bak}")
        input("\n按回车键继续...")

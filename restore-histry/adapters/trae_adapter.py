# -*- coding: utf-8 -*-
"""
Trae (字节跳动 AI IDE) 专属会话管理与恢复适配器
基于 VS Code 架构，按工作区隔离扫描 workspaceStorage 中的 state.vscdb。
"""

import os
import json
import sqlite3
import shutil
import datetime
from typing import List, Optional, Dict, Any
from core.base_adapter import BaseRestoreAdapter
from core.session_envelope import SessionEnvelope

class TraeRestoreAdapter(BaseRestoreAdapter):
    @property
    def tool_id(self) -> str:
        return "trae"

    @property
    def name(self) -> str:
        return "Trae (字节跳动 AI IDE)"

    @property
    def description(self) -> str:
        return "基于 VS Code 架构。按工作区扫描 state.vscdb，支持单工程会话状态提取与安全备份"

    def _get_workspace_roots(self):
        appdata = os.environ.get("APPDATA", "")
        roots = []
        for name in ["Trae", "TRAE SOLO CN", "trae"]:
            p = os.path.join(appdata, name, "User", "workspaceStorage")
            if os.path.exists(p):
                roots.append(p)
        return roots

    def is_installed(self) -> bool:
        return len(self._get_workspace_roots()) > 0

    def get_data_dir(self) -> str:
        roots = self._get_workspace_roots()
        return roots[0] if roots else ""

    def list_workspaces(self) -> List[str]:
        workspaces = set()
        for root in self._get_workspace_roots():
            for folder in os.listdir(root):
                fp = os.path.join(root, folder, "workspace.json")
                if os.path.exists(fp):
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            w = data.get("folder")
                            if w: workspaces.add(w)
                    except: pass
        return sorted(list(workspaces))

    def list_sessions(self, workspace: Optional[str] = None) -> List[SessionEnvelope]:
        envelopes = []
        for root in self._get_workspace_roots():
            if not os.path.exists(root):
                continue
            for folder in os.listdir(root):
                folder_path = os.path.join(root, folder)
                db_path = os.path.join(folder_path, "state.vscdb")
                if not os.path.exists(db_path):
                    continue

                ws_name = folder
                ws_json = os.path.join(folder_path, "workspace.json")
                if os.path.exists(ws_json):
                    try:
                        with open(ws_json, "r", encoding="utf-8") as f:
                            ws_name = json.load(f).get("folder", folder)
                    except: pass

                if workspace and ws_name != workspace:
                    continue

                mtime = os.path.getmtime(db_path)
                size = os.path.getsize(db_path)

                # 尝试从 SQLite 中探测会话首条输入与消息轮数
                first_prompt = ""
                msg_count = 0
                try:
                    conn = sqlite3.connect(db_path, timeout=3.0)
                    c = conn.cursor()
                    c.execute("SELECT value FROM ItemTable WHERE key = 'icube-ai-agent-storage-input-history'")
                    row = c.fetchone()
                    if row and row[0]:
                        try:
                            history = json.loads(row[0])
                            if isinstance(history, list) and history:
                                msg_count = len(history)
                                for h in history:
                                    txt = h.get("inputText", "").strip()
                                    if txt:
                                        first_prompt = txt[:40] + ("..." if len(txt) > 40 else "")
                                        break
                        except: pass
                    
                    if not first_prompt:
                        c.execute("SELECT value FROM ItemTable WHERE key = 'memento/icube-ai-agent-storage'")
                        row_m = c.fetchone()
                        if row_m and row_m[0]:
                            try:
                                m_data = json.loads(row_m[0])
                                msgs = m_data.get("list", [{}])[0].get("messages", [])
                                if msgs:
                                    msg_count = max(msg_count, len(msgs))
                                    first_prompt = f"Agent 交互记录 ({len(msgs)} 轮对话)"
                            except: pass
                    conn.close()
                except Exception:
                    pass

                disp_title = f"Trae 会话: {first_prompt}" if first_prompt else f"Trae 工作区: {os.path.basename(ws_name)}"

                envelopes.append(SessionEnvelope(
                    session_id=f"trae-{folder}",
                    tool_id=self.tool_id,
                    tool_name=self.name,
                    workspace=ws_name,
                    title=disp_title,
                    updated_at=datetime.datetime.fromtimestamp(mtime),
                    message_count=msg_count,
                    size_bytes=size,
                    status="active",
                    raw_path=db_path,
                    extra_meta={"folder_hash": folder}
                ))
        envelopes.sort(key=lambda x: x.updated_at or datetime.datetime.min, reverse=True)
        return envelopes

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        for s in self.list_sessions():
            if s.session_id == session_id:
                snippets = []
                if os.path.exists(s.raw_path):
                    try:
                        conn = sqlite3.connect(s.raw_path, timeout=3.0)
                        c = conn.cursor()
                        c.execute("SELECT value FROM ItemTable WHERE key = 'icube-ai-agent-storage-input-history'")
                        row = c.fetchone()
                        if row and row[0]:
                            history = json.loads(row[0])
                            if isinstance(history, list):
                                for item in history[:3]:
                                    t = item.get("inputText", "").strip()
                                    if t: snippets.append(t[:120])
                        conn.close()
                    except: pass
                return {"envelope": s, "raw_db": s.raw_path, "preview_snippets": snippets}
        return None

    def backup_session(self, session_id: str) -> str:
        detail = self.get_session_detail(session_id)
        if not detail or not os.path.exists(detail["raw_db"]):
            raise ValueError(f"未找到会话 {session_id}")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(detail["raw_db"]), f"backup_{ts}")
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(detail["raw_db"], os.path.join(backup_dir, "state.vscdb"))
        return backup_dir

    def restore_session(self, session_id: str, options: Optional[Dict[str, Any]] = None) -> bool:
        if not session_id:
            raise ValueError("必须指定单会话 ID！")
        detail = self.get_session_detail(session_id)
        if not detail or not os.path.exists(detail["raw_db"]):
            raise ValueError(f"未找到会话 {session_id} 对应的数据文件")

        db_path = detail["raw_db"]
        folder_dir = os.path.dirname(db_path)

        # 1. 严格做安全快照
        self.backup_session(session_id)

        # 2. 查找是否有指定或最近的备份还原源
        opt = options or {}
        src_backup = opt.get("backup_path")
        if not src_backup:
            # 搜索历史备份文件夹 (backup_YYYYMMDD_HHMMSS)
            backups = sorted([
                os.path.join(folder_dir, d) for d in os.listdir(folder_dir)
                if d.startswith("backup_") and os.path.isdir(os.path.join(folder_dir, d))
            ], reverse=True)
            # 排除刚才创建的最新的那个
            if len(backups) > 1:
                candidate = os.path.join(backups[1], "state.vscdb")
                if os.path.exists(candidate):
                    src_backup = candidate

        restored_file = False
        if src_backup and os.path.exists(src_backup):
            shutil.copy2(src_backup, db_path)
            restored_file = True

        # 3. 真实更新活跃 state.vscdb: 强制将可能被隐藏或折叠的 AI Chat 面板重置为可见与展开
        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            c = conn.cursor()
            c.execute("SELECT value FROM ItemTable WHERE key = 'workbench.panel.icube.aiChatSidebar'")
            row = c.fetchone()
            if row and row[0]:
                try:
                    val = json.loads(row[0])
                    view_cfg = val.get("workbench.panel.chat.view.ai-chat", {})
                    if view_cfg.get("isHidden") is True:
                        view_cfg["isHidden"] = False
                        val["workbench.panel.chat.view.ai-chat"] = view_cfg
                        c.execute("UPDATE ItemTable SET value = ? WHERE key = 'workbench.panel.icube.aiChatSidebar'", (json.dumps(val),))
                        conn.commit()
                except: pass
            conn.close()
        except Exception as e:
            print(f"[!] Trae 活跃状态表重置警告: {e}")

        print(f"[OK] Trae 会话 {session_id} 恢复完成！(数据源已同步, 面板激活)")
        return True

    def export_session(self, session_id: str, target_file: Optional[str] = None) -> str:
        detail = self.get_session_detail(session_id)
        if not detail:
            raise ValueError(f"会话 {session_id} 不存在")

        if not target_file:
            home = os.path.expanduser("~")
            export_dir = os.path.join(home, "Desktop", "AI_Sessions_Export")
            os.makedirs(export_dir, exist_ok=True)
            target_file = os.path.join(export_dir, f"Trae_{session_id}.md")

        db_path = detail["raw_db"]
        env = detail["envelope"]

        prompts = []
        messages = []
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path, timeout=5.0)
                c = conn.cursor()
                # 读取输入历史
                c.execute("SELECT value FROM ItemTable WHERE key = 'icube-ai-agent-storage-input-history'")
                r_hist = c.fetchone()
                if r_hist and r_hist[0]:
                    try:
                        h_list = json.loads(r_hist[0])
                        if isinstance(h_list, list):
                            for h in h_list:
                                q = h.get("inputText", "").strip()
                                if q: prompts.append(q)
                    except: pass

                # 读取 agent storage
                c.execute("SELECT value FROM ItemTable WHERE key = 'memento/icube-ai-agent-storage'")
                r_mem = c.fetchone()
                if r_mem and r_mem[0]:
                    try:
                        m_obj = json.loads(r_mem[0])
                        for s in m_obj.get("list", []):
                            for m in s.get("messages", []):
                                messages.append(m)
                    except: pass
                conn.close()
            except Exception as e:
                print(f"[!] 读取 Trae 会话数据错误: {e}")

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(f"# Trae AI 会话归档 - {session_id}\n\n")
            f.write(f"- **工作区**: {env.workspace}\n")
            f.write(f"- **会话标题**: {env.title}\n")
            f.write(f"- **最后活跃**: {env.time_human}\n")
            f.write(f"- **底层数据库**: `{db_path}`\n")
            f.write(f"- **记录轮次**: {len(prompts)} 条输入指令 / {len(messages)} 条交互流\n\n---\n\n")

            f.write("## 1. 用户指令与问题历史 (User Prompts)\n\n")
            if prompts:
                for idx, p in enumerate(prompts, 1):
                    f.write(f"### Turn #{idx}\n\n```text\n{p}\n```\n\n")
            else:
                f.write("> 暂无持久化的历史输入提示词记录\n\n")

            if messages:
                f.write("## 2. 完整上下文消息体 (Messages)\n\n")
                for m in messages:
                    role = m.get("role", "message").upper()
                    content = m.get("content") or m.get("text") or str(m)
                    f.write(f"### [{role}]\n\n{content}\n\n")

        print(f"[OK] Trae 会话已成功导出至: {target_file}")
        return target_file
